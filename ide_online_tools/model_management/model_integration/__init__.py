from flask import Blueprint


m_integration = Blueprint('m_integration', __name__, url_prefix='/m_integration')


from . import views
