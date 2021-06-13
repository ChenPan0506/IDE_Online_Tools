import pandas as pd

sheet_key_inx = {
    "Model": ["部件编号",
              "部件名称",
              "失效模式",
              "输入",
              "接口异常",
              "症状类别",
              "症状_失效概率频度",
              "受影响的接口异常",
              "输出",
              "FS",
              "IS",
              "FO",
              "IO"],
    "Model_sys": ["系统编号",
                  "系统名称",
                  "部件名称",
                  "失效模式",
                  "输入",
                  "接口异常",
                  "症状类别",
                  "症状_失效概率频度",
                  "受影响的接口异常",
                  "输出",
                  "FS",
                  "IS",
                  "FO",
                  "IO"],
    "01Assembly": [],
    "02Interface": [],
    "03FM Occurence Count": [],
    "04Corrective Action-Cost": [],
    "05FM-CA": [],
    "06Test": [],
    "07TestResult-Test": []}


class BaseSheet:

    def __init__(self, filename, sheet_name, creattype="file"):
        if creattype == "file":
            self.data = pd.read_excel(filename, sheet_name=sheet_name, header=None)
        elif creattype == "obj":
            self.data = filename

        #     判断sheet代表的是部件还是系统
        if self.data.iloc[0, 0] == "部件编号" and sheet_name == "Model":
            self.sheettype = "part"
            self.frame_list = sheet_key_inx[sheet_name]
        elif self.data.iloc[0, 0] == "系统编号" and sheet_name == "Model":
            self.sheettype = "system"
            self.frame_list = sheet_key_inx[sheet_name + "_sys"]
        self.shape = self.data.shape
        self.sheetname = sheet_name
        self.table_structure = self.frame_recg()
        if self.table_structure != -1 and self.sheetname == "Model":
            self.table_parts = self.tablesplit()
            print("Sheet: %s 创建完成! " % sheet_name)
        else:
            self.table_parts = "未按照格式分表"
            # print("Sheet: %s 格式不合法!" % sheet_name)

    def frame_recg(self):
        frame_result = {}
        if self.sheetname not in sheet_key_inx.keys():
            print("Sheet: %s is not defined" % self.sheetname)
        elif self.sheetname == "Model":
            # 20190910 加快查询速度
            col_names = self.data.columns.tolist()
            for name in self.frame_list:
                for col_name in self.data.columns.values.tolist():
                    row_nums = self.data[self.data[col_name] == name].index.tolist()
                    if len(row_nums) == 1:
                        frame_result[name] = [row_nums[0], col_names.index(col_name)]

            for key, values in frame_result.items():
                # 给每个数据分区增加 [数据起始点x坐标,数据起始点y坐标，数据区域高度，数据区域宽度]
                if self.sheettype == "system":
                    if key == "系统编号":
                        values.extend([values[0] + 1, values[1], 1, 1])
                    if key == "系统名称":
                        values.extend([values[0] + 1, values[1], 1, 1])
                    if key == "症状类别" or key == "症状_失效概率频度":
                        values.extend([values[0], values[1] + 1, 1, frame_result["输出"][1] - values[1] - 1])
                    if key == "输出" or key == "受影响的接口异常":
                        values.extend([values[0], values[1] + 1, 1, self.shape[1] - values[1]])
                    if key == "输入" or key == "接口异常":
                        values.extend([values[0] + 1, values[1], self.shape[0] - values[0], 1])
                    if key == "部件名称" or key == "失效模式":
                        values.extend([values[0] + 1, values[1], frame_result["输入"][0] - values[0] - 1, 1])

                    if key == "FS":
                        values.extend([values[0] + 1, values[1] + 1, frame_result["IS"][0] - values[0] - 1,
                                       frame_result["FO"][1] - values[1] - 1])
                    if key == "FO":
                        values.extend([values[0] + 1, values[1] + 1, frame_result["IS"][0] - values[0] - 1,
                                       self.shape[1] - values[1]])
                    if key == "IS":
                        values.extend([values[0] + 1, values[1] + 1, self.shape[0] - values[0],
                                       frame_result["FO"][1] - values[1] - 1])
                    if key == "IO":
                        values.extend(
                            [values[0] + 1, values[1] + 1, self.shape[0] - values[0], self.shape[1] - values[1]])

                if self.sheettype == "part":
                    if key == "部件编号":
                        values.extend([values[0] + 1, values[1], 1, 1])
                    if key == "部件名称":
                        values.extend([values[0] + 1, values[1], 1, 1])
                    if key == "症状类别" or key == "症状_失效概率频度":
                        values.extend([values[0], values[1] + 1, 1, frame_result["输出"][1] - values[1] - 1])
                    if key == "输出" or key == "受影响的接口异常":
                        values.extend([values[0], values[1] + 1, 1, self.shape[1] - values[1] - 1])
                    if key == "输入" or key == "接口异常":
                        values.extend([values[0] + 1, values[1], self.shape[0] - values[0] - 1, 1])
                    if key == "失效模式":
                        values.extend([values[0] + 1, values[1] - 1, frame_result["输入"][0] - values[0] - 1, 3])

                    if key == "FS":
                        values.extend([values[0] + 1, values[1] + 1, frame_result["IS"][0] - values[0] - 1,
                                       frame_result["FO"][1] - values[1] - 1])
                    if key == "FO":
                        values.extend([values[0] + 1, values[1] + 1, frame_result["IS"][0] - values[0] - 1,
                                       self.shape[1] - values[1] - 1])
                    if key == "IS":
                        values.extend([values[0] + 1, values[1] + 1, self.shape[0] - values[0] - 1,
                                       frame_result["FO"][1] - values[1] - 1])
                    if key == "IO":
                        values.extend([values[0] + 1, values[1] + 1, self.shape[0] - values[0] - 1,
                                       self.shape[1] - values[1] - 1])
            return frame_result
        else:
            # print("Sheet：{0}格式未定义".format(self.sheetname))
            return -1

    def tablesplit(self):
        table_parts_data = {}
        for key, values in self.table_structure.items():
            table_parts_data[key] = self.data.iloc[values[2]:values[2] + values[4], values[3]:values[3] + values[5]]
        return table_parts_data

    def tablesplit1(self):
        if self.sheetname not in sheet_key_inx.keys():
            print("Sheet: %s is not defined")
        elif self.sheetname == "Model":
            table_parts = []
            table_parts.append([self.data.iloc[
                                (self.table_structure[1]["输入"][0] + 1):(self.table_structure[1]["失效模式"][0]),
                                (self.table_structure[1]["受影响的输入"][1] + 1):(self.table_structure[1]["症状"][1])],
                                self.data.iloc[
                                (self.table_structure[1]["输入"][0] + 1):(self.table_structure[1]["失效模式"][0]), 1],
                                self.data.iloc[1,
                                (self.table_structure[1]["受影响的输入"][1] + 1):(self.table_structure[1]["症状"][1])]])
            table_parts.append([self.data.iloc[
                                (self.table_structure[1]["失效模式"][0] + 1):(self.table_structure[1]["输出"][0]),
                                (self.table_structure[1]["受影响的输入"][1] + 1):(self.table_structure[1]["症状"][1])],
                                self.data.iloc[
                                (self.table_structure[1]["失效模式"][0] + 1):(self.table_structure[1]["输出"][0]), 1],
                                self.data.iloc[1,
                                (self.table_structure[1]["受影响的输入"][1] + 1):(self.table_structure[1]["症状"][1])]])
            table_parts.append([self.data.iloc[(self.table_structure[1]["输出"][0] + 1):(self.table_structure[2][0]),
                                (self.table_structure[1]["受影响的输入"][1] + 1):(self.table_structure[1]["症状"][1])],
                                self.data.iloc[(self.table_structure[1]["输出"][0] + 1):(self.table_structure[2][0]), 1],
                                self.data.iloc[1,
                                (self.table_structure[1]["受影响的输入"][1] + 1):(self.table_structure[1]["症状"][1])]])
            table_parts.append([self.data.iloc[
                                (self.table_structure[1]["输入"][0] + 1):(self.table_structure[1]["失效模式"][0]),
                                (self.table_structure[1]["症状"][1] + 1):(self.table_structure[1]["受影响的输出"][1])],
                                self.data.iloc[
                                (self.table_structure[1]["输入"][0] + 1):(self.table_structure[1]["失效模式"][0]), 1],
                                self.data.iloc[1,
                                (self.table_structure[1]["症状"][1] + 1):(self.table_structure[1]["受影响的输出"][1])]])
            table_parts.append([self.data.iloc[
                                (self.table_structure[1]["失效模式"][0] + 1):(self.table_structure[1]["输出"][0]),
                                (self.table_structure[1]["症状"][1] + 1):(self.table_structure[1]["受影响的输出"][1])],
                                self.data.iloc[
                                (self.table_structure[1]["失效模式"][0] + 1):(self.table_structure[1]["输出"][0]), 1],
                                self.data.iloc[1,
                                (self.table_structure[1]["症状"][1] + 1):(self.table_structure[1]["受影响的输出"][1])]])
            table_parts.append([self.data.iloc[(self.table_structure[1]["输出"][0] + 1):(self.table_structure[2][0]),
                                (self.table_structure[1]["症状"][1] + 1):(self.table_structure[1]["受影响的输出"][1])],
                                self.data.iloc[(self.table_structure[1]["输出"][0] + 1):(self.table_structure[2][0]), 1],
                                self.data.iloc[1,
                                (self.table_structure[1]["症状"][1] + 1):(self.table_structure[1]["受影响的输出"][1])]])
            table_parts.append([self.data.iloc[
                                (self.table_structure[1]["输入"][0] + 1):(self.table_structure[1]["失效模式"][0]),
                                (self.table_structure[1]["受影响的输出"][1] + 1):(self.table_structure[2][1])],
                                self.data.iloc[
                                (self.table_structure[1]["输入"][0] + 1):(self.table_structure[1]["失效模式"][0]), 1],
                                self.data.iloc[1,
                                (self.table_structure[1]["受影响的输出"][1] + 1):(self.table_structure[2][1])]])
            table_parts.append([self.data.iloc[
                                (self.table_structure[1]["失效模式"][0] + 1):(self.table_structure[1]["输出"][0]),
                                (self.table_structure[1]["受影响的输出"][1] + 1):(self.table_structure[2][1])],
                                self.data.iloc[
                                (self.table_structure[1]["失效模式"][0] + 1):(self.table_structure[1]["输出"][0]), 1],
                                self.data.iloc[1,
                                (self.table_structure[1]["受影响的输出"][1] + 1):(self.table_structure[2][1])]])
            table_parts.append([self.data.iloc[(self.table_structure[1]["输出"][0] + 1):(self.table_structure[2][0]),
                                (self.table_structure[1]["受影响的输出"][1] + 1):(self.table_structure[2][1])],
                                self.data.iloc[(self.table_structure[1]["输出"][0] + 1):(self.table_structure[2][0]), 1],
                                self.data.iloc[1,
                                (self.table_structure[1]["受影响的输出"][1] + 1):(self.table_structure[2][1])]])
            for x in range(0, len(table_parts)):
                table_parts[x][0].index = self.data.iloc[table_parts[x][0].index, 0]
                table_parts[x][0].columns = self.data.iloc[0, table_parts[x][0].columns]
            return table_parts
        else:
            print("该sheet分表方法未定义！")
