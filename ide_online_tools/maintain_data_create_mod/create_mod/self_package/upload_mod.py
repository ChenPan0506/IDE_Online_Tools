# -*- coding:utf-8 -*-
import os
import uuid
import platform
import pandas as pd
from flask import request
from werkzeug.utils import secure_filename


class Upload:
    def __init__(self, path):
        if platform.system() == "Windows":
            self.slash = '\\'
        elif platform.system() == "Linux":
            self.slash = '/'
        self.path = path

    def upload_file(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        else:
            pass
        file = request.files['uploadFile']
        filename = secure_filename(file.filename)
        file_name = str(uuid.uuid4()) + '-' + filename
        file.save(os.path.join(self.path, file_name))
        read_file = pd.ExcelFile(file)
        part_name = read_file.parse(usecols=['主损件名称'])['主损件名称'].unique().tolist()
        file_path = self.path + self.slash + file_name
        print(file_path)
        text_area = str(part_name)[1:-1].replace("'", '')
        options = [{'value': x} for x in part_name]
        return_data = {'state': 1, 'text_area': text_area, 'options': options, 'file_name': file_name}
        return return_data

