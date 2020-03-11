import pdb
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from sqlalchemy.sql import func
from server import app, db
from application.models import Contato, Role, User

if __name__ == "__main__":
    df = pd.read_excel('Contatos.xlsx')
    for index, row in df.iterrows():
        contato = Contato()
        contato.nome = row['Nome']
        contato.tipo = row['Tipo']
        contato.local = row['Pais/Cidade']
        contato.expediente = row['Expediente']
        contato.endereco = row['Endereço']
        contato.contato = row['Contato']
        contato.email = row['Email']
        contato.obs = row['OBS']
        contato.topologia = row['Topologia']
        contato.save()

uso = Role(nome="admin")
uso2 = Role(nome="comum")
uso.save()
uso2.save()