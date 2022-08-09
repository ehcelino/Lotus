from fpdf import FPDF
import os

imagem_peq = os.path.join(os.getcwd(), 'recursos', 'logo_small.png')
pdfviewer = os.path.join(os.getcwd(), 'recursos', 'SumatraPDF.exe')
arq_recibo = 'recibo.pdf'
arq_relatorio = 'relatorio.pdf'
arq_lista = 'lista.pdf'
arq_recibo_vendas = 'vendas.pdf'


# INICIO FUNCAO GERA RECIBO
def gera_recibo_pdf(nome, valorpago, datapgto, datavencto, atraso, usuario):
    rpdf = FPDF('P', 'cm', 'A4')
    rpdf.add_page()
    rpdf.add_font('Roboto', '', 'Roboto-Regular.ttf', uni=True)
    rpdf.add_font('Roboto', 'I', 'Roboto-MediumItalic.ttf', uni=True)
    rpdf.add_font('Roboto', 'B', 'Roboto-Medium.ttf', uni=True)
    rpdf.add_font('RobotoBold', 'B', 'Roboto-Bold.ttf', uni=True)
    rpdf.set_font('RobotoBold', 'B', 14)
    rpdf.image(imagem_peq, 16.6, 1.6)
    rpdf.rect(1, 1, 19, 8.8, 'D')
    rpdf.cell(0, 0.6, '', 0, 2, 'C')
    rpdf.cell(0, 0.6, 'RECIBO DE PAGAMENTO DE MENSALIDADE', 0, 2, 'C')
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(0, 0.6, 'Lótus Condicionamento Dinâmico Integrado', 0, 2, 'C')
    rpdf.cell(0, 0.6, 'Andréia de Cássia Gonçalves (CREF 020951-G/MG)', 0, 2, 'C')
    rpdf.set_font('Roboto', 'I', 14)
    rpdf.cell(0, 0.6, 'Rua Coronel Paiva, 12  Centro  Ouro Fino MG', 0, 2, 'C')
    rpdf.line(1, 4.5, 20, 4.5)
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(0.5, 1, '', 0, 1)
    rpdf.cell(0.5, 1, '')
    rpdf.cell(3.6, 1, 'Nome do aluno: ')
    rpdf.set_font('Roboto', '', 14)
    rpdf.cell(0, 1, nome, 0, 1)
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(0.5, 1, '')
    rpdf.cell(4.7, 1, 'Valor do pagamento: ')
    rpdf.set_font('Roboto', '', 14)
    rpdf.cell(2.5, 1, valorpago)
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(3.5, 1, '')
    rpdf.cell(4.6, 1, 'Data do pagamento: ')
    rpdf.set_font('Roboto', '', 14)
    rpdf.cell(1, 1, datapgto, 0, 1)
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(0.5, 1, '')
    rpdf.cell(4.4, 1, 'Dia do vencimento: ')
    rpdf.set_font('Roboto', '', 14)
    rpdf.cell(6.3, 1, datavencto)
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(1.7, 1, 'Atraso: ')
    rpdf.set_font('Roboto', '', 14)
    rpdf.cell(1, 1, atraso + ' dias', 0, 1)
    rpdf.cell(0.5, 1, '')
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(3.2, 1, 'Recebido por: ')
    rpdf.set_font('Roboto', '', 14)
    rpdf.cell(2.5, 1, usuario)
    # rpdf.cell(19, 10, 'Hello World!', 1)
    # rpdf.cell(40, 10, 'Hello World!', 1)
    # rpdf.cell(60, 10, 'Powered by FPDF.', 0, 1, 'C')
    # rpdf.output(arq_recibo, 'F')
    rpdf.output(arq_recibo)


# Imprime o recibo de vendas (produtos do estúdio)

def recibo_vendas_pdf(nome, valorpago, datapgto, produtos, usuario):
    # produtos: data, descrição e valor
    rpdf = FPDF('P', 'cm', 'A4')
    rpdf.add_page()
    rpdf.add_font('Roboto', '', 'Roboto-Regular.ttf', uni=True)
    rpdf.add_font('Roboto', 'I', 'Roboto-MediumItalic.ttf', uni=True)
    rpdf.add_font('Roboto', 'B', 'Roboto-Medium.ttf', uni=True)
    rpdf.add_font('RobotoBold', 'B', 'Roboto-Bold.ttf', uni=True)
    rpdf.set_font('RobotoBold', 'B', 14)
    rpdf.image(imagem_peq, 16.6, 1.6)
    rpdf.rect(1, 1, 19, 8.8, 'D')
    rpdf.cell(0, 0.6, '', 0, 2, 'C')
    rpdf.cell(0, 0.6, 'RECIBO DE PAGAMENTO DE PRODUTOS', 0, 2, 'C')
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(0, 0.6, 'Lótus Condicionamento Dinâmico Integrado', 0, 2, 'C')
    rpdf.cell(0, 0.6, 'Andréia de Cássia Gonçalves (CREF 020951-G/MG)', 0, 2, 'C')
    rpdf.set_font('Roboto', 'I', 14)
    rpdf.cell(0, 0.6, 'Rua Coronel Paiva, 12  Centro  Ouro Fino MG', 0, 2, 'C')
    rpdf.line(1, 4.5, 20, 4.5)
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(0.5, 1, '', 0, 1)
    rpdf.cell(0.2, 1, '')
    rpdf.cell(1.7, 1, 'Nome: ')
    rpdf.set_font('Roboto', '', 14)
    rpdf.cell(12.5, 1, nome, 0, 0)
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(1.3, 1, 'Data:', 0, 0)
    rpdf.set_font('Roboto', '', 14)
    rpdf.cell(0, 1, datapgto, 0, 1)
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(0, 0.6, 'Descrição', 0, 1, 'C')
    rpdf.set_font('Roboto', '', 14)
    for idx, x in enumerate(produtos):
        rpdf.cell(0.5, 0.6, '')
        tempstr = str(x[0])
        rpdf.cell(2.5, 0.6, tempstr, 0, 0, 'R')
        tempstr = str(x[1])
        rpdf.cell(6.5, 0.6, tempstr, 0, 0, 'L')
        tempstr = str(x[2])
        rpdf.cell(9, 0.6, tempstr, 0, 1, 'R')
    rpdf.cell(14.0, 0.6, '', 0, 0)
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(0, 0.6, 'Total:', 0, 0)
    rpdf.set_font('Roboto', '', 14)
    rpdf.cell(-0.5, 0.6, valorpago, 0, 1, 'R')
    rpdf.cell(0.2, 0.6, '', 0, 0)
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(3.5, 0.6, 'Recebido por:', 0, 0)
    rpdf.set_font('Roboto', '', 14)
    rpdf.cell(0, 0.6, usuario, 0, 0)
    rpdf.output(arq_recibo_vendas)


# Final imprime recibo de vendas

# IMPRIME UMA LISTA DE NOMES DE ALUNO E SEUS DIAS DE VENCIMENTO
def gera_lista_pdf(lista):
    rpdf = FPDF('P', 'cm', 'A4')
    rpdf.add_page()
    rpdf.add_font('Roboto', '', 'Roboto-Regular.ttf', uni=True)
    rpdf.add_font('Roboto', 'I', 'Roboto-MediumItalic.ttf', uni=True)
    rpdf.add_font('Roboto', 'B', 'Roboto-Medium.ttf', uni=True)
    rpdf.add_font('RobotoBold', 'B', 'Roboto-Bold.ttf', uni=True)
    rpdf.set_font('RobotoBold', 'B', 14)
    rpdf.image(imagem_peq, 16.6, 1.6)
    rpdf.rect(1, 1, 19, 3.5, 'D')
    rpdf.cell(0, 0.6, '', 0, 2, 'C')
    rpdf.cell(0, 0.6, 'LISTA DE ALUNOS ATIVOS', 0, 2, 'C')
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(0, 0.6, 'Lótus Condicionamento Dinâmico Integrado', 0, 2, 'C')
    rpdf.cell(0, 0.6, 'Andréia de Cássia Gonçalves (CREF 020951-G/MG)', 0, 2, 'C')
    rpdf.set_font('Roboto', 'I', 14)
    rpdf.cell(0, 0.6, 'Rua Coronel Paiva, 12  Centro  Ouro Fino MG', 0, 2, 'C')
    # rpdf.line(1, 4.5, 20, 4.5)
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(0.5, 1, '', 0, 1)
    rpdf.cell(0.1, 1, '')
    rpdf.cell(2, 1, 'Índice')
    rpdf.cell(0.5, 1, '')
    rpdf.cell(12.5, 1, 'Nome')
    rpdf.cell(4.7, 1, 'Vencimento', 0, 1)
    rpdf.set_font('Roboto', '', 14)
    tempx = 6
    for idx, x in enumerate(lista):
        rpdf.cell(0.5, 0.6, '')
        tempstr = str(x[0])
        rpdf.cell(0.5, 0.6, tempstr, 0, 0, 'R')
        rpdf.cell(1.5, 0.6, '')
        tempstr = str(x[1])
        rpdf.cell(13.8, 0.6, tempstr)
        tempstr = str(x[2])
        rpdf.cell(5, 0.6, tempstr, 0, 1)
        tempx = tempx + 0.6
        rpdf.line(1, tempx, 20, tempx)
        if tempx == 27.00000000000002:
            tempx = -0.25
        print(x[0], 'tempx ', tempx)
    # rpdf.cell(19, 10, 'Hello World!', 1)
    # rpdf.cell(40, 10, 'Hello World!', 1)
    # rpdf.cell(60, 10, 'Powered by FPDF.', 0, 1, 'C')
    # rpdf.output(arq_recibo, 'F')
    rpdf.output(arq_lista)


class PDF(FPDF):
    # def header(self):
    # Logo
    #     self.image('logo_pb.png', 10, 8, 33)
    # Arial bold 15
    #     self.set_font('Arial', 'B', 15)
    # Move to the right
    #     self.cell(80)
    # Title
    #     self.cell(30, 10, 'Title', 1, 0, 'C')
    # Line break
    #     self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-6.8)
        self.set_font('Roboto', 'B', 12)
        # Page number
        self.cell(0, 10, 'Página ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


# Instantiation of inherited class
# pdf = PDF()
# pdf.alias_nb_pages()
# pdf.add_page()
# pdf.set_font('Times', '', 12)
# for i in range(1, 41):
#     pdf.cell(0, 10, 'Printing line number ' + str(i), 0, 1)
# pdf.output('tuto2.pdf', 'F')


# Imprime uma lista de alunos em dívida e suas respectivas mensalidades atrasadas


def gera_lista_dividas(lista, mesano):
    # lista: índice, nome, atraso
    rpdf = PDF('P', 'cm', 'A4')
    rpdf.alias_nb_pages()
    rpdf.add_page()
    rpdf.add_font('Roboto', '', 'Roboto-Regular.ttf', uni=True)
    rpdf.add_font('Roboto', 'I', 'Roboto-MediumItalic.ttf', uni=True)
    rpdf.add_font('Roboto', 'B', 'Roboto-Medium.ttf', uni=True)
    rpdf.add_font('RobotoBold', 'B', 'Roboto-Bold.ttf', uni=True)
    rpdf.set_font('RobotoBold', 'B', 14)
    rpdf.image(imagem_peq, 16.6, 1.6)
    rpdf.rect(1, 1, 19, 3.5, 'D')
    rpdf.cell(0, 0.6, '', 0, 2, 'C')
    rpdf.cell(0, 0.6, 'LISTA DE ALUNOS EM DÍVIDA', 0, 2, 'C')
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(0, 0.6, 'Lótus Condicionamento Dinâmico Integrado', 0, 2, 'C')
    rpdf.cell(0, 0.6, 'Andréia de Cássia Gonçalves (CREF 020951-G/MG)', 0, 2, 'C')
    rpdf.set_font('Roboto', 'I', 14)
    rpdf.cell(0, 0.6, 'Rua Coronel Paiva, 12  Centro  Ouro Fino MG', 0, 2, 'C')
    # rpdf.line(1, 4.5, 20, 4.5)
    rpdf.set_font('Roboto', 'B', 14)
    rpdf.cell(0.8, 1, '', 0, 1)
    rpdf.cell(0.5, 1, 'Mês: ' + mesano, 0, 1)
    rpdf.cell(0.1, 1, '')
    rpdf.cell(2, 1, 'Índice')
    rpdf.cell(0.5, 1, '')
    rpdf.cell(12.9, 1, 'Nome')
    rpdf.cell(4.7, 1, 'Atraso', 0, 1)
    rpdf.set_font('Roboto', '', 14)
    tempx = 6
    for idx, x in enumerate(lista):
        rpdf.cell(0.5, 0.6, '')
        tempstr = str(x[0])
        rpdf.cell(0.5, 0.6, tempstr, 0, 0, 'R')
        rpdf.cell(1.5, 0.6, '')
        tempstr = str(x[1])
        rpdf.cell(13.8, 0.6, tempstr)
        tempstr = str(x[2])
        rpdf.cell(5, 0.6, tempstr, 0, 1)
        # tempx = tempx + 0.6
        # rpdf.line(1, tempx, 20, tempx)
        # if tempx == 27.00000000000002:
        #     rpdf.cell(0, 10, 'Página %s' % rpdf.page_no(), 0, 0, 'C')
        #     tempx = -0.25
        # print(x[0], 'tempx ', tempx)
    # rpdf.cell(19, 10, 'Hello World!', 1)
    # rpdf.cell(40, 10, 'Hello World!', 1)
    # rpdf.cell(60, 10, 'Powered by FPDF.', 0, 1, 'C')
    # rpdf.output(arq_recibo, 'F')
    rpdf.output(arq_lista)


def gera_relatorio_pdf(mes, ano, valortotal, templist):
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
    tempstr = 'Relatório de recebimento do mês de ' + mes + ' de ' + ano
    relpdf.line(1, 4.5, 20, 4.5)
    relpdf.cell(0, 0.6, tempstr, 0, 2, 'C')
    relpdf.cell(0, 2, '', 0, 2, 'C')
    relpdf.cell(1.4, 0.6, str(''), 0, 0, 'L')
    relpdf.cell(3.8, 0.6, str('Data do pagto.'), 0, 0, 'L')
    relpdf.cell(11.7, 0.6, str('Nome'), 0, 0, 'L')
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
        relpdf.cell(10, 0.6, str(tempstr), 0, 0, 'L')
        #        tempstr = templist[i][2]
        #        relpdf.cell(2, 0.6, str(tempstr), 0, 0, 'L')
        tempstr = templist[i][3]
        relpdf.cell(3, 0.6, str(tempstr), 0, 1, 'R')
        #        tempstr = templist[i][4]
        #        relpdf.cell(1, 0.6, str(tempstr), 0, 1, 'L')
        i = i + 1
    relpdf.cell(0, 0.6, '', 0, 2, 'C')
    relpdf.line(relpdf.get_x(), relpdf.get_y(), 20, relpdf.get_y())
    tempstr = 'Valor total recebido: ' + valortotal
    relpdf.cell(11.8, 0.6, str(''), 0, 0, 'L')
    relpdf.cell(0, 0.6, str(tempstr), 0, 2, 'L')
    # relpdf.output(arq_relatorio, 'F')
    relpdf.output(arq_relatorio)


produtos_venda = [
    ('07/05/2022', 'Chocolate negro', 'R$ 50,00'),
    ('08/06/2022', 'Chocolate branco', 'R$ 50,00')
]

# gera_lista_dividas(produtos_venda, '07/2022')
# recibo_vendas_pdf('Fulano', 'R$ 100,00', '08/07/2022', produtos_venda, 'Andréia')
# os.system('\"' + pdfviewer + '\" ' + arq_lista)
