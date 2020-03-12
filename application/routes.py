from sqlalchemy.ext.declarative import as_declarative
from flask import render_template, redirect, request, url_for, jsonify, Response, flash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.sql import func, update
from server import app
import random
from application.models import *
from datetime import timedelta, datetime
from application.rbac import role_required
from htmlmin.main import minify


from functions_database import get_drinks_price, get_customer_info
from algoritmo import bussola
import pandas as pd


@app.after_request
def response_minify(response):
    """
    minify html response to decrease site traffic
    """
    if response.content_type == u'text/html; charset=utf-8':
        response.set_data(
            minify(response.get_data(as_text=True))
        )

        return response
    return response


@app.route('/errorPage')
def errorPage():
    return render_template('errorPage.html')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/cadastro-usuario/', methods=['GET', 'POST'])
def cadastro_usuario():
    if request.method == 'GET':
        eu = Customer(name="Bruno", lat=1, lon=1, city="SP", state="SP")
        return render_template('cadastro.html')
    else:
        return 'Ainda nao ta feito'


@app.route('/cadastro-drink/', methods=['GET', 'POST'])
def cadastro_drink():
    if request.method == 'GET':
        drink = Drink(name="Beats", price=5, cluster=1)
        return render_template('cadastro.html')
    else:
        return 'Ainda nao ta feito'

@app.route('/cadastro-pedido/', methods=['GET', 'POST'])
def cadastro_order():
    if request.method == 'GET':
        cust = Customer.query.filter_by(name="Bruno").first()
        drk = Drink.query.filter_by(name="Beats").first()
        order = Order(order_id=1, quantity=1000, customer_id=cust.id, drink_id=drk.id)
        return render_template('cadastro.html')
    else:
        return 'Ainda nao ta feito'

@app.route('/pedido/', methods=['GET', 'POST'])
def pedido():
    # DICIONARIO PARA TESTE


    # dict_bebidas = {
    #     "Antarctica Originial": 3,
    #     "Bohemia": 5.5,
    #     "Budweiser": 6,
    #     "Colorado Appia": 5,
    #     "Colorado Ribeirão": 5,
    #     "Do Bem Integral": 5,
    #     "Do Bem Tangerina": 5,
    #     "Do Bem Goiaba": 5,
    #     "Do Bem Manga": 5,
    #     "Energetico Fusion Pessego": 5,
    #     "Energetico Fusion Limao e Hortela": 5,
    #     "Energetico Fusion Normal": 5,
    #     "Pepsi Zero": 5,
    #     "Pepsi": 5,
    #     "Guarana Antarctica Zero": 5,
    #     "Guarana Antarctica": 5,
    #     "H2OH! Limão": 5,
    #     "Stella Artois": 5,
    #     "Tônica Antarctica": 5
    #     }

    dict_bebidas = get_drinks_price()
    dict_bebidas = dict(zip(dict_bebidas.name, dict_bebidas.price))

    if request.method == 'GET':
        # recebe um df com as bebidas e preços
        return render_template('editar.html', dict_bebidas=dict_bebidas)
    ## FUNÇÕES DE TRATAMENTO
    dict_pedido = request.form.to_dict()
    nome = dict_pedido.pop("nome")
    email = dict_pedido.pop("email")

    # Testing algortimo function

    customer_id = 1 # Setting default customer
    df_customer = get_customer_info(1)
    quantidade_pedido = pd.DataFrame({"bebida":['Antarctica Originial', "Budweiser", "Guarana Antarctica",
    "Energetico Fusion Normal", "Energetico Fusion Pessego"], "quantidade":[100, 50, 300, 120, 210]})
    quantidade_pedido.set_index(["bebida"], inplace=True)
    print(bussola(quantidade_pedido, df_customer['lat'].values[0], df_customer['lon'].values[0]))

    flash("Pedido cadastrado!")
    return render_template('editar.html', dict_bebidas=dict_bebidas)
