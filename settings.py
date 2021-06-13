from flask_uploads import DOCUMENTS
import os

project_dir_path = os.path.dirname(os.path.abspath(__file__)).replace("\\", '/')


# Flask 项目配置文件
class Config(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'SECRET_KEY#'
    # DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/ide-online-tools-db?charset=UTF8MB4'
    HOST = '10.16.148.27'
    SERVER_PORT = 8084
    REDIS_DB_INDEX = 1
    REDIS_HOST = 'localhost'
    REDIS_PORT = '6379'

    MODEL_FILES_PATH = "C:/PanChen_File/Python_workdir/IDE_Online_Tools/model_files"
    UPLOADED_FILES_DEST = project_dir_path + '/data/model_management_files'
    UPLOADED_FILES_ALLOW = DOCUMENTS
    ROOT_PATH = project_dir_path
    UPLOAD_FOLDER = project_dir_path + r'\data\NLP\user\deal_with\upload'

    IS_INTEGRATION_RESET = True
    IS_TRANSFORM_RESET = True

    TRANSFORM_DATABASE_NAME = 'mysql+pymysql://root:root@localhost:3306/ide-online-tools-db?charset=UTF8MB4'
    T_SOCKET_RESPONSE_TOPIC = "modelTransformResponse"
    I_SOCKET_RESPONSE_TOPIC = "modelIntegrationResponse"

    T_SOCKET_START_ENDPOINT = "startTransform"
    I_SOCKET_START_ENDPOINT = "startIntegration"
    # 下载功能需要绝对路径，统一部署后使用 ROOT_PATH
    MODEL_CHECK_RESULTS_PATH = project_dir_path + r"/data/model_check_results"
    # 用于连接数据的数据库
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3306/ide-all?charset=UTF8MB4"
    # 一个映射绑定 (bind) 键到SQLAlchemy连接URIs的字典。参考：http://www.pythondoc.com/flask-sqlalchemy/binds.html#binds
    # SQLALCHEMY_BINDS = {
    #     'ide-flask-dev': "mysql+pymysql://root:root@localhost:3306/ide-flask?charset=UTF8MB4",
    #     'ide-flask-prod': "mysql+pymysql://root:root@localhost:3306/ide-flask-prod?charset=UTF8MB4",
    # }
    # 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存， 如果不必要的可以禁用它。
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 如果设置成 True，SQLAlchemy 将会记录所有 发到标准输出(stderr)的语句，这对调试很有帮助。
    SQLALCHEMY_ECHO = True
    # 数据库连接池的大小。默认是数据库引擎的默认值 （通常是 5）。
    SQLALCHEMY_POOL_SIZE = 10
    # 指定数据库连接池的超时时间。默认是10。
    SQLALCHEMY_POOL_TIMEOUT = 10
    # 自动回收连接的秒数。这对MySQL 是必须的，默认情况下MySQL会自动移除闲置 8小时或者以上的连接。
    # 需要注意地是如果使用 MySQL 的话， Flask-SQLAlchemy会自动地设置这个值为 2小时。
    SQLALCHEMY_POOL_RECYCLE = 2
    # 控制在连接池达到最大值后可以创建的连接数。当这些额外的连接回收到连接池后将会被断开和抛弃。
    SQLALCHEMY_MAX_OVERFLOW = 10
    # 可以用于显式地禁用或者启用查询记录。查询记录 在调试或者测试模式下自动启用
    SQLALCHEMY_RECORD_QUERIES = True

    API_DOC_MEMBER = ['m_integration', 'm_transform', 'app', 'main', 'm_config', 'c_mod']
    RESTFUL_API_DOC_EXCLUDE = []


# 继承基类的配置类，可以对需求环境进行配置。即，生成环境和测试环境，使用的类不同即可达成效果。
class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


config = {
        'development': DevelopmentConfig,
        'testing': ProductionConfig,
        'production': ProductionConfig,
        'default': DevelopmentConfig
        }
