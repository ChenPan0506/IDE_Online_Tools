from flask import Blueprint

m_check = Blueprint('m_check', __name__,
                          url_prefix='/model-check')

from . import views
