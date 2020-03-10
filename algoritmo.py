#from pedido import prazo_pedido, quantidade_pedido, posicao_pedido
#from func_custo import depositos_prox
from functions_database import get_stock_per_drink, get_stock_per_cluster, get_stock_total, get_clusters
#from cluster import clusters
import pandas as pd
import pdb

"""
Legenda:
- prazo_pedido: Data que o cliente pediu como prazo
- quantidade_pedido: Dataframe com index sendo a bebida e uma coluna sendo a quantidade referente a cada bebida
- posicao_pedido: longitude e latitude do cliente

- depositos_prox: Dataframe com id de cada deposito mais proximos(menos custosos) ao pedido, 
                  além do custo e tempo para chegar relativo a cada depósito. Consideramos que todos os
                  depositos presentes nesse DataFrame fazem entrega em D+0



- get_stock_per_drink(id): Retorna o DataFrame com o número de cada bebida presente no estoque do cdd baseado no id
- get_stock_per_cluster(id): Retorna o DataFrame com o número de cada cluster presente no estoque do cdd baseado no id

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
    clusters_command = pd.DataFrame(columns=['cluster', 'quantidade'])
    clusters_command['cluster'] = clusters['cluster'].unique()
    clusters_command.fillna(0, inplace=True)
    clusters_command.set_index('cluster', inplace=True)

    for cluster, row in clusters.iterrows():
        names = clusters.loc[cluster, "name"]
        this_cluster = quantidade_pedido[quantidade_pedido.index.isin(names) == True]
        total = this_cluster["quantidade"].sum()
        clusters_command.loc[cluster, "quantidade"] = total
    
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
    df_bebidas = pd.DataFrame({'id':depositos_prox.index,'custo_frete':depositos_prox['custo_frete']}, columns=['id','custo_frete']) 
    df_bebidas.set_index('id', inplace=True)

    #Criação de DataFrame para monitorar se há ou não estoque suficiente de cada cluster por depósito
    df_clusters = pd.DataFrame({'id':depositos_prox.index, 'custo_frete':depositos_prox['custo_frete']}, 
                                columns=['id','custo_frete']) 
    df_clusters.set_index('id', inplace=True)

    #Gera Dataframe com flag 'sim' ou 'nao' para presença suficiente de cada bebida no estoque
    for id,row in df_bebidas.iterrows():
        stock_drinks = get_stock_per_drink(id) #DataFrame com estoque de bebidas naquele deposito
        stock_drinks.set_index(["drink_name"], inplace=True)
        df_bebidas.loc[id, 'estoque'] = 'sim'

        for bebida,row in quantidade_pedido.iterrows():
            if row['quantidade'] > stock_drinks.loc[bebida, 'quantity']:
                df_bebidas.loc[id,'estoque'] = 'nao'
                break

    for id,row in df_clusters.iterrows():
        stock_clusters = get_stock_per_cluster(id) #DataFrame com estoque de clusters naquele deposito
        stock_clusters.set_index(["cluster"], inplace=True)
        df_clusters.loc[id, 'estoque'] = 'sim'

        for cluster,row in clusters_command.iterrows():
            
            if row['quantidade'] > stock_clusters.loc[cluster, 'quantity']:
                df_clusters.loc[id,'estoque'] = 'nao'
                break

    for id, row in depositos_prox.iterrows():
        if df_bebidas.loc[id, 'estoque'] == 'sim':
            depositos_prox.loc[id,'condition'] = 'infull'
        
        elif df_clusters.loc[id, 'estoque'] == 'sim':
            depositos_prox.loc[id,'condition'] = 'partial'
        
        else:
            depositos_prox.loc[id,'condition'] = 'none'
    return depositos_prox

def combine_stocks(ranking_depositos, quantidade_pedidos):
    """    
    Função que verifica se os dois maiores depósitos combinados tem estoque suficiente para atender ao pedido
    :param ranking_depositos: DataFrame de depósitos baseado no estoque presente
    :param quantidade_pedido: DataFrame com marca e quantidade das bebidas pedidas
    :return: condition: Flag com True ou False baseado na existência ou não de depósito suficiente 
    """
    
    id_1 = ranking_depositos.loc[0,"id"]
    id_2 = ranking_depositos.loc[1,"id"]
    stock_1 = get_stock_per_drink(id_1) #DataFrame com estoque de bebidas do maior deposito
    stock_1.set_index("drink_name", inplace=True)
    stock_2 = get_stock_per_drink(id_2) #DataFrame com estoque de bebidas do segundo maior deposito
    stock_2.set_index("drink_name", inplace=True)

    condition = True

    #pdb.set_trace()
    for bebida,row in quantidade_pedido.iterrows():
        if row['quantidade'] > stock_1.loc[bebida, "quantity"] + stock_2.loc[bebida, "quantity"]:
            condition = False
            break
    
    #Verificação para saber se o tempo de entrega combinado é menor do que 1 dia(tempo em minutos)
    if depositos_prox.loc[id_1, "tempo_entrega"] + depositos_prox.loc[id_2, "tempo_entrega"] > 1440:
        condition = False

    return condition

if __name__ == "__main__":
    quantidade_pedido = pd.DataFrame({"bebida":['Antarctica Originial', "Budweiser", "Guarana Antarctica", 
    "Energetico Fusion Normal", "Energetico Fusion Pessego"], "quantidade":[10, 5, 30, 12, 21]})
    quantidade_pedido.set_index(["bebida"], inplace=True)

    depositos_prox = pd.DataFrame({"id":[1, 2, 3, 4], "custo_frete":[100, 150, 70, 230], 
                                    "tempo_entrega":[10, 15, 7, 23]}) #Se o custo for referente ao tempo 
    depositos_prox.set_index(["id"], inplace=True)
    #depositos_prox.set_index(["id"], inplace=True)
    
    
    #Calculo dos clusters presentes no pedido
    clusters = get_clusters()
    clusters_command = cluster_pedido(clusters, quantidade_pedido)

    #Estabelecimento do limite de preço para conseguirmos entregar ou não no dia D
    #preco_total = quantidade_pedido['preco'].sum()

    #DataFrame que rankeia depositos baseado no total de estoque presente
    ranking_depositos = pd.DataFrame(columns={"id", "n_estoque"})
    for id in depositos_prox.index:
        ranking_depositos = ranking_depositos.append({"id":id, "n_estoque":get_stock_total(id)}, ignore_index=True) 
        
    ranking_depositos.sort_values(by=["n_estoque"], inplace=True, ascending=False, ignore_index=True)

    #Acrescentada condição de cada deposito: 'infull', 'partial' ou 'none'
    depositos_prox = existe_estoque(depositos_prox, clusters_command, quantidade_pedido)
    
    #DataFrame reorganizado para ter uma ordem baseado no tempo de cada deposito para o cliente
    depositos_prox.sort_values(by=['tempo_entrega'], axis=0, inplace=True)

    
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

#Pegar bebidas mais baratas entre as disponíveis
#Colocar preço de produto mais frete no retorno ao cliente
#Precisa popular mais o dataframe pois só tem 4 stocks
#Consertar o "Originial"