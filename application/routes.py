from sqlalchemy.ext.declarative import as_declarative
from flask import render_template, redirect, request, url_for, jsonify, Response
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.sql import func, update
from server import app
import random
from application.models import *
from datetime import timedelta, datetime
from application.rbac import role_required
from htmlmin.main import minify


import datetime
import psycopg2
from config import HOST, \
                DATABASE, \
                PASSWORD, \
                USER
conn = psycopg2.connect(host=HOST,database=DATABASE, user=USER, password=PASSWORD)
cursor = conn.cursor()


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


@app.route('/insert')
def home():
    order  = { 'customer_id': 1, 'bebida': { '1': 100,'2': 300, '3': 50, '4': 100, '5': 10, '6': 0, '7': 0,  '8': 10, '9': 20, '10': 30, '11': 0, '12': 0, '13': 0, '14': 0, '15': 0}}
    # [HOT FIX] Generating order_id from time
    now = datetime.datetime.now()
    order_id = int(f'{now.day}{now.hour}{now.minute}{now.second}')
    for drink_id, quantity in order['bebida'].items():
        if quantity > 0:
            query_insert = "insert into orders(customer_id, order_id, quantity, drink_id) values (%s, %s, %s, %s)"
            cursor.execute(query_insert, (order['customer_id'], order_id, quantity, drink_id))
            conn.commit()
    return render_template('home.html', value = 'animal')


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

@app.route('/cadastro/', methods=['GET', 'POST'])
def cadastro_pedido():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        return 'Ainda nao ta feito'
