from flask import Blueprint

anesthesia_bp = Blueprint('anesthesia', __name__)

from . import routes
