from .BaseSheet import BaseSheet
from flask_socketio import emit


class BasePart:
    def __init__(self, filename, percents):
        self.sheetsname_list = ["Model", "01Assembly", "02Interface", "03FM Occurence Count",
                                "04Corrective Action-Cost", "05FM-CA", "06Test", "07TestResult-Test"]
        self.sheets_list = {}
        for shtname in self.sheetsname_list:
            self.sheets_list[shtname] = BaseSheet(filename, shtname, creattype="file")
        self.partname = self.sheets_list["Model"].table_parts["部件名称"]  # 读取部件名称
        self.Model_data = self.sheets_list["Model"].data
        print("部件: %s 创建完成! " % self.partname.iloc[0, 0])
        emit('modelIntegrationResponse', {'percent': percents, 'message': "部件: %s 创建完成! " % self.partname.iloc[0, 0]})
