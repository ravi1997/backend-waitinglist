from flask import Blueprint

main_bp = Blueprint('main', __name__, static_folder='build/web')

from . import routes