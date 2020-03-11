import pdb

from server import db
from application.models import *
from time import sleep


db.create_all()
db.session.commit()
