from flask import redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from server import db, admin
from application.models import *

class AdminView(ModelView):

    def is_accessible(self):
        return 'dev' in current_user.get_roles() if current_user.is_authenticated else False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('denied'))

