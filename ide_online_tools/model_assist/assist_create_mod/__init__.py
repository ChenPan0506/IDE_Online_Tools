# -*- coding:utf-8 -*-
from flask import Blueprint

ac_mod = Blueprint('ac_mod', __name__, url_prefix='/assist_create_mod')

from . import base_manage_mod, batch_build_mod, single_build_mod
