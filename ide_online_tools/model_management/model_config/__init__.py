from flask import Blueprint

m_config = Blueprint('m_link_config', __name__, url_prefix='/m_config')

from . import views