# -*- coding:utf-8 -*-
from flask import Blueprint

c_mod = Blueprint('c_mod', __name__, url_prefix='/create_mod')

from . import views