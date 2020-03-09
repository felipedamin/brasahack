from pedido import prazo_pedido, quantidade_pedido, posicao_pedido
from func_custo import depositos_prox
from functions_database import get_stock_per_drink, get_stock_per_clusters
from cluster import clusters
import pandas as pd

"""
Legenda:
- prazo_pedido: Data que o cliente pediu como prazo
- quantidade_pedido: Dataframe com index sendo a bebida e uma coluna sendo a quantidade referente a cada bebida
- posicao_pedido: longitude e latitude do cliente

- depositos_prox: Dataframe com id de cada deposito mais proximos(menos custosos) ao pedido,
                  além do custo e tempo para chegar relativo a cada depósito

- get_stock_per_drink(id): Retorna o DataFrame com o número de cada bebida presente no estoque do cdd baseado no id
- get_stock_per_clusters(id): Retorna o DataFrame com o número de cada cluster presente no estoque do cdd baseado no id


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
    cluster_command = pd.DataFrame(columns=['cluster', 'quantidade'])
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
def existe_estoque(depositos_fav, clusters_command, quantidade_pedido):
    """
    Função que consulta o estoque dos armazens mais proximos e retorna a condição do estoque:
    1) infull = tem estoque para exatamento o que o cliente pediu
    2) partial = tem estoque parcial, ou seja, existem bebidas suficiente para o mesmo cluster, mas não
        exatamente o que o cliente pediu
    3) none = não há estoque suficiente para o pedido

    :param deposito: dataframe com dados sobre quantidade presente para cada bebida e para cada cluster no
                       deposito mais próximo ao cliente
    :param clusters_command: DataFrame com cluster e quantidade desses clusters no pedido
    :param quantidade_pedido: DataFrame com marca e quantidade das bebidas pedidas
    :return: depositos_fav: DataFrame de depositos favoritos atualizado com coluna sobre sua condição
    """

    #Criação de DataFrame para monitorar se há ou não estoque suficiente de cada bebida por depósito
    df_bebidas = pd.DataFrame([depositos_fav['ids'], depositos_fav['custo_frete']], columns=['ids','custo_frete'])
    df_bebidas.set_index('id', inplace=True)

    #Criação de DataFrame para monitorar se há ou não estoque suficiente de cada cluster por depósito
    df_clusters = pd.DataFrame([depositos_fav['ids'], depositos_fav['custo_frete']], columns=['ids','custo_frete'])
    df_clusters.set_index('id', inplace=True)

    #Gera Dataframe com flag 'sim' ou 'nao' para presença suficiente de cada bebida no estoque
    for id,row in df_bebidas.iterrows():
        get_stock_per_drink = get_stock_per_drink(id) #DataFrame com estoque de bebidas naquele deposito
        df_bebidas.loc[id, 'estoque'] = 'sim'

        for bebida,row in quantidade_pedido.iterrows():
            if row['n_pedido'] > get_stock_per_drink.loc[bebida, 'n_estoque']:
                df_bebidas.loc[id,'estoque'] = 'nao'
                break

    for id,row in df_clusters.iterrows():
        get_stock_per_clusters = get_stock_per_clusters(id) #DataFrame com estoque de clusters naquele deposito
        df_clusters.loc[id, 'estoque'] = 'sim'

        for cluster,row in clusters_command.iterrows():
            if row['n_pedido'] > get_stock_per_clusters.loc[cluster, 'n_estoque']:
                df_clusters.loc[id,'estoque'] = 'nao'
                break

    for id, row in depositos_fav.iterrows():
        if df_bebidas.loc[id, 'estoque'] == 'sim':
            depositos_fav[id,'condition'] = 'infull'

        elif df_clusters.loc[id, 'estoque'] == 'sim':
            depositos_fav[id,'condition'] = 'partial'

        else:
            depositos_fav = 'none'

    return depositos_fav

if __name__ == "__main__":
    #Calculo dos clusters presentes no pedido
    clusters_command = cluster_pedido(clusters, quantidade_pedido)

    #Estabelecimento do limite de preço para conseguirmos entregar ou não no dia D
    preco_total = quantidade_pedido['preco'].sum()
    threshold = threshold(preco_total)

    #Filtro de depositos elegíveis -> Se custo_frete < threshold e tempo de entrega pro dia D
    depositos_fav = depositos_prox[depositos_prox['custo_frete'] < threshold]

    #Acrescentada condição de cada deposito: 'infull', 'partial' ou 'none'
    depositos_fav = existe_estoque(depositos_fav, clusters_command, quantidade_pedido)

    #DataFrame reorganizado para ter uma ordem baseado no tempo de cada deposito para o cliente
    depositos_fav.sort_values(by=['tempo_entrega'], axis=1, inplace=True)

    if not depositos_fav[depositos_fav['condition'] == "infull"].empty:
            print("Entregaremos seu pedido em algumas horas")

    elif not depositos_fav[depositos_fav['condition'] == "partial"].empty:

        print("Temos 2 opções para você: Uma misturamos as bebidas e entregamos hj e outra nao misturamos e \
                entregamos amanhã")

    else :
        print("Entregaremos apenas amanhã, mas temos um desconto especial para você")
