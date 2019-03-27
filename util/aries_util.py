#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import subprocess

import traceback
from constant import CONFIG_CONST

def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        return False


def writeToFile(file_path, record):
    f = open(file_path, 'a')
    f.write(record)
    f.write('\n')
    f.close()
    pass


def doSubprocess(command, result, is_record_to_file=False):
    print("doSubprocessPrintLog command: " + command)

    try:
        result['output'] = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        result["status"] = CONFIG_CONST.SUCCESS_STATUS

    except subprocess.CalledProcessError, exc:
        traceback.print_exc()
        if not is_record_to_file:
            result["errorLog"] = exc.output
        # else:
        #     result["errorLog"] = writeErrorLog(exc.output)
        # result["status"] = CONFIG_CONST.FAIL_STATUS

    except Exception as e:
        traceback.print_exc()
        result["errorLog"] = str(e)
        result["status"] = CONFIG_CONST.FAIL_STATUS
    finally:
        return result


# def writeErrorLog(msg):
#     mkdir('/tmp/android-build')
#     time_str = time.strftime('%Y%m%d-%H%M%S')
#     log_path = '/tmp/android-build/%s.log' % time_str
#     writeToFile(log_path, msg)
#     oss_log_path = upload_file(log_path)
#     # print('oss_log_path', oss_log_path)
#     return oss_log_path



if __name__ == '__main__':
    result = {
        'status': 1,
        'errorMsg': "",
        'errorLog': "",
        'output': ""
    }

    uploadCommand = "cd /Users/zhusg/TuyaProject/TuyaBlueMesh && ./gradlew :bluemesh:upload"
    print("uploadCommand:" + uploadCommand)
    result = doSubprocess(uploadCommand, result, True)
    print(result)
