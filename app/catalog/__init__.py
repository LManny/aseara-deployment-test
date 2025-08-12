from flask import Blueprint

catalog = Blueprint('catalog', __name__, template_folder='templates')

from . import routes