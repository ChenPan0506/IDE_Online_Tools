from flask import current_app, Flask, request, jsonify, send_from_directory, abort
import os
import pandas as pd
from openpyxl import load_workbook
import re
import time
from loguru import logger
from . import m_check, check_function
from settings import Config
import json
from ast import literal_eval
import zipfile
from win32com.client import DispatchEx
import pythoncom


def just_open(filename):
    pythoncom.CoInitialize()
    try:
        xl_app = DispatchEx("Excel.Application")
        # xl_app.Visible = False
        xl_book = xl_app.Workbooks.Open(filename)
        xl_book.Save()
        xl_book.Close()
        xl_app.Quit()
    finally:
        if xl_app:
            xl_app.Quit()

    pythoncom.CoUninitialize()


@m_check.route('/run', methods=["POST", "GET"])
def model_check_views():
    all_data = request
    xl_file_uid = request.form['uid']
    xl_file = request.files['file']
    xl_file_name = xl_file.filename
    print(xl_file_name)
    point_loc = re.search(r".xls", xl_file_name).span()[0]

    # save_path = Config.MODEL_CHECK_RESULTS_PATH + xl_file_uid + "/" + xl_file_name[0:point_loc] + \
    #             time.strftime(' %y-%m-%d %H-%M-%S', time.localtime(time.time())) + "/"
    save_path = Config.MODEL_CHECK_RESULTS_PATH + "/" + xl_file_uid + "/" + xl_file_name[0:point_loc] + "/"
    file_name = xl_file_name[0:point_loc] + ".txt"
    save_xl_name = xl_file_name[0:point_loc] + ".xlsx"

    xl_file_workbook = load_workbook(xl_file)
    xl_file_data = pd.read_excel(xl_file, sheet_name=None, header=None)
    rename_stat, txt_content, dict_warning, dict_error, xl_file_workbook = \
        check_function.check_sheet(xl_file_data, xl_file_name, xl_file_workbook)

    logger.add(sink=save_path + file_name)
    logger.remove()
    with open(save_path + file_name, "w") as f:
        f.write(txt_content)

    if rename_stat:
        os.rename(
            save_path + file_name, save_path + file_name)
        xl_file_workbook.save(save_path + save_xl_name)
        just_open(save_path + save_xl_name)
        state = "pass"
    else:
        os.rename(
            save_path + file_name, save_path + "Error-" + file_name)
        xl_file_workbook.save(save_path + "Error-" + save_xl_name)
        just_open(save_path + "Error-" + save_xl_name)
        state = "notpass"

    response_msg = {
        "code": "20000",
        "uid": xl_file_uid,
        "name": xl_file_name,
        "state": state,
        "warning": dict_warning,
        "error": dict_error,
    }

    return response_msg


@m_check.route('/download', methods=["POST", "GET"])
def model_check_result():
    req = request
    req_data = json.loads(request.get_data(as_text=True))
    file_list = literal_eval(req_data['downloadFileList'])
    dl_uid = req_data['uuid']

    for item in file_list:
        point_loc = re.search(r".xls", item["dlName"]).span()[0]
        file_path = Config.MODEL_CHECK_RESULTS_PATH + "/" + str(item["dlGuid"]) + "/" + item["dlName"][0:point_loc]
        if os.path.isdir(file_path):
            pass
            # current_file_list = os.listdir(file_path)
            # for current_file_name in current_file_list:
            #     if current_file_name.endswith(".xlsx"):
            #         just_open(file_path + "/" + current_file_name)
        else:
            abort(404)

    # zipf_name = "download" + str(dl_uid) + time.strftime(' %y-%m-%d %H-%M-%S', time.localtime(time.time())) + ".zip"
    zipf_name = "download_" + str(dl_uid) + ".zip"
    zipf = zipfile.ZipFile(Config.MODEL_CHECK_RESULTS_PATH + "/" + zipf_name, "w", zipfile.ZIP_DEFLATED)
    for item in file_list:
        point_loc = re.search(r".xls", item["dlName"]).span()[0]
        file_path = Config.MODEL_CHECK_RESULTS_PATH + "/" + str(item["dlGuid"]) + "/" + item["dlName"][0:point_loc]
        current_file_list = os.listdir(file_path)
        for current_file_name in current_file_list:
            zipf.write(file_path + "/" + current_file_name, current_file_name)

    zipf.close()
    return send_from_directory(Config.MODEL_CHECK_RESULTS_PATH, zipf_name, as_attachment=True)
