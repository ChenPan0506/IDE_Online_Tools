from . import ma
from .tables import *


# class TVehicleModelSchema(ma.SQLAlchemySchema):
class TVehicleModelSchema(ma.Schema):
    class Meta:
        model = TVehicleModel
        include_fk = False
        fields = (
            "table_id",
            "vehicle_model_id",
            "version_code",
            "vehicle_type_id",
            "vehicle_config_id",
            "vehicle_model_name",
            "release_time",
            "import_time",
            "modify_time",
            "create_user"
        )


class TVehicleConfigSchema(ma.Schema):
    class Meta:
        model = TVehicleConfig
        include_fk = False
        fields = (
            "table_id",
            "vehicle_config_id",
            "vehicle_config_name",
            "vehicle_config_description",
            "vehicle_type_id_belong",
            "modify_time",
            "create_time",
            "create_user"
        )


class TVehicleTypeSchema(ma.Schema):
    class Meta:
        model = TVehicleType
        include_fk = False
        fields = (
            "table_id",
            "vehicle_type_id",
            "vin_re",
            "brand_name",
            "vehicle_type_name",
            "create_user",
            "create_time",
            "modify_time"
        )


class TConfigModelLinkSchema(ma.Schema):
    class Meta:
        model = TConfigModelLink
        include_fk = False
        fields = (
            "table_id",
            "config_model_link_id",
            "vehicle_type_id",
            "vehicle_config_id",
            "vehicle_model_id",
            "al_param_id",
            "release_time",
            "description",
            "create_time",
            "state",
            "operation",
            "editState"
        )
