import pandas as pd
import functions_database as fdb
import numpy as np

class deliveries:
    def __init__(self):
        self.cdds = fdb.get_cdds()
        self.positions = [self.cdds["lat"], self.cdds["lon"]]
        self.delivery = {}

    def getDelivery(self):
        return self.delivery

    def addDelivery(self, time, price, origin, lat, lon):
        self.delivery[time] = [{ 'price': price, 'latDestination': lat, 'lonDestination': lon, 'origin': origin }]
        return True
    
    def updateDelivery(self, time, price, origin, lat, lon):
        self.delivery[time].append({ 'price': price, 'origin': origin, 'latDestination': lat, 'lonDestination': lon })
        return True

    ## começa calculando as distancias
    def calculateDistances(self, lat, lon, n):
        degreeToRad = float(np.pi / 180.0)

        # analiso a distancia de todos os cdds e depositos auxiliares.
        deltaLat = (self.cdds['lat'] - lat) * degreeToRad
        deltaLon = (self.cdds['lon'] - lon) * degreeToRad

        aux = np.sin(deltaLat/2)**2 + np.cos(lat*degreeToRad) * np.cos(self.cdds['lat'] * degreeToRad) * (np.sin(deltaLon/2))**2
        c = 2 * np.arctan2(np.sqrt(aux), np.sqrt(1 - aux))

        ## distance in kilometers
        self.cdds = self.cdds.assign(distance=c*6367)
        self.cdds = self.cdds.assign(coeficiente=12)

        # analiso as entregas ja agendadas buscando alternativas mais baratas.
        # motivo: economizar caminhao e mao de obra
        columns = ['name','lat','lon']
        bars = []
        for time in self.delivery.values():
            for bar in time:
                bars.append([bar['origin'], bar['latDestination'], bar['lonDestination']])
        self.bars = pd.DataFrame(bars, columns=columns)
        ## Para nao confundir essa parte do dataframe:
        ## Nesses casos a coluna "origin" representa o depósito de onde estao saindo os produtos
        ## Contudo as colunas 'lat' e 'lon' nao correspondem à latitude e longggitude do depósito,
        ## elas correspondem à latitude e longitude de onde o caminhão irá estar, ou seja
        ## à latitude e longitude do local da entrega anterior
        # analiso a distancia de todos os cdds e depositos auxiliares.
        deltaLat = (self.bars['lat'] - lat) * degreeToRad
        deltaLon = (self.bars['lon'] - lon) * degreeToRad

        aux = np.sin(deltaLat/2)**2 + np.cos(lat*degreeToRad) * np.cos(self.bars['lat'] * degreeToRad) * (np.sin(deltaLon/2))**2
        c = 2 * np.arctan2(np.sqrt(aux), np.sqrt(1 - aux))

        ## distance in kilometers
        self.bars = self.bars.assign(distance=c*6367)
        self.bars = self.bars.assign(coeficiente=6)

        self.cdds = self.cdds.append(self.bars, ignore_index=True)

        price = self.calculateFrete(n)
        return price

    def calculateFrete(self, n):
        # caso divide o caminhao: coef=6; caso contrario, coef=12
        price = round(self.cdds['distance'] * self.cdds['coeficiente'], 2)
        self.cdds = self.cdds.assign(price=price)
        self.cdds.sort_values(by=['price'], inplace=True, ascending=True)

        # devolve a opçao mais barata
        return self.cdds.head(n)

if __name__ == '__main__':
    deliv = deliveries()
    bestDelivery = deliv.calculateDistances(-23.6, -46.6, 3)
    print(bestDelivery)
    print('\n')

    #a opçao aceita é adicionada em "self.delivery[time]"
    deliv.addDelivery('10am', bestDelivery.head(1)['price'].to_string(index=False), bestDelivery.head(1)['name'].to_string(index=False), -23.6, -46.6)
    
    # segunda entrega
    bestDelivery2 = deliv.calculateDistances(-23.61, -46.61, 3)
    deliv.updateDelivery('10am', bestDelivery2.head(1)['price'].to_string(index=False), bestDelivery2.head(1)['name'].to_string(index=False), -23.65, -46.65)
    print(bestDelivery2)
    print('\n')

    print(deliv.delivery)