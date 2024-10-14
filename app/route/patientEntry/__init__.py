from flask import Blueprint

patiententry_bp = Blueprint('patiententry', __name__)

from . import routes
