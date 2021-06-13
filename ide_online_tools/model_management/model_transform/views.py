import os
import os.path
import shutil

from flask import current_app, send_from_directory, jsonify
from flask import request
from flask_cors import cross_origin
from flask_socketio import emit
from flask_uploads import UploadSet

from ide_online_tools.model_management import socketio, transformer
from . import m_transform

FILES = tuple('db xlsm'.split())
@m_transform.route('/', methods=['GET'])
def model_transform_test():
    """模型转换模块测试
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### text
        模型转换模块测试
    @@@
    """
    return '模型转换模块测试'


@m_transform.route('/upload', methods=['GET', 'POST'])
@cross_origin()
def upload_transform_files():
    """模型转换文件上传
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
     ```json
         {
          "message": "文件上传成功",
          "status": 200
        }
     ```
    @@@
    """
    file_dir = current_app.config['UPLOADED_FILES_DEST'] + '\\transform-files'
    if request.method == 'POST' and 'file' in request.files:
        if current_app.config['IS_TRANSFORM_RESET']:
            if os.path.exists(file_dir):
                shutil.rmtree(file_dir)
        filename = UploadSet('FILES', extensions=FILES).save(request.files['file'],
                                           name='transform-files/' + request.files["file"].filename)
        print("文件（{0}）已经保存".format(request.files["file"].filename))
        current_app.config['IS_TRANSFORM_RESET'] = False
        return jsonify({'status': 200, 'message': filename + ':已经保存！'}), 200, {"name": "**"}
    return jsonify({'status': 400, 'message': '文件上传失败'}), 400, {"name": "**"}


@socketio.on('startTransform')
def start_transform(data):
    state = transformer.run(data['vehicle_model_id'],
                            data['model_version_code'],
                            data['vehicle_model_name'],
                            vehicle_type_id=data['vehicle_type_id'],
                            vehicle_config_id=data['vehicle_config_id'],
                            create_user=data['create_user'],
                            f_deny=data['f_deny'],
                            transform_type=data['transform_type']
                            )
    if state == 1:
        emit('modelTransformResponse', {'percent': 100, 'message': "模型转换完成"})
    elif state == 0:
        emit('modelTransformResponse', {'percent': 0, 'message': "模型版本号重复"})



@m_transform.route('/startTransform', methods=['HEAD'])
@cross_origin()
def start_integration_mock_http():
    """模型转换过程开始 socket 接口
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### request body
    ```json
        {
            'vehicle_model_id': 'IDM-VC1-01',
            'model_version_code': 'IDM-VC1-00-V01',
            'vehicle_model_name': '第一个Test车辆模型',
            'vehicle_type_id': 'VHT-VH1-01',
            'vehicle_config_id': 'VHC-VH1-01',
            'create_user': 'cpp',
            'f_deny': '0.5',
            'transform_type': 'add',
        }
    ```
    #### request example
    ```javascript
    releaseModel() {
        this.$socket.emit('startTransform', {
                                        'vehicle_model_id': 'IDM-VC1-01',
                                        'model_version_code': 'IDM-VC1-00-V01',
                                        'vehicle_model_name': '第一个Test车辆模型',
                                        'vehicle_type_id': 'VHT-VH1-01',
                                        'vehicle_config_id': 'VHC-VH1-01',
                                        'create_user': 'cpp',
                                        'f_deny': '0.5',
                                        'transform_type': 'add',
                                        })
    }
    ```
    #### return
    - ##### json
     ```json
         {
          "message": "模型转换完成",
          "status": 200
        }
     ```
    @@@
    """
    return jsonify({'status': 200, 'message': "这是一个模拟socket接口:startTransform"}), 200, {"name": "**"}


@m_transform.route('/download/transform_model_info', methods=['GET'])
@cross_origin()
def download_transform_template_files():
    """下载模型转换模板文件
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### attachment file
    @@@
    """
    transform_output_template_dir = current_app.config['UPLOADED_FILES_DEST'] + '/templates/transform'
    return send_from_directory(transform_output_template_dir, 'VHMS_BOM_INFO_TEMPLATE.xlsm', as_attachment=True)
