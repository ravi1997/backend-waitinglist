from flask import Blueprint

priority_bp = Blueprint('priority', __name__)

from . import routes
