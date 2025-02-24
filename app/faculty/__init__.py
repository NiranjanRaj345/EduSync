from flask import Blueprint

bp = Blueprint('faculty', __name__)

from . import routes
