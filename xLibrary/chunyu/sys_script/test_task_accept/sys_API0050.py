# coding=utf-8

import re
import os
import sys
import json
import chardet
import func_timeout
from jira import JIRA
from func_timeout import func_set_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *


"""测试任务受理：
step1：规则解析初始化
        入参：流程编号flow_code
        出参：数据结构list（供脚本使用）flow_list
        1.解析专家系统-数据结构（流程-事件-交易-具象交易-规则）。API0000_expert_sys().query_data_structure()
            入参：流程编号flow_code
            出参：数据结构list（供脚本使用）flow_list
            (1)连接专家系统数据库
            (2)从专家系统数据库获取数据结构json，传给前端展示
                入参：流程编号flow_code
                出参：数据结构dict（供前端展示）flow_dict
            (3)从专家系统数据库获取数据结构(列表)，提供给脚本使用
                入参：流程编号flow_code
                出参：数据结构list（供脚本使用）flow_list
        2.校验数据结构正确性
            入参：流程编号flow_code
            出参：dict
step2：执行脚本
        入参：数据结构list（供脚本使用）flow_list
        出参：dict
        遍历事件-交易：
        1.读取数据源规则
        2.执行数据源规则
        3.展示结果约定规则
"""

#测试任务受理
class sys_API0050:

    def __init__(self):
        pass


    @func_set_timeout(30)#设定函数超执行时间
    def test_task_accept(self, flow_code, dict):
        try:
            #执行记录日志
            logging.warning(API0000_diy().text_conversion('测试任务受理_开始'))

            """step1:专家系统-规则解析初始化"""
            #执行记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp'*4 + '规则解析初始化' + '_开始'))
            #调用原子脚本
            rs = API0000_expert_sys().rule_parsing_initialization(flow_code, dict)
            flow_list = rs[0]   #数据结构list（供脚本使用）
            dict = rs[1]
            assert dict['logInfo']['code'] == '1'
            #执行记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp'*4 + '规则解析初始化' + '_结束'))

            """step2:执行脚本"""
            dict = API0000_expert_sys().execute_script(flow_list, dict)
            assert dict['logInfo']['code'] == '1'

            #执行记录日志
            logging.warning(API0000_diy().text_conversion('测试任务受理_结束'))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'
            print traceback.format_exc()
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            is_success = False
            dict['logInfo']['code'] = '0'
            message = '执行时间超时退出'
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
        finally:
            pass
            #step3:定义轨迹信息+检查点信息:
            #dict = API0000_diy().result(dict, is_success, message, unit)
            #print dict['logInfo']['msg']
        return dict





if __name__ == "__main__":
    try:
        #1.初始化
        msg = ''   #执行python脚本前存在的错误信息
        flow_code = 'checkdata_tool1'   #流程编号
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            execNo = sys.argv[1]   #测试编号
        #定义dict
        dict = {'execNo': execNo, 'issues_json':{'json':'','html':''}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':''}}
        #5.1定义logging文件路径
        if 'win' in sys.platform:
            logging_filename = 'D:\\xLibrary\\chunyu\\%s.html' % str(execNo)
            #判断windows是否存在某文件，存在则删除文件
            if os.path.exists(logging_filename):
                os.remove(logging_filename)
        else:
            logging_filename = '/data/xServer/xReport/%s.html' % str(execNo) 
        #5.2定义logging格式
        logging.basicConfig(level=logging.WARNING , format='%(message)s  &nbsp&nbsp&nbsp&nbsp%(asctime)s <br/><br/>', filename=logging_filename, filemode='a')
        #6.执行脚本
        dict = sys_API0050().test_task_accept(flow_code, dict)
        assert dict['logInfo']['code'] == '1'   #断言是否异常
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = 0
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:
        dict['logInfo']['code'] = 0
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
    finally:
        pass










