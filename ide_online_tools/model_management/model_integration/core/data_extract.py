import numpy as np
import pandas as pd
import copy
from sqlalchemy import create_engine
import pickle

vehicle_code = {
    "车辆1": "VH1",  # Vehicle 1
    "车辆2": "VH2",  # Vehicle 2
    "车辆3": "VH3",  # Vehicle 3
    "车辆4": "VH4"  # Vehicle 4

}
# 车辆各个系统编号-三位，英文大写：
sys_code_dict = {
    "热管理系统": "HVC",
    "电池热管理系统": "BHV",
    "车身": "BDC",
    "底盘": "CHS",
    "动力总成": "PWT",
    "排放控制": "SCR",
}
# 车辆各个部件的信息类型编号-二位，英文大写：
part_info_type = {
    "失效模式": "FM",
    "症状": "SY",
    "故障码": "DT",  # DTC
    "测试动作": "TA",  # Test Action
    "测试结果": "TR",  # Test Result
    "维修动作": "CA",  # CA Action
    "维修结果": "CR",  # CA Result
    "接口信息": "II",  # Interface Information
    "接口异常": "IE",  # Interface Exception
    "配置表ID": "CF",  # Config
}
# 生成关联ID的关联类型
link_type_dict = {
    "FmAndSy": "FS",
    "FmAndTest": "FT",
    "FmAndDTC": "FD",
    "FmAndCa": "FC",
    "AlgorithmParameter": "AP"
}


def system_inputBinaryFile(filepath):
    f = open(filepath, 'rb')
    sys = pickle.load(f)
    f.close()
    print("序列化文件读取完成！")
    return sys


# 信息唯一识别码生成器 ：待完善
def uidgenerator(vc="配置1", sys_code="热管理", part_id=1, info_type="失效模式", record_id=1):
    part_id_6b = "%06d" % part_id
    record_id_4b = "%04d" % record_id
    if part_id == 0 and record_id == 0 and info_type == "":
        return "-".join([vehicle_code[vc], sys_code_dict[sys_code]])
    elif part_id != 0 and record_id == 0 and info_type == "":
        return "-".join([vehicle_code[vc], sys_code_dict[sys_code], part_id_6b])
    elif part_id != 0 and record_id == 0 and info_type != "":
        return "-".join([vehicle_code[vc], sys_code_dict[sys_code], part_id_6b, part_info_type[info_type]])
    else:
        return "-".join(
            [vehicle_code[vc], sys_code_dict[sys_code], part_id_6b, part_info_type[info_type], record_id_4b])


# 关联唯一识别码生成器 ：待完善
def linkidgenerator(vc="配置1", link__type="FmAndSy", link_record_id=1):
    link_record_id_6b = "%06d" % link_record_id
    return "-".join([vehicle_code[vc], link_type_dict[link__type], link_record_id_6b])


# 数据库连接
engine = create_engine("mysql+pymysql://root:root@localhost:3306/battery_cooling_system_vali_0304_2?charset=UTF8MB4")

# 系统模型文件加载导入
sys_data = system_inputBinaryFile("./BCOOL0304-1-sys.db")
print("数据载入成功!")

# 读取数据库的表结构和系统BOM文档
dbfilename = "./VDES_table.xlsx"
vdes_bom_filename = "./VDES_BOM_for_battery_cooling_system.xlsx"
dtc_bom_filename = "./DTC_BOM.xlsx"
# 导入车辆配置表
vehicle_bom_data = pd.read_excel(vdes_bom_filename, sheet_name="VDES_BOM")
# 导入DTC列表文件
dtc_bom_data = pd.read_excel(dtc_bom_filename, sheet_name="DTC_BOM")
# 文件读取：读取数据库表结构模板（excel文件格式）
vehicle_config_data = pd.read_excel(dbfilename, sheet_name="vehicle_config_infotable")
account_config_data = pd.read_excel(dbfilename, sheet_name="vehicle_config_infotable")
systems_data = pd.read_excel(dbfilename, sheet_name="systems_infotable")
algorithm_parameter_data = pd.read_excel(dbfilename, sheet_name="algorithm_parameter_table")

parts_data_col = pd.read_excel(dbfilename, sheet_name="parts_infotable")
config_parts_link_data_col = pd.read_excel(dbfilename, sheet_name="config_parts_link_table")

fm_info_data_col = pd.read_excel(dbfilename, sheet_name="FM_infotable")
dtc_info_data_col = pd.read_excel(dbfilename, sheet_name="DTC_infotable")
sy_info_data_col = pd.read_excel(dbfilename, sheet_name="SY_infotable")
test_action_info_data_col = pd.read_excel(dbfilename, sheet_name="Test_action_infotable")
ca_action_info_data_col = pd.read_excel(dbfilename, sheet_name="CA_action_infotable")
ca_result_info_data_col = pd.read_excel(dbfilename, sheet_name="CA_result_infotable")
test_result_info_data_col = pd.read_excel(dbfilename, sheet_name="Test_result_table")
fs_link_data_col = pd.read_excel(dbfilename, sheet_name="FS_table")
f_dtc_link_data_col = pd.read_excel(dbfilename, sheet_name="F_DTC_table")
f_test_link_data_col = pd.read_excel(dbfilename, sheet_name="F_Test_table")
print("文件读入成功")

# 连接数据库并处理数据后导入数据库：

# 部件BOM表导入：parts_infotable 信息处理
sys_num = {}  # 生成某一系统的部件编号
parts_data = pd.DataFrame(np.zeros([vehicle_bom_data.shape[0], len(parts_data_col.columns.tolist())]),
                          columns=parts_data_col.columns.tolist())
config_parts_link_data = pd.DataFrame(
    np.zeros([vehicle_bom_data.shape[0], len(config_parts_link_data_col.columns.tolist())]),
    columns=config_parts_link_data_col.columns.tolist())
for i in vehicle_bom_data.index.tolist():
    if vehicle_bom_data["system_name"][i] in sys_num.keys():
        sys_num[vehicle_bom_data["system_name"][i]] += 1
    else:
        sys_num[vehicle_bom_data["system_name"][i]] = 1
    parts_data.loc[i, "part_table_id"] = i + 1
    parts_data.loc[i, "part_id"] = uidgenerator(vehicle_bom_data["vehicle_config_code"][i],
                                                vehicle_bom_data["system_name"][i],
                                                sys_num[vehicle_bom_data["system_name"][i]], "", 0)
    parts_data.loc[i, "part_name"] = vehicle_bom_data["part_name"][i]
    parts_data.loc[i, "part_description"] = vehicle_bom_data["system_name"][i] + ":" + vehicle_bom_data["part_name"][i]
    parts_data.loc[i, "part_type"] = "外购件"
    parts_data.loc[i, "belongto_sys_id"] = uidgenerator(vehicle_bom_data["vehicle_config_code"][i],
                                                        vehicle_bom_data["system_name"][i], 0, "", 0)
    parts_data.loc[i, "software_version"] = "V0.1"
    # 车型配置和部件的关系表
    config_parts_link_data.loc[i, "config_parts_table_id"] += i + 1
    config_parts_link_data.loc[i, "vehicle_config_code"] = vehicle_code[
        vehicle_bom_data["vehicle_config_code"][i]]
    config_parts_link_data.loc[i, "part_id"] = uidgenerator(vehicle_bom_data["vehicle_config_code"][i],
                                                            vehicle_bom_data["system_name"][i],
                                                            sys_num[vehicle_bom_data["system_name"][i]], "", 0)
    config_parts_link_data.loc[i, "config_parts_id"] = uidgenerator(vehicle_bom_data["vehicle_config_code"][i],
                                                                    vehicle_bom_data["system_name"][i],
                                                                    sys_num[vehicle_bom_data["system_name"][i]],
                                                                    "配置表ID", 0)
print("BOM 生成完成")
# 信息表数据导入
# fm infotable：失效模式信息表导入
fm_times = sys_data.sys_full_cursor["IS"][0] - sys_data.sys_full_cursor["FS"][0] - 1
fm_info_data = pd.DataFrame(np.zeros([fm_times, len(fm_info_data_col.columns.tolist())]),
                            columns=fm_info_data_col.columns.tolist())
fm_zone = [(sys_data.sys_full_cursor["FS"][0] + 1, sys_data.sys_full_cursor["IS"][0]), (0, 3)]
fm_zone_data = sys_data.sysdatatable[0].iloc[fm_zone[0][0]:fm_zone[0][1], 0:3]
fm_num = {}  # 生成某一系统的部件的失效模式编号
for i, index in enumerate(fm_zone_data.index.tolist()):
    if fm_zone_data.loc[index, 0] in fm_num.keys():
        fm_num[fm_zone_data.loc[index, 0]] += 1
    else:
        fm_num[fm_zone_data.loc[index, 0]] = 1
    fm_info_data.loc[i, "FM_info_id"] = i + 1
    fm_info_data.loc[i, "FM_id"] = \
        parts_data["part_id"][parts_data["part_name"] == fm_zone_data.loc[index, 0]].tolist()[0] + "-" + part_info_type[
            "失效模式"] + "-" + "%04d" % fm_num[fm_zone_data.loc[index, 0]]
    fm_info_data.loc[i, "FM_name"] = fm_zone_data.loc[index, 1]
    fm_info_data.loc[i, "FM_f"] = fm_zone_data.loc[index, 2]
    fm_info_data.loc[i, "FM_p"] = 1
    fm_info_data.loc[i, "part_id"] = \
        parts_data["part_id"][parts_data["part_name"] == fm_zone_data.loc[index, 0]].tolist()[0]
    fm_info_data.loc[i, "FM_times"] = 1
print("fm_infotable 生成完成")
# SY table   # DTC table
# 症状和dtc表导入
sy_dtc_test_zone_data = sys_data.sysdatatable[0].iloc[0:2,
                        sys_data.sys_full_cursor["FS"][1] + 1:sys_data.sys_full_cursor["FO"][1]].T
sy_dtc_test_zone_data.columns = ["症状类别", "症状描述"]
sy_zone_data = sy_dtc_test_zone_data[sy_dtc_test_zone_data["症状类别"].str.contains("系统症状|部件症状") == True]
dtc_zone_data = sy_dtc_test_zone_data[sy_dtc_test_zone_data["症状类别"].str.contains("DTC") == True]
# test_zone_data=sy_dtc_test_zone_data[sy_dtc_test_zone_data["症状类别"].str.contains("Test") == True]

dtc_info_data = pd.DataFrame(np.zeros([dtc_zone_data.shape[0], len(dtc_info_data_col.columns.tolist())]),
                             columns=dtc_info_data_col.columns.tolist())

# writer = pd.ExcelWriter("./HVC-DTC-BOM.xlsx", engine='xlsxwriter')
# dtc_zone_data.to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
# writer.save()
# writer.close()

for i, index in enumerate(dtc_zone_data.index.tolist()):
    dtc_info_data.loc[i, "DTC_info_id"] = i + 1
    dtc_info_data.loc[i, "DTC_id"] = "VC3-000-000000-DT-" + "%04d" % (i + 1)
    dtc_info_data.loc[i, "DTC"] = dtc_zone_data.loc[index, "症状类别"].split("_")[1]
    dtc_info_data.loc[i, "DTC_description"] = dtc_zone_data.loc[index, "症状描述"]
    dtc_info_data.loc[i, "DTC_system_id"] = ""
    dtc_info_data.loc[i, "DTC_part_id"] = \
    dtc_bom_data[(dtc_bom_data["PCODE"] == dtc_zone_data.loc[index, "症状类别"].split("_")[1])]["归属控制器"].values.tolist()[0]

sy_info_data = pd.DataFrame(np.zeros([sy_zone_data.shape[0], len(sy_info_data_col.columns.tolist())]),
                            columns=sy_info_data_col.columns.tolist())
sysy_num = {}
for i, index in enumerate(sy_zone_data.index.tolist()):
    if sy_zone_data.loc[index, "症状类别"] in sysy_num.keys():
        sysy_num[sy_zone_data.loc[index, "症状类别"]] += 1
    else:
        sysy_num[sy_zone_data.loc[index, "症状类别"]] = 1
    sy_info_data.loc[i, "SY_info_id"] = i + 1
    if sy_zone_data.loc[index, "症状类别"] == "系统症状":
        sy_info_data.loc[i, "SY_id"] = "VC3-000-000000-SY-" + "%04d" % (sysy_num[sy_zone_data.loc[index, "症状类别"]])
        sy_info_data.loc[i, "SY_level"] = "系统级"
        sy_info_data.loc[i, "SY_part_id"] = ""
    elif "部件症状_" in sy_zone_data.loc[index, "症状类别"]:
        pat_name = sy_zone_data.loc[index, "症状类别"].split("_")[1]
        sy_info_data.loc[i, "SY_id"] = parts_data["part_id"][parts_data["part_name"] == pat_name].tolist()[
                                           0] + "-SY-" + "%04d" % (sysy_num[sy_zone_data.loc[index, "症状类别"]])
        sy_info_data.loc[i, "SY_level"] = "部件级"
        sy_info_data.loc[i, "SY_part_id"] = parts_data["part_id"][parts_data["part_name"] == pat_name].tolist()[0]
        # print(" ")
    sy_info_data.loc[i, "SY_sys_id"] = ""

    sy_info_data.loc[i, "SY_desciption"] = sy_zone_data.loc[index, "症状描述"]
    sy_info_data.loc[i, "SY_times"] = "1"
    sy_info_data.loc[i, "SY_p"] = "1"
print("sy_infotable test_infotable 生成完成")

# test action table  # ca action table
test_action_zone_data = pd.DataFrame()
ca_action_zone_data = pd.DataFrame()
for part_name, sheets in sys_data.parts_dict.items():
    test_action_zone_data = pd.concat([test_action_zone_data, sheets.sheets_list["06Test"].data.loc[1:, :]],
                                      ignore_index=True)
    ca_action_zone_data = pd.concat(
        [ca_action_zone_data, sheets.sheets_list["04Corrective Action-Cost"].data.loc[1:, :]], ignore_index=True)
test_action_zone_data.columns = ["Test_content", "Test_time_h", "Test_cost_yuan", "part_bom_id", "part_name",
                                 "Test_instruction", "Test_complexity", "Test_type"]
ca_action_zone_data.columns = ["CA_name", "CA_time_h", "CA_cost_yuan", "part_bom_id", "part_name", "CA_instruction"]

test_action_info_data = pd.DataFrame(
    np.zeros([test_action_zone_data.shape[0], len(test_action_info_data_col.columns.tolist())]),
    columns=test_action_info_data_col.columns.tolist())
test_action_num = {}
for i, index in enumerate(test_action_zone_data.index.tolist()):
    part_id = parts_data["part_id"][parts_data["part_name"] == test_action_zone_data.loc[index, "part_name"]].tolist()[
        0]
    if test_action_zone_data.loc[index, "part_name"] in test_action_num.keys():
        test_action_num[test_action_zone_data.loc[index, "part_name"]] += 1
    else:
        test_action_num[test_action_zone_data.loc[index, "part_name"]] = 1
    test_action_info_data.loc[i, "Test_action_info_id"] = i + 1
    test_action_info_data.loc[i, "Test_action_id"] = part_id + "-" + part_info_type["测试动作"] + "-" + "%04d" % (
    test_action_num[test_action_zone_data.loc[index, "part_name"]])
    test_action_info_data.loc[i, "Test_content"] = test_action_zone_data.loc[index, "Test_content"]
    test_action_info_data.loc[i, "Test_instruction"] = ""  # test_action_zone_data.loc[index, "Test_instruction"]  #计划从表格中读取，实际中先赋值为空字符串
    test_action_info_data.loc[i, "Test_system_id"] = part_id[0:-7]
    test_action_info_data.loc[i, "Test_part_id"] = part_id
    test_action_info_data.loc[i, "Test_cost_yuan"] = test_action_zone_data.loc[index, "Test_cost_yuan"]
    test_action_info_data.loc[i, "Test_time_h"] = test_action_zone_data.loc[index, "Test_time_h"]
    test_action_info_data.loc[i, "Test_type"] = test_action_zone_data.loc[index, "Test_type"]
    test_action_info_data.loc[i, "Test_complexity"] = test_action_zone_data.loc[index, "Test_complexity"]
    test_action_info_data.loc[i, "Test_instruction_doc_link"] = ""
    test_action_info_data.loc[i, "Test_instruction_video_link"] = ""
    test_action_info_data.loc[i, "Test_equipment"] = ""

ca_action_info_data = pd.DataFrame(
    np.zeros([ca_action_zone_data.shape[0], len(ca_action_info_data_col.columns.tolist())]),
    columns=ca_action_info_data_col.columns.tolist())
ca_action_num = {}

for i, index in enumerate(ca_action_zone_data.index.tolist()):
    part_id = parts_data["part_id"][parts_data["part_name"] == ca_action_zone_data.loc[index, "part_name"]].tolist()[0]
    if ca_action_zone_data.loc[index, "part_name"] in ca_action_num.keys():
        ca_action_num[ca_action_zone_data.loc[index, "part_name"]] += 1
    else:
        ca_action_num[ca_action_zone_data.loc[index, "part_name"]] = 1

    ca_action_info_data.loc[i, "CA_info_id"] = i + 1
    ca_action_info_data.loc[i, "CA_action_id"] = part_id + "-" + part_info_type["维修动作"] + "-" + "%04d" % (
    ca_action_num[ca_action_zone_data.loc[index, "part_name"]])
    ca_action_info_data.loc[i, "CA_name"] = ca_action_zone_data.loc[index, "CA_name"]
    ca_action_info_data.loc[i, "CA_time_h"] = ca_action_zone_data.loc[index, "CA_time_h"]
    ca_action_info_data.loc[i, "CA_cost_yuan"] = ca_action_zone_data.loc[index, "CA_cost_yuan"]
    ca_action_info_data.loc[i, "CA_part_id"] = part_id
    ca_action_info_data.loc[i, "CA_system_id"] = part_id[0:-7]
    ca_action_info_data.loc[i, "CA_instruction"] = "" #  ca_action_zone_data.loc[index, "CA_instruction"]   #计划从表格中读取，目前先修改为空字符串
    ca_action_info_data.loc[i, "CA_type"] = ""
    ca_action_info_data.loc[i, "CA_complexity"] = ""
    ca_action_info_data.loc[i, "CA_instruction_doc_link"] = ""
    ca_action_info_data.loc[i, "CA_instruction_video_link"] = ""
    ca_action_info_data.loc[i, "CA_equipment"] = ""
print("test_action_table, ca action table, 生成完成")

# ca result table
test_result_zone_data = pd.DataFrame(
    columns=["part_name", "test_ex_name", "link_value", "Test_action_name", "Test_result_check"])
# test_result_zone_data.columns = ["part_name","fm_name","link_value","ca_action_name"]
ca_result_zone_data = pd.DataFrame(columns=["part_name", "fm_name", "link_value", "ca_action_name"])
# ca_result_zone_data.columns = ["part_name","fm_name","link_value","ca_action_name"]
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
                test_result_zone_data = test_result_zone_data.append(pd.DataFrame(
                    {"part_name": part_name, "test_ex_name": index_test_ex, "link_value": "X",
                     "Test_action_name": index_test, "Test_result_check": data_tmp2.iloc[nn, 0]},
                    index=[0]), ignore_index=True)

ca_result_info_data = pd.DataFrame(
    np.zeros([ca_result_zone_data.shape[0], len(ca_result_info_data_col.columns.tolist())]),
    columns=ca_result_info_data_col.columns.tolist())
test_result_info_data = pd.DataFrame(
    np.zeros([test_result_zone_data.shape[0], len(test_result_info_data_col.columns.tolist())]),
    columns=test_result_info_data_col.columns.tolist())

# 导入 # ca result table    # test result table
ca_result_num = {}
test_result_num = {}

for i, index in enumerate(ca_result_zone_data.index.tolist()):
    part_id = parts_data["part_id"][parts_data["part_name"] == ca_result_zone_data.loc[index, "part_name"]].tolist()[0]
    if ca_result_zone_data.loc[index, "part_name"] in ca_result_num.keys():
        ca_result_num[ca_result_zone_data.loc[index, "part_name"]] += 1
    else:
        ca_result_num[ca_result_zone_data.loc[index, "part_name"]] = 1

    ca_result_info_data.loc[i, "CA_result_id"] = i + 1
    # zzz = (fm_info_data["part_id"] == part_id) & (fm_info_data["FM_name"] == ca_result_zone_data.loc[index, "fm_name"])
    # xxx = fm_info_data[zzz]["FM_id"].tolist()[0]
    # 报错一般为查询时候没查询到，检查模型excel
    ca_result_info_data.loc[i, "CA_FM_link_id"] = part_id + "-" + part_info_type["维修结果"] + "-" + "%04d" % (
    ca_result_num[ca_result_zone_data.loc[index, "part_name"]])
    ca_result_info_data.loc[i, "CA_impact_FM_id"] = fm_info_data[
        (fm_info_data["part_id"] == part_id) & (fm_info_data["FM_name"] == ca_result_zone_data.loc[index, "fm_name"])][
        "FM_id"].tolist()[0]
    ca_result_info_data.loc[i, "CA_action_id"] = ca_action_info_data[(ca_action_info_data["CA_part_id"] == part_id) & (
                ca_action_info_data["CA_name"] == ca_result_zone_data.loc[index, "ca_action_name"])][
        "CA_action_id"].values.tolist()[0]

for i, index in enumerate(test_result_zone_data.index.tolist()):
    part_id = parts_data["part_id"][parts_data["part_name"] == test_result_zone_data.loc[index, "part_name"]].tolist()[
        0]
    if test_result_zone_data.loc[index, "part_name"] in test_result_num.keys():
        test_result_num[test_result_zone_data.loc[index, "part_name"]] += 1
    else:
        test_result_num[test_result_zone_data.loc[index, "part_name"]] = 1

    test_result_info_data.loc[i, "Test_result_info_id"] = i + 1
    test_result_info_data.loc[i, "Test_result_id"] = part_id + "-" + part_info_type["测试结果"] + "-" + "%04d" % (
    test_result_num[test_result_zone_data.loc[index, "part_name"]])
    test_result_info_data.loc[i, "Test_result_name"] = test_result_zone_data.loc[index, "test_ex_name"]
    test_result_info_data.loc[i, "Test_result_check"] = test_result_zone_data.loc[index, "Test_result_check"]
    # ccc = (test_action_info_data["Test_part_id"] == part_id) & (test_action_info_data["Test_content"] == test_result_zone_data.loc[index, "Test_action_name"])
    test_result_info_data.loc[i, "Test_action_id"] = test_action_info_data[
        (test_action_info_data["Test_part_id"] == part_id) & (
                    test_action_info_data["Test_content"] == test_result_zone_data.loc[index, "Test_action_name"])][
        "Test_action_id"].values.tolist()[0]
    test_result_info_data.loc[i, "Test_system_id"] = part_id[0:-7]
    test_result_info_data.loc[i, "Test_part_id"] = part_id

print("test_result_table, ca result table, 生成完成")
# 关联表导入

reasoner_link_zone_data = sys_data.sysdatatable[0].iloc[0:sys_data.sys_full_cursor["IO"][0],
                          0:sys_data.sys_full_cursor["IO"][1]].T
reasoner_link_zone_data.columns = [str(x) for x in range(0, len(reasoner_link_zone_data.columns))]
fs_zone_data = reasoner_link_zone_data[reasoner_link_zone_data["0"].str.contains("症状类别|系统编号|系统名称|系统症状|部件症状_") == True].T
f_dtc_zone_data = reasoner_link_zone_data[reasoner_link_zone_data["0"].str.contains("症状类别|系统编号|系统名称|DTC_") == True].T
f_test_zone_data = reasoner_link_zone_data[reasoner_link_zone_data["0"].str.contains("症状类别|系统编号|系统名称|Test_") == True].T

# FS table
f_deny = 0.5
ooo = 0
fs_link_data = pd.DataFrame(columns=fs_link_data_col.columns.tolist())
for nnn, index_fs in enumerate(fs_zone_data.index.tolist()):
    for mmm, col_fs in enumerate(fs_zone_data.columns):
        # 增加否定系数后修改
        if nnn > 2 and mmm > 2:
            if str(fs_zone_data.iloc[nnn, mmm]) == "[,]" or pd.isna(fs_zone_data.iloc[nnn, mmm]):
                pass
            else:
                xxx1 = str(fs_zone_data.iloc[nnn, mmm])[1:-1].split(",")[0]
                xxx2 = str(fs_zone_data.iloc[nnn, mmm])[1:-1].split(",")[1]


                part_id_fm = \
                    parts_data["part_id"][parts_data["part_name"] == fs_zone_data.iloc[nnn, 0]].tolist()[0]
                ooo += 1
                if xxx2 == "1":
                    link_FS_correlation2 = 0
                if xxx2 == "X":
                    link_FS_correlation2 = 1 - f_deny
                if xxx2 == "0":
                    link_FS_correlation2 = 1

                if str(fs_zone_data.iloc[0, mmm]) == "系统症状":
                    SY_id_temp = \
                    sy_info_data["SY_id"][(sy_info_data["SY_desciption"] == fs_zone_data.iloc[1, mmm])].tolist()[0]
                elif "部件症状_" in str(fs_zone_data.iloc[0, mmm]):
                    part_id_sy = \
                        parts_data["part_id"][parts_data["part_name"] == fs_zone_data.iloc[0, mmm].split("_")[1]].tolist()[
                            0]
                    SY_id_temp = \
                        sy_info_data["SY_id"][(sy_info_data["SY_desciption"] == fs_zone_data.iloc[1, mmm]) & (
                                    sy_info_data["SY_part_id"] == part_id_sy)].tolist()[0]
                fs_link_data = fs_link_data.append(
                    pd.DataFrame({"link_FS_info_id": ooo,
                                  "link_FS_id": part_id_fm[0:4] + link_type_dict["FmAndSy"] + "-" + "%06d" % ooo,
                                  "FM_id": fm_info_data["FM_id"][(fm_info_data["FM_name"] == fs_zone_data.iloc[nnn, 1]) & (
                                              fm_info_data["part_id"] == part_id_fm)].tolist()[0],
                                  "SY_id": SY_id_temp,
                                  "link_FS_level": str(fs_zone_data.iloc[nnn, mmm]),
                                  "link_FS_correlation1": float(fs_zone_data.iloc[nnn, 2]) / float(
                                      fs_zone_data.iloc[2, mmm]),
                                  "link_FS_correlation2": link_FS_correlation2,
                                  "link_FS_times": "1"}, index=[0]), ignore_index=True)


print("FS table  生成完成")
# F DTC table
f_deny = 0.5
ooo = 0
f_dtc_link_data = pd.DataFrame(columns=f_dtc_link_data_col.columns.tolist())
for nnn, index_fs in enumerate(f_dtc_zone_data.index.tolist()):
    for mmm, col_fs in enumerate(f_dtc_zone_data.columns):
        if nnn > 2 and mmm > 2:
            if str(f_dtc_zone_data.iloc[nnn, mmm]) == "[,]" or pd.isna(f_dtc_zone_data.iloc[nnn, mmm]):
                pass
            else:
                xxx1 = str(f_dtc_zone_data.iloc[nnn, mmm])[1:-1].split(",")[0]
                xxx2 = str(f_dtc_zone_data.iloc[nnn, mmm])[1:-1].split(",")[1]

                part_id = \
                    parts_data["part_id"][parts_data["part_name"] == f_dtc_zone_data.iloc[nnn, 0]].tolist()[0]
                ooo += 1

                if xxx2 == "1":
                    link_F_DTC_correlation2 = 0
                if xxx2 == "X":
                    link_F_DTC_correlation2 = 1 - f_deny
                if xxx2 == "0":
                    link_F_DTC_correlation2 = 1


                f_dtc_link_data = f_dtc_link_data.append(
                    pd.DataFrame({"link_F_DTC_info_id": ooo,
                                  "link_F_DTC_id": part_id[0:4] + link_type_dict["FmAndDTC"] + "-" + "%06d" % ooo,
                                  "FM_id": fm_info_data["FM_id"][
                                      (fm_info_data["FM_name"] == f_dtc_zone_data.iloc[nnn, 1]) & (
                                                  fm_info_data["part_id"] == part_id)].tolist()[0],
                                  "DTC_id": dtc_info_data["DTC_id"][
                                      (dtc_info_data["DTC_description"] == f_dtc_zone_data.iloc[1, mmm]) & (
                                                  dtc_info_data["DTC"] == f_dtc_zone_data.iloc[0, mmm].split("_")[
                                              1])].tolist()[0],
                                  "link_F_DTC_level": str(f_dtc_zone_data.iloc[nnn, mmm]),
                                  "link_F_DTC_correlation1": float(f_dtc_zone_data.iloc[nnn, 2]) / float(
                                      f_dtc_zone_data.iloc[2, mmm]),
                                  "link_F_DTC_correlation2": link_F_DTC_correlation2,
                                  "link_F_DTC_times": "1"}, index=[0]), ignore_index=True)

print("F DTC table  生成完成")

# F Test table

f_deny = 0.5
ooo = 0
f_test_link_data = pd.DataFrame(columns=f_test_link_data_col.columns.tolist())
for nnn, index_fs in enumerate(f_test_zone_data.index.tolist()):
    for mmm, col_fs in enumerate(f_test_zone_data.columns):
        if nnn > 2 and mmm > 2:
            if str(f_test_zone_data.iloc[nnn, mmm]) == "[,]" or pd.isna(f_test_zone_data.iloc[nnn, mmm]):
                pass
            else:
                xxx1 = str(f_test_zone_data.iloc[nnn, mmm])[1:-1].split(",")[0]
                xxx2 = str(f_test_zone_data.iloc[nnn, mmm])[1:-1].split(",")[1]


                part_id_fm = \
                    parts_data["part_id"][parts_data["part_name"] == f_test_zone_data.iloc[nnn, 0]].tolist()[0]
                part_id_test = \
                    parts_data["part_id"][parts_data["part_name"] == f_test_zone_data.iloc[0, mmm].split("_")[1]].tolist()[
                        0]
                ooo += 1
                if xxx2 == "1":
                    link_F_Test_correlation2 = 0
                if xxx2 == "X":
                    link_F_Test_correlation2 = 1 - f_deny
                if xxx2 == "0":
                    link_F_Test_correlation2 = 1

                f_test_link_data = f_test_link_data.append(
                    pd.DataFrame({"link_F_Test_info_id": ooo,
                                  "link_F_Test_id": part_id[0:4] + link_type_dict["FmAndTest"] + "-" + "%06d" % ooo,
                                  "FM_id": fm_info_data["FM_id"][
                                      (fm_info_data["FM_name"] == f_test_zone_data.iloc[nnn, 1]) & (
                                                  fm_info_data["part_id"] == part_id_fm)].tolist()[0],
                                  "Test_result_id": test_result_info_data["Test_result_id"][
                                      (test_result_info_data["Test_result_name"] == f_test_zone_data.iloc[1, mmm]) & (
                                                  test_result_info_data["Test_part_id"] == part_id_test)].tolist()[0],
                                  "link_F_Test_level": str(f_test_zone_data.iloc[nnn, mmm]),
                                  "link_F_Test_correlation1": float(f_test_zone_data.iloc[nnn, 2]) / float(
                                      f_test_zone_data.iloc[2, mmm]),
                                  "link_F_Test_correlation2": link_F_Test_correlation2,
                                  "link_F_Test_times": "1"}, index=[0]), ignore_index=True)

print("F Test table 生成完成")
print(" ")

# 数据读取完成后写入数据库

# # # 读取excel 直接导入数据库
vehicle_config_data.to_sql("vehicle_config_infotable", con=engine, if_exists="append", index=False)
systems_data.to_sql("systems_infotable", con=engine, if_exists="append", index=False)
algorithm_parameter_data.to_sql("algorithm_parameter_table", con=engine, if_exists="append", index=False)
# #
# # 生成后的数据写入数据库
parts_data.to_sql("parts_infotable", con=engine, if_exists="append", index=False)
config_parts_link_data.to_sql("config_parts_link_table", con=engine, if_exists="append", index=False)
fm_info_data.to_sql("fm_infotable", con=engine, if_exists="append", index=False)
dtc_info_data.to_sql("dtc_infotable", con=engine, if_exists="append", index=False)
sy_info_data.to_sql("sy_infotable", con=engine, if_exists="append", index=False)
test_action_info_data.to_sql("test_action_infotable", con=engine, if_exists="append", index=False)
ca_action_info_data.to_sql("ca_action_infotable", con=engine, if_exists="append", index=False)
ca_result_info_data.to_sql("ca_result_infotable", con=engine, if_exists="append", index=False)
test_result_info_data.to_sql("test_result_table", con=engine, if_exists="append", index=False)
fs_link_data.to_sql("fs_table", con=engine, if_exists="append", index=False)
f_dtc_link_data.to_sql("f_dtc_table", con=engine, if_exists="append", index=False)
f_test_link_data.to_sql("f_test_table", con=engine, if_exists="append", index=False)
print("表格导入数据库完成")
print(" ")
