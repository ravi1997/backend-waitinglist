from flask import Blueprint

adminSuperAdmin_bp = Blueprint('adminSuperAdmin', __name__)

from . import routes
