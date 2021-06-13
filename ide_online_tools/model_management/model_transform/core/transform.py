import numpy as np
import pandas as pd
import copy
import time
import datetime
from sqlalchemy import create_engine, event, and_
import pickle
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from ide_online_tools.model_management.model_transform.tables import *


def system_inputBinaryFile(filepath):
    f = open(filepath, 'rb')
    sys = pickle.load(f)
    f.close()
    print("序列化文件读取完成！")
    return sys


ts = time.time()
# MODEL_VERSION = "IDM-VC1-00-V01"
F_DENY = 0.5

# vdes_bom_filename = "C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\model_files\\final_test_model_20200422\\VHMS_BOM_INFO_TEMPLATE.xlsm"
# vdes_bom_filename = "C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\model_files\\final_test_model_20200422\\VHMS_BOM_INFO_TEMPLATE.xlsm"
# vdes_bom_filename = "C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\model_files\\final_test_model_20200422\\VHMS_BOM_INFO_TEMPLATE.xlsm"
# vdes_bom_filename = "C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\model_files\\all-output\\动力总成\\VHMS_BOM_INFO_PWT.xlsm"
vdes_bom_filename = "C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\model_files\\final_test_model_20200422\\VHMS_BOM_INFO_TEMPLATE.xlsm"
# dtc_bom_filename = "D:\\Python_workdir\\IDE_Online_Tools\\data\\model_files\\final_test_model_20200422\\DTC_BOM_VX1_TS0001_200413.xlsx"

# sys_db_file = "C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\model_files\\all-output\\动力总成\\V00000110_动力总成_200428.db"
# sys_db_file = "C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\model_files\\all-output\\动力总成\\V00000110_动力总成_200428.db"
# sys_db_file = "C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\model_files\\all-output\\动力总成\\V00000110_动力总成_200428.db"
# sys_db_file = "C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\model_files\\all-output\\动力总成\\V00000110_动力总成_200428.db"
sys_db_file = "C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\output\\BCOOL0426-1-sys.db"

# 数据库连接
# engine = create_engine("mysql+pymysql://root:root@localhost:3306/ide-2-sgn?charset=UTF8MB4", echo=False)
# engine = create_engine("mysql+pymysql://root:root@localhost:3306/ide-2-air?charset=UTF8MB4", echo=False)
# engine = create_engine("mysql+pymysql://root:root@localhost:3306/ide-2-all?charset=UTF8MB4", echo=False)
# engine = create_engine("mysql+pymysql://root:root@localhost:3306/ide-2-chs?charset=UTF8MB4", echo=False)
engine = create_engine("mysql+pymysql://root:root@localhost:3306/ide-2-8?charset=UTF8MB4", echo=False)


def add_own_encoders_int(conn, cursor, query, *args):
    cursor.connection.encoders[np.int64] = lambda value, encoders: int(value)


def add_own_encoders_float(conn, cursor, query, *args):
    cursor.connection.encoders[np.float64] = lambda value, encoders: float(value)


# 解决方法
event.listen(engine, "before_cursor_execute", add_own_encoders_int)
event.listen(engine, "before_cursor_execute", add_own_encoders_float)

# 建表
if not database_exists(engine.url):  # 如果数据库不存在
    print("数据库 {} 不存在，将新建数据库！".format(engine.url))
    create_database(engine.url)  # 创建数据库
    Base.metadata.create_all(engine)  # 创建表结构

# 创建与数据库的会话session class ,注意,这里返回给session的是个class类,不是实例
Session_class = sessionmaker(bind=engine)  # 创建用于数据库session的类
Session = Session_class()  # 这里才是生成session实例可以理解为cursor

# 车辆表写入

vehicle_info = pd.read_excel(vdes_bom_filename, sheet_name="BOM_VEHICLE")
system_info = pd.read_excel(vdes_bom_filename, sheet_name="BOM_SYSTEM")
part_info = pd.read_excel(vdes_bom_filename, sheet_name="BOM_PART")
ECU_info = pd.read_excel(vdes_bom_filename, sheet_name="BOM_DTC")
# 本次导入信息的车辆ID
VEHICLE_ID = vehicle_info["vehicle_id"][vehicle_info.index[0]]
MODEL_VERSION = "-".join(["IDM", VEHICLE_ID, "%02d" % 1, "V10"])
vehicle = TVehicle(
    vehicle_id=vehicle_info["vehicle_id"][vehicle_info.index[0]],
    vehicle_brand=vehicle_info["vehicle_brand"][vehicle_info.index[0]],
    vehicle_name=vehicle_info["vehicle_name"][vehicle_info.index[0]],
    vehicle_type=vehicle_info["vehicle_type"][vehicle_info.index[0]],
    vehicle_config_id=vehicle_info["vehicle_config_id"][vehicle_info.index[0]],
    vehicle_comment=vehicle_info["vehicle_comment"][vehicle_info.index[0]],
    model_version=MODEL_VERSION
)

vehicle_add_prequery = Session.query(TVehicle).filter(
    TVehicle.vehicle_id == vehicle_info["vehicle_id"][vehicle_info.index[0]]).all()
if len(vehicle_add_prequery) == 0:
    Session.add(vehicle)
else:
    print("当前导入的车型( {} )信息数据库中已经存在！".format(vehicle_add_prequery[0].vehicle_id))
Session.commit()
#
# 导入系统信息
system = TSystem(
    system_id=system_info["system_id_define"][system_info.index[0]],
    system_name=system_info["system_name"][system_info.index[0]],
    system_description=system_info["system_description"][system_info.index[0]],
    system_type=system_info["system_type"][system_info.index[0]],
    vehicle_id_belong=system_info["vehicle_id_belong"][system_info.index[0]],
    system_producer=system_info["system_producer"][system_info.index[0]],
    software_version=system_info["software_version"][system_info.index[0]],
    model_version=MODEL_VERSION
)
system_add_prequery = Session.query(TSystem).filter(
    TSystem.system_id == system_info["system_id"][system_info.index[0]]).all()
if len(system_add_prequery) == 0:
    Session.add(system)
else:
    print("当前导入的系统( {} )信息数据库中已经存在！".format(system_add_prequery[0].system_id))
Session.commit()

# 导入部件信息
for i, row_content_index in enumerate(part_info.index.tolist()):
    if pd.isna(part_info["system_name"][row_content_index]):
        break
    system_query = Session.query(TSystem).filter(
        TSystem.system_name == part_info["system_name"][row_content_index]).first()
    # 生成part ID
    part_id = "-".join([system_query.vehicle_id_belong, system_query.system_id, "%06d" % (row_content_index + 1)])
    part_add_prequery = Session.query(TPart).filter(
        TPart.part_id == part_id).all()
    if len(part_add_prequery) == 0:
        part = TPart(part_id=part_id,
                     bom_id=part_info["bom_id"][row_content_index],
                     part_name=part_info["part_name"][row_content_index],
                     part_type="-",
                     part_description="-",
                     sys_id_belong=system_query.system_id,
                     software_version=part_info["software_version"][row_content_index],
                     part_producer="-",
                     model_version=MODEL_VERSION
                     )
        Session.add(part)
    else:
        print("当前导入的部件( {} )信息数据库中已经存在！".format(part_add_prequery[0].part_name))
Session.commit()





# 导入车型信息
vehicle_type = TVehicleType(
    vehicle_type_id="-".join(["VHT", VEHICLE_ID, "%02d" % 1]),
    vin_re="LDC131D2010457852",
    brand_name="高合HiPhi",
    vehicle_type_name="EV-SUV",
    create_user="cp",
)
vehicle_type_add_prequery = Session.query(TVehicleType).filter(
    TVehicleType.vehicle_type_id == "-".join(["VHT", VEHICLE_ID, "%02d" % 1])).all()
if len(vehicle_type_add_prequery) == 0:
    Session.add(vehicle_type)
else:
    print("当前导入的车型( {} )信息数据库中已经存在！".format(vehicle_type_add_prequery[0].vehicle_type_id))
Session.commit()



# 导入车型配置信息
vehicle_config = TVehicleConfig(
    vehicle_config_id="-".join(["VHC", VEHICLE_ID, "%02d" % 1]),
    vehicle_config_name="第一个车辆配置",
    vehicle_config_description="第一个车辆配置",
    vehicle_type_id_belong="-".join(["VHT", VEHICLE_ID, "%02d" % 1]),
    create_user="cp",
)
vehicle_config_add_prequery = Session.query(TVehicleConfig).filter(
    TVehicleConfig.vehicle_config_id == "-".join(["VHC", VEHICLE_ID, "%02d" % 1])).all()
if len(vehicle_config_add_prequery) == 0:
    Session.add(vehicle_config)
else:
    print("当前导入的车辆配置( {} )信息数据库中已经存在！".format(vehicle_config_add_prequery[0].vehicle_config_id))
Session.commit()

# 导入模型信息  version_code="-".join(["IDM", VEHICLE_ID, "%02d" % 1, "V10"]),
vehicle_model = TVehicleModel(
    vehicle_model_id=MODEL_VERSION,
    version_code=MODEL_VERSION,
    vehicle_type_id="-".join(["VHT", VEHICLE_ID, "%02d" % 1]),
    vehicle_config_id="-".join(["VHC", VEHICLE_ID, "%02d" % 1]),
    vehicle_model_name="第一个Test车辆模型",
    release_time=datetime.datetime.now(),
    create_user="cp",
)
vehicle_model_add_prequery = Session.query(TVehicleModel).filter(
    TVehicleModel.vehicle_model_id == "-".join(["IDM", VEHICLE_ID, "%02d" % 1, "V10"])).all()
if len(vehicle_model_add_prequery) == 0:
    Session.add(vehicle_model)
else:
    print("当前导入的车辆模型( {} )信息数据库中已经存在！".format(vehicle_model_add_prequery[0].vehicle_model_id))
Session.commit()


# 导入算法参数信息
data_json = {}
data_json["p_observe_absy_limit"] = 0
data_json["b_test_basis"] = 1.2
data_json["b_test_part"] = 1
data_json["b_test_sys"] = 1
data_json["theta_cr_high"] = 0.01
data_json["theta_cr_middle"] = 0.02
data_json["theta_cr_low"] = 0.05
data_json["theta_effect_test"] = 0.5

data_json["t_test_limit_high"] = 70
data_json["t_test_limit_low"] = 40
data_json["e_test_allcontain"] = -0.2
data_json["k_cost_ca"] = 0.3

al_param = TAlgorithmParameter(
    al_param_set_id="-".join(["ALP", VEHICLE_ID, "%02d" % 1]),
    al_param_set_name="base版本算法",
    al_param_set_data=str(data_json),
    al_param_set_version="V1",
    al_param_type="base"
)
al_param_add_prequery = Session.query(TAlgorithmParameter).filter(
    TAlgorithmParameter.al_param_set_id == "-".join(["IDM", VEHICLE_ID, "%02d" % 1, "V10"])).all()
if len(al_param_add_prequery) == 0:
    Session.add(al_param)
else:
    print("当前导入的车辆模型( {} )信息数据库中已经存在！".format(al_param_add_prequery[0].al_param_set_id))
Session.commit()



# 导入车型-模型匹配关联信息
# vehicle_config_link_config = TConfigModelLink(
#     config_model_link_id="%06d" % 1,
#     vehicle_type_id="-".join(["VHT", VEHICLE_ID, "%02d" % 1]),
#     vehicle_type_name="EV-SUV",
#     vehicle_config_id="-".join(["VHC", VEHICLE_ID, "%02d" % 1]),
#     vehicle_config_name="第一个车辆配置",
#     vehicle_model_id="-".join(["IDM", VEHICLE_ID, "%02d" % 1, "V10"]),
#     vehicle_model_code="-".join(["IDM", VEHICLE_ID, "%02d" % 1, "V10"]),
#     al_param_id="-".join(["ALP", VEHICLE_ID, "%02d" % 1]),
#     al_param_name="第一个算法参数",
#     description="第一个车型模型关联",
#     state="release",
#     operation="",
#     release_time=datetime.datetime.now()
# )
vehicle_config_link_config = TConfigModelLink(
    config_model_link_id="%06d" % 1,
    vehicle_type_id="-".join(["VHT", VEHICLE_ID, "%02d" % 1]),
    vehicle_config_id="-".join(["VHC", VEHICLE_ID, "%02d" % 1]),
    vehicle_model_id=MODEL_VERSION,
    al_param_id="-".join(["ALP", VEHICLE_ID, "%02d" % 1]),
    description="第一个车型模型关联",
    state="release",
    operation="",
    release_time=datetime.datetime.now()
)
vehicle_config_model_add_prequery = Session.query(TConfigModelLink).filter(
    TConfigModelLink.config_model_link_id == "%06d" % 1).all()
if len(vehicle_config_model_add_prequery) == 0:
    Session.add(vehicle_config_link_config)
else:
    print("当前导入的车型-模型关联( {} )信息数据库中已经存在！".format(vehicle_config_model_add_prequery[0].config_model_link_id))
Session.commit()

# 导入DTC节点信息
ECU_info_drop_duplicates = ECU_info.drop_duplicates(subset=["vehicle_name", "dtc_node"], keep="first")
for row_content_index in ECU_info_drop_duplicates.index.tolist():
    if pd.isna(ECU_info_drop_duplicates["vehicle_name"][row_content_index]):
        break
    vehicle_query = Session.query(TVehicle).filter(
        TVehicle.vehicle_name == ECU_info_drop_duplicates["vehicle_name"][row_content_index]).first()
    # 生成 node_id
    node_id = "-".join([vehicle_query.vehicle_id, "ECU", "%06d" % (row_content_index + 1)])
    dtc_node_add_prequery = Session.query(TDtcNodeInfo).filter(
        TDtcNodeInfo.node_id == node_id).all()
    if len(dtc_node_add_prequery) == 0:
        dtc_node = TDtcNodeInfo(node_id=node_id,
                                node_name=ECU_info_drop_duplicates["dtc_node"][row_content_index],
                                node_description=ECU_info_drop_duplicates["dtc_node"][row_content_index],
                                model_version=MODEL_VERSION,
                                )
        Session.add(dtc_node)
    else:
        print("当前导入的ECU节点( {} )信息数据库中已经存在！".format(dtc_node_add_prequery[0].node_name))
Session.commit()

# 系统模型数据加载
sys_data = system_inputBinaryFile(sys_db_file)
print("系统模型数据载入成功!")


# 信息表数据导入
fm_zone = [(sys_data.sys_full_cursor["FS"][0] + 1, sys_data.sys_full_cursor["IS"][0]), (0, 3)]
fm_zone_data = sys_data.sysdatatable[0].iloc[fm_zone[0][0]:fm_zone[0][1], 0:3]
fm_num = {}  # 生成某一系统的部件的失效模式编号
for i, index in enumerate(fm_zone_data.index.tolist()):
    if fm_zone_data.loc[index, 0] in fm_num.keys():
        fm_num[fm_zone_data.loc[index, 0]] += 1
    else:
        fm_num[fm_zone_data.loc[index, 0]] = 1
    part_id_query = Session.query(TPart).filter(
        TPart.part_name == fm_zone_data.loc[index, 0]).first()
    fm_id = "-".join([part_id_query.part_id, "FM", "%04d" % fm_num[fm_zone_data.loc[index, 0]]])
    fm_info_add_prequery = Session.query(TFmInfo).filter(
        TFmInfo.fm_id == fm_id).all()
    if len(fm_info_add_prequery) == 0:
        fm_info = TFmInfo(
            fm_id=fm_id,
            fm_name=fm_zone_data.loc[index, 1],
            fm_f=fm_zone_data.loc[index, 2],
            fm_p=1,
            part_id=part_id_query.part_id,
            fm_times=0,
            model_version=MODEL_VERSION
        )
        Session.add(fm_info)
    else:
        print("当前导入的失效模式( {} )信息数据库中已经存在！".format(fm_info_add_prequery[0].fm_name))
        pass

Session.commit()
print("t_fm_info表导入完成")
# dtc表 从输入的BOM_DTC表导入
# 导入DTC信息
for row_content_index in ECU_info.index.tolist():
    if pd.isna(ECU_info.loc[row_content_index, "dtc_node"]):
        break
    node_info_query = Session.query(TDtcNodeInfo).filter(
        TDtcNodeInfo.node_name == ECU_info.loc[row_content_index, "dtc_node"]).first()
    # 生成 dtc ID
    dtc_id = "-".join([node_info_query.node_id, "DT", "%04d" % (row_content_index + 1)])
    dtc_add_prequery = Session.query(TDtcInfo).filter(
        TDtcInfo.dtc_id == dtc_id).all()
    if len(dtc_add_prequery) == 0:
        dtc_info = TDtcInfo(
            dtc_id=dtc_id,
            dtc=ECU_info["dtc"][row_content_index],
            dtc_description=ECU_info["dtc_description"][row_content_index],
            dtc_node=ECU_info["dtc_node"][row_content_index],
            dtc_confirm_condition=ECU_info["dtc_confirm_condition"][row_content_index],
            model_version=MODEL_VERSION
        )
        Session.add(dtc_info)
    else:
        print("当前导入的dtc( {} )信息数据库中已经存在！".format(dtc_add_prequery[0].dtc))
Session.commit()

# 症状和dtc表 从模型导入
sy_dtc_test_zone_data = sys_data.sysdatatable[0].iloc[0:2,
                        sys_data.sys_full_cursor["FS"][1] + 1:sys_data.sys_full_cursor["FO"][1]].T
sy_dtc_test_zone_data.columns = ["症状类别", "症状描述"]
sy_zone_data = sy_dtc_test_zone_data[sy_dtc_test_zone_data["症状类别"].str.contains("系统症状|部件症状") == True]
dtc_zone_data = sy_dtc_test_zone_data[sy_dtc_test_zone_data["症状类别"].str.contains("DTC_") == True]
test_zone_data = sy_dtc_test_zone_data[sy_dtc_test_zone_data["症状类别"].str.contains("Test_") == True]

for i, index in enumerate(dtc_zone_data.index.tolist()):
    dtc = dtc_zone_data.loc[index, "症状类别"].split("_")[2]  # DTC_BMS_P10F109
    dtc_node_name = dtc_zone_data.loc[index, "症状类别"].split("_")[1]  # DTC_BMS_P10F109

    dtc_add_prequery = Session.query(TDtcInfo).filter(and_(TDtcInfo.dtc_node == dtc_node_name,
                                                           TDtcInfo.dtc == dtc)).all()
    if len(dtc_add_prequery) == 0:
        # 当有新加入的dtc时，一般不会触发
        node_info_query = Session.query(TDtcNodeInfo).filter(
            TDtcNodeInfo.node_name == dtc_node_name).all()
        assert len(node_info_query) == 1
        # 生成 dtc ID
        dtc_id = "-".join([node_info_query[0].node_id, "DT", "%04d" % (i + 1)])

        dtc_info = TDtcInfo(
            dtc_id=dtc_id,
            dtc=dtc,
            dtc_description=dtc_zone_data.loc[index, "症状描述"],
            dtc_node=dtc_node_name,
            dtc_confirm_condition="undefined",
            model_version=MODEL_VERSION
        )
        Session.add(dtc_info)
        print("模型中存在BOM_DTC表中不存在的DTC：{}".format(dtc))
    else:
        print("当前导入的dtc( {} )信息,已经从BOM_DTC表中导入，数据库中已经存在！".format(dtc_add_prequery[0].dtc))
Session.commit()
print("t_dtc_info 导入完成")

sy_num = {}
for i, index in enumerate(sy_zone_data.index.tolist()):
    if sy_zone_data.loc[index, "症状类别"] in sy_num.keys():
        sy_num[sy_zone_data.loc[index, "症状类别"]] += 1
    else:
        sy_num[sy_zone_data.loc[index, "症状类别"]] = 1
    sy_id = ""
    sy_level = ""
    sy_part_id = ""
    if sy_zone_data.loc[index, "症状类别"] == "系统症状":
        # sy_id = "VC3-000-000000-SY-" + "%04d" % (sysy_num[sy_zone_data.loc[index, "症状类别"]])
        sy_id = "-".join([VEHICLE_ID, "000", "000000", "SY", "%04d" % (sy_num[sy_zone_data.loc[index, "症状类别"]])])
        sy_level = "系统级"
        sy_part_id = "-"
    elif "部件症状_" in sy_zone_data.loc[index, "症状类别"]:
        part_name = sy_zone_data.loc[index, "症状类别"].split("_")[1]  # 部件症状_水管
        part_info = Session.query(TPart).filter(TPart.part_name == part_name).first()
        sy_id = "-".join([part_info.part_id, "SY", "%04d" % (sy_num[sy_zone_data.loc[index, "症状类别"]])])
        sy_level = part_name
        sy_part_id = part_info.part_id

    sy_add_prequery = Session.query(TSymptomInfo).filter(TSymptomInfo.sy_id == sy_id).all()
    if len(sy_add_prequery) == 0:
        sy_info = TSymptomInfo(
            sy_id=sy_id,
            sy_level=sy_level,
            sy_description=sy_zone_data.loc[index, "症状描述"],
            sy_sys_id="-",
            sy_part_id=sy_part_id,
            sy_times=1,
            sy_p=1,
            model_version=MODEL_VERSION
        )
        Session.add(sy_info)
    else:
        print("当前导入的症状( {} )信息,数据库中已经存在！".format(sy_add_prequery[0].sy_description))
print("t_symptom_info 导入完成")
Session.commit()

# 测试项目表  # 维修项目表
test_action_zone_data = pd.DataFrame()
ca_action_zone_data = pd.DataFrame()
for part_name, sheets in sys_data.parts_dict.items():
    test_action_zone_data = pd.concat([test_action_zone_data, sheets.sheets_list["06Test"].data.loc[1:, :]],
                                      ignore_index=True)
    ca_action_zone_data = pd.concat(
        [ca_action_zone_data, sheets.sheets_list["04Corrective Action-Cost"].data.loc[1:, :]],
        ignore_index=True)
test_action_zone_data.columns = ["test_action_content",
                                 "test_time_h",
                                 "test_cost_yuan",
                                 "part_bom_id",
                                 "part_name",
                                 "test_instruction_doc_link",
                                 "test_complexity",
                                 "test_type"]
ca_action_zone_data.columns = ["ca_name",
                               "ca_time_h",
                               "ca_cost_yuan",
                               "part_bom_id",
                               "part_name",
                               "ca_instruction"]

test_action_num = {}
for i, index in enumerate(test_action_zone_data.index.tolist()):
    if test_action_zone_data.loc[index, "part_name"] in test_action_num.keys():
        test_action_num[test_action_zone_data.loc[index, "part_name"]] += 1
    else:
        test_action_num[test_action_zone_data.loc[index, "part_name"]] = 1

    part_info = Session.query(TPart).filter(TPart.part_name == test_action_zone_data.loc[index, "part_name"]).first()
    test_action_id = "-".join([part_info.part_id, "TA", "%04d" % (test_action_num[part_info.part_name])])

    ta_add_prequery = Session.query(TTestActionInfo).filter(TTestActionInfo.test_action_id == test_action_id).all()
    if len(ta_add_prequery) == 0:
        test_action_info = TTestActionInfo(test_action_id=test_action_id,
                                           test_action_content=test_action_zone_data.loc[index, "test_action_content"],
                                           test_system_id=part_info.part_id[0:-7],
                                           test_part_id=part_info.part_id,
                                           test_cost_yuan=float(test_action_zone_data.loc[index, "test_cost_yuan"]),
                                           test_time_h=float(test_action_zone_data.loc[index, "test_time_h"]),
                                           test_type=test_action_zone_data.loc[index, "test_type"],
                                           test_complexity=test_action_zone_data.loc[index, "test_complexity"],
                                           test_instruction_doc_link="-",
                                           test_instruction_video_link="-",
                                           test_equipment="-",
                                           model_version=MODEL_VERSION
                                           )
        Session.add(test_action_info)
    else:
        print("当前导入的测试项目( {} )信息,数据库中已经存在！".format(ta_add_prequery[0].test_action_content))
Session.commit()
ca_action_num = {}
for i, index in enumerate(ca_action_zone_data.index.tolist()):
    if ca_action_zone_data.loc[index, "part_name"] in ca_action_num.keys():
        ca_action_num[ca_action_zone_data.loc[index, "part_name"]] += 1
    else:
        ca_action_num[ca_action_zone_data.loc[index, "part_name"]] = 1
    part_info = Session.query(TPart).filter(TPart.part_name == ca_action_zone_data.loc[index, "part_name"]).first()
    ca_action_id = "-".join([part_info.part_id, "CA", "%04d" % (ca_action_num[part_info.part_name])])
    ca_add_prequery = Session.query(TCaActionInfo).filter(TCaActionInfo.ca_action_id == ca_action_id).all()
    if len(ca_add_prequery) == 0:
        ca_action_info = TCaActionInfo(ca_action_id=ca_action_id,
                                       ca_name=ca_action_zone_data.loc[index, "ca_name"],
                                       ca_system_id=part_info.part_id[0:-7],
                                       ca_part_id=part_info.part_id,
                                       ca_cost_yuan=float(ca_action_zone_data.loc[index, "ca_cost_yuan"]),
                                       ca_time_h=float(ca_action_zone_data.loc[index, "ca_time_h"]),
                                       ca_type="-",
                                       ca_instruction="-",
                                       ca_complexity=0,
                                       ca_instruction_doc_link="-",
                                       ca_instruction_video_link="-",
                                       ca_equipment="-",
                                       model_version=MODEL_VERSION
                                       )
        Session.add(ca_action_info)
    else:
        print("当前导入的维修项目( {} )信息,数据库中已经存在！".format(ca_add_prequery[0].ca_name))

Session.commit()
print("test_action_table, ca action table, 导入完成")
# 测试结果和失效模式-维修项目关系提取
test_result_zone_data = pd.DataFrame(columns=["part_name",
                                              "test_ex_name",
                                              "link_value",
                                              "Test_action_name",
                                              "Test_result_check",
                                              "connect_to_ie"])
ca_result_zone_data = pd.DataFrame(columns=["part_name",
                                            "fm_name",
                                            "link_value",
                                            "ca_action_name"])
for part_name, sheets in sys_data.parts_dict.items():
    data_tmp = copy.deepcopy(sheets.sheets_list["05FM-CA"].data)
    data_tmp.index = data_tmp.iloc[:, 0]
    data_tmp.columns = data_tmp.iloc[0, :]
    data_tmp = data_tmp.drop(["失效模式"], axis=1)
    data_tmp = data_tmp.drop(["失效模式"], axis=0)
    for n, index_fm in enumerate(data_tmp.index.tolist()):
        for m, index_ca in enumerate(data_tmp.columns.tolist()):
            if data_tmp.iloc[n, m] == "X":
                ca_result_zone_data = ca_result_zone_data.append(pd.DataFrame(
                    {"part_name": part_name, "fm_name": index_fm, "link_value": "X", "ca_action_name": index_ca},
                    index=[0]), ignore_index=True)
    data_tmp2 = copy.deepcopy(sheets.sheets_list["07TestResult-Test"].data)
    data_tmp2.index = data_tmp2.iloc[:, 0]
    data_tmp2.columns = data_tmp2.iloc[0, :]
    data_tmp2 = data_tmp2.drop(["测试结果"], axis=1)
    data_tmp2 = data_tmp2.drop(["测试结果"], axis=0)
    for nn, index_test_ex in enumerate(data_tmp2.index.tolist()):
        for mm, index_test in enumerate(data_tmp2.columns.tolist()):
            if data_tmp2.iloc[nn, mm] == "X":
                if str(data_tmp2.iloc[nn, 0]) == "0":
                    test_result_zone_data = test_result_zone_data.append(pd.DataFrame(
                        {"part_name": part_name, "test_ex_name": index_test_ex, "link_value": "X",
                         "Test_action_name": index_test, "Test_result_check": data_tmp2.iloc[nn, 0],
                         "connect_to_ie": -1},
                        index=[0]), ignore_index=True)
                elif str(data_tmp2.iloc[nn, 0]) == "1":
                    temp = sy_dtc_test_zone_data[
                        sy_dtc_test_zone_data["症状类别"].str.contains("Test_" + part_name) == True]
                    temp = temp[temp["症状描述"].str.contains(index_test_ex) == True]
                    assert len(temp.index.tolist()) == 1
                    times = sys_data.sysdatatable[0].iloc[
                            sys_data.sys_full_cursor["IS"][0]:sys_data.sys_full_cursor["IS"][0] + 1,
                            temp.index.tolist()[0]].tolist()
                    if times[0] == 0:
                        connect_to_ie = 0
                    elif times[0] > 0:
                        connect_to_ie = 1
                    else:
                        connect_to_ie = -1
                    test_result_zone_data = test_result_zone_data.append(pd.DataFrame(
                        {"part_name": part_name, "test_ex_name": index_test_ex, "link_value": "X",
                         "Test_action_name": index_test, "Test_result_check": data_tmp2.iloc[nn, 0],
                         "connect_to_ie": connect_to_ie},  # x if(x>y) else y
                        index=[0]), ignore_index=True)

# 导入 # ca result table    # test result table
ca_result_num = {}
test_result_num = {}
cnt_fm_ca = 0
for i, index in enumerate(ca_result_zone_data.index.tolist()):
    cnt_fm_ca += 1
    if ca_result_zone_data.loc[index, "part_name"] in ca_result_num.keys():
        ca_result_num[ca_result_zone_data.loc[index, "part_name"]] += 1
    else:
        ca_result_num[ca_result_zone_data.loc[index, "part_name"]] = 1
    part_info = Session.query(TPart).filter(TPart.part_name == ca_result_zone_data.loc[index, "part_name"]).first()
    fm_ca_link_id = "-".join([part_info.part_id.split("-")[0], "FC", "%06d" % cnt_fm_ca])
    fm_info_result = Session.query(TFmInfo).filter(and_(TFmInfo.part_id == part_info.part_id,
                                                        TFmInfo.fm_name == ca_result_zone_data.loc[
                                                            index, "fm_name"])).first()
    ca_info_result = Session.query(TCaActionInfo).filter(and_(TCaActionInfo.ca_part_id == part_info.part_id,
                                                              TCaActionInfo.ca_name == ca_result_zone_data.loc[
                                                                  index, "ca_action_name"])).first()

    fm_ca_add_prequery = Session.query(TFmCaLink).filter(TFmCaLink.fm_ca_link_id == fm_ca_link_id).all()
    if len(fm_ca_add_prequery) == 0:
        fm_ca_link_info = TFmCaLink(fm_ca_link_id=fm_ca_link_id,
                                    fm_id=fm_info_result.fm_id,
                                    ca_id=ca_info_result.ca_action_id,
                                    model_version=MODEL_VERSION,
                                    other=""
                                    )
        Session.add(fm_ca_link_info)
    else:
        print("当前导入的失效模式FM和维修项目CA关联( {} )信息,数据库中已经存在！".format(fm_ca_add_prequery[0].fm_ca_link_id))

for i, index in enumerate(test_result_zone_data.index.tolist()):
    if test_result_zone_data.loc[index, "part_name"] in test_result_num.keys():
        test_result_num[test_result_zone_data.loc[index, "part_name"]] += 1
    else:
        test_result_num[test_result_zone_data.loc[index, "part_name"]] = 1
    part_info = Session.query(TPart).filter(
        TPart.part_name == test_result_zone_data.loc[index, "part_name"]).first()
    test_result_id = "-".join([part_info.part_id, "TR", "%04d" % (test_result_num[part_info.part_name])])
    # test_result_zone_data.loc[index, "Test_action_name"]
    test_action_result = Session.query(TTestActionInfo).filter(and_(
        TTestActionInfo.test_part_id == part_info.part_id, TTestActionInfo.test_action_content == test_result_zone_data.loc[index, "Test_action_name"])).first()
    test_result_add_prequery = Session.query(TTestResultInfo).filter(
        TTestResultInfo.test_result_id == test_result_id).all()
    if len(test_result_add_prequery) == 0:
        test_result_info = TTestResultInfo(test_result_id=test_result_id,
                                           test_result_name=test_result_zone_data.loc[index, "test_ex_name"],
                                           test_result_check=test_result_zone_data.loc[index, "Test_result_check"],
                                           test_action_id=test_action_result.test_action_id,
                                           test_system_id=part_info.part_id[0:-7],
                                           connect_to_ie=test_result_zone_data.loc[index, "connect_to_ie"],
                                           test_part_id=part_info.part_id,
                                           model_version=MODEL_VERSION
                                           )
        Session.add(test_result_info)
    else:
        print("当前导入的部件测试结果( {} )信息,数据库中已经存在！".format(test_result_add_prequery[0].test_result_name))
Session.commit()
print("test_result_table, ca result table(FM-CA) 导入完成")

# 提取出模型中的所有接口信息
ie_zone_data_in = sys_data.sysdatatable[0].iloc[sys_data.sys_full_cursor["IS"][0] + 1:, 0:2]
ie_zone_data_out = sys_data.sysdatatable[0].iloc[0:2, sys_data.sys_full_cursor["IO"][1] + 1:].T
ie_zone_data = pd.concat([ie_zone_data_in, ie_zone_data_out], ignore_index=True)
ie_zone_data = ie_zone_data.drop_duplicates()
ie_zone_data.columns = ["interface", "interface_exception"]
ie_zone_data["interface_type"] = ie_zone_data["interface"].map(lambda x: x.split("_")[0])
ie_zone_data["interface_property"] = ie_zone_data["interface"].map(lambda x: "".join(x.split("_")[1:]))
interface_info = ie_zone_data[["interface", "interface_type", "interface_property"]]
interface_info = interface_info.drop_duplicates()
for i, index in enumerate(interface_info.index.tolist()):
    interface_id = "-".join([VEHICLE_ID, "INF", "%06d" % (i + 1)])
    interface_info_add_prequery = Session.query(TInterfaceInfo).filter(
        TInterfaceInfo.interface_id == interface_id).all()
    if len(interface_info_add_prequery) == 0:
        interface_info_result = TInterfaceInfo(interface_id=interface_id,
                                               interface_name=interface_info.loc[index, "interface"],
                                               interface_description="-",
                                               interface_type=interface_info.loc[index, "interface_type"],
                                               interface_property=interface_info.loc[index, "interface_property"],
                                               interface_dirction=0,
                                               interface_connect_state=0,
                                               model_version=MODEL_VERSION
                                               )
        Session.add(interface_info_result)
    else:
        print("当前导入的接口( {} )信息,数据库中已经存在！".format(interface_info_add_prequery[0].interface_name))

for i, index in enumerate(ie_zone_data.index.tolist()):
    interface_result = Session.query(TInterfaceInfo).filter(
        TInterfaceInfo.interface_name == ie_zone_data.loc[index, "interface"]).first()
    ie_id = "-".join([interface_result.interface_id, "IE", "%04d" % (i + 1)])
    interface_exception_add_prequery = Session.query(TInterfaceExceptionInfo).filter(
        TInterfaceExceptionInfo.ie_id == ie_id).all()
    if len(interface_exception_add_prequery) == 0:
        ie_info = TInterfaceExceptionInfo(ie_id=ie_id,
                                          ie_description=ie_zone_data.loc[index, "interface_exception"],
                                          ie_cause="-",
                                          ie_influence="-",
                                          interface_id_belong=interface_result.interface_id,
                                          ie_state=0,
                                          model_version=MODEL_VERSION
                                          )
        Session.add(ie_info)
    else:
        print("当前导入的接口异常( {} )信息,数据库中已经存在！".format(interface_exception_add_prequery[0].ie_description))
Session.commit()

# 关联表导入

# 获得主要推理区域数据
reasoner_link_zone_data = sys_data.sysdatatable[0].iloc[0:sys_data.sys_full_cursor["IO"][0],
                          0:sys_data.sys_full_cursor["IO"][1]].T
reasoner_link_zone_data.columns = [str(x) for x in range(0, len(reasoner_link_zone_data.columns))]
f_s_zone_data = reasoner_link_zone_data[
    reasoner_link_zone_data["0"].str.contains("症状类别|系统编号|系统名称|系统症状|部件症状_") == True].T
f_dtc_zone_data = reasoner_link_zone_data[
    reasoner_link_zone_data["0"].str.contains("症状类别|系统编号|系统名称|DTC_") == True].T
f_test_zone_data = reasoner_link_zone_data[
    reasoner_link_zone_data["0"].str.contains("症状类别|系统编号|系统名称|Test_") == True].T
# 获得 FM-interface-out区域数据
fm_ca_columns = [0, 1, 2]
fm_ca_columns.extend(list(range(sys_data.sys_full_cursor["IO"][1] + 1, sys_data.sysdatatable[0].shape[1])))
fm_interface_out_link_zone_data = sys_data.sysdatatable[0].iloc[0:sys_data.sys_full_cursor["IO"][0], fm_ca_columns]

# 获得 interface-in interface-out区域数据
ie_in_ie_out_columns = [0, 1, 2]
ie_in_ie_out_columns.extend(list(range(sys_data.sys_full_cursor["IO"][1] + 1, sys_data.sysdatatable[0].shape[1])))
ie_in_ie_out_index = [0, 1]
ie_in_ie_out_index.extend(list(range(sys_data.sys_full_cursor["IO"][0], sys_data.sysdatatable[0].shape[0])))

interface_in_out_link_zone_data = sys_data.sysdatatable[0].iloc[ie_in_ie_out_index, ie_in_ie_out_columns]
# 获得 Interface Exception 区域数据
interface_link_zone_data = sys_data.sysdatatable[0].iloc[ie_in_ie_out_index,
                           0:sys_data.sys_full_cursor["IO"][1]].T
interface_link_zone_data.columns = [str(x) if x == 0 else y for x, y in enumerate(interface_link_zone_data.columns)]
i_s_zone_data = interface_link_zone_data[
    interface_link_zone_data["0"].str.contains("症状类别|系统编号|系统名称|系统症状|部件症状_") == True].T
i_dtc_zone_data = interface_link_zone_data[
    interface_link_zone_data["0"].str.contains("症状类别|系统编号|系统名称|DTC_") == True].T
i_test_zone_data = interface_link_zone_data[
    interface_link_zone_data["0"].str.contains("症状类别|系统编号|系统名称|Test_") == True].T

# FS table
cnt = 0
for n, indexs in enumerate(f_s_zone_data.index.tolist()):
    for m, columns in enumerate(f_s_zone_data.columns):
        if n > 2 and m > 2:
            if str(f_s_zone_data.iloc[n, m]) == "[,]" or pd.isna(f_s_zone_data.iloc[n, m]):
                pass
            else:
                cnt += 1
                link_entity_part1 = str(f_s_zone_data.iloc[n, m])[1:-1].split(",")[0]
                link_entity_part2 = str(f_s_zone_data.iloc[n, m])[1:-1].split(",")[1]

                # 获得当前关联部件信息
                part_info_f = Session.query(TPart).filter(
                    TPart.part_name == f_s_zone_data.iloc[n, 0]).all()
                assert len(part_info_f) == 1

                # 获得当前关联FM信息
                fm_info_f_s = Session.query(TFmInfo).filter(
                    and_(TFmInfo.part_id == part_info_f[0].part_id, TFmInfo.fm_name == f_s_zone_data.iloc[n, 1])).all()
                assert len(fm_info_f_s) == 1

                # 获得当前关联SY信息
                if str(f_s_zone_data.iloc[0, m]) == "系统症状":
                    sy_info_f_s = Session.query(TSymptomInfo).filter(
                        TSymptomInfo.sy_description == f_s_zone_data.iloc[1, m]).all()
                    assert len(sy_info_f_s) == 1
                elif "部件症状_" in str(f_s_zone_data.iloc[0, m]):
                    # 按照部件级症状所属部件查询部件信息
                    part_info_s = Session.query(TPart).filter(
                        TPart.part_name == f_s_zone_data.iloc[0, m].split("_")[1]).all()
                    assert len(part_info_s) == 1

                    sy_info_f_s = Session.query(TSymptomInfo).filter(
                        and_(TSymptomInfo.sy_description == f_s_zone_data.iloc[1, m],
                             TSymptomInfo.sy_part_id == part_info_s[0].part_id)).all()
                    assert len(part_info_s) == 1
                else:
                    sy_info_f_s = TSymptomInfo()

                # 计算关联系数 link_fs_correlation1
                link_fs_correlation1 = float(f_s_zone_data.iloc[n, 2]) / float(f_s_zone_data.iloc[2, m])

                # 计算否定系数 link_fs_correlation2
                if link_entity_part2 == "1":
                    link_fs_correlation2 = 0
                elif link_entity_part2 == "X":
                    link_fs_correlation2 = 1 - F_DENY
                elif link_entity_part2 == "0":
                    link_fs_correlation2 = 1
                else:
                    link_fs_correlation2 = -1
                # 获得关联ID 当FM和SY属于不同部件时，关联ID 按照FM的编号
                fm_sy_link_id = part_info_f[0].part_id[0:4] + "FS-" + "%06d" % cnt
                # 查询是否重复
                f_s_link_add_prequery = Session.query(TFmSyLink).filter(
                    TFmSyLink.fm_sy_link_id == fm_sy_link_id).all()
                if len(f_s_link_add_prequery) == 0:
                    f_s_link_info = TFmSyLink(fm_sy_link_id=fm_sy_link_id,
                                              fm_id=fm_info_f_s[0].fm_id,
                                              sy_id=sy_info_f_s[0].sy_id,
                                              link_level="-",
                                              link_times=1,
                                              model_version=MODEL_VERSION,
                                              link_correlation1=link_fs_correlation1,
                                              link_correlation2=link_fs_correlation2,
                                              link_correlation3=0,
                                              link_correlation4=0,
                                              link_correlation5=0,
                                              )
                    Session.add(f_s_link_info)
                else:
                    print("当前导入的失效模式-症状关联( {} )信息,数据库中已经存在！".format(f_s_link_add_prequery[0].fm_sy_link_id))
Session.commit()
print("Fm-Sy table  导入完成")

# F DTC table
cnt = 0
for n, indexs in enumerate(f_dtc_zone_data.index.tolist()):
    for m, columns in enumerate(f_dtc_zone_data.columns):
        if n > 2 and m > 2:
            if str(f_dtc_zone_data.iloc[n, m]) == "[,]" or pd.isna(f_dtc_zone_data.iloc[n, m]):
                pass
            else:
                cnt += 1
                link_entity_part1 = str(f_dtc_zone_data.iloc[n, m])[1:-1].split(",")[0]
                link_entity_part2 = str(f_dtc_zone_data.iloc[n, m])[1:-1].split(",")[1]

                # 获得当前关联部件信息
                part_info_f = Session.query(TPart).filter(
                    TPart.part_name == f_dtc_zone_data.iloc[n, 0]).all()
                assert len(part_info_f) == 1

                # # 获得当前关联ECU信息  由于直接可以通过节点信息和dtc查询到dtc_id 暂时没有必要
                # ecu_info_f = Session.query(TDtcNodeInfo).filter(
                #     TDtcNodeInfo.node_name == f_dtc_zone_data.iloc[0, m].split("_")[1]).all()
                # assert len(part_info_f) == 1

                # 获得当前关联FM信息
                fm_info_f_dtc = Session.query(TFmInfo).filter(
                    and_(TFmInfo.part_id == part_info_f[0].part_id,
                         TFmInfo.fm_name == f_dtc_zone_data.iloc[n, 1])).all()
                assert len(fm_info_f_dtc) == 1

                # 获得当前关联DTC信息
                dtc_info_f_dtc = Session.query(TDtcInfo).filter(
                    and_(TDtcInfo.dtc_node == f_dtc_zone_data.iloc[0, m].split("_")[1],
                         TDtcInfo.dtc == f_dtc_zone_data.iloc[0, m].split("_")[2])).all()
                assert len(dtc_info_f_dtc) == 1

                # 计算关联系数 link_fs_correlation1
                link_f_dtc_correlation1 = float(f_dtc_zone_data.iloc[n, 2]) / float(f_dtc_zone_data.iloc[2, m])

                # 计算否定系数 link_fs_correlation2
                if link_entity_part2 == "1":
                    link_f_dtc_correlation2 = 0
                elif link_entity_part2 == "X":
                    link_f_dtc_correlation2 = 1 - F_DENY
                elif link_entity_part2 == "0":
                    link_f_dtc_correlation2 = 1
                else:
                    link_f_dtc_correlation2 = -1
                # 获得关联ID 当FM和SY属于不同部件时，关联ID 按照FM的编号
                fm_dtc_link_id = part_info_f[0].part_id[0:4] + "FD-" + "%06d" % cnt
                # 查询是否重复
                f_dtc_link_add_prequery = Session.query(TFmDtcLink).filter(
                    TFmDtcLink.fm_dtc_link_id == fm_dtc_link_id).all()
                if len(f_dtc_link_add_prequery) == 0:
                    f_dtc_link_info = TFmDtcLink(fm_dtc_link_id=fm_dtc_link_id,
                                                 fm_id=fm_info_f_dtc[0].fm_id,
                                                 dtc_id=dtc_info_f_dtc[0].dtc_id,
                                                 link_level="-",
                                                 link_times=1,
                                                 model_version=MODEL_VERSION,
                                                 link_correlation1=link_f_dtc_correlation1,
                                                 link_correlation2=link_f_dtc_correlation2,
                                                 link_correlation3=0,
                                                 link_correlation4=0,
                                                 link_correlation5=0,
                                                 )
                    Session.add(f_dtc_link_info)
                else:
                    print("当前导入的失效模式-DTC关联( {} )信息,数据库中已经存在！".format(f_dtc_link_add_prequery[0].fm_dtc_link_id))
Session.commit()
print("F DTC table  导入完成")

# F Test table
cnt = 0
for n, indexs in enumerate(f_test_zone_data.index.tolist()):
    for m, columns in enumerate(f_test_zone_data.columns):
        if n > 2 and m > 2:
            if str(f_test_zone_data.iloc[n, m]) == "[,]" or pd.isna(f_test_zone_data.iloc[n, m]):
                pass
            else:
                cnt += 1
                link_entity_part1 = str(f_test_zone_data.iloc[n, m])[1:-1].split(",")[0]
                link_entity_part2 = str(f_test_zone_data.iloc[n, m])[1:-1].split(",")[1]

                # 获得当前FM关联部件信息
                part_info_f = Session.query(TPart).filter(
                    TPart.part_name == f_test_zone_data.iloc[n, 0]).all()
                assert len(part_info_f) == 1

                # 获得当前关联Test 对应部件信息
                part_info_t = Session.query(TPart).filter(
                    TPart.part_name == f_test_zone_data.iloc[0, m].split("_")[1]).all()
                assert len(part_info_t) == 1

                # 获得当前关联FM信息
                fm_info_f_test = Session.query(TFmInfo).filter(
                    and_(TFmInfo.part_id == part_info_f[0].part_id,
                         TFmInfo.fm_name == f_test_zone_data.iloc[n, 1])).all()
                assert len(fm_info_f_test) == 1

                # 获得当前关联Test信息
                test_info_f_test = Session.query(TTestResultInfo).filter(
                    and_(TTestResultInfo.test_part_id == part_info_t[0].part_id,
                         TTestResultInfo.test_result_name == f_test_zone_data.iloc[1, m])).all()
                assert len(test_info_f_test) == 1

                # 计算关联系数 link_fs_correlation1
                link_f_test_correlation1 = float(f_test_zone_data.iloc[n, 2]) / float(f_test_zone_data.iloc[2, m])

                # 计算否定系数 link_fs_correlation2
                if link_entity_part2 == "1":
                    link_f_test_correlation2 = 0
                elif link_entity_part2 == "X":
                    link_f_test_correlation2 = 1 - F_DENY
                elif link_entity_part2 == "0":
                    link_f_test_correlation2 = 1
                else:
                    link_f_test_correlation2 = -1
                # 获得关联ID 当FM和Test属于不同部件时，关联ID 按照FM的编号
                fm_test_link_id = part_info_f[0].part_id[0:4] + "FT-" + "%06d" % cnt
                # 查询是否重复
                f_test_link_add_prequery = Session.query(TFmTestLink).filter(
                    TFmTestLink.fm_test_link_id == fm_test_link_id).all()
                if len(f_test_link_add_prequery) == 0:
                    f_test_link_info = TFmTestLink(fm_test_link_id=fm_test_link_id,
                                                   fm_id=fm_info_f_test[0].fm_id,
                                                   test_id=test_info_f_test[0].test_result_id,
                                                   link_level="-",
                                                   link_times=1,
                                                   model_version=MODEL_VERSION,
                                                   link_correlation1=link_f_test_correlation1,
                                                   link_correlation2=link_f_test_correlation2,
                                                   link_correlation3=0,
                                                   link_correlation4=0,
                                                   link_correlation5=0,
                                                   )
                    Session.add(f_test_link_info)
                else:
                    print("当前导入的失效模式-TEST关联( {} )信息,数据库中已经存在！".format(f_test_link_add_prequery[0].fm_test_link_id))
Session.commit()
print("F Test Table 导入完成")

# F IE-out table
cnt = 0
for n, indexs in enumerate(fm_interface_out_link_zone_data.index.tolist()):
    for m, columns in enumerate(fm_interface_out_link_zone_data.columns):
        if n > 2 and m > 2:
            if str(fm_interface_out_link_zone_data.iloc[n, m]) == "[,]" or pd.isna(
                    fm_interface_out_link_zone_data.iloc[n, m]):
                pass
            else:
                cnt += 1
                link_entity_part1 = str(fm_interface_out_link_zone_data.iloc[n, m])[1:-1].split(",")[0]
                link_entity_part2 = str(fm_interface_out_link_zone_data.iloc[n, m])[1:-1].split(",")[1]

                # 获得当前FM关联部件信息
                part_info_f = Session.query(TPart).filter(
                    TPart.part_name == fm_interface_out_link_zone_data.iloc[n, 0]).all()
                assert len(part_info_f) == 1

                # 获得当前关联Interface out 对应接口信息
                interface_info_out = Session.query(TInterfaceInfo).filter(
                    TInterfaceInfo.interface_name == fm_interface_out_link_zone_data.iloc[0, m]).all()
                assert len(interface_info_out) == 1

                # 获得当前关联FM信息
                fm_info_f_ie = Session.query(TFmInfo).filter(
                    and_(TFmInfo.part_id == part_info_f[0].part_id,
                         TFmInfo.fm_name == fm_interface_out_link_zone_data.iloc[n, 1])).all()
                assert len(fm_info_f_ie) == 1

                # 获得当前关联IE-out信息
                ie_info_f_iout = Session.query(TInterfaceExceptionInfo).filter(
                    and_(TInterfaceExceptionInfo.ie_description == fm_interface_out_link_zone_data.iloc[1, m],
                         TInterfaceExceptionInfo.interface_id_belong == interface_info_out[0].interface_id)).all()
                assert len(ie_info_f_iout) == 1

                # 计算关联系数 link_fs_correlation1
                link_f_ie_out_correlation1 = float(fm_interface_out_link_zone_data.iloc[n, 2]) / float(
                    fm_interface_out_link_zone_data.iloc[2, m])

                # 计算否定系数 link_fs_correlation2
                if link_entity_part2 == "1":
                    link_f_ie_out_correlation2 = 0
                elif link_entity_part2 == "X":
                    link_f_ie_out_correlation2 = 1 - F_DENY
                elif link_entity_part2 == "0":
                    link_f_ie_out_correlation2 = 1
                else:
                    link_f_ie_out_correlation2 = -1
                # 获得关联ID 当FM和IE属于不同部件时，关联ID 按照FM的编号
                fm_ie_link_id = part_info_f[0].part_id[0:4] + "FI-" + "%06d" % cnt
                # 查询是否重复
                f_ie_link_add_prequery = Session.query(TFmIeLink).filter(
                    TFmIeLink.fm_ie_link_id == fm_ie_link_id).all()
                if len(f_ie_link_add_prequery) == 0:
                    f_ie_link_info = TFmIeLink(fm_ie_link_id=fm_ie_link_id,
                                               fm_id=fm_info_f_ie[0].fm_id,
                                               ie_id=ie_info_f_iout[0].ie_id,
                                               link_level="-",
                                               link_times=1,
                                               model_version=MODEL_VERSION,
                                               link_correlation1=link_f_ie_out_correlation1,
                                               link_correlation2=link_f_ie_out_correlation2,
                                               link_correlation3=0,
                                               link_correlation4=0,
                                               link_correlation5=0,
                                               )
                    Session.add(f_ie_link_info)
                else:
                    print("当前导入的失效模式-输出接口异常关联( {} )信息,数据库中已经存在！".format(f_ie_link_add_prequery[0].fm_ie_link_id))
Session.commit()
print("F IE-out table 导入完成")

# IE Sy Table

cnt = 0
for n, indexs in enumerate(i_s_zone_data.index.tolist()):
    for m, columns in enumerate(i_s_zone_data.columns):
        if n > 2 and m > 2:
            if str(i_s_zone_data.iloc[n, m]) == "[,]" or pd.isna(i_s_zone_data.iloc[n, m]):
                pass
            else:
                cnt += 1
                link_entity_part1 = str(i_s_zone_data.iloc[n, m])[1:-1].split(",")[0]
                link_entity_part2 = str(i_s_zone_data.iloc[n, m])[1:-1].split(",")[1]

                # 获得当前接口异常关联的接口信息
                interface_info_s = Session.query(TInterfaceInfo).filter(
                    TInterfaceInfo.interface_name == i_s_zone_data.iloc[n, 0]).all()
                assert len(interface_info_s) == 1

                # 获得当前关联SY信息
                if str(i_s_zone_data.iloc[0, m]) == "系统症状":
                    sy_info_ie_sy = Session.query(TSymptomInfo).filter(
                        TSymptomInfo.sy_description == f_s_zone_data.iloc[1, m]).all()
                    assert len(sy_info_ie_sy) == 1
                elif "部件症状_" in str(i_s_zone_data.iloc[0, m]):
                    # 按照部件级症状所属部件查询部件信息
                    part_info_s = Session.query(TPart).filter(
                        TPart.part_name == i_s_zone_data.iloc[0, m].split("_")[1]).all()
                    assert len(part_info_s) == 1

                    sy_info_ie_sy = Session.query(TSymptomInfo).filter(
                        and_(TSymptomInfo.sy_description == i_s_zone_data.iloc[1, m],
                             TSymptomInfo.sy_part_id == part_info_s[0].part_id)).all()
                    assert len(sy_info_ie_sy) == 1
                else:
                    sy_info_ie_sy = TSymptomInfo()

                # 获得当前关联接口异常信息
                interface_exception_info_ie_sy = Session.query(TInterfaceExceptionInfo).filter(
                    and_(TInterfaceExceptionInfo.interface_id_belong == interface_info_s[0].interface_id,
                         TInterfaceExceptionInfo.ie_description == i_s_zone_data.iloc[n, 1])).all()
                assert len(interface_exception_info_ie_sy) == 1

                # 计算关联系数 link_ie_sy_correlation1
                link_ie_sy_correlation1 = 1 / float(i_s_zone_data.iloc[2, m])

                # 获得关联ID 当FM和Test属于不同部件时，关联ID 按照FM的编号
                ie_sy_link_id = interface_info_s[0].interface_id[0:4] + "IS-" + "%06d" % cnt
                # 查询是否重复
                ie_sy_link_add_prequery = Session.query(TIeSyLink).filter(
                    TIeSyLink.ie_sy_link_id == ie_sy_link_id).all()
                if len(ie_sy_link_add_prequery) == 0:
                    ie_sy_link_info = TIeSyLink(ie_sy_link_id=ie_sy_link_id,
                                                ie_id=interface_exception_info_ie_sy[0].ie_id,
                                                sy_id=sy_info_ie_sy[0].sy_id,
                                                link_level="-",
                                                link_times=1,
                                                model_version=MODEL_VERSION,
                                                link_correlation1=link_ie_sy_correlation1,
                                                link_correlation2=0,
                                                link_correlation3=0,
                                                link_correlation4=0,
                                                link_correlation5=0,
                                                )
                    Session.add(ie_sy_link_info)
                else:
                    print("当前导入的接口异常-Sy关联( {} )信息,数据库中已经存在！".format(ie_sy_link_add_prequery[0].ie_sy_link_id))
Session.commit()
print("IE Sy Table 导入完成")

# IE DTC Table
cnt = 0
for n, indexs in enumerate(i_dtc_zone_data.index.tolist()):
    for m, columns in enumerate(i_dtc_zone_data.columns):
        if n > 2 and m > 2:
            if str(i_dtc_zone_data.iloc[n, m]) == "[,]" or pd.isna(i_dtc_zone_data.iloc[n, m]):
                pass
            else:
                cnt += 1
                link_entity_part1 = str(i_dtc_zone_data.iloc[n, m])[1:-1].split(",")[0]
                link_entity_part2 = str(i_dtc_zone_data.iloc[n, m])[1:-1].split(",")[1]

                # 获得当前接口异常关联的接口信息
                interface_info_s = Session.query(TInterfaceInfo).filter(
                    TInterfaceInfo.interface_name == i_dtc_zone_data.iloc[n, 0]).all()
                assert len(interface_info_s) == 1

                # 获得当前关联DTC信息
                dtc_info_ie_dtc = Session.query(TDtcInfo).filter(
                    and_(TDtcInfo.dtc_node == i_dtc_zone_data.iloc[0, m].split("_")[1],
                         TDtcInfo.dtc == i_dtc_zone_data.iloc[0, m].split("_")[2])).all()
                assert len(dtc_info_ie_dtc) == 1

                # 获得当前关联接口异常信息
                interface_exception_info_ie_dtc = Session.query(TInterfaceExceptionInfo).filter(
                    and_(TInterfaceExceptionInfo.interface_id_belong == interface_info_s[0].interface_id,
                         TInterfaceExceptionInfo.ie_description == i_dtc_zone_data.iloc[n, 1])).all()
                assert len(interface_exception_info_ie_dtc) == 1

                # 计算关联系数 link_ie_dtc_correlation1
                link_ie_dtc_correlation1 = 1 / float(i_dtc_zone_data.iloc[2, m])

                # 获得关联ID 当ie和Dtc属于不同部件时，关联ID 按照ie的编号
                ie_dtc_link_id = interface_info_s[0].interface_id[0:4] + "ID-" + "%06d" % cnt
                # 查询是否重复
                ie_dtc_link_add_prequery = Session.query(TIeDtcLink).filter(
                    TIeDtcLink.ie_dtc_link_id == ie_dtc_link_id).all()
                if len(ie_dtc_link_add_prequery) == 0:
                    ie_dtc_link_info = TIeDtcLink(ie_dtc_link_id=ie_dtc_link_id,
                                                  ie_id=interface_exception_info_ie_dtc[0].ie_id,
                                                  dtc_id=dtc_info_ie_dtc[0].dtc_id,
                                                  link_level="-",
                                                  link_times=1,
                                                  model_version=MODEL_VERSION,
                                                  link_correlation1=link_ie_dtc_correlation1,
                                                  link_correlation2=0,
                                                  link_correlation3=0,
                                                  link_correlation4=0,
                                                  link_correlation5=0,
                                                  )
                    Session.add(ie_dtc_link_info)
                else:
                    print("当前导入的接口异常-DTC关联( {} )信息,数据库中已经存在！".format(ie_dtc_link_add_prequery[0].ie_dtc_link_id))
Session.commit()
print("IE dtc Table 导入完成")

# IE Test Table
cnt = 0
for n, indexs in enumerate(i_test_zone_data.index.tolist()):
    for m, columns in enumerate(i_test_zone_data.columns):
        if n > 2 and m > 2:
            if str(i_test_zone_data.iloc[n, m]) == "[,]" or pd.isna(i_test_zone_data.iloc[n, m]):
                pass
            else:
                cnt += 1
                link_entity_part1 = str(i_test_zone_data.iloc[n, m])[1:-1].split(",")[0]
                link_entity_part2 = str(i_test_zone_data.iloc[n, m])[1:-1].split(",")[1]

                # 获得当前接口异常关联的接口信息
                interface_info_s = Session.query(TInterfaceInfo).filter(
                    TInterfaceInfo.interface_name == i_test_zone_data.iloc[n, 0]).all()
                assert len(interface_info_s) == 1

                # 获得当前关联Test 对应部件信息
                part_info_t = Session.query(TPart).filter(
                    TPart.part_name == i_test_zone_data.iloc[0, m].split("_")[1]).all()
                assert len(part_info_t) == 1

                # 获得当前关联Test信息
                test_info_ie_test = Session.query(TTestResultInfo).filter(
                    and_(TTestResultInfo.test_part_id == part_info_t[0].part_id,
                         TTestResultInfo.test_result_name == i_test_zone_data.iloc[1, m])).all()
                assert len(test_info_ie_test) == 1

                # 获得当前关联接口异常信息
                interface_exception_info_ie_test = Session.query(TInterfaceExceptionInfo).filter(
                    and_(TInterfaceExceptionInfo.interface_id_belong == interface_info_s[0].interface_id,
                         TInterfaceExceptionInfo.ie_description == i_test_zone_data.iloc[n, 1])).all()
                assert len(interface_exception_info_ie_test) == 1

                # 计算关联系数 link_ie_test_correlation1
                link_ie_test_correlation1 = 1 / float(i_test_zone_data.iloc[2, m])

                # 获得关联ID 当ie和Test属于不同部件时，关联ID 按照ie的编号
                ie_test_link_id = interface_info_s[0].interface_id[0:4] + "IT-" + "%06d" % cnt
                # 查询是否重复
                ie_test_link_add_prequery = Session.query(TIeTestLink).filter(
                    TIeTestLink.ie_test_link_id == ie_test_link_id).all()
                if len(ie_test_link_add_prequery) == 0:
                    ie_test_link_info = TIeTestLink(ie_test_link_id=ie_test_link_id,
                                                    ie_id=interface_exception_info_ie_test[0].ie_id,
                                                    test_id=test_info_ie_test[0].test_result_id,
                                                    link_level="-",
                                                    link_times=1,
                                                    model_version=MODEL_VERSION,
                                                    link_correlation1=link_ie_test_correlation1,
                                                    link_correlation2=0,
                                                    link_correlation3=0,
                                                    link_correlation4=0,
                                                    link_correlation5=0,
                                                    )
                    Session.add(ie_test_link_info)
                else:
                    print("当前导入的接口异常-Test 关联( {} )信息,数据库中已经存在！".format(ie_test_link_add_prequery[0].ie_test_link_id))
Session.commit()
print("IE test Table 导入完成")

# IE-in IE-out Table
cnt = 0
for n, indexs in enumerate(interface_in_out_link_zone_data.index.tolist()):
    for m, columns in enumerate(interface_in_out_link_zone_data.columns):
        if n > 2 and m > 2:
            if str(interface_in_out_link_zone_data.iloc[n, m]) == "[,]" or pd.isna(
                    interface_in_out_link_zone_data.iloc[n, m]):
                pass
            else:
                cnt += 1
                link_entity_part1 = str(interface_in_out_link_zone_data.iloc[n, m])[1:-1].split(",")[0]
                link_entity_part2 = str(interface_in_out_link_zone_data.iloc[n, m])[1:-1].split(",")[1]

                # 获得当前输入接口异常关联的接口信息
                interface_info_in = Session.query(TInterfaceInfo).filter(
                    TInterfaceInfo.interface_name == interface_in_out_link_zone_data.iloc[n, 0]).all()
                assert len(interface_info_in) == 1

                # 获得当前输出接口异常关联的接口信息
                interface_info_out = Session.query(TInterfaceInfo).filter(
                    TInterfaceInfo.interface_name == interface_in_out_link_zone_data.iloc[0, m]).all()
                assert len(interface_info_out) == 1

                # # 获得当前关联Test 对应部件信息
                # part_info_t = Session.query(TPart).filter(
                #     TPart.part_name == i_test_zone_data.iloc[0, m].split("_")[1]).all()
                # assert len(part_info_t) == 1
                #
                # # 获得当前关联Test信息
                # test_info_ie_test = Session.query(TTestResultInfo).filter(
                #     and_(TTestResultInfo.test_part_id == part_info_t[0].part_id,
                #          TTestResultInfo.test_result_name == i_test_zone_data.iloc[1, m])).all()
                # assert len(test_info_ie_test) == 1

                # 获得当前输入关联接口异常信息
                interface_exception_info_ie_in = Session.query(TInterfaceExceptionInfo).filter(
                    and_(TInterfaceExceptionInfo.interface_id_belong == interface_info_in[0].interface_id,
                         TInterfaceExceptionInfo.ie_description == interface_in_out_link_zone_data.iloc[n, 1])).all()
                assert len(interface_exception_info_ie_in) == 1

                # 获得当前输出关联接口异常信息
                interface_exception_info_ie_out = Session.query(TInterfaceExceptionInfo).filter(
                    and_(TInterfaceExceptionInfo.interface_id_belong == interface_info_out[0].interface_id,
                         TInterfaceExceptionInfo.ie_description == interface_in_out_link_zone_data.iloc[1, m])).all()
                assert len(interface_exception_info_ie_out) == 1

                # 计算关联系数 link_ie_ie_correlation1
                link_ie_ie_correlation1 = 1

                # 获得关联ID 当Ie in和Ie out属于不同接口时，关联ID 按照Ie in的编号
                ie_ie_link_id = interface_info_in[0].interface_id[0:4] + "II-" + "%06d" % cnt
                # 查询是否重复
                ie_ie_link_add_prequery = Session.query(TIeIeLink).filter(
                    TIeIeLink.ie_ie_link_id == ie_ie_link_id).all()
                if len(ie_ie_link_add_prequery) == 0:
                    ie_ie_link_info = TIeIeLink(ie_ie_link_id=ie_ie_link_id,
                                                ie_i_id=interface_exception_info_ie_in[0].ie_id,
                                                ie_o_id=interface_exception_info_ie_out[0].ie_id,
                                                link_level="-",
                                                link_times=1,
                                                model_version=MODEL_VERSION,
                                                link_correlation1=link_ie_ie_correlation1,
                                                link_correlation2=0,
                                                link_correlation3=0,
                                                link_correlation4=0,
                                                link_correlation5=0,
                                                )
                    Session.add(ie_ie_link_info)
                else:
                    print(
                        "当前导入的接口异常in-接口异常out 关联( {} )信息,数据库中已经存在！".format(ie_ie_link_add_prequery[0].ie_ie_link_id))
Session.commit()
print("IE-in IE-out Table 导入完成")

te = time.time()
print("本次运行使用时间: " + str(te - ts) + "s")
print(" ")
