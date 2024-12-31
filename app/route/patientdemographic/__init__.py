from flask import Blueprint

patientdemographic_bp = Blueprint('patientdemographic', __name__)

from . import routes
