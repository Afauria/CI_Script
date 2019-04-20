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


# 拉取项目仓库App_Shell，切换分支
def check_branch():
    pass


# 替换gradle依赖文件
def modify_gradle(updatemodules):
    print 'modify module version...'
    for data in updatemodules:
        pattern = 'com.zwy.cidemo:%s:' % (data['moduleName'])
        # sed:-i表示直接修改源文件：sed -i 's/替换前/替换后/g' 文件名 / /中间是正则表达式
        # com.zwy.cidemo:module_girls:1.0.4
        found_command = '''sed -n "/%s/p" dependencies.gradle''' % (pattern)
        result = aries_util.doSubprocess(found_command)
        if result['status'] == CONFIG_CONST.FAIL_STATUS:
            return result
        if data['type'] == LINK_TYPE['REMOVE_MODULE']:
            result = remove_implementation(pattern)
        else:
            if len(result['output']) == 0:
                result = add_implementation(pattern, data['version'])
            else:
                result = modify_implementation(pattern, data['version'])
        if result['status'] == CONFIG_CONST.FAIL_STATUS:
            return result
    return result


def add_implementation(pattern, version):
    print 'add new implementation...'
    add_command = '''sed -i "1a \    '%s'," dependencies.gradle''' % (pattern + version)
    result = aries_util.doSubprocess(add_command)
    return result


def modify_implementation(pattern, version):
    print 'modify implementation...'
    modify_command = '''sed -i "s/'%s.*'/'%s'/g" dependencies.gradle''' % (pattern, pattern + version)
    result = aries_util.doSubprocess(modify_command)
    return result


def remove_implementation(pattern):
    print 'remove implementation...'
    remove_command = '''sed -i "/%s/d" dependencies.gradle''' % pattern
    result = aries_util.doSubprocess(remove_command)
    return result


# 提交代码
def commit_update(path, branch):
    print 'commit ci project update...'
    result = {
        'status': CONFIG_CONST.FAIL_STATUS,
        'errorLog': ""
    }
    try:
        repo = Repo(path)
        git = repo.git
        git.add('dependencies.gradle')
        commit_msg = 'ci project build'
        status = git.commit('--allow-empty', m=commit_msg)
        print 'commit status: ' + status
        if branch.startswith("origin/"):
            branch = branch[7:]
        branch = "HEAD:" + branch
        print 'push branch: ' + branch
        git.push('origin', branch)
        result['status'] = CONFIG_CONST.SUCCESS_STATUS
    except Exception as e:
        print 'commit error: ' + str(e)
        result['errorLog'] = str(e)
    finally:
        return result


# 转换编码
# command = 'cat %s/gradle.properties | iconv -f GBK -t UTF-8' % module_name

def main(args):
    print '-----项目构建-----'
    project_id = args.p
    project_name = args.n
    build_version = args.v
    build_num = args.i
    project_modules = args.l
    branch = args.b
    print 'project modules: ' + project_modules
    project_build_result = {
        "projectId": project_id,
        "projectName": project_name,
        "buildNum": build_num,
        "version": build_version,
        "buildStatus": BUILD_STATUS["SUCCESS"],
        "message": "项目%s构建成功" % project_name
    }
    modules = json.loads(project_modules)
    result = modify_gradle(modules)
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        project_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
        project_build_result["message"] = "项目%s构建失败：%s" % (project_name, result['errorLog'])
        return request.post("api/jenkins/notify/project", project_build_result)
    result = commit_update(".", branch)
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        project_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
        project_build_result["message"] = "项目%s构建失败：%s" % (project_name, result['errorLog'])
        return request.post("api/jenkins/notify/project", project_build_result)
    return request.post("api/jenkins/notify/project", project_build_result)


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
