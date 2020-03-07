from pedido import prazo_pedido, quantidade_pedido, posicao_pedido
from func_custo import depositos_prox
from funcoes_db import cdds_dispo, cdd_bebidas, preco_total
from cluster import clusters
import pandas as pd

"""
Legenda:
- prazo_pedido: Data que o cliente pediu como prazo
- quantidade_pedido: Dataframe com index sendo a bebida e uma coluna sendo a quantidade referente a cada bebida
- posicao_pedido: longitude e latitude do cliente

- depositos_prox: Dataframe com id de cada deposito mais proximos(menos custosos) ao pedido, 
                  além do custo e tempo para chegar relativo a cada depósito

- cdd_bebidas(id): Retorna o DataFrame com o número de cada bebida presente no estoque do cdd baseado no id
- cdd_clusters(id): Retorna o DataFrame com o número de cada cluster presente no estoque do cdd baseado no id
- preco_total(quantidade_pedido): Retorna o preço total da compra

"""

def threshold(preco_total):
    """
    Função para cálculo do threshold máximo que nos permita entregar a encomenda no dia D
    Estabelecemos como threshold o valor de 60% do total do pedido

    :param preco_total: preco_total do pedido feito pelo cliente
    :return: threshold
    """
    return 0,6*preco_total


# Supondo clusters como, por exemplo, {bronze:[skol, brahma, antartica], prata:[bud, original, stella],
#                                       ouro:[colorado, corona, leffe]}
def cluster_pedido(clusters, quantidade_pedido):
    """    
    Função para a separação das bebidas comandadas em clusters

    :param clusters: DataFrame de clusters de bebidas da Ambev
    :param quantidade_pedido: DataFrame com tipo e quantidade de cada bebida da comanda
    :return: clusters_command: DataFrame com o nome do cluster e a quantidade de bebidas presentes do pedido
    """
    cluster_command = pd.DataFrame(columns=['cluster', 'quantidade']
    clusters_command['cluster'] = clusters['cluster'].unique()
    clusters_command.set_index('cluster', inplace=True)
    
    for cluster,row in cluster_command.iterrows():
        total = clusters[clusters['cluster'] == cluster].sum()
        clusters_command[cluster] = total

    return clusters_command
"""
def depositos_proximos(posicao_pedido, depositos):
     '''    
    Função que devolve armazens mais próximos ao local do pedido feito

    :param posicao_pedido: localização do cliente que fez o pedido
    :param armazens: database de todos os cdds da empresa
    :return: depositos_prox
    '''

    return posicao_pedido
"""
def existe_estoque(deposito, clusters_command, quantidade_pedido):
     """    
    Função que consulta o estoque dos armazens mais proximos e retorna a condição do estoque:
    1) infull = tem estoque para exatamento o que o cliente pediu
    2) partial = tem estoque parcial, ou seja, existem bebidas suficiente para o mesmo cluster, mas não
        exatamente o que o cliente pediu
    3) none = não há estoque suficiente para o pedido
    
    :param deposito: dataframe com dados sobre quantidade presente para cada bebida e para cada cluster no
                       deposito mais próximo ao cliente
    :param clusters_command: clusters de todas bebidas do pedido
    :param quantidade_pedido: dicionário com quantidade e marca das bebidas pedidas
    :return: condition
    """


    #Criação de DataFrame para monitorar a quantidade de pedidos e a presenção ou não de estoque
    df_bebidas = pd.DataFrame.from_dict(quantidade_pedido, orient='index', columns=['n_pedido'])
    
    df_clusters = pd.DataFrame.from_dict(clusters_command, orient='index', columns=['n_pedido'])

    #Gera Dataframe com flag 'sim' ou 'nao' para presença suficiente de cada bebida no estoque
    for bebida,row in df_bebidas.iterrows():
        if row['n_pedido'] < deposito[bebida]:
            df_bebidas.loc[bebida,'estoque'] = 'sim'
        else:
            df_bebidas.loc[bebida,'estoque'] = 'nao'
    
    #Gera Dataframe com flag 'sim' ou 'nao' para presença suficiente de cada cluster no estoque
    for cluster,row in df_clusters.iterrows():
        if row['n_pedido'] < deposito[clusters]:
            df_clusters.loc[cluster,'estoque'] = 'sim'
        else:
            df_clusters.loc[cluster,'estoque'] = 'nao'
    
    if df_bebidas[df_bebidas['estoque'] == 'nao'].empty:
        condition = 'infull'
    elif df_clusters[df_clusters['estoque'] == 'nao'].empty:
        condition = 'partial'
    else:
        condition = 'none'
    
    return 

if __name__ == "__main__":
    #Calculo dos clusters presentes no pedido 
    clusters_command = cluster_pedido(clusters, quantidade_pedido)

    #Estabelecimento do limite para conseguirmos entregar ou não no dia D
    threshold = threshold(quantidade_pedido, precos_bebidas)
    
    
    #Considerando que elegemos um depósito favorito
    deposito_fav = favorite_deposito(depositos_prox)

    condition = existe_estoque(deposito_fav, clusters_command, quantidade_pedido)

    if threshold > custo_frete and condition =='infull':
        print("Entregaremos seu pedido em algumas horas")
    
    elif threshold > custo_frete and condition =='partial':
        print("Temos 2 opções para você")
    
    elif threshold < custo_frete or condition =='none':
        print("Entregaremos apenas amanhã, mas temos um desconto especial para você")
