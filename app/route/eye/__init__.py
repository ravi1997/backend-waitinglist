from flask import Blueprint

eye_bp = Blueprint('eye', __name__)

from . import routes
