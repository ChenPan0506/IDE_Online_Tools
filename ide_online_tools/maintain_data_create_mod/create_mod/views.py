# -*- coding:utf-8 -*-
import uuid
import time
import jpype
import numpy as np
import pandas as pd
import re, copy
import collections
from pyhanlp import *
from styleframe import StyleFrame, Styler
from pandas.io.json import json_normalize
from flask import request, json, send_from_directory
from settings import Config
from .self_package import upload_mod
from . import c_mod


# 词库字典路径
user_words_dict_path = Config.ROOT_PATH + '/data/NLP/user/dictionary/user_words.txt'
stop_words_dict_path = Config.ROOT_PATH + '/data/NLP/user/dictionary/stop_words.txt'
synonym_words_dict_path = Config.ROOT_PATH + '/data/NLP/user/dictionary/synonym_words.txt'
init_synonym_words_dict_path = Config.ROOT_PATH + '/data/NLP/public/dictionary/init_synonym_words.txt'
init_user_words_dict_path = Config.ROOT_PATH + '/data/NLP/public/dictionary/init_user_words.txt'
init_stop_words_dict_path = Config.ROOT_PATH + '/data/NLP/public/dictionary/init_stop_words.txt'

# 文件处理保存路径
upload_path = Config.ROOT_PATH + '/data/NLP/user/deal_with/upload'
analyze_data_save_path = Config.ROOT_PATH + '/data/NLP/user/deal_with/analyze_data'
display_data_save_path = Config.ROOT_PATH + '/data/NLP/user/deal_with/display_data'
revise_data_save_path = Config.ROOT_PATH + '/data/NLP/user/deal_with/revise_data'
template_data_path = Config.ROOT_PATH + '/data/NLP/public'


print(user_words_dict_path)
stop_words = [line.strip() for line in open(init_stop_words_dict_path, encoding='utf-8').readlines()]
parser = JClass('com.hankcs.hanlp.dependency.nnparser.NeuralNetworkDependencyParser')  # 调用原始类接口进行句法分析


# ——————————————————————————————————————————文件读取函数———————————————————————————————————————
def read_files(path, part):
    data = pd.read_excel(path, header=0, index_col=0, sheet_name='all_data')
    parts_name = part
    data.set_index(['主损件名称'], inplace=True)
    if len(parts_name) > 0:
        parts_data = data.loc[parts_name].reset_index(drop=False)
        parts_data.dropna(axis=0, how='all', inplace=True)
        parts_data.replace(np.nan, 0, inplace=True)
        count_data = parts_data.groupby(['主损件名称']).size().reset_index().rename(columns={0: '频率'})
        combine_data = pd.merge(parts_data, count_data, how='outer').sort_values(by=['频率', '主损件名称'], ascending=False)
        sort_data = combine_data[['主损件名称', '故障描述', '原因分析', '频率']].reset_index(drop=True)
    else:
        parts_data = data.reset_index(drop=False)
        parts_data.dropna(axis=0, how='all', inplace=True)
        parts_data.replace(np.nan, 0, inplace=True)
        count_data = parts_data.groupby(['主损件名称']).size().reset_index().rename(columns={0: '频率'})
        combine_data = pd.merge(parts_data, count_data, how='outer').sort_values(by=['频率', '主损件名称'], ascending=False)
        sort_data = combine_data[['主损件名称', '故障描述', '原因分析', '频率']].reset_index(drop=True)
    return sort_data


# —————————————————————————————————————————分词和删除停用词函数————————————————————————————————————
def segmentor1(sentence):
    cut_word = HanLP.segment(str(sentence))
    cut_words = [w for w in cut_word if re.match(r"^[\u4E00-\u9FA5A-Za-z]+$", w.word)]
    words = [x for x in cut_words if x.word not in stop_words]
    return words


def segmentor2(sentence):
    patternes = [r'\((.*)?\)', r'（(.*)?）']
    for pattern in patternes:
        sentence = re.sub(pattern, '', sentence)
    cut_word = HanLP.segment(str(sentence))
    words = [x for x in cut_word if x.word not in stop_words]
    j_tokens = jpype.java.util.ArrayList()
    for token in words:
        j_tokens.add(token)
    return j_tokens


# ————————————————————————————————————————————词频统计类——————————————————————————————————————
class words_fleq_count():
    def __init__(self, data):
        self.data = data

    def count_pos(self, segmentor_list, pos_list):
        nature_list_n = []
        for token in segmentor_list:
            if str(token.nature) in pos_list:
                nature_list_n.append(token.word)
        return str(nature_list_n)[1:-1]

    def count_pos_sort(self):
        dict1 = {'名词': ['n', 'nz'], '形容词': ['a'], '动词': ['v', 'vi', 'vn'], '方位词': ['f']}
        new_data = self.data.loc[:, ['故障描述_分词', '原因分析_分词']]
        parts_name = self.data.loc[0, '主损件名称']
        col_name = ['故障描述', '原因分析']
        for i in col_name:
            for (key, values) in dict1.items():
                new_data[i + '_' + key] = new_data[i + '_分词'].apply(
                    lambda x: self.count_pos(segmentor_list=x, pos_list=values))
        count_name = ['故障描述_名词', '故障描述_形容词', '故障描述_动词', '故障描述_方位词', '原因分析_名词',
                      '原因分析_形容词', '原因分析_动词', '原因分析_方位词']
        df_count_pos_words = pd.DataFrame(columns=['词性词频统计'])
        for i in count_name:
            words = ','.join(new_data[i]).replace(' ', '').replace("'", '').split(',')
            df_count_words = pd.DataFrame(collections.Counter(words).most_common(), columns=[i, i + '_次数'])
            df_count_words.drop(index=df_count_words[df_count_words[i] == ''].index[0], inplace=True)
            df_count_words.reset_index(drop=True, inplace=True)
            df_count_pos_words = pd.concat([df_count_pos_words, df_count_words], axis=1, join='outer')
        save_time = time.strftime("-%Y%m%d%H%M%S-", time.localtime())
        save_path = Config.ROOT_PATH + './data/NLP/optimize/count_pos_words' + save_time + str(uuid.uuid4()) + '.xlsx'
        df_count_pos_words.to_excel(save_path, sheet_name='词性词频统计', index=False, header=True)
        return df_count_pos_words


# ——————————————————————————————————————————词性分析过滤函数—————————————————————————————————————
def posttagger_process(segmentor_list):
    num_pos = 0
    words_list = []
    if len(segmentor_list) < 4:
        words_list.extend([x.word for x in segmentor_list])
    else:
        for i, token in enumerate(segmentor_list):
            if len(words_list) == 0:
                if str(token.nature) in ['n', 'nz', 'r', 'nx']:
                    words_list.append(token.word)
            else:
                if str(token.nature) in ['f', 'd', 'an']:
                    words_list.append(token.word)
                if str(token.nature) in ['v', 'vi', 'vn', 'a']:
                    if num_pos < 3:
                        words_list.append(token.word)
                        num_pos += 1
                if str(token.nature) in ['n', 'nz']:
                    words_list.append(token.word)
                    num_pos = 0
    return words_list


# ————————————————————————————————————————————构建近义词字典————————————————————————————————————
def synonyms_dict():
    combine_dict = {}
    for line in open(init_synonym_words_dict_path, "r"):
        seperate_word = line.strip().split("\t")
        num = len(seperate_word)
        for i in range(1, num):
            combine_dict[seperate_word[i]] = seperate_word[0]
    return combine_dict


# ————————————————————————————————————————————近义词替换函数————————————————————————————————————
def synonyms_exchange(segmentor_list):
    combine_dict = synonyms_dict()
    final_sentence = ''
    for token in segmentor_list:
        if token in combine_dict:
            token = combine_dict[token]
            if token != final_sentence[-len(token):]:
                final_sentence += token
        else:
            if token != final_sentence[-len(token):]:
                final_sentence += token
    return final_sentence


def rule_word(word, new_sentence, word_array, num, tree):
    if len(new_sentence) > 0 and new_sentence[-1] == "故障码":
        if num + 1 < len(word_array) and word.POSTAG == "nx" and word_array[num+1].POSTAG == "m":
            new_sentence.append(word.LEMMA + word_array[num+1].LEMMA + "，")
    elif num + 1 < len(word_array) and word.POSTAG == "m" and word_array[num+1].POSTAG == "转":
        new_sentence.append(word.LEMMA)
    elif word.POSTAG in ["nx", "ns", "m", "w", "b",  "q"]:
        pass
    elif num + 1 < len(word_array) and word.LEMMA == "缸" and word_array[num+1].POSTAG in ["n", "nz"]:
        pass
    else:
        if word.DEPREL == "HED":
            new_sentence.append(word.LEMMA)
        if word.DEPREL == "COO":
            if tree.findChildren(word).isEmpty() and word.POSTAG not in ["n", "vi", "v"]:
                pass
            else:
                new_sentence.append(word.LEMMA)
        if word.DEPREL == "CMP":
            new_sentence.append(word.LEMMA)
        if word.DEPREL == "SBV":
            new_sentence.append(word.LEMMA)
        if word.DEPREL == "ADV":
            if num + 1 < len(word_array) and word_array[num+1].DEPREL == word.HEAD.DEPREL:
                new_sentence.append(word.LEMMA)
            elif word.POSTAG == "v" or word.POSTAG == "a":
                new_sentence.append(word.LEMMA)
        if word.DEPREL == "ATT":
            if num + 1 < len(word_array) and word.POSTAG not in ["m", "mq", "rz"]:
                if word_array[num+1].DEPREL in [word.HEAD.DEPREL, "ADV", "SBV", "ATT", "WP"]:
                    new_sentence.append(word.LEMMA)
        if word.DEPREL == "VOB":
            new_sentence.append(word.LEMMA)
        if word.DEPREL == "POB":
            if word.POSTAG in ["n", "v", "vi"]:
                new_sentence.append(word.LEMMA)
        if word.DEPREL == "LAD" and word.POSTAG == "cc":
            new_sentence.append(word.LEMMA)
    return new_sentence


def analyze_dependency_parser(sentence):
    new_sentence = []
    tree = parser.compute(sentence)
    word_array = tree.getWordArray()
    pos_list = [n.POSTAG for n in word_array]
    nn_list = ['n', 'nz', 'r', 'nx', 'vn']
    bk_list = ['致', '导致', '致使', '造成', '使', '属', '属于', '引起', '而', "引发", "引致", "所至"]
    ps_list = ["无法使用", "无法正常使用", "不能正常使用", "不能使用"]
    if set(pos_list) & set(nn_list):
        for num, word in enumerate(word_array):
            if word.LEMMA in bk_list:
                if len(new_sentence) == 0:
                    pass
                else:
                    break
            elif word.LEMMA in ps_list:
                pass
            elif len(new_sentence) == 0:
                if num + 1 < len(word_array) and word.POSTAG == "nx" and word_array[num + 1].POSTAG == "m":
                    new_sentence.append(word.LEMMA + word_array[num + 1].LEMMA)
                elif word.POSTAG in ['n', 'nz', 'r', 'nx', 'vn']:
                    if num - 1 >= 0 and word_array[num - 1].POSTAG in ["v", "d"]:
                        if word_array[num - 1].LEMMA not in bk_list:
                            new_sentence.append(word_array[num - 1].LEMMA)
                    if num + 1 < len(word_array) and word.LEMMA == "缸" and word_array[num + 1].POSTAG in ["n", "nz"]:
                        pass
                    else:
                        new_sentence.append(word.LEMMA)
            elif len(new_sentence) > 0 and word.LEMMA != new_sentence[-1]:
                rule_word(word, new_sentence, word_array, num, tree)
    else:
        for num, word in enumerate(word_array):
            if word.LEMMA in bk_list:
                if len(new_sentence) == 0:
                    pass
                else:
                    break
            elif len(new_sentence) > 0:
                if word.LEMMA != new_sentence[-1]:
                    rule_word(word, new_sentence, word_array, num, tree)
            else:
                rule_word(word, new_sentence, word_array, num, tree)
    new_sentence = sorted(set(new_sentence), key=new_sentence.index)
    return new_sentence


def describe_dependency_parser(sentence):
    new_sentence = []
    tree = parser.compute(sentence)
    word_array = tree.getWordArray()
    pos_list = [n.POSTAG for n in word_array]
    nn_list = ['n', 'nz', 'r', 'nx', 'vn']
    excl_list = ['致', '导致', '致使', '造成', '使', '属', '属于', '引起', '而', "引发", "引致", "所至"]
    apd_list = ['致', '导致', '致使', '造成', '使', '引起', '而', "引发", "引致", "所至"]
    bk_list = ['属', '属于']
    if set(pos_list) & set(nn_list):
        for num, word in enumerate(word_array):
            if len(new_sentence) == 0:
                if num + 1 < len(word_array) and word.POSTAG == "nx" and word_array[num + 1].POSTAG == "m":
                    new_sentence.append(word.LEMMA + word_array[num + 1].LEMMA)
                elif word.POSTAG in ['n', 'nz', 'r', 'nx', 'vn']:
                    if num - 1 >= 0 and word_array[num - 1].POSTAG in ["v", "d"]:
                        if word_array[num - 1].LEMMA not in excl_list:
                            new_sentence.append(word_array[num - 1].LEMMA)
                    if num + 1 < len(word_array) and word.LEMMA == "缸" and word_array[num + 1].POSTAG in ["n", "nz"]:
                        pass
                    else:
                        new_sentence.append(word.LEMMA)
            elif word.LEMMA in apd_list:
                new_sentence.append('，')
            elif word.LEMMA in bk_list:
                break
            elif len(new_sentence) > 0 and word.LEMMA != new_sentence[-1]:
                rule_word(word, new_sentence, word_array, num, tree)
    else:
        for num, word in enumerate(word_array):
            if word.LEMMA in apd_list:
                new_sentence.append('，')
            elif word.LEMMA in bk_list:
                break
            elif len(new_sentence) > 0:
                if word.LEMMA != new_sentence[-1]:
                    rule_word(word, new_sentence, word_array, num, tree)
            else:
                rule_word(word, new_sentence, word_array, num, tree)
    new_sentence = sorted(set(new_sentence), key=new_sentence.index)
    return new_sentence


# ————————————————————————————————————————————数据处理主函数————————————————————————————————————
def creat_new_setence(data):
    analyse_names = [(describe_dependency_parser, '故障描述'), (analyze_dependency_parser, '原因分析')]
    for i in analyse_names:
        data[i[1] + '_分词'] = data[i[1]].apply(segmentor2)
        data[i[1] + '_句法分析'] = data[i[1]+'_分词'].apply(i[0])
        data[i[1] + '_同义词替换'] = data[i[1] + '_句法分析'].apply(synonyms_exchange)
    df_data_save = copy.deepcopy(data)
    save_time = time.strftime("-%Y%m%d%H%M%S-", time.localtime())
    save_path = Config.ROOT_PATH + '/data/NLP/optimize/process_data' + save_time + str(uuid.uuid4()) + '.xlsx'
    df_data_save.to_excel(save_path, sheet_name='句子提取', index=False, header=True)
    return data


# ——————————————————————————————————————————只取前3个原始数据进行展示—————————————————————————————————
def old_data_sort(data, sentence):
    manage_data = data.loc[sentence].values
    if len(manage_data.shape) > 1:
        data_to_list = list(set(manage_data[:, 0].tolist()))
        if len(data_to_list) > 3:
            choices_data = np.random.choice(data_to_list, size=3, replace=False)
            return str(choices_data)[1:-1]
        else:
            return str(data_to_list)[1:-1]
    else:
        choices_data = manage_data[0]
        return choices_data


# ——————————————————————————————————————————生成前端要求的样式函数——————————————————————————————————
def display_data_build(data, columns_name):
    stable_data = data[[columns_name[0], columns_name[1]]]
    stable_data = stable_data.dropna(axis=0, how='all', inplace=False)
    old_and_new_data = data[[columns_name[2], columns_name[3]]]
    old_and_new_data.set_index([columns_name[3]], inplace=True)
    stable_data.loc[:, columns_name[2]] = stable_data.loc[:, columns_name[0]].apply(lambda x: old_data_sort(data=old_and_new_data, sentence=x))
    last_data = stable_data[columns_name[:3]]
    return last_data


# ——————————————————————————————————————————生成json格式数据函数———————————————————————————————————
def creat_json_data(data, analyze_file_name):
    data.replace(np.nan, 0, inplace=True)
    data.replace(np.inf, 0, inplace=True)
    data = data.astype({'故障描述_处理后_频次': 'int', '原因分析_处理后_频次': 'int'})
    part_data = data.reset_index().applymap(str)
    describe_table = []
    analyze_table = []
    for i in range(len(part_data.index)):
        transform_data = part_data.loc[i].values.tolist()
        if transform_data[3] != '0':
            describe_table_row = {"serialNumber": i+1, "partsName": transform_data[1], "extractResult": transform_data[2],
                                  "frequency": transform_data[3], "primaryData": transform_data[4], "confirmModify": transform_data[5]}
            describe_table.append(describe_table_row)
        if transform_data[7] != '0':
            analyze_table_row = {"serialNumber": i+1, "partsName": transform_data[6], "extractResult": transform_data[7],
                                 "frequency": transform_data[8], "primaryData": transform_data[9], "confirmModify": transform_data[10]}
            analyze_table.append(analyze_table_row)
    dict_data = {"code": 0, "msg": "success", "data": {"analyzeFileName": analyze_file_name, 'describeTable': describe_table, 'analyzeTable': analyze_table}}
    return dict_data


# —————————————————————————————————————————前端开始分析展示效果主函数—————————————————————————————————
def creat_display_data(data, file_name, part):
    process_list = ['故障描述', '原因分析']
    parts_names = data['主损件名称'].unique()
    new_index_data = data.set_index(['主损件名称'])
    analyze_save_time = time.strftime("-%Y%m%d%H%M%S-", time.localtime())
    analyze_data_save_name = 'analyze_data_' + part + analyze_save_time + file_name
    analyze_path = analyze_data_save_path+'/'+analyze_data_save_name
    writer = pd.ExcelWriter(analyze_path)
    all_data = pd.DataFrame(columns=['数据整理'])
    for num, i in enumerate(process_list):
        all_parts_data = pd.DataFrame(columns=['主损件名称', '频率', '故障描述', '原因分析', '故障描述_处理后',
                                               '原因分析_处理后', i + '_处理后_次数', i + '_处理后_统计', i + '_处理后_频次', '主损件名称_' + str(num+1)])
        display_data = pd.DataFrame(columns=[i + '_处理后_统计', i + '_处理后_频次', i, '主损件名称_' + str(num+1)])
        for parts_name in parts_names:
            setence_count = new_index_data.loc[parts_name].groupby([i + '_处理后']).size().reset_index().rename(columns={0: i + '_处理后_次数'})
            merge_data = pd.merge(new_index_data.loc[parts_name], setence_count, how='outer')\
                .sort_values(by=[i + '_处理后_次数', i + '_处理后'], ascending=False)
            setence_count_sort = new_index_data.loc[parts_name][i + '_处理后'].value_counts().reset_index().\
                rename(columns={'index': i + '_处理后_统计', i + '_处理后': i + '_处理后_频次'})
            setence_count_sort.loc[:, '主损件名称_' + str(num+1)] = str(parts_name)
            merge_data.reset_index(drop=True, inplace=True)
            concat_data = pd.concat([merge_data, setence_count_sort], axis=1)
            concat_data.loc[:, '主损件名称'] = str(parts_name)
            all_parts_data = pd.concat([all_parts_data, concat_data], axis=0, ignore_index=True, sort=False)
            select_data_columns_name = [i + '_处理后_统计', i + '_处理后_频次', i, i + '_处理后']
            display_data_part = display_data_build(concat_data, select_data_columns_name)
            display_data_part.loc[:, '主损件名称_' + str(num+1)] = str(parts_name)
            display_data = pd.concat([display_data, display_data_part], axis=0, ignore_index=True, sort=False)
        display_data = display_data.sort_values(by=[i + '_处理后_频次'], ascending=False)
        display_data.reset_index(drop=True, inplace=True)
        confirm_revise_data = display_data[[i + '_处理后_统计']].rename(columns={i + '_处理后_统计': '修改确认_' + str(num+1)})
        all_data = pd.concat([all_data, display_data, confirm_revise_data], axis=1)
        all_data[i + '_处理后_频次'] = all_data[i + '_处理后_频次'].astype('int')
        all_parts_data.to_excel(writer, sheet_name=i + '_处理后', index=True, header=True)
    writer.save()
    last_display_data = all_data[['主损件名称_1', '故障描述_处理后_统计', '故障描述_处理后_频次', '故障描述', '修改确认_1',
                                 '主损件名称_2', '原因分析_处理后_统计', '原因分析_处理后_频次', '原因分析', '修改确认_2']]
    display_data_js = creat_json_data(last_display_data, analyze_data_save_name)
    display_save_time = time.strftime("-%Y%m%d%H%M%S-", time.localtime())
    save_path = display_data_save_path+'/display_data_' + part + display_save_time + file_name
    last_display_data.to_excel(save_path, sheet_name='数据', index=True, header=True)
    return display_data_js


# ————————————————————————————————————————————句子比较函数—————————————————————————————————————
def compare_sentence(df, sentence):
    for i in range(len(df)):
        if df.loc[i, 'extractResult'] == sentence:
            if df.loc[i, 'extractResult'] == df.loc[i, 'confirmModify']:
                return sentence
            else:
                return df.loc[i, 'confirmModify']
        elif pd.isna(df.loc[i, 'extractResult']):
            break


# ——————————————————————————————————————————生成关联关系表格数据———————————————————————————————————
def creat_association_data(new_relation, parts_names):
    data = new_relation.set_index(['主损件名称_1'])
    new_relation_last_data = pd.DataFrame(columns=['序号', '主损件名称', '故障描述_确认后', '原因分析_确认后', '频次统计'])
    for part in parts_names:
        count_relation_data = data.loc[part][['故障描述_确认后', '原因分析_确认后']].groupby(
            ['故障描述_确认后', '原因分析_确认后'], sort=False)['原因分析_确认后'].count().to_frame(name='频次统计').reset_index()
        sort_relation_data = count_relation_data.groupby('故障描述_确认后', sort=False).apply(
            lambda x: x.sort_values('频次统计', ascending=False)).reset_index(drop=True).reset_index().rename(columns={'index': '序号'})
        sort_relation_data.loc[:, '主损件名称'] = part
        new_relation_last = sort_relation_data[['序号', '主损件名称', '故障描述_确认后', '原因分析_确认后', '频次统计']]
        new_relation_last_data = pd.concat([new_relation_last_data, new_relation_last], axis=0, ignore_index=True, sort=False)
    return new_relation_last_data


# ———————————————————————————————————————————————部件模型表格——————————————————————————————————
def creat_model_data(count_data, associat_data, parts_names, ew):
    for part in parts_names:
        table_head = pd.DataFrame({"部件编码": ["S00001", None], "部件名称": [part, "失效模式"], "症状类型": ["症状_失效概率频度", "FS"]})
        describe_data = count_data.set_index(['主损件名称_1']).loc[part][['故障描述_确认后', '频次_1']].reset_index(drop=True)
        describe_data['症状类型'] = '系统症状'
        trs_data = describe_data[['症状类型', '故障描述_确认后', '频次_1']].set_index(['症状类型']).T.reset_index(drop=True)
        right_last_data = pd.DataFrame({"输出": ["受影响的接口异常", "FO"]})
        right_data = pd.concat([table_head, trs_data, right_last_data], axis=1)
        right_table_data = right_data.T.reset_index().T.reset_index(drop=True)
        analyze_data = count_data.set_index(['主损件名称_2']).loc[part][['原因分析_确认后', '频次_2']].reset_index(drop=True)
        analyze_data['部件名称'] = part
        bottom_data = analyze_data[['部件名称', '原因分析_确认后', '频次_2']].rename(columns={'部件名称': 0, '原因分析_确认后': 1, '频次_2': 2})
        bottom_last_data = pd.DataFrame({0: ["输入"], 1: ["接口异常"], 2: ["IS"]})
        table_all_data = pd.concat([right_table_data, bottom_data, bottom_last_data], axis=0, ignore_index=True, sort=False)
        table_all_data.loc[table_all_data.index[-1], table_all_data.columns[-1]] = 'IO'
        centre_data = associat_data.set_index(['主损件名称']).loc[part][['故障描述_确认后', '原因分析_确认后', '频次统计']].reset_index(drop=True)
        x_table_all_data = copy.deepcopy(table_all_data)
        for n in range(len(centre_data)):
            i = np.where(table_all_data[1] == centre_data.loc[n, '原因分析_确认后'])[0][0]
            j = np.where(table_all_data.loc[1] == centre_data.loc[n, '故障描述_确认后'])[0][0]
            x_table_all_data.loc[i, j] = 'X'
            table_all_data.loc[i, j] = centre_data.loc[n, '频次统计']
        table_all_data.columns = table_all_data.columns.astype('str')
        sf_table = StyleFrame(table_all_data)
        sf_table.set_column_width_dict(col_width_dict={'0': 15, '1': 60, '2': 5})
        sf_table.set_column_width(columns=[str(x) for x in range(3, len(table_all_data.columns))], width=5)
        sf_table.apply_column_style(cols_to_style=table_all_data.columns,
                                    styler_obj=Styler(font_size=8, bg_color='white'), style_header=True)
        sf_table.apply_column_style(cols_to_style=['2', str(len(table_all_data.columns) - 1)],
                                    styler_obj=Styler(font_size=8, bg_color='grey'), style_header=True)
        sf_table.apply_style_by_indexes(indexes_to_style=[1, len(table_all_data) - 2],
                                        styler_obj=Styler(font_size=8, bg_color='grey'))
        sf_table.to_excel(ew, sheet_name='Model_'+part, index=False, header=False, columns_and_rows_to_freeze="C3")
        x_table_all_data.columns = x_table_all_data.columns.astype('str')
        sf_x_table = StyleFrame(x_table_all_data)
        sf_x_table.set_column_width_dict(col_width_dict={'0': 15, '1': 60, '2': 5})
        sf_x_table.set_column_width(columns=[str(x) for x in range(3, len(x_table_all_data.columns))], width=5)
        sf_x_table.apply_column_style(cols_to_style=x_table_all_data.columns,
                                      styler_obj=Styler(font_size=8, bg_color='white'), style_header=True)
        sf_x_table.apply_column_style(cols_to_style=['2', str(len(x_table_all_data.columns) - 1)],
                                      styler_obj=Styler(font_size=8, bg_color='grey'), style_header=True)
        sf_x_table.apply_style_by_indexes(indexes_to_style=[1, len(x_table_all_data) - 2],
                                          styler_obj=Styler(font_size=8, bg_color='grey'))
        sf_x_table.to_excel(ew, sheet_name='Model_X_'+part, index=False, header=False, columns_and_rows_to_freeze="C3")


# ———————————————————————————————————————————————生成部件模型——————————————————————————————————
@c_mod.route("/revise_data", methods=['POST', 'GET'])
def revise_data():
    receive_data = request.data.decode('utf-8')
    js_data = json.loads(receive_data)['data']
    analyze_file_name = js_data['analyzeFileName']
    analyze_file_path = analyze_data_save_path+'/'+analyze_file_name
    read_file = pd.ExcelFile(analyze_file_path)
    read_data = read_file.parse(sheet_name=0, usecols=['主损件名称', '故障描述_处理后', '原因分析_处理后'], header=0)
    revise_save_name = analyze_file_name.rsplit('analyze_data_', 1)[1]
    save_path = revise_data_save_path+'/revise_data_'+revise_save_name
    ew = StyleFrame.ExcelWriter(save_path)
    steps = [('describeTable', '故障描述'), ('analyzeTable', '原因分析')]
    all_new_relation = pd.DataFrame(columns=['new_relation'])
    all_count_data = pd.DataFrame(columns=['all_count_data'])
    parts_names = read_data['主损件名称'].unique()
    for num, step in enumerate(steps):
        df_data = json_normalize(js_data[step[0]]).set_index(['partsName'])
        df_data["frequency"] = df_data["frequency"].astype('int')
        all_parts_data = pd.DataFrame(columns=['主损件名称', step[1]+'_确认后', '频次'])
        all_parts_new_relation_data = pd.DataFrame(columns=['主损件名称', '故障描述_处理后', '原因分析_处理后',
                                                            "extractResult", "confirmModify", step[1]+'_确认后'])
        for part in parts_names:
            revise_save = df_data.loc[part][['confirmModify', 'frequency']].groupby('confirmModify').sum()\
                .sort_values(by=['frequency'], ascending=False).reset_index()
            revise_save['主损件名称'] = part
            revise_save_data = revise_save.rename(columns={'confirmModify': step[1]+'_确认后', 'frequency': '频次'})
            all_parts_data = pd.concat([all_parts_data, revise_save_data], axis=0, ignore_index=True, sort=False)

            revise_cal = df_data.loc[part].sort_values(by=['frequency'], ascending=False).reset_index()
            revise_cal_data = revise_cal[["extractResult", "confirmModify"]]
            old_data = read_data.set_index(['主损件名称']).loc[part].reset_index()
            concat_data = pd.concat([old_data, revise_cal_data], axis=1)
            concat_data[step[1]+'_确认后'] = concat_data[step[1]+'_处理后'].apply(lambda x: compare_sentence(concat_data, x))
            all_parts_new_relation_data = pd.concat([all_parts_new_relation_data, concat_data], axis=0, ignore_index=True, sort=False)
        all_parts_data_last = all_parts_data.sort_values(by=['频次'], ascending=False).reset_index(drop=True, inplace=False)
        all_parts_data_last = all_parts_data_last.reset_index().rename(columns={'index': '序号'})
        sf = StyleFrame(all_parts_data_last)
        sf.set_column_width_dict(col_width_dict={"序号": 10, "主损件名称": 15, step[1]+'_确认后': 62, "频次": 10})
        sf.to_excel(ew, sheet_name=step[1], index=True, header=True)

        new_relation_data = all_parts_new_relation_data[['主损件名称', step[1] + '_确认后']].rename(
            columns={'主损件名称': '主损件名称_' + str(num+1)})
        all_new_relation = pd.concat([all_new_relation, new_relation_data], axis=1)

        count_data = all_parts_data_last.rename(columns={"主损件名称": "主损件名称_"+str(num+1), "频次": "频次_"+str(num+1)})
        all_count_data = pd.concat([all_count_data, count_data], axis=1)
    association_table_data = creat_association_data(all_new_relation, parts_names)
    sf_relation = StyleFrame(association_table_data)
    sf_relation.set_column_width_dict(
        col_width_dict={"序号": 10, "主损件名称": 15, "故障描述_确认后": 62, "原因分析_确认后": 62, "频次统计": 10})
    sf_relation.to_excel(ew, sheet_name='关系统计', index=False, header=True)

    creat_model_data(all_count_data, association_table_data, parts_names, ew)
    ew.save()
    return {"code": 0, "msg": "success", "revise_save_name": revise_save_name}


# ————————————————————————————————————————————————开始运行分析—————————————————————————————————
@c_mod.route('/analyse', methods=['POST', 'GET'])
def analyse():
    file_name = request.args.get('file_name')
    read_path = upload_path + '/' + file_name
    part_name = request.args.get('part_name')
    print(read_path, part_name)
    read_data = read_files(read_path, part_name)
    new_setence = creat_new_setence(data=read_data)
    new_setence_f = new_setence[['主损件名称', '频率', '故障描述', '原因分析', '故障描述_同义词替换', '原因分析_同义词替换']]\
        .rename(columns={'故障描述_同义词替换': '故障描述_处理后', '原因分析_同义词替换': '原因分析_处理后'})
    new_setence_f.replace(np.nan, 0, inplace=True)
    new_setence_f.replace('', 0, inplace=True)
    table_data = creat_display_data(new_setence_f, file_name, part_name)
    return table_data


# ——————————————————————————————————————————————————文件下载—————————————————————————————————
@c_mod.route('/download_result', methods=['POST', 'GET'])
def download_result():
    revise_save_name = request.args.get('revise_save_name')
    filename = 'revise_data_'+revise_save_name
    directory = revise_data_save_path
    return send_from_directory(directory, filename, as_attachment=True)


# —————————————————————————————————————————————————模板文件下载————————————————————————————————
@c_mod.route("/download_template", methods=['POST', 'GET'])
def download_file():
    filename = 'template_data.xlsx'
    directory = template_data_path
    return send_from_directory(directory, filename, as_attachment=True)


# —————————————————————————————————————————————————上传接口返回————————————————————————————————
@c_mod.route('/upload', methods=['GET', 'POST'])
def upload_file():
    return upload_mod.Upload(path=upload_path).upload_file()
