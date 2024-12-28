from flask import Blueprint

daycare_bp = Blueprint('daycare', __name__)

from . import routes
