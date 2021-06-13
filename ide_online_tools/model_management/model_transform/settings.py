
vehicle_config_code = {
    "车辆配置1": "VC1",  # Vehicle Config 1
    "车辆配置2": "VC2",  # Vehicle Config 2
    "车辆配置3": "VC3",  # Vehicle Config 3
    "车辆配置4": "VC4"  # Vehicle Config 4
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
