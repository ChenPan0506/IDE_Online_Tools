# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class AccountTable(db.Model):
    __tablename__ = 'account_table'

    account_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20, 'utf8_general_ci'), nullable=False)
    password = db.Column(db.String(20, 'utf8_general_ci'), nullable=False)
    role = db.Column(db.String(255))
    description = db.Column(db.String(255))
    status = db.Column(db.String(32), nullable=False)


class TAlgorithmParameter(db.Model):
    __tablename__ = 't_algorithm_parameter'

    table_id = db.Column(db.Integer, primary_key=True)
    al_param_set_id = db.Column(db.String(22), nullable=False, index=True)
    al_param_set_name = db.Column(db.String(255), nullable=False)
    al_param_set_data = db.Column(db.Text, nullable=False)
    al_param_set_version = db.Column(db.String(255), nullable=False)
    al_param_type = db.Column(db.String(255), nullable=False)
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    update_time = db.Column(db.DateTime, server_default=db.FetchedValue())


class TCaActionInfo(db.Model):
    __tablename__ = 't_ca_action_info'

    table_id = db.Column(db.Integer, primary_key=True)
    ca_action_id = db.Column(db.String(22), nullable=False, info='维修动作ID')
    ca_name = db.Column(db.Text, nullable=False, info='维修名称')
    ca_time_h = db.Column(db.Float, nullable=False, info='维修工时')
    ca_cost_yuan = db.Column(db.Float, nullable=False)
    ca_part_id = db.Column(db.String(22), nullable=False)
    ca_system_id = db.Column(db.String(22), nullable=False)
    ca_instruction = db.Column(db.Text, nullable=False)
    ca_type = db.Column(db.String(16), nullable=False)
    ca_complexity = db.Column(db.Float, nullable=False)
    ca_instruction_doc_link = db.Column(db.Text)
    ca_instruction_video_link = db.Column(db.Text)
    ca_equipment = db.Column(db.Text)
    model_version = db.Column(db.String(22), nullable=False, index=True)


class TConfigLink(db.Model):
    __tablename__ = 't_config_link'

    table_id = db.Column(db.Integer, primary_key=True, info='表id')
    config_part_link_id = db.Column(db.String(22), nullable=False, info='配置-部件关系id')
    config_id = db.Column(db.ForeignKey('t_vehicle_config.vehicle_config_id'), nullable=False, index=True, info='配置id')
    part_id = db.Column(db.ForeignKey('t_part.part_id'), nullable=False, index=True, info='部件id')
    creat_time = db.Column(db.DateTime, nullable=False, info='创建时间')
    creat_user = db.Column(db.Text, info='创建者')

    config = db.relationship('TVehicleConfig', primaryjoin='TConfigLink.config_id == TVehicleConfig.vehicle_config_id',
                             backref='t_config_links')
    part = db.relationship('TPart', primaryjoin='TConfigLink.part_id == TPart.part_id', backref='t_config_links')


class TConfigModelLink(db.Model):
    __tablename__ = 't_config_model_link'
    __table_args__ = (
        db.Index('vehicle_type_id', 'vehicle_type_id', 'vehicle_config_id', 'vehicle_model_id', 'al_param_id'),
    )

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    config_model_link_id = db.Column(db.String(22), info='配置模型关联ID')
    vehicle_type_id = db.Column(db.ForeignKey('t_vehicle_type.vehicle_type_id', ondelete='CASCADE', onupdate='CASCADE'),
                                nullable=False, index=True, info='车型ID')
    vehicle_config_id = db.Column(
        db.ForeignKey('t_vehicle_config.vehicle_config_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
        index=True, info='配置ID')
    vehicle_model_id = db.Column(
        db.ForeignKey('t_vehicle_model.vehicle_model_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
        index=True, info='模型ID')
    al_param_id = db.Column(
        db.ForeignKey('t_algorithm_parameter.al_param_set_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
        index=True)
    release_time = db.Column(db.DateTime, nullable=False, info='发布时间')
    description = db.Column(db.Text, nullable=False, info='配置描述')
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue(), info='创建时间')
    state = db.Column(db.Text, nullable=False, info='状态')
    operation = db.Column(db.Text, nullable=False, info='操作')

    al_param = db.relationship('TAlgorithmParameter',
                               primaryjoin='TConfigModelLink.al_param_id == TAlgorithmParameter.al_param_set_id',
                               backref='t_config_model_links')
    vehicle_config = db.relationship('TVehicleConfig',
                                     primaryjoin='TConfigModelLink.vehicle_config_id == TVehicleConfig.vehicle_config_id',
                                     backref='t_config_model_links')
    vehicle_model = db.relationship('TVehicleModel',
                                    primaryjoin='TConfigModelLink.vehicle_model_id == TVehicleModel.vehicle_model_id',
                                    backref='t_config_model_links')
    vehicle_type = db.relationship('TVehicleType',
                                   primaryjoin='TConfigModelLink.vehicle_type_id == TVehicleType.vehicle_type_id',
                                   backref='t_config_model_links')


class TDtcInfo(db.Model):
    __tablename__ = 't_dtc_info'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    dtc_id = db.Column(db.String(22), nullable=False, info='DTC  ID')
    dtc = db.Column(db.String(16), nullable=False, info='DTC  码')
    dtc_description = db.Column(db.Text, nullable=False, info='DTC描述')
    dtc_node = db.Column(db.Text, nullable=False, info='DTC所属节点')
    dtc_confirm_condition = db.Column(db.String(16), nullable=False, info='DTC 确认条件')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')


class TDtcNodeInfo(db.Model):
    __tablename__ = 't_dtc_node_info'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    node_id = db.Column(db.String(22), nullable=False, info='节点  ID')
    node_name = db.Column(db.String(16), nullable=False, info='节点名')
    node_description = db.Column(db.Text, nullable=False, info='节点描述')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')


class TFmCaLink(db.Model):
    __tablename__ = 't_fm_ca_link'

    table_id = db.Column(db.Integer, primary_key=True, info='表id')
    fm_ca_link_id = db.Column(db.String(22), nullable=False, info='失效模式和维修措施关联关系ID')
    fm_id = db.Column(db.String(22), nullable=False, info='失效模式ID')
    ca_id = db.Column(db.String(22), nullable=False, info='维修措施ID')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')
    other = db.Column(db.Text, nullable=False, info='备注')


class TFmDtcLink(db.Model):
    __tablename__ = 't_fm_dtc_link'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    fm_dtc_link_id = db.Column(db.String(22), nullable=False, info='失效模式和dtc关联ID')
    fm_id = db.Column(db.String(22), nullable=False, info='失效模式ID')
    dtc_id = db.Column(db.String(22), nullable=False, info='dtc  ID')
    link_level = db.Column(db.String(16), nullable=False, info='关联级别')
    link_times = db.Column(db.Integer, nullable=False, info='关联次数')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')
    link_correlation1 = db.Column(db.Float, nullable=False, info='关联系数1（正向系数）')
    link_correlation2 = db.Column(db.Float, nullable=False, info='关联系数1（否定系数）')
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)


class TFmIeLink(db.Model):
    __tablename__ = 't_fm_ie_link'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    fm_ie_link_id = db.Column(db.String(22), nullable=False, info='失效模式和接口异常关联ID')
    fm_id = db.Column(db.String(22), nullable=False, info='失效模式ID')
    ie_id = db.Column(db.String(22), nullable=False, info='接口异常 ID')
    link_level = db.Column(db.String(16), nullable=False, info='关联级别')
    link_times = db.Column(db.Integer, nullable=False, info='关联次数')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')
    link_correlation1 = db.Column(db.Float, nullable=False, info='关联系数1（正向系数）')
    link_correlation2 = db.Column(db.Float, nullable=False, info='关联系数1（否定系数）')
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)


class TFmInfo(db.Model):
    __tablename__ = 't_fm_info'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    fm_id = db.Column(db.String(22), nullable=False, unique=True, info='失效模式ID')
    fm_name = db.Column(db.Text, nullable=False, info='失效模式名称')
    fm_f = db.Column(db.Float, nullable=False, info='失效模式初始关联系数')
    fm_p = db.Column(db.Float, info='失效模式概率（预留）')
    part_id = db.Column(db.String(22), nullable=False, info='失效模式所属部件')
    fm_times = db.Column(db.Integer, info='失效模式频度')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')


class TFmSyLink(db.Model):
    __tablename__ = 't_fm_sy_link'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    fm_sy_link_id = db.Column(db.String(22), nullable=False, info='失效模式和症状关联ID')
    fm_id = db.Column(db.String(22), nullable=False, info='失效模式ID')
    sy_id = db.Column(db.String(22), nullable=False, info='症状ID')
    link_level = db.Column(db.String(16), nullable=False, info='关联级别')
    link_times = db.Column(db.Integer, nullable=False, info='关联次数')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')
    link_correlation1 = db.Column(db.Float, nullable=False, info='关联系数1（正向系数）')
    link_correlation2 = db.Column(db.Float, nullable=False, info='关联系数1（否定系数）')
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)


class TFmTestLink(db.Model):
    __tablename__ = 't_fm_test_link'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    fm_test_link_id = db.Column(db.String(22), nullable=False, info='失效模式和test关联ID')
    fm_id = db.Column(db.String(22), nullable=False, info='失效模式ID')
    test_id = db.Column(db.String(22), nullable=False, info='test  ID')
    link_level = db.Column(db.String(16), nullable=False, info='关联级别')
    link_times = db.Column(db.Integer, nullable=False, info='关联次数')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')
    link_correlation1 = db.Column(db.Float, nullable=False, info='关联系数1（正向系数）')
    link_correlation2 = db.Column(db.Float, nullable=False, info='关联系数1（否定系数）')
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)


class THealthIndicatorInfo(db.Model):
    __tablename__ = 't_health_indicator_info'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    hi_id = db.Column(db.String(22), nullable=False, info='健康指标 ID')
    hi_name = db.Column(db.Text, nullable=False, info='健康指标名称')
    hi_description = db.Column(db.Text, nullable=False, info='健康指标描述')
    hi_unit = db.Column(db.String(16), nullable=False, info='健康指标单位')
    hi_refresh_rate = db.Column(db.Integer, nullable=False, info='健康指标更新频率')
    hi_state = db.Column(db.Integer, nullable=False, info='健康指标状态')
    sys_id_belong = db.Column(db.String(22), nullable=False, info='所属系统')
    part_id_belong = db.Column(db.String(22), nullable=False, info='所属部件')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')


class THiIeLink(db.Model):
    __tablename__ = 't_hi_ie_link'

    table_id = db.Column(db.Integer, primary_key=True, info='表id')
    hi_ie_link_id = db.Column(db.String(22), nullable=False, info='健康指标和接口异常关联关系ID')
    hi_id = db.Column(db.String(22), nullable=False, info='健康指标ID')
    ie_id = db.Column(db.String(22), nullable=False, info='接口异常ID')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')
    other = db.Column(db.Text, nullable=False, info='备注')


class TIeDtcLink(db.Model):
    __tablename__ = 't_ie_dtc_link'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    ie_dtc_link_id = db.Column(db.String(22), nullable=False, info='接口异常和dtc关联ID')
    ie_id = db.Column(db.String(22), nullable=False, info='接口异常ID')
    dtc_id = db.Column(db.String(22), nullable=False, info='dtc  ID')
    link_level = db.Column(db.String(16), nullable=False, info='关联级别')
    link_times = db.Column(db.Integer, nullable=False, info='关联次数')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')
    link_correlation1 = db.Column(db.Float, nullable=False, info='关联系数1（正向系数）')
    link_correlation2 = db.Column(db.Float, nullable=False, info='关联系数1（否定系数）')
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)


class TIeIeLink(db.Model):
    __tablename__ = 't_ie_ie_link'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    ie_ie_link_id = db.Column(db.String(22), nullable=False, info='接口异常和接口异常关联ID')
    ie_i_id = db.Column(db.String(22), nullable=False, info='输入接口异常 ID')
    ie_o_id = db.Column(db.String(22), nullable=False, info='输出接口异常 ID')
    link_level = db.Column(db.String(16), nullable=False, info='关联级别')
    link_times = db.Column(db.Integer, nullable=False, info='关联次数')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')
    link_correlation1 = db.Column(db.Float, nullable=False, info='关联系数1（正向系数）')
    link_correlation2 = db.Column(db.Float, nullable=False, info='关联系数1（否定系数）')
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)


class TIeSyLink(db.Model):
    __tablename__ = 't_ie_sy_link'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    ie_sy_link_id = db.Column(db.String(22), nullable=False, info='接口异常和症状关联ID')
    ie_id = db.Column(db.String(22), nullable=False, info='接口异常ID')
    sy_id = db.Column(db.String(22), nullable=False, info='症状ID')
    link_level = db.Column(db.String(16), nullable=False, info='关联级别')
    link_times = db.Column(db.Integer, nullable=False, info='关联次数')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')
    link_correlation1 = db.Column(db.Float, nullable=False, info='关联系数1（正向系数）')
    link_correlation2 = db.Column(db.Float, nullable=False, info='关联系数1（否定系数）')
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)


class TIeTestLink(db.Model):
    __tablename__ = 't_ie_test_link'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    ie_test_link_id = db.Column(db.String(22), nullable=False, info='接口异常和test关联ID')
    ie_id = db.Column(db.String(22), nullable=False, info='接口异常ID')
    test_id = db.Column(db.String(22), nullable=False, info='test  ID')
    link_level = db.Column(db.String(16), nullable=False, info='关联级别')
    link_times = db.Column(db.Integer, nullable=False, info='关联次数')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')
    link_correlation1 = db.Column(db.Float, nullable=False, info='关联系数1（正向系数）')
    link_correlation2 = db.Column(db.Float, nullable=False, info='关联系数1（否定系数）')
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)


class TInterfaceExceptionInfo(db.Model):
    __tablename__ = 't_interface_exception_info'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    ie_id = db.Column(db.String(22), nullable=False, info='失效模式ID')
    ie_description = db.Column(db.Text, nullable=False, info='失效模式名称')
    ie_cause = db.Column(db.Text, nullable=False, info='失效模式初始关联系数')
    ie_influence = db.Column(db.Text, nullable=False, info='失效模式概率（预留）')
    interface_id_belong = db.Column(db.String(22), nullable=False, info='失效模式所属部件')
    ie_state = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='接口异常状态')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')


class TInterfaceInfo(db.Model):
    __tablename__ = 't_interface_info'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    interface_id = db.Column(db.String(22), nullable=False, info='接口 ID')
    interface_name = db.Column(db.Text, nullable=False, info='接口名称')
    interface_description = db.Column(db.Text, nullable=False, info='接口描述')
    interface_type = db.Column(db.String(16), nullable=False, info='接口类型')
    interface_property = db.Column(db.Text, nullable=False, info='接口属性')
    interface_dirction = db.Column(db.Integer, nullable=False, info='接口方向')
    interface_connect_state = db.Column(db.Integer, nullable=False, info='接口连接状态')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')


class TInterfaceTypeInfo(db.Model):
    __tablename__ = 't_interface_type_info'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    interface_type_id = db.Column(db.String(22), nullable=False, info='接口 ID')
    interface_type_name = db.Column(db.Text, nullable=False, info='接口名称')
    interface_type_description = db.Column(db.Text, nullable=False, info='接口描述')
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')


class TPart(db.Model):
    __tablename__ = 't_part'

    table_id = db.Column(db.Integer, primary_key=True, info='表id')
    part_id = db.Column(db.String(14), nullable=False, unique=True, info='部件id')
    bom_id = db.Column(db.Text, info='BOM表id')
    part_name = db.Column(db.String(255), nullable=False, info='部件名称')
    part_description = db.Column(db.String(255), info='部件描述')
    part_type = db.Column(db.String(255), info='部件类型')
    sys_id_belong = db.Column(db.ForeignKey('t_system.system_id'), nullable=False, index=True, info='所属系统')
    software_version = db.Column(db.Text, nullable=False, info='软件版本')
    part_producer = db.Column(db.Text, info='生产厂家')

    t_system = db.relationship('TSystem', primaryjoin='TPart.sys_id_belong == TSystem.system_id', backref='t_parts')


class TSymptomInfo(db.Model):
    __tablename__ = 't_symptom_info'

    table_id = db.Column(db.Integer, primary_key=True, info='表id')
    sy_id = db.Column(db.String(22), nullable=False, server_default=db.FetchedValue(), info='症状id')
    sy_level = db.Column(db.Text, nullable=False, info='症状级别')
    sy_description = db.Column(db.Text, nullable=False, info='症状描述')
    sy_sys_id = db.Column(db.String(7), nullable=False, server_default=db.FetchedValue(), info='症状所属系统')
    sy_part_id = db.Column(db.String(14), nullable=False, server_default=db.FetchedValue(), info='症状所属部件')
    sy_times = db.Column(db.Integer, nullable=False, info='症状发生频次')
    sy_p = db.Column(db.Float, nullable=False, info='症状发生概率')
    model_version = db.Column(db.String(22), nullable=False, index=True, server_default=db.FetchedValue(),
                              info='模型版本编号')


class TSystem(db.Model):
    __tablename__ = 't_system'

    table_id = db.Column(db.Integer, primary_key=True, info='表id')
    system_id = db.Column(db.String(7), nullable=False, unique=True, info='系统ID')
    system_name = db.Column(db.Text, nullable=False, info='系统名称')
    system_description = db.Column(db.Text, info='系统描述')
    system_type = db.Column(db.Text, nullable=False, info='系统类型')
    vehicle_id_belong = db.Column(db.ForeignKey('t_vehicle.vehicle_id'), nullable=False, index=True, info='所属车辆ID')
    system_producer = db.Column(db.Text, info='生产厂家')
    software_version = db.Column(db.Text, nullable=False, info='软件版本')

    t_vehicle = db.relationship('TVehicle', primaryjoin='TSystem.vehicle_id_belong == TVehicle.vehicle_id',
                                backref='t_systems')


class TTestActionInfo(db.Model):
    __tablename__ = 't_test_action_info'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    test_action_id = db.Column(db.String(22), nullable=False, info='测试动作ID')
    test_action_content = db.Column(db.Text, nullable=False, info='测试内容')
    test_system_id = db.Column(db.String(22), nullable=False, info='系统id')
    test_part_id = db.Column(db.String(22), nullable=False, info='部件ID')
    test_cost_yuan = db.Column(db.Float, nullable=False, info='成本')
    test_time_h = db.Column(db.Float, nullable=False, info='工时')
    test_type = db.Column(db.String(16), nullable=False, info='测试类型')
    test_complexity = db.Column(db.Float, nullable=False, info='测试复杂度')
    test_instruction_doc_link = db.Column(db.Text, info='测试文档指导')
    test_instruction_video_link = db.Column(db.Text, info='测试视频指导')
    test_equipment = db.Column(db.Text, info='测试设备')
    model_version = db.Column(db.String(22), nullable=False, info='模型版本')


class TTestResultInfo(db.Model):
    __tablename__ = 't_test_result_info'

    table_id = db.Column(db.Integer, primary_key=True, info='表id')
    test_result_id = db.Column(db.String(22), nullable=False, info='测试结果ID')
    test_result_name = db.Column(db.Text, nullable=False, info='测试名称ID')
    test_result_check = db.Column(db.Integer, nullable=False, info='测试结果判定')
    test_action_id = db.Column(db.String(22), nullable=False, info='对应测试动作ID')
    test_system_id = db.Column(db.String(22), nullable=False, info='所属系统')
    connect_to_ie = db.Column(db.Integer, nullable=False)
    test_part_id = db.Column(db.String(22), nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True, info='模型版本')


class TUserOperationLog(db.Model):
    __tablename__ = 't_user_operation_log'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    cache_id = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='本次缓存ID')
    save_time = db.Column(db.DateTime, server_default=db.FetchedValue(), info='保存时间')
    vehicle_type_name = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='车辆类型名称')
    vehicle_config_name = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='车辆配置名称')
    vehicle_model_version = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='模型版本')
    algorithm_version = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='算法版本')
    vin = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='车辆VIN号')
    user_name = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='登录用户名')
    operate_log_data = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='操作日志数据')
    submit_phase = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='提交阶段（中间提交/完成后提交）')
    submit_timestamp = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='提交时间')
    submit_type = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='提交类型（增量/全量）')
    vehicle_infomation = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='车辆信息')
    vehicle_type_match = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='匹配的车辆类型')
    vehicle_dtc = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='发生的DTC信息')
    vehicle_dtc_count = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='本次推理发生的DTC个数')
    user_input_sy_text = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='用户输入的症状描述')
    input_times_count = db.Column(db.Integer, nullable=False, info='用户输入的次数')
    sy_confirm_result = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='确认发生的症状')
    sy_confirm_times_count = db.Column(db.Integer, nullable=False, info='确认发生的症状个数')
    test_items = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='测试项目')
    test_times_conut = db.Column(db.Integer, nullable=False, info='测试次数')
    ca_items = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='维修项目')
    ca_times_count = db.Column(db.Integer, nullable=False, info='维修项目个数')
    ca_result = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='维修结果')
    fm_list_with_score_final = db.Column(db.String(255, 'utf8_general_ci'), nullable=False, info='最终的失效模式列表（包含推荐系数）')
    advice_response_text = db.Column(db.String(255, 'utf8_general_ci'), info='用户输入的其他建议')


class TVehicle(db.Model):
    __tablename__ = 't_vehicle'

    table_id = db.Column(db.Integer, primary_key=True, info='表id')
    vehicle_id = db.Column(db.String(7), nullable=False, unique=True, info='车辆id')
    vehicle_brand = db.Column(db.Text, nullable=False, info='车辆品牌')
    vehicle_name = db.Column(db.Text, nullable=False, info='车辆名称')
    vehicle_type = db.Column(db.Text, nullable=False, info='车辆类型')
    vehicle_config_id = db.Column(db.String(22), nullable=False, info='车辆配置ID')
    vehicle_comment = db.Column(db.Text, info='车辆介绍')


class TVehicleConfig(db.Model):
    __tablename__ = 't_vehicle_config'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    vehicle_config_id = db.Column(db.String(22), nullable=False, unique=True, info='车辆配置ID')
    vehicle_config_name = db.Column(db.Text, nullable=False, info='车辆配置名称')
    vehicle_config_description = db.Column(db.Text, nullable=False, info='车辆配置详细描述')
    vehicle_type_id_belong = db.Column(
        db.ForeignKey('t_vehicle_type.vehicle_type_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
        index=True, info='所属配置')
    modify_time = db.Column(db.DateTime, server_default=db.FetchedValue(), info='修改时间')
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue(), info='创建时间')
    create_user = db.Column(db.Text, nullable=False, info='创建人')

    t_vehicle_type = db.relationship('TVehicleType',
                                     primaryjoin='TVehicleConfig.vehicle_type_id_belong == TVehicleType.vehicle_type_id',
                                     backref='t_vehicle_configs')


class TVehicleModel(db.Model):
    __tablename__ = 't_vehicle_model'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    vehicle_model_id = db.Column(db.String(22), nullable=False, unique=True, info='模型编号')
    version_code = db.Column(db.String(22), nullable=False, info='模型版本编号')
    vehicle_type_id = db.Column(db.ForeignKey('t_vehicle_type.vehicle_type_id', ondelete='CASCADE', onupdate='CASCADE'),
                                nullable=False, index=True, info='车型编号')
    vehicle_config_id = db.Column(
        db.ForeignKey('t_vehicle_config.vehicle_config_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
        index=True, info='配置编号')
    vehicle_model_name = db.Column(db.Text, nullable=False, info='模型名称')
    release_time = db.Column(db.DateTime, nullable=False, info='发布时间')
    import_time = db.Column(db.DateTime, server_default=db.FetchedValue(), info='导入时间')
    modify_time = db.Column(db.DateTime, server_default=db.FetchedValue(), info='修改时间')
    create_user = db.Column(db.Text, nullable=False)

    # vehicle_config = db.relationship('TVehicleConfig',
    #                                  primaryjoin='TVehicleModel.vehicle_config_id == TVehicleConfig.vehicle_config_id',
    #                                  backref='t_vehicle_models')
    # vehicle_type = db.relationship('TVehicleType',
    #                                primaryjoin='TVehicleModel.vehicle_type_id == TVehicleType.vehicle_type_id',
    #                                backref='t_vehicle_models')


class TVehicleType(db.Model):
    __tablename__ = 't_vehicle_type'

    table_id = db.Column(db.Integer, primary_key=True, info='表ID')
    vehicle_type_id = db.Column(db.String(22), nullable=False, unique=True, info='车型编号ID')
    vin_re = db.Column(db.Text, nullable=False, info='vin规则')
    brand_name = db.Column(db.Text, nullable=False, info='品牌名称')
    vehicle_type_name = db.Column(db.Text, nullable=False, info='车型名称')
    create_user = db.Column(db.Text, nullable=False, info='创建人')
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue(), info='创建时间')
    modify_time = db.Column(db.DateTime, server_default=db.FetchedValue(), info='修改时间')
