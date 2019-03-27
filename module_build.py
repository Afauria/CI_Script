# -*- coding=utf-8 -*-

import sys
import argparse
from util import aries_util

reload(sys)
sys.setdefaultencoding('utf8')


# metavar表示参数值，<>表示必填，通过-h参数能够查看帮助
def _parse_args():
    parser = argparse.ArgumentParser(description='ci 组件构建发布脚本')
    parser.add_argument('-n', metavar='<module name>', help='模块名称')
    parser.add_argument('-p', metavar='<project path>', help='项目地址')
    parser.add_argument('-v', metavar='<build version>', help='构建版本号')
    parser.add_argument('-k', metavar='<build hashkey>', help='构建消息的hashKey')
    parser.add_argument('-b', metavar='<build branch>', help='构建分支')
    parser.add_argument('-i', metavar='<build id>', help='build id')
    parser.add_argument('-s', metavar='<spec>', help='定制组件名')

    return parser.parse_args()


def main(args):
    print '-----组件构建-----'
    module_name = args.n
    # uploadCommand = './gradlew :%s:upload' % (module_name)
    command = 'cat %s/gradle.properties | iconv -f GBK -t UTF-8' % module_name
    # sed:-i表示直接修改源文件：sed -i 's/替换前/替换后/g' 文件名
    modifyCommand = 'sed -i \"s///g\" %s/gradle.properties' % module_name
    command = 'cat %s/gradle.properties | iconv -f GBK -t UTF-8' % module_name
    result = {
        'status': 1,
        'errorMsg': "",
        'errorLog': "",
        'output': ""
    }
    print aries_util.doSubprocess(command, result)['output']


if __name__ == '__main__':
    args = _parse_args()
    main(args)
