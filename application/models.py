from datetime import datetime
from server import db


class Base():
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class PessoaFisica(db.Model, Base):
    fcoeficiente = db.Column(db.Text)
    fvalorprest = db.Column(db.Text)
    fprimeirovenc = db.Column(db.Text)
    fcarencia = db.Column(db.Text)
    fobs = db.Column(db.Text)
    created_on = db.Column(db.DateTime, default=datetime.now)


class PessoaJuridica(db.Model, Base):
    jprimeirovenc = db.Column(db.Text)
    jcarencia = db.Column(db.Text)
    jobs = db.Column(db.Text)
    created_on = db.Column(db.DateTime, default=datetime.now)


class Veiculos(db.Model, Base):
    idVeic = db.Column(db.Integer, primary_key=True)
    vtipocli = db.Column(db.Text)
    vestado = db.Column(db.Text)
    created_on = db.Column(db.DateTime, default=datetime.now)




