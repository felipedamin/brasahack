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


@app.route('/cadastrar-pedido/', methods=['GET', 'POST'])
def cadastro_order():
    if request.method == 'GET':

        return render_template('cadastro.html')
    else:
        return 'Ainda nao ta feito'


@app.route('/pedido/', methods=['GET', 'POST'])
def pedido():
    if request.method == 'GET':
        dict_bebidas = get_drinks_price()
        dict_bebidas = dict(zip(dict_bebidas.name, dict_bebidas.price))
        # recebe um df com as bebidas e preços
        return render_template('cadastrar-pedido.html', dict_bebidas=dict_bebidas)
    
    dict_pedido = request.form.to_dict()
    nome = dict_pedido.pop("nome")
    email = dict_pedido.pop("email")

    # Testing algortimo function

    customer_id = 1 # Setting default customer
    df_customer = get_customer_info(1)
    quantidade_pedido = pd.DataFrame({"bebida":dict_pedido.keys(), "quantidade":dict_pedido.values()})
    quantidade_pedido.set_index(["bebida"], inplace=True)
    print(bussola(quantidade_pedido, df_customer['lat'].values[0], df_customer['lon'].values[0]))

    ## DICT PARA O FRONT
    # dict_pedidos={}
    flash("Pedido cadastrado!")
    return render_template('cadastrar-pedido.html', dict_pedidos=dict_pedidos)
