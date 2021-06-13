from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import import_string

db = SQLAlchemy()

blueprints = [
    'ide_online_tools.model_assist.model_check:m_check',
    'ide_online_tools.model_assist.assist_create_mod:ac_mod',
]


def init_assist_module(app):
    # Load Base Configs
    db.init_app(app)

    # Load extensions

    # Load blueprints
    for bp_name in blueprints:
        bp = import_string(bp_name)
        app.register_blueprint(bp)
        print("BluePrint: {" + bp_name + "} 已挂载！")

    print("模块:{" + __name__ + "} 已经加载！")
