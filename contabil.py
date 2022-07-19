import PySimpleGUI as sg
from datetime import datetime  # , date
import os
import sqlite3
import calendar
import locale
import re
from fpdf import FPDF

# from json import (load as jsonload, dump as jsondump)

"""
    Programa para contabilidade do estúdio lótus
    Faltam:
    Relatórios (em tela e impressos)
    Relatório mensal: por categoria e por entrada/saida
    OK CHECAR A RECORRÊNCIA NA ALTERACAO DE REGISTRO
    OK SE UM VALOR RECORRENTE MUDAR, ELE MUDA EM TODOS OS MESES - ISSO TÁ ERRADO
    OK TRATAR EXCLUSÃO NAS FUNCOES DE HISTORICO
        
"""

# arq_ajustes = os.path.join(os.path.dirname(__file__), r'contabil.cfg')
dirajustes = os.path.join(os.getcwd(), 'ajustes')
meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro',
         'Outubro', 'Novembro', 'Dezembro']
dias = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab']
anos = ['2020', '2021', '2022', '2023', '2024', '2025']
dbfinanceiro = os.path.join(os.getcwd(), 'db', 'financeiro.db')
dbhistorico = os.path.join(os.getcwd(), 'db', 'historico.db')
dbsistema = os.path.join(os.getcwd(), 'db', 'sistema.db')
mdbfile = os.path.join(os.getcwd(), 'db', 'mensalidades.db')
pdfvw = os.path.join(os.getcwd(), 'recursos', 'SumatraPDF.exe')
arq_rel_mens = 'rel_mensal.pdf'
regex_data = re.compile(r'\d{2}\/\d{2}\/\d{4}|\d{2}\/\d{2}\/\d{4}\d{2}\/\d{2}\/\d{4}|\d{2}\/\d{2}\/\d{4}')
regex_dinheiro = re.compile(r'^(\d{1,}\d+\,\d{2}?)$')


# TODO USER SETTINGS

class Movimento:
    def __init__(self, indice, data, ensai, tipo, desc, valor, relrec):
        self.indice = indice
        self.data = data
        self.ensai = ensai
        self.tipo = tipo
        self.desc = desc
        self.valor = valor
        self.relrec = relrec

    def set_indice(self, indice):
        self.indice = indice

    def set_data(self, data):
        self.data = data

    def set_ensai(self, ensai):
        self.ensai = ensai

    def set_tipo(self, tipo):
        self.tipo = tipo

    def set_desc(self, desc):
        self.desc = desc

    def set_valor(self, valor):
        self.valor = valor

    def set_relrec(self, relrec):
        self.relrec = relrec

    def get_indice(self):
        return self.indice

    def get_data(self):
        return self.data

    def get_ensai(self):
        return self.ensai

    def get_tipo(self):
        return self.tipo

    def get_desc(self):
        return self.desc

    def get_valor(self):
        return self.valor

    def get_relrec(self):
        return self.relrec


def apaga_movimento(index):
    conexao = sqlite3.connect(dbfinanceiro)
    c = conexao.cursor()
    c.execute('DELETE FROM movimento WHERE mo_index = ?', (index,))
    conexao.commit()
    conexao.close()


def apaga_recorrente(index):
    conexao = sqlite3.connect(dbfinanceiro)
    c = conexao.cursor()
    c.execute('DELETE FROM recorrente WHERE re_index = ?', (index,))
    conexao.commit()
    conexao.close()


def mensalidades_le_pagas(mesano):
    valortotal = 0.0
    conexao = sqlite3.connect(dbsistema)
    c = conexao.cursor()
    c.execute('SELECT al_index, al_nome FROM Alunos')
    index_alunos = c.fetchall()
    print(index_alunos[0][0])
    conexao.close()
    conexao = sqlite3.connect(mdbfile)
    c = conexao.cursor()
    for idx, x in enumerate(index_alunos):
        nometabela = 'mens_' + str(x[0])
        print(nometabela)
        comando = 'SELECT me_vlrpago FROM ' + nometabela + ' WHERE me_mesano = ? AND me_pg = "1"'
        # print(comando)
        c.execute(comando, (mesano,))
        valorpago = c.fetchone()
        print(valorpago)
        if valorpago is not None:
            valortotal = valortotal + float(valorpago[0])
    print(valortotal)
    valfinal = str(valortotal).replace('.', ',')
    valfinal = valfinal + '0'
    conexao.close()
    return valfinal


def recebido_mensal(mesano):
    conexao = sqlite3.connect(dbsistema)
    c = conexao.cursor()

    # c.execute('SELECT al_nome,al_endereco,al_telefone01,al_telefone02,al_email,al_dt_matricula,al_dt_vencto FROM
    # Alunos WHERE al_index = ?', (indice,))

    # c.execute('SELECT fi_data_pgto,fi_atraso,fi_valor_rec,fi_recebido FROM Financeiro fin JOIN Alunos al on
    # fin.fi_nome = al.al_index WHERE al.al_index = ?', (indice,))

    mesano = ('%' + mesano + '%')
    # c.execute('SELECT fi_valor_rec FROM Financeiro WHERE fi_data_pgto LIKE ? AND ', (mesano,))
    c.execute(
        'SELECT fi_valor_rec FROM Financeiro JOIN Alunos on Financeiro.fi_nome = Alunos.al_index WHERE fi_data_pgto '
        'LIKE ? AND '
        'Alunos.al_ativo = "S"',
        (mesano,))
    resultado = c.fetchall()
    # print(resultado)
    valor_final = 0.0
    for idx, x in enumerate(resultado):
        valor = resultado[idx][0]
        # print(resultado[idx])
        valor = valor.replace(',', '.')
        valor_final = valor_final + float(valor)
    # print(valor_final)
    valfinal = str(valor_final).replace('.', ',')
    valfinal = valfinal + '0'
    # print(resultado)
    # FILTRANDO O RESULTADO:
    # print(resultado)
    # i = 0
    # res_filtrado = resultado
    # while i < len(resultado):
    #    res_filtrado[i] = resultado[i][1], resultado[i][6], resultado[i][2], resultado[i][4], resultado[i][3]
    # fi_data_pgto, al_nome, fi_atraso, fi_recebido, fi_valor_recebido
    # print(resultado[i][1])
    #    i = i + 1
    # print(resultado)
    # print(res_filtrado)
    # print(len(resultado))
    conexao.close()
    return valfinal


def grava_movimento(data, ensai, tipo, descricao, valor, relrec):
    conexao = sqlite3.connect(dbfinanceiro)
    c = conexao.cursor()
    dados = [data, ensai, tipo, descricao, valor, relrec]
    c.execute("INSERT INTO movimento(mo_data, mo_ensai,"
              "mo_tipo, mo_descricao, mo_valor, mo_relrec) VALUES (?,?,?,?,?,?)", dados)
    conexao.commit()
    conexao.close()


def altera_movimento(data, ensai, tipo, descricao, valor, indice):
    conexao = sqlite3.connect(dbfinanceiro)
    c = conexao.cursor()
    dadosupdt = [data, ensai, tipo, descricao, valor, indice]
    c.execute("UPDATE movimento SET mo_data = ?, mo_ensai = ?,"
              "mo_tipo = ?, mo_descricao = ?, mo_valor = ? WHERE mo_index = ?", dadosupdt)
    conexao.commit()
    conexao.close()


def grava_recorrente(dia, ensai, tipo, descricao, valor):
    conexao = sqlite3.connect(dbfinanceiro)
    c = conexao.cursor()
    dados = [dia, ensai, tipo, descricao, valor]
    c.execute("INSERT INTO recorrente(re_dia, re_ensai,"
              "re_tipo, re_descricao, re_valor) VALUES (?,?,?,?,?)", dados)
    conexao.commit()
    conexao.close()


def altera_recorrente(dia, ensai, tipo, descricao, valor, indice):
    conexao = sqlite3.connect(dbfinanceiro)
    c = conexao.cursor()
    dados = [dia, ensai, tipo, descricao, valor, indice]
    c.execute("UPDATE recorrente SET re_dia = ?, re_ensai = ?,"
              "re_tipo = ?, re_descricao = ?, re_valor = ? WHERE re_index = ?", dados)
    conexao.commit()
    conexao.close()


# def vincular_dados(mesano):
#    conexao = sqlite3.connect(dbfinanceiro)
#    c = conexao.cursor()


def le_movimento(mesano):
    conexao = sqlite3.connect(dbfinanceiro)
    c = conexao.cursor()
    if mesano == '':
        c.execute("""
                        SELECT mo_index,mo_data,mo_ensai,mo_tipo,mo_descricao,mo_valor,mo_relrec FROM movimento;
                    """)
    else:
        mesano2 = ('%' + mesano + '%')
        c.execute(
            'SELECT mo_index,mo_data,mo_ensai,mo_tipo,mo_descricao,'
            'mo_valor,mo_relrec FROM movimento WHERE mo_data like ?', (mesano2,)
        )
    dados = c.fetchall()
    conexao.close()
    # le_movimento: mo_index, mo_data, mo_ensai, mo_tipo, mo_descricao, mo_valor, mo_relrec
    # APPENDS DOS DADOS DA TABELA RECORRENTE E DO RECEBIDO DO ESTÚDIO
    # SE QUISER QUE OS APPENDS ACONTEÇAM TO DO MES, RETIRAR O IF
    # if dados:
    # temp_rec = le_recorrente()
    # dados.append(
    #    ('', ('05/' + mesano), 'ENTRADA', 'Mensalidades do Estúdio', 'Recebidos', recebido_mensal(mesano), 100))
    # print(temp_rec)
    # for idx, x in enumerate(temp_rec):
    #     data = x[1] + '/' + mesano
    #     dados.append((x[0], data, x[2], x[3], x[4], x[5], x[0]))

    valores_tmp = dados
    # ORGANIZA A LISTA PELA DATA
    # print(valores_tmp)
    valores_sort = []
    valores_sorted = []
    for idx, x in enumerate(valores_tmp):
        if x[1] != '':
            # print(x)
            datatmp = datetime.strptime(x[1], '%d/%m/%Y')
            listatmp = [datatmp, (x[2]), (x[3]), (x[4]), (x[5]), (x[6]), (x[0])]
            valores_sort.append(listatmp)
    # print(valores_sort)
    # valores_sorted = sorted(valores_sort, key=valores_sort[0][1])
    valores_sort.sort()
    for idx, x in enumerate(valores_sort):
        txttmp = datetime.strftime(x[0], '%d/%m/%Y')
        listatmp = [(x[6]), txttmp, (x[1]), (x[2]), (x[3]), (x[4]), (x[5])]
        valores_sorted.append(listatmp)
    # print(dados)
    return valores_sorted


# CALCULA O VALOR TOTAL, ISTO EH, ENTRADAS - SAIDAS
def calcula(mesano):
    resultado = 0.0
    tbl_tmp = le_movimento(mesano)
    for idx, x in enumerate(tbl_tmp):
        if x[2] == 'ENTRADA':
            valor = x[5].replace(',', '.')
            resultado = resultado + float(valor)
            # print(resultado)
        else:
            valor = x[5]
            # print('valor:', valor)
            valor = valor.replace(',', '.')
            resultado = resultado - float(valor)
        # print(resultado)
    return resultado


# CALCULA SOMENTE O VALOR DAS ENTRADAS
def calcula_en(mesano):
    resultado = 0.0
    tbl_tmp = le_movimento(mesano)
    for idx, x in enumerate(tbl_tmp):
        if x[2] == 'ENTRADA':
            valor = x[5].replace(',', '.')
            resultado = resultado + float(valor)
            # print(resultado)
        # else:
        #    valor = x[5]
        # print('valor:', valor)
        #    valor = valor.replace(',', '.')
        #    resultado = resultado - float(valor)
        # print(resultado)
    return resultado


# CALCULA SOMENTE O VALOR DAS SAIDAS
def calcula_sa(mesano):
    resultado = 0.0
    tbl_tmp = le_movimento(mesano)
    for idx, x in enumerate(tbl_tmp):
        if x[2] == 'SAIDA':
            valor = x[5].replace(',', '.')
            resultado = resultado + float(valor)
            # print(resultado)
        # else:
        #    valor = x[5]
        # print('valor:', valor)
        #    valor = valor.replace(',', '.')
        #    resultado = resultado - float(valor)
        # print(resultado)
    return resultado


def le_recorrente():
    conexao = sqlite3.connect(dbfinanceiro)
    c = conexao.cursor()
    c.execute("""
                SELECT re_index,re_dia,re_ensai,re_tipo,re_descricao,re_valor FROM recorrente;
            """)
    dados = c.fetchall()
    conexao.close()
    # print(dados)
    return dados


# le_recorrente: re_index, re_dia, re_ensai, re_tipo, re_descricao, re_valor

def incorpora_tabelas(mesano):
    # existe = True
    array = []
    data = datetime.strptime(mesano, '%m/%Y')
    ult_dia = calendar.monthrange(int(datetime.strftime(data, '%Y')),
                                  int(datetime.strftime(data, '%m')))
    # le_movimento: mo_index, mo_data, mo_ensai, mo_tipo, mo_descricao, mo_valor, mo_relrec
    # le_recorrente: re_index, re_dia, re_ensai, re_tipo, re_descricao, re_valor
    # print(mesano)
    temp_mov = le_movimento(mesano)
    temp_rec = le_recorrente()
    for idx, x in enumerate(temp_mov):
        # print(x[6])
        array.append(x[6])
    # print(array)
    for idx, x in enumerate(temp_rec):
        # print(x)
        if x[0] not in array:
            data = x[1] + '/' + mesano
            grava_movimento(data, x[2], x[3], x[4], x[5], x[0])
    # for idx, x in enumerate(array):
    if 100 not in array:
        grava_movimento((str(ult_dia[1]) + '/' + mesano), 'ENTRADA', 'Mensalidades do Estúdio',
                        'Recebidos', mensalidades_le_pagas(mesano), '100')  # recebido_mensal(mesano)
    else:
        for idx, x in enumerate(temp_mov):
            if x[6] == 100:
                if x[5] != mensalidades_le_pagas(mesano):
                    altera_movimento((str(ult_dia[1]) + '/' + mesano), 'ENTRADA', 'Mensalidades do Estúdio',
                                     'Recebidos', mensalidades_le_pagas(mesano), x[0])


#        for idx2, x2 in enumerate(temp_rec):


def grava_tipo(tipo):
    conexao = sqlite3.connect(dbfinanceiro)
    c = conexao.cursor()
    dados = [tipo]
    c.execute("INSERT INTO tipo(ti_tipo) VALUES (?)", dados)
    conexao.commit()
    conexao.close()


def le_tipo():
    conexao = sqlite3.connect(dbfinanceiro)
    c = conexao.cursor()
    c.execute("""
                SELECT ti_tipo FROM tipo;
            """)
    dados = c.fetchall()
    conexao.close()
    # print(dados)
    return dados


def apaga_tipo(texto):
    texto2 = ('%' + texto + '%')
    conexao = sqlite3.connect(dbfinanceiro)
    c = conexao.cursor()
    c.execute('DELETE FROM tipo WHERE ti_tipo LIKE ?', (texto2,))
    conexao.commit()
    conexao.close()


def tableexists(dbcon, tablename):
    dbcur = dbcon.cursor()
    dbcur.execute("""
        SELECT * FROM sqlite_master WHERE type = 'table' AND name = '{0}'
        """.format(tablename))  # .replace('\'', '\'\'')
    # SELECT * FROM sqlite_master WHERE type = 'table' AND name = 'the_table_name'
    # print(tablename)
    # print('dbcur.fetchone()[1] ', dbcur.fetchone())
    # print(dbcur.fetchone()[2])
    myvar = dbcur.fetchall()
    # print(myvar)
    if not myvar:
        dbcur.close()
        return False
    dbcur.close()
    return True


def checa_historico(meseano):
    ultima_gravacao = sg.user_settings_get_entry('-ultima_grav_historico-', datetime.strftime(datetime.now(), '%m/%Y'))
    if datetime.strptime(ultima_gravacao, '%m/%Y') < datetime.strptime(meseano, '%m/%Y'):
        grava_historico(meseano, False)
        sg.user_settings_set_entry('-ultima_grav_historico-', datetime.strftime(datetime.now(), '%m/%Y'))


def grava_historico(mesano, exclui):
    # mesano = string 00/0000
    # exclui = True para excluir registro, False para operação normal.
    # dataatual = datetime.strftime(datetime.now(), '%m')
    # mespassado =
    # ult_dia = calendar.monthrange(int(datetime.strftime(data, '%Y')),
    #                               int(datetime.strftime(data, '%m')))
    # sg.user_settings_set_entry('-ultima_grav_historico-', '06/2022')
    datatmp = datetime.strptime(mesano, '%m/%Y')
    nometabela = 'tbl_' + datetime.strftime(datatmp, '%m_%Y')
    conexao = sqlite3.connect(dbhistorico)
    # SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';
    # SELECT name FROM myattacheddb.sqlite_master WHERE type='table' AND name='{table_name}';
    # if(return > 0)
    # comando0 = "SELECT name FROM sqlite_master WHERE type='table' AND name='{" + nometabela + "}';"

    comando = ('create table if not exists ' + nometabela + '(mo_index INTEGER PRIMARY KEY, mo_altindex INTEGER, '
                                                            'mo_data TEXT, mo_ensai '
                                                            'TEXT, mo_tipo TEXT, mo_descricao TEXT, mo_valor TEXT, '
                                                            'mo_relrec INTEGER);')
    # print(comando)
    # print(tableexists(conexao, nometabela))
    mov_mes = le_movimento(mesano)
    if not tableexists(conexao, nometabela):
        print('Tabela não existe. Cria a tabela e grava todos os dados.')
        c = conexao.cursor()
        c.execute(comando)

        # print(mov_mes)
        for idx, x in enumerate(mov_mes):
            comando2 = 'INSERT INTO ' + nometabela + '(mo_altindex, mo_data, mo_ensai, mo_tipo,' \
                                                     ' mo_descricao, mo_valor, mo_relrec) VALUES (?,?,?,?,?,?,?) '
            dados = [x[0], x[1], x[2], x[3], x[4], x[5], x[6]]
            c.execute(comando2, dados)
            conexao.commit()
    else:
        c = conexao.cursor()
        if exclui:
            print('excluindo registro')
            comandoex1 = 'SELECT * FROM {0} '.format(nometabela)
            c.execute(comandoex1)
            tbltmp = c.fetchall()
            arraytmp2 = []
            for idx, x in enumerate(mov_mes):
                arraytmp2.append(x[0])
            for idx, x in enumerate(tbltmp):
                print('x[1] ', x[1])
                print(arraytmp2)
                if x[1] not in arraytmp2:
                    print('registro encontrado. excluindo.')
                    comandoex1 = 'DELETE FROM {0} WHERE mo_altindex = ?'.format(nometabela)
                    tmpv = [x[1]]
                    c.execute(comandoex1, tmpv)
                    conexao.commit()
        else:
            print('Tabela existe. Compara os índices e resolve se deve alterar algum dado.')
            c = conexao.cursor()
            comando3 = 'SELECT * FROM {0} '.format(nometabela)
            c.execute(comando3)
            tabelatmp = c.fetchall()
            arraytmp = []
            for idx, x in enumerate(tabelatmp):
                arraytmp.append(x[1])
            for idx, x in enumerate(mov_mes):
                if x[0] in arraytmp:
                    print('encontrou entrada já na tabela, atualizando.')
                    dados = [x[1], x[2], x[3], x[4], x[5], x[6], x[0]]
                    comando4 = 'UPDATE {0} SET mo_data = ?, mo_ensai = ?, mo_tipo = ?, ' \
                               'mo_descricao = ?, mo_valor = ?, ' \
                               'mo_relrec = ? WHERE mo_altindex = ?'.format(nometabela)
                    c.execute(comando4, dados)
                    conexao.commit()
                else:
                    print('Encontrou dados que não constavam na tabela, inserindo.')
                    comando2 = 'INSERT INTO ' + nometabela + '(mo_altindex, mo_data, mo_ensai, mo_tipo,' \
                                                             'mo_descricao, mo_valor, mo_relrec) VALUES (?,?,?,?,?,?,' \
                                                             '?) '
                    dados = [x[0], x[1], x[2], x[3], x[4], x[5], x[6]]
                    c.execute(comando2, dados)
                    conexao.commit()
            #            print[idx]
            # print('tabelatmp[idx] ', tabelatmp[idx])
            #            print('x[0] ', x[0], 'tabelatmp[idx][1] ', tabelatmp[idx][1])
            #            for idx2, x2 in enumerate(tabelatmp):
            #                if x2[1] == x[0]:
            #                    print('encontrou entrada já na tabela, atualizando.')
            #                    dados = [x[1], x[2], x[3], x[4], x[5], x[6], x[0]]
            # comando4 = 'UPDATE {0} SET mo_data = ?, mo_ensai = ?, mo_tipo = ?, mo_descricao = ?, mo_valor = ?, ' \
            #                               'mo_relrec = ? WHERE mo_altindex = ?'.format(nometabela)
            #                    c.execute(comando4, dados)
            #                    conexao.commit()
            #            else:
            #                print('Encontrou dados que não constavam na tabela, inserindo.')
            #                comando2 = 'INSERT INTO ' + nometabela + '(mo_altindex, mo_data, mo_ensai, mo_tipo,' \
            # ' mo_descricao, mo_valor, mo_relrec) VALUES (?,?,?,?,?,?,?)'
    #               dados = [x[0], x[1], x[2], x[3], x[4], x[5], x[6]]
    #               c.execute(comando2, dados)
    #               conexao.commit()
    conexao.close()


# SELECT mo_index,mo_data,mo_ensai,mo_tipo,mo_descricao,mo_valor,mo_relrec


def convmes(mes):
    res = ''
    #    mesat = datetime.now()
    #    m = mesat.strftime('%m')
    if mes == meses[0]:
        res = '01'
    elif mes == meses[1]:
        res = '02'
    elif mes == meses[2]:
        res = '03'
    elif mes == meses[3]:
        res = '04'
    elif mes == meses[4]:
        res = '05'
    elif mes == meses[5]:
        res = '06'
    elif mes == meses[6]:
        res = '07'
    elif mes == meses[7]:
        res = '08'
    elif mes == meses[8]:
        res = '09'
    elif mes == meses[9]:
        res = '10'
    elif mes == meses[10]:
        res = '11'
    elif mes == meses[11]:
        res = '12'
    return res


def mesatual():
    res = ''
    mesat = datetime.now()
    m = mesat.strftime('%m')
    if m == '01':
        res = meses[0]
    elif m == '02':
        res = meses[1]
    elif m == '03':
        res = meses[2]
    elif m == '04':
        res = meses[3]
    elif m == '05':
        res = meses[4]
    elif m == '06':
        res = meses[5]
    elif m == '07':
        res = meses[6]
    elif m == '08':
        res = meses[7]
    elif m == '09':
        res = meses[8]
    elif m == '10':
        res = meses[9]
    elif m == '11':
        res = meses[10]
    elif m == '12':
        res = meses[11]
    return res


def gera_pdf_mes(listatmp, mestmp, valorfinal):
    rpdf = FPDF('P', 'cm', 'A4')
    rpdf.add_page()
    rpdf.add_font('Calibri', 'I', 'Calibrii.ttf', uni=True)
    rpdf.add_font('Calibri', 'B', 'Calibrib.ttf', uni=True)
    rpdf.add_font('Calibri', '', 'Calibri.ttf', uni=True)
    rpdf.set_font('Calibri', 'B', 14)
    # rpdf.image(imagem_peq, 16.6, 1.6)
    rpdf.rect(1, 1, 19, 8.8, 'D')
    rpdf.cell(0, 0.6, '', 0, 2, 'C')
    string1 = 'RELATÓRIO FINANCEIRO DO MÊS DE {}'.format(mestmp)
    rpdf.cell(0, 0.6, string1, 0, 2, 'C')
    rpdf.cell(0, 0.6, 'Lótus Condicionamento Dinâmico Integrado', 0, 2, 'C')
    rpdf.cell(0, 0.6, 'Andréia de Cássia Gonçalves (CREF 020951-G/MG)', 0, 2, 'C')
    rpdf.set_font('Calibri', 'I', 14)
    rpdf.cell(0, 0.6, 'Rua Coronel Paiva, 12  Centro  Ouro Fino MG', 0, 2, 'C')
    rpdf.line(1, 4.5, 20, 4.5)
    rpdf.set_font('Calibri', 'B', 14)
    rpdf.cell(0.5, 1, '', 0, 1)
    rpdf.cell(0.5, 1, '')
    rpdf.cell(0.4, 0.6, str(''), 0, 0, 'L')
    rpdf.cell(1.8, 0.6, str('Data'), 0, 0, 'L')
    rpdf.cell(1.5, 0.6, str('Tipo'), 0, 0, 'L')
    rpdf.cell(6, 0.6, str('Categoria'), 0, 0, 'L')
    rpdf.cell(6.8, 0.6, str('Descrição'), 0, 0, 'L')
    rpdf.cell(6.8, 0.6, str('Valor'), 0, 1, 'L')
    for idx, x in enumerate(listatmp):
        # DATA
        rpdf.cell(0.2, 0.6, str(''), 0, 0, 'L')
        tempstr = x[1]
        rpdf.cell(2.8, 0.6, str(tempstr), 0, 0, 'L')
        # TIPO
        tempstr = x[2]
        tempstr = tempstr[0]
        # relpdf.cell(0,0.6,str(tempstr),0,0,'R')
        rpdf.cell(1, 0.6, str(tempstr), 0, 0, 'L')
        # CATEGORIA
        tempstr = x[3]
        rpdf.cell(6, 0.6, str(tempstr), 0, 0, 'L')
        # DESCRICAO
        tempstr = x[4]
        rpdf.cell(7.6, 0.6, str(tempstr), 0, 0, 'L')
        # VALOR
        tempstr = x[5]
        rpdf.cell(1, 0.6, str(tempstr), 0, 1, 'R')
    rpdf.cell(0.4, 0.6, str(''), 0, 1, 'L')
    rpdf.cell(13.7, 0.6, str(''), 0, 0, 'L')
    rpdf.cell(3.7, 0.6, str('Valor final:'), 0, 0, 'L')
    rpdf.cell(1, 0.6, str(valorfinal), 0, 1, 'R')
    # rpdf.cell(19, 10, 'Hello World!', 1)
    # rpdf.cell(40, 10, 'Hello World!', 1)
    # rpdf.cell(60, 10, 'Powered by FPDF.', 0, 1, 'C')
    # rpdf.output(arq_recibo, 'F')
    rpdf.output(arq_rel_mens)


class Contabil:
    locale.setlocale(locale.LC_ALL, 'pt_BR')
    calendar.setfirstweekday(calendar.SUNDAY)
    sg.user_settings_filename(path=dirajustes)
    checa_historico(datetime.strftime(datetime.now(), '%m/%Y'))
    titulos = ['Indice', 'Data', 'Tipo', 'Categoria', 'Descrição', 'Valor']

    largura = [0, 10, 10, 30, 35, 10]

    visibilidade = [False, True, True, True, True, True]

    row = []

    dados = []

    recorrente = False

    templinha = []

    # tipos = []

    def cria_janela(self):
        coluna1_def = sg.Column(
            [[sg.T('Data:'), sg.I(default_text=datetime.strftime(datetime.now(), '%d/%m/%Y'), k='-DATAMOV-',
                                  size=10),
              sg.CalendarButton('Data', locale='pt_BR', format='%d/%m/%Y',
                                month_names=meses, day_abbreviations=dias), sg.T('Tipo:'),
              # sg.Combo(['Entrada', 'Saída'], default_value='Entrada'),
              sg.Radio('Entrada', group_id='-ENSAI-', k='-EN-', default=True),
              sg.Radio('Saída', group_id='-ENSAI-', k='-SAI-'),
              sg.T('Categoria:'), sg.Combo([], size=25, k='-TIPOMOV-')],
             [sg.T('Descrição:'), sg.I(size=50, k='-DESCMOV-'), sg.Push(), sg.T('Valor:'),
              sg.I(size=15, k='-VALORMOV-')]
             # disabled=True,
             ])
        coluna3_def = sg.Column([
            [sg.B('Adicionar', k='-AD-', bind_return_key=True)], [sg.B('Categorias', k='-NVCAT-')]
        ])
        coluna2_def = sg.Column([
            [sg.Checkbox('É recorrente?', k='-REC-')],
            [sg.T('Dia do mês:'), sg.I(size=3, k='-DIAREC-')],
            [sg.T('A partir de:'),
             sg.I(default_text=datetime.strftime(datetime.now(), '%d/%m/%Y'), k='-DATAREC-', size=10)]
        ])

        # bloco_def = [[coluna1_def], [coluna2_def]
        #             ]

        menu_def = [['&Arquivo', ['Adicionar aluno', 'Imprimir relatório', 'Informações do aluno', '---', '&Sair']],
                    # 'Save::savekey',
                    ['&Editar', ['!Configurações', 'Mudar tema'], ],
                    ['&Relatórios', ['Relatório mensal', 'Devedores']],
                    ['&Ferramentas', ['Backup parcial', 'Backup completo', 'Administração', ['Limpar banco de dados']]],
                    ['A&juda', ['Tela principal', 'Sobre...']], ]

        self.layout = [[sg.Menu(menu_def)],
                       [sg.Text('Contabilidade', font='_ 25', key='-CONT-')],
                       [sg.HorizontalSeparator(k='-SEP-')],
                       [sg.T('Mês:'), sg.Combo(meses, key='-MES-', default_value=mesatual(), enable_events=True),
                        sg.T('Ano:'),
                        sg.Combo(anos, key='-ANO-', default_value=datetime.strftime(datetime.now(), '%Y'),
                                 enable_events=True)],
                       [sg.Push(),
                        sg.Table(values=le_movimento(datetime.strftime(datetime.now(), '%m/%Y')), headings=self.titulos,
                                 # values=le_movimento(datetime.strftime(datetime.now(), '%m/%Y'))
                                 col_widths=self.largura,
                                 visible_column_map=self.visibilidade,
                                 auto_size_columns=False,  # justification='Left',
                                 k='-TABELA-',
                                 enable_events=True,
                                 expand_x=True,
                                 expand_y=True,
                                 num_rows=16), sg.Push()],
                       [sg.B('Alterar registro', k='-ALTERA-'), sg.B('Apagar registro', k='-APAGA-'),
                        sg.B('Gerar relatório em PDF', k='-RELPDF-'),
                        sg.Push(), sg.T('Saldo:'),
                        sg.I(default_text=locale.currency(calcula(datetime.strftime(datetime.now(), '%m/%Y'))),
                             size=10, k='-SALDO-')],
                       [sg.Frame('Movimento', [[coluna1_def, coluna2_def, coluna3_def]], k='-FRAME-')],
                       # s=(800, 100),
                       [sg.Push(), sg.Button('Sair', k='-SAIR-')]]

        return sg.Window('Contabilidade', self.layout, enable_close_attempted_event=True,
                         location=sg.user_settings_get_entry('-location-', (None, None)),
                         finalize=True)  # size=(800, 550)

    def __init__(self):
        self.layout = None
        self.val3 = None
        self.ev3 = None
        self.w_rel_men = None
        self.indiceinfo = None
        self.valalt = None
        self.evalt = None
        self.winalt = None
        self.janela_nvcat = None
        self.winnvcat = None
        self.val2 = None
        self.ev2 = None
        self.values = None
        self.event = None
        self.window = self.cria_janela()

    def atualiza(self):
        tmpmesano = str(convmes(self.values['-MES-'].rstrip())) + '/' + str(self.values['-ANO-'].rstrip())
        self.window['-TABELA-'].Update(le_movimento(tmpmesano))
        self.window['-SALDO-'].Update(value=locale.currency(calcula(tmpmesano)))

    def run(self):
        while True:  # Event Loop
            incorpora_tabelas(datetime.strftime(datetime.now(), '%m/%Y'))
            # incorpora_tabelas('06/2022')
            # loc = locale.getlocale()
            # print(loc)
            # var = calendar.day_name
            # for idx, x in enumerate(var):
            #    print(x)
            # self.window['-MES-'].update(mesatual())
            tmptipo = le_tipo()
            tipos = []
            for idx, x in enumerate(tmptipo):
                tipos.append(x[0])
            self.window['-TIPOMOV-'].update(values=sorted(tipos))
            # self.window['-TABELA-'].Update(le_movimento(''))
            # print(mesatual() + '/' + datetime.strftime(datetime.now(), '%Y'))

            # print(convmes(mesatual()))
            # print(datetime.strftime(datetime.now(), '%Y'))

            # mesano = str(self.values['-MES-'][0].rstrip()) + '/' + datetime.strftime(datetime.now(), '%Y')

            # self.window['-SALDO-'].Update(locale.currency(calcula('07/2022')))
            # mesano2 = datetime.strftime(datetime.now(), '%m/%Y')
            # print(mesano2)
            # print(self.values['-MES-'].rstrip())
            # tmpmesano = str(convmes(self.window['-MES-'])) + '/' + str(self.values['-ANO-'].rstrip())
            # self.window['-SALDO-'].Update(locale.currency(calcula(tmpmesano)))
            # self.window['-SALDO-'].Update(locale.currency(calcula(mesatual())))
            self.event, self.values = self.window.read()
            # print(self.values['-MES-'].rstrip())
            # tmpmesano = str(convmes(self.window['-MES-'])) + '/' + str(self.values['-ANO-'].rstrip())
            # self.window['-SALDO-'].Update(locale.currency(calcula(tmpmesano)))

            if self.event in ('Relatório mensal', '-RELPDF-'):
                mesano2 = str(convmes(self.values['-MES-'].rstrip())) + '/' + str(self.values['-ANO-'].rstrip())
                gera_pdf_mes(le_movimento(mesano2), self.values['-MES-'].rstrip(), locale.currency(calcula(mesano2)))
                self.window.perform_long_operation(lambda: os.system('\"' + pdfvw + '\" ' + arq_rel_mens),
                                                   '-FUNCTION COMPLETED-')

            if self.event in ('-MES-', '-ANO-'):
                self.atualiza()

            # print(self.values['-MES-'].rstrip())

            if self.event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT, '-SAIR-', 'Sair'):
                opcao, _ = sg.Window('Continuar?', [[sg.T('Tem certeza que deseja sair?')],
                                                    [sg.Yes(s=10, button_text='Sim'), sg.No(s=10, button_text='Não')]],
                                     disable_close=True, element_justification='center').read(close=True)
                if opcao == 'Sim':
                    # try:
                    sg.user_settings_set_entry('-location-', self.window.current_location())
                    # except:
                    #    sg.user_settings_set_entry('-location-', (None, None))
                    break

            #            if self.event == '-REC-':
            #                if self.values['-REC-']:
            #                    self.window['-DIAREC-'].update(disabled=False)
            #                if not self.values['-REC-']:
            #                    self.window['-DIAREC-'].update(disabled=True)

            ##########################################
            # Atualiza a linha selecionada na tabela
            ##########################################
            if self.event == '-TABELA-':
                # if self.event == 'bind_return_key':
                self.row = self.values[self.event]
                self.dados = self.window['-TABELA-'].Values
                # print(self.dados[self.row[0]][6])
                # print(self.dados[self.row[0]])

            if self.event == '-AD-':
                ##########################################
                # CHECAGEM DE VALORES ADICIONAR REGISTRO
                ##########################################
                if not re.fullmatch(regex_data, self.values['-DATAMOV-'].rstrip()):
                    sg.popup('Data inválida')
                elif self.values['-TIPOMOV-'].rstrip() == '':
                    sg.popup('Selecione uma categoria')
                elif self.values['-VALORMOV-'].rstrip == '':
                    sg.popup('Entre com um valor')
                elif not re.fullmatch(regex_dinheiro, self.values['-VALORMOV-'].rstrip()):
                    sg.popup('Valor inválido.')
                elif self.values['-REC-'] and self.values['-DIAREC-'] == '':
                    sg.popup('Entre com o dia da recorrência.')
                else:
                    if self.values['-EN-']:
                        tensai = 'ENTRADA'
                    else:
                        tensai = 'SAIDA'
                    if self.values['-REC-']:
                        grava_recorrente(self.values['-DIAREC-'].rstrip(), tensai, self.values['-TIPOMOV-'].rstrip(),
                                         self.values['-DESCMOV-'].rstrip(), self.values['-VALORMOV-'].rstrip())
                        incorpora_tabelas(datetime.strftime(datetime.now(), '%m/%Y'))
                        # mestmp = self.values['-DATAREC-'].rstrip() TODO Gravar recorrencia retroativamente
                    else:
                        grava_movimento(self.values['-DATAMOV-'].rstrip(), tensai, self.values['-TIPOMOV-'].rstrip(),
                                        self.values['-DESCMOV-'].rstrip(), self.values['-VALORMOV-'].rstrip(), 99)
                    self.window['-DESCMOV-'].update('')
                    self.window['-VALORMOV-'].update('')
                    self.window['-DIAREC-'].update('')
                    self.window['-REC-'].update(value=False)

                    # self.window['-TABELA-'].Update(le_movimento(''))
                    self.atualiza()
                    dttmp = self.values['-DATAMOV-'].rstrip()
                    grava_historico(dttmp[3:], False)
            ##########################################
            # ALTERAÇÃO DE REGISTRO
            #
            ##########################################
            if self.event == '-ALTERA-':
                if len(self.row) != 0 and self.dados[self.row[0]][6] != 100:
                    # if self.dados[self.row[0]][6] == 100:
                    #     print('SAIU COMO CEM')
                    #     sg.Popup('Este registro não pode ser alterado manualmente.')
                    #     self.winalt.close()
                    # print('DADOS[ROW]:', self.dados[self.row[0]])
                    # print('ROW INDEX:', self.dados[self.row[0]][0])
                    # self.indice = str(self.dados[self.row[0]][0])
                    # ObjMaisInfo = MaisInfo()
                    # self.indiceinfo = self.dados[self.row[0]][0]
                    lay_altera = [
                        [sg.Text('Alteração de registro', font='_ 25')],
                        [sg.HorizontalSeparator(k='-SEP-')],
                        [sg.T('Data:'), sg.I(s=10, k='-ADATA-'),
                         sg.CalendarButton('Data', locale='pt_BR', format='%d/%m/%Y',
                                           month_names=meses, day_abbreviations=dias),
                         sg.T('Tipo:'),
                         sg.Radio('Entrada', group_id='-AENSAI-', k='-AEN-', default=True),
                         sg.Radio('Saída', group_id='-AENSAI-', k='-ASAI-'),
                         sg.T('Categoria:'), sg.Combo([], size=25, k='-ATIPOMOV-')],
                        [sg.T('Descrição:'), sg.I(size=50, k='-ADESCMOV-'), sg.Push(), sg.T('Valor:'),
                         sg.I(size=15, k='-AVALORMOV-')],
                        [sg.Checkbox('É recorrente?', k='-AREC-', disabled=True),
                         sg.T('Dia do mês:'), sg.I(size=3, k='-ADIAREC-')],
                        [sg.T('Observação: você não pode alterar um registro '
                              'normal para um recorrente ou vice-versa.')],
                        [sg.T('Neste caso você deve apagar o registro e inserir um novo.')],
                        [sg.Push(), sg.B('Gravar alterações', k='-GRAVA-'), sg.B('Voltar', k='-VOLTAR-')]
                    ]
                    self.winalt = sg.Window('Altera registro', layout=lay_altera, finalize=True)
                    while True:
                        #    break
                        self.winalt['-ADATA-'].update(self.dados[self.row[0]][1])
                        if self.dados[self.row[0]][2] == 'ENTRADA':
                            self.winalt['-AEN-'].update(value=True)
                        else:
                            self.winalt['-ASAI-'].update(value=True)
                        self.winalt['-ATIPOMOV-'].update(values=tipos)
                        self.winalt['-ATIPOMOV-'].update(value=self.dados[self.row[0]][3])
                        self.winalt['-ADESCMOV-'].update(self.dados[self.row[0]][4])
                        self.winalt['-AVALORMOV-'].update(self.dados[self.row[0]][5])
                        # tempint = self.dados[self.row[0]][6]
                        # print(tempint)
                        if self.dados[self.row[0]][6] != 99:
                            temprecorrente = le_recorrente()
                            for idx, x in enumerate(temprecorrente):
                                if temprecorrente[idx][0] == self.dados[self.row[0]][6]:
                                    self.templinha.append(x)
                            # print(self.templinha)
                            # print(self.templinha[0][1])
                            self.winalt['-AREC-'].update(value=True)
                            self.winalt['-ADIAREC-'].update(value=self.templinha[0][1])
                            self.recorrente = True
                            self.winalt['-AREC-'].update(disabled=True)
                        self.evalt, self.valalt = self.winalt.read()
                        if self.evalt in (sg.WIN_CLOSED, '-VOLTAR-'):
                            self.winalt.close()
                            break
                        if self.evalt == '-GRAVA-':
                            ##########################################
                            # CHECAGEM DE VALORES ALTERACAO DE REGISTRO
                            ##########################################
                            if not re.fullmatch(regex_data, self.valalt['-ADATA-'].rstrip()):
                                sg.popup('Data inválida')
                            elif self.valalt['-ATIPOMOV-'].rstrip() == '':
                                sg.popup('Selecione uma categoria')
                            elif self.valalt['-AVALORMOV-'].rstrip == '':
                                sg.popup('Entre com um valor')
                            elif not re.fullmatch(regex_dinheiro, self.valalt['-AVALORMOV-'].rstrip()):
                                sg.popup('Valor inválido.')
                            # elif self.values['-REC-'] and self.values['-DIAREC-'] == '':
                            #     sg.popup('Entre com o dia da recorrência.')
                            else:
                                if self.valalt['-AEN-']:
                                    tensai = 'ENTRADA'
                                else:
                                    tensai = 'SAIDA'
                                if not self.recorrente:
                                    altera_movimento(self.valalt['-ADATA-'].rstrip(),
                                                     tensai, self.valalt['-ATIPOMOV-'].rstrip(),
                                                     self.valalt['-ADESCMOV-'].rstrip(),
                                                     self.valalt['-AVALORMOV-'].rstrip(), self.dados[self.row[0]][0])
                                else:
                                    altera_recorrente(self.valalt['-ADIAREC-'].rstrip(),
                                                      tensai, self.valalt['-ATIPOMOV-'].rstrip(),
                                                      self.valalt['-ADESCMOV-'].rstrip(),
                                                      self.valalt['-AVALORMOV-'].rstrip(), self.templinha[0][0]
                                                      )

                                self.atualiza()
                                strtmp = self.valalt['-ADATA-'].rstrip()
                                grava_historico(strtmp[3:], False)
                                sg.Popup('Registro alterado com sucesso.')
                                self.winalt.close()
                                break
                else:
                    sg.Popup('Selecione um registro da tabela.')

            if self.event == '-APAGA-':
                if len(self.row) != 0:
                    opcao, _ = sg.Window('Continuar?', [[sg.T('Tem certeza que deseja apagar o registro? '
                                                              'Esta operação é definitiva.')],
                                                        [sg.Yes(s=10, button_text='Sim'),
                                                         sg.No(s=10, button_text='Não')]],
                                         disable_close=True, element_justification='center').read(close=True)
                    if opcao == 'Sim':
                        print('A APAGAR: ', self.dados[self.row[0]])
                        datatmp = self.dados[self.row[0]][1]
                        print('DATATMP: ', datatmp)
                        print('É recorrente? ', self.dados[self.row[0]][6])
                        if self.dados[self.row[0]][6] == 99:
                            apaga_movimento(self.dados[self.row[0]][0])
                        else:
                            apaga_movimento(self.dados[self.row[0]][0])
                            apaga_recorrente(self.dados[self.row[0]][6])
                        # self.window['-TABELA-'].Update(le_movimento(''))

                        grava_historico(datatmp[3:], True)
                        self.atualiza()
                else:
                    sg.Popup('Selecione um registro da tabela.')

            if self.event == '-NVCAT-':
                layoutnvcat = [
                    [sg.Text('Categorias', font='_ 25', key='-TXTNVCAT-')],
                    [sg.HorizontalSeparator(k='-SEP-')],
                    [sg.T('Categorias existentes: '), sg.Combo([], k='-CATEGORIAS-', s=20),
                     sg.B('Apagar', k='-APAGA-')],
                    [sg.T('Cria nova categoria')],
                    [sg.Text('Nome da categoria:'), sg.I(size=30, k='-NOMECAT-')],
                    [sg.Push(), sg.B('Adicionar', k='-ADD-'), sg.B('Voltar', k='-VOLTAR-')]
                ]
                self.winnvcat = sg.Window('Categorias', layout=layoutnvcat, finalize=True)
                while True:
                    tmptipo = le_tipo()
                    tipos = []
                    for idx, x in enumerate(tmptipo):
                        tipos.append(x[0])
                    self.winnvcat['-CATEGORIAS-'].update(values=sorted(tipos))
                    self.ev2, self.val2 = self.winnvcat.read()
                    if self.ev2 in (sg.WIN_CLOSED, '-VOLTAR-'):
                        self.winnvcat.close()
                        break

                    if self.ev2 == '-APAGA-':
                        print(self.val2['-CATEGORIAS-'].rstrip())
                        apaga_tipo(self.val2['-CATEGORIAS-'].rstrip())
                        # TODO apaga categoria
                    if self.ev2 == '-ADD-':
                        grava_tipo(self.val2['-NOMECAT-'].rstrip())
                        for idx, x in enumerate(tmptipo):
                            tipos.append(x[0])
                        self.window['-TIPOMOV-'].update(sorted(tipos))

            ##########################################
            # RELATORIOS
            # RELATORIO MENSAL
            ##########################################
            if self.event == 'Relatório mensal':
                layout_rel_mens = [
                    [sg.Text('Relatório mensal', font='_ 25', key='-TXTNVCAT-')],
                    [sg.HorizontalSeparator(k='-SEP-')],
                    [sg.T('Mês do relatório:'),
                     sg.Combo(meses, key='-MES-', default_value=mesatual(), enable_events=True),
                     sg.T('Ano:'), sg.Combo(anos, key='-ANO-', default_value=datetime.strftime(datetime.now(), '%Y'),
                                            enable_events=True)],
                    [sg.Table(values=le_movimento(datetime.strftime(datetime.now(), '%m/%Y')), headings=self.titulos,
                              col_widths=self.largura,
                              visible_column_map=self.visibilidade,
                              auto_size_columns=False,  # justification='Left',
                              k='-TABELA-',
                              enable_events=True,
                              expand_x=True,
                              expand_y=True,
                              num_rows=20)],
                    [sg.Push(), sg.T('Saldo:'),
                     sg.I(default_text=locale.currency(calcula(datetime.strftime(datetime.now(), '%m/%Y'))),
                          size=10, k='-SALDO-')],
                    [sg.Push(), sg.Button('Voltar', k='-VOLTAR-')]
                ]
                self.w_rel_men = sg.Window('Categorias', layout=layout_rel_mens, finalize=True)
                while True:
                    self.ev3, self.val3 = self.w_rel_men.read()
                    if self.ev3 in (sg.WIN_CLOSED, '-VOLTAR-'):
                        self.w_rel_men.close()
                        break
                    if self.ev3 in ('-MES-', '-ANO-'):
                        tmpmesano = str(convmes(self.val3['-MES-'].rstrip())) + '/' + str(self.val3['-ANO-'].rstrip())
                        self.w_rel_men['-TABELA-'].Update(le_movimento(tmpmesano))
                        self.w_rel_men['-SALDO-'].Update(value=locale.currency(calcula(tmpmesano)))

            ##########################################
            # RELATORIOS
            # RELATORIO ANUAL
            ##########################################
            # TODO relatório anual
        self.window.close()


# Ajustes feitos antes de rodar o programa
# locale.setlocale(locale.LC_ALL, 'pt_BR')
# calendar.setfirstweekday(calendar.SUNDAY)
# sg.user_settings_filename(path=dirajustes)
# Ajustes feitos antes de rodar o programa

# recebido_mensal(datetime.strftime(datetime.now(), '%m/%Y'))
# recebido_mensal('06/2022')
# incorpora_tabelas()
# contabilidade = Contabil()
# contabilidade.run()
# gera_df()
# gera_pdf_mes(le_movimento(datetime.strftime(datetime.now(), '%m/%Y')), 'Maio', '100,00')
