from flask import Blueprint

designation_bp = Blueprint('designation', __name__)

from . import routes
