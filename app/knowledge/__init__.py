from flask import Blueprint

bp = Blueprint('knowledge', __name__)

from app.knowledge import routes