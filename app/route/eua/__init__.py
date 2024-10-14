from flask import Blueprint

eua_bp = Blueprint('eua', __name__)

from . import routes
