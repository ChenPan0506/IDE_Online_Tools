from flask import Blueprint

m_transform = Blueprint('m_transform', __name__, url_prefix='/m_transform')

from . import views
