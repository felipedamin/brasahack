from sqlalchemy.ext.declarative import as_declarative
from flask import render_template, redirect, request, url_for, jsonify, Response
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.sql import func, update
from server import app
import random
from application.models import PessoaFisica, PessoaJuridica, Veiculos
from datetime import timedelta, datetime
from application.rbac import role_required
from htmlmin.main import minify


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
    return render_template('menuPrincipal.html')


@app.route('/cadastro-pedido/', methods=['GET', 'POST'])
def cadastro_pedido():
    if request.method == 'GET':
        return render_template('cadastro.html')
    else:
        return 'Ainda nao ta feito'

