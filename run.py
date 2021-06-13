from ide_online_tools import create_app
from settings import config

app = create_app(config["development"])


@app.route('/')
def index_main():
    return '<h1>IDE_Online_Tools by Flask App</h1>' \
           '<h4><a href="//localhost:8080/model-management/model-integration">模型集成</a></h4><br>' \
           '<h4><a href="//localhost:8080/model-management/model-transform">模型转换/管理</a></h4><br>' \
           '<h4><a href="/docs/api">接口文档</a></h4>'


if __name__ == '__main__':
    # app.run("0.0.0.0", debug=False)  # 部署模式
    # socketio.run(app, host=app.config.get("HOST"), port=app.config.get("SERVER_PORT"), debug=True)  # socketio调试模式
    app.run(host=app.config.get("HOST"), port=app.config.get("SERVER_PORT"), debug=True, threaded=True)  # 调试模式
