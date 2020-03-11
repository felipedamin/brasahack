import pandas as pd 

def teste1():
    quantidade_pedido = {"skol": 13, "brahma": 18, "stella": 12}

    df_pedido = pd.DataFrame.from_dict(quantidade_pedido, orient='index', columns=['n_pedido'])
    
    for index,row in df_pedido.iterrows():
        print(index)
        if row['n_pedido'] < 10:
            df_pedido.loc[index,'estoque'] = 'sim'
        else:
            df_pedido.loc[index,'estoque'] = 'nao'
    
    if not df_pedido[df_pedido['estoque'] == 'sim'].empty:
        print('sim')
    else:
        print('nao')
    
    return df_pedido

if __name__ == "__main__":
    ranking = pd.DataFrame(columns={"id", "estoque"})
    ids = {"20": 1200,"30": 3600,"40":7200}


    ranking = ranking.append({"id":10, "estoque":20}, ignore_index=True)
    
    print(ranking)

