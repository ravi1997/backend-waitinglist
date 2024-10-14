from flask import Blueprint

short_bp = Blueprint('short', __name__)

from . import routes
