# from tkinter import DISABLED
# from turtle import update
# import subprocess
import PySimpleGUI as sg
import sqlite3
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import os
import re
import shutil
import locale

# from PySimpleGUI import TABLE_SELECT_MODE_BROWSE

import contabil
# from colorama import Back
# from requests import NullHandler
# from tkhtmlview import *
from fpdf import FPDF

################################################################
# OBSERVACAO: PARA O FPDF FUNCIONAR, EXECUTE EM UM CMD ELEVADO:
# setx /M SYSTEM_TTFFONTS C:\Windows\fonts
# INVALIDO: COPIE AS FONTES PARA A PASTA DO PROGRAMA
################################################################

################################################################
# PARA GERAR O EXECUTAVEL:
# pyinstaller principal.spec
################################################################

################################################################
# PROGRAMA DE GERENCIAMENTO DE ALUNOS LOTUS
#
# A FAZER
# - intervalos - parar de cobrar a mensalidade quando uma pessoa fizer um intervalo
# - planos - planos de 3 meses pré pagos para vender
# - implementar log de erros de acordo com
# https://stackoverflow.com/questions/3383865/how-to-log-error-to-file-and-not-fail-on-exception
# - mudar a cor da linha na tabela quando um aluno estiver em pausa
# - mudar a cor da linha quando um aluno estiver com um plano
################################################################


# sg.theme(sg.user_settings_get_entry('-tema-', 'DarkBlue2'))

# sg.set_options(use_custom_titlebar=True)
locale.setlocale(locale.LC_ALL, '')

dbfile = os.path.join(os.getcwd(), 'db', 'sistema.db')
mdbfile = os.path.join(os.getcwd(), 'db', 'mensalidades.db')
imagem = os.path.join(os.getcwd(), 'recursos', 'logo.png')
imagem_peq = os.path.join(os.getcwd(), 'recursos', 'logo_small.png')
icone = os.path.join(os.getcwd(), 'recursos', 'logo_icon.ico')
ajustes = os.path.join(os.getcwd(), 'ajustes')
pdfviewer = os.path.join(os.getcwd(), 'recursos', 'SumatraPDF.exe')
meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro',
         'Novembro', 'Dezembro']
dias = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab']

# ultimobkp = '10/06/2022'
ajuda = ''
regexTelefone = re.compile(r'^\(?[1-9]{2}\)? ?(?:[2-8]|9[1-9])[0-9]{3}(\-|\.)?[0-9]{4}$')  # OK
# ORIGINAL PARA TELEFONE: ^\(?[1-9]{2}\)? ?(?:[2-8]|9[1-9])[0-9]{3}\-?[0-9]{4}$
regexCPF = re.compile(r'\d{3}\.\d{3}\.\d{3}\-\d{2}')
regexDinheiro = re.compile(r'^(\d{1,}\d+\,\d{2}?)$')  # OK
regexEmail = re.compile(r'^[\w\.]+@([\w-]+\.)+[\w-]{2,4}$')  # OK
regexDia = re.compile(r'\b[0-3]{0,1}[0-9]{1}\b')  # OK
arq_recibo = 'recibo.pdf'
arq_relatorio = 'relatorio.pdf'
sg.theme(sg.user_settings_get_entry('-tema-'))


# sg.show_debugger_popout_window()

# INICIO FUNCAO RECRIA BANCO DE DADOS


def novobanco():
    try:
        shutil.copyfile(dbfile, dbfile + '.bkp')
    except:
        print('erro')
    if os.path.exists(dbfile):
        os.remove(dbfile)
    conn = sqlite3.connect(dbfile)
    conn.close()

    conn = sqlite3.connect(dbfile)
    # definindo um cursor
    cursor = conn.cursor()

    # criando a tabela (schema)
    cursor.execute("""
    CREATE TABLE "Alunos" (
    "al_index"	INTEGER,
    "al_nome"	TEXT,
    "al_endereco"	TEXT,
    "al_telefone01"	TEXT,
    "al_cpf"	TEXT,
    "al_email"	TEXT,
    "al_dt_matricula"	TEXT,
    "al_dt_vencto"	TEXT,
    "al_valmens"	TEXT,
    "al_ultimopagto"	TEXT,
    "al_ativo"	TEXT,
    PRIMARY KEY("al_index")
    );
    """)

    conn.close()

    conn = sqlite3.connect(dbfile)
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE "Financeiro" (
    "fi_nome"	INTEGER,
    "fi_data_pgto"	TEXT,
    "fi_atraso"	TEXT,
    "fi_valor_rec"	TEXT,
    "fi_recebido"	TEXT,
    FOREIGN KEY("fi_nome") REFERENCES "Alunos"("al_index")
    );
    """)

    conn.close()


# FINAL FUNCAO RECRIA BANCO DE DADOS

# FUNCAO VERIFICA SE TABELA EXISTE
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


# FUNCAO CRIA TABELA NO DB MENSALIDADES
def mensalidades_cria(index):
    nometabela = 'mens_' + str(index)
    conexao = sqlite3.connect(mdbfile)
    comando = ('create table if not exists ' + nometabela + '(me_index INTEGER PRIMARY KEY, me_mesano TEXT, '
                                                            'me_diaven TEXT, me_valor TEXT, me_datapgto '
                                                            'TEXT, me_vlrmulta TEXT, me_vlrextras TEXT, me_vlrpago '
                                                            'TEXT, '
                                                            'me_pg INTEGER, me_atraso TEXT);')
    if not tableexists(conexao, nometabela):
        c = conexao.cursor()
        c.execute(comando)
    conexao.close()


# FUNCAO INSERE DADOS NA TABELA MENSALIDADE
def mensalidades_insere(index, mesano, diaven, valor, datapgto, vlrmulta, vlrextras, vlrpago, pg, atraso):
    # RETORNA 0 SE NAO EXISTIR O REGISTRO, 1 SE EXISTIR E FOR ATUALIZADO, 2 SE EXISTIR E JÁ FOI PAGO
    inseredtultpgto = False
    dados = [mesano, diaven, valor, datapgto, vlrmulta, vlrextras, vlrpago, pg, atraso]
    conexao = sqlite3.connect(mdbfile)
    resultado = 0
    c = conexao.cursor()
    nometabela = 'mens_' + str(index)
    # primeiro, checa se o registro já existe
    comando = 'SELECT * FROM ' + nometabela
    c.execute(comando)
    cdados = c.fetchall()
    if cdados:
        # se existe, checa se já foi pago
        for idx, x in enumerate(cdados):
            if x[1] == mesano and x[8] != 1:
                # se a data da mensalidade for igual a data entrada na funcao, e
                # se a coluna me_pg for != 1 (ou seja não pago)
                dadosupdt = [mesano, diaven, valor, datapgto, vlrmulta, vlrextras, vlrpago, pg, atraso, x[0]]
                comando = 'UPDATE' + nometabela + ' SET me_mesano = ?, me_diaven = ?,me_valor = ?, me_datapagto = ?, me_vlrmulta = ?, me_vlrextras = ?, me_vlrpago = ?, me_pg = ?, me_atraso = ? WHERE me_index = ?'
                c.execute(comando, dadosupdt)
                resultado = 1
                inseredtultpgto = True
            if x[1] == mesano and x[8] == 1:
                resultado = 2
    else:
        comando = 'INSERT INTO ' + nometabela + '(me_mesano,me_diaven,me_valor,me_datapgto' \
                                                ',me_vlrmulta,me_vlrextras,me_vlrpago,me_pg,me_atraso) VALUES (?,?,?,?,?,?,?,?,?)'
        c.execute(comando, dados)
        resultado = 0
        inseredtultpgto = True
    conexao.commit()
    conexao.close()
    if inseredtultpgto:
        # insere a data do ultimo pagamento na tabela alunos
        secinsert = [datapgto, index]
        conexao = sqlite3.connect(dbfile)
        c = conexao.cursor()
        c.execute('UPDATE Alunos SET al_ultimopagto = ? WHERE al_index = ?', secinsert)
        conexao.commit()
        conexao.close()
    return resultado


def mensalidades_atraso(index):
    # RETORNA UMA LISTA DATA DAS MENSALIDADES EM ATRASO.
    conexao = sqlite3.connect(mdbfile)
    mensatraso = []
    c = conexao.cursor()
    nometabela = 'mens_' + str(index)
    comando = 'SELECT * FROM ' + nometabela
    c.execute(comando)
    cdados = c.fetchall()
    if cdados:
        for idx, x in enumerate(cdados):
            if x[8] != 1:
                mensatraso.append(x[1])
    conexao.close()
    return mensatraso


# FUNCAO PUXA TODOS OS DADOS DO REGISTRO ATRASADO NA TABELA MENSALIDADES
def mensalidades_ler_atrasado(index, mesano):
    conexao = sqlite3.connect(mdbfile)
    c = conexao.cursor()
    # dados = [mesano]
    nometabela = 'mens_' + str(index)
    comando = 'SELECT * FROM ' + nometabela + ' WHERE me_mesano = ?'
    c.execute(comando, (mesano,))
    dados = c.fetchall()[0]
    conexao.close()
    return dados


# FUNCAO LISTA MENSALIDADES ANTIGAS
def mensalidades_lista(index):
    conexao = sqlite3.connect(mdbfile)
    c = conexao.cursor()
    nometabela = 'mens_' + str(index)
    comando = 'SELECT me_index, me_datapagto, me_atraso, me_valor, me_vlrpago FROM ' + nometabela
    c.execute(comando)
    dados = c.fetchall()
    conexao.close()
    return dados


# FUNCAO ATUALIZA AS TABELAS MENSALIDADES COM OS NAO PAGADORES
def mensalidades_atualiza():
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    c.execute('SELECT al_index, al_dt_vencto, al_valmens, al_ativo FROM Alunos')
    indices = c.fetchall()
    conexao.close()
    for idx, x in enumerate(indices):
        if x[3] == 'S':
            mensalidades_cria(x[0])
            # nometabela = 'mens_' + str(x[0])
            # conexao = sqlite3.connect(mdbfile)
            # c = conexao.cursor()
            # comando = 'SELECT me_mesano FROM {0} '.format(nometabela)
            # c.execute(comando)
            # dados = c.fetchall()


# FUNCAO LE A TABELA PLANOS
def planos_ler():
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    c.execute('SELECT * FROM Planos')
    resultado = c.fetchall()
    conexao.close()
    return resultado


# FUNCAO BUSCA OS DADOS DO PLANO INSCRITO DO ALUNO
def planos_busca(index):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    c.execute('SELECT al_planoindex, al_plano, al_pl_inicio, al_pl_fim FROM Alunos WHERE al_index = ?', (index,))
    resultado = c.fetchone()
    conexao.close()
    return resultado


# ESCREVE OS DADOS DO PLANO DO ALUNO
def planos_escreve(index, planoindex, plano, inicio, fim):
    conexao = sqlite3.connect(dbfile)
    dados = [planoindex, plano, inicio, fim, index]
    c = conexao.cursor()
    c.execute('UPDATE Alunos SET al_planoindex = ?, al_plano = ?, al_pl_inicio = ?, al_pl_fim = ? WHERE al_index = ?',
              dados)
    conexao.commit()
    conexao.close()


# FUNCAO PEGA O al_index DO ULTIMO REGISTRO DA TABELA
def alunos_ultimo():
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    c.execute('SELECT max(al_index) FROM Alunos')
    dados = c.fetchone()[0]
    #    for linha in c.fetchall():
    #        print(linha)
    conexao.close()
    return dados


# INICIO FUNCAO MES ATUAL
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


# FINAL FUNCAO MES ATUAL

# INICIO FUNCAO GERA RECIBO
def gera_recibo_pdf(nome, valorpago, datapgto, datavencto, atraso, usuario):
    rpdf = FPDF('P', 'cm', 'A4')
    rpdf.add_page()
    rpdf.add_font('Calibri', 'I', 'Calibrii.ttf', uni=True)
    rpdf.add_font('Calibri', 'B', 'Calibrib.ttf', uni=True)
    rpdf.add_font('Calibri', '', 'Calibri.ttf', uni=True)
    rpdf.set_font('Calibri', 'B', 14)
    rpdf.image(imagem_peq, 16.6, 1.6)
    rpdf.rect(1, 1, 19, 8.8, 'D')
    rpdf.cell(0, 0.6, '', 0, 2, 'C')
    rpdf.cell(0, 0.6, 'RECIBO DE PAGAMENTO DE MENSALIDADE', 0, 2, 'C')
    rpdf.cell(0, 0.6, 'Lótus Condicionamento Dinâmico Integrado', 0, 2, 'C')
    rpdf.cell(0, 0.6, 'Andréia de Cássia Gonçalves (CREF 020951-G/MG)', 0, 2, 'C')
    rpdf.set_font('Calibri', 'I', 14)
    rpdf.cell(0, 0.6, 'Rua Coronel Paiva, 12  Centro  Ouro Fino MG', 0, 2, 'C')
    rpdf.line(1, 4.5, 20, 4.5)
    rpdf.set_font('Calibri', 'B', 14)
    rpdf.cell(0.5, 1, '', 0, 1)
    rpdf.cell(0.5, 1, '')
    rpdf.cell(3.5, 1, 'Nome do aluno: ')
    rpdf.set_font('Calibri', '', 14)
    rpdf.cell(0, 1, nome, 0, 1)
    rpdf.set_font('Calibri', 'B', 14)
    rpdf.cell(0.5, 1, '')
    rpdf.cell(4.6, 1, 'Valor do pagamento: ')
    rpdf.set_font('Calibri', '', 14)
    rpdf.cell(2.5, 1, valorpago)
    rpdf.set_font('Calibri', 'B', 14)
    rpdf.cell(0.5, 1, '')
    rpdf.cell(4.5, 1, 'Data do pagamento: ')
    rpdf.set_font('Calibri', '', 14)
    rpdf.cell(1, 1, datapgto, 0, 1)
    rpdf.set_font('Calibri', 'B', 14)
    rpdf.cell(0.5, 1, '')
    rpdf.cell(4.6, 1, 'Dia do vencimento: ')
    rpdf.set_font('Calibri', '', 14)
    rpdf.cell(3, 1, datavencto)
    rpdf.set_font('Calibri', 'B', 14)
    rpdf.cell(1.7, 1, 'Atraso: ')
    rpdf.set_font('Calibri', '', 14)
    rpdf.cell(1, 1, atraso + ' dias', 0, 1)
    rpdf.cell(0.5, 1, '')
    rpdf.set_font('Calibri', 'B', 14)
    rpdf.cell(3.2, 1, 'Recebido por: ')
    rpdf.set_font('Calibri', '', 14)
    rpdf.cell(2.5, 1, usuario)
    # rpdf.cell(19, 10, 'Hello World!', 1)
    # rpdf.cell(40, 10, 'Hello World!', 1)
    # rpdf.cell(60, 10, 'Powered by FPDF.', 0, 1, 'C')
    # rpdf.output(arq_recibo, 'F')
    rpdf.output(arq_recibo)


# FINAL FUNCAO GERA RECIBO


# INICIO FUNCAO APAGA REGISTROS
def apaga_registro(index):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    c.execute('DELETE FROM Financeiro WHERE fi_nome = ?', (index,))
    c.execute('DELETE FROM Alunos WHERE al_index = ?', (index,))
    conexao.commit()
    conexao.close()


# FINAL FUNCAO APAGA REGISTROS

# INICIO FUNCAO LEITURA DOS DADOS
def ler_todos_dados():
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    c.execute("""
                SELECT al_index,al_nome,al_endereco,al_telefone01,al_cpf,
                al_email,al_dt_matricula,al_dt_vencto,al_valmens,al_ultimopagto,al_ativo FROM Alunos;
            """)
    dados = c.fetchall()
    #    for linha in c.fetchall():
    #        print(linha)
    conexao.close()
    return dados


# FINAL FUNCAO LEITURA DOS DADOS

# INICIO FUNCAO LEITURA DOS DADOS ATIVOS
def ler_todos_dados_ativos():
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    c.execute("""
                SELECT al_index,al_nome,al_endereco,al_telefone01,al_cpf,
                al_email,al_dt_matricula,al_dt_vencto,al_valmens,
                al_ultimopagto,al_ativo FROM Alunos WHERE al_ativo = 'S';
            """)
    dados = c.fetchall()
    #    for linha in c.fetchall():
    #        print(linha)
    conexao.close()
    return dados


# FINAL FUNCAO LEITURA DOS DADOS ATIVOS

# FUNCAO - LOCALIZAR ALUNO
def buscar_por_nome(nome, ret_ativos):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    # print(nome)
    nome = ('%' + nome + '%')
    # print(nome)
    if ret_ativos:
        c.execute(
            'SELECT al_index,al_nome,al_endereco,al_telefone01,al_cpf,al_email,al_dt_matricula,al_dt_vencto,'
            'al_valmens,al_ultimopagto,al_ativo FROM Alunos WHERE al_nome like ? AND al_ativo = "S" ',
            (nome,))
    if not ret_ativos:
        c.execute(
            'SELECT al_index,al_nome,al_endereco,al_telefone01,al_cpf,al_email,al_dt_matricula,al_dt_vencto,'
            'al_valmens,al_ultimopagto,al_ativo FROM Alunos WHERE al_nome like ?',
            (nome,))
    resultado = c.fetchall()
    # print(resultado)
    conexao.close()
    return resultado


# FIM FUNCAO - LOCALIZAR ALUNO


# FUNCAO - CADASTRO DE ALUNO
def cadastrar_aluno(nome, endereco, tel1, cpf, email, mat, venc, valmens, ativo):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    dadosinsert = [nome, endereco, tel1, cpf, email, mat, venc, valmens, ativo]
    c.execute(
        "INSERT INTO Alunos(al_nome,al_endereco,al_telefone01,al_cpf,al_email,al_dt_matricula,al_dt_vencto,"
        "al_valmens,al_ativo) VALUES (?,?,?,?,?,?,?,?,?)",
        dadosinsert)
    conexao.commit()
    conexao.close()


# FIM FUNCAO - CADASTRO DE ALUNO

# FUNCAO ADICIONA VENDA

def venda_adiciona(relalunos, data, desc, valor, cobra, formapgt, pg):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    dadosinsert = [relalunos, data, desc, valor, cobra, formapgt, pg]
    c.execute(
        "INSERT INTO Vendas(ve_relalunos,"
        " ve_data, ve_desc, ve_valor, ve_cobra, ve_formapgt, ve_pg) VALUES (?,?,?,?,?,?,?)",
        dadosinsert)
    conexao.commit()
    conexao.close()


# FUNCAO LE VENDA

def venda_busca(indicealuno):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    iterable = [indicealuno]
    c.execute("""
                    SELECT ve_index,ve_data,ve_desc,ve_valor,
                    ve_cobra,ve_formapgt,ve_pg FROM Vendas WHERE ve_relalunos = ?;
                """, iterable)
    dados = c.fetchall()
    conexao.close()
    return dados


# FUNCAO RECEBE VENDA

def venda_recebe(indice, data):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    data = ('%' + data + '%')
    vcobraset = 'NAO'
    vcobracompara = 'SIM'
    dados = [vcobraset, indice, data, vcobracompara]
    c.execute(
        "UPDATE Vendas SET ve_cobra = ? WHERE ve_relalunos = ? AND ve_data like ? AND ve_cobra = ?", dados)
    conexao.commit()
    conexao.close()


# FUNCAO ALTERA CADASTRO DE ALUNO
def alterar_aluno(nome, endereco, tel1, tel2, email, mat, venc, valmens, ativo, indice):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    dadosinsert = [nome, endereco, tel1, tel2, email, mat, venc, valmens, ativo, indice]
    c.execute(
        "UPDATE Alunos SET al_nome = ?, al_endereco = ?, al_telefone01 = ?, al_cpf = ?, al_email = ?, al_dt_matricula "
        "= ?, al_dt_vencto = ?, al_valmens = ?, al_ativo = ? WHERE al_index = ?",
        dadosinsert)
    conexao.commit()
    conexao.close()


# FIM FUNCAO ALTERA CADASTRO DE ALUNO

# FUNCAO LE ARQUIVO DE TEXTO
def abrir_texto(nomearquivo):
    f = open(os.path.join(os.getcwd(), 'ajuda', nomearquivo))
    texto = f.read()
    f.close()
    return texto


# FIM FUNCAO LE ARQUIVO DE TEXTO


# DEF BUSCA DADOS NA TABELA FINANCEIRO
def busca_dados_financeiros(indice):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    # c.execute('SELECT al_nome,al_endereco,al_telefone01,al_telefone02,al_email,al_dt_matricula,al_dt_vencto FROM
    # Alunos WHERE al_index = ?', (indice,))
    c.execute(
        'SELECT fi_nome,fi_data_pgto,fi_atraso,fi_valor_rec,fi_recebido FROM Financeiro fin JOIN Alunos al on '
        'fin.fi_nome = al.al_index WHERE al.al_index = ?',
        (indice,))
    resultado = c.fetchall()
    # print('tamanho resultado')
    # print(len(resultado))
    conexao.close()
    return resultado


# FIM DEF BUSCA DADOS NA TABELA FINANCEIRO

def mensalidade_busca(index):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    # c.execute('SELECT al_nome,al_endereco,al_telefone01,al_telefone02,al_email,al_dt_matricula,al_dt_vencto FROM
    # Alunos WHERE al_index = ?', (indice,))
    c.execute(
        'SELECT fi_data_pgto FROM Financeiro WHERE fi_nome = ?', (index,))
    resultado = c.fetchall()
    conexao.close()
    return resultado


# FUNCAO APAGA DADOS FINANCEIROS
def apaga_dados_financeiros(aluno, data):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    c.execute('DELETE FROM Financeiro WHERE fi_nome = ? AND fi_data_pgto = ?', (aluno, data))
    # c.execute('SELECT fi_nome,fi_data_pgto,fi_atraso,fi_valor_rec,fi_recebido FROM Financeiro fin JOIN Alunos al on
    # fin.fi_nome = al.al_index WHERE al.al_index = ?', (indice,))
    conexao.commit()
    conexao.close()


# FINAL FUNCAO APAGA DADOS FINANCEIROS


# FUNCAO GERA RELATORIO FINANCEIRO MENSAL
def rel_fin_mensal(mesano):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()

    # c.execute('SELECT al_nome,al_endereco,al_telefone01,al_telefone02,al_email,al_dt_matricula,al_dt_vencto FROM
    # Alunos WHERE al_index = ?', (indice,))

    # c.execute('SELECT fi_data_pgto,fi_atraso,fi_valor_rec,fi_recebido FROM Financeiro fin JOIN Alunos al on
    # fin.fi_nome = al.al_index WHERE al.al_index = ?', (indice,))

    mesano = ('%' + mesano + '%')
    #    c.execute('SELECT fi_nome,* FROM Financeiro WHERE fi_data_pgto LIKE ?', (mesano,))
    c.execute(
        'SELECT * FROM Financeiro JOIN Alunos on Financeiro.fi_nome = Alunos.al_index WHERE fi_data_pgto LIKE ? AND '
        'Alunos.al_ativo = "S"',
        (mesano,))
    resultado = c.fetchall()
    # print(resultado)
    # FILTRANDO O RESULTADO:
    # print(resultado)
    i = 0
    res_filtrado = resultado
    while i < len(resultado):
        res_filtrado[i] = resultado[i][1], resultado[i][6], resultado[i][2], resultado[i][4], resultado[i][3]
        # fi_data_pgto, al_nome, fi_atraso, fi_recebido, fi_valor_recebido
        # print(resultado[i][1])
        i = i + 1
    # print(resultado)
    # print(res_filtrado)
    # print(len(resultado))
    conexao.close()
    return res_filtrado


# FIM GERA RELATORIO FINANCEIRO MENSAL

# FUNCAO GERA RELATORIO NAO PAGADORES
def rel_nao_pagadores(mesano, opcao):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    # c.execute('SELECT al_nome,al_endereco,al_telefone01,al_telefone02,al_email,al_dt_matricula,al_dt_vencto FROM
    # Alunos WHERE al_index = ?', (indice,))

    # c.execute('SELECT fi_data_pgto,fi_atraso,fi_valor_rec,fi_recebido FROM Financeiro fin JOIN Alunos al on
    # fin.fi_nome = al.al_index WHERE al.al_index = ?', (indice,))

    # mesano = ('%'+ mesano + '%')
    #    c.execute('SELECT fi_nome,* FROM Financeiro WHERE fi_data_pgto LIKE ?', (mesano,))
    # print(mesano)
    # c.execute('SELECT al_nome,al_ultimopagto,al_valmens FROM Alunos WHERE al_ultimopagto NOT like ?',(mesano,))
    c.execute('SELECT al_nome,al_ultimopagto,al_valmens,al_dt_vencto FROM Alunos')
    resultado_par = c.fetchall()
    conexao.close()
    mesanant = ''
    mes = mesano[0:2]  # SEPARA O MES
    ano = mesano[3:7]  # SEPARA O ANO
    if mes == '01':  # TESTA PARA JANEIRO
        mes = 12
        ano = int(ano) - 1
    # mesanterior = str(mes) + '/' + str(ano)
    else:
        mescalc = int(mes) - 1  # TIRA 1 DO MES (TRANSFORMA NO MES ANTERIOR)
        # mesanterior = str(mescalc) + '/' + ano  # TRANSFORMA mesanterior EM STRING MES + ANO
        mescalc = int(mes) - 1  # SUBTRAI MAIS UM DO MES (TRANSFORMA NO AN ANTERIOR)
        mesanant = str(mescalc) + '/' + ano
    # print(mesano2)
    # dmesanterior = datetime.strptime(mesanterior, '%m/%Y').date()
    dmesanant = datetime.strptime(mesanant, '%m/%Y').date()
    dmesatual = datetime.strptime(mesano, '%m/%Y').date()
    # dif = data1 - data2
    # print(str(dif))
    resultado = []
    i = 0
    while i < len(resultado_par):
        # print(resultado_par[i])
        if resultado_par[i][1] is not None:
            temp2 = resultado_par[i][1]
            temp2 = temp2[3:10]
            # print('temp2 ',temp2)
            # print('data2 ',data2)
            datatemp = datetime.strptime(temp2, '%m/%Y').date()
            # print('Datatemp ', datatemp)
            if opcao == 'atual':
                if datatemp < dmesatual and datatemp == dmesanant:
                    # print('datatemp<data2')
                    resultado.append(resultado_par[i])
                    # print(resultado)
            if opcao == 'anteriores':
                if datatemp < dmesatual:
                    # print('datatemp<data2')
                    resultado.append(resultado_par[i])
                    # print(resultado)
        else:
            resultado.append(resultado_par[i])
        i = i + 1

    return resultado


# FIM GERA RELATORIO NAO PAGADORES

# FUNCAO INSERE DADOS NA TABELA FINANCEIRO
def insere_dados_financeiros(indice, datapagto, atraso, valrec, recpor):
    dadosinsert = [indice, datapagto, atraso, valrec, recpor]
    secinsert = [datapagto, indice]
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    c.execute('INSERT INTO Financeiro (fi_nome,fi_data_pgto,fi_atraso,fi_valor_rec,fi_recebido) VALUES (?,?,?,?,?)',
              dadosinsert)
    c.execute('UPDATE Alunos SET al_ultimopagto = ? WHERE al_index = ?', secinsert)
    conexao.commit()
    # print('tamanho resultado')
    # print(len(resultado))
    conexao.close()


# FINAL FUNCAO INSERE DADOS NA TABELA FINANCEIRO


# FUNCAO BUSCA ALUNO POR INDICE
def buscar_aluno_index(indice):
    conexao = sqlite3.connect(dbfile)
    c = conexao.cursor()
    c.execute(
        'SELECT al_index,al_nome,al_endereco,al_telefone01,al_cpf,al_email,al_dt_matricula,al_dt_vencto,al_valmens,'
        'al_ultimopagto,al_ativo FROM Alunos WHERE al_index = ?',
        (indice,))
    #    c.execute('SELECT * from Alunos WHERE al_index = ?', (indice,))
    resultado = c.fetchone()
    # print('resultado')
    # print(resultado)
    conexao.close()
    return resultado


# FINAL FUNCAO BUSCA ALUNO POR INDICE

# INICIO SPLASH SCREEN
def splashscreen():
    imgfile = imagem
    display_time_milliseconds = 1500  # DISPLAY_TIME_MILLISECONDS
    sg.Window('Window Title', [[sg.Image(filename=imgfile)]], transparent_color=sg.theme_background_color(),
              no_titlebar=True).read(timeout=display_time_milliseconds, close=True)  # keep_on_top=True


# FINAL SPLASH SCREEN

# FUNCAO CALCULA DIFERENCA ENTRE DATAS RETORNA DIAS
def diferenca_datas(date1, date2):
    d1 = datetime.strptime(date1, "%d/%m/%Y")
    d2 = datetime.strptime(date2, "%d/%m/%Y")
    resultado = (d2 - d1).days
    if resultado <= 0:
        resultado = 0
    else:
        resultado = abs(resultado)
    return resultado


# FINAL FUNCAO CALCULA DIFERENCA ENTRE DATAS RETORNA DIAS

# FUNCAO GERA DATA VENCIMENTO
def geravencto(datavencto):
    tdata = date.today()
    mesano = tdata.strftime("%m/%Y")
    datavencimento = (str(datavencto) + '/' + mesano)
    # print(datavencimento)
    return datavencimento


# FINAL FUNCAO GERA DATA VENCIMENTO

# INICIO JANELA AJUDA
class Ajuda:
    nomearquivo = ''

    def __init__(self):
        self.values = None
        self.event = None
        self.layout = [
            [sg.Text('Ajuda do programa', font='_ 25', key='-TITULO-')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.Multiline(disabled=True, size=(50, 20), k='-TEXTO-')],
            [sg.Button('Fechar', k='-FECHAR-')]
        ]

        self.window = sg.Window('Ajuda', self.layout,
                                default_element_size=(12, 1), finalize=True, modal=True, disable_minimize=True,
                                location=(10, 10))

    def run(self):
        while True:
            self.window['-TEXTO-'].update(abrir_texto(self.nomearquivo))
            # janelahtml = HTMLScrolledText(self.window.TKroot, html=abrir_texto(self.nomearquivo), width=60, height=20)
            # janelahtml.pack()
            self.event, self.values = self.window.read()
            if self.event == sg.WIN_CLOSED or self.event == '-FECHAR-':
                break
        self.window.close()


# FINAL JANELA AJUDA

# INICIO RECEBE MENSALIDADE
class Recebe:
    indicealuno = 2
    tam_texto = (10, 1)
    tam_input = (10, 1)
    diasatraso = 0
    nome_aluno = ''

    def __init__(self):
        self.values = None
        self.event = None
        self.layout = [
            [sg.Text('nome', font='_ 25', key='-NOMEALUNO-')],
            # [sg.Text('nome',relief='sunken', font=('italic'),key='-NOMEALUNO-')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.Text('Vencimento:', size=self.tam_texto), sg.Input(k='-DATAVEN-', size=self.tam_input, disabled=True),
             sg.Push(), sg.Text('Valor:', size=self.tam_texto),
             sg.Input(k='-VALMENS-', size=self.tam_input, disabled=True)],
            [sg.Text('Pagamento:', size=self.tam_texto, ),
             sg.Input(k='-DATAPAGTO-', size=self.tam_input, default_text=datetime.strftime(datetime.now(), '%d/%m/%Y')),
             sg.CalendarButton('Data', locale='pt_BR', format='%d/%m/%Y', month_names=meses, day_abbreviations=dias),
             sg.Push(), sg.Text('Atraso:', size=self.tam_texto), sg.Input(k='-ATRASO-', size=self.tam_input)],
            [sg.Text('Recebido:', self.tam_texto), sg.Input(k='-VALREC-', size=self.tam_input),
             sg.Push(), sg.Text('Multa:', self.tam_texto), sg.Input(k='-VALMULTA-', size=self.tam_input)],
            [sg.Text('Usuário:', size=self.tam_texto), sg.Input(k='-USUARIO-', size=(18, 1), default_text='Andréia'),
             sg.Push(), sg.Checkbox('Aplica multa?', default=False, k='-APLMULTA-', enable_events=True)],
            [sg.Button('Calcular', k='-CALC-'), sg.Button('Confirma', k='-CONF-', bind_return_key=True),
             sg.Button('Gera para impressão', k='-IMPRIME-', disabled=True), sg.Button('Voltar', k='-VOLTAR-')],
            [sg.Text(key='-EXPAND-', font='ANY 1', pad=(0, 0))],
            [sg.StatusBar('Pronto para receber dados', k='-STATUS-', s=10, expand_y=True)]
        ]
        # JANELA RECEBE MENSALIDADE
        self.window = sg.Window('Recebimento de mensalidade', self.layout,
                                default_element_size=(12, 1), finalize=True, modal=True,
                                disable_minimize=True)  # modal=True,

    def run(self):
        while True:
            self.window['-NOMEALUNO-'].update(str(buscar_aluno_index(self.indicealuno)[1]))
            self.nome_aluno = str(buscar_aluno_index(self.indicealuno)[1])
            self.window['-VALMENS-'].update(str(buscar_aluno_index(self.indicealuno)[8]))
            self.window['-DATAVEN-'].update(str(buscar_aluno_index(self.indicealuno)[7]))
            # diasatraso = diferenca_datas(geravencto(self.values['-DATAVEN-'].rstrip()),
            #                              self.values['-DATAPAGTO-'].rstrip())
            diasatraso = diferenca_datas(geravencto(str(buscar_aluno_index(self.indicealuno)[7])),
                                         datetime.strftime(datetime.now(), '%d/%m/%Y'))
            self.window['-ATRASO-'].update(diasatraso)
            # self.window['-VALREC-'].update(str(buscar_aluno_index(self.indicealuno)[8]))
            vlrfnstr = str(buscar_aluno_index(self.indicealuno)[8])
            if diasatraso > 5:
                valorstr = str(buscar_aluno_index(self.indicealuno)[8])
                # print(resultado[idx])
                valorstr = valorstr.replace(',', '.')
                vlrmulta = float(valorstr) * 0.02
                vlrmultastr = str(vlrmulta)
                vlrmultastr = vlrmultastr.replace('.', ',')
                vlrmultastr = vlrmultastr + '0'
                valorfin = float(valorstr) + vlrmulta
                vlrfnstr = str(valorfin)
                vlrfnstr = vlrfnstr.replace('.', ',')
                vlrfnstr = vlrfnstr + '0'
                self.window['-VALMULTA-'].update(vlrmultastr)
            self.event, self.values = self.window.read()
            if self.event in (sg.WIN_CLOSED, '-VOLTAR-'):
                break

            if self.event == '-APLMULTA-':
                if self.values['-APLMULTA-']:
                    self.window['-VALREC-'].update(vlrfnstr)
                else:
                    self.window['-VALREC-'].update(str(buscar_aluno_index(self.indicealuno)[8]))

            if self.event == '-CALC-':
                if self.values['-DATAPAGTO-'].rstrip() == '':
                    sg.Popup('Não foi preenchida a data de pagamento.')
                else:
                    diasatraso = diferenca_datas(geravencto(self.values['-DATAVEN-'].rstrip()),
                                                 self.values['-DATAPAGTO-'].rstrip())
                    self.window['-ATRASO-'].update(diasatraso)
                    if diasatraso > 5:
                        valorstr = str(buscar_aluno_index(self.indicealuno)[8])
                        # print(resultado[idx])
                        valorstr = valorstr.replace(',', '.')
                        vlrmulta = float(valorstr) * 0.02
                        vlrmultastr = str(vlrmulta)
                        vlrmultastr = vlrmultastr.replace('.', ',')
                        vlrmultastr = vlrmultastr + '0'
                        valorfin = float(valorstr) + vlrmulta
                        vlrfnstr = str(valorfin)
                        vlrfnstr = vlrfnstr.replace('.', ',')
                        vlrfnstr = vlrfnstr + '0'
                        self.window['-VALMULTA-'].update(vlrmultastr)
                    if self.values['-APLMULTA-']:
                        self.window['-VALREC-'].update(vlrfnstr)
                    else:
                        self.window['-VALREC-'].update(str(buscar_aluno_index(self.indicealuno)[8]))

                    # self.window['-IMPRIME-'].update(disabled=False)

            if self.event == '-CONF-':
                if self.values['-DATAPAGTO-'].rstrip() == '':
                    sg.Popup('Não foi preenchida a data de pagamento.')
                else:
                    diasatraso = diferenca_datas(geravencto(self.values['-DATAVEN-'].rstrip()),
                                                 self.values['-DATAPAGTO-'].rstrip())
                    self.window['-ATRASO-'].update(diasatraso)
                    # print(self.indicealuno,self.values['-DATAPAGTO-'].rstrip(),diasatraso,self.values['-VALREC-'].rstrip(),self.values['-USUARIO-'].rstrip())
                    insere_dados_financeiros(self.indicealuno, self.values['-DATAPAGTO-'].rstrip(), diasatraso,
                                             self.values['-VALREC-'].rstrip(), self.values['-USUARIO-'].rstrip())
                    self.window['-IMPRIME-'].update(disabled=False)
                    self.window['-STATUS-'].update('Inserido com sucesso.')
                    # sg.Popup('Dados inseridos com sucesso.')

            if self.event == '-IMPRIME-':
                if self.values['-DATAPAGTO-'].rstrip() == '':
                    sg.Popup('Não foi preenchida a data de pagamento.')
                else:
                    diasatraso = diferenca_datas(geravencto(self.values['-DATAVEN-'].rstrip()),
                                                 self.values['-DATAPAGTO-'].rstrip())
                    self.window['-ATRASO-'].update(diasatraso)
                    gera_recibo_pdf(self.nome_aluno, self.values['-VALREC-'].rstrip(),
                                    self.values['-DATAPAGTO-'].rstrip(), self.values['-DATAVEN-'].rstrip(),
                                    self.values['-ATRASO-'].rstrip(), self.values['-USUARIO-'].rstrip())
                    self.window.perform_long_operation(lambda: os.system('\"' + pdfviewer + '\" ' + arq_recibo),
                                                       '-FUNCTION COMPLETED-')
                    # os.system(arq_recibo)
                    break
        self.window.close()


# FINAL RECEBE MENSALIDADE

#########################################
# RECEBE MENSALIDADE V2
#########################################
class Receber:
    indicealuno = 2
    tam_texto = (10, 1)
    tam_input = (10, 1)
    diasatraso = 0
    tblheader = ['Indice', 'Data', 'Descrição', 'Valor']
    largcol = [0, 12, 25, 12]
    nome_aluno = ''
    # vendastbl = [[], [], [], []]
    vendastbl = []
    valortotal = 0.0
    vlrmultastr = ''
    multar = False
    vlrmulta = 0.0
    valorextras = None
    vlrmensal = 0.0
    diasatrs = ''
    mesano = ''
    datavencto = ''
    ematraso = False

    def __init__(self):
        self.values = None
        self.event = None

        self.layout = [
            [sg.Text('nome', font='_ 25', key='-NOMEALUNO-')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.pin(sg.Text('Em atraso (clique para efetuar o pagamento): ',
                            k='-LBLATRASO-', visible=False, font='default 10 bold')),
             sg.Text('', k='-ATRASO0-', enable_events=True, font='default 10 underline', text_color='blue'),
             sg.Text('', k='-ATRASO1-', enable_events=True, font='default 10 underline', text_color='blue')],
            [sg.HorizontalSeparator(k='-SEPATRASO-')],
            [sg.Text('Vencimento:', size=self.tam_texto), sg.Input(k='-DATAVEN-', size=self.tam_input, disabled=True),
             sg.Push(), sg.Text('Valor:', size=self.tam_texto),
             sg.Input(k='-VALMENS-', size=self.tam_input, disabled=True)],
            [sg.Text('Pagamento:', size=self.tam_texto, ),
             sg.Input(k='-DATAPAGTO-', size=self.tam_input, default_text=datetime.strftime(datetime.now(), '%d/%m/%Y')),
             sg.CalendarButton('Data', locale='pt_BR', format='%d/%m/%Y', month_names=meses, day_abbreviations=dias),
             sg.Push(), sg.Text('Atraso:', size=self.tam_texto), sg.Input(k='-ATRASO-', size=self.tam_input)],
            [sg.Text('Multa:', self.tam_texto), sg.Input(k='-VALMULTA-', size=self.tam_input),
             sg.Checkbox('Aplica multa?', default=False, k='-APLMULTA-', enable_events=True),
             sg.Push(), sg.Text('Usuário:', size=self.tam_texto),
             sg.Input(k='-USUARIO-', size=(18, 1), default_text='Andréia')],
            [sg.Push(), sg.T('Adicionais'), sg.Push()],
            [sg.Table(values=[],
                      visible_column_map=[False, True, True, True],
                      headings=self.tblheader, max_col_width=25,
                      auto_size_columns=False,
                      col_widths=self.largcol,
                      justification='left',
                      num_rows=5,
                      # alternating_row_color='lightblue4',
                      key='-TABELA-',
                      # selected_row_colors='black on lightblue1',
                      enable_events=True,
                      expand_x=True,
                      expand_y=True,
                      # enable_click_events=True,
                      # right_click_menu=self.right_click_menu, ESTE PARAMETRO CONTROLA O MENU DO BOTAO DIREITO
                      # select_mode=TABLE_SELECT_MODE_BROWSE,
                      bind_return_key=True  # ESTE PARAMETRO PERMITE A LEITURA DO CLIQUE DUPLO
                      )],
            [sg.Push(), sg.Text('Valor total:', self.tam_texto), sg.Input(k='-VALREC-', size=self.tam_input)],
            [sg.Text('Forma de pagamento:'),
             sg.Radio('Dinheiro', group_id='-RADIO1-', k='-RDIN-', default=True),
             sg.Radio('Cartão', group_id='-RADIO1-', k='-RCAR-', default=False),
             sg.Radio('Outros', group_id='-RADIO1-', k='-ROUT-', default=False)],
            [sg.Button('Calcular', k='-CALC-'), sg.Button('Confirma', k='-CONF-', bind_return_key=True),
             sg.Button('Gera para impressão', k='-IMPRIME-', disabled=True), sg.Button('Voltar', k='-VOLTAR-')],
            [sg.Text(key='-EXPAND-', font='ANY 1', pad=(0, 0))],
            [sg.StatusBar('Pronto para receber dados', k='-STATUS-', s=10, expand_y=True)]
        ]

        self.window = sg.Window('Recebimento de mensalidade', self.layout,
                                default_element_size=(12, 1), finalize=True, modal=True,
                                disable_minimize=True)

        self.window['-ATRASO0-'].set_cursor(cursor='hand2')
        self.window['-ATRASO1-'].set_cursor(cursor='hand2')

    def run(self):
        while True:
            self.vendastbl = []
            self.datavencto = ''
            if not self.ematraso:
                atraso = mensalidades_atraso(self.indicealuno)
                if atraso:
                    self.window['-LBLATRASO-'].update(visible=True)
                    for idx, x in enumerate(atraso):
                        item = '-ATRASO' + str(idx) + '-'
                        self.window[item].update(x)
                self.window['-NOMEALUNO-'].update(str(buscar_aluno_index(self.indicealuno)[1]))
                self.nome_aluno = str(buscar_aluno_index(self.indicealuno)[1])
                valormsld = buscar_aluno_index(self.indicealuno)[8]
                valormsld = valormsld.replace(',', '.')
                self.vlrmensal = float(valormsld)
                self.window['-VALMENS-'].update(locale.currency(self.vlrmensal))
                self.datavencto = \
                    str(buscar_aluno_index(self.indicealuno)[7]) + '/' + datetime.strftime(datetime.now(), '%m/%Y')
                self.window['-DATAVEN-'].update(self.datavencto)
                # diasatraso = diferenca_datas(geravencto(self.values['-DATAVEN-'].rstrip()),
                #                              self.values['-DATAPAGTO-'].rstrip())
                self.diasatraso = diferenca_datas(geravencto(str(buscar_aluno_index(self.indicealuno)[7])),
                                                  datetime.strftime(datetime.now(), '%d/%m/%Y'))
                self.window['-ATRASO-'].update(self.diasatraso)
                # self.window['-VALREC-'].update(str(buscar_aluno_index(self.indicealuno)[8]))
                self.mesano = datetime.strftime(datetime.now(), '%m/%Y')
                vlrfnstr = str(buscar_aluno_index(self.indicealuno)[8])
                if self.diasatraso > 5:
                    valorstr = str(buscar_aluno_index(self.indicealuno)[8])
                    # print(resultado[idx])
                    valorstr = valorstr.replace(',', '.')
                    self.vlrmulta = float(valorstr) * 0.02
                    self.vlrmultastr = str(self.vlrmulta)
                    self.vlrmultastr = self.vlrmultastr.replace('.', ',')
                    self.vlrmultastr = self.vlrmultastr + '0'
                    # valorfin = float(valorstr) + vlrmulta
                    # vlrfnstr = str(valorfin)
                    # vlrfnstr = vlrfnstr.replace('.', ',')
                    # vlrfnstr = vlrfnstr + '0'
                    # self.window['-VALMULTA-'].update(self.vlrmultastr)
                    self.window['-VALMULTA-'].update(locale.currency(self.vlrmulta))

                    if self.window['-VALMULTA-'] != '':
                        self.window['-APLMULTA-'].update(text_color='Red')
                tmpvendas = venda_busca(self.indicealuno)
                if not self.window['-TABELA-'].Values:
                    # vendastbl = []
                    for idx, x in enumerate(tmpvendas):
                        if x[4] == 'SIM':
                            self.vendastbl.append([x[0], x[1], x[2], x[3]])
                    # if self.window['-VALMULTA-'] != '':
                    # if diasatraso > 5:
                    #    tmpappend = [99, datetime.strftime(datetime.now(), '%d/%m/%Y'), 'Multa', vlrmultastr]
                    #    vendastbl.append(tmpappend)

                    # self.vendastbl = self.window['-TABELA-'].Values
                    self.valortotal = 0.0
                    self.valorextras = 0.0
                    mens = 'Mensalidade de ' + self.mesano
                    for idx, x in enumerate(self.vendastbl):
                        self.valorextras = self.valorextras + locale.atof(x[3])
                        # EDITANDO mensalidade DE TAL tAL
                    tmpappend = [99, datetime.strftime(datetime.now(), '%d/%m/%Y'), mens,
                                 str(buscar_aluno_index(self.indicealuno)[8])]
                    print('Valores extras: ', self.valorextras)
                    self.vendastbl.append(tmpappend)
                    self.window['-TABELA-'].update(values=self.vendastbl)
                    self.valortotal = self.valorextras + locale.atof(str(buscar_aluno_index(self.indicealuno)[8]))
                    self.window['-VALREC-'].update(locale.currency(self.valortotal))
                    print('valor total: ', self.valortotal)
                # self.window.write_event_value('-TABELA-', 'value')

            self.event, self.values = self.window.read()
            if self.event in (sg.WIN_CLOSED, '-VOLTAR-'):
                break

            if self.event == '-ATRASO0-':
                self.ematraso = True
                # EDITANDO
                mesano2 = str(self.window['-ATRASO0-'].get())
                self.mesano = str(self.window['-ATRASO0-'].get())
                atrasado = mensalidades_ler_atrasado(self.indicealuno, mesano2)
                print('Atrasado: ', atrasado)
                self.datavencto = str(atrasado[2]) + '/' + str(mesano2)
                self.window['-DATAVEN-'].update(self.datavencto)
                at_multa = self.vlrmulta
                self.window['-VALMULTA-'].update(locale.currency(self.vlrmulta))
                self.window['-APLMULTA-'].update(text_color='Red')
                self.window['-APLMULTA-'].update(value=True)
                self.window.write_event_value('-APLMULTA-', 'value')
                # tmpappend = [99, datetime.strftime(datetime.now(), '%d/%m/%Y'), 'Multa', self.vlrmultastr]
                vendastmp = []
                vendastmp = self.window['-TABELA-'].Values
                # vendastmp.append(tmpappend)
                # self.window['-TABELA-'].update(values=vendastmp)
                self.valortotal = 0.0
                for idx, x in enumerate(vendastmp):
                    self.valortotal = self.valortotal + locale.atof(x[3])
                self.window['-VALREC-'].update(locale.currency(self.valortotal))
                self.vlrmensal = float(atrasado[3])
                self.window['-VALMENS-'].update(locale.currency(self.vlrmensal))
                self.diasatraso = diferenca_datas(self.datavencto,
                                                  datetime.strftime(datetime.now(), '%d/%m/%Y'))
                self.window['-ATRASO-'].update(self.diasatraso)
                mens = 'Mensalidade de ' + self.mesano
                # for idx, x in enumerate(self.vendastbl):
                #    self.valorextras = self.valorextras + locale.atof(x[3])
                # EDITANDO mensalidade DE TAL tAL
                tmpappend = []
                tmpappend = [99, datetime.strftime(datetime.now(), '%d/%m/%Y'), mens,
                             str(buscar_aluno_index(self.indicealuno)[8])]
                print('Valores extras: ', self.valorextras)
                self.vendastbl = []
                self.vendastbl.append(tmpappend)
                self.window['-TABELA-'].update(values=self.vendastbl)

            if self.event == '-APLMULTA-':
                print(self.vlrmultastr)
                if self.vlrmultastr != '':
                    if self.values['-APLMULTA-']:
                        print('entrou no aplica multa - ', self.values['-APLMULTA-'])
                        tmpappend = [99, datetime.strftime(datetime.now(), '%d/%m/%Y'), 'Multa', self.vlrmultastr]
                        vendastmp = []
                        vendastmp = self.window['-TABELA-'].Values
                        vendastmp.append(tmpappend)
                        self.window['-TABELA-'].update(values=vendastmp)
                        self.valortotal = 0.0
                        for idx, x in enumerate(vendastmp):
                            self.valortotal = self.valortotal + locale.atof(x[3])
                        self.window['-VALREC-'].update(locale.currency(self.valortotal))
                    else:
                        print('entrou no else - ', self.values['-APLMULTA-'])
                        tmpappend = [99, datetime.strftime(datetime.now(), '%d/%m/%Y'), 'Multa', self.vlrmultastr]
                        vendastmp = []
                        vendastmp = self.window['-TABELA-'].Values
                        vendastmp.remove(tmpappend)
                        # self.vendastbl = []
                        self.window['-TABELA-'].update(values=vendastmp)
                        self.valortotal = 0.0
                        for idx, x in enumerate(vendastmp):
                            self.valortotal = self.valortotal + locale.atof(x[3])
                        self.window['-VALREC-'].update(locale.currency(self.valortotal))

            if self.event == '-CONF-':
                valormsld = buscar_aluno_index(self.indicealuno)[8]
                valormsld = valormsld.replace(',', '.')
                tmp = mensalidades_insere(self.indicealuno, self.mesano,
                                          buscar_aluno_index(self.indicealuno)[7], self.vlrmensal,
                                          datetime.strftime(datetime.now(), '%d/%m/%Y'), self.vlrmulta,
                                          self.valorextras, self.valortotal, 1, self.diasatraso)
                if tmp == 2:
                    sg.popup('Esta mensalidade já foi paga.')
                    # insere_dados_financeiros(self.indicealuno, self.values['-DATAPAGTO-'].rstrip(), self.diasatraso,
                    #                         self.valortotal, self.values['-USUARIO-'].rstrip())
                    tmpdata = self.values['-DATAPAGTO-'].rstrip()
                    tmpdata = tmpdata[3:]
                    print(tmpdata)
                    print(self.indicealuno)
                    venda_recebe(self.indicealuno, tmpdata)

        self.window.close()


#########################################
# FINAL RECEBE MENSALIDADE V2
#########################################


#########################################
# INICIO TELA PRINCIPAL
#########################################
class Principal:
    # ################################### CAD ALUNO
    formatodata = "%d/%m/%Y"
    res = True
    # ################################### CAD ALUNO

    # ####################################TEMA
    # sg.theme(sg.user_settings_get_entry('-tema-'))
    # sg.change_look_and_feel('DarkBlue3')
    lista_temas = sg.list_of_look_and_feel_values()
    lista_temas.sort()
    # ####################################TEMA

    # ################################### MAIS INFO
    tblheadinfo = ['Indice', 'Data pagto', 'Atraso', 'Valor', 'Valor pago']
    largcolinfo = [10, 10, 10, 10]
    # tblvalores = ['01/01/2011','01/01/2011','Andréia']
    #    global indice
    indiceinfo = 0
    rowinfo = []
    dadosinfo = []
    # ################################### MAIS INFO

    # ################################RECEBE VENDAS
    tblhdven = ['Indice', 'Data', 'Descrição', 'Valor']
    lcven = [0, 12, 25, 12]
    tmpdata = []

    largcol = [0, 25, 25, 12, 12, 20, 9, 6, 8, 9, 4]
    coljust = ['r', 'l', 'l', 'r', 'r', 'l', 'r', 'r', 'r', 'r']
    tblhead = ['Indice', 'Nome', 'Endereço', 'Telefone', 'CPF', 'E-mail', 'Mat.', 'Venc.', 'Mensalidade',
               'Último pagto', 'Ativo']
    # "!" DESABILITA ITEM DO MENU, "&" TRANSFORMA EM ATALHO DO TECLADO, "'---'" CRIA UMA LINHA ENTRE OPCOES DO MENU
    menu_def = [
        ['&Arquivo', ['Adicionar aluno', 'Receber mensalidade', 'Informações do aluno', 'Financeiro', '---', '&Sair']],
        # 'Save::savekey',
        ['&Editar', ['!Configurações', 'Mudar tema'], ],
        ['&Relatórios', ['Recebimento', 'Devedores']],
        ['&Ferramentas', ['Backup parcial', 'Backup completo', 'Administração', ['Limpar banco de dados']]],
        ['A&juda', ['Tela principal', 'Sobre...']], ]
    # ALTMENU
    right_click_menu = ['Unused', ['Abrir', '!&Click', '&Menu', 'E&xit', 'Properties']]
    row = []
    dados = []

    def __init__(self):
        self.rowinfop = None
        self.dadosinfop = None
        self.valuesven = None
        self.eventven = None
        self.windowven = None
        self.layoutven = None
        self.indiceven = None
        self.indiceve = None
        self.dadosve = None
        self.rowve = None
        self.valuesv = None
        self.windowv = None
        self.layoutv = None
        self.indicev = None
        self.framelayout = None
        self.eventv = None
        self.cad_real = None
        self.values2 = None
        self.event2 = None
        self.window2 = None
        self.layout2 = None
        self.valuesinfo = None
        self.eventinfo = None
        self.windowinfo = None
        self.layoutinfo = None
        self.values3 = None
        self.event3 = None
        self.window3 = None
        self.layout3 = None
        self.values = None
        self.event = None
        sg.theme(sg.user_settings_get_entry('-tema-'))
        # print(ler_todos_dados()[1])
        self.layout = [
            [sg.Menu(self.menu_def, )],
            [sg.Text(''), sg.Image(source=imagem_peq), sg.Text('Sistema de gerenciamento de alunos', font='_ 25'), ],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.Table(values=ler_todos_dados_ativos(),
                      visible_column_map=[False, True, True, True, True, True, True, True, False, True, True],
                      headings=self.tblhead, max_col_width=25,
                      auto_size_columns=False,
                      col_widths=self.largcol,
                      # display_row_numbers=True,
                      justification='left',
                      num_rows=18,
                      # alternating_row_color='lightblue4',
                      key='-TABELA-',
                      # selected_row_colors='black on lightblue1',
                      enable_events=True,
                      expand_x=True,
                      expand_y=True,
                      # enable_click_events=True,
                      # right_click_menu=self.right_click_menu, ESTE PARAMETRO CONTROLA O MENU DO BOTAO DIREITO
                      # select_mode=TABLE_SELECT_MODE_BROWSE,
                      bind_return_key=True  # ESTE PARAMETRO PERMITE A LEITURA DO CLIQUE DUPLO
                      )],
            # [sg.Text('Local do click:'),sg.Input(k='-CLICKED-')],
            [sg.Text('Buscar aluno por nome'), sg.Input(key='-BUSCAR-'),
             sg.Button('Buscar', key='-BBUSCA-', bind_return_key=True),
             sg.Button('Limpar', key='-LIMPA-'), sg.Button('Atualizar', k='-ATUALIZAR-'),
             sg.Checkbox('Apenas alunos ativos', k='-ATIVOS-', default=True, enable_events=True)],
            # [sg.Text('O que deseja fazer?')],
            [sg.Button('Adicionar alunos', key='-AD-'), sg.Button('Receber mensalidade', k='-RECEBE-'),
             sg.Button('Vender', k='-VENDA-'), sg.Button('Receber', k='-RECVENDA-'),
             sg.Button('Mais informações', k='-MAISINFO-')],
            [sg.Push(), sg.Button('Sair', k='-SAIR-')],
            [sg.Text(key='-EXPAND-', font='ANY 1', pad=(0, 0))],
            [sg.StatusBar('Obrigado por usar um software de código aberto!', k='-STATUS-', s=10, expand_y=True)]
        ]

        self.window = sg.Window('Gerenciamento de alunos', self.layout,
                                icon=icone, resizable=True, finalize=True,
                                enable_close_attempted_event=True,
                                location=sg.user_settings_get_entry('-location-', (None, None)))
        # ,right_click_menu=self.right_click_menu use_default_focus=True,
        self.window['-EXPAND-'].expand(True, True, True)
        # self.window.bind('<FocusOut>', '+FOCUS OUT+') #, self.window['-CLICKED-'].ButtonReboundCallback)
        # self.window['-CLICKED-'].bind('<FocusIn>', '+INPUT FOCUS+')
        self.window.bind('<F1>', 'Tela principal')

    def run(self):
        while True:
            now = datetime.now()
            now = now.strftime('%d/%m/%Y')
            if sg.user_settings_get_entry('-lastbackup-') is None:
                self.window['-STATUS-'].update('Nenhum backup efetuado.')
            else:
                ultimobkp = sg.user_settings_get_entry('-lastbackup-')
                tempobkp = diferenca_datas(ultimobkp, now)
                self.window['-STATUS-'].update('Último backup realizado há ' + str(tempobkp) + ' dias atrás.')

            tmptabela = self.window['-TABELA-'].Values
            # print(self.window['-TABELA-'].Values)
            indice = 0
            for idx, x in enumerate(tmptabela):
                atrasado = mensalidades_atraso(x[0])
                if atrasado:
                    self.window['-TABELA-'].Update(row_colors=[[indice, 'red']])
                indice = indice + 1

            self.event, self.values = self.window.read()
            # print(self.event,self.values)
            # if ultimobkp
            # print(self.event)
            # self.window['-TABELA-'].bind('<Enter>', '+MOUSE OVER+')
            # if (self.event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or self.event == 'Sair') and sg.popup_yes_no('Tem
            # certeza que deseja sair do programa?') == 'Yes':

            if self.event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT, 'Sair', '-SAIR-'):
                opcao, _ = sg.Window('Continuar?', [[sg.T('Tem certeza que deseja sair do programa?')],
                                                    [sg.Yes(s=10, button_text='Sim'), sg.No(s=10, button_text='Não')]],
                                     disable_close=True, element_justification='center').read(close=True)
                if opcao == 'Sim':
                    sg.user_settings_set_entry('-location-', self.window.current_location())
                    break

            if self.event == 'Financeiro':
                objcontabil = contabil.Contabil()
                objcontabil.run()

            #                self.window.perform_long_operation(lambda: subprocess.call("contabil.exe", shell=True),
            #                                                   '-FUNCTION COMPLETED-')

            if self.event == 'Limpar banco de dados':
                opcao, _ = sg.Window('Continuar?', [[sg.T('Tem certeza?')],
                                                    [sg.Yes(s=10, button_text='Sim'), sg.No(s=10, button_text='Não')]],
                                     disable_close=True, element_justification='center').read(close=True)
                if opcao == 'Sim':
                    novobanco()
            # #################################### JANELA DE TEMAS
            if self.event == 'Mudar tema':
                self.layout3 = [[sg.Text('Navegador de temas')],
                                [sg.Text('Clique em um tema para ver uma janela de preview.')],
                                [sg.T('O tema original é DarkBlue3.')],
                                [sg.T('O novo tema será aplicado assim que você abrir o programa novamente.')],
                                [sg.Listbox(values=self.lista_temas,
                                            size=(20, 12), key='-LISTA-', enable_events=True)],
                                [sg.B('Salvar tema', k='-SALVA-'), sg.Button('Sair', k='-SAIR-')]]
                self.window3 = sg.Window('Navegador de temas', self.layout3)

                while True:
                    self.event3, self.values3 = self.window3.read()
                    # print(self.event3)
                    # print(self.values3)
                    if self.event3 in (None, '-SAIR-'):
                        break
                    sg.change_look_and_feel(self.values3['-LISTA-'][0])
                    sg.popup_get_text('Este é o tema {}'.format(self.values3['-LISTA-'][0]))

                    if self.event3 in '-SALVA-':
                        sg.user_settings_set_entry('-tema-', self.values3['-LISTA-'][0])
                        # sg.popup(self.values3['-LISTA-'][0])
                        # sg.popup(sg.user_settings_get_entry('-tema-'))
                        break
                self.window3.close()
            # #################################### JANELA DE TEMAS

            if self.event == '-RECVENDA-':
                if len(self.row) != 0:
                    self.indiceven = self.dados[self.row[0]][0]
                    tempvenda = venda_busca(self.indiceven)
                    naopago = False
                    for idx, x in enumerate(tempvenda):
                        if x[4] == 'SIM':
                            naopago = True
                    if naopago:
                        tmpvendas = venda_busca(self.indiceven)
                        self.layoutven = [
                            [sg.Text('Recebimento de vendas', font='_ 25')],
                            [sg.HorizontalSeparator(k='-SEP-')],
                            [sg.Text('Vendas registradas')],
                            [sg.Table(values=[],
                                      visible_column_map=[False, True, True, True],
                                      headings=self.tblhdven, max_col_width=25,
                                      auto_size_columns=False,
                                      col_widths=self.lcven,
                                      justification='left',
                                      num_rows=5,
                                      # alternating_row_color='lightblue4',
                                      key='-TABELAVEN-',
                                      # selected_row_colors='black on lightblue1',
                                      enable_events=True,
                                      expand_x=True,
                                      expand_y=True,
                                      # enable_click_events=True,
                                      # right_click_menu=self.right_click_menu,
                                      # ESTE PARAMETRO CONTROLA O MENU DO BOTAO DIREITO
                                      # select_mode=TABLE_SELECT_MODE_BROWSE,
                                      bind_return_key=True  # ESTE PARAMETRO PERMITE A LEITURA DO CLIQUE DUPLO
                                      )],
                            [sg.Push(), sg.T('Valor total: '), sg.I(size=(10, 1), k='-TOTALVEN-')],
                            [sg.Push(), sg.Button('Recebe', k='-RECEBEVEN-'), sg.Button('Sair', k='-SAIR-')]
                        ]
                        self.windowven = sg.Window('Receber vendas', layout=self.layoutven, finalize=True)

                        while True:
                            if not self.windowven['-TABELAVEN-'].Values:
                                print('entrou no ifnot da tabela')
                                vendastbl = []

                                vlrtotal = 0.0
                                for idx, x in enumerate(tmpvendas):
                                    if x[4] == 'SIM':
                                        vendastbl.append([x[0], x[1], x[2], x[3]])
                                        vlrtotal = vlrtotal + float(x[3])
                                        self.tmpdata.append(x[1])
                                self.windowven['-TABELAVEN-'].update(values=vendastbl)
                                self.windowven['-TOTALVEN-'].update(locale.currency(vlrtotal))
                            self.eventven, self.valuesven = self.windowven.read()
                            print(self.eventven, self.valuesven)

                            if self.eventven == '-RECEBEVEN-':
                                for idx, x in enumerate(self.tmpdata):
                                    venda_recebe(self.indiceven, x)
                                sg.Popup('Recebido com sucesso!')
                                # TODO imprime recibo?
                                break

                            if self.eventven in (None, '-SAIR-'):
                                break

                        self.windowven.close()
                    else:
                        sg.popup('Não há registro de vendas para este aluno.')
                else:
                    sg.popup('Selecione um registro na tabela.')
            ##################################################
            #             JANELA VENDAS
            # todo: receber vendas anteriores
            ##################################################
            if self.event in ('-VENDA-', 'Receber venda'):
                if len(self.row) != 0:
                    self.indicev = self.dados[self.row[0]][0]
                    index = 0
                    tblheader = ['Indice', 'Data', 'Descrição', 'Valor']
                    largcol = [0, 12, 25, 12]
                    tmptable = []
                    valorestabela = []
                    subtotal = 0.0

                    self.framelayout = [
                        [sg.T('Aluno:', s=(6, 1)),
                         sg.I(default_text=str(buscar_aluno_index(self.indicev)[1]), k='-NOMEV-', s=(28, 1)),
                         sg.Push(), sg.T('Data:', s=(6, 1)),
                         sg.I(default_text=datetime.strftime(datetime.now(), '%d/%m/%Y'), k='-DATAV-', s=(10, 1)),
                         sg.CalendarButton('Data', locale='pt_BR', format='%d/%m/%Y',
                                           month_names=meses, day_abbreviations=dias)],
                        [sg.T('Produto:', s=(6, 1)), sg.Combo([], k='-VDESC-', s=(28, 1)), sg.Push(),
                         sg.T('Valor:', s=(6, 1)), sg.I(k='-VALORV-', s=(10, 1))],
                        [sg.Push(), sg.Button('Adiciona', k='-ADD-'), sg.Push()],
                        [sg.HorizontalSeparator(k='-SEP1-')],
                        [sg.Table(values=[],
                                  visible_column_map=[False, True, True, True],
                                  headings=tblheader, max_col_width=25,
                                  auto_size_columns=False,
                                  col_widths=largcol,
                                  justification='left',
                                  num_rows=5,
                                  # alternating_row_color='lightblue4',
                                  key='-TABELAV-',
                                  # selected_row_colors='black on lightblue1',
                                  enable_events=True,
                                  expand_x=True,
                                  expand_y=True,
                                  # enable_click_events=True, right_click_menu=self.right_click_menu, ESTE PARAMETRO
                                  # CONTROLA O MENU DO BOTAO DIREITO select_mode=TABLE_SELECT_MODE_BROWSE,
                                  bind_return_key=True  # ESTE PARAMETRO PERMITE A LEITURA DO CLIQUE DUPLO
                                  )],
                        [sg.B('Apaga', k='-VAPA-'), sg.Push(), sg.T('Valor total:'), sg.I(k='-VTOTAL-', s=(10, 1))],
                        [sg.Text('Forma de pagamento:'),
                         sg.Radio('Dinheiro', group_id='-RADIO1-', k='-RDIN-', default=True),
                         sg.Radio('Cartão', group_id='-RADIO1-', k='-RCAR-', default=False),
                         sg.Radio('Outros', group_id='-RADIO1-', k='-ROUT-', default=False)],
                        [sg.Frame('Atenção:', [[sg.Checkbox('Cobrar junto à mensalidade?',
                                                            k='-COBRA-', default=True)]],
                                  background_color='Red')],
                        [sg.Push(), sg.B('Gravar/Receber', k='-GRAVA-'), sg.B('Cancelar', k='-VOLTAR-')]
                    ]
                    self.layoutv = [
                        [sg.Text('Venda de produtos', font='_ 25', key='-VTITLE-')],
                        [sg.HorizontalSeparator(k='-SEP-')],
                        [sg.Frame(title='', layout=self.framelayout)]
                    ]
                    self.windowv = sg.Window('Venda de produtos', self.layoutv, use_default_focus=True,
                                             finalize=True,
                                             modal=True)
                    while True:
                        self.eventv, self.valuesv = self.windowv.read()
                        if self.eventv in (sg.WIN_CLOSED, '-VOLTAR-'):
                            break
                        print(self.eventv, self.valuesv)

                        if self.eventv == '-TABELAV-':
                            self.rowv = self.valuesv[self.eventv]
                            self.dadosv = self.windowv['-TABELAV-'].Values
                            print('ROWV', self.rowv)
                            print('DADOSV', self.dadosv)

                        if self.eventv == '-ADD-':
                            # print(self.valuesv['-DATAV-'].rstrip())
                            # print(self.valuesv['-VDESC-'].rstrip())
                            # print(self.valuesv['-VALORV-'].rstrip())
                            tmpvar = ['', self.valuesv['-DATAV-'].rstrip(),
                                      self.valuesv['-VDESC-'].rstrip(), self.valuesv['-VALORV-'].rstrip()]
                            tmptable.append(tmpvar)
                            self.windowv['-TABELAV-'].update(values=tmptable)
                            valorestabela = self.windowv['-TABELAV-'].Values
                            subtotal = 0.0
                            for idx, x in enumerate(valorestabela):
                                subtotal = subtotal + locale.atof(x[3])
                            self.windowv['-VTOTAL-'].update(value=locale.currency(subtotal))

                        if self.eventv == '-VAPA-':
                            if len(self.rowv) != 0:
                                self.indicevv = self.dadosv[self.rowv[0]][0]
                                self.remover = self.dadosv[self.rowv[0]]
                                # self.indicev = self.rowv
                                valorestabela = self.windowv['-TABELAV-'].Values
                                # self.indicev = self.dadosv[self.rowv[0]][0]
                                # print('GET tabela', self.windowv['-TABELAV-'].get())
                                print('INDICEVV ', self.indicevv)
                                print('valorestabela ', valorestabela)
                                valorestabela.remove(self.remover)
                                # self.windowv['-TABELAV-'].update()
                                self.windowv['-TABELAV-'].update(values=valorestabela)
                                subtotal = 0.0
                                for idx, x in enumerate(valorestabela):
                                    subtotal = subtotal + locale.atof(x[3])
                                self.windowv['-VTOTAL-'].update(value=locale.currency(subtotal))
                            else:
                                sg.popup('Selecione um registro na tabela.')

                        if self.eventv == '-GRAVA-':
                            valorestabela = self.windowv['-TABELAV-'].Values
                            tmpcobranca = ''
                            tmpforma = ''
                            tmppago = ''
                            if self.valuesv['-COBRA-']:
                                tmpcobranca = 'SIM'
                            else:
                                tmpcobranca = 'NAO'
                            if self.valuesv['-RDIN-']:
                                tmpforma = 'DINHEIRO'
                            if self.valuesv['-RCAR-']:
                                tmpforma = 'CARTAO'
                            if self.valuesv['-ROUT-']:
                                tmpforma = 'OUTROS'
                            if tmpcobranca == 'SIM':
                                tmppago = 'NAO'
                            else:
                                tmppago = 'SIM'
                            for idx, x in enumerate(valorestabela):
                                venda_adiciona(self.indicev, x[1], x[2], x[3], tmpcobranca, tmpforma, tmppago)
                            sg.popup('Venda realizada com sucesso.')
                            break
                            # self.valuesv['-DATAV-'].rstrip()

                    self.windowv.close()
                else:
                    sg.Popup('Selecione um registro na tabela.')

            ##################################################
            #             JANELA MAIS INFORMACOES
            ##################################################
            #
            if self.event in ('-MAISINFO-', 'Informações do aluno'):
                if len(self.row) != 0:
                    #    print('DADOS[ROW]:',dados[row[0]])
                    #    print('ROW INDEX:',dados[row[0]][0])
                    # ObjMaisInfo = MaisInfo()
                    self.indiceinfo = self.dados[self.row[0]][0]
                    # ObjMaisInfo.run()
                    self.layoutinfo = [
                        [sg.Text('nome', font='_ 25', key='-NOMEALUNO-')],
                        [sg.HorizontalSeparator(k='-SEP-')],
                        # [sg.Text('nome',relief='sunken', font=('italic'),key='-NOMEALUNO-')],
                        # [sg.Text('Informações detalhadas')],
                        [
                            sg.TabGroup([[sg.Tab(
                                'Detalhes',
                                [
                                    # [sg.Text('', size=(7, 1))],
                                    [sg.Text('',
                                             text_color='Red', font='_ 10 bold', k='-ATRASO-')],
                                    [sg.Text('Nome:', size=(8, 1)), sg.Input(key='-NOME-', size=(41, 1))],
                                    [sg.Text('Endereço:', size=(8, 1)),
                                     sg.Input(key='-END-', size=(41, 1))],
                                    [sg.Text('Telefone:', size=(8, 1)),
                                     sg.Input(key='-TEL1-', size=(14, 1)), sg.Text('CPF:', size=(8, 1)),
                                     sg.Input(key='-CPF-', size=(14, 1))],
                                    [sg.Text('Email:', size=(8, 1)), sg.Input(key='-EMAIL-', size=(41, 1))],
                                    [sg.Text('Matrícula:', size=(8, 1)),
                                     sg.Input(key='-MAT-', size=(10, 1)),
                                     sg.CalendarButton('Data', locale='pt_BR', format='%d/%m/%Y',
                                                       month_names=meses, day_abbreviations=dias),
                                     sg.Text('Vencimento:', size=(10, 1)),
                                     sg.Input(key='-VEN-', size=(9, 1))],
                                    [sg.Text('Valor mensalidade:', size=(16, 1)),
                                     sg.Input(k='-VALMENS-', size=(8, 1)), sg.Text('', size=(19, 1))],
                                    [sg.Text('Data do último pagamento:'),
                                     sg.I(k='-ULTPGT-', s=(9, 1), disabled=True),
                                     sg.Text('', size=(15, 1))],
                                    [sg.Radio('Ativo', "RadioAtivo", default=True, k='-RATV-'),
                                     sg.Radio('Inativo', "RadioAtivo", k='-RINT-')],
                                    [sg.Text('', size=(1, 1))],
                                    # [sg.Button('Receber mensalidade',k='-RECEBE-')],
                                    [sg.Button('Alterar dados', k='-ALTERA-'),
                                     sg.Button('Apagar registro', k='-APAGA-')]
                                ],
                                element_justification='center', key='-mykey-',
                                expand_x=True, expand_y=True
                            ),  # expand_x=True, expand_y=True,
                                sg.Tab('Planos',
                                       [
                                           [sg.Frame('', layout=[
                                               [sg.T('Inscrito:', s=(6, 1)),
                                                sg.I('Nenhum', s=(40, 1), k='-INSCRITO-', disabled=True)],
                                               [sg.T('Período:', s=(6, 1)),
                                                sg.I(k='-PERIODO-', s=(15, 1), disabled=True), sg.Push(),
                                                sg.T('Início:', s=(6, 1)),
                                                sg.I(k='-INICIO-', s=(15, 1), disabled=True)],
                                               [sg.T('Valor:', s=(6, 1)), sg.I(k='-VALOR-', s=(15, 1), disabled=True),
                                                sg.Push(), sg.T('Final:', s=(6, 1)),
                                                sg.I(k='-FINAL-', s=(15, 1), disabled=True)],
                                               [sg.T('Normal:', s=(6, 1)), sg.I(k='-VLNORM-', s=(15, 1), disabled=True),
                                                sg.Push(), sg.T('Plano:', s=(6, 1)),
                                                sg.I(k='-VLMEN-', s=(15, 1), disabled=True)],
                                               [sg.HorizontalSeparator(k='-SEP-')],
                                               [sg.T('Planos disponíveis - clique para selecionar')],
                                               [sg.Table(values=planos_ler(),
                                                         headings=['No.', 'Plano', 'Período', 'Valor'],
                                                         visible_column_map=[False, True, True, True],
                                                         # sg.Table(values=busca_dadosinfo_financeiros(self.indiceinfo),headings=self.tblheadinfo,
                                                         key='-TABELAPL-',
                                                         # max_col_width=10,
                                                         auto_size_columns=False,
                                                         col_widths=[0, 30, 10, 10],
                                                         # pad=(5,5,5,5),
                                                         num_rows=5,
                                                         # def_col_width=5,
                                                         # alternating_row_color='lightblue4',
                                                         # selected_row_colors='black on lightblue1',
                                                         enable_events=True,
                                                         expand_x=False,
                                                         expand_y=True
                                                         # select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                                                         # enable_click_events=True
                                                         )], [sg.CalendarButton('Data', locale='pt_BR',
                                                                                format='%d/%m/%Y',
                                                                                month_names=meses,
                                                                                day_abbreviations=dias),
                                                              sg.Push(),
                                                              sg.B('Inscrever', k='-INSC-'),
                                                              sg.B('Altera', k='-ALTERA-'),
                                                              sg.B('Pausa', k='-PAUSA-')]
                                           ])]
                                       ]
                                       ),
                                sg.Tab('Mensalidades',
                                       [
                                           # [sg.Text('Mensalidades')],
                                           [sg.Table(values=busca_dados_financeiros(self.indiceinfo),
                                                     headings=self.tblheadinfo,
                                                     visible_column_map=[False, True, True, True, True],
                                                     # sg.Table(values=busca_dadosinfo_financeiros(self.indiceinfo),headings=self.tblheadinfo,
                                                     key='-TABELAPG-',
                                                     # max_col_width=10,
                                                     auto_size_columns=False,
                                                     col_widths=self.largcolinfo,
                                                     # pad=(5,5,5,5),
                                                     num_rows=18,
                                                     # def_col_width=5,
                                                     # alternating_row_color='lightblue4',
                                                     # selected_row_colors='black on lightblue1',
                                                     enable_events=True,
                                                     expand_x=False,
                                                     expand_y=True,
                                                     # select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                                                     # enable_click_events=True
                                                     )],
                                           # [sg.Input(key='-in2-')]
                                           [sg.Button('Apagar', k='-APAGAR-'),
                                            sg.Button('Imprime recibo', k='-IMPRIME-', focus=True)]
                                           # sg.Button('Popular tabela',k='-POP-'),
                                       ], element_justification='center', key='-mykey2-',
                                       expand_x=True, expand_y=True
                                       )
                            ]
                            ], s=(500, 350), key='-group2-', tab_location='topleft',
                                enable_events=True)], [sg.Button('Voltar', k='-VOLTAR-')]
                    ]
                    self.windowinfo = sg.Window('Detalhes do aluno', self.layoutinfo, use_default_focus=True,
                                                finalize=True,
                                                modal=True)
                    # default_element_size=(12, 1),resizable=True,disable_minimize=True,
                    self.windowinfo.bind('<F1>', '-AJUDA-')
                    while True:
                        self.windowinfo['-NOMEALUNO-'].update(str(buscar_aluno_index(self.indiceinfo)[1]))
                        self.windowinfo['-NOME-'].update(str(buscar_aluno_index(self.indiceinfo)[1]))
                        self.windowinfo['-END-'].update(str(buscar_aluno_index(self.indiceinfo)[2]))
                        self.windowinfo['-TEL1-'].update(str(buscar_aluno_index(self.indiceinfo)[3]))
                        self.windowinfo['-CPF-'].update(str(buscar_aluno_index(self.indiceinfo)[4]))
                        self.windowinfo['-EMAIL-'].update(str(buscar_aluno_index(self.indiceinfo)[5]))
                        self.windowinfo['-MAT-'].update(str(buscar_aluno_index(self.indiceinfo)[6]))
                        self.windowinfo['-VEN-'].update(str(buscar_aluno_index(self.indiceinfo)[7]))
                        self.windowinfo['-VALMENS-'].update(str(buscar_aluno_index(self.indiceinfo)[8]))
                        self.windowinfo['-ULTPGT-'].update(str(buscar_aluno_index(self.indiceinfo)[9]))
                        planos = planos_busca(self.indiceinfo)
                        print(planos)
                        if planos[0] is not None:
                            print('entrou no if')
                            periodo = ''
                            self.windowinfo['-INSCRITO-'].update(planos[1])
                            plan = planos_ler()
                            for idx, x in enumerate(plan):
                                if x[0] == planos[0]:
                                    periodo = x[2]
                            self.windowinfo['-PERIODO-'].update(str(periodo) + ' meses')

                        if buscar_aluno_index(self.indiceinfo)[10] == 'S':
                            self.windowinfo['-RATV-'].update(value=True)
                        else:
                            self.windowinfo['-RINT-'].update(value=True)
                        # Em atraso -- falta elaborar
                        # datastr = str(buscar_aluno_index(self.indiceinfo)[7]) + '/' + \
                        #          datetime.strftime(datetime.now(), '%m/%Y')
                        # datavenc = datetime.strptime(datastr, '%d/%m/%Y')
                        # if datavenc < datetime.now():
                        #    atraso = datetime.now() - datavenc
                        #    atrasostr = atraso.days
                        #    scrstr = 'Mensalidade em atraso: ' + str(atrasostr) + ' dias.'
                        #    self.windowinfo['-ATRASO-'].update(scrstr)
                        atraso = mensalidades_atraso(self.indiceinfo)
                        if atraso:
                            scrstr = 'Mensalidades em atraso: '
                            scrstr2 = ''
                            for idx, x in enumerate(atraso):
                                scrstr2 = scrstr2 + ' ' + x
                            scrstr = scrstr + scrstr2
                            self.windowinfo['-ATRASO-'].update(scrstr)
                        #########################
                        self.eventinfo, self.valuesinfo = self.windowinfo.read()
                        if self.eventinfo == sg.WIN_CLOSED or self.eventinfo == '-VOLTAR-':
                            break

                        if self.eventinfo == '-TABELAPL-':
                            self.rowinfop = self.valuesinfo[self.eventinfo]
                            self.dadosinfop = self.windowinfo['-TABELAPL-'].Values

                        if self.eventinfo == '-INSC-':
                            self.windowinfo['-INSCRITO-'].update(self.dadosinfop[self.rowinfop[0]][1])
                            self.windowinfo['-PERIODO-'].update(self.dadosinfop[self.rowinfop[0]][2])
                            tmpmonths = int(self.dadosinfop[self.rowinfop[0]][2])
                            valorstr = buscar_aluno_index(self.indiceinfo)[8]
                            valorstr = valorstr.replace(',', '.')
                            valordesc = float(valorstr) * float(self.dadosinfop[self.rowinfop[0]][3])
                            valorfinal = float(valorstr) - valordesc
                            self.windowinfo['-VLMEN-'].update(locale.currency(valorfinal))
                            self.windowinfo['-VLNORM-'].update(str(buscar_aluno_index(self.indiceinfo)[8]))
                            valorfinal = valorfinal * tmpmonths
                            self.windowinfo['-VALOR-'].update(locale.currency(valorfinal))
                            self.windowinfo['-INICIO-'].update(datetime.strftime(datetime.now(), '%d/%m/%Y'))

                            dtdatafinal = date.today() + relativedelta(months=+tmpmonths)
                            datafinal = datetime.strftime(dtdatafinal, '%d/%m/%Y')
                            self.windowinfo['-FINAL-'].update(datafinal)

                        if self.eventinfo == '-AJUDA-':
                            obj_ajuda = Ajuda()
                            obj_ajuda.nomearquivo = 'informacoes.html'
                            obj_ajuda.run()

                        if self.eventinfo == '-APAGAR-':
                            if len(self.rowinfo) != 0:
                                opcao, _ = sg.Window('Continuar?',
                                                     [[sg.T('Tem certeza? Esta operação é definitiva.')],
                                                      [sg.Yes(s=10, button_text='Sim'),
                                                       sg.No(s=10, button_text='Não')]], disable_close=True,
                                                     modal=True).read(close=True)
                                if opcao == 'Sim':
                                    apaga_dados_financeiros(self.dadosinfo[self.rowinfo[0]][0],
                                                            self.dadosinfo[self.rowinfo[0]][1])
                                    self.windowinfo['-TABELAPG-'].update(
                                        valuesinfo=busca_dados_financeiros(self.indiceinfo))

                        if self.eventinfo == '-POP-' or self.eventinfo == '-group2-':
                            self.windowinfo['-TABELAPG-'].update(busca_dados_financeiros(self.indiceinfo))

                        ##########################################
                        # CHECAGEM DE VALORES
                        ##########################################
                        if self.eventinfo == '-ALTERA-':
                            if self.valuesinfo['-NOME-'].rstrip() == '':
                                sg.popup('Campo nome não pode ser vazio.')
                            elif self.valuesinfo['-END-'].rstrip() == '':
                                sg.popup('Campo endereço não pode ser vazio.')
                            elif self.valuesinfo['-TEL1-'].rstrip() != '' and not re.fullmatch(regexTelefone,
                                                                                               self.valuesinfo[
                                                                                                   '-TEL1-'].rstrip()):
                                sg.popup('Telefone deve ser no formato (xx)xxxxx-xxxx')
                            elif self.valuesinfo['-CPF-'].rstrip() != '' and not \
                                    re.fullmatch(regexCPF, self.valuesinfo['-CPF-'].rstrip()):
                                sg.popup('Telefone deve ser no formato (xx)xxxxx-xxxx')  # EDITANDO
                            elif self.valuesinfo['-EMAIL-'].rstrip() != '' and not \
                                    re.fullmatch(regexEmail, self.valuesinfo['-EMAIL-'].rstrip()):
                                sg.popup('Campo email deve ser no formato abc@de.fgh')
                            elif self.valuesinfo['-MAT-'].rstrip() == '':
                                sg.popup('Data de matrícula não pode ser vazio.')
                            elif self.valuesinfo['-VEN-'].rstrip() == '':
                                sg.popup('Data de vencimento não pode ser vazio.')
                            elif self.valuesinfo['-VALMENS-'].rstrip() == '':
                                sg.popup('Campo valor da mensalidade não pode ser vazio.')
                            elif self.valuesinfo['-VALMENS-'].rstrip() != '' and not \
                                    re.fullmatch(regexDinheiro, self.valuesinfo['-VALMENS-'].rstrip()):
                                sg.popup('Valor da mensalidade deve ser no formato xxx,xx')
                            elif self.valuesinfo['-VEN-'].rstrip() != '' and not \
                                    re.fullmatch(regexDia, self.valuesinfo['-VEN-'].rstrip()):
                                sg.popup('Data de vencimento deve ser entre 01 e 31.')
                            elif self.valuesinfo['-VALMENS-'].rstrip() != '' and not \
                                    re.fullmatch(regexDinheiro, self.valuesinfo['-VALMENS-'].rstrip()):
                                sg.popup('Valor da mensalidade deve ser no formato xxx,xx')
                            else:
                                ##########################################
                                # CHECAGEM DE VALORES
                                ##########################################
                                opcao, _ = sg.Window('Continuar?', [[sg.T('Aceita as alterações?')],
                                                                    [sg.Yes(s=10, button_text='Sim'),
                                                                     sg.No(s=10, button_text='Não')]],
                                                     disable_close=True, modal=True).read(close=True)
                                if opcao == 'Sim':
                                    cad_atv = ''
                                    # print(self.windowinfo['-RATV-'])
                                    if self.valuesinfo['-RATV-']:
                                        cad_atv = 'S'
                                    else:
                                        cad_atv = 'N'
                                    alterar_aluno(self.valuesinfo['-NOME-'].rstrip(), self.valuesinfo['-END-'].rstrip(),
                                                  self.valuesinfo['-TEL1-'].rstrip(), self.valuesinfo['-CPF-'].rstrip(),
                                                  self.valuesinfo['-EMAIL-'].rstrip(),
                                                  self.valuesinfo['-MAT-'].rstrip(), self.valuesinfo['-VEN-'].rstrip(),
                                                  self.valuesinfo['-VALMENS-'].rstrip(), cad_atv, self.indiceinfo)
                                    if self.values['-BUSCAR-'] != '':
                                        if self.values['-ATIVOS-']:
                                            busca = buscar_por_nome(str(self.values['-BUSCAR-'].rstrip()), True)
                                        else:
                                            busca = buscar_por_nome(str(self.values['-BUSCAR-'].rstrip()), False)
                                        self.window['-TABELA-'].update(values=busca)
                                    else:
                                        if self.values['-ATIVOS-']:
                                            temp = ler_todos_dados_ativos()
                                        else:
                                            temp = ler_todos_dados()
                                        # temp = ler_todos_dados()
                                        self.window['-TABELA-'].update(values=temp)
                                    sg.Popup('Alterações efetuadas com sucesso.')

                        #########################################
                        # GERA RECIBO PARA IMPRESSAO
                        #########################################

                        if self.eventinfo == '-TABELAPG-':
                            self.rowinfo = self.valuesinfo[self.eventinfo]
                            self.dadosinfo = self.windowinfo['-TABELAPG-'].Values

                        if self.eventinfo == '-IMPRIME-':
                            if len(self.rowinfo) != 0:
                                # print('Self.dadosinfo ', self.dadosinfo)
                                # print('RECIBO')
                                # print(self.valuesinfo['-NOME-'].rstrip(),self.dadosinfo[self.rowinfo[0]][2],self.dadosinfo[self.rowinfo[0]][0],self.valuesinfo['-VEN-'].rstrip(),self.dadosinfo[self.rowinfo[0]][1],self.dadosinfo[self.rowinfo[0]][3])
                                # print(self.valuesinfo['-NOME-'].rstrip(),str(self.dadosinfo[self.rowinfo[0]][2]),str(self.dadosinfo[self.rowinfo[0]][0]),self.valuesinfo['-VEN-'].rstrip(),str(self.dadosinfo[self.rowinfo[0]][1]),str(self.dadosinfo[self.rowinfo[0]][3]))
                                gera_recibo_pdf(self.valuesinfo['-NOME-'].rstrip(),
                                                str(self.dadosinfo[self.rowinfo[0]][3]),
                                                str(self.dadosinfo[self.rowinfo[0]][1]),
                                                self.valuesinfo['-VEN-'].rstrip(),
                                                str(self.dadosinfo[self.rowinfo[0]][0]),
                                                str(self.dadosinfo[self.rowinfo[0]][4]))
                                self.windowinfo.perform_long_operation(
                                    lambda: os.system('\"' + pdfviewer + '\" ' + arq_recibo), '-FUNCTION COMPLETED-')
                            # os.system(arq_recibo)
                            #    print('dadosinfo[rowinfo]:',dadosinfo[rowinfo[0]])
                            #    print('rowinfo INDEX:',dadosinfo[rowinfo[0]][0])
                            #                    ObjMaisInfo = MaisInfo()
                            #                    ObjMaisInfo.indiceinfo = self.dadosinfo[self.rowinfo[0]][0]
                            #                    ObjMaisInfo.run()
                            else:
                                sg.Popup('Selecione um registro na tabela.')

                        if self.eventinfo == '-APAGA-':
                            opcao, _ = sg.Window('Continuar?', [[sg.T('Tem certeza? Esta operação é definitiva.')],
                                                                [sg.Yes(s=10, button_text='Sim'),
                                                                 sg.No(s=10, button_text='Não')]], disable_close=True,
                                                 modal=True).read(close=True)
                            # if opcao == 'Não':
                            #    break
                            if opcao == 'Sim':

                                apaga_registro(self.indiceinfo)
                                if self.values['-ATIVOS-']:
                                    temp = ler_todos_dados_ativos()
                                else:
                                    temp = ler_todos_dados()
                                # temp = ler_todos_dados()
                                self.window['-TABELA-'].update(values=temp)
                                sg.Popup('Registro excluído definitivamente.')
                                break
                    # print(self.eventinfo, self.valuesinfo)
                    self.windowinfo.close()

                else:
                    sg.Popup('Selecione um registro na tabela.')
            ##################################################
            #             JANELA MAIS INFORMACOES
            ##################################################

            #            if self.event == '-ATIVOS-':
            #                if self.values['-ATIVOS-']:
            #                    busca = ler_todos_dados_ativos()
            #                else:
            #                    busca = ler_todos_dados()
            # print(busca)
            #                self.window['-TABELA-'].update(values=busca)

            if self.event == 'Backup parcial':
                obj_backup_db = BackupDB()
                obj_backup_db.run()

            if self.event == 'Backup completo':
                obj_backup_completo = BackupCompleto()
                obj_backup_completo.run()

            if self.event == 'Tela principal':
                obj_ajuda = Ajuda()
                obj_ajuda.nomearquivo = 'telaprincipal.html'
                obj_ajuda.run()

            if self.event == 'Recebimento':
                obj_relatorio_mensal = RelatorioMensal()
                obj_relatorio_mensal.run()

            if self.event == 'Devedores':
                obj_rel_nao_pago = RelNaoPago()
                obj_rel_nao_pago.run()

            if self.event == '-BBUSCA-' or self.event == '-ATIVOS-':
                # print(str(self.values['-BUSCAR-'].rstrip()))
                # busca = buscar_por_nome(str(self.window['-BUSCAR-']))
                if self.values['-ATIVOS-']:
                    busca = buscar_por_nome(str(self.values['-BUSCAR-'].rstrip()), True)
                else:
                    busca = buscar_por_nome(str(self.values['-BUSCAR-'].rstrip()), False)
                # busca = buscar_por_nome(str(self.values['-BUSCAR-'].rstrip()))
                # print(busca)
                self.window['-TABELA-'].update(values=busca)

            # if self.event == '-ATUALIZAR-':
            #    sg.popup_non_blocking('Popup', *self.values['-ATUALIZAR-'])

            if self.event in ('-LIMPA-', '-ATUALIZAR-'):
                # print(str(self.values['-BUSCAR-'].rstrip()))
                self.window['-BUSCAR-'].update('')
                # busca = buscar_por_nome(str(self.values['-BUSCAR-'].rstrip()))
                if self.values['-ATIVOS-']:
                    busca = ler_todos_dados_ativos()
                else:
                    busca = ler_todos_dados()
                # print(busca)
                self.window['-TABELA-'].update(values=busca)

            ##################################################
            #             JANELA CADASTRO ALUNO
            ##################################################

            if self.event == '-AD-' or self.event == 'Adicionar aluno':
                self.layout2 = [
                    [sg.Text('Cadastro', font='_ 25', key='-NOMEALUNO-')],
                    [sg.HorizontalSeparator(k='-SEP-')],
                    [sg.Text('', size=(7, 1))],
                    [sg.Text('Nome:', size=(8, 1)),
                     sg.Input(key='-NOME-', size=(41, 1), tooltip='Nome do aluno', focus=True)],
                    [sg.Text('Endereço:', size=(8, 1)), sg.Input(key='-END-', size=(41, 1), tooltip='Endereço')],
                    [sg.Text('Telefone:', size=(8, 1)),
                     sg.Input(key='-TEL1-', size=(14, 1), tooltip='Telefone ou celular'), sg.Text('CPF:', size=(8, 1)),
                     sg.Input(key='-CPF-', size=(14, 1), tooltip='Pode ficar em branco')],  # ,enable_events=True
                    [sg.Text('Email:', size=(8, 1)), sg.Input(key='-EMAIL-', size=(41, 1))],
                    [sg.Text('Matrícula:', size=(8, 1)),
                     sg.Input(key='-MAT-', size=(9, 1), tooltip='Data da matrícula (não pode ficar em branco)'),
                     sg.CalendarButton('Data', locale='pt_BR', format='%d/%m/%Y', month_names=meses,
                                       day_abbreviations=dias), sg.Text('Vencimento dia:', size=(13, 1)),
                     sg.Input(key='-VEN-', size=(6, 1), tooltip='Dia do vencimento da mensalidade com dois dígitos')],
                    [sg.Text('Valor da mensalidade R$:', size=(19, 1)),
                     sg.Input(key='-VALMENS-', size=(8, 1), tooltip='Valor da mensalidade no formato xxx,xx')],

                    # [sg.Radio('Ativo', "RadioAtivo", default=True, k='-RATV-'), sg.Radio('Inativo', "RadioAtivo",
                    # k='-RINT-')],

                    [sg.Text('', size=(7, 1))],
                    [sg.Button('Cadastrar', key='-CAD-', bind_return_key=True), sg.Button('Ajuda', k='-AJUDA-'),
                     sg.Button('Fechar', key='-FECHAR-')]
                ]

                self.window2 = sg.Window('Cadastro', self.layout2, use_default_focus=True, finalize=True, modal=True)
                self.window2.bind('<F1>', '-AJUDA-')
                while True:
                    # EDITANDO
                    dttmp = datetime.now()
                    dttmp2 = dttmp.strftime('%d/%m/%Y')
                    self.window2['-MAT-'].update(dttmp2)
                    self.window2['-VEN-'].update('10')
                    self.event2, self.values2 = self.window2.read()
                    # print(self.event2,self.values2)
                    # print(self.event2)
                    # print(self.values2)
                    if self.event2 == sg.WIN_CLOSED or self.event2 == '-FECHAR-':
                        break

                    if self.event2 == '-AJUDA-':
                        obj_ajuda = Ajuda()
                        obj_ajuda.nomearquivo = 'cadastro.html'
                        obj_ajuda.run()

                    if self.event2 == '-CAD-':
                        if self.values2['-NOME-'].rstrip() == '':
                            sg.popup('Campo nome não pode ser vazio.')
                        elif self.values2['-END-'].rstrip() == '':
                            sg.popup('Campo endereço não pode ser vazio.')
                        elif self.values2['-TEL1-'].rstrip() != '' and not \
                                re.fullmatch(regexTelefone, self.values2['-TEL1-'].rstrip()):
                            sg.popup('Telefone deve ser no formato (xx)xxxxx-xxxx')
                        elif self.values2['-CPF-'].rstrip() != '' and not \
                                re.fullmatch(regexCPF, self.values2['-CPF-'].rstrip()):
                            sg.popup('CPF deve ser no formato 000.000.000-00')
                        elif self.values2['-EMAIL-'].rstrip() != '' and not \
                                re.fullmatch(regexEmail, self.values2['-EMAIL-'].rstrip()):
                            sg.popup('Campo email deve ser no formato abc@de.fgh')
                        elif self.values2['-MAT-'].rstrip() == '':
                            sg.popup('Data de matrícula não pode ser vazio.')
                        elif self.values2['-VEN-'].rstrip() == '':
                            sg.popup('Dia de vencimento não pode ser vazio.')
                        elif self.values2['-VALMENS-'].rstrip() == '':
                            sg.popup('Campo valor da mensalidade não pode ser vazio.')
                        elif self.values2['-VALMENS-'].rstrip() != '' and not \
                                re.fullmatch(regexDinheiro, self.values2['-VALMENS-'].rstrip()):
                            sg.popup('Valor da mensalidade deve ser no formato xxx,xx.')
                        elif self.values2['-VEN-'].rstrip() != '' and not \
                                re.fullmatch(regexDia, self.values2['-VEN-'].rstrip()):
                            sg.popup('Data de vencimento deve ser entre 01 e 31.')
                        elif self.values2['-VALMENS-'].rstrip() != '' and not \
                                re.fullmatch(regexDinheiro, self.values2['-VALMENS-'].rstrip()):
                            sg.popup('Valor da mensalidade deve ser no formato xxx,xx')
                        else:
                            # cad_atv = ''
                            # if self.values['-RATV-']:
                            #    cad_atv='S'
                            # else:
                            #    cad_atv='N'
                            cadastrar_aluno(self.values2['-NOME-'].rstrip(), self.values2['-END-'].rstrip(),
                                            self.values2['-TEL1-'].rstrip(), self.values2['-CPF-'].rstrip(),
                                            self.values2['-EMAIL-'].rstrip(), self.values2['-MAT-'].rstrip(),
                                            self.values2['-VEN-'].rstrip(), self.values2['-VALMENS-'].rstrip(), 'S')
                            # cria uma entrada para este aluno no banco mensalidades
                            mensalidades_cria(alunos_ultimo())
                            self.window2['-NOME-'].update('')
                            self.window2['-END-'].update('')
                            self.window2['-TEL1-'].update('')
                            self.window2['-CPF-'].update('')
                            self.window2['-EMAIL-'].update('')
                            self.window2['-MAT-'].update('')
                            self.window2['-VEN-'].update('')
                            self.window2['-VALMENS-'].update('')
                            self.window2['-NOME-'].SetFocus()
                            # sg.popup('Cadastro realizado com sucesso.')
                            self.cad_real = True
                            if self.values['-ATIVOS-']:
                                temp = ler_todos_dados_ativos()
                            else:
                                temp = ler_todos_dados()
                            # temp = ler_todos_dados()
                            self.window['-TABELA-'].update(values=temp)
                self.window2.close()

            ##################################################
            #             JANELA CADASTRO ALUNO
            ##################################################

            if self.event == '-TABELA-':
                # if self.event == 'bind_return_key':
                self.row = self.values[self.event]
                self.dados = self.window['-TABELA-'].Values
                # print(self.row)
                # print(self.dados)
                # aluno = buscar_aluno_index(indice)
                # indice = ler_todos_dados()[row]
                # i = 0
                # while i < len(row):
                #    print('DT_SEL', row[i])
                #    i = i + 1
                # print('ROW',row)

            if self.event in ('-RECEBE-', 'Receber mensalidade'):
                if len(self.row) != 0:
                    if mensalidade_busca(self.dados[self.row[0]][0]):
                        print(str(mensalidade_busca(self.dados[self.row[0]][0])))
                        tmpstring = str(mensalidade_busca(self.dados[self.row[0]][0]))
                        finalstr = tmpstring.translate({ord(c): None for c in "[(',)]"})
                        print('finalstr: ', finalstr)
                        print('numero aluno: ', self.dados[self.row[0]][0])
                        tmpdate = datetime.strptime(finalstr, '%d/%m/%Y')
                        print(tmpdate)
                        # tmpdate = tmpdate[3:5]
                        tmpnowstr = datetime.strftime(datetime.now(), '%d/%m/%Y')
                        tmpnow = datetime.strptime(tmpnowstr, '%d/%m/%Y')
                        # tmpnow = tmpnow[0:2]
                        if tmpdate < tmpnow:
                            obj_recebe = Receber()
                            obj_recebe.indicealuno = self.dados[self.row[0]][0]
                            obj_recebe.run()
                        else:
                            sg.popup('Este aluno já pagou a mensalidade deste mês.')
                    else:
                        obj_recebe = Receber()
                        obj_recebe.indicealuno = self.dados[self.row[0]][0]
                        obj_recebe.run()
                else:
                    sg.Popup('Selecione um registro na tabela.')
                # row =
                # if len(row) != 0:
                # ObjRecebe = Recebe()
                # ObjRecebe.indicealuno = dados
                # ObjRecebe.run()

                # data_selected =
                # data_selected = [ler_todos_dados()[row] for row in self.values[self.event]]
                # print('ROW:',row)
                # print('LEN ROW:',len(row))
                # if len(row) == 0:
                #   print('SAINDO DO CODIGO')
                # else:
                # data_selected = [ler_todos_dados()[row] for row in self.values[self.event]]
                # print(row)
                # i = 0
                # while i < len(data_selected[0]):
                #    print('DT_SEL', data_selected[0][i])
                #    i = i + 1
                # print('DataSelected:', data_selected[0][0])
                # data_index=int(data_selected[0][0])
                # print('indice:', data_index)
                #    ObjMaisInfo = MaisInfo()
                # ObjMaisInfo.indice = data_index
                # print('ObjMaisInfo.indice',ObjMaisInfo.indice)
                #   ObjMaisInfo.run() #PAREI AQUIs
                # print(row)
                # if row:
                # sg.Popup(f'Selected row is {row}')
                # dados_aluno = str(indice_aluno(self.values['listagem'][0]))
                # ObjMaisInfo = MaisInfo()
                # ObjMaisInfo.indice = dados_aluno
                # ObjMaisInfo.run()
            # if isinstance(self.event, tuple):
            #    if self.event[0] == '-TABLE-':

            # if self.event[2][0] == -1 and self.event[2][1] != -1:           # Header was clicked and wasn't the
            # "row" column

            #            col_num_clicked = self.event[2][1]
            #        self.window['-CLICKED-'].update(f'{self.event[2][0]},{self.event[2][1]}')
            # if self.event == '-TABELA-':
            #    print('EVENTO TABELA!')
            # print(self.values)
            # print(self.event)
        self.window.close()


# FINAL TELA PRINCIPAL

# INICIO TELA DE BACKUP
class BackupDB:
    pasta = ''
    nomearqorig = ''
    nomearqbkp = ''

    def __init__(self):
        self.values = None
        self.event = None
        self.layout = [
            [sg.Text('Cópia de segurança', font='_ 25')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.Text('Selecione a pasta onde deseja guardar uma cópia do banco de dados:')],
            [sg.Combo(sorted(sg.user_settings_get_entry('-foldernames-', [])),
                      default_value=sg.user_settings_get_entry('-last foldername-', ''), size=(50, 1),
                      key='-FOLDERNAME-'), sg.FolderBrowse('Abrir pasta...')],
            [sg.Button('Gerar cópia', k='-BACKUP-'), sg.Button('Sair', k='-SAIR-')]
        ]

        self.window = sg.Window('Cópia de segurança', self.layout, disable_minimize=True)

    def run(self):
        while True:
            self.event, self.values = self.window.read()
            if self.event in (sg.WIN_CLOSED, '-SAIR-'):
                break
            if self.event == '-BACKUP-':
                sg.user_settings_set_entry('-foldernames-', list(
                    set(sg.user_settings_get_entry('-foldernames-', []) + [self.values['-FOLDERNAME-'], ])))
                sg.user_settings_set_entry('-last foldername-', self.values['-FOLDERNAME-'])
                self.nomearqorig = dbfile
                data = datetime.now()
                data = data.strftime("%d-%m-%Y")
                self.nomearqbkp = self.values['-FOLDERNAME-'].rstrip() + '/' + 'sistema.db.' + data + '.bkp'
                data = datetime.now()
                data = data.strftime("%d/%m/%Y")
                sg.user_settings_set_entry('-lastbackup-', data)
                # print(self.nomearqorig)
                # print(self.nomearqbkp)
                try:
                    shutil.copyfile(self.nomearqorig, self.nomearqbkp)
                    sg.popup('Arquivo gravado com sucesso.')
                except:
                    sg.popup('Erro durante a gravação do arquivo.')
        self.window.close()


# FINAL TELA DE BACKUP

# INICIO BACKUP COMPLETO
class BackupCompleto:
    pastabkp = ''
    pastaorig = '.'
    nomearq = ''

    def __init__(self):
        self.values = None
        self.event = None
        self.layout = [
            [sg.Text('Cópia de segurança completa', font='_ 25')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.T('Esta função gera um arquivo compactado.')],
            [sg.T('De preferência, use como destino um drive removível (pendrive).')],
            [sg.Text('Selecione a pasta onde deseja guardar uma cópia do sistema:')],
            [sg.Combo(sorted(sg.user_settings_get_entry('-pastasbkpcompleto-', [])),
                      default_value=sg.user_settings_get_entry('-ultimapastabkpcompleto-', ''), size=(50, 1),
                      key='-NOMEDAPASTA-'), sg.FolderBrowse('Abrir pasta...')],
            [sg.Button('Gerar cópia', k='-BACKUP-'), sg.Button('Sair', k='-SAIR-')]
        ]

        self.window = sg.Window('Cópia de segurança', self.layout, disable_minimize=True)

    def run(self):
        while True:
            self.event, self.values = self.window.read()
            if self.event in (sg.WIN_CLOSED, '-SAIR-'):
                break
            if self.event == '-BACKUP-':
                sg.user_settings_set_entry('-pastasbkpcompleto-', list(
                    set(sg.user_settings_get_entry('-pastasbkpcompleto-', []) + [self.values['-NOMEDAPASTA-'], ])))
                sg.user_settings_set_entry('-ultimapastabkpcompleto-', self.values['-NOMEDAPASTA-'])
                data = datetime.now()
                data = data.strftime("%d-%m-%Y")
                # self.pastabkp = self.values['-NOMEDAPASTA-'].rstrip() + '/' + 'sistema' + data
                self.pastabkp = self.values['-NOMEDAPASTA-'].rstrip() + '/'
                self.nomearq = 'sistema-' + data
                # data = datetime.now()
                # data = data.strftime("%d/%m/%Y")
                # sg.user_settings_set_entry('-lastbackup-',data)
                # print(self.pastabkp)
                arquivos = os.listdir(self.pastaorig)
                # print(arquivos)
                # shutil.copytree(self.pastaorig,self.pastabkp)
                try:
                    shutil.make_archive((self.pastabkp + self.nomearq), 'zip', self.pastabkp, self.pastaorig)
                    sg.popup('Arquivo compactado gerado com sucesso.')
                except:
                    sg.popup('Erro na criação do arquivo compactado.')
                # print(self.nomearqbkp)
                # try:
                #    shutil.copyfile(self.nomearqorig,self.nomearqbkp)
                #    sg.popup('Arquivo gravado com sucesso.')
                # except:
                #    sg.popup('Erro durante a gravação do arquivo.')
        self.window.close()


# FINAL BACKUP COMPLETO

#######################################
# RELATORIOS
#######################################

# INICIO DE RELATORIO DE PAGAMENTO MENSAL
class RelatorioMensal:
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro',
             'Outubro', 'Novembro', 'Dezembro']
    rot_tabela = ['Data', 'Aluno', 'Atraso', 'Rec. por', 'Valor']

    def __init__(self):
        self.values = None
        self.event = None
        self.layout = [
            [sg.Text('Relatório de pagamentos do mês', font='_ 25', key='-TITULO-')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.Text('Mês desejado:'), sg.Combo(meses, key='-MES-', default_value=mesatual(), enable_events=True),
             # TODO
             sg.T('Ano:'), sg.I(default_text='2022', s=(10, 1), k='-ANO-')],
            [sg.Table(values=[], headings=self.rot_tabela,
                      # max_col_width=15,
                      auto_size_columns=True,
                      num_rows=15,
                      def_col_width=10,
                      alternating_row_color='lightblue4',
                      key='-TABLE-',
                      selected_row_colors='black on lightblue1',
                      enable_events=True,
                      expand_x=True,
                      expand_y=True,
                      enable_click_events=True
                      )],
            [sg.Push(), sg.T('Valor total recebido:'), sg.I(k='-TOTAL-', disabled=True, s=(10, 1))],
            [sg.Button('Gerar relatório', key='-GERA-', bind_return_key=True),
             sg.Button('Imprimir', key='-IMPRIME-', disabled=True), sg.Button('Fechar', key='-FECHAR-')]

        ]

        self.window = sg.Window('Relatório mensal', self.layout, size=(
            700, 500))  # return_keyboard_events=True, enable_close_attempted_event=True modal=True,

    def run(self):
        while True:
            self.event, self.values = self.window.read()
            mes = 0
            mesano = ''
            if self.values['-MES-'].rstrip() == 'Janeiro':
                mes = 1
            elif self.values['-MES-'].rstrip() == 'Fevereiro':
                mes = 2
            elif self.values['-MES-'].rstrip() == 'Março':
                mes = 3
            elif self.values['-MES-'].rstrip() == 'Abril':
                mes = 4
            elif self.values['-MES-'].rstrip() == 'Maio':
                mes = 5
            elif self.values['-MES-'].rstrip() == 'Junho':
                mes = 6
            elif self.values['-MES-'].rstrip() == 'Julho':
                mes = 7
            elif self.values['-MES-'].rstrip() == 'Agosto':
                mes = 8
            elif self.values['-MES-'].rstrip() == 'Setembro':
                mes = 9
            elif self.values['-MES-'].rstrip() == 'Outubro':
                mes = 10
            elif self.values['-MES-'].rstrip() == 'Novembro':
                mes = 11
            elif self.values['-MES-'].rstrip() == 'Dezembro':
                mes = 12

            if self.event == '-GERA-' or self.event == '-MES-':
                mesano = str(mes) + '/' + str(self.values['-ANO-'].rstrip())
                self.window['-TABLE-'].update(rel_fin_mensal(mesano))
                calc_val_rec = rel_fin_mensal(mesano)
                val_rec = 0.00
                i = 0
                while i < len(calc_val_rec):
                    valor = calc_val_rec[i][4]
                    valor = valor.replace(',', '.')
                    val_rec = val_rec + float(valor)
                    # print(val_rec)
                    i = i + 1
                valfinal = str(val_rec).replace('.', ',')
                valfinal = valfinal + '0'
                self.window['-TOTAL-'].update(valfinal)
                self.window['-IMPRIME-'].update(disabled=False)

            if self.event == '-IMPRIME-':
                relpdf = FPDF('P', 'cm', 'A4')
                relpdf.add_page()
                relpdf.add_font('Calibri', 'I', 'Calibrii.ttf', uni=True)
                relpdf.add_font('Calibri', 'B', 'Calibrib.ttf', uni=True)
                relpdf.add_font('Calibri', '', 'Calibri.ttf', uni=True)
                relpdf.image(imagem_peq, 16.6, 1.6)
                relpdf.set_font('Calibri', 'B', 14)
                relpdf.cell(0, 0.6, '', 0, 2, 'C')
                relpdf.cell(0, 0.6, '', 0, 2, 'C')
                relpdf.cell(0, 0.6, '', 0, 2, 'C')
                relpdf.cell(0, 0.6, '', 0, 2, 'C')
                tempstr = 'Relatório de recebimento do mês de ' + str(self.values['-MES-'].rstrip()) + ' de ' + \
                          self.values['-ANO-'].rstrip()
                relpdf.line(1, 4.5, 20, 4.5)
                relpdf.cell(0, 0.6, tempstr, 0, 2, 'C')
                relpdf.cell(0, 2, '', 0, 2, 'C')
                templist = rel_fin_mensal(mesano)
                relpdf.cell(1.4, 0.6, str(''), 0, 0, 'L')
                relpdf.cell(3.8, 0.6, str('Data do pagto.'), 0, 0, 'L')
                relpdf.cell(5.8, 0.6, str('Nome'), 0, 0, 'L')
                relpdf.cell(2.4, 0.6, str('Atraso.'), 0, 0, 'L')
                relpdf.cell(3, 0.6, str('Rec. por'), 0, 0, 'L')
                relpdf.cell(6.2, 0.6, str('Valor'), 0, 1, 'L')
                i = 0
                while i < len(templist):
                    relpdf.cell(1.6, 0.6, str(''), 0, 0, 'L')
                    tempstr = templist[i][0]
                    # print(tempstr)
                    relpdf.cell(3.6, 0.6, str(tempstr), 0, 0, 'L')
                    tempstr = templist[i][1]
                    # print(tempstr)
                    # relpdf.cell(0,0.6,str(tempstr),0,0,'R')
                    relpdf.cell(6.2, 0.6, str(tempstr), 0, 0, 'L')
                    tempstr = templist[i][2]
                    relpdf.cell(2, 0.6, str(tempstr), 0, 0, 'L')
                    tempstr = templist[i][3]
                    relpdf.cell(3, 0.6, str(tempstr), 0, 0, 'L')
                    tempstr = templist[i][4]
                    relpdf.cell(1, 0.6, str(tempstr), 0, 1, 'L')
                    i = i + 1
                relpdf.cell(0, 0.6, '', 0, 2, 'C')
                relpdf.line(relpdf.get_x(), relpdf.get_y(), 20, relpdf.get_y())
                tempstr = 'Valor total recebido: ' + self.values['-TOTAL-'].rstrip()
                relpdf.cell(11.8, 0.6, str(''), 0, 0, 'L')
                relpdf.cell(0, 0.6, str(tempstr), 0, 2, 'L')
                # relpdf.output(arq_relatorio, 'F')
                relpdf.output(arq_relatorio)
                self.window.perform_long_operation(lambda: os.system('\"' + pdfviewer + '\" ' + arq_relatorio),
                                                   '-FUNCTION COMPLETED-')

            if self.event == sg.WIN_CLOSED or self.event == '-FECHAR-':
                break

        self.window.close()


# FINAL DE RELATORIO DE PAGAMENTO MENSAL

# INICIO DE RELATORIO DE NAO PAGADORES MENSAL
class RelNaoPago:
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro',
             'Outubro', 'Novembro', 'Dezembro']
    rot_tabela = ['Aluno', 'Último pagamento', 'Valor', 'Dia vencto.']
    larg_col = [25, 15, 15, 12]

    def __init__(self):
        self.values = None
        self.event = None
        self.layout = [
            [sg.Text('Relatório de não pagadores', font='_ 25', key='-TITULO-')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.Text('Mês desejado:'), sg.Combo(meses, key='-MES-', default_value=mesatual(), enable_events=True),
             sg.T('Ano:'),
             sg.I(default_text='2022', s=(10, 1), k='-ANO-')],
            [sg.Radio('Somente mês selecionado', "RadioDemo", default=True, k='-R1-'),
             sg.Radio('Mês selecionado e anteriores', "RadioDemo", k='-R2-')],
            [sg.Table(values=[], headings=self.rot_tabela, col_widths=self.larg_col,
                      # max_col_width=15,
                      auto_size_columns=False,
                      num_rows=15,
                      def_col_width=10,
                      alternating_row_color='lightblue4',
                      key='-TABLE-',
                      selected_row_colors='black on lightblue1',
                      enable_events=True,
                      expand_x=True,
                      expand_y=True,
                      enable_click_events=True
                      )],
            [sg.Push(), sg.T('Valor total devido:'), sg.I(k='-TOTAL-', disabled=True, s=(10, 1))],
            [sg.Button('Gerar relatório', key='-GERA-', bind_return_key=True), sg.Button('Fechar', key='-FECHAR-')]

        ]

        self.window = sg.Window('Relatório mensal', self.layout, size=(
            700, 500))  # return_keyboard_events=True, enable_close_attempted_event=True modal=True,

    def run(self):
        while True:
            self.event, self.values = self.window.read()
            mes = ''
            if self.values['-MES-'].rstrip() == 'Janeiro':
                mes = '01'
            elif self.values['-MES-'].rstrip() == 'Fevereiro':
                mes = '02'
            elif self.values['-MES-'].rstrip() == 'Março':
                mes = '03'
            elif self.values['-MES-'].rstrip() == 'Abril':
                mes = '04'
            elif self.values['-MES-'].rstrip() == 'Maio':
                mes = '05'
            elif self.values['-MES-'].rstrip() == 'Junho':
                mes = '06'
            elif self.values['-MES-'].rstrip() == 'Julho':
                mes = '07'
            elif self.values['-MES-'].rstrip() == 'Agosto':
                mes = '08'
            elif self.values['-MES-'].rstrip() == 'Setembro':
                mes = '09'
            elif self.values['-MES-'].rstrip() == 'Outubro':
                mes = '10'
            elif self.values['-MES-'].rstrip() == 'Novembro':
                mes = '11'
            elif self.values['-MES-'].rstrip() == 'Dezembro':
                mes = '12'

            if (self.event == '-GERA-' or self.event == '-MES-') and self.values['-R1-'] is True:
                # print('entrou no if')
                mesano = mes + '/' + str(self.values['-ANO-'].rstrip())
                self.window['-TABLE-'].update(rel_nao_pagadores(mesano, 'atual'))
                calc_val_dev = rel_nao_pagadores(mesano, 'atual')
                val_dev = 0.00
                i = 0
                while i < len(calc_val_dev):
                    valor = calc_val_dev[i][2]
                    # print(calc_val_dev[i][2])
                    # print(calc_val_dev[i])
                    valor = valor.replace(',', '.')
                    val_dev = val_dev + float(valor)
                    # print(val_rec)
                    i = i + 1
                valfinal = str(val_dev).replace('.', ',')
                valfinal = valfinal + '0'
                self.window['-TOTAL-'].update(valfinal)

            if (self.event == '-GERA-' or self.event == '-MES-') and self.values['-R2-'] is True:
                # print('entrou no if')
                mesano = mes + '/' + str(self.values['-ANO-'].rstrip())
                self.window['-TABLE-'].update(rel_nao_pagadores(mesano, 'anteriores'))
                calc_val_dev = rel_nao_pagadores(mesano, 'anteriores')
                val_dev = 0.00
                i = 0
                while i < len(calc_val_dev):
                    valor = calc_val_dev[i][2]
                    # print(calc_val_dev[i][2])
                    # print(calc_val_dev[i])
                    valor = valor.replace(',', '.')
                    val_dev = val_dev + float(valor)
                    # print(val_rec)
                    i = i + 1
                valfinal = str(val_dev).replace('.', ',')
                valfinal = valfinal + '0'
                self.window['-TOTAL-'].update(valfinal)

            if self.event == sg.WIN_CLOSED or self.event == '-FECHAR-':
                break

        self.window.close()


# FINAL DE RELATORIO DE NAO PAGADORES MENSAL

############################################
# PRINCIPAL
sg.user_settings_filename(path=ajustes)
# splashscreen()
ObjPrincipal = Principal()
ObjPrincipal.run()
############################################


# print('DBFILE',dbfile)
# print(os.getcwd())
# ObjRecebe = Recebe()
# ObjRecebe.indicealuno = 2
# ObjRecebe.run()

# ObjCadastro = CadastroAluno()
# ObjCadastro.run()
# geravencto(10)

# ObjRelMen = RelatorioMensal()
# ObjRelMen.run()
# variavel = '06/2022'
# rel_fin_mensal(variavel)
# ObjBackupDB = BackupDB()
# ObjBackupDB.run()
# gera_recibo_pdf('Zé das Couves','100,00','10/10/2010','10/10/2010','0','Andréia')

# ObjMaisInfo = MaisInfo()
# ObjMaisInfo.indice = 1
# ObjMaisInfo.run()

# print(pdfviewer)
# temp = '\"'+pdfviewer + '\" ' + arq_recibo
# print('\"'+pdfviewer + ' ' + arq_recibo+'\"')
# print(temp)
# os.system(temp)


# ObjBackupCompleto = BackupCompleto()
# ObjBackupCompleto.run()
