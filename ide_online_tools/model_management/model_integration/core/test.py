from BaseSystem import BaseSystem
import time
import pickle
import pandas as pd

if __name__ == "__main__":
    ts = time.time()

    file_dir = "C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\model_files\\final_test_model_20200422\\Model\\"
    relation_filename = "C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\model_files" \
                        "\\final_test_model_20200422\\Model\\Netlist_TS0001_测试系统.xlsx"

    # 输入
    #     # SCR
    #     file_dir = "./SCR-2/"
    #     relation_filename = "./SCR-2/Netlist_SCR00001_SCR系统.xlsx"

    # # HVC
    # file_dir = "./热管理系统-191227/"
    # relation_filename = "./热管理系统-191227/Netlist_SV000000TH_热管理系统1211.xlsx"

    # # SCR&HVC
    # file_dir = "./SCR&HVC/"
    # relation_filename = "./SCR&HVC/Netlist_SCR&HVC00001_SCR&HVC系统.xlsx"

    # 系统创建测试
    sys = BaseSystem()
    sys.creatsys(file_dir, relation_filename)
    sys.Model_data_integration()

    writer = pd.ExcelWriter("C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\output/BCOOL0511-jixie-sys.xlsx", engine='xlsxwriter')
    sys.sysdatatable[0].to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
    writer.save()
    writer.close()

    sys.duplicate_sy_merge()

    writer = pd.ExcelWriter("C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\output/BCOOL0511-merge-sys.xlsx", engine='xlsxwriter')
    sys.sysdatatable[0].to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
    writer.save()
    writer.close()

    sys.data_reasoning()

    writer = pd.ExcelWriter("C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\output/BCOOL0511-final-sys.xlsx", engine='xlsxwriter')
    sys.sysdatatable[0].to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
    writer.save()
    writer.close()

    # sys.split_sys_table()
    # 结果保存

    # # SCR
    # writer = pd.ExcelWriter("./SCR-2-sys.xlsx", engine='xlsxwriter')
    # sys.sysdatatable[0].to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
    # writer.save()
    # writer.close()
    # picklestring = pickle.dumps(sys)
    # fn = './SCR-2-sys.db'
    # with open(fn, 'wb') as f:  # open file with write-mode
    #     f.write(picklestring)  # serialize and save object

    # # HVC
    # writer = pd.ExcelWriter("./HVC-sys.xlsx", engine='xlsxwriter')
    # sys.sysdatatable[0].to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
    # writer.save()
    # writer.close()
    # picklestring = pickle.dumps(sys)
    # fn = './HVC-sys.db'
    # with open(fn, 'wb') as f:  # open file with write-mode
    #     f.write(picklestring)  # serialize and save object

    # # SCR&HVC
    # writer = pd.ExcelWriter("./SCR&HVC-sys.xlsx", engine='xlsxwriter')
    # sys.sysdatatable[0].to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
    # writer.save()
    # writer.close()
    # picklestring = pickle.dumps(sys)
    # fn = './SCR&HVC-sys.db'
    # with open(fn, 'wb') as f:  # open file with write-mode
    #     f.write(picklestring)  # serialize and save object

    # SCR
    writer = pd.ExcelWriter("C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\output/BCOOL0511-1-sys.xlsx", engine='xlsxwriter')
    sys.sysdatatable[0].to_excel(writer, encoding='utf_8_sig', index=True, header=True, sheet_name="sys")
    writer.save()
    writer.close()
    picklestring = pickle.dumps(sys)
    fn = 'C:\\PanChen_File\\Python_workdir\\IDE_Online_Tools\\data\\output/BCOOL0426-1-sys.db'
    with open(fn, 'wb') as f:  # open file with write-mode
        f.write(picklestring)  # serialize and save object

    te = time.time()
    print("本次运行使用时间: " + str(te - ts) + "s")
    print(" ")
