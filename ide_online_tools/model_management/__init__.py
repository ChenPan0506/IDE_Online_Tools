import numpy as np
from flask_marshmallow import Marshmallow
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads
from sqlalchemy import event
from werkzeug.utils import import_string


# socket config
socketio = SocketIO(cors_allowed_origins='*')
db = SQLAlchemy()
ma = Marshmallow()

from ..model_management.tables import *
from ..model_management.tables_schema import *
from ide_online_tools.model_management.utils.transformer import Transformer
transformer = Transformer()

blueprints = [
    'ide_online_tools.model_management.model_integration:m_integration',
    'ide_online_tools.model_management.model_transform:m_transform',
    'ide_online_tools.model_management.model_config:m_config',
]


def add_own_encoders_int(conn, cursor, query, *args):
    cursor.connection.encoders[np.int64] = lambda value, encoders: int(value)


def add_own_encoders_float(conn, cursor, query, *args):
    cursor.connection.encoders[np.float64] = lambda value, encoders: float(value)


def init_mm_module(app):
    # Load Base Configs
    db.init_app(app)
    ma.init_app(app)
    # Load extensions

    # Load Flask-Uploads config
    model_files = UploadSet('FILES')
    configure_uploads(app, model_files)

    transformer.init_transformer(app, db)
    with app.app_context():
        event.listen(db.engine, "before_cursor_execute", add_own_encoders_int)
        event.listen(db.engine, "before_cursor_execute", add_own_encoders_float)

    # transformer.transformer_db.create_all(app=app)
    # socket init app
    socketio.init_app(app)

    @socketio.on('connect')
    def test_connect():
        app.logger.info('Socket Client connected')
        emit('modelIntegrationResponse', {'percent': 0, 'message': "后台连接成功！"})

    @socketio.on('disconnect')
    def test_disconnect():
        app.logger.info('Socket Client disconnected')

    app.logger.info("模块:{" + __name__ + "} 已经加载！")
    # Load blueprints
    for bp_name in blueprints:
        bp = import_string(bp_name)
        app.register_blueprint(bp)
        app.logger.info("BluePrint: {" + bp_name + "} 已挂载！")
