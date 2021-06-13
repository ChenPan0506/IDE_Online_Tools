from flask_cors import cross_origin
from flask import jsonify, request
import json
from sqlalchemy import distinct
from . import m_config
from .. import db
from ide_online_tools.model_management.tables import *
from ide_online_tools.model_management.tables_schema import *
from ide_online_tools.model_management.utils.formatter import Formatter


@m_config.route('/')
@cross_origin()
def model_config_test():
    """模型配置模块测试
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### text
    模型配置模块测试
    @@@
    """
    return '模型配置模块测试'


# 模型信息表 CRUD
# 模型信息表整体查询
@m_config.route('/model_info_table', methods=['GET'])
@cross_origin()
def get_model_info_table():
    """查询系统模型表的所有记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
    > [
        {
            "vehicleConfigId": "VHC-VH1-01",
            "tableId": 1,
            "releaseTime": "2020-05-06T18:13:12",
            "importTime": "2020-05-06T18:13:12",
            "vehicleTypeId": "VHT-VH1-01",
            "vehicleModelId": "IDM-VC1-00-V01",
            "versionCode": "IDM-VC1-00-V01",
            "modifyTime": "2020-05-07T09:40:56",
            "createUser": "cp",
            "vehicleModelName": "第一个Test车辆模型"
        },
        {
            "vehicleConfigId": "VHC-VH1-01",
            "tableId": 1,
            "releaseTime": "2020-05-06T18:13:12",
            "importTime": "2020-05-06T18:13:12",
            "vehicleTypeId": "VHT-VH1-01",
            "vehicleModelId": "IDM-VC1-00-V01",
            "versionCode": "IDM-VC1-00-V01",
            "modifyTime": "2020-05-07T09:40:56",
            "createUser": "cp",
            "vehicleModelName": "第一个Test车辆模型"
        },
      ]
    @@@
    """
    vehicle_model_all = TVehicleModel.query.all()
    vehicle_models = TVehicleModelSchema(many=True)
    return Formatter.formatter(vehicle_models.dumps(vehicle_model_all), False)


# 查询模型编号列表
@m_config.route('/vehicle_model_id_list', methods=['GET'])
@cross_origin()
def get_vehicle_model_id_list():
    """查询模型编号列表
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
    >
        [
          "IDM-VC1-00-V01",
          "IDM-VC1-00-V02"
        ]
    @@@
    """
    data = TVehicleModel.query.with_entities(TVehicleModel.vehicle_model_id).distinct().all()
    vehicle_models = TVehicleModelSchema(many=True)
    result = []
    for model_id in vehicle_models.dump(data):
        result.append(model_id["vehicle_model_id"])
    return jsonify(result)

# 查询模型编号是否存在
@m_config.route('/vehicle_model_id_exist/<vehicle_model_id>', methods=['GET'])
@cross_origin()
def check_vehicle_model_id_exist(vehicle_model_id):
    """查询模型编号是否存在
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    vehicle_model_id    |    false    |    string   |    模型ID    |
    #### return
    - ##### json
    >
        {"massage": "模型ID不存在", "data": 0}
    @@@
    """
    data = TVehicleModel.query.filter_by(vehicle_model_id=vehicle_model_id).all()
    if len(data) == 0:
        return jsonify({"massage": "模型ID不存在", "data": 0}), 200, ""
    elif len(data) > 0:
        return jsonify({"massage": "模型ID存在", "data": 1}), 409, ""
    else:
        jsonify({"massage": "内部错误", "data": -1}), 500, ""


# 查询模型编号和模型版本号是否唯一
@m_config.route('/model_version_code_exist/<vehicle_model_id>/<version_code>', methods=['GET'])
@cross_origin()
def check_model_version_code_exist(vehicle_model_id, version_code):
    """查询模型编号和模型版本号是否存在
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    vehicle_model_id    |    false    |    string   |    模型ID    |
    |    version_code    |    false    |    string   |    模型版本号    |
    #### return
    - ##### json
    >
        {"massage": "模型ID和版本号不存在", "data": 0}
    @@@
    """
    data = TVehicleModel.query.filter_by(vehicle_model_id=vehicle_model_id, version_code=version_code).all()
    if len(data) == 0:
        return jsonify({"massage": "模型ID和版本号不存在", "data": 0}), 200, ""
    elif len(data) > 0:
        return jsonify({"massage": "模型ID和版本号存在", "data": 1}), 409, ""
    else:
        jsonify({"massage": "内部错误", "data": -1}), 500, ""


# 查询模型编号列表 with_name
@m_config.route('/vehicle_model_id_list_with_name', methods=['GET'])
@cross_origin()
def get_vehicle_model_id_list_with_name():
    """查询模型编号列表和名称
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
    >[
        {
            "vehicleModelName": "第一个Test车辆模型",
            "vehicleModelId": "VHC-VH1-01"
        },
        {
            "vehicleModelName": "第二22个测试车辆模型",
            "vehicleModelId": "VHC-VH1-01"
        }
    ]
    @@@
    """
    vehicle_model_all = TVehicleModel.query.with_entities(TVehicleModel.vehicle_config_id,
                                                          TVehicleModel.vehicle_model_name).distinct().all()
    vehicle_models = TVehicleModelSchema(many=True)
    return Formatter.formatter(vehicle_models.dumps(vehicle_model_all), False)


# 查询模型版本号列表
@m_config.route('/vehicle_model_version_code_list', methods=['GET'])
@cross_origin()
def get_vehicle_model_version_code_list():
    """查询模型版本号列表
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
    >[
        "IDM-VC1-00-V01"
    ]
    @@@
    """
    data = TVehicleModel.query.with_entities(TVehicleModel.version_code).distinct().all()
    vehicle_models = TVehicleModelSchema(many=True)
    result = []
    for model_id in vehicle_models.dump(data):
        result.append(model_id["version_code"])
    return jsonify(result)


# 根据指定模型编号查询模型
@m_config.route('/vehicle_model_item/<vehicle_model_id>', methods=['GET'])
@cross_origin()
def get_models_item_by_id(vehicle_model_id):
    """根据指定模型编号查询模型
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    vehicle_model_id    |    false    |    String   |    车辆模型ID    |
    #### return
    - ##### json
    >[
        {
            "vehicleConfigId": "VHC-VH1-01",
            "vehicleModelName": "第二22个测试车辆模型",
            "tableId": 2,
            "importTime": "2020-05-09T17:20:06",
            "versionCode": "IDM-VC1-00-V01",
            "vehicleModelId": "IDM-VC1-00-V02",
            "releaseTime": "2020-05-09T17:19:52",
            "vehicleTypeId": "VHT-VH1-01",
            "modifyTime": "2020-06-03T13:10:52",
            "createUser": "cp"
        }
    ]
    @@@
    """
    vehicle_model_all = TVehicleModel.query.filter_by(vehicle_model_id=vehicle_model_id).all()
    vehicle_models = TVehicleModelSchema(many=True)
    return Formatter.formatter(vehicle_models.dumps(vehicle_model_all), False)


# 根据指定模型编号和指定版本查询模型
@m_config.route('/vehicle_model_item/<vehicle_model_id>/<version_code>', methods=['GET'])
@cross_origin()
def get_model_item_by_id_and_code(vehicle_model_id, version_code):
    """根据指定模型编号和版本号查询模型
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    vehicle_model_id    |    false    |    String   |    车辆模型ID    |
    |    version_code    |    false    |    String   |    版本号    |
    #### return
    - ##### json
    >[
        {
            "vehicleConfigId": "VHC-VH1-01",
            "vehicleModelName": "第二22个测试车辆模型",
            "tableId": 2,
            "importTime": "2020-05-09T17:20:06",
            "versionCode": "IDM-VC1-00-V01",
            "vehicleModelId": "IDM-VC1-00-V02",
            "releaseTime": "2020-05-09T17:19:52",
            "vehicleTypeId": "VHT-VH1-01",
            "modifyTime": "2020-06-03T13:10:52",
            "createUser": "cp"
        }
    ]
    @@@
    """
    vehicle_model_all = TVehicleModel.query.filter_by(vehicle_model_id=vehicle_model_id,
                                                      version_code=version_code)
    vehicle_models = TVehicleModelSchema(many=True)
    return Formatter.formatter(vehicle_models.dumps(vehicle_model_all), False)


# 车辆配置信息表 CRUD
# 车辆配置表整体查询
@m_config.route('/vehicle_config_table', methods=['GET'])
@cross_origin()
def get_vehicle_config_table():
    """查询车辆配置表的所有记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
    > [
        {
            "modifyTime": "2020-05-09T16:35:49",
            "vehicleConfigId": "VHC-VH1-01",
            "vehicleTypeIdBelong": "VHT-VH1-01",
            "tableId": 1,
            "vehicleConfigDescription": "快充-长续航",
            "vehicleConfigName": "长续航性能版",
            "createUser": "cp",
            "createTime": "2020-05-06T18:13:12"
        },
        {
            "modifyTime": "2020-05-09T16:34:56",
            "vehicleConfigId": "VHC-VH1-02",
            "vehicleTypeIdBelong": "VHT-VH1-01",
            "tableId": 2,
            "vehicleConfigDescription": "四驱电机",
            "vehicleConfigName": "性能版",
            "createUser": "cp",
            "createTime": "2020-05-09T16:34:56"
        },
        {
            "modifyTime": "2020-05-09T16:36:57",
            "vehicleConfigId": "VHC-VH1-03",
            "vehicleTypeIdBelong": "VHT-VH1-01",
            "tableId": 3,
            "vehicleConfigDescription": "豪华内饰",
            "vehicleConfigName": "尊贵版",
            "createUser": "cp",
            "createTime": "2020-05-09T16:36:57"
        },
        {
            "modifyTime": "2020-05-09T16:38:05",
            "vehicleConfigId": "VHC-VH2-01",
            "vehicleTypeIdBelong": "VHT-VH2-01",
            "tableId": 4,
            "vehicleConfigDescription": "快充-长续航",
            "vehicleConfigName": "长续航性能版",
            "createUser": "cp",
            "createTime": "2020-05-09T16:38:05"
        },
        {
            "modifyTime": "2020-05-09T16:40:05",
            "vehicleConfigId": "VHC -VH2-02",
            "vehicleTypeIdBelong": "VHT-VH2-01",
            "tableId": 5,
            "vehicleConfigDescription": "两驱-单车机屏幕",
            "vehicleConfigName": "青春版",
            "createUser": "cp",
            "createTime": "2020-05-09T16:40:05"
        },
        {
            "modifyTime": "2020-06-03T13:43:36",
            "vehicleConfigId": "VHC-VH3-01",
            "vehicleTypeIdBelong": "VHT-VH3-01",
            "tableId": 6,
            "vehicleConfigDescription": "四驱-快充",
            "vehicleConfigName": "标准版s",
            "createUser": "cp",
            "createTime": "2020-05-09T16:40:51"
        },
        {
            "modifyTime": "2020-06-03T16:40:02",
            "vehicleConfigId": "VHC-VH1-07",
            "vehicleTypeIdBelong": "VHT-VH1-01",
            "tableId": 9,
            "vehicleConfigDescription": "快充-长续航",
            "vehicleConfigName": "长续航性能版",
            "createUser": "大幅度",
            "createTime": "2020-06-03T16:40:02"
        },
        {
            "modifyTime": "2020-06-03T16:50:08",
            "vehicleConfigId": "VHC-VH1-06",
            "vehicleTypeIdBelong": "VHT-VH1-01",
            "tableId": 14,
            "vehicleConfigDescription": "快充-长续航1233",
            "vehicleConfigName": "长续航性能版",
            "createUser": "cpppppp",
            "createTime": "2020-06-03T16:50:08"
        }
    ]
    @@@
    """
    vehicle_config_all = TVehicleConfig.query.all()
    vehicle_configs = TVehicleConfigSchema(many=True)
    return Formatter.formatter(vehicle_configs.dumps(vehicle_config_all), False)


# 车辆配置表ID列表vehicle_config_id查询
@m_config.route('/vehicle_config_id_list', methods=['GET'])
@cross_origin()
def get_vehicle_config_id_list():
    """车辆配置表ID列表查询
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
    > [
          "VHC-VH2-02",
          "VHC-VH1-01",
          "VHC-VH1-02",
          "VHC-VH1-03",
          "VHC-VH1-06",
          "VHC-VH1-07",
          "VHC-VH2-01",
          "VHC-VH3-01"
      ]
    @@@
    """
    data = TVehicleConfig.query.with_entities(TVehicleConfig.vehicle_config_id).distinct().all()
    vehicle_configs = TVehicleConfigSchema(many=True)
    result = []
    for model_id in vehicle_configs.dump(data):
        result.append(model_id["vehicle_config_id"])
    return jsonify(result)


# 查询配置表ID是否存在
@m_config.route('/vehicle_config_id_exist/<vehicle_config_id>', methods=['POST'])
@cross_origin()
def check_vehicle_config_id_exist(vehicle_config_id):
    """查询配置表ID是否存在
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    vehicle_config_id    |    false    |    string   |    车辆配置ID    |
    #### return
    - ##### json
    >
        {"massage": "车辆配置ID不存在", "data": 0}
    @@@
    """
    data = TVehicleConfig.query.filter_by(vehicle_config_id=vehicle_config_id).all()
    if len(data) == 0:
        return jsonify({"massage": "车辆配置ID不存在", "data": 0}), 200, ""
    elif len(data) > 0:
        return jsonify({"massage": "车辆配置ID存在", "data": 1}), 409, ""
    else:
        jsonify({"massage": "内部错误", "data": -1}), 500, ""


# 车辆配置表ID列表 vehicle_config_id 和 vehicle_config_name 查询
@m_config.route('/vehicle_config_id_list_with_name', methods=['GET'])
@cross_origin()
def get_vehicle_config_id_list_with_name():
    """查询车辆配置ID列表和名称
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
    >[
        {
            "vehicleConfigId": "VHC-VH1-01",
            "vehicleConfigName": "长续航性能版"
        },
        {
            "vehicleConfigId": "VHC-VH1-02",
            "vehicleConfigName": "性能版"
        },
        {
            "vehicleConfigId": "VHC-VH1-03",
            "vehicleConfigName": "尊贵版"
        },
        {
            "vehicleConfigId": "VHC-VH2-01",
            "vehicleConfigName": "长续航性能版"
        },
        {
            "vehicleConfigId": "VHC-VH2-02",
            "vehicleConfigName": "青春版"
        },
        {
            "vehicleConfigId": "VHC-VH3-01",
            "vehicleConfigName": "标准版s"
        },
        {
            "vehicleConfigId": "VHC-VH1-07",
            "vehicleConfigName": "长续航性能版"
        },
        {
            "vehicleConfigId": "VHC-VH1-06",
            "vehicleConfigName": "长续航性能版"
        }
    ]
    @@@
    """
    vehicle_config_all = TVehicleConfig.query.with_entities(TVehicleConfig.vehicle_config_id,
                                                            TVehicleConfig.vehicle_config_name).distinct().all()
    vehicle_configs = TVehicleConfigSchema(many=True)
    return Formatter.formatter(vehicle_configs.dumps(vehicle_config_all), False)


# 车辆配置表新增一条记录
@m_config.route('/vehicle_config', methods=['POST'])
@cross_origin()
def add_vehicle_config_item():
    """车辆配置表新增一条记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### request body
    - ##### form data
    ```json
        {
            "vehicleConfigId": "VHC-VH1-06"
            "vehicleConfigName": "长续航性能版"
            "vehicleConfigDescription": "快充-长续航"
            "vehicleTypeIdBelong": "VHT-VH1-01"
            "modifyTime": "这是模型说明"
            "createTime": ""
            "createUser": "的恢复规划"
            "date1": "2020-06-19T16:00:00.000Z"
            'date2': "2020-06-04T04:52:55.000Z"
        }
    ```
    #### return
    - ##### json
    ```
        {
            "message": "增加车辆配置信息成功",
             "status": 200
        }
    ```
    @@@
    """
    try:
        vehicle_config_info = request.form
        vehicle_config_item = TVehicleConfig(
            vehicle_config_id=vehicle_config_info["vehicleConfigId"],
            vehicle_config_name=vehicle_config_info["vehicleConfigName"],
            vehicle_config_description=vehicle_config_info["vehicleConfigDescription"],
            vehicle_type_id_belong=vehicle_config_info["vehicleTypeIdBelong"],
            create_user=vehicle_config_info["createUser"]
        )
        db.session.add(vehicle_config_item)
        db.session.commit()
        return jsonify({'status': 200, 'message': '增加车辆配置信息成功'}), 200, {"name": "**"}
    except BaseException as e:
        return jsonify({'status': 500, 'message': '增加车辆配置信息失败'}), 500, {"name": "**"}


# 车辆配置表删除一条记录
@m_config.route('/vehicle_config/<vehicle_config_id>', methods=['DELETE'])
@cross_origin()
def del_vehicle_config_item(vehicle_config_id):
    """车辆配置表删除一条记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    vehicle_config_id    |    false    |    String   |    删除配置ID    |
    #### return
    - ##### json
    ```
        {
            "message": "删除车辆配置信息成功",
             "status": 200
        }
    ```
    @@@
    """
    try:
        vehicle_config_item = TVehicleConfig.query.filter_by(vehicle_config_id=vehicle_config_id)
        db.session.delete(vehicle_config_item)
        db.session.commit()
        return jsonify({'status': 200, 'message': '删除车辆配置信息成功'}), 200, {"name": "**"}
    except BaseException as e:
        return jsonify({'status': 500, 'message': '删除车辆配置信息失败'}), 500, {"name": "**"}


# 车辆配置表修改一条记录
@m_config.route('/vehicle_config/<vehicle_config_id>', methods=['PUT'])
@cross_origin()
def update_vehicle_config_item(vehicle_config_id):
    """车辆配置表修改一条记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    vehicle_config_id    |    false    |    String   |    修改配置ID    |
    #### request body
    - ##### json
    ```json
        {
            "vehicleConfigId": "VHC-VH1-06"
            "vehicleConfigName": "长续航性能版"
            "vehicleConfigDescription": "快充-长续航"
            "vehicleTypeIdBelong": "VHT-VH1-01"
            "createUser": "用户1"
        }
    ```
    #### return
    - ##### json
    ```
        {
            "message": "修改车辆配置信息成功",
             "status": 200
        }
    ```
    @@@
    """
    try:
        if request.method == 'PUT':
            data = request.get_data()
            json_data = json.loads(data.decode("utf-8"))
            vehicle_config_item = TVehicleConfig.query.filter_by(vehicle_config_id=vehicle_config_id)

            vehicle_config_item.vehicle_config_id = json_data["vehicleConfigId"]
            vehicle_config_item.vehicle_config_name = json_data["vehicleConfigName"]
            vehicle_config_item.vehicle_config_description = json_data["vehicleConfigDescription"]
            vehicle_config_item.vehicle_type_id_belong = json_data["vehicleTypeIdBelong"]
            vehicle_config_item.create_user = json_data["createUser"]
            db.session.commit()

            return jsonify({'status': 200, 'message': '修改车辆配置信息成功'}), 200, {"name": "**"}
    except BaseException as e:
        return jsonify({'status': 500, 'message': '修改车辆配置信息失败'}), 500, {"name": "**"}


# 车辆类型表 CRUD
# 车辆类型表查询
@m_config.route('/vehicle_type_table', methods=['GET'])
@cross_origin()
def get_vehicle_type_table():
    """查询车辆类型表的所有记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
    > [
        {
            "vehicleTypeName": "EV-SUV-2020款",
            "vehicleTypeId": "VHT-VH1-01",
            "createUser": "cp",
            "tableId": 1,
            "vinRe": "LDC131D2010457851",
            "modifyTime": "2020-05-09T16:32:23",
            "brandName": "高合HiPhi1",
            "createTime": "2020-05-06T18:13:12"
        },
        {
            "vehicleTypeName": "EV-Sport-2021款",
            "vehicleTypeId": "VHT-VH2-01",
            "createUser": "cp",
            "tableId": 2,
            "vinRe": "LDC131D2010457852",
            "modifyTime": "2020-05-09T16:32:31",
            "brandName": "高合HiPhi2",
            "createTime": "2020-05-09T16:30:02"
        },
        {
            "vehicleTypeName": "EV-MPV-2020款",
            "vehicleTypeId": "VHT-VH3-01",
            "createUser": "cp",
            "tableId": 3,
            "vinRe": "LDC131D2010457853",
            "modifyTime": "2020-05-09T16:32:45",
            "brandName": "高合HiPhi3",
            "createTime": "2020-05-09T16:31:56"
        }
    ]
    @@@
    """
    vehicle_type_all = TVehicleType.query.all()
    vehicle_types = TVehicleTypeSchema(many=True)
    return Formatter.formatter(vehicle_types.dumps(vehicle_type_all), False)


# 车辆类型表ID列表 vehicle_type_id 查询
@m_config.route('/vehicle_type_id_list', methods=['GET'])
@cross_origin()
def get_vehicle_type_id_list():
    """车辆类型表ID列表查询
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
    > [
        "VHT-VH1-01",
        "VHT-VH2-01",
        "VHT-VH3-01"
      ]
    @@@
    """
    data = TVehicleType.query.with_entities(TVehicleType.vehicle_type_id).distinct().all()
    vehicle_types = TVehicleTypeSchema(many=True)
    result = []
    for model_id in vehicle_types.dump(data):
        result.append(model_id["vehicle_type_id"])
    return jsonify(result)


# 查询车型表ID是否存在
@m_config.route('/vehicle_type_id_exist/<vehicle_type_id>', methods=['POST'])
@cross_origin()
def check_vehicle_type_id_exist(vehicle_type_id):
    """查询车型表ID是否存在
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    vehicle_type_id    |    false    |    string   |    车型ID    |
    #### return
    - ##### json
    >
        {"massage": "车型ID不存在", "data": 0}
    @@@
    """
    data = TVehicleType.query.filter_by(vehicle_type_id=vehicle_type_id).all()
    if len(data) == 0:
        return jsonify({"massage": "车型ID不存在", "data": 0}), 200, ""
    elif len(data) > 0:
        return jsonify({"massage": "车型ID存在", "data": 1}), 409, ""
    else:
        jsonify({"massage": "内部错误", "data": -1}), 500, ""



# 车辆类型表ID列表 vehicle_type_id 和 vehicle_type_name 查询
@m_config.route('/vehicle_type_id_list_with_name', methods=['GET'])
@cross_origin()
def get_vehicle_type_id_list_with_name():
    """查询车辆配置ID列表和名称
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
    >[
        {
            "vehicleTypeId": "VHT-VH1-01",
            "vehicleTypeName": "EV-SUV-2020款"
        },
        {
            "vehicleTypeId": "VHT-VH2-01",
            "vehicleTypeName": "EV-Sport-2021款"
        },
        {
            "vehicleTypeId": "VHT-VH3-01",
            "vehicleTypeName": "EV-MPV-2020款"
        }
    ]
    @@@
    """
    vehicle_type_all = TVehicleType.query.with_entities(TVehicleType.vehicle_type_id,
                                                        TVehicleType.vehicle_type_name).distinct().all()
    vehicle_types = TVehicleTypeSchema(many=True)
    return Formatter.formatter(vehicle_types.dumps(vehicle_type_all), False)


# 车辆类型表新增
@m_config.route('/vehicle_type', methods=['GET', 'POST'])
@cross_origin()
def add_vehicle_type_item():
    """车辆类型表新增一条记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### request body
    - ##### form data
    ```json
        {
            "vehicleTypeId": "VHT-VH1-01"
            "vinRe": "LDC13*******"
            "brandName": "高合HiPhi1"
            "vehicleTypeName": "EV-SUV-2020款"
            "createUser": "用户1"
            "date1": "2020-06-19T16:00:00.000Z"
            'date2': "2020-06-04T04:52:55.000Z"
        }
    ```
    #### return
    - ##### json
    ```
        {
            "message": "增加车辆类型信息成功",
             "status": 200
        }
    ```
    @@@
    """
    try:
        vehicle_type_info = request.form
        vehicle_type_item = TVehicleType(
            vehicle_type_id=vehicle_type_info["vehicleTypeId"],
            vin_re=vehicle_type_info["vinRe"],
            brand_name=vehicle_type_info["brandName"],
            vehicle_type_name=vehicle_type_info["vehicleTypeName"],
            create_user=vehicle_type_info["createUser"]
        )
        db.session.add(vehicle_type_item)
        db.session.commit()
        return jsonify({'status': 200, 'message': '增加车辆类型信息成功'}), 200, {"name": "**"}
    except BaseException as e:
        return jsonify({'status': 500, 'message': '增加车辆类型信息失败'}), 500, {"name": "**"}


# 车辆类型表删除一条记录
@m_config.route('/vehicle_type/<vehicle_type_id>', methods=['DELETE'])
@cross_origin()
def del_vehicle_type_item(vehicle_type_id):
    """车辆类型表删除一条记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    vehicle_type_id    |    false    |    String   |    删除车辆类型ID    |
    #### return
    - ##### json
    ```
        {
            "message": "删除车辆类型信息成功",
             "status": 200
        }
    ```
    @@@
    """
    try:
        vehicle_type_item = TVehicleType.query.filter_by(vehicle_type_id=vehicle_type_id)
        db.session.delete(vehicle_type_item)
        db.session.commit()
        return jsonify({'status': 200, 'message': '删除车辆类型信息成功'}), 200, {"name": "**"}
    except BaseException as e:
        return jsonify({'status': 500, 'message': '删除车辆类型信息失败'}), 500, {"name": "**"}


# 车辆类型表修改一条记录
@m_config.route('/vehicle_type/<vehicle_type_id>', methods=['PUT'])
@cross_origin()
def update_vehicle_type_item(vehicle_type_id):
    """车辆类型表修改一条记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    vehicle_type_id    |    false    |    String   |    修改车辆类型ID    |
    #### request body
    - ##### json
    ```json
        {
            "vehicleTypeId": "VHT-VH1-01"
            "vinRe": "LDC13*******"
            "brandName": "高合HiPhi1"
            "vehicleTypeName": "EV-SUV-2020款"
            "createUser": "用户1"
        }
    ```
    #### return
    - ##### json
    ```
        {
            "message": "修改车辆配置信息成功",
             "status": 200
        }
    ```
    @@@
    """
    try:
        if request.method == 'PUT':
            data = request.get_data()
            json_data = json.loads(data.decode("utf-8"))
            vehicle_type_item = TVehicleType.query.filter_by(vehicle_type_id=vehicle_type_id)
            vehicle_type_item.vehicle_type_id = json_data["vehicleTypeId"],
            vehicle_type_item.vin_re = json_data["vinRe"],
            vehicle_type_item.brand_name = json_data["brandName"],
            vehicle_type_item.vehicle_type_name = json_data["vehicleTypeName"],
            vehicle_type_item.create_user = json_data["createUser"]
            db.session.commit()
            return jsonify({'status': 200, 'message': '修改车辆类型信息成功'}), 200, {"name": "**"}
    except BaseException as e:
        return jsonify({'status': 500, 'message': '修改车辆类型信息失败'}), 500, {"name": "**"}


# 车辆类型配置模型link表 CRUD
# 车辆类型配置模型link表查询
@m_config.route('/vehicle_config_model_link_table', methods=['GET'])
@cross_origin()
def get_vehicle_config_model_link_table():
    """查询车辆类型表的所有记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### return
    - ##### json
    > [
        {
            "operation": "-",
            "tableId": 1,
            "configModelLinkId": "000001",
            "vehicleModelId": "IDM-VC1-00-V01",
            "state": "release",
            "vehicleConfigId": "VHC-VH1-01",
            "description": "第一个车型模型关联",
            "editState": false,
            "alParamId": "ALP-VH1-01",
            "releaseTime": "2020-05-06T18:13:12",
            "createTime": "2020-05-06T18:13:12",
            "vehicleTypeId": "VHT-VH1-01"
        },
        {
            "operation": " -",
            "tableId": 2,
            "configModelLinkId": "000002",
            "vehicleModelId": "IDM-VC1-00-V02",
            "state": "debug",
            "vehicleConfigId": "VHC-VH1-02",
            "description": " 第一个车型模型关联",
            "editState": false,
            "alParamId": "ALP-VH1-03",
            "releaseTime": "2020-05-09T17:22:41",
            "createTime": "2020-05-09T17:23:08",
            "vehicleTypeId": "VHT-VH3-01"
        },
        {
            "operation": " -",
            "tableId": 3,
            "configModelLinkId": "000003",
            "vehicleModelId": "IDM-VC1-00-V02",
            "state": "debug",
            "vehicleConfigId": "VHC-VH1-03",
            "description": " 第一个车型模型关联",
            "editState": false,
            "alParamId": "ALP-VH1-02",
            "releaseTime": "2020-05-09T17:25:17",
            "createTime": "2020-05-09T17:25:31",
            "vehicleTypeId": "VHT-VH2-01"
        }
    ]
    @@@
    """
    vehicle_config_model_link_all = TConfigModelLink.query.all()
    for object_item in vehicle_config_model_link_all:
        object_item.editState = False
    vehicle_config_model_links = TConfigModelLinkSchema(many=True)
    return Formatter.formatter(vehicle_config_model_links.dumps(vehicle_config_model_link_all), False)


# 车辆配置与模型匹配映射表新增
@m_config.route('/vehicle_config_model_link_table', methods=['GET', 'POST'])
@cross_origin()
def add_vehicle_config_model_link_item():
    """车辆配置与模型匹配映射表新增一条记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    none    |    none    |    none   |    none    |
    #### request body
    - ##### form data
    ```json
        {
            "configModelLinkId": "000008",
            "vehicleTypeId": “VHT-VH1-01”,
            ""vehicleConfigId"": “VHC-VH1-01”,
            ""vehicleModelId"": “IDM-VC1-00-V01”,
            ""alParamId"": “ALP-VH1-01”,
            "description": '这是link配置说明',
            "state": 'release',
            "operation": '-',
            "releaseTime": '2020-05-06 18:13:12'
        }
    ```
    #### return
    - ##### json
    ```
        {
            "message": "增加车辆配置模型关联信息成功",
             "status": 200
        }
    ```
    @@@
    """
    try:
        vehicle_config_model_link_info = request.form
        vehicle_config_model_link_item = TConfigModelLink(
            config_model_link_id=vehicle_config_model_link_info["configModelLinkId"],
            vehicle_type_id=vehicle_config_model_link_info["vehicleTypeId"],
            vehicle_config_id=vehicle_config_model_link_info["vehicleConfigId"],
            vehicle_model_id=vehicle_config_model_link_info["vehicleModelId"],
            al_param_id=vehicle_config_model_link_info["alParamId"],
            description=vehicle_config_model_link_info["description"],
            state=vehicle_config_model_link_info["state"],
            operation=vehicle_config_model_link_info["operation"],
            release_time=vehicle_config_model_link_info["releaseTime"]
        )
        db.session.add(vehicle_config_model_link_item)
        db.session.commit()
        return jsonify({'status': 200, 'message': '增加车辆配置模型关联信息成功'}), 200, {"name": "**"}
    except BaseException as e:
        return jsonify({'status': 500, 'message': '增加车辆配置模型关联信息失败'}), 500, {"name": "**"}


# 车辆配置与模型匹配映射表删除一条记录
@m_config.route('/vehicle_config_model_link/<config_model_link_id>', methods=['DELETE'])
@cross_origin()
def del_vehicle_config_model_link_item(config_model_link_id):
    """车辆配置与模型匹配映射表删除一条记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    config_model_link_id    |    false    |    String   |    车辆配置与模型匹配映射ID    |
    #### return
    - ##### json
    ```
        {
            "message": "删除车辆配置与模型匹配映射表记录成功",
             "status": 200
        }
    ```
    @@@
    """
    try:
        vehicle_config_model_link_item = TConfigModelLink.query.filter_by(config_model_link_id=config_model_link_id)
        db.session.delete(vehicle_config_model_link_item)
        db.session.commit()
        return jsonify({'status': 200, 'message': '删除车辆配置与模型匹配映射表记录成功'}), 200, {"name": "**"}
    except BaseException as e:
        return jsonify({'status': 500, 'message': '删除车辆配置与模型匹配映射表记录失败'}), 500, {"name": "**"}


# 车辆配置与模型匹配映射表修改一条记录
@m_config.route('/vehicle_config_model_link/<config_model_link_id>', methods=['PUT'])
@cross_origin()
def update_vehicle_config_model_link_item(config_model_link_id):
    """车辆配置与模型匹配映射表修改一条记录
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    config_model_link_id    |    false    |    String   |    配置模型关联ID    |
    #### request body
    - ##### json
    ```json
        {
            "configModelLinkId": "000008",
            "vehicleTypeId": “VHT-VH1-01”,
            "vehicleConfigId": “VHC-VH1-01”,
            "vehicleModelId": “IDM-VC1-00-V01”,
            "alParamId": “ALP-VH1-01”,
            "description": '这是link配置说明',
            "state": 'release',
            "operation": '-',
            "releaseTime": '2020-05-06 18:13:12'
        }
    ```
    #### return
    - ##### json
    ```
        {
            "message": "修改车辆配置与模型匹配映射成功",
             "status": 200
        }
    ```
    @@@
    """
    try:
        if request.method == 'PUT':
            data = request.get_data()
            json_data = json.loads(data.decode("utf-8"))
            vehicle_config_model_link_item = TConfigModelLink.query.filter_by(config_model_link_id=config_model_link_id)

            vehicle_config_model_link_item.config_model_link_id = json_data["configModelLinkId"],
            vehicle_config_model_link_item.vehicle_type_id = json_data["vehicleTypeId"],
            vehicle_config_model_link_item.vehicle_config_id = json_data["vehicleConfigId"],
            vehicle_config_model_link_item.vehicle_model_id = json_data["vehicleModelId"],
            vehicle_config_model_link_item.al_param_id = json_data["alParamId"],
            vehicle_config_model_link_item.description = json_data["description"],
            vehicle_config_model_link_item.state = json_data["state"],
            vehicle_config_model_link_item.operation = json_data["operation"],
            vehicle_config_model_link_item.release_time = json_data["releaseTime"]

            db.session.commit()
            return jsonify({'status': 200, 'message': '修改车辆配置与模型匹配映射成功'}), 200, {"name": "**"}
    except BaseException as e:
        return jsonify({'status': 500, 'message': '修改车辆配置与模型匹配映射失败'}), 500, {"name": "**"}


# 查询车型-配置-模型link关联是否重复
@m_config.route('/vehicle_type_config_model_exist', methods=['POST'])
@cross_origin()
def check_vehicle_type_config_model_exist():
    """校验车型 配置 模型link关联是否重复
    @@@
    #### args
    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |   none     |    none    |   none    |    none    |
    #### request body
    ```javascript
        {
            "vehicleTypeId": "VHT-VH1-01",
            "vehicleConfigId": "VHC-VH1-01",
            "vehicleModelId": "IDM-VC1-00-V01"
        }
    ```
    #### return
    - ##### json
    >
        {"massage": "车型-配置-模型link关联合法可用", "data": 1}
    @@@
    """
    data = request.get_data()
    data = TConfigModelLink.query.filter_by(
        vehicle_type_id=data["vehicleTypeId"],
        vehicle_config_id=data["vehicleConfigId"],
        vehicle_model_id=data["vehicleModelId"],
    ).all()

    if len(data) == 0:
        return jsonify({"massage": "车型-配置-模型link关联合法可用", "data": 1}), 200, ""
    elif len(data) > 0:
        return jsonify({"massage": "车型-配置-模型link关联重复", "data": 0}), 409, ""
    else:
        jsonify({"massage": "内部错误", "data": -1}), 500, ""
