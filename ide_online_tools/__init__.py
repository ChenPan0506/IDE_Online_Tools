from flask import Flask
from flask_cors import CORS
from flask_docs import ApiDoc
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import import_string

import logging
from logging.handlers import TimedRotatingFileHandler
from ide_online_tools import model_management, maintain_data_create_mod, model_assist

# db = SQLAlchemy()
blueprints = [
    'ide_online_tools.main:main',
]


def create_app(config):
    app = Flask(__name__)

    app.config.from_object(config)

    # Load extensions
    # 通用模块统一通过从文件中导入，在此处进行统一的初始化操作
    # logger.init_app  # 日志模块
    log_init(app)
    # mail.init_app(app)  # 邮件模块
    # db.init_app(app)  # 数据库模块
    # cache.init_app(app)  # 缓存处理模块

    # RESRful-doc 配置
    # 使用 CDN
    # app.config['API_DOC_CDN'] = True
    # 禁用文档页面
    # app.config['API_DOC_ENABLE'] = False
    # 需要显示文档的 Api
    app.config['API_DOC_MEMBER'] = ['m_integration', 'm_transform', 'm_config', 'm_check', 'app', 'main']
    # 需要排除的 RESTful Api 文档
    app.config['RESTFUL_API_DOC_EXCLUDE'] = []
    ApiDoc(app, title='在线工具开发在线接口Api文档', version='0.1')

    # 跨域设置
    CORS(app, resources=r'/*')
    # 功能模块也在此处进行统一的初始化操作
    app.logger.info("根模块:{" + __name__ + "}已经加载！")
    model_management.init_mm_module(app)
    # 模型校核.init_模型校核_module(app)
    model_assist.init_assist_module(app)
    # 自然语言.init_自然语言_module(app)
    maintain_data_create_mod.init_cm_module(app)

    # Load blueprints
    for bp_name in blueprints:
        bp = import_string(bp_name)
        app.register_blueprint(bp)

    return app


def log_init(app):
    formatter = logging.Formatter("[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s")
    handler = TimedRotatingFileHandler("ide_online_tools.log", when="D", interval=1, backupCount=15, encoding="UTF-8",
                                       delay=False, utc=True)
    app.logger.addHandler(handler)
    handler.setFormatter(formatter)

