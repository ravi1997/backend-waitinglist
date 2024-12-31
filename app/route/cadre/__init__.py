from flask import Blueprint

cadre_bp = Blueprint('cadre', __name__)

from . import routes
