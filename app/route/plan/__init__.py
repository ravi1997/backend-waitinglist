from flask import Blueprint

plan_bp = Blueprint('plan', __name__)

from . import routes
