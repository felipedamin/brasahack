import pandas as pd
import numpy as np
import psycopg2
from config import HOST, \
                DATABASE, \
                PASSWORD, \
                USER

conn = psycopg2.connect(host=HOST,database=DATABASE, user=USER, password=PASSWORD)

"""
Nesse script estão contidas as funções que requerem conexao diretas ao banco de dados

"""


def get_cdds(order_city = 'São Paulo'):
    """
    Função para coletar os cdds da cidade em que foi realizada o pedido. Default = São Paulo

    :param order_city: string com o nome da cidade do pedido
    :return dataframe with columns (cdd_id, name, lat, lon)
    """
    query_cdds = "select id, name, lat, lon from cdd where city = %s"
    cdds = pd.read_sql_query(query_cdds, conn, params = [order_city])
    return cdds

def get_drinks_price():
    """
    Função que coleta do banco o preço de cada uma das bebidas

    :param None
    :return dicionário no formato {'drink_id': price, ...}

    """
    query_drinks = "select name, price from drinks"
    dic_precos = pd.read_sql_query(query_drinks, conn)
    return dict(zip(dic_precos.name, dic_precos.price))

def get_clusters():
    """
    Função responsável por retornar as bebidas presentes em cada um dos clusters

    :param None
    :return dicionário formatio {'cluster': ['Antarctica Originial', 'Bohemia', 'Budweiser', 'Stella Artois', 'Colorado Ribeirão', 'Colorado Appia'],  ...}
    """
    query_clusters = "select name, cluster from drinks"
    clusters = pd.read_sql_query(query_clusters, conn)
    cluster = clusters.groupby('cluster')['name'].apply(list).reset_index()
    return dict(zip(cluster.cluster, cluster.name))

def get_stock_per_drink(cdd_id):
    """
    Função por responsável por retornar a quantidade de cada uma das bebidas em um determinado stock
    :param None
    :return dicionário no formato {'drink_id': 'quantity', ...}
    """
    query_cdd = "select cdd_id, quantity, drink_id from cdd_stock where cdd_id = %s order by drink_id"
    df_per_drink = pd.read_sql_query(query_cdd, conn, params = [cdd_id])
    return dict(zip(df_per_drink.drink_id, df_per_drink.quantity))

def get_stock_per_cluster(cdd_id):
    """
    Função por responsável por retornar a quantidade de cada uma das bebidas por cluster em um determinado stock
    :param None
    :return dicionário no formato {'cluster': 'quantity', ...}
    """
    query_cdd = """select cdd_id, sum(quantity) as quantity, dr.cluster as cluster from cdd_stock cs
                    inner join drinks dr
                        on cs.drink_id = dr.id
                    where cdd_id = %s
                    group by dr.cluster, cdd_id
                    order by dr.cluster"""
    df_per_cluster = pd.read_sql_query(query_cdd, conn, params = [cdd_id])
    return dict(zip(df_per_cluster.cluster, df_per_cluster.quantity))

if __name__ == '__main__':
    print(get_stock_per_drink(1))
