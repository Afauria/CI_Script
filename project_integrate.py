# -*- coding=utf-8 -*-

import sys
import argparse
from util import aries_util
from util.constant import CONFIG_CONST, BUILD_STATUS, LINK_TYPE
from git import Repo
from util import request
import json

reload(sys)
sys.setdefaultencoding('utf8')


# 指定submodule分支，更新submodule
def submodule_update(branch):
    if branch.startswith("origin/"):
        branch = branch[7:]
    # modify_branch_command = '''sed -i "s/branch = .*/branch = %s/g" .gitmodules''' % branch
    modify_branch_command = 'git config -f .gitmodules submodule.CIDemo_AppShell.branch %s' % branch
    result = aries_util.doSubprocess(modify_branch_command)
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        return result
    update_command = "git submodule update --init --recursive --remote"
    result = aries_util.doSubprocess(update_command)
    return result


def assemble():
    assemble_command = "./gradlew assembleRelease"
    return aries_util.doSubprocess(assemble_command)


def main(args):
    print '-----项目集成-----'
    project_id = args.p
    project_name = args.n
    build_version = args.v
    build_num = args.i
    branch = args.b
    project_build_result = {
        "projectId": project_id,
        "projectName": project_name,
        "buildNum": build_num,
        "version": build_version,
        "buildStatus": BUILD_STATUS["SUCCESS"],
        "message": "项目%s集成成功" % project_name
    }
    result = submodule_update(branch)
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        project_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
        project_build_result["message"] = "项目%s集成失败：%s" % (project_name, result['errorLog'])
    #     return request.post("api/jenkins/notify/project", project_build_result)
    # return request.post("api/jenkins/notify/project", project_build_result)


# metavar表示参数值，<>表示必填，通过-h参数能够查看帮助
def _parse_args():
    parser = argparse.ArgumentParser(description='ci 项目构建发布脚本')
    parser.add_argument('-p', metavar='<project id>', help='项目id')
    parser.add_argument('-n', metavar='<project name>', help='项目名称')
    parser.add_argument('-c', metavar='<catalog>', help='工程目录')
    parser.add_argument('-v', metavar='<build version>', help='构建版本号')
    parser.add_argument('-k', metavar='<build hashkey>', help='构建消息的hashKey')
    parser.add_argument('-b', metavar='<build branch>', help='构建分支')
    parser.add_argument('-i', metavar='<build id>', help='build id')
    parser.add_argument('-l', metavar='<module list>', help='项目组件')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    main(args)
