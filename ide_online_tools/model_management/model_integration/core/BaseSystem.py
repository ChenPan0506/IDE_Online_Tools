import glob
import pickle
import pandas as pd
import numpy as np
import copy
from flask_socketio import emit
from .BaseSheet import BaseSheet
from .BasePart import BasePart


class BaseSystem:

    def __init__(self):
        self.sysshape = [0, 0]
        self.systable_Structure = [[0, 0, 0, 0, 0, 0], ]
        self.sysdatatable = [pd.DataFrame(), ]
        self.sysdatatable_mask = pd.DataFrame()
        self.parts = []
        self.partsrelation = []
        self.parts_order = []  # 部件连接顺序
        self.parts_dict = {}  # 部件查询表

        # 系统表集成过程中的关键坐标点7个：输入，接口异常，IS，输出，受影响的接口异常，FO，IO
        self.sys_key_cursor = {"输入": [0, 0], "接口异常": [0, 0], "IS": [0, 0], "输出": [0, 0], "受影响的接口异常": [0, 0],
                               "FO": [0, 0], "IO": [0, 0]}
        self.sys_key_cursor_inx = {"输入": "失效模式", "接口异常": "失效模式", "IS": "失效模式", "输出": "症状类别", "受影响的接口异常": "症状_失效概率频度",
                                   "FO": "FS"}

    def creatsys(self, partspath, relationfilepath):
        self.partsrelation_data = pd.read_excel(relationfilepath, sheet_name="NetList", header=None)
        self.sysname = self.partsrelation_data.iloc[1, 1]
        self.sysnum = self.partsrelation_data.iloc[0, 1]
        for i in range(3, self.partsrelation_data.shape[0]):
            for j in (1, 4, 7):
                if self.partsrelation_data.iloc[i, j] in self.parts_order:
                    pass
                else:
                    self.parts_order.append(self.partsrelation_data.iloc[i, j])
        percent = 0
        for index, file_num in enumerate(self.parts_order):

            if glob.glob(partspath + str(file_num) + "_*.xlsx"):
                print(glob.glob(partspath + str(file_num) + "_*.xlsx")[0])
                part_tmp = BasePart(glob.glob(partspath + str(file_num) + "_*.xlsx")[0], round(percent, 1))
                percent = ((index + 1) / len(self.parts_order)) * 25
                self.parts.append(part_tmp)
                self.parts_dict[str(part_tmp.partname.values)[3:-3]] = part_tmp  # 保存部件信息字典
            else:
                print("部件：%s 对应的文件不存在" % str(file_num))
                # emit('modelIntegrationResponse', {'percent': 0, 'message': "部件：%s 对应的文件不存在" % str(file_num)})

        print("开始计算合表尺寸")
        emit('modelIntegrationResponse', {'percent': 28, 'message': "开始计算合表尺寸..."})

        # 合成表的尺寸计算
        for i, partOBJ in enumerate(self.parts):
            if i == 0:
                self.sysshape[0] = partOBJ.Model_data.shape[0]
                self.sysshape[1] = partOBJ.Model_data.shape[1]
                for key, value in partOBJ.sheets_list["Model"].table_structure.items():
                    if key in self.sys_key_cursor.keys():  # 第一个表
                        self.sys_key_cursor[key] = [value[0], value[1]]
            elif i != 0:
                self.sysshape[0] += partOBJ.sheets_list["Model"].table_structure["FS"][4]
                self.sysshape[1] += partOBJ.sheets_list["Model"].table_structure["FS"][5]
                self.sysshape[0] += partOBJ.sheets_list["Model"].table_structure["IO"][4]
                self.sysshape[1] += partOBJ.sheets_list["Model"].table_structure["IO"][5]
                for key, value in partOBJ.sheets_list["Model"].table_structure.items():
                    if key in self.sys_key_cursor_inx.keys():  # 第2 ~ N个表
                        if key in ["输入", "接口异常", "IS"]:
                            self.sys_key_cursor[key][0] += \
                                partOBJ.sheets_list["Model"].table_structure[self.sys_key_cursor_inx[key]][4]
                        elif key in ["输出", "受影响的接口异常", "FO"]:
                            self.sys_key_cursor[key][1] += \
                                partOBJ.sheets_list["Model"].table_structure[self.sys_key_cursor_inx[key]][5]
        self.sys_key_cursor["IO"] = [self.sys_key_cursor["IS"][0], self.sys_key_cursor["FO"][1]]
        self.sysdatatable[0] = pd.DataFrame(np.zeros([self.sysshape[0], self.sysshape[1]]))
        self.sysdatatable_mask = pd.DataFrame(np.zeros([self.sysshape[0], self.sysshape[1]]))
        self.sysdatatable[0] = self.sysdatatable[0].replace(0, np.nan)
        emit('modelIntegrationResponse', {'percent': 29, 'message': "合表尺寸计算完成..."})

    def Model_data_integration(self):
        """
        输入部件OBJ ：[part1,part2,....,partn]
        :return: Dataframe 集成表格
        """
        self.sys_fix_cursor = {"系统编号": [0, 0], "系统名称": [0, 1], "失效模式": [2, 1], "部件名称": [2, 0], "FS": [2, 2],
                               "症状类别": [0, 2], "症状_失效概率频度": [1, 2]}
        self.sys_full_cursor = copy.deepcopy(self.sys_fix_cursor)
        self.sys_full_cursor.update(self.sys_key_cursor)
        for k, v in self.sys_full_cursor.items():
            self.sysdatatable[0].iloc[v[0], v[1]] = k

        self.sysdatatable[0].iloc[1, 0] = self.sysnum  # 系统编号
        self.sysdatatable[0].iloc[1, 1] = self.sysname  # # 系统名称

        key_cursor = copy.deepcopy(self.sys_full_cursor)
        for part_tables in self.parts:
            for key, values in part_tables.sheets_list["Model"].table_parts.items():
                if key != "部件编号" and key != "部件名称" and values.size != 0:
                    cursor = key_cursor[key]
                    if key == "FS" or key == "IS" or key == "FO" or key == "IO":
                        cursor[0] += 1
                        cursor[1] += 1
                        self.sysdatatable_mask.iloc[cursor[0]:cursor[0] + values.shape[0],
                        cursor[1]:cursor[1] + values.shape[1]] = 1
                        self.sysdatatable[0].iloc[cursor[0]:cursor[0] + values.shape[0],
                        cursor[1]:cursor[1] + values.shape[1]] = values.values
                        key_cursor[key][0] += values.shape[0] - 1
                        key_cursor[key][1] += values.shape[1] - 1

                    if key == "症状类别" or key == "症状_失效概率频度" or key == "输出" or key == "受影响的接口异常":
                        cursor[1] += 1

                        self.sysdatatable[0].iloc[cursor[0],
                        cursor[1]:cursor[1] + values.shape[1]] = values.values.flatten()
                        key_cursor[key][1] += values.shape[1] - 1

                    if key == "输入" or key == "接口异常":
                        cursor[0] += 1

                        self.sysdatatable[0].iloc[cursor[0]:cursor[0] + values.shape[0],
                        cursor[1]] = values.values.flatten()
                        key_cursor[key][0] += values.shape[0] - 1
                    if key == "失效模式":
                        cursor[0] += 1
                        self.sysdatatable[0].iloc[cursor[0]:cursor[0] + values.shape[0],
                        cursor[1] - 1:cursor[1] + 2] = values.values
                        key_cursor[key][0] += values.shape[0] - 1

        print("data integration finished")

    def duplicate_sy_merge(self):

        ############################################     删除重复列    ############################################
        sy_duplicate = self.sysdatatable[0].iloc[0:2, self.sys_full_cursor["症状类别"][1]:]
        sy_duplicate = sy_duplicate.T
        sy_duplicate.columns = [u'症状类别', u'症状_失效概率频度']
        sy_duplicate["combine"] = sy_duplicate[['症状类别', '症状_失效概率频度']].apply(lambda x: ','.join(x), axis=1)
        elements = set(sy_duplicate["combine"])
        if len(sy_duplicate["combine"]) == len(elements):
            print("系统：%s 集成完成后不包含重复症状" % self.sysname)
        else:
            print("系统：{0} 集成后包含{1}项重复".format(self.sysname, len(sy_duplicate["combine"]) - len(elements)))
            # 找重复症状  [[1],[2],......[45,38],[56]....]

            nums = [[] for x in elements]
            for inx, itm in enumerate(elements):
                for i in range(0, len(sy_duplicate["combine"])):
                    if itm == sy_duplicate["combine"].iloc[i]:
                        nums[inx].append(sy_duplicate["combine"].index[i])

            nums.sort(reverse=True)
            # print(nums)
            # 重复症状 合并
            for element in nums:
                if len(element) == 1:
                    pass
                else:
                    for cols_inx in range(0, len(element)):
                        if cols_inx == 0:
                            pass
                        else:
                            tmp = self.sysdatatable[0][element[cols_inx]][self.sys_full_cursor["FS"][0] + 1:]
                            for j, content in zip(tmp.index, tmp.values):
                                result_list = ["U", "U"]
                                if pd.isna(self.sysdatatable[0][element[0]][j]) or self.sysdatatable[0][element[0]][
                                    j] == "[,]":
                                    if pd.isna(content) or content == "[,]":
                                        pass
                                    else:
                                        self.sysdatatable[0][element[0]][j] = content
                                else:
                                    if pd.isna(content) or content == "[,]":
                                        pass
                                    else:
                                        content1_str = copy.deepcopy(str(self.sysdatatable[0][element[0]][j]))
                                        content1 = content1_str[1:-1].split(",")
                                        content2 = content[1:-1].split(",")
                                        # 第一项肯定为 X
                                        assert content1[0] == "X" and content2[0] == "X"
                                        result_list[0] = "X"
                                        # if content1[0] == "1" and content2[0] == "1":
                                        #     result_list[0] = "1"
                                        # else:
                                        #     result_list[0] = "X"
                                        # if content1[1] == "0" or content2[1] == "0":
                                        #     result_list[1] = "0"
                                        # elif content1[1] != "0" and content2[1] != "0":
                                        #     if content1[1] == "X" or content2[1] == "X":
                                        #         result_list[1] = "X"
                                        #     else:
                                        #         result_list[1] = "1"
                                        if content1[1] == "1" and content2[1] == "1":
                                            result_list[1] = "1"
                                        elif content1[1] == "0" or content2[1] == "0":
                                            result_list[1] = "0"
                                        else:
                                            result_list[1] = "X"
                                        self.sysdatatable[0][element[0]][j] = str(result_list).replace("'", "").replace(
                                            " ", "")

            # 删除重复列
            change_col_index = copy.deepcopy(self.sys_full_cursor["输出"][1])
            for element in nums:
                if len(element) == 1:
                    pass
                else:
                    # print("删除{0}列".format(len(element) - 1))
                    self.sysdatatable[0] = self.sysdatatable[0].drop(element[1:], axis=1)
                    self.sysdatatable_mask = self.sysdatatable_mask.drop(element[1:], axis=1)
                    # key_cursor 更新
                    for del_col in element[1:]:
                        if del_col < change_col_index:
                            self.sys_full_cursor["输出"][1] -= 1
                            self.sys_full_cursor["受影响的接口异常"][1] -= 1
                            self.sys_full_cursor["FO"][1] -= 1
                            self.sys_full_cursor["IO"][1] -= 1
        for inx, col in enumerate(self.sysdatatable[0].columns.values):
            self.sysdatatable[0].columns.values[inx] = inx

        emit('modelIntegrationResponse', {'percent': 50, 'message': "列去重完成..."})
        ############################################     删除重复行    ############################################
        sy_duplicate2 = self.sysdatatable[0].iloc[self.sys_full_cursor["输入"][0]:, 0:2]
        # sy_duplicate2 = sy_duplicate.T
        sy_duplicate2.columns = [u'输入', u'接口异常']
        sy_duplicate2["combine"] = sy_duplicate2[['输入', '接口异常']].apply(lambda x: ','.join(x), axis=1)
        elements2 = set(sy_duplicate2["combine"])
        if len(sy_duplicate2["combine"]) == len(elements2):
            print("系统：%s 集成完成后不包含重复症状" % self.sysname)
        else:
            print("系统：{0} 集成后包含{1}项重复".format(self.sysname, len(sy_duplicate2["combine"]) - len(elements2)))
            # 找重复症状  [[1],[2],......[45,38],[56]....]
            nums2 = [[] for x in elements2]
            for inx2, itm2 in enumerate(elements2):
                for i2 in range(0, len(sy_duplicate2["combine"])):
                    if itm2 == sy_duplicate2["combine"].iloc[i2]:
                        nums2[inx2].append(sy_duplicate2["combine"].index[i2])

            nums2.sort(reverse=True)
            # print(nums2)
            # 重复症状 合并
            for element2 in nums2:
                if len(element2) == 1:
                    pass
                else:
                    for cols_inx2 in range(0, len(element2)):
                        if cols_inx2 == 0:
                            pass
                        else:
                            tmp2 = self.sysdatatable[0].iloc[element2[cols_inx2], self.sys_full_cursor["FS"][1] + 1:]
                            for j2, content2 in zip(tmp2.index, tmp2.values):
                                result_list2 = ["U", "U"]
                                if pd.isna(self.sysdatatable[0].iloc[element2[0], j2]) or self.sysdatatable[0].iloc[
                                    element2[0], j2] == "[,]":
                                    if pd.isna(content2) or content2 == "[,]":
                                        pass
                                    else:
                                        self.sysdatatable[0].iloc[element2[0], j2] = content2
                                else:
                                    if pd.isna(content2) or content2 == "[,]":
                                        pass
                                    else:
                                        content1_str2 = copy.deepcopy(str(self.sysdatatable[0].iloc[element2[0], j2]))
                                        content12 = content1_str2[1:-1].split(",")
                                        content22 = content2[1:-1].split(",")
                                        if content12[0] == "1" and content22[0] == "1":
                                            result_list2[0] = "1"
                                        else:
                                            result_list2[0] = "X"
                                        if content12[1] == "0" or content22[1] == "0":
                                            result_list2[1] = "0"
                                        elif content12[1] != "0" and content22[1] != "0":
                                            if content12[1] == "X" or content22[1] == "X":
                                                result_list2[1] = "X"
                                            else:
                                                result_list2[1] = "1"
                                        self.sysdatatable[0].iloc[element2[0], j2] = str(result_list2).replace("'",
                                                                                                               "").replace(
                                            " ", "")

            # 删除重复行
            for element2 in nums2:
                if len(element2) == 1:
                    pass
                else:
                    # print("删除{0}行".format(len(element2) - 1))
                    self.sysdatatable[0] = self.sysdatatable[0].drop(element2[1:], axis=0)
                    self.sysdatatable_mask = self.sysdatatable_mask.drop(element2[1:], axis=0)
        for inx2, col2 in enumerate(self.sysdatatable[0].index.values):
            self.sysdatatable[0].index.values[inx2] = inx2
        emit('modelIntegrationResponse', {'percent': 59, 'message': "行去重完成..."})

    def sys_relation_input(self):
        relation_tuple = []
        for inx, link in enumerate(self.partsrelation_data["连接件编号"]):
            if pd.isna(link) is True:
                relation_tuple.append((self.partsrelation_data["上游部件输出"][inx], self.partsrelation_data["下游部件输入"][inx]))
            else:
                relation_tuple.append((self.partsrelation_data["上游部件输出"][inx], self.partsrelation_data["上游部件输出"][inx]))
                relation_tuple.append((self.partsrelation_data["下游部件输入"][inx], self.partsrelation_data["下游部件输入"][inx]))
        self.partsrelation = relation_tuple

    def data_reasoning(self):
        print("start reasoning...")
        sy_duplicate = self.sysdatatable[0].iloc[0:2, self.sys_full_cursor["输出"][1]:]
        sy_duplicate = sy_duplicate.T
        sy_duplicate.columns = [u'输出', u'受影响的接口异常']
        sy_duplicate["combine"] = sy_duplicate[['输出', '受影响的接口异常']].apply(lambda x: ','.join(x), axis=1)

        sy_duplicate2 = self.sysdatatable[0].iloc[self.sys_full_cursor["输入"][0]:, 0:2]
        sy_duplicate2.columns = [u'输入', u'接口异常']
        sy_duplicate2["combine"] = sy_duplicate2[['输入', '接口异常']].apply(lambda x: ','.join(x), axis=1)

        # 推理前获得表中X的个数
        numof_x_old = self.sysdatatable[0].iloc[self.sys_full_cursor["FS"][0] + 1:,
                      self.sys_full_cursor["FS"][0] + 1:].count().sum() - 1
        itestop = 1
        while itestop:
            print("外层循环")
            for i, interface_out in enumerate(sy_duplicate["combine"]):
                for j, interface_in in enumerate(sy_duplicate2["combine"]):
                    if interface_out == interface_in:
                        reason_col = sy_duplicate["combine"].index[i]
                        reason_row = sy_duplicate2["combine"].index[j]
                        X_list = [x for x, y in
                                  zip(self.sysdatatable[0].iloc[self.sys_full_cursor["FS"][0] + 1:, reason_col].index
                                      ,
                                      self.sysdatatable[0].iloc[self.sys_full_cursor["FS"][0] + 1:, reason_col].values)
                                  if (pd.isna(y) or y == "[,]") is False]
                        Y_list = [x for x, y in
                                  zip(self.sysdatatable[0].iloc[reason_row, self.sys_full_cursor["FS"][1] + 1:].index
                                      ,
                                      self.sysdatatable[0].iloc[reason_row, self.sys_full_cursor["FS"][1] + 1:].values)
                                  if (pd.isna(y) or y == "[,]") is False]
                        # 循环填入“X”
                        for X in X_list:
                            for Y in Y_list:
                                # if ((X == 48 or X == 49) and Y == 5):
                                #     print("")
                                if self.sysdatatable[0].iloc[X, Y] == "[,]" or pd.isna(self.sysdatatable[0].iloc[X, Y]):
                                    zone2 = self.sysdatatable[0].iloc[X, reason_col][1:-1].split(",")
                                    zone3 = self.sysdatatable[0].iloc[reason_row, Y][1:-1].split(",")
                                    # 只要有0 结果即为0
                                    if zone2[1] == '0' or zone3[1] == '0':
                                        self.sysdatatable[0].iloc[X, Y] = "[X,0]"
                                    # 全1 结果才为1
                                    elif zone2[1] == '1' and zone3[1] == '1':
                                        self.sysdatatable[0].iloc[X, Y] = "[X,1]"
                                    # 其他均为X
                                    else:
                                        self.sysdatatable[0].iloc[X, Y] = "[X,X]"
                                else:
                                    pass
                                    # 如果传递过程中原来的区域已经填写了数值，则不传递。认为人工填写的数值，准确程度大于传递的数值
                                    # zone1 = self.sysdatatable[0].iloc[X, Y][1:-1].split(",")
                                    # zone2 = self.sysdatatable[0].iloc[X, reason_col][1:-1].split(",")
                                    # zone3 = self.sysdatatable[0].iloc[reason_row, Y][1:-1].split(",")
                                    # if zone1[1] == '0' or zone2[1] == '0' or zone3[1] == '0':
                                    #     self.sysdatatable[0].iloc[X, Y] = "[X," + str(0) + "]"
                                    # elif zone1[1] == '1' and zone2[1] == '1' and zone3[1] == '1':
                                    #     self.sysdatatable[0].iloc[X, Y] = "[X," + str(1) + "]"
                                    # else:
                                    #     self.sysdatatable[0].iloc[X, Y] = "[X,X]"

            numof_x_new = self.sysdatatable[0].iloc[self.sys_full_cursor["FS"][0] + 1:,
                          self.sys_full_cursor["FS"][0] + 1:].count().sum() - 1
            print("当前X个数：{0}; 原始X个数：{1}; 新增 {2} 个".format(numof_x_new, numof_x_old, numof_x_new - numof_x_old))
            if numof_x_new == numof_x_old:
                itestop = 0
            else:
                numof_x_old = numof_x_new

        sum_fm_col_extension = list(range(self.sys_full_cursor["FS"][1], self.sys_full_cursor["IO"][1]))
        sum_fm_col_extension.extend(list(range(self.sys_full_cursor["IO"][1] + 1, self.sysdatatable[0].shape[1])))
        sum_fm_col = copy.deepcopy(
            self.sysdatatable[0].iloc[self.sys_full_cursor["FS"][0] + 1:self.sys_full_cursor["IO"][0],
            sum_fm_col_extension])
        sum_io_col = copy.deepcopy(
            self.sysdatatable[0].iloc[self.sys_full_cursor["IS"][0] + 1:,
            sum_fm_col_extension])
        delate_dtc_col_index = []
        for col_number in sum_fm_col.columns.tolist():
            if col_number == 2:
                pass
            else:
                temp_fm = sum_fm_col.loc[:, [2, col_number]]
                temp_io = sum_io_col.loc[:, [col_number]]
                temp_fm.columns = ["f", "sum_f_FM"]
                temp_io.columns = ["sum_f_IO"]

                self.sysdatatable[0].iloc[2, col_number] = temp_fm["f"][
                    (temp_fm["sum_f_FM"] == "[X,1]") | (temp_fm["sum_f_FM"] == "[X,0]") | (
                                temp_fm["sum_f_FM"] == "[X,X]")].sum()

                self.sysdatatable[0].iloc[self.sys_full_cursor["IS"][0], col_number] = temp_io["sum_f_IO"][
                    (temp_io["sum_f_IO"] == "[X,1]") | (temp_io["sum_f_IO"] == "[X,0]") | (
                                temp_io["sum_f_IO"] == "[X,X]")].count()

                if ("DTC_" in self.sysdatatable[0].iloc[0, col_number]
                        # and self.sysdatatable[0].iloc[self.sys_full_cursor["IS"][0], col_number] == 0
                        and self.sysdatatable[0].iloc[2, col_number] == 0):
                    emit('modelIntegrationResponse', {'percent': 59, 'message': "孤立DTC节点" + self.sysdatatable[0].iloc[0, col_number]})
                    delate_dtc_col_index.append(col_number)
        # 删除 统计X个数为0的dtc项目
        print("需要删除的DTC的数量为：" + str(len(delate_dtc_col_index)))
        if len(delate_dtc_col_index) != 0:
            self.sysdatatable[0] = self.sysdatatable[0].drop(delate_dtc_col_index, axis=1)
            # 重排dataframe的列索引
            for inx, col in enumerate(self.sysdatatable[0].columns.values):
                self.sysdatatable[0].columns.values[inx] = inx
        print("reason finished! and sum col X is calculated! and sum io times is calculated!")

    def split_sys_table(self):
        self.sys_split_sheet = BaseSheet(self.sysdatatable[0], "Model", creattype="obj")

    def system_outputFile(self, path, sheetname):
        self.sysdatatable[0].to_excel(path + "/sys.xlsx", encoding='utf_8_sig', index=False, header=False,
                                      sheet_name=sheetname)

        print("文件存储完成！")

    def system_outputBinaryFile(self, path):
        f = open(path + './sys.db', 'wb')
        pickle.dump(self, f)
        f.close()
        print("序列化文件存储完成！")

    @staticmethod
    def system_inputBinaryFile(filepath):
        f = open(filepath, 'rb')
        sys = pickle.load(f)
        f.close()
        print("序列化文件读取完成！")
        return sys