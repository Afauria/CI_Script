# coding=utf-8


class _const:
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("can't change const %s" % name)
        if not name.isupper():
            raise self.ConstCaseError('const name "%s" is not all uppercase' % name)
        self.__dict__[name] = value


CONFIG_CONST = _const()

CONFIG_CONST.RPC_SERVER_IP = '192.168.13.177'
CONFIG_CONST.RPC_SERVER_PORT = 1235

CONFIG_CONST.RPC_SERVER_BUILD_MODULE_FUN = 'AndroidBuildMsgProcessor.ProcessModuleMessage'
CONFIG_CONST.RPC_SERVER_BUILD_PROJECT_FUN = 'AndroidBuildMsgProcessor.ProcessProjectMessage'
CONFIG_CONST.RPC_SERVER_BUILD_INTEGRATE_FUN = 'AndroidBuildMsgProcessor.ProcessIntegrateMessage'

CONFIG_CONST.RPC_SEND_KEY_STATUS = 'BuildStatus'
CONFIG_CONST.RPC_SEND_KEY_HASHKEY = 'MsgHashKey'
CONFIG_CONST.RPC_SEND_KEY_MSG = 'BuildMsg'
CONFIG_CONST.RPC_SEND_KEY_LOGURL = 'LogUrl'
CONFIG_CONST.RPC_SEND_KEY_BUILD_ID = 'BuildId'
CONFIG_CONST.RPC_SEND_KEY_BUILD_TYPE = 'BuildType'
CONFIG_CONST.RPC_SEND_KEY_COMPONENT_ID = 'ComponentId'

CONFIG_CONST.PROJECT_BUILD_TYPE = 1
CONFIG_CONST.PROJECT_INTEGRATE_TYPE = 2

# 构建状态
CONFIG_CONST.SUCCESS_STATUS = 1
CONFIG_CONST.FAIL_STATUS = 2

CONFIG_CONST.MAVEN_TUYA_RELEASE_PATH = 'http://112.124.7.102:8081/nexus/content/repositories/releases/com/tuya/smart/'
CONFIG_CONST.MAVEN_RELEASE_PATH = 'http://112.124.7.102:8081/nexus/content/repositories/releases/'

BUILD_STATUS = {
    "UNBUILD": 1,
    "BUILDING": 2,
    "SUCCESS": 3,
    "FAILURE": 4
}
LINK_TYPE = {
    'ADD_MODULE': 1,
    'REMOVE_MODULE': 2
}

