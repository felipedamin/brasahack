from pedido import prazo, quantidade_pedido, posicao_pedido
from func_custo import custo_frete, tempo_frete
from database import precos_bebidas, depositos
from cluster import clusters
import pandas as pd

def threshold(quantidade_pedido, dic_precos):
    """
    Função para cálculo do threshold máximo que nos permita entregar a encomenda no dia D
    Estabelecemos como threshold o valor de 60% do total do pedido

    :param quantidade_pedido: dicionário com a quantidade de cada tipo de bebida da comanda
    :param dic_preco: dicionário com o preço de cada tipo de bebida do portfólio
    :return: threshold
    """

    for tipo, quant in quantidade_pedido.items():
        preco = dic_precos[tipo]
        receita += preco*quant
    
    threshold = 0,6*receita
    return threshold


# Supondo clusters como, por exemplo, {bronze:[skol, brahma, antartica], prata:[bud, original, stella],
#                                       ouro:[colorado, corona, leffe]}
def cluster_pedido(clusters, quantidade_pedido):
    """    
    Função para a separação das bebidas comandadas em clusters

    :param clusters: dicionário de clusters de bebidas da Ambev
    :param quantidade_pedido: dicionário com tipo e quantidade de cada bebida da comanda
    :return: clusters_command: dicionário com o nome do cluster e a quantidade de bebidas presentes do pedido
    """
    clusters_command = {}

    for cluster in clusters.keys:
        clusters_command[cluster] = 0
    
    for bebida, quant in quantidade_pedido.items():
        for cluster, marcas in clusters.items():
            if bebida in marcas:
                clusters_command[cluster] += quant
                break

    return clusters_command

def depositos_proximos(posicao_pedido, depositos):
     """    
    Função que devolve armazens mais próximos ao local do pedido feito

    :param posicao_pedido: localização do cliente que fez o pedido
    :param armazens: database de todos os cdds da empresa
    :return: depositos_prox
    """

    return posicao_pedido

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
    depositos_prox = depositos_prox(posicao_pedido, depositos)
    
    #Considerando que elegemos um depósito favorito
    deposito_fav = favorite_deposito(depositos_prox)

    condition = existe_estoque(deposito_fav, clusters_command, quantidade_pedido)

    if threshold > custo_frete and condition =='infull':
        print("Entregaremos seu pedido em algumas horas")
    
    elif threshold > custo_frete and condition =='partial':
        print("Temos 2 opções para você")
    
    elif threshold < custo_frete or condition =='none':
        print("Entregaremos apenas amanhã, mas temos um desconto especial para você")
