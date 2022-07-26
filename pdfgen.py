from fpdf import FPDF
import os

imagem_peq = os.path.join(os.getcwd(), 'recursos', 'logo_small.png')
pdfviewer = os.path.join(os.getcwd(), 'recursos', 'SumatraPDF.exe')
arq_recibo = 'recibo.pdf'
arq_relatorio = 'relatorio.pdf'


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
