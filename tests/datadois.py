from dateutil.relativedelta import relativedelta
from time import strftime
from datetime import datetime
x = 0
mesano = []
data_plano_inicio = '10/10/2010'
duracao = 3
data_inicio = datetime.strptime(data_plano_inicio, '%d/%m/%Y')
while x < duracao:
    data_inicio = data_inicio + relativedelta(months=+x)
    messtr = data_inicio.strftime('%m/%Y')
    mesano.append(messtr)
    x = x + 1
print(mesano)

comeca = '02/02/2002'
print(comeca[2:])

diad = 10
data_ultimo = datetime.now() + relativedelta(day=diad)
print(data_ultimo)
data_comeco = datetime.strptime('10/06/2022', '%d/%m/%Y')

meses_delta = data_ultimo - data_comeco
meses = round(meses_delta.days / 30)
print(meses)
datas = []
idx = 0
while idx < meses + 1:
    if idx == 0:
        datas.append(datetime.strftime(data_comeco, '%d/%m/%Y'))
    else:
        datatmp = data_comeco + relativedelta(months=+idx)
        datas.append(datetime.strftime(datatmp, '%d/%m/%Y'))
    idx = idx + 1
print(datas)