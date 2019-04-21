# -*- coding=utf-8 -*-

import sys
import argparse
from util import aries_util
from util.constant import CONFIG_CONST, BUILD_STATUS, LINK_TYPE
from util import request
from git import Repo
import re

reload(sys)
sys.setdefaultencoding('utf8')

demo_path = "/var/jenkins_workspace/CIDemo_App"
# 蒲公英
u_key = "b86d599851919e28cefdb6e3fbb45b40"
api_key = "b19ae9afa279ddf0d53fdcb5bcbec3b7"
pgy_baseurl = "https://www.pgyer.com/"


# 切换分支，拉取最新代码
def check_branch(branch):
    print 'check branch...'
    result = {
        'status': CONFIG_CONST.FAIL_STATUS,
        'errorLog': ""
    }
    try:
        repo = Repo(demo_path)
        git = repo.git
        git.add(".")
        git.reset("--hard")
        if branch.startswith("origin/"):
            branch = branch[7:]
        git.checkout(branch)
        git.pull('origin', branch)
        result['status'] = CONFIG_CONST.SUCCESS_STATUS
    except Exception as e:
        print 'commit error: ' + str(e)
        result['errorLog'] = str(e)
    finally:
        return result


def modify_sdk_path():
    print 'modify sdk path...'
    modify_command = '''cd %s && sed -i "s/sdk.dir=.*/sdk.dir=\\/var\\/android_sdk/g" local.properties''' % demo_path
    return aries_util.doSubprocess(modify_command)


# 指定submodule分支，更新submodule
def submodule_update(branch):
    print '更新submodule...'
    if branch.startswith("origin/"):
        branch = branch[7:]
    # modify_branch_command = '''sed -i "s/branch = .*/branch = %s/g" .gitmodules''' % branch
    modify_branch_command = 'cd %s && git config -f .gitmodules submodule.CIDemo_AppShell.branch %s' % (
        demo_path, branch)
    result = aries_util.doSubprocess(modify_branch_command)
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        return result
    update_command = "cd %s && git submodule update --init --recursive --remote" % demo_path
    result = aries_util.doSubprocess(update_command)
    return result


def assemble():
    assemble_command = "cd %s && ./gradlew assembleRelease" % demo_path
    return aries_util.doSubprocess(assemble_command)


# 上传apk地址
def upload_apk():
    apk_path = demo_path + "/CIDemo_AppShell/build/outputs/apk/release/CIDemo_AppShell-release.apk"
    upload_command = '''curl -F "file=@%s" -F "uKey=%s" -F "_api_key=%s" https://qiniu-storage.pgyer.com/apiv1/app/upload''' % (
        apk_path, u_key, api_key)
    return aries_util.doSubprocess(upload_command)


def main(args):
    print '-----项目集成-----'
    project_id = args.p
    project_name = args.n
    build_num = args.i
    branch = args.b
    project_build_result = {
        "projectId": project_id,
        "projectName": project_name,
        "buildNum": build_num,
        "buildStatus": BUILD_STATUS["SUCCESS"],
        "message": "项目%s集成成功" % project_name,
        "downloadUrl": "",
        "type": 2
    }
    result = check_branch(branch)
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        project_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
        project_build_result["message"] = "项目%s集成失败：切换分支失败"
        return request.post("api/jenkins/notify/project", project_build_result)
    result = modify_sdk_path()
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        project_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
        project_build_result["message"] = "项目%s集成失败：修改sdk路径失败"
        return request.post("api/jenkins/notify/project", project_build_result)
    result = submodule_update(branch)
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        project_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
        project_build_result["message"] = "项目%s集成失败：更新submodule失败"
        return request.post("api/jenkins/notify/project", project_build_result)
    result = assemble()
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        project_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
        project_build_result["message"] = "项目%s集成失败：打包apk失败"
        return request.post("api/jenkins/notify/project", project_build_result)
    result = upload_apk()
    if result['status'] == CONFIG_CONST.FAIL_STATUS:
        project_build_result["buildStatus"] = BUILD_STATUS["FAILURE"]
        project_build_result["message"] = "项目%s集成失败：上传apk失败"
        return request.post("api/jenkins/notify/project", project_build_result)
    pgy_result = result['output']
    app_shortcut_url = re.findall('''"appShortcutUrl":"(.+?)"''', pgy_result)
    project_build_result["downloadUrl"] = pgy_baseurl + app_shortcut_url[0]
    print "download url:" + project_build_result["downloadUrl"]
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


def test():
    pgy_result = '''{"code":0,"message":"","data":{"appKey":"5823303395f90520d5edced88b680e3f","userKey":"b86d599851919e28cefdb6e3fbb45b40","appType":"2","appIsLastest":"1","appFileSize":"3711048","appName":"\u7ec4\u4ef6\u5316\u9879\u76ee","appVersion":"1.0","appVersionNo":"1","appBuildVersion":"6","appIdentifier":"com.zwy.cidemo","appIcon":"efdfa4a54b8c5678b37b6f224e78a47c","appDescription":"","appUpdateDescription":"","appScreenshots":"","appShortcutUrl":"R81V","appCreated":"2019-04-22 00:58:23","appUpdated":"2019-04-22 00:58:23","appQRCodeURL":"https:\/\/www.pgyer.com\/app\/qrcodeHistory\/68f2093850d4f695d80cd955fabcbe9d47a8d71ed3578fe9ef96cec3570232c4"}}'''
    app_shortcut_url = re.findall('''"appShortcutUrl":"(.+?)"''', pgy_result)
    print app_shortcut_url[0]


if __name__ == '__main__':
    args = _parse_args()
    main(args)
    # test()
