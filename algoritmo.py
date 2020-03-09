from pedido import prazo_pedido, quantidade_pedido, posicao_pedido
from func_custo import depositos_prox
from functions_database import get_stock_per_drink, get_stock_per_clusters, total_estoque
from cluster import clusters
import pandas as pd

"""
Legenda:
- prazo_pedido: Data que o cliente pediu como prazo
- quantidade_pedido: Dataframe com index sendo a bebida e uma coluna sendo a quantidade referente a cada bebida
- posicao_pedido: longitude e latitude do cliente

- depositos_prox: Dataframe com id de cada deposito mais proximos(menos custosos) ao pedido, 
                  além do custo e tempo para chegar relativo a cada depósito. Consideramos que todos os
                  depositos presentes nesse DataFrame fazem entrega em D+0


- get_stock_per_drink(id): Retorna o DataFrame com o número de cada bebida presente no estoque do cdd baseado no id
- get_stock_per_clusters(id): Retorna o DataFrame com o número de cada cluster presente no estoque do cdd baseado no id

"""

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
    
    for cluster, row in cluster_command.iterrows():
        total = clusters[clusters['cluster'] == cluster].sum()
        clusters_command[cluster] = total

    return clusters_command

def existe_estoque(depositos_prox, clusters_command, quantidade_pedido):
    """    
    Função que consulta o estoque dos armazens mais proximos e retorna a condição do estoque:
    1) infull = tem estoque para exatamento o que o cliente pediu
    2) partial = tem estoque parcial, ou seja, existem bebidas suficiente para o mesmo cluster, mas não
        exatamente o que o cliente pediu
    3) none = não há estoque suficiente para o pedido
    
    :param deposito_fav: dataframe com dados sobre quantidade presente para cada bebida e para cada cluster no
                       deposito mais próximo ao cliente
    :param clusters_command: DataFrame com cluster e quantidade desses clusters no pedido
    :param quantidade_pedido: DataFrame com marca e quantidade das bebidas pedidas
    :return: depositos_prox: DataFrame de depositos favoritos atualizado com coluna sobre sua condição
    """

    #Criação de DataFrame para monitorar se há ou não estoque suficiente de cada bebida por depósito
    df_bebidas = pd.DataFrame([depositos_prox['ids'], depositos_prox['custo_frete']], columns=['ids','custo_frete']) 
    df_bebidas.set_index('id', inplace=True)

    #Criação de DataFrame para monitorar se há ou não estoque suficiente de cada cluster por depósito
    df_clusters = pd.DataFrame([depositos_prox['ids'], depositos_prox['custo_frete']], columns=['ids','custo_frete']) 
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
    
    for id, row in depositos_prox.iterrows():
        if df_bebidas.loc[id, 'estoque'] == 'sim':
            depositos_prox[id,'condition'] = 'infull'
        
        elif df_clusters.loc[id, 'estoque'] == 'sim':
            depositos_prox[id,'condition'] = 'partial'
        
        else:
            depositos_prox = 'none'
    
    return depositos_prox

def combine_stocks(ranking_depositos, quantidade_pedidos):
    """    
    Função que verifica se os dois maiores depósitos combinados tem estoque suficiente para atender ao pedido
    :param ranking_depositos: DataFrame de depósitos baseado no estoque presente
    :param quantidade_pedido: DataFrame com marca e quantidade das bebidas pedidas
    :return: condition: Flag com True ou False baseado na existência ou não de depósito suficiente 
    """
    id_1 = ranking_depositos.iloc[0,"id"]
    id_2 = ranking_depositos.iloc[1,"id"]
    stock_1 = get_stock_per_drink(id_1) #DataFrame com estoque de bebidas do maior deposito
    stock_2 = get_stock_per_drink(id_2) #DataFrame com estoque de bebidas do segundo maior deposito

    condition = true

    for bebida,row in quantidade_pedido.iterrows():
        if row['n_pedido'] > stock_1.loc[bebida, "quantidade"] + stock_2.loc[bebida, "quantidade"]:
            condition = false
            break
    
    #Verificação para saber se o tempo de entrega combinado é menor do que 1 dia(tempo em minutos)
    if depositos_prox[id_1, "tempo_de_entrega"] + depositos_prox[id_2, "tempo_de_entrega"] > 1440:
        condition = False

    return condition


if __name__ == "__main__":
    #Calculo dos clusters presentes no pedido 
    clusters_command = cluster_pedido(clusters, quantidade_pedido)

    #Estabelecimento do limite de preço para conseguirmos entregar ou não no dia D
    preco_total = quantidade_pedido['preco'].sum()

    #DataFrame que rankeia depositos baseado no total de estoque presente
    ranking_depositos = pd.DataFrame(colums={"id", "n_estoque"})
    for id in depositos_prox["id"]:
        ranking_depositos = ranking_depositos.append[{"id":id, "n_estoque":total_estoque(id)}, ignore_index=True] 
    ranking_depositos.sort_values(by=["n_estoque"], inplace=True)


    #Acrescentada condição de cada deposito: 'infull', 'partial' ou 'none'
    depositos_prox = existe_estoque(depositos_prox, clusters_command, quantidade_pedido)

    #DataFrame reorganizado para ter uma ordem baseado no tempo de cada deposito para o cliente
    depositos_prox.sort_values(by=['tempo_entrega'], axis=1, inplace=True)

    if not depositos_prox[depositos_prox['condition'] == "infull"].empty:
        print("Entregaremos seu pedido em algumas horas")
    
    elif not depositos_prox[depositos_prox['condition'] == "partial"].empty:
        condition = combine_stocks(ranking_depositos, quantidade_pedido)
        if condition:
            print("Temos 2 opções para você: Uma misturamos as bebidas e entregamos hj e outra nao misturamos e \
                entregamos amanhã")
        else:
            print("Podemos misturar as opções?")
    else :
        print("Entregaremos apenas amanhã, mas temos um desconto especial para você")
