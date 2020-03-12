from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SECRET_KEY'] = b'afde35339a5c24cb22c17703971e865d3765cc37de35e96a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///application/database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
admin = Admin(app, template_mode='bootstrap3')

from application import routes
from application import admin
