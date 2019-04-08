# -*- coding=utf-8 -*-

import sys
import argparse
from util import aries_util
from util.constant import CONFIG_CONST, BUILD_STATUS
from git import Repo
from util import request
import subprocess

reload(sys)
sys.setdefaultencoding('utf8')


# 拉取项目仓库App_Shell，切换分支
def check_branch():
    pass


# 替换gradle依赖文件
def modify_gradle(updatemodules):
    print 'modify module version...'
    result = {
        'status': 1,
        'errorLog': "",
        'output': ""
    }
    for data in updatemodules:
        pattern = 'com.zwy.cidemo:module_%s:' % (data['module_name'])
        # sed:-i表示直接修改源文件：sed -i 's/替换前/替换后/g' 文件名 / /中间是正则表达式
        # com.zwy.cidemo:module_girls:1.0.4
        found_command = '''sed -n "/%s/p" dependencies.gradle''' % (pattern)
        result = aries_util.doSubprocess(found_command)
        if len(result['output']) == 0:
            result = add_implementation(pattern, data['version'])
        else:
            result = modify_implementation(pattern, data['version'])
        if result['status'] == CONFIG_CONST.FAIL_STATUS:
            return result
    return result


def add_implementation(pattern, version):
    print 'add new implementation.'
    add_command = '''sed -i "1a \    '%s'," dependencies.gradle''' % (pattern + version)
    result = aries_util.doSubprocess(add_command)
    return result


def modify_implementation(pattern, version):
    print 'modify implementation.'
    modify_command = '''sed -i "s/'%s.*'/'%s'/g" dependencies.gradle''' % (pattern, pattern + version)
    result = aries_util.doSubprocess(modify_command)
    return result


# 提交代码
def commit_update():
    pass


# 转换编码
# command = 'cat %s/gradle.properties | iconv -f GBK -t UTF-8' % module_name

def main(args):
    print '-----组件构建-----'
    module_id = args.m
    module_name = args.n
    build_version = args.v
    build_num = args.i
    catalog = args.c
    module_build_result = {
        "moduleId": module_id,
        "jobName": module_name,
        "buildNum": build_num,
        "version": build_version,
        "buildStatus": BUILD_STATUS["SUCCESS"],
        "message": "test"
    }
    modules = [{"module_name": "girls", "version": "1.0.1.rc-1"}]
    modify_gradle(modules)

    # if result['status'] == CONFIG_CONST.FAIL_STATUS:
    #     module_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
    #     module_build_result["message"] = result['errorLog']
    # request.post("api/jenkins/notify/module", module_build_result)


# metavar表示参数值，<>表示必填，通过-h参数能够查看帮助
def _parse_args():
    parser = argparse.ArgumentParser(description='ci 项目构建发布脚本')
    parser.add_argument('-m', metavar='<module id>', help='build id')
    parser.add_argument('-n', metavar='<module name>', help='模块名称')
    parser.add_argument('-c', metavar='<catalog>', help='工程目录')
    parser.add_argument('-v', metavar='<build version>', help='构建版本号')
    parser.add_argument('-k', metavar='<build hashkey>', help='构建消息的hashKey')
    parser.add_argument('-b', metavar='<build branch>', help='构建分支')
    parser.add_argument('-i', metavar='<build id>', help='build id')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    main(args)
