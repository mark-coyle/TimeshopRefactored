from flask import Flask, request, current_app
from flask_mysqldb import MySQL
# from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
# from pymongo import MongoClient

import simplejson as json
import time
import datetime
import re
import sys
import os
from config import Config

mysql = MySQL()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mysql.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.orders import bp as orders_bp
    app.register_blueprint(orders_bp)

    from app.cart import bp as cart_bp
    app.register_blueprint(cart_bp)

    from app.account import bp as account_bp
    app.register_blueprint(account_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.products import bp as products_bp
    app.register_blueprint(products_bp)

    return app
