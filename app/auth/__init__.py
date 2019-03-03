from flask import Blueprint

bp = Blueprint('auth', __name__, static_folder='static', static_url_path='/app/static')

from app.auth import routes