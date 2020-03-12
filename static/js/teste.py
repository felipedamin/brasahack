import pandas as pd

bebidas = pd.DataFrame({"bebida":['Antarctica', 'Skol', 'Energetico'], "quantidade":[100,200,150]})
bebidas.set_index("bebida", inplace=True)
cluster = ['Antarctica', 'Skol']

bebidas.loc[bebidas.index.isin(cluster), "cluster"] = 0

print(bebidas)