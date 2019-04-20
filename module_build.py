# -*- coding=utf-8 -*-

import sys
import argparse
from util import aries_util
from util.constant import CONFIG_CONST, BUILD_STATUS
from util import request
from git import Repo

reload(sys)
sys.setdefaultencoding('utf8')


def modify_sdk_path():
    print 'modify sdk path...'
    modify_command = '''sed -i "s/sdk.dir=.*/sdk.dir=\\/var\\/android_sdk/g" local.properties'''
    return aries_util.doSubprocess(modify_command)


def modify_build_version(module_name, build_version):
    print 'modify build version...'
    # sed:-i表示直接修改源文件：sed -i 's/替换前/替换后/g' 文件名
    modify_command = '''sed -i "s/version '.*'/version '%s'/g" %s/upload_nexus.gradle''' % (
        build_version, module_name)
    return aries_util.doSubprocess(modify_command)


def upload_maven(module_name):
    print 'upload maven...'
    upload_command = './gradlew :%s:upload' % module_name
    return aries_util.doSubprocess(upload_command)


# 提交代码
def commit_update(path, branch, module_name):
    print 'commit ci module update...'
    result = {
        'status': CONFIG_CONST.FAIL_STATUS,
        'errorLog': ""
    }
    try:
        repo = Repo(path)
        git = repo.git

        git.add('%s/upload_nexus.gradle' % module_name)
        commit_msg = 'ci module build'
        status = git.commit('--allow-empty', m=commit_msg)
        print 'commit status: ' + status
        if branch.startswith("origin/"):
            branch = branch[7:]
        branch = "HEAD:"+branch
        print 'push branch: ' + branch
        git.push('origin', branch)
        result['status'] = CONFIG_CONST.SUCCESS_STATUS
    except Exception as e:
        print 'commit error: ' + str(e)
        result['errorLog'] = str(e)
    finally:
        return result


# metavar表示参数值，<>表示必填，通过-h参数能够查看帮助
def _parse_args():
    parser = argparse.ArgumentParser(description='ci 组件构建发布脚本')
    parser.add_argument('-m', metavar='<module id>', help='组件id')
    parser.add_argument('-n', metavar='<module name>', help='模块名称')
    parser.add_argument('-c', metavar='<catalog>', help='工程目录')
    parser.add_argument('-v', metavar='<build version>', help='构建版本号')
    parser.add_argument('-k', metavar='<build hashkey>', help='构建消息的hashKey')
    parser.add_argument('-b', metavar='<build branch>', help='构建分支')
    parser.add_argument('-i', metavar='<build id>', help='build id')
    return parser.parse_args()


# 转换编码
# command = 'cat %s/gradle.properties | iconv -f GBK -t UTF-8' % module_name

def main(args):
    print '-----组件构建-----'
    module_id = args.m
    module_name = args.n
    build_version = args.v
    build_num = args.i
    catalog = args.c
    branch = args.b
    module_build_result = {
        "moduleId": module_id,
        "moduleName": module_name,
        "buildNum": build_num,
        "version": build_version,
        "buildStatus": BUILD_STATUS["SUCCESS"],
        "message": "构建成功"
    }
    result = modify_sdk_path()
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        module_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
        module_build_result["message"] = "构建失败：修改sdk路径失败"
        return request.post("api/jenkins/notify/module", module_build_result)
    # 修改版本号
    result = modify_build_version(module_name, build_version)
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        module_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
        module_build_result["message"] = "构建失败：修改版本号失败"
        return request.post("api/jenkins/notify/module", module_build_result)
    # 上传maven
    result = upload_maven(module_name)
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        module_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
        module_build_result["message"] = "构建失败：上传maven失败"
        return request.post("api/jenkins/notify/module", module_build_result)
    # 提交代码
    result = commit_update(".", branch, module_name)
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        module_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
        module_build_result["message"] = "构建失败：提交代码失败"
        return request.post("api/jenkins/notify/module", module_build_result)
    return request.post("api/jenkins/notify/module", module_build_result)


if __name__ == '__main__':
    args = _parse_args()
    main(args)
