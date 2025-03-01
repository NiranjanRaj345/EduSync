from flask import Blueprint

bp = Blueprint('auth', __name__)

from .session_manager import check_active_session
from . import routes

__all__ = ['bp', 'check_active_session']
