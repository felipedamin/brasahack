from datetime import datetime
from server import db


class Base():
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class CDD(db.Model, Base):
    __tablename__ =  'cdd'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    lat = db.Column(db.BigInteger)
    lon = db.Column(db.BigInteger)
    client_type = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    bar = db.Column(db.Boolean)

    def __init__(self, name = None, lat = None, lon=None,
                client_type=None, city=None, state=None, bar=None):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.client_type = client_type
        self.city = city
        self.state = state
        self.bar = bar
        self.save()

    def __repr__(self):
        return f'<CDD {self.name}>'


class CDDStock(db.Model, Base):
    __tablename__ =  'cdd_stock'

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    cdd_id = db.Column(db.Integer, db.ForeignKey('cdd.id'))
    drink_id = db.Column(db.Integer, db.ForeignKey('drink.id'))
    
    drinks = db.relationship('Drink', backref="cdd_stock")
    cdd = db.relationship("CDD", backref="cdd_stocks")


    def __init__(self, quantity = None, cdd_id = None, drink_id = None):
        self.quantity = quantity
        self.cdd_id = cdd_id
        self.drink_id = drink_id
        self.save()

    def __repr__(self):
        return f'<CDDStock {self.cdd.name}>'


class Drink(db.Model, Base):
    __tablename__ =  'drink'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    price = db.Column(db.BigInteger)
    cluster = db.Column(db.Integer)

    def __init__(self, name=None, price=None, cluster=None):
        self.name = name
        self.price = price
        self.cluster = cluster
        self.save()

    def __repr__(self):
        return f'<Drink {self.name}>'


class Order(db.Model, Base):
    __tablename__ =  'order'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    customer_id =  db.Column(db.Integer, db.ForeignKey('customer.id'))
    drink_id = db.Column(db.Integer, db.ForeignKey('drink.id'))
    
    drinks = db.relationship('Drink', backref="orders")

    def __init__(self, order_id=None, quantity=None, customer_id=None, drink_id=None):
        self.order_id = order_id
        self.quantity = quantity
        self.customer_id = customer_id
        self.drink_id = drink_id
        self.save()

    def __repr__(self):
        return f'<Order {self.order_id}>'


class Customer(db.Model, Base):
    __tablename__ =  'customer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    lat = db.Column(db.Text)
    lon = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)

    orders = db.relationship("Order", backref="customer")

    def __init__(self, name=None, lat=None, lon=None, city=None, state=None):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.city = city
        self.state = state
        self.save()

    def __repr__(self):
        return f'<Customer {self.name}>'
