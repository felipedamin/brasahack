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

def get_order(customer_id, order_id = 1):
    """
    Função para retornar um determinado pedido de um determinado clinte

    :param customer_id: id do cliente
    :return [DataFrame] with columns ['drink_id', 'quantity']
    """
    query_order = "select drink_id, quantity from orders where customer_id = %s and order_id = %s"
    orders = pd.read_sql_query(query_order, conn, params = [customer_id, order_id])
    return orders

def get_cdds(order_city = 'São Paulo'):
    """
    Função para coletar os cdds da cidade em que foi realizada o pedido. Default = São Paulo

    :param order_city: string com o nome da cidade do pedido
    :return [DataFrame] with columns (cdd_id, name, lat, lon)
    """
    query_cdds = "select id, name, lat, lon from cdd where city = %s"
    cdds = pd.read_sql_query(query_cdds, conn, params = [order_city])
    return cdds

def get_drinks_price():
    """
    Função que coleta do banco o preço de cada uma das bebidas

    :param None
    :return [DataFrame] no formato ['drink_id', 'price']

    """
    query_drinks = "select name, price from drinks"
    dic_precos = pd.read_sql_query(query_drinks, conn)
    return dic_precos

def get_clusters():
    """
    Função responsável por retornar as bebidas presentes em cada um dos clusters

    :param None
    :return [DataFrame] no formatio ['cluster', ['bebidas']], Ex: clustert 0, contém bebidas ['Antarctica Originial', 'Bohemia', 'Budweiser', 'Stella Artois', 'Colorado Ribeirão', 'Colorado Appia']
    """
    query_clusters = "select name, cluster from drinks"
    clusters = pd.read_sql_query(query_clusters, conn)
    cluster = clusters.groupby('cluster')['name'].apply(list).reset_index()
    return cluster

def get_stock_total(cdd_id):
    """
    Função por responsável por retornar a quantidade total de bebidas em um determinado stock
    :param None
    :return [int] quantidade total de bebidas no armazém
    """
    query_cdd = "select sum(quantity) as quantity from cdd_stock where cdd_id = %s group by cdd_id"
    df_stock_total = pd.read_sql_query(query_cdd, conn, params = [cdd_id])
    return df_stock_total['quantity'].values[0]


def get_stock_per_drink(cdd_id):
    """
    Função por responsável por retornar a quantidade de cada uma das bebidas em um determinado stock
    :param None
    :return [DataFrame] no formato ['drink_id', 'quantity']
    """
    query_cdd = """select cdd_id, quantity, drink_id, dr.name as drink_name, dr.cluster as cluster, dr.price as price from cdd_stock cdd
                inner join drinks dr on dr.id = cdd.drink_id
                where cdd_id = %s order by drink_id"""
    df_per_drink = pd.read_sql_query(query_cdd, conn, params = [cdd_id])
    return df_per_drink[['drink_id', 'quantity', 'drink_name', 'price','cluster']]

def get_stock_per_cluster(cdd_id):
    """
    Função por responsável por retornar a quantidade de cada uma das bebidas por cluster em um determinado stock
    :param None
    :return [DataFrame] no formato ['cluster', 'quantity']
    """
    query_cdd = """select cdd_id, sum(quantity) as quantity, dr.cluster as cluster from cdd_stock cs
                    inner join drinks dr
                        on cs.drink_id = dr.id
                    where cdd_id = %s
                    group by dr.cluster, cdd_id
                    order by dr.cluster"""
    df_per_cluster = pd.read_sql_query(query_cdd, conn, params = [cdd_id])
    return df_per_cluster[['cluster', 'quantity']]

if __name__=='__main__':
    print(get_stock_per_drink(1))
