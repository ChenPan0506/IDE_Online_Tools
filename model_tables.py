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
    ca_action_id = db.Column(db.String(22), nullable=False)
    ca_name = db.Column(db.Text, nullable=False)
    ca_time_h = db.Column(db.Float, nullable=False)
    ca_cost_yuan = db.Column(db.Float, nullable=False)
    ca_part_id = db.Column(db.String(22), nullable=False)
    ca_part_name = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
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

    table_id = db.Column(db.Integer, primary_key=True)
    config_part_link_id = db.Column(db.String(22), nullable=False)
    config_id = db.Column(db.ForeignKey('t_vehicle_config.vehicle_config_id'), nullable=False, index=True)
    part_id = db.Column(db.ForeignKey('t_part.part_id'), nullable=False, index=True)
    creat_time = db.Column(db.DateTime, nullable=False)
    creat_user = db.Column(db.Text)

    config = db.relationship('TVehicleConfig', primaryjoin='TConfigLink.config_id == TVehicleConfig.vehicle_config_id', backref='t_config_links')
    part = db.relationship('TPart', primaryjoin='TConfigLink.part_id == TPart.part_id', backref='t_config_links')



class TConfigModelLink(db.Model):
    __tablename__ = 't_config_model_link'
    __table_args__ = (
        db.Index('vehicle_type_id', 'vehicle_type_id', 'vehicle_config_id', 'vehicle_model_id', 'al_param_id'),
    )

    table_id = db.Column(db.Integer, primary_key=True)
    config_model_link_id = db.Column(db.String(22))
    vehicle_type_id = db.Column(db.ForeignKey('t_vehicle_type.vehicle_type_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    vehicle_config_id = db.Column(db.ForeignKey('t_vehicle_config.vehicle_config_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    vehicle_model_id = db.Column(db.ForeignKey('t_vehicle_model.vehicle_model_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    al_param_id = db.Column(db.ForeignKey('t_algorithm_parameter.al_param_set_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    release_time = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    state = db.Column(db.Text, nullable=False)
    operation = db.Column(db.Text, nullable=False)

    al_param = db.relationship('TAlgorithmParameter', primaryjoin='TConfigModelLink.al_param_id == TAlgorithmParameter.al_param_set_id', backref='t_config_model_links')
    vehicle_config = db.relationship('TVehicleConfig', primaryjoin='TConfigModelLink.vehicle_config_id == TVehicleConfig.vehicle_config_id', backref='t_config_model_links')
    vehicle_model = db.relationship('TVehicleModel', primaryjoin='TConfigModelLink.vehicle_model_id == TVehicleModel.vehicle_model_id', backref='t_config_model_links')
    vehicle_type = db.relationship('TVehicleType', primaryjoin='TConfigModelLink.vehicle_type_id == TVehicleType.vehicle_type_id', backref='t_config_model_links')



class TDtcInfo(db.Model):
    __tablename__ = 't_dtc_info'

    table_id = db.Column(db.Integer, primary_key=True)
    dtc_id = db.Column(db.String(22), nullable=False, index=True)
    dtc = db.Column(db.String(16), nullable=False)
    dtc_description = db.Column(db.Text, nullable=False)
    dtc_node = db.Column(db.Text, nullable=False)
    dtc_confirm_condition = db.Column(db.String(16), nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)



class TDtcNodeInfo(db.Model):
    __tablename__ = 't_dtc_node_info'

    table_id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.String(22), nullable=False)
    node_name = db.Column(db.String(16), nullable=False)
    node_description = db.Column(db.Text, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)



class TFmCaLink(db.Model):
    __tablename__ = 't_fm_ca_link'

    table_id = db.Column(db.Integer, primary_key=True)
    fm_ca_link_id = db.Column(db.String(22), nullable=False)
    fm_id = db.Column(db.String(22), nullable=False)
    ca_id = db.Column(db.String(22), nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)
    other = db.Column(db.Text, nullable=False)



class TFmDtcLink(db.Model):
    __tablename__ = 't_fm_dtc_link'

    table_id = db.Column(db.Integer, primary_key=True)
    fm_dtc_link_id = db.Column(db.String(22), nullable=False)
    fm_id = db.Column(db.String(22), nullable=False)
    dtc_id = db.Column(db.String(22), nullable=False)
    link_level = db.Column(db.String(16), nullable=False)
    link_times = db.Column(db.Integer, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)
    link_correlation1 = db.Column(db.Float, nullable=False)
    link_correlation2 = db.Column(db.Float, nullable=False)
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)



class TFmIeLink(db.Model):
    __tablename__ = 't_fm_ie_link'

    table_id = db.Column(db.Integer, primary_key=True)
    fm_ie_link_id = db.Column(db.String(22), nullable=False)
    fm_id = db.Column(db.String(22), nullable=False)
    ie_id = db.Column(db.String(22), nullable=False)
    link_level = db.Column(db.String(16), nullable=False)
    link_times = db.Column(db.Integer, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)
    link_correlation1 = db.Column(db.Float, nullable=False)
    link_correlation2 = db.Column(db.Float, nullable=False)
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)



class TFmInfo(db.Model):
    __tablename__ = 't_fm_info'

    table_id = db.Column(db.Integer, primary_key=True)
    fm_id = db.Column(db.String(22), nullable=False, unique=True)
    fm_name = db.Column(db.Text, nullable=False)
    fm_f = db.Column(db.Float, nullable=False)
    fm_p = db.Column(db.Float)
    part_id = db.Column(db.String(22), nullable=False)
    part_name = db.Column(db.String(255), nullable=False)
    fm_times = db.Column(db.Integer)
    model_version = db.Column(db.String(22), nullable=False, index=True)



class TFmSyLink(db.Model):
    __tablename__ = 't_fm_sy_link'

    table_id = db.Column(db.Integer, primary_key=True)
    fm_sy_link_id = db.Column(db.String(22), nullable=False)
    fm_id = db.Column(db.String(22), nullable=False)
    sy_id = db.Column(db.String(22), nullable=False)
    link_level = db.Column(db.String(16), nullable=False)
    link_times = db.Column(db.Integer, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)
    link_correlation1 = db.Column(db.Float, nullable=False)
    link_correlation2 = db.Column(db.Float, nullable=False)
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)



class TFmTestLink(db.Model):
    __tablename__ = 't_fm_test_link'

    table_id = db.Column(db.Integer, primary_key=True)
    fm_test_link_id = db.Column(db.String(22), nullable=False)
    fm_id = db.Column(db.String(22), nullable=False)
    test_id = db.Column(db.String(22), nullable=False)
    link_level = db.Column(db.String(16), nullable=False)
    link_times = db.Column(db.Integer, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)
    link_correlation1 = db.Column(db.Float, nullable=False)
    link_correlation2 = db.Column(db.Float, nullable=False)
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)



class THealthIndicatorInfo(db.Model):
    __tablename__ = 't_health_indicator_info'

    table_id = db.Column(db.Integer, primary_key=True)
    hi_id = db.Column(db.String(22), nullable=False)
    hi_name = db.Column(db.Text, nullable=False)
    hi_description = db.Column(db.Text, nullable=False)
    hi_unit = db.Column(db.String(16), nullable=False)
    hi_refresh_rate = db.Column(db.Integer, nullable=False)
    hi_state = db.Column(db.Integer, nullable=False)
    sys_id_belong = db.Column(db.String(22), nullable=False)
    part_id_belong = db.Column(db.String(22), nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)



class THiIeLink(db.Model):
    __tablename__ = 't_hi_ie_link'

    table_id = db.Column(db.Integer, primary_key=True)
    hi_ie_link_id = db.Column(db.String(22), nullable=False)
    hi_id = db.Column(db.String(22), nullable=False)
    ie_id = db.Column(db.String(22), nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)
    other = db.Column(db.Text, nullable=False)



class TIeDtcLink(db.Model):
    __tablename__ = 't_ie_dtc_link'

    table_id = db.Column(db.Integer, primary_key=True)
    ie_dtc_link_id = db.Column(db.String(22), nullable=False)
    ie_id = db.Column(db.String(22), nullable=False)
    dtc_id = db.Column(db.String(22), nullable=False)
    link_level = db.Column(db.String(16), nullable=False)
    link_times = db.Column(db.Integer, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)
    link_correlation1 = db.Column(db.Float, nullable=False)
    link_correlation2 = db.Column(db.Float, nullable=False)
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)



class TIeIeLink(db.Model):
    __tablename__ = 't_ie_ie_link'

    table_id = db.Column(db.Integer, primary_key=True)
    ie_ie_link_id = db.Column(db.String(22), nullable=False)
    ie_i_id = db.Column(db.String(22), nullable=False)
    ie_o_id = db.Column(db.String(22), nullable=False)
    link_level = db.Column(db.String(16), nullable=False)
    link_times = db.Column(db.Integer, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)
    link_correlation1 = db.Column(db.Float, nullable=False)
    link_correlation2 = db.Column(db.Float, nullable=False)
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)



class TIeSyLink(db.Model):
    __tablename__ = 't_ie_sy_link'

    table_id = db.Column(db.Integer, primary_key=True)
    ie_sy_link_id = db.Column(db.String(22), nullable=False)
    ie_id = db.Column(db.String(22), nullable=False)
    sy_id = db.Column(db.String(22), nullable=False)
    link_level = db.Column(db.String(16), nullable=False)
    link_times = db.Column(db.Integer, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)
    link_correlation1 = db.Column(db.Float, nullable=False)
    link_correlation2 = db.Column(db.Float, nullable=False)
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)



class TIeTestLink(db.Model):
    __tablename__ = 't_ie_test_link'

    table_id = db.Column(db.Integer, primary_key=True)
    ie_test_link_id = db.Column(db.String(22), nullable=False)
    ie_id = db.Column(db.String(22), nullable=False)
    test_id = db.Column(db.String(22), nullable=False)
    link_level = db.Column(db.String(16), nullable=False)
    link_times = db.Column(db.Integer, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)
    link_correlation1 = db.Column(db.Float, nullable=False)
    link_correlation2 = db.Column(db.Float, nullable=False)
    link_correlation3 = db.Column(db.Float, nullable=False)
    link_correlation4 = db.Column(db.Float, nullable=False)
    link_correlation5 = db.Column(db.Float, nullable=False)



class TInterfaceExceptionInfo(db.Model):
    __tablename__ = 't_interface_exception_info'

    table_id = db.Column(db.Integer, primary_key=True)
    ie_id = db.Column(db.String(22), nullable=False)
    ie_description = db.Column(db.Text, nullable=False)
    ie_cause = db.Column(db.Text, nullable=False)
    ie_influence = db.Column(db.Text, nullable=False)
    interface_id_belong = db.Column(db.String(22), nullable=False)
    ie_state = db.Column(db.Integer, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)



class TInterfaceInfo(db.Model):
    __tablename__ = 't_interface_info'

    table_id = db.Column(db.Integer, primary_key=True)
    interface_id = db.Column(db.String(22), nullable=False)
    interface_name = db.Column(db.Text, nullable=False)
    interface_description = db.Column(db.Text, nullable=False)
    interface_type = db.Column(db.String(16), nullable=False)
    interface_property = db.Column(db.Text, nullable=False)
    interface_dirction = db.Column(db.Integer, nullable=False)
    interface_connect_state = db.Column(db.Integer, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)



class TInterfaceTypeInfo(db.Model):
    __tablename__ = 't_interface_type_info'

    table_id = db.Column(db.Integer, primary_key=True)
    interface_type_id = db.Column(db.String(22), nullable=False)
    interface_type_name = db.Column(db.Text, nullable=False)
    interface_type_description = db.Column(db.Text, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)



class TPart(db.Model):
    __tablename__ = 't_part'

    table_id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.String(14), nullable=False, unique=True)
    bom_id = db.Column(db.Text)
    part_name = db.Column(db.String(255), nullable=False)
    part_description = db.Column(db.String(255))
    part_type = db.Column(db.String(255))
    sys_id_belong = db.Column(db.ForeignKey('t_system.system_id'), nullable=False, index=True)
    software_version = db.Column(db.Text, nullable=False)
    part_producer = db.Column(db.Text)
    model_version = db.Column(db.String(22), nullable=False, index=True)

    t_system = db.relationship('TSystem', primaryjoin='TPart.sys_id_belong == TSystem.system_id', backref='t_parts')



class TSymptomInfo(db.Model):
    __tablename__ = 't_symptom_info'

    table_id = db.Column(db.Integer, primary_key=True)
    sy_id = db.Column(db.String(22), nullable=False)
    sy_level = db.Column(db.Text, nullable=False)
    sy_description = db.Column(db.Text, nullable=False)
    sy_sys_id = db.Column(db.String(7), nullable=False)
    sy_part_id = db.Column(db.String(14), nullable=False)
    sy_times = db.Column(db.Integer, nullable=False)
    sy_p = db.Column(db.Float, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)



class TSystem(db.Model):
    __tablename__ = 't_system'

    table_id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.String(7), nullable=False, unique=True)
    system_name = db.Column(db.Text, nullable=False)
    system_description = db.Column(db.Text)
    system_type = db.Column(db.Text, nullable=False)
    vehicle_id_belong = db.Column(db.ForeignKey('t_vehicle.vehicle_id'), nullable=False, index=True)
    system_producer = db.Column(db.Text)
    software_version = db.Column(db.Text, nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)

    t_vehicle = db.relationship('TVehicle', primaryjoin='TSystem.vehicle_id_belong == TVehicle.vehicle_id', backref='t_systems')



class TTestActionInfo(db.Model):
    __tablename__ = 't_test_action_info'

    table_id = db.Column(db.Integer, primary_key=True)
    test_action_id = db.Column(db.String(22), nullable=False)
    test_action_content = db.Column(db.Text, nullable=False)
    test_system_id = db.Column(db.String(22), nullable=False)
    test_part_id = db.Column(db.String(22), nullable=False)
    test_part_name = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    test_cost_yuan = db.Column(db.Float, nullable=False)
    test_time_h = db.Column(db.Float, nullable=False)
    test_type = db.Column(db.String(16), nullable=False)
    test_complexity = db.Column(db.Float, nullable=False)
    test_instruction_doc_link = db.Column(db.Text)
    test_instruction_video_link = db.Column(db.Text)
    test_equipment = db.Column(db.Text)
    model_version = db.Column(db.String(22), nullable=False)



class TTestResultInfo(db.Model):
    __tablename__ = 't_test_result_info'

    table_id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.String(22), nullable=False, index=True)
    test_result_name = db.Column(db.Text, nullable=False)
    test_result_check = db.Column(db.Integer, nullable=False)
    test_action_id = db.Column(db.String(22), nullable=False)
    test_system_id = db.Column(db.String(22), nullable=False)
    connect_to_ie = db.Column(db.Integer, nullable=False)
    test_part_id = db.Column(db.String(22), nullable=False)
    model_version = db.Column(db.String(22), nullable=False, index=True)



class TUserOperationLog(db.Model):
    __tablename__ = 't_user_operation_log'

    table_id = db.Column(db.Integer, primary_key=True)
    cache_id = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    save_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    vehicle_type_name = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    vehicle_config_name = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    vehicle_model_version = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    algorithm_version = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    vin = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    user_name = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    operate_log_data = db.Column(db.String(15000, 'utf8_general_ci'), nullable=False)
    submit_phase = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    submit_timestamp = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    submit_type = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    vehicle_infomation = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    vehicle_type_match = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    vehicle_dtc = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    vehicle_dtc_count = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    user_input_sy_text = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    input_times_count = db.Column(db.Integer, nullable=False)
    sy_confirm_result = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    sy_confirm_times_count = db.Column(db.Integer, nullable=False)
    test_items = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    test_times_conut = db.Column(db.Integer, nullable=False)
    ca_items = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    ca_times_count = db.Column(db.Integer, nullable=False)
    ca_result = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    fm_list_with_score_final = db.Column(db.String(255, 'utf8_general_ci'), nullable=False)
    advice_response_text = db.Column(db.String(255, 'utf8_general_ci'))



class TVehicle(db.Model):
    __tablename__ = 't_vehicle'

    table_id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(7), nullable=False, unique=True)
    vehicle_brand = db.Column(db.Text, nullable=False)
    vehicle_name = db.Column(db.Text, nullable=False)
    vehicle_type = db.Column(db.Text, nullable=False)
    vehicle_config_id = db.Column(db.String(22), nullable=False)
    vehicle_comment = db.Column(db.Text)
    model_version = db.Column(db.String(22), nullable=False, index=True)



class TVehicleConfig(db.Model):
    __tablename__ = 't_vehicle_config'

    table_id = db.Column(db.Integer, primary_key=True)
    vehicle_config_id = db.Column(db.String(22), nullable=False, unique=True)
    vehicle_config_name = db.Column(db.Text, nullable=False)
    vehicle_config_description = db.Column(db.Text, nullable=False)
    vehicle_type_id_belong = db.Column(db.ForeignKey('t_vehicle_type.vehicle_type_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    modify_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    create_user = db.Column(db.Text, nullable=False)

    t_vehicle_type = db.relationship('TVehicleType', primaryjoin='TVehicleConfig.vehicle_type_id_belong == TVehicleType.vehicle_type_id', backref='t_vehicle_configs')



class TVehicleModel(db.Model):
    __tablename__ = 't_vehicle_model'

    table_id = db.Column(db.Integer, primary_key=True)
    vehicle_model_id = db.Column(db.String(22), nullable=False, unique=True)
    version_code = db.Column(db.String(22), nullable=False)
    vehicle_type_id = db.Column(db.String(22), nullable=False, index=True)
    vehicle_config_id = db.Column(db.String(22), nullable=False, index=True)
    vehicle_model_name = db.Column(db.Text, nullable=False)
    release_time = db.Column(db.DateTime, nullable=False)
    import_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    modify_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    create_user = db.Column(db.Text, nullable=False)



class TVehicleType(db.Model):
    __tablename__ = 't_vehicle_type'

    table_id = db.Column(db.Integer, primary_key=True)
    vehicle_type_id = db.Column(db.String(22), nullable=False, unique=True)
    vin_re = db.Column(db.Text, nullable=False)
    brand_name = db.Column(db.Text, nullable=False)
    vehicle_type_name = db.Column(db.Text, nullable=False)
    create_user = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    modify_time = db.Column(db.DateTime, server_default=db.FetchedValue())
