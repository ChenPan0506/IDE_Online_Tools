from flask import Blueprint

main = Blueprint('main', __name__, url_prefix='/main')

from ide_online_tools import views
