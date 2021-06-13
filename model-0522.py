# coding: utf-8
from sqlalchemy import CHAR, Column, DateTime, Float, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.mysql import CHAR, INTEGER, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class AccountTable(Base):
    __tablename__ = 'account_table'

    account_id = Column(INTEGER(11), primary_key=True)
    username = Column(VARCHAR(20), nullable=False)
    password = Column(CHAR(20), nullable=False)
    role = Column(String(255))
    description = Column(String(255))
    status = Column(CHAR(32), nullable=False)


class TAlgorithmParameter(Base):
    __tablename__ = 't_algorithm_parameter'

    table_id = Column(INTEGER(11), primary_key=True)
    al_param_set_id = Column(CHAR(22), nullable=False, index=True)
    al_param_set_name = Column(String(255), nullable=False)
    al_param_set_data = Column(Text, nullable=False)
    al_param_set_version = Column(String(255), nullable=False)
    al_param_type = Column(String(255), nullable=False)
    create_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class TCaActionInfo(Base):
    __tablename__ = 't_ca_action_info'

    table_id = Column(INTEGER(11), primary_key=True)
    ca_action_id = Column(CHAR(22), nullable=False, comment='维修动作ID')
    ca_name = Column(Text, nullable=False, comment='维修名称')
    ca_time_h = Column(Float, nullable=False, comment='维修工时')
    ca_cost_yuan = Column(Float, nullable=False)
    ca_part_id = Column(CHAR(22), nullable=False)
    ca_system_id = Column(CHAR(22), nullable=False)
    ca_instruction = Column(Text, nullable=False)
    ca_type = Column(CHAR(16), nullable=False)
    ca_complexity = Column(Float, nullable=False)
    ca_instruction_doc_link = Column(Text)
    ca_instruction_video_link = Column(Text)
    ca_equipment = Column(Text)
    model_version = Column(CHAR(22), nullable=False, index=True)


class TDtcInfo(Base):
    __tablename__ = 't_dtc_info'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    dtc_id = Column(CHAR(22), nullable=False, comment='DTC  ID')
    dtc = Column(CHAR(16), nullable=False, comment='DTC  码')
    dtc_description = Column(Text, nullable=False, comment='DTC描述')
    dtc_node = Column(Text, nullable=False, comment='DTC所属节点')
    dtc_confirm_condition = Column(CHAR(16), nullable=False, comment='DTC 确认条件')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')


class TDtcNodeInfo(Base):
    __tablename__ = 't_dtc_node_info'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    node_id = Column(CHAR(22), nullable=False, comment='节点  ID')
    node_name = Column(CHAR(16), nullable=False, comment='节点名')
    node_description = Column(Text, nullable=False, comment='节点描述')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')


class TFmCaLink(Base):
    __tablename__ = 't_fm_ca_link'

    table_id = Column(INTEGER(11), primary_key=True, comment='表id')
    fm_ca_link_id = Column(CHAR(22), nullable=False, comment='失效模式和维修措施关联关系ID')
    fm_id = Column(CHAR(22), nullable=False, comment='失效模式ID')
    ca_id = Column(CHAR(22), nullable=False, comment='维修措施ID')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')
    other = Column(Text, nullable=False, comment='备注')


class TFmDtcLink(Base):
    __tablename__ = 't_fm_dtc_link'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    fm_dtc_link_id = Column(CHAR(22), nullable=False, comment='失效模式和dtc关联ID')
    fm_id = Column(CHAR(22), nullable=False, comment='失效模式ID')
    dtc_id = Column(CHAR(22), nullable=False, comment='dtc  ID')
    link_level = Column(String(16), nullable=False, comment='关联级别')
    link_times = Column(INTEGER(11), nullable=False, comment='关联次数')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')
    link_correlation1 = Column(Float, nullable=False, comment='关联系数1（正向系数）')
    link_correlation2 = Column(Float, nullable=False, comment='关联系数1（否定系数）')
    link_correlation3 = Column(Float, nullable=False)
    link_correlation4 = Column(Float, nullable=False)
    link_correlation5 = Column(Float, nullable=False)


class TFmIeLink(Base):
    __tablename__ = 't_fm_ie_link'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    fm_ie_link_id = Column(CHAR(22), nullable=False, comment='失效模式和接口异常关联ID')
    fm_id = Column(CHAR(22), nullable=False, comment='失效模式ID')
    ie_id = Column(CHAR(22), nullable=False, comment='接口异常 ID')
    link_level = Column(String(16), nullable=False, comment='关联级别')
    link_times = Column(INTEGER(11), nullable=False, comment='关联次数')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')
    link_correlation1 = Column(Float, nullable=False, comment='关联系数1（正向系数）')
    link_correlation2 = Column(Float, nullable=False, comment='关联系数1（否定系数）')
    link_correlation3 = Column(Float, nullable=False)
    link_correlation4 = Column(Float, nullable=False)
    link_correlation5 = Column(Float, nullable=False)


class TFmInfo(Base):
    __tablename__ = 't_fm_info'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    fm_id = Column(CHAR(22), nullable=False, unique=True, comment='失效模式ID')
    fm_name = Column(Text, nullable=False, comment='失效模式名称')
    fm_f = Column(Float, nullable=False, comment='失效模式初始关联系数')
    fm_p = Column(Float, comment='失效模式概率（预留）')
    part_id = Column(CHAR(22), nullable=False, comment='失效模式所属部件')
    fm_times = Column(INTEGER(11), comment='失效模式频度')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')


class TFmSyLink(Base):
    __tablename__ = 't_fm_sy_link'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    fm_sy_link_id = Column(CHAR(22), nullable=False, comment='失效模式和症状关联ID')
    fm_id = Column(CHAR(22), nullable=False, comment='失效模式ID')
    sy_id = Column(CHAR(22), nullable=False, comment='症状ID')
    link_level = Column(String(16), nullable=False, comment='关联级别')
    link_times = Column(INTEGER(11), nullable=False, comment='关联次数')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')
    link_correlation1 = Column(Float, nullable=False, comment='关联系数1（正向系数）')
    link_correlation2 = Column(Float, nullable=False, comment='关联系数1（否定系数）')
    link_correlation3 = Column(Float, nullable=False)
    link_correlation4 = Column(Float, nullable=False)
    link_correlation5 = Column(Float, nullable=False)


class TFmTestLink(Base):
    __tablename__ = 't_fm_test_link'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    fm_test_link_id = Column(CHAR(22), nullable=False, comment='失效模式和test关联ID')
    fm_id = Column(CHAR(22), nullable=False, comment='失效模式ID')
    test_id = Column(CHAR(22), nullable=False, comment='test  ID')
    link_level = Column(String(16), nullable=False, comment='关联级别')
    link_times = Column(INTEGER(11), nullable=False, comment='关联次数')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')
    link_correlation1 = Column(Float, nullable=False, comment='关联系数1（正向系数）')
    link_correlation2 = Column(Float, nullable=False, comment='关联系数1（否定系数）')
    link_correlation3 = Column(Float, nullable=False)
    link_correlation4 = Column(Float, nullable=False)
    link_correlation5 = Column(Float, nullable=False)


class THealthIndicatorInfo(Base):
    __tablename__ = 't_health_indicator_info'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    hi_id = Column(CHAR(22), nullable=False, comment='健康指标 ID')
    hi_name = Column(Text, nullable=False, comment='健康指标名称')
    hi_description = Column(Text, nullable=False, comment='健康指标描述')
    hi_unit = Column(CHAR(16), nullable=False, comment='健康指标单位')
    hi_refresh_rate = Column(INTEGER(11), nullable=False, comment='健康指标更新频率')
    hi_state = Column(INTEGER(11), nullable=False, comment='健康指标状态')
    sys_id_belong = Column(CHAR(22), nullable=False, comment='所属系统')
    part_id_belong = Column(CHAR(22), nullable=False, comment='所属部件')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')


class THiIeLink(Base):
    __tablename__ = 't_hi_ie_link'

    table_id = Column(INTEGER(11), primary_key=True, comment='表id')
    hi_ie_link_id = Column(CHAR(22), nullable=False, comment='健康指标和接口异常关联关系ID')
    hi_id = Column(CHAR(22), nullable=False, comment='健康指标ID')
    ie_id = Column(CHAR(22), nullable=False, comment='接口异常ID')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')
    other = Column(Text, nullable=False, comment='备注')


class TIeDtcLink(Base):
    __tablename__ = 't_ie_dtc_link'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    ie_dtc_link_id = Column(CHAR(22), nullable=False, comment='接口异常和dtc关联ID')
    ie_id = Column(CHAR(22), nullable=False, comment='接口异常ID')
    dtc_id = Column(CHAR(22), nullable=False, comment='dtc  ID')
    link_level = Column(String(16), nullable=False, comment='关联级别')
    link_times = Column(INTEGER(11), nullable=False, comment='关联次数')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')
    link_correlation1 = Column(Float, nullable=False, comment='关联系数1（正向系数）')
    link_correlation2 = Column(Float, nullable=False, comment='关联系数1（否定系数）')
    link_correlation3 = Column(Float, nullable=False)
    link_correlation4 = Column(Float, nullable=False)
    link_correlation5 = Column(Float, nullable=False)


class TIeIeLink(Base):
    __tablename__ = 't_ie_ie_link'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    ie_ie_link_id = Column(CHAR(22), nullable=False, comment='接口异常和接口异常关联ID')
    ie_i_id = Column(CHAR(22), nullable=False, comment='输入接口异常 ID')
    ie_o_id = Column(CHAR(22), nullable=False, comment='输出接口异常 ID')
    link_level = Column(String(16), nullable=False, comment='关联级别')
    link_times = Column(INTEGER(11), nullable=False, comment='关联次数')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')
    link_correlation1 = Column(Float, nullable=False, comment='关联系数1（正向系数）')
    link_correlation2 = Column(Float, nullable=False, comment='关联系数1（否定系数）')
    link_correlation3 = Column(Float, nullable=False)
    link_correlation4 = Column(Float, nullable=False)
    link_correlation5 = Column(Float, nullable=False)


class TIeSyLink(Base):
    __tablename__ = 't_ie_sy_link'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    ie_sy_link_id = Column(CHAR(22), nullable=False, comment='接口异常和症状关联ID')
    ie_id = Column(CHAR(22), nullable=False, comment='接口异常ID')
    sy_id = Column(CHAR(22), nullable=False, comment='症状ID')
    link_level = Column(String(16), nullable=False, comment='关联级别')
    link_times = Column(INTEGER(11), nullable=False, comment='关联次数')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')
    link_correlation1 = Column(Float, nullable=False, comment='关联系数1（正向系数）')
    link_correlation2 = Column(Float, nullable=False, comment='关联系数1（否定系数）')
    link_correlation3 = Column(Float, nullable=False)
    link_correlation4 = Column(Float, nullable=False)
    link_correlation5 = Column(Float, nullable=False)


class TIeTestLink(Base):
    __tablename__ = 't_ie_test_link'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    ie_test_link_id = Column(CHAR(22), nullable=False, comment='接口异常和test关联ID')
    ie_id = Column(CHAR(22), nullable=False, comment='接口异常ID')
    test_id = Column(CHAR(22), nullable=False, comment='test  ID')
    link_level = Column(String(16), nullable=False, comment='关联级别')
    link_times = Column(INTEGER(11), nullable=False, comment='关联次数')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')
    link_correlation1 = Column(Float, nullable=False, comment='关联系数1（正向系数）')
    link_correlation2 = Column(Float, nullable=False, comment='关联系数1（否定系数）')
    link_correlation3 = Column(Float, nullable=False)
    link_correlation4 = Column(Float, nullable=False)
    link_correlation5 = Column(Float, nullable=False)


class TInterfaceExceptionInfo(Base):
    __tablename__ = 't_interface_exception_info'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    ie_id = Column(CHAR(22), nullable=False, comment='失效模式ID')
    ie_description = Column(Text, nullable=False, comment='失效模式名称')
    ie_cause = Column(Text, nullable=False, comment='失效模式初始关联系数')
    ie_influence = Column(Text, nullable=False, comment='失效模式概率（预留）')
    interface_id_belong = Column(CHAR(22), nullable=False, comment='失效模式所属部件')
    ie_state = Column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='接口异常状态')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')


class TInterfaceInfo(Base):
    __tablename__ = 't_interface_info'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    interface_id = Column(CHAR(22), nullable=False, comment='接口 ID')
    interface_name = Column(Text, nullable=False, comment='接口名称')
    interface_description = Column(Text, nullable=False, comment='接口描述')
    interface_type = Column(CHAR(16), nullable=False, comment='接口类型')
    interface_property = Column(Text, nullable=False, comment='接口属性')
    interface_dirction = Column(INTEGER(11), nullable=False, comment='接口方向')
    interface_connect_state = Column(INTEGER(11), nullable=False, comment='接口连接状态')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')


class TInterfaceTypeInfo(Base):
    __tablename__ = 't_interface_type_info'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    interface_type_id = Column(CHAR(22), nullable=False, comment='接口 ID')
    interface_type_name = Column(Text, nullable=False, comment='接口名称')
    interface_type_description = Column(Text, nullable=False, comment='接口描述')
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')


class TSymptomInfo(Base):
    __tablename__ = 't_symptom_info'

    table_id = Column(INTEGER(11), primary_key=True, comment='表id')
    sy_id = Column(CHAR(22), nullable=False, server_default=text("''"), comment='症状id')
    sy_level = Column(Text, nullable=False, comment='症状级别')
    sy_description = Column(Text, nullable=False, comment='症状描述')
    sy_sys_id = Column(CHAR(7), nullable=False, server_default=text("''"), comment='症状所属系统')
    sy_part_id = Column(CHAR(14), nullable=False, server_default=text("''"), comment='症状所属部件')
    sy_times = Column(INTEGER(11), nullable=False, comment='症状发生频次')
    sy_p = Column(Float, nullable=False, comment='症状发生概率')
    model_version = Column(CHAR(22), nullable=False, index=True, server_default=text("''"), comment='模型版本编号')


class TTestActionInfo(Base):
    __tablename__ = 't_test_action_info'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    test_action_id = Column(CHAR(22), nullable=False, comment='测试动作ID')
    test_action_content = Column(Text, nullable=False, comment='测试内容')
    test_system_id = Column(CHAR(22), nullable=False, comment='系统id')
    test_part_id = Column(CHAR(22), nullable=False, comment='部件ID')
    test_cost_yuan = Column(Float, nullable=False, comment='成本')
    test_time_h = Column(Float, nullable=False, comment='工时')
    test_type = Column(CHAR(16), nullable=False, comment='测试类型')
    test_complexity = Column(Float, nullable=False, comment='测试复杂度')
    test_instruction_doc_link = Column(Text, comment='测试文档指导')
    test_instruction_video_link = Column(Text, comment='测试视频指导')
    test_equipment = Column(Text, comment='测试设备')
    model_version = Column(CHAR(22), nullable=False, comment='模型版本')


class TTestResultInfo(Base):
    __tablename__ = 't_test_result_info'

    table_id = Column(INTEGER(11), primary_key=True, comment='表id')
    test_result_id = Column(CHAR(22), nullable=False, comment='测试结果ID')
    test_result_name = Column(Text, nullable=False, comment='测试名称ID')
    test_result_check = Column(INTEGER(11), nullable=False, comment='测试结果判定')
    test_action_id = Column(CHAR(22), nullable=False, comment='对应测试动作ID')
    test_system_id = Column(CHAR(22), nullable=False, comment='所属系统')
    connect_to_ie = Column(INTEGER(11), nullable=False)
    test_part_id = Column(CHAR(22), nullable=False)
    model_version = Column(CHAR(22), nullable=False, index=True, comment='模型版本')


class TUserOperationLog(Base):
    __tablename__ = 't_user_operation_log'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    cache_id = Column(VARCHAR(255), nullable=False, comment='本次缓存ID')
    save_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='保存时间')
    vehicle_type_name = Column(VARCHAR(255), nullable=False, comment='车辆类型名称')
    vehicle_config_name = Column(VARCHAR(255), nullable=False, comment='车辆配置名称')
    vehicle_model_version = Column(VARCHAR(255), nullable=False, comment='模型版本')
    algorithm_version = Column(VARCHAR(255), nullable=False, comment='算法版本')
    vin = Column(VARCHAR(255), nullable=False, comment='车辆VIN号')
    user_name = Column(VARCHAR(255), nullable=False, comment='登录用户名')
    operate_log_data = Column(VARCHAR(255), nullable=False, comment='操作日志数据')
    submit_phase = Column(VARCHAR(255), nullable=False, comment='提交阶段（中间提交/完成后提交）')
    submit_timestamp = Column(VARCHAR(255), nullable=False, comment='提交时间')
    submit_type = Column(VARCHAR(255), nullable=False, comment='提交类型（增量/全量）')
    vehicle_infomation = Column(VARCHAR(255), nullable=False, comment='车辆信息')
    vehicle_type_match = Column(VARCHAR(255), nullable=False, comment='匹配的车辆类型')
    vehicle_dtc = Column(VARCHAR(255), nullable=False, comment='发生的DTC信息')
    vehicle_dtc_count = Column(VARCHAR(255), nullable=False, comment='本次推理发生的DTC个数')
    user_input_sy_text = Column(VARCHAR(255), nullable=False, comment='用户输入的症状描述')
    input_times_count = Column(INTEGER(11), nullable=False, comment='用户输入的次数')
    sy_confirm_result = Column(VARCHAR(255), nullable=False, comment='确认发生的症状')
    sy_confirm_times_count = Column(INTEGER(11), nullable=False, comment='确认发生的症状个数')
    test_items = Column(VARCHAR(255), nullable=False, comment='测试项目')
    test_times_conut = Column(INTEGER(11), nullable=False, comment='测试次数')
    ca_items = Column(VARCHAR(255), nullable=False, comment='维修项目')
    ca_times_count = Column(INTEGER(11), nullable=False, comment='维修项目个数')
    ca_result = Column(VARCHAR(255), nullable=False, comment='维修结果')
    fm_list_with_score_final = Column(VARCHAR(255), nullable=False, comment='最终的失效模式列表（包含推荐系数）')
    advice_response_text = Column(VARCHAR(255), comment='用户输入的其他建议')


class TVehicle(Base):
    __tablename__ = 't_vehicle'

    table_id = Column(INTEGER(11), primary_key=True, comment='表id')
    vehicle_id = Column(CHAR(7), nullable=False, unique=True, comment='车辆id')
    vehicle_brand = Column(Text, nullable=False, comment='车辆品牌')
    vehicle_name = Column(Text, nullable=False, comment='车辆名称')
    vehicle_type = Column(Text, nullable=False, comment='车辆类型')
    vehicle_config_id = Column(CHAR(22), nullable=False, comment='车辆配置ID')
    vehicle_comment = Column(Text, comment='车辆介绍')


class TVehicleType(Base):
    __tablename__ = 't_vehicle_type'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    vehicle_type_id = Column(CHAR(22), nullable=False, unique=True, comment='车型编号ID')
    vin_re = Column(Text, nullable=False, comment='vin规则')
    brand_name = Column(Text, nullable=False, comment='品牌名称')
    vehicle_type_name = Column(Text, nullable=False, comment='车型名称')
    create_user = Column(Text, nullable=False, comment='创建人')
    create_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    modify_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='修改时间')


class TSystem(Base):
    __tablename__ = 't_system'

    table_id = Column(INTEGER(11), primary_key=True, comment='表id')
    system_id = Column(CHAR(7), nullable=False, unique=True, comment='系统ID')
    system_name = Column(Text, nullable=False, comment='系统名称')
    system_description = Column(Text, comment='系统描述')
    system_type = Column(Text, nullable=False, comment='系统类型')
    vehicle_id_belong = Column(ForeignKey('t_vehicle.vehicle_id'), nullable=False, index=True, comment='所属车辆ID')
    system_producer = Column(Text, comment='生产厂家')
    software_version = Column(Text, nullable=False, comment='软件版本')

    t_vehicle = relationship('TVehicle')


class TVehicleConfig(Base):
    __tablename__ = 't_vehicle_config'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    vehicle_config_id = Column(CHAR(22), nullable=False, unique=True, comment='车辆配置ID')
    vehicle_config_name = Column(Text, nullable=False, comment='车辆配置名称')
    vehicle_config_description = Column(Text, nullable=False, comment='车辆配置详细描述')
    vehicle_type_id_belong = Column(ForeignKey('t_vehicle_type.vehicle_type_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='所属配置')
    modify_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='修改时间')
    create_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    create_user = Column(Text, nullable=False, comment='创建人')

    t_vehicle_type = relationship('TVehicleType')


class TPart(Base):
    __tablename__ = 't_part'

    table_id = Column(INTEGER(11), primary_key=True, comment='表id')
    part_id = Column(CHAR(14), nullable=False, unique=True, comment='部件id')
    bom_id = Column(Text, comment='BOM表id')
    part_name = Column(String(255), nullable=False, comment='部件名称')
    part_description = Column(String(255), comment='部件描述')
    part_type = Column(String(255), comment='部件类型')
    sys_id_belong = Column(ForeignKey('t_system.system_id'), nullable=False, index=True, comment='所属系统')
    software_version = Column(Text, nullable=False, comment='软件版本')
    part_producer = Column(Text, comment='生产厂家')

    t_system = relationship('TSystem')


class TVehicleModel(Base):
    __tablename__ = 't_vehicle_model'

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    vehicle_model_id = Column(CHAR(22), nullable=False, unique=True, comment='模型编号')
    version_code = Column(CHAR(22), nullable=False, comment='模型版本编号')
    vehicle_type_id = Column(ForeignKey('t_vehicle_type.vehicle_type_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='车型编号')
    vehicle_config_id = Column(ForeignKey('t_vehicle_config.vehicle_config_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='配置编号')
    vehicle_model_name = Column(Text, nullable=False, comment='模型名称')
    release_time = Column(DateTime, nullable=False, comment='发布时间')
    import_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='导入时间')
    modify_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='修改时间')
    create_user = Column(Text, nullable=False)

    vehicle_config = relationship('TVehicleConfig')
    vehicle_type = relationship('TVehicleType')


class TConfigLink(Base):
    __tablename__ = 't_config_link'

    table_id = Column(INTEGER(11), primary_key=True, comment='表id')
    config_part_link_id = Column(CHAR(22), nullable=False, comment='配置-部件关系id')
    config_id = Column(ForeignKey('t_vehicle_config.vehicle_config_id'), nullable=False, index=True, comment='配置id')
    part_id = Column(ForeignKey('t_part.part_id'), nullable=False, index=True, comment='部件id')
    creat_time = Column(DateTime, nullable=False, comment='创建时间')
    creat_user = Column(Text, comment='创建者')

    config = relationship('TVehicleConfig')
    part = relationship('TPart')


class TConfigModelLink(Base):
    __tablename__ = 't_config_model_link'
    __table_args__ = (
        Index('vehicle_type_id', 'vehicle_type_id', 'vehicle_config_id', 'vehicle_model_id', 'al_param_id', unique=True),
    )

    table_id = Column(INTEGER(11), primary_key=True, comment='表ID')
    config_model_link_id = Column(CHAR(22), comment='配置模型关联ID')
    vehicle_type_id = Column(ForeignKey('t_vehicle_type.vehicle_type_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='车型ID')
    vehicle_config_id = Column(ForeignKey('t_vehicle_config.vehicle_config_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='配置ID')
    vehicle_model_id = Column(ForeignKey('t_vehicle_model.vehicle_model_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='模型ID')
    al_param_id = Column(ForeignKey('t_algorithm_parameter.al_param_set_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    release_time = Column(DateTime, nullable=False, comment='发布时间')
    description = Column(Text, nullable=False, comment='配置描述')
    create_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    state = Column(Text, nullable=False, comment='状态')
    operation = Column(Text, nullable=False, comment='操作')

    al_param = relationship('TAlgorithmParameter')
    vehicle_config = relationship('TVehicleConfig')
    vehicle_model = relationship('TVehicleModel')
    vehicle_type = relationship('TVehicleType')
