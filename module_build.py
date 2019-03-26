# -*- coding: utf-8 -*-

from util import request
import sys

reload(sys)
sys.setdefaultencoding('utf8')


if __name__ == '__main__':
    print '-----组件构建-----'
    module_name = ''
    uploadCommand = './gradlew :%s:upload' % (module_name)
