import os
import os.path
import pickle
import shutil
import time
import zipfile

import pandas as pd
from flask import current_app, jsonify, request, send_from_directory
from flask_cors import cross_origin
from flask_socketio import emit
from flask_uploads import UploadSet

from ide_online_tools.model_management import socketio
from . import m_integration
from .core.BaseSystem import BaseSystem


@m_integration.route('/upload', methods=['GET', 'POST'])
@cross_origin()
def upload_integration_files():
    """模型集成文件上传
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
    file_dir = current_app.config['UPLOADED_FILES_DEST'] + '\\integration-files'
    if request.method == 'POST' and 'file' in request.files:
        if current_app.config['IS_INTEGRATION_RESET']:
            if os.path.exists(file_dir):
                shutil.rmtree(file_dir)
        filename = UploadSet('FILES').save(request.files['file'],
                                           name='integration-files/' + request.files["file"].filename)
        print("文件（{0}）已经保存".format(request.files["file"].filename))
        current_app.config['IS_INTEGRATION_RESET'] = False
        return jsonify({'status': 200, 'message': filename + ':已经保存！'}), 200, {"name": "**"}
    return jsonify({'status': 400, 'message': '文件上传失败'}), 400, {"name": "**"}


@m_integration.route('/download/model', methods=['GET'])
@cross_origin()
def download_integration_result_file():
    """ 下载模型集成文件
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### attachment file
    @@@
    """
    integration_output_dir = current_app.config['UPLOADED_FILES_DEST'] + '/integration-output'
    # net_list_file = scan_files(integration_output_dir, postfix=".zip")
    return send_from_directory(integration_output_dir, 'integratedModelFile.zip', as_attachment=True)


@m_integration.route('/reset', methods=['POST', 'OPTIONS'])
@cross_origin()
def model_integration_reset():
    """模型集成过程重置
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
     ```json
         {
          "message": "重置成功！",
          "status": 200
        }
     ```
    @@@
    """
    file_dir = current_app.config['UPLOADED_FILES_DEST'] + '/integration-files'
    integration_output_dir = current_app.config['UPLOADED_FILES_DEST'] + '/integration-output'
    transform_input_dir = current_app.config['UPLOADED_FILES_DEST'] + '/transform-input'
    if os.path.exists(file_dir):
        shutil.rmtree(file_dir)
    if os.path.exists(transform_input_dir):
        shutil.rmtree(transform_input_dir)
    if os.path.exists(integration_output_dir):
        shutil.rmtree(integration_output_dir)
    current_app.config['IS_INTEGRATION_RESET'] = True
    return jsonify({'status': 200, 'message': '重置成功！'}), 200, {"name": "**"}


@socketio.on('startIntegration')
@cross_origin()
def start_integration(data):
    file_dir = current_app.config['UPLOADED_FILES_DEST'] + '/integration-files/'
    integration_output_dir = current_app.config['UPLOADED_FILES_DEST'] + '/integration-output'
    transform_input_dir = current_app.config['UPLOADED_FILES_DEST'] + '/transform-input'
    if not os.path.exists(integration_output_dir):
        os.makedirs(integration_output_dir)
    if not os.path.exists(transform_input_dir):
        os.makedirs(transform_input_dir)
    net_list_file = scan_files(file_dir, prefix="Netlist_")
    print(net_list_file)
    if len(net_list_file) > 1:
        emit('modelIntegrationResponse', {'percent': 0, 'message': "上传了多个Netlist文件"})
        return "False"
    elif len(net_list_file) < 1:
        emit('modelIntegrationResponse', {'percent': 0, 'message': "没有上传Netlist文件"})
        return "False"
    else:
        ts = time.time()
        emit('modelIntegrationResponse', {'percent': 0.1, 'message': "开始集成模型"})

        sys = BaseSystem()
        sys.creatsys(file_dir, net_list_file[0])
        sys.Model_data_integration()
        emit('modelIntegrationResponse', {'percent': 35, 'message': "模型合并完成..."})

        writer = pd.ExcelWriter(integration_output_dir + "/ALL-0617-jixie-sys.xlsx",
                                engine='xlsxwriter')
        sys.sysdatatable[0].to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
        writer.save()
        writer.close()

        emit('modelIntegrationResponse', {'percent': 40, 'message': "开始数据去重..."})
        sys.duplicate_sy_merge()

        writer = pd.ExcelWriter(integration_output_dir + "/ALL-0617-merge-sys.xlsx", engine='xlsxwriter')
        sys.sysdatatable[0].to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
        writer.save()
        writer.close()

        emit('modelIntegrationResponse', {'percent': 60.5, 'message': "数据去重完成..."})
        emit('modelIntegrationResponse', {'percent': 62.3, 'message': "新关联开始创建..."})
        sys.data_reasoning()
        emit('modelIntegrationResponse', {'percent': 80, 'message': "新关联创建完成..."})
        net_name = net_list_file[0].split("/")[-1].replace("Netlist_", '')

        # 提取模型中的所有dtc并保存成文件
        sy_dtc_test_zone_data = sys.sysdatatable[0].iloc[0:2,
                                sys.sys_full_cursor["FS"][1] + 1:sys.sys_full_cursor["FO"][1]].T
        sy_dtc_test_zone_data.columns = ["dtc_info", "dtc_description"]
        dtc_zone_data = sy_dtc_test_zone_data[sy_dtc_test_zone_data["dtc_info"].str.contains("DTC_") == True]
        expand_dtc = dtc_zone_data['dtc_info'].str.split('_', 3, expand=True)  # DTC_BMS_P12543 | 电池系统故障
        expand_dtc.columns = ["type", "dtc_node", "dtc"]
        dtc_zone_data = dtc_zone_data.join(expand_dtc)
        # flag = dtc_zone_data.dtc_info.duplicated()
        # if flag.any():
        #     emit('modelIntegrationResponse', {'percent': 82.3, 'message': "dtc有重复项目！"})
        #     return jsonify({'status': 500, 'message': '模型集成出错，有重复dtc！'}), 500, {"name": "**"}
        writer = pd.ExcelWriter(integration_output_dir + "/" + "all_dtcs_in_model_" + net_name, engine='xlsxwriter')
        dtc_zone_data.to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
        writer.save()
        writer.close()

        # 集成输出保存
        writer = pd.ExcelWriter(integration_output_dir + "/" + net_name, engine='xlsxwriter')
        sys.sysdatatable[0].to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
        writer.save()
        writer.close()

        # 转换输入保存
        writer = pd.ExcelWriter(transform_input_dir + "/" + net_name, engine='xlsxwriter')
        sys.sysdatatable[0].to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
        writer.save()
        writer.close()

        net_name = net_name.replace(".xlsx", ".db")

        pickle_string = pickle.dumps(sys)
        fn = integration_output_dir + '/' + net_name
        with open(fn, 'wb') as f:  # open file with write-mode
            f.write(pickle_string)  # serialize and save object

        fn = transform_input_dir + '/' + net_name
        with open(fn, 'wb') as f:  # open file with write-mode
            f.write(pickle_string)  # serialize and save object
        emit('modelIntegrationResponse', {'percent': 90, 'message': "模型保存完成..."})
        te = time.time()
        print("本次运行使用时间: " + str(round(te - ts, 2)) + " s")
        emit('modelIntegrationResponse', {'percent': 98, 'message': "本次模型集成已经完成。"})
        emit('modelIntegrationResponse', {'percent': 98, 'message': "本次模型集成共用时: " + str(round(te - ts, 2)) + "s"})
        zip_dir(integration_output_dir, integration_output_dir+'/integratedModelFile.zip')
        emit('modelIntegrationResponse', {'percent': 100, 'message': "模型文件已经压缩保存，可以点击下载"})
        return jsonify({'status': 200, 'message': '模型集成完成！'}), 200, {"name": "**"}


@m_integration.route('/startIntegration', methods=['HEAD'])
@cross_origin()
def start_integration_mock_http():
    """模型集成过程开始 socket 接口
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
     ```json
         {
          "message": "这是一个模拟socket接口:startIntegration",
          "status": 200
        }
     ```
    @@@
    """
    return jsonify({'status': 200, 'message': "这是一个模拟socket接口:startIntegration"}), 200, {"name": "**"}


def zip_dir(dirname, zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else:
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))
    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        zf.write(tar, arcname)
    zf.close()


def scan_files(directory, prefix=None, postfix=None):
    files_list = []
    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    files_list.append(os.path.join(root, special_file))
            elif prefix:
                if special_file.startswith(prefix):
                    files_list.append(os.path.join(root, special_file))
            else:
                files_list.append(os.path.join(root, special_file))
    return files_list
