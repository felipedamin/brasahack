import createMap
#matrix, positions = createMap.main()
import functions_database as fdb
import numpy as np

class deliveries:
    def __init__(self):
        self.cdds = fdb.get_cdds()
        self.positions = [self.cdds["lat"], self.cdds["lon"]]
        self.delivery = {}

    '''
    Recebe um pedido:
        (lat, lon)
    deve retornar:
        DataFrame com [id_deposito, custo_entrega, tempo_entrega]
    '''

    def getDelivery(self):
        return self.delivery

    def addDelivery(self, time, price, origin, lat, lon):
        self.delivery[time] = { 'price': price, 'origin': origin, 'latDestination': lat, 'lonDestination': lon }
        return True

    def updateDelivery(self, time, price, origin, lat, lon):
        self.delivery[time] = [self.delivery[time], { 'price': price, 'origin': origin, 'latDestination': lat, 'lonDestination': lon }]
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
        self.cdds = self.cdds.assign(coeficiente=10)

        ## TODO
        # analiso as entregas ja agendadas buscando alternativas mais baratas.
        print(self.delivery)
        # motivo: economizar caminhao e mao de obra
        # caso divide: coef=5; caso contrario, coef=10

        price = self.calculateFrete(n)
        return price

    def calculateFrete(self, n):
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
    bestDelivery2 = deliv.calculateDistances(-23.65, -46.65, 3)
    deliv.updateDelivery('10am', bestDelivery2.head(1)['price'].to_string(index=False), bestDelivery2.head(1)['name'].to_string(index=False), -23.65, -46.65)

    print(deliv.delivery)