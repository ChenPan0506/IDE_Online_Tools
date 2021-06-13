# 整体映射database数据库并写入model.py文件
flask-sqlacodegen mysql+pymysql://root:root@localhost/ide-2-3 --outfile model-0601.py --flask
# 映射table数据表并写入table.py文件
flask-sqlacodegen mysql+pymysql://root:root@localhost/ide-2-3 --table table_name --outfile table_name.py --flask