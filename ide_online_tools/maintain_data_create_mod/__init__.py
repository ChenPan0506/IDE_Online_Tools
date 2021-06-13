# -*- coding:utf-8 -*-
from werkzeug.utils import import_string


blueprints = [
    'ide_online_tools.maintain_data_create_mod.create_mod:c_mod',
]


def init_cm_module(app):
    # Load Base Configs

    # Load extensions

    # Load blueprints
    for bp_name in blueprints:
        bp = import_string(bp_name)
        app.register_blueprint(bp)
        print("BluePrint: {" + bp_name + "} 已挂载！")

    print("模块:{" + __name__ + "} 已经加载！")