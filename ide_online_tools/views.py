from ide_online_tools.main import main


@main.route('/')
def index():
    """主模块测试接口
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |

    #### return
    - ##### html
    ```html
        <h1>IDE_Online_tools主模块测试!</h1>
    ```
    @@@
    """
    return '<h1>IDE_Online_tools主模块测试!</h1>'


@main.route('/ide')
def ide_main():
    """在线工具测试
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### html
    ```html
        <h1>华人运通 EEA 大数据组 在线工具！</h1>
    ```
    @@@
    """
    return '<h1>华人运通 EEA 大数据组 在线工具！</h1>'