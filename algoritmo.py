#from pedido import prazo_pedido, quantidade_pedido, posicao_pedido
#from func_custo import depositos_prox
from functions_database import get_stock_per_drink, get_stock_per_cluster, get_stock_total, get_clusters, get_drinks_price
#from cluster import clusters
import pandas as pd
import pdb
from calculateDistances import deliveries

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
def order_cluster(clusters, order):
    """
    Função para a separação das bebidas comandadas em clusters

    :param clusters: DataFrame de clusters de bebidas da Ambev
    :param quantidade_pedido: DataFrame com tipo e quantidade de cada bebida da comanda
    :return: clusters_command: DataFrame com o nome do cluster e a quantidade de bebidas presentes do pedido
    """
    drinks_price = get_drinks_price()
    drinks_price.set_index("name", inplace=True)

    for cluster,row in clusters.iterrows():
        names = clusters.loc[cluster,"name"]
        order.loc[order.index.isin(names),"cluster"] = cluster

    for drink, row in drinks_price.iterrows():
        if drink in order.index:
            order.loc[drink,"price"] = drinks_price.loc[drink,"price"]

    order["cluster"] = order["cluster"].astype(int)
    clusters_command = order.groupby("cluster").agg('sum')

    return order,clusters_command

def exist_stock(depo_close, clusters_command, order):
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


    for id,row_depo in depo_close.iterrows():
        stock_drinks = get_stock_per_drink(id)
        stock_drinks.set_index(["drink_name"], inplace=True)
        stock_clusters = get_stock_per_cluster(id)
        stock_clusters.set_index(["cluster"], inplace=True)

        depo_close.loc[id, "condition"] = "infull"
        for drink, row_order in order.iterrows():
            if row_order["quantity"] > stock_drinks.loc[drink, 'quantity']:
                depo_close.loc[id, "condition"] = "partial"
                break
        for cluster,row_order in clusters_command.iterrows():
            if row_order["quantity"] > stock_clusters.loc[cluster,"quantity"]:
                depo_close.loc[id, "condition"] = "none"
                break
    return depo_close

def combine_depo(depo_ranking, order):
    """
    Função que verifica se os dois maiores depósitos combinados tem estoque suficiente para atender ao pedido
    :param ranking_depositos: DataFrame de depósitos baseado no estoque presente
    :param quantidade_pedido: DataFrame com marca e quantidade das bebidas pedidas
    :return: condition: Flag com True ou False baseado na existência ou não de depósito suficiente
    """

    ids = depo_ranking.index

    id_1 = int(ids[0])
    id_2 = int(ids[1])
    stock_1 = get_stock_per_drink(id_1) #DataFrame com estoque de bebidas do maior deposito
    stock_1.set_index("drink_name", inplace=True)
    stock_2 = get_stock_per_drink(id_2) #DataFrame com estoque de bebidas do segundo maior deposito
    stock_2.set_index("drink_name", inplace=True)
    condition = True

    for drink,row in order.iterrows():
        if row['quantity'] > stock_1.loc[drink, "quantity"] + stock_2.loc[drink, "quantity"]:
            condition = False
            break

    freight = depo_ranking.loc[id_1, "price"] + depo_ranking.loc[id_2, "price"]
    return condition, freight


def mix_drinks(id_depo, order):

    stock_drinks = get_stock_per_drink(id_depo)
    stock_drinks.set_index(["drink_name"], inplace=True)
    deliv = {}

    for drink, row in order.iterrows():
        if order.loc[drink, "quantity"] > stock_drinks.loc[drink,"quantity"]:
            basket = stock_drinks.loc[drink,"quantity"]
            stock_drinks.loc[drink,"quantity"] -= basket
            if drink in deliv.keys(): #suficiente
                deliv[drink] += basket
            else:
                deliv[drink] = basket

            cluster_drink = stock_drinks.loc[drink,"cluster"]
            same_cluster = stock_drinks[(stock_drinks["cluster"] == cluster_drink) & (stock_drinks["quantity"] != 0)]
            same_cluster.sort_values(by=["price"], ascending=True, inplace=True)
            #same_cluster.drop(drink, inplace=True)

            for drink_cluster, row_cluster in same_cluster.iterrows():
                if basket + stock_drinks.loc[drink_cluster,"quantity"] >= order.loc[drink, "quantity"]:
                    add = order.loc[drink, "quantity"]-basket
                    stock_drinks.loc[drink_cluster,"quantity"] -= add
                    basket = order.loc[drink, "quantity"]

                    if drink_cluster in deliv.keys(): #suficiente
                        deliv[drink_cluster] += add
                    else:
                        deliv[drink_cluster] = add
                    break

                else:
                    add = stock_drinks.loc[drink_cluster,"quantity"]
                    stock_drinks.loc[drink_cluster,"quantity"] -= add # =0
                    basket += add

                    if drink_cluster in deliv.keys(): #n_suficiente
                        deliv[drink_cluster] += add
                    else:
                        deliv[drink_cluster] = add

        else:

            if drink in deliv.keys():
                deliv[drink]  += order.loc[drink, "quantity"]
                stock_drinks.loc[drink,"quantity"] -= order.loc[drink, "quantity"]
            else:
                deliv[drink] = order.loc[drink, "quantity"]
                stock_drinks.loc[drink,"quantity"] -= order.loc[drink, "quantity"]

    return deliv


def bussola(order): #lat e lon
    deliv = deliveries()
    depo_close = deliv.calculateDistances(-23.6, -46.6, 3)
    depo_close.set_index(["id"], inplace=True)

    # Calculo dos clusters presentes no pedido
    clusters = get_clusters()
    order,clusters_command = order_cluster(clusters, order)

    # DataFrame que rankeia depositos baseado no total de estoque presente
    for id in depo_close.index:
        depo_close.loc[id,"nb_stock"] = get_stock_total(id)
    depo_close["nb_stock"] = depo_close["nb_stock"].astype(int)
    depo_close.sort_values(by=["nb_stock"], inplace=True, ascending=False, ignore_index=False)

    # Acrescentada condição de cada deposito: 'infull', 'partial' ou 'none'
    depo_close = exist_stock(depo_close, clusters_command, order)

    # DataFrame reorganizado para ter uma ordem baseado no custo de cada deposito para o cliente
    depo_close.sort_values(by=['price'], axis=0, inplace=True)
    
    # DataFrame que reune os drinks e seus preços correspondentes
    drinks_price = get_drinks_price()
    drinks_price.set_index("name", inplace=True)


    if not depo_close[depo_close['condition'] == "infull"].empty:
        #DataFrame com depositos que podem fazer entrega infull em D+0
        depo_full = depo_close[depo_close["condition"] == "infull"]
        
        #Id do deposito de entrega mais barata entre os "infulls"
        id_cheap_full = int(depo_full.index[0])
        
        #A entrega do deposito infull é a mesma do pedido 
        deliv_full = order["quantity"].to_dict()
        deliv_full = {key: int(value) for key,value in deliv_full.items()}
        
        #Calculo do preço sem frete
        price = 0
        for drink, row in drinks_price.iterrows():
            if drink in deliv_full.keys():
                price += row["price"]*deliv_full[drink]

        #Calculo do preço com frete
        price_total = price+depo_full.loc[id_cheap_full, "price"]
        price_total = float(price_total)
        result = {
                    "total1": round(price_total,2),
                    "entrega1":"Hoje",
                    "pedido1": deliv_full,
                }
        
        #Considerando caso 2 caso haja tambem algum deposito com condição "partial"
        depo_pos = depo_close[depo_close["condition"] != "none"]
        id_cheap_part = int(depo_pos.index[0])
        
        if depo_pos.loc[id_cheap_part,'condition'] == "partial":     
            #Calculo das bebidas misturadas
            deliv_mix = mix_drinks(id_cheap_part, order)
            deliv_mix = {key:int(value) for key,value in deliv_mix.items()}
            
            price = 0
            for drink, row in drinks_price.iterrows():
                if drink in deliv_mix.keys():
                    price += row["price"]*deliv_mix[drink]

            price_total_mix = price+depo_pos.loc[id_cheap_part, "price"]
            price_total_mix = float(price_total_mix)
            
            #Resultado que contempla as duas opções
            result2 = {
                "total2": round(price_total_mix,2),
                "entrega2":"Hoje",
                "pedido2": deliv_mix,
            }
            result.update(result2)

        return result

    #Caso em que não há possibilidade de entrega infull por apenas um deposito
    elif not depo_close[depo_close['condition'] == "partial"].empty:
        depo_partial = depo_close[depo_close["condition"] == "partial"]
        id_cheap_part = int(depo_partial.index[0])
        deliv_mix = mix_drinks(id_cheap_part, order)
        deliv_mix = {key:int(value) for key,value in deliv_mix.items()}
        
        price = 0
        for drink, row in drinks_price.iterrows():
            if drink in deliv_mix.keys():
                price += row["price"]*deliv_mix[drink]
        price_total = price+depo_partial.loc[id_cheap_part, "price"]
        price_total = float(price_total)
        result = {
            "total1": round(price_total,2),
            "entrega1":"Hoje",
            "pedido1": deliv_mix,
        }

        #Verificação se é também possível combinar os depósitos para uma entrega infull
        combine,freight = combine_depo(depo_close, order)
        #Se for possível combinar os depósitos, devemos adicionar essa possibilidade também
        if combine:
            deliv_combine = order["quantity"].to_dict()
            deliv_combine = {key:int(value) for key,value in deliv_combine.items()}

            price = 0
            for drink, row in drinks_price.iterrows():
                if drink in deliv_combine.keys():
                    price += order.loc[drink,"price"]*deliv_combine[drink]

            price_total = price + freight
            price_total = int(price_total)
            result2 = {
                        "total2": round(price_total, 2),
                        "entrega2":"Hoje",
                        "pedido2": deliv_combine,
                    }
            result.update(result2)

            return result

        #Caso em que não é possível combinar os depósitos
        else:
            id_cheapest = int(depo_close.index[0])
        
            deliv_none = order["quantity"].to_dict()
            deliv_none = {key:int(value) for key,value in deliv_none.items()}

            price = 0
            for drink, row in drinks_price.iterrows():
                if drink in deliv_none.keys():
                    price += row["price"]*deliv_none[drink]

            price_total = price+depo_close.loc[id_cheapest, "price"]
            price_total = float(price_total)
            result2 = {
                        "total2": round(price_total,2),
                        "entrega2":"Amanhã",
                        "pedido2": deliv_none,
                    }
            result.update(result2)
            return result

    #Caso em que a entrega será efetuada apenas amanhã. Nesse caso a entrega é infull
    else:
        id_cheap_none = int(depo_close.index[0])
        
        deliv_none = order["quantity"].to_dict()
        deliv_none = {key:int(value) for key,value in deliv_none.items()}

        price = 0
        for drink, row in drinks_price.iterrows():
            if drink in deliv_none.keys():
                price += row["price"]*deliv_none[drink]

        price_total = price+depo_close.loc[id_cheap_none, "price"]
        price_total = float(price_total)
        result = {
                    "total1": round(price_total,2),
                    "entrega1":"Amanhã",
                    "pedido1": deliv_none,
                }
        return result


if __name__ == "__main__":
    order = pd.DataFrame({"drink":['Original', "Budweiser", "Guarana Antarctica",
    "Energetico Fusion Normal", "Energetico Fusion Pessego"], "quantity":[100, 50, 300, 120, 210]})
    order.set_index(["drink"], inplace=True)

    dict_pedido = bussola(order)
    print(dict_pedido)



#Pegar bebidas mais baratas entre as disponíveis
#Colocar preço de produto mais frete no retorno ao cliente
#Precisa popular mais o dataframe pois só tem 4 stocks
#Consertar o "Originial"
