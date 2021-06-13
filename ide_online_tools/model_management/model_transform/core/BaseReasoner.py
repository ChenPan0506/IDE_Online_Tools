import pandas as pd
import numpy as np
from numpy import NaN
import copy
from functools import reduce


class BaseReasoner:
    """
    VDES: 基本推理机类

    """

    def __init__(self, basesystem):
        self.reasoner_name = basesystem.sysname + "_reasoner"
        self.sys_name = basesystem.sysname

        # 推理过程变量定义
        self.database = basesystem
        self.model_data = basesystem.sysdatatable[0]

        # 中间计算结果
        self.FM_list_output = pd.DataFrame()  # FM_list-输出表
        self.sy_maybe_found = []  # 可能同时存在的症状推荐表

        # 输出数据
        self.CA_list_output = pd.DataFrame()  # 维修-输出表
        self.Test_list_output = pd.DataFrame()  # 测试-输出表

    def fm_list_cal(self, sy_list):

        """
        通过输入的故障症状输出按照相关程度排序（降序）后的失效模式列表
        :param sy_list: 症状列表
        :return:
            FM_list_data: 失效模式列表,按照失效模式的综合概率降序排列
            sy_maybe_found_output: 输出可能还存在的症状供选择确认，反馈的格式与输入的sy_list相同

        输入sy_list格式为:
        [
        {
            "sy_name": "***"
            "sy_state": "***"
            "sy_kind": "***"
        },
        {
            "sy_name": "***"
            "sy_state": "***"
            "sy_kind": "***"
        },
        ]
        """

        sy_list_data = sy_list["DTC_input"] + sy_list["SY_input"]

        sy_data = self.model_data.iloc[0:2,
                  self.database.sys_full_cursor["症状_失效概率频度"][1] + 1:self.database.sys_full_cursor["输出"][1]]
        sy_data = sy_data.T
        sys_sy_col_num = list(sy_data[sy_data.loc[:, 0].apply(lambda x: x[-2:]) == "症状"].index.values)
        DTC_sy_col_num = list(sy_data[sy_data.loc[:, 0].apply(lambda x: x[0:4]) == "DTC_"].index.values)
        sy_DTC_col_num = list(np.hstack((sys_sy_col_num, DTC_sy_col_num)))
        sy_DTC_col_num.sort(reverse=False)

        # FS 区域数据
        main_reasoner_data = self.model_data.iloc[
                             self.database.sys_full_cursor["FS"][0] + 1:self.database.sys_full_cursor["IO"][0],
                             self.database.sys_full_cursor["FS"][1] + 1:self.database.sys_full_cursor["IO"][1]]
        # 计算变量定义
        col_num = [[] for x in range(0, len(sy_list_data))]
        col_num_sy0 = [[] for x in range(0, len(sy_list_data))]
        FM_list = [[] for x in range(0, len(sy_list_data))]
        Sy_confirm_nothappen = []

        X_unique_fm = []  # 单一 X 时候的列名
        FM_list_set = []
        sy_X_num = copy.deepcopy(sy_list_data)

        for i, sy in enumerate(sy_list_data):
            if sy["input_type"] == "SY":
                if sy["sy_state"] == "1":
                    col_num[i] = int(sy_data[sy_data.loc[:, 1] == sy["sy_name"]].index.values)
                    FM_list[i] = list(main_reasoner_data[main_reasoner_data.loc[:, col_num[i]] == "X"].index.values)
                    FM_list_set.extend(FM_list[i])
                    sy_X_num[i]["X_num"] = len(FM_list[i])  # 症状对应的X个数
                    if len(FM_list[i]) == 1:
                        X_unique_fm.append(FM_list[i][0])
                elif sy["sy_state"] == "0":
                    # 输入症状状态为0（未发生）时，统计对应的列索引  col_num_sy0
                    col_num_sy0[i] = int(sy_data[sy_data.loc[:, 1] == sy["sy_name"]].index.values)
                    col_num[i] = int(sy_data[sy_data.loc[:, 1] == sy["sy_name"]].index.values)
                    col_numsy_nothappen = int(sy_data[sy_data.loc[:, 1] == sy["sy_name"]].index.values)
                    FM_list[i] = list(
                        main_reasoner_data[main_reasoner_data.loc[:, col_numsy_nothappen] == "X"].index.values)
                    if len(FM_list[i]) == 1:
                        Sy_confirm_nothappen.append(FM_list[i][0])
                    else:
                        Sy_confirm_nothappen.extend(FM_list[i])
                else:
                    pass
            elif sy["input_type"] == "DTC":
                if sy["DTC_state"] == "1":
                    col_num[i] = int(sy_data[sy_data.loc[:, 0] == sy["DTC_code"]].index.values)
                    FM_list[i] = list(main_reasoner_data[main_reasoner_data.loc[:, col_num[i]] == "X"].index.values)
                    FM_list_set.extend(FM_list[i])
                    sy_X_num[i]["X_num"] = len(FM_list[i])  # 症状对应的X个数
                    if len(FM_list[i]) == 1:
                        X_unique_fm.append(FM_list[i][0])

        FM_list_set = list(set(FM_list_set))  # 获得所有的失效模式

        # 根据输入症状推测还可能存在的症状
        sy_maybe_found = self.model_data.loc[FM_list_set, sy_DTC_col_num]  # .count(axis=1)
        tmp = sy_maybe_found.isin(["X"]).any()
        sy_maybe_found_inx = list(tmp[tmp == True].index.values)
        # 删除已经输入的症状
        for x in col_num:
            if x and x in sy_maybe_found_inx:  # 排除输入  确认未发生症状  还有其DTC未删除，后续分表后修改提出，目前在UI端按照类型筛选显示。
                sy_maybe_found_inx.remove(x)
        # 可能发生的症状反馈
        sy_maybe_found_output = [[] for x in range(0, len(sy_maybe_found_inx))]
        for ii, cols in enumerate(sy_maybe_found_inx):
            sy_maybe_found_output[ii] = {"sy_name": self.model_data.iloc[1, cols], "sy_state": "2",
                                         "sy_kind": self.model_data.iloc[0, cols]}
        # FM_list 计算
        FM_list_data = copy.deepcopy(self.model_data.iloc[FM_list_set, 0:3])
        FM_list_data.columns = ["partname", "FM", "f"]
        col_num_tmp = copy.deepcopy(col_num)
        for iii, col_num_0 in enumerate(col_num_sy0):
            if col_num_0 != []:
                col_num_tmp.remove(col_num_0)

        FM_list_data["X_num"] = self.model_data.iloc[FM_list_data.index, col_num_tmp].count(axis=1)

        if len(X_unique_fm) == 0:
            FM_list_data["X_unique"] = 0
        elif len(X_unique_fm) > 0:
            FM_list_data["X_unique"] = 0
            for cols in X_unique_fm:
                for inx in FM_list_data.index.values:
                    if cols == inx:
                        FM_list_data.loc[inx, "X_unique"] = 1

        FM_list_data["F"] = FM_list_data.apply(BaseReasoner.F_FM_cal, axis=1)

        # 确认未发生的症状修改FM_list对应的系数值
        FM_list_data["index_num"] = FM_list_data.index
        # 求 交集
        modify_F_list = list(set(Sy_confirm_nothappen).intersection(set(copy.deepcopy(FM_list_data.index.values))))

        if modify_F_list:  # 如果没有需要FM参数的则跳过
            FM_list_data["F_modify"] = FM_list_data.apply(BaseReasoner.F_modify_sy_comfirm, indexs=modify_F_list,
                                                          axis=1)
        else:
            FM_list_data["F_modify"] = FM_list_data["F"]

        FM_list_data = FM_list_data.sort_values(by="F_modify", ascending=False)

        # sy_maybe_found_output 转换为dataframe格式
        sy_maybe_df = pd.DataFrame(np.zeros([len(sy_maybe_found_output), 4]))
        sy_maybe_df.columns = ["发生", "未发生", "症状类型", "症状描述"]
        sy_maybe_df["发生"] = 0
        sy_maybe_df["未发生"] = 0
        for inx, sy_maybe_tmp in enumerate(sy_maybe_found_output):
            sy_maybe_df.loc[inx, "症状类型"] = sy_maybe_tmp["sy_kind"]
            sy_maybe_df.loc[inx, "症状描述"] = sy_maybe_tmp["sy_name"]

        # 结果保存到类属性
        self.FM_list_output = FM_list_data
        self.sy_maybe_found = sy_maybe_df

        sy_maybe_df = sy_maybe_df[sy_maybe_df["症状类型"].isin(["系统症状", "部件症状"])]
        return sy_maybe_df, FM_list_data

    def ca_list_cal(self, add_info=None):
        FM_list_data = copy.deepcopy(self.FM_list_output)  # .sort_values(by="partname", ascending=False)
        # 判断是更新输出 还是第一次计算test_list
        if add_info == None:
            pass
        else:
            FM_list_data = self.FM_list_update(FM_list_data, add_info)
        part_include = set(FM_list_data["partname"].values)
        # 按照部件分别找到FM_list中的每个失效模式对应列索引
        fm_row_index = {}
        for i, partname in enumerate(part_include):
            fm_row_index[partname] = list(FM_list_data[FM_list_data.loc[:, "partname"] == partname].index.values)
        L_CA = pd.DataFrame()
        # 查询每个部件对应的维修步骤和对应的推荐系数
        for key, value in fm_row_index.items():
            fm_row_name = pd.DataFrame(FM_list_data.loc[value, ["FM", "F_modify"]])
            fm_row_name.columns = ["失效模式", "F_modify"]
            FM_CA_temp = self.database.parts_dict[key].sheets_list["05FM-CA"].data
            FM_CA_temp.columns = FM_CA_temp.iloc[0, :]
            CA_data = FM_CA_temp.merge(fm_row_name, on="失效模式", how="inner")
            tmp = CA_data.isna().all()
            tmp = list(tmp[tmp == True].index.values)
            CA_data = CA_data.drop(tmp, axis=1)

            l_CA = CA_data.apply(BaseReasoner.l_CA_cal, axis=1)  # CA_data["l_CA"]
            l_CA.columns = copy.deepcopy(CA_data.columns)
            l_CA = l_CA.apply(max, axis=0).drop(["失效模式", "F_modify"])  # ***可能要保存
            l_CA = pd.DataFrame(l_CA)
            l_CA["维修措施"] = l_CA.index
            l_CA.columns = ["l_CA", "维修措施"]

            # 查表 "04Corrective Action-Cost"  处理计算的L值重复的问题
            CAC_temp = copy.deepcopy(self.database.parts_dict[key].sheets_list["04Corrective Action-Cost"].data)
            CAC_temp.columns = CAC_temp.iloc[0, :]
            CAC_temp = CAC_temp.drop([0])
            l_CA = CAC_temp.merge(l_CA, on="维修措施", how="inner")
            L_CA = pd.concat([l_CA, L_CA], axis=0)

        L_CA = L_CA.reset_index(drop=True)
        L_CA.index = L_CA["维修措施"].values
        L_CA["L_CA"] = pd.DataFrame(BaseReasoner.L_CA_cal(L_CA["l_CA"]))

        CA_num = set(L_CA["L_CA"])
        if len(L_CA["L_CA"]) == len(CA_num):
            L_CA_output = copy.deepcopy(L_CA)
            L_CA_output = L_CA_output[["维修措施", "部件名称", "L_CA"]]
            L_CA_output.columns = ["维修动作", "部件", "推荐指数"]
            L_CA_output = L_CA_output.loc[:, ["推荐指数", "部件", "维修动作"]]
            F_CA_parts = L_CA_output.sort_values(by="推荐指数", ascending=False)

            F_CA_parts = F_CA_parts.reset_index(drop=True)
            F_CA_parts["序号"] = F_CA_parts.index.values
            F_CA_parts["维修指导"] = "查看指导"
            F_CA_parts["维修反馈"] = "已维修"
            F_CA_parts = F_CA_parts.loc[:, ["序号", "推荐指数", "部件", "维修动作", "维修指导", "维修反馈"]]
            F_CA_parts['推荐指数'] = F_CA_parts['推荐指数'].map(lambda x: ('%.2f') % x)
            F_CA_parts['序号'] = F_CA_parts['序号'].map(lambda x: int(x) + 1)

            self.F_CA_sys = F_CA_parts
            return F_CA_parts
        else:
            nums = [[] for x in CA_num]
            for inx, itm in enumerate(CA_num):
                for i in range(0, len(L_CA["L_CA"])):
                    if itm == L_CA["L_CA"][i]:
                        nums[inx].append((L_CA["维修措施"][i], L_CA["L_CA"][i]))
            for CAC_itm in nums:
                if len(CAC_itm) == 1:
                    pass
                else:
                    CA_with_sameF = pd.DataFrame(CAC_itm)  # F 值相等的维修措施dataframe
                    CA_with_sameF.columns = ["维修措施", "L_CA_duplicate"]
                    F_CA_duplicate = L_CA.merge(CA_with_sameF, on="维修措施", how="inner")
                    F_CA_duplicate["F_CA"] = F_CA_duplicate.apply(BaseReasoner.F_CA_cal,
                                                                  min=F_CA_duplicate["成本（元）"].min(), axis=1)
                    ccc = F_CA_duplicate[["维修措施", "F_CA"]]
                    for rows in range(0, ccc.shape[0]):
                        L_CA.loc[ccc.loc[rows, "维修措施"], "L_CA"] = ccc.loc[rows, "F_CA"]
            F_CA_parts = L_CA[["L_CA", "部件名称", "维修措施"]]

            F_CA_parts.columns = ["推荐指数", "部件", "维修动作"]
            F_CA_parts = F_CA_parts.reset_index(drop=True)
            F_CA_parts = F_CA_parts.loc[:, ["推荐指数", "部件", "维修动作"]]
            F_CA_parts = F_CA_parts.sort_values(by=["推荐指数", "部件"], ascending=(False, True), kind="mergesort")
            F_CA_parts = F_CA_parts.reset_index(drop=True)
            F_CA_parts["序号"] = F_CA_parts.index.values
            F_CA_parts["维修指导"] = "查看指导"
            F_CA_parts["维修反馈"] = "已维修"
            F_CA_parts = F_CA_parts.loc[:, ["序号", "推荐指数", "部件", "维修动作", "维修指导", "维修反馈"]]
            F_CA_parts['推荐指数'] = F_CA_parts['推荐指数'].map(lambda x: ('%.2f') % x)
            F_CA_parts['序号'] = F_CA_parts['序号'].map(lambda x: int(x) + 1)
            self.F_CA_sys = F_CA_parts
        return F_CA_parts

    def test_list_cal(self, add_info=None):
        FM_list_data = copy.deepcopy(self.FM_list_output)
        # 判断是更新输出 还是第一次计算test_list
        if add_info == None:
            pass
        else:
            FM_list_data = self.FM_list_update(FM_list_data, add_info)

        part_include = set(FM_list_data["partname"].values)
        # 按照部件分别找到FM_list中的每个失效模式对应列索引
        fm_row_index = {}
        for i, partname in enumerate(part_include):
            fm_row_index[partname] = list(FM_list_data[FM_list_data.loc[:, "partname"] == partname].index.values)
        test_ex_col_index = {}
        for j, partname in enumerate(part_include):
            tmp = list(range(self.database.sys_full_cursor["症状类别"][1], self.database.sys_full_cursor["输出"][1]))
            test_ex_col_index[partname] = list(
                self.model_data.loc[0, tmp][self.model_data.loc[0, tmp] == "Test_" + partname].index.values)
        T_Test_p_parts = pd.Series()

        # 查询每个部件对应的测试异常、测试项目
        for key, value in fm_row_index.items():
            fm_row_name = pd.DataFrame(FM_list_data.loc[value, ["FM", "F_modify"]])
            fm_row_name.columns = ["失效模式", "F_modify"]
            test_ex_data = self.model_data.iloc[fm_row_index[key], test_ex_col_index[key]]
            tmp111 = test_ex_data.isna().all().tolist()
            if False in tmp111:  # 去除异常    某个失效模式不对应Test项目
                test_ex_data.columns = self.model_data.iloc[1, test_ex_col_index[key]].to_list()
                test_ex_data = pd.concat([fm_row_name, test_ex_data], axis=1, ignore_index=False)
                qq = test_ex_data.columns
                test_ex_data = test_ex_data.apply(BaseReasoner.Test_ex_find_cal, axis=1)  # 可能需要保存
                test_ex_data.columns = qq
                tmp = test_ex_data.isna().all()
                tmp = list(tmp[tmp == True].index.values)
                test_ex_data = test_ex_data.drop(tmp, axis=1)  # 需要保留

                test_ex_itms = copy.deepcopy(test_ex_data)
                test_ex_itms = test_ex_itms.drop(["失效模式", "F_modify"], axis=1).replace([NaN], [-1])  # 保留

                test_ex_list = pd.DataFrame(test_ex_itms.apply(max, axis=0))
                test_ex_list["测试结果"] = test_ex_list.index
                test_ex_list.columns = ["L_T_Syk", "测试结果"]

                TRT_data_tmp = copy.deepcopy(
                    self.database.parts_dict[key].sheets_list["07TestResult-Test"].data)  # 回查使用
                TRT_data = copy.deepcopy(TRT_data_tmp)
                TRT_data.columns = TRT_data.iloc[0, :]
                TRT_data = TRT_data.merge(test_ex_list, on="测试结果", how="inner")  # 维修动作查询表
                qq2 = TRT_data.columns
                TRT_data = TRT_data.apply(BaseReasoner.Test_action_find_cal, axis=1)
                TRT_data.columns = qq2

                tmp = TRT_data.isna().all()
                tmp = list(tmp[tmp == True].index.values)
                TRT_data = TRT_data.drop(tmp, axis=1)  # 需要保留

                TRT_itm = copy.deepcopy(TRT_data)
                TRT_itm = TRT_itm.drop(["测试结果", "结果判定", "L_T_Syk"], axis=1).replace([NaN], [-1])
                TRT_itm = pd.DataFrame(TRT_itm.apply(max, axis=0))
                # TRT_itm["测试项目"] = TRT_itm.index
                TRT_itm.columns = ["t_Test_p"]
                TRT_itm["部件"] = key
                T_Test_p_parts = pd.concat([T_Test_p_parts, TRT_itm], axis=0, sort=True)

        if T_Test_p_parts.size != 0:
            T_Test_p_parts = T_Test_p_parts[["t_Test_p", "部件"]]
            temp = T_Test_p_parts["t_Test_p"][T_Test_p_parts["t_Test_p"] < 100]
            T_Test_p_parts["T_Test_p"] = T_Test_p_parts.apply(BaseReasoner.T_Test_p_cal, sum=temp.sum(), axis=1)
            T_Test_p_parts["检测项目"] = T_Test_p_parts.index
            T_Test_p_parts = T_Test_p_parts.loc[:, ["T_Test_p", "部件", "检测项目"]]
            T_Test_p_parts.columns = ["推荐指数", "部件", "检测项目"]
            T_Test_p_parts = T_Test_p_parts.sort_values(by=["推荐指数", "部件"], ascending=(False, True), kind="mergesort")
            T_Test_p_parts = T_Test_p_parts.reset_index(drop=True)
            T_Test_p_parts["序号"] = T_Test_p_parts.index.values
            T_Test_p_parts["检测指导"] = "查看指导"
            T_Test_p_parts["检测反馈"] = "反馈检测结果"
            T_Test_p_parts = T_Test_p_parts.loc[:, ["序号", "推荐指数", "部件", "检测项目", "检测指导", "检测反馈"]]
            T_Test_p_parts['推荐指数'] = T_Test_p_parts['推荐指数'].map(lambda x: ('%.2f') % x)
            T_Test_p_parts['序号'] = T_Test_p_parts['序号'].map(lambda x: int(x) + 1)
            self.T_Test_sys = T_Test_p_parts

            # 检测项目输出
            test_result_response = {}
            for test_itme_index in range(T_Test_p_parts.shape[0]):
                if T_Test_p_parts.iloc[test_itme_index, 2] in test_result_response:
                    pass
                else:
                    test_result_response[T_Test_p_parts.iloc[test_itme_index, 2]] = {}

                if T_Test_p_parts.iloc[test_itme_index, 3] in test_result_response[
                    T_Test_p_parts.iloc[test_itme_index, 2]]:
                    pass
                else:
                    test_result_response[T_Test_p_parts.iloc[test_itme_index, 2]][
                        T_Test_p_parts.iloc[test_itme_index, 3]] = {}
                testlist_tmp = copy.deepcopy(
                    self.database.parts_dict[T_Test_p_parts.iloc[test_itme_index, 2]].sheets_list[
                        "07TestResult-Test"].data)
                testlist_tmp.columns = testlist_tmp.loc[0, :]

                ccc = testlist_tmp["测试结果"][testlist_tmp[T_Test_p_parts.iloc[test_itme_index, 3]] == "X"]
                for testitms in ccc:
                    test_result_response[T_Test_p_parts.iloc[test_itme_index, 2]][
                        T_Test_p_parts.iloc[test_itme_index, 3]][testitms] = [0]

            return T_Test_p_parts, test_result_response
        else:
            return pd.DataFrame(), pd.DataFrame()

    def FM_list_update(self, FM_list, add_info):
        # 测试反馈 更新FM list
        if len(add_info["Test_response"]) > 0:
            test_name_list_1 = []
            test_partname_list_1 = []
            test_name_list_0 = []
            test_partname_list_0 = []
            for test_itm in add_info["Test_response"]:
                if test_itm["response_type"] == "Test":
                    test_temp = self.database.parts_dict[test_itm["part_name"]].sheets_list["07TestResult-Test"].data
                    test_temp.columns = test_temp.loc[0, :]
                    testitm_list_update = test_temp[["测试结果", "结果判定"]][test_temp[test_itm["Test_action"]] == "X"]
                    for inxs in testitm_list_update.index:
                        if testitm_list_update.loc[inxs, "测试结果"] == test_itm["Test_resp_result"] and \
                                testitm_list_update.loc[inxs, "结果判定"] == 1:
                            test_name_list_1.append(test_itm["Test_resp_result"])
                            test_partname_list_1.append(test_itm["part_name"])
                        elif testitm_list_update.loc[inxs, "测试结果"] == test_itm["Test_resp_result"] and \
                                testitm_list_update.loc[inxs, "结果判定"] == 0:
                            for inxss in testitm_list_update.index:
                                if testitm_list_update.loc[inxss, "测试结果"] != test_itm["Test_resp_result"]:
                                    test_name_list_0.append(testitm_list_update.loc[inxss, "测试结果"])
                                    test_partname_list_0.append(test_itm["part_name"])

            # 修改反馈的正常测试项目对应的失效模式F_modify系数为0
            test_fm_data = copy.deepcopy(
                self.model_data.loc[0:self.database.sys_full_cursor["IO"][0], 0:self.database.sys_full_cursor["IO"][1]])
            fm_list_update_test_0 = []
            if len(test_partname_list_0) == 0:  # 有勾选测试正常项目
                pass
            else:
                for partname_0, test_0 in zip(test_partname_list_0, test_name_list_0):
                    test_fm_data = test_fm_data.T
                    tmp3 = test_fm_data.loc[:, 0:1]
                    test_fm_data.index = tmp3.apply(lambda x: ','.join(x), axis=1)
                    test_fm_data = test_fm_data.T
                    tmp4 = test_fm_data.iloc[:, 0:2][test_fm_data[",".join(["Test_" + partname_0, test_0])] == "X"]
                    tmp4.columns = ["partname", "FM"]
                    fm_list_update_test_0.append(tmp4)
                if len(fm_list_update_test_0) > 0:
                    fm_df_update_test_0 = reduce(BaseReasoner.fm_concat, fm_list_update_test_0)
                    fm_df_update_test_0 = fm_df_update_test_0.drop_duplicates()
                    for inxx0 in fm_df_update_test_0.index:
                        if inxx0 in FM_list.index.values.tolist():
                            FM_list.loc[inxx0, "F_modify"] = 0
                            print("修改了正常测试反馈对应的FM_list")
                        else:
                            FM_list.loc[inxx0, "F_modify"] = 0
                            FM_list.loc[inxx0, "partname"] = fm_df_update_test_0.loc[inxx0, "partname"]
                            FM_list.loc[inxx0, "FM"] = fm_df_update_test_0.loc[inxx0, "FM"]

            # 修改反馈的异常测试项目对应的失效模式F_modify系数为100
            test_fm_data = copy.deepcopy(self.model_data.loc[0:self.database.sys_full_cursor["IO"][0] - 1,
                                         0:self.database.sys_full_cursor["IO"][1] - 1])
            fm_list_update_test_1 = []
            if len(test_partname_list_1) == 0:  # 有勾选测试异常项目
                pass
            else:
                for partname_1, test_1 in zip(test_partname_list_1, test_name_list_1):
                    test_fm_data = test_fm_data.T
                    tmp1 = test_fm_data.loc[:, 0:1]
                    test_fm_data.index = tmp1.apply(lambda x: ','.join(x), axis=1)
                    test_fm_data = test_fm_data.T
                    tmp2 = test_fm_data.iloc[:, 0:2][test_fm_data[",".join(["Test_" + partname_1, test_1])] == "X"]
                    tmp2.columns = ["partname", "FM"]
                    fm_list_update_test_1.append(tmp2)

                if len(fm_list_update_test_1) > 0:
                    fm_df_update_test_1 = reduce(BaseReasoner.fm_concat, fm_list_update_test_1)
                    fm_df_update_test_1 = fm_df_update_test_1.drop_duplicates()
                    for inxx1 in fm_df_update_test_1.index:
                        if inxx1 in FM_list.index.values.tolist():
                            FM_list.loc[inxx1, "F_modify"] = 100
                            print("修改了异常测试反馈对应的FM_list")
                        else:
                            FM_list.loc[inxx1, "F_modify"] = 100
                            FM_list.loc[inxx1, "partname"] = fm_df_update_test_1.loc[inxx1, "partname"]
                            FM_list.loc[inxx1, "FM"] = fm_df_update_test_1.loc[inxx1, "FM"]


        else:
            print("没有测试反馈")

        # 维修反馈 更新FM list

        if len(add_info["CA_response"]) > 0:
            for ca_itm in add_info["CA_response"]:
                if ca_itm["response_type"] == "CA":
                    ca_temp = self.database.parts_dict[ca_itm["part_name"]].sheets_list["05FM-CA"].data
                    ca_temp.columns = ca_temp.loc[0, :]
                    fm_list_update_ca = ca_temp["失效模式"][ca_temp[ca_itm["CA_action"]] == "X"]
                    # fm_tobe_modify = FM_list["FM"][FM_list["partname"] == ca_itm["part_name"]]
                    fm_tmp = self.model_data.iloc[3:, 0:2]
                    fm_tmp.columns = self.model_data.loc[2, 0:1]
                    fm_tmp["组合"] = fm_tmp.apply(lambda x: ",".join(x), axis=1)
                    for value in fm_list_update_ca:
                        inx = fm_tmp["组合"][fm_tmp["组合"] == ",".join([ca_itm["part_name"], value])].index.values[0]
                        if inx in FM_list.index.values.tolist():
                            FM_list.loc[inx, "F_modify"] = 0
                            print("修改了 维修项目对应的FM_list")
                        else:
                            FM_list.loc[inx, "F_modify"] = 0
                            FM_list.loc[inx, "partname"] = ca_itm["part_name"]
                            FM_list.loc[inx, "FM"] = value
                            print("增加了 维修项目对应的FM_list")


        else:
            print("没有维修反馈")
        return FM_list.sort_values(by="F_modify", ascending=False)

    @staticmethod
    def F_modify_sy_comfirm(Serieslike, indexs=[]):
        if Serieslike["index_num"] in indexs and Serieslike["F"] != 100:
            return Serieslike["F"] * 0.5
        else:
            return Serieslike["F"]

    @staticmethod
    def T_Test_p_cal(Serieslike, sum=0):
        if Serieslike["t_Test_p"] == 100:
            return 100
        elif sum == 0:
            return 0
        else:
            return 10 * float(Serieslike["t_Test_p"]) ** 0.5

    @staticmethod
    def Test_action_find_cal(Serieslike):
        result = [[] for x in range(0, len(Serieslike))]
        for i, ser in enumerate(Serieslike):
            if ser == "X":
                result[i] = Serieslike["L_T_Syk"]
            else:
                result[i] = ser
        return pd.Series(result)

    @staticmethod
    def Test_ex_find_cal(Serieslike):
        result = [[] for x in range(0, len(Serieslike))]
        for i, ser in enumerate(Serieslike):
            if ser == "X":
                result[i] = Serieslike["F_modify"]
            else:
                result[i] = ser
        return pd.Series(result)

    # 程序中间计算系数、推荐系数等的方法
    @staticmethod
    def F_FM_cal(Serieslike):
        f = Serieslike["f"]
        X_num = Serieslike["X_num"]
        X_unique = Serieslike["X_unique"]
        if X_unique == 1:
            return 100
        else:
            return min(99, f * X_num ** 3)

    @staticmethod
    def l_CA_cal(Serieslike):
        result = [[] for x in range(0, len(Serieslike))]
        for i, ser in enumerate(Serieslike):
            if i == 0 or i == len(Serieslike):
                result[i] = -1
            else:
                if ser == "X":
                    result[i] = Serieslike["F_modify"]
                else:
                    result[i] = -1
        return pd.Series(result)

    @staticmethod
    def L_CA_cal(l_CA):
        L_CA = copy.deepcopy(l_CA)
        times_100 = l_CA.to_list().count(100)
        for inx, v in zip(l_CA.index, l_CA.values):
            if v == 100:
                L_CA[inx] = 100
            elif 0 < v < 100:
                L_CA[inx] = (v / (l_CA.sum() - 100 * times_100)) * 100
            elif v == 0:
                L_CA[inx] = 0
        return L_CA

    @staticmethod
    def F_CA_cal(Serieslike, min=0):
        return Serieslike["L_CA"] * (0.3 * (min / Serieslike["成本（元）"]) + 0.7)

    @staticmethod
    def fm_concat(df1, df2, axis1=0):
        return pd.concat([df1, df2], axis=axis1)

    @staticmethod
    def find_index(df, itm):
        x = -1
        y = -1
        if isinstance(df, pd.DataFrame):
            for xx in df.index:
                for yy in df.columns:
                    if df.iloc[xx, yy] == itm:
                        y = yy
                        x = xx

        elif isinstance(df, pd.Series):
            y = -1
            for xx in df.index:
                if df[xx] == itm:
                    x = xx
        return (x, y)

    @staticmethod
    def str4(string):
        return string[0:5]
