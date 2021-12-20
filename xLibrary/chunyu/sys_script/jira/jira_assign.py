# coding=utf-8

import re
import os
import sys
import json
import chardet
import datetime
import func_timeout
from jira import JIRA
from func_timeout import func_set_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *


class jira_operation_assign:

    def __init__(self):
        pass


    @func_set_timeout(30)#设定函数超执行时间
    def jira_assign(self, issue_key, tester_name, issue_begin, issue_end, dict):
        try:
            logging.warning(API0000_diy().text_conversion('开始'))
            #初始化
            jira_url =  'https://jira.9an-data.com'   #jira地址
            jira_name = 'xingchunyu'   #jira登录用户名
            jira_password = 'Abc123456'   #jira登录密码
            #assign_name = 'chunqing.zhang'
            assign_name = 'xingchunyu'   #给配给谁
            #assign_name = assign_name.encode('utf8')

            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：jira分配任务'  # 节点

            #定义
            if tester_name == '赵影娜':
                issue_assignee = 'zhaoyingna'
            elif tester_name == '赵桂红':
                issue_assignee = 'zhaogh'
            elif tester_name == '尹爱珍':
                issue_assignee = 'yinaizhen'
            elif tester_name == '张纯清':
                issue_assignee = 'chunqing.zhang'
            elif tester_name == '张祥杰':
                issue_assignee = 'zhangxiangjie'
            elif tester_name == 'even':
                issue_assignee = 'even.gu'
            elif tester_name == '周艺伟':
                issue_assignee = 'zhouyiwei'
            elif tester_name == '何萌':
                issue_assignee = 'hemeng'
            elif tester_name == '王留恒':
                issue_assignee = 'wangliuheng'
            elif tester_name == '邢春雨':
                issue_assignee = 'xingchunyu'
            else:
                is_success = False
                message = '待分配人不在测试人员范围内！'
            assert is_success != False

            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：jira任务分配'  # 节点

            #连接jira
            try:
                jira = JIRA(auth=(jira_name, jira_password), options={'server': jira_url})
            except Exception, e:
                is_success = False
                message = '连接jira失败，请检查用户名、密码、jira地址是否正确！'
            assert is_success != False

            #获取任务对象
            try:
                issue = jira.issue(issue_key)
            except Exception, e:
                is_success = False
                message = 'jira获取问题对象报错！'
            assert is_success != False

            #获取任务概述
            if issue.fields.description == None:
                issue_description = ''
            else:
                issue_description = issue.fields.description.encode('utf-8').replace(u'\xa0', u' ')
            
            #任务概述顶端加入【计划开始时间】【计划完成时间】
            if issue_begin == '' and issue_end =='':
                issue.update(
                        {
                            "assignee": {"name": issue_assignee}
                        }
                    )
            else:
                issue_description = '*'*5 + '\n' + '最新分配时间：' + datetime.datetime.now().strftime('%Y-%m-%d') + '\n' + '【计划开始时间】：' + issue_begin + '\n【计划完成时间】：' + issue_end + '\n' + '*'*5 + '\n' + issue_description
                issue.update(
                        {
                            "assignee": {"name": issue_assignee},
                            "description": issue_description
                        }
                    )

            is_success = True
            dict['logInfo']['code'] = '1'   #断言是否异常
            logging.warning(API0000_diy().text_conversion('结束'))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'
            message = traceback.format_exc()
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            is_success = False
            dict['logInfo']['code'] = '0'
            message = '执行时间超时退出'
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
        finally:
            #step3:定义轨迹信息+检查点信息:
            dict = API0000_diy().result(dict, is_success, message, unit)
            #print dict['logInfo']['msg']
        return dict






if __name__ == "__main__":
    try:
        #1.初始化
        msg = ''   #执行python脚本前存在的错误信息
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            issue_key = 'JK001-18706'   #待分配测试任务
            tester_name = '邢春雨'   #待分配人
            issue_begin = ''   #开始测试时间
            issue_end = ''   #开始验收时间
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                msg = '后台传值数有误！'
                execNo = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['issue_key','tester_name', 'issue_begin', 'issue_end']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                issue_key = rs[2][0]   #待分配测试任务
                tester_name = rs[2][1]   #待分配人
                issue_begin = rs[2][2]   #开始测试时间
                issue_end = rs[2][3]   #开始验收时间
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
        dict = jira_operation_assign().jira_assign(issue_key, tester_name, issue_begin, issue_end, dict)
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
        try:
            #打印终端开始符
            dict['issues_json']['html'] = dict['issues_json']['html'] + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:
                if dict['logInfo']['code'] == '1':
                    dict['issues_json']['html'] = dict['issues_json']['html'] + '是否查询成功：成功'
                    dict['issues_json']['json'] = {'result':'分配成功'}
                else:
                    dict['issues_json']['html'] = dict['issues_json']['html'] +  '是否查询成功：不成功；不成功原因：' + dict['logInfo']['msg']
                    dict['issues_json']['json'] = {'result':'未分配成功'}
            else:
                if dict['logInfo']['code'] == '1':
                    dict['issues_json']['html'] = dict['issues_json']['html'] + "是否查询成功：成功" 
                    dict['issues_json']['json'] = {'result':'分配成功'}
                else:
                    dict['issues_json']['html'] = dict['issues_json']['html'] + "是否查询成功：不成功"
                    dict['issues_json']['json'] = {'result':'未分配成功'}
            #打印终端结束符
            dict['issues_json']['html'] = dict['issues_json']['html'] +  '#'*3 + 'RESULT' + '#'*3
            #print (json.dumps(dict['issues_json']['json']).encode('ascii')).decode('unicode-escape')

            #json转化为字符串
            dict['issues_json'] = (json.dumps(dict['issues_json']).encode('ascii')).decode('unicode-escape') 
            print dict['issues_json']
            logging.warning(API0000_diy().text_conversion("dict['issues_json']:\n" + dict['issues_json']))
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())

















