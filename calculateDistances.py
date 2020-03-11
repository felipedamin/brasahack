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

    def addDelivery(self, time, price, lat, lon, origin):
        self.delivery[time] = { 'price': price, 'latDestination': lat, 'lonDestination': lon, 'origin': origin }
        return True

    ## começa calculando as distancias
    def calculateDistances(self, lat, lon):
        degreeToRad = float(np.pi / 180.0)
        deltaLat = (self.cdds['lat'] - lat) * degreeToRad
        deltaLon = (self.cdds['lon'] - lon) * degreeToRad

        
        aux = np.sin(deltaLat/2)**2 + np.cos(lat*degreeToRad) * np.cos(self.cdds['lat'] * degreeToRad) * (np.sin(deltaLon/2))**2
        c = 2 * np.arctan2(np.sqrt(aux), np.sqrt(1 - aux))

        ## distance in kilometers
        self.cdds = self.cdds.assign(distance=c*6367)
        price = self.calculateFrete()
        return price

    def calculateFrete(self):
        price = round(self.cdds['distance'] * 10, 2)
        self.cdds = self.cdds.assign(price=price)

        # devolve a opçao mais barata
        return self.cdds.loc[self.cdds['price'].idxmin()]

def mainTest():
    deliv = deliveries()
    bestDelivery = deliv.calculateDistances(-23.6, -46.6)
    print(bestDelivery)
    print('\n')
    
    ## a opçao aceita é adicionada em "self.delivery[time]"
    deliv.addDelivery('10am', bestDelivery['price'], -23.6, -46.6, bestDelivery['name'])
    deliv.addDelivery('11am', bestDelivery['price'], -23.6, -46.6, bestDelivery['name'])
    deliv.addDelivery('12am', bestDelivery['price'], -23.6, -46.6, bestDelivery['name'])

    print(deliv.delivery)

mainTest()