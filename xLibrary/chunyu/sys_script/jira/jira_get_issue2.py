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
from xLibrary.chunyu.sys_script.expert_sys.connect_mysql import expert_sys
from xLibrary.chunyu.sys_script.jira.jira_get_issue3 import jira_operation3



class jira_operation2:

    def __init__(self):
        pass


    @func_set_timeout(60)#设定函数超执行时间
    def jira_get_issue2(self, issue_key, dict):
        try:
            logging.warning(API0000_diy().text_conversion('开始'))
            #sys.stdout = open(r'C:\Users\9an02\Desktop\test1.txt', mode='w')
            #初始化
            jira_url =  'https://jira.9an-data.com'   #jira地址
            jira_name = 'xingchunyu'   #jira登录用户名
            jira_password = 'Abc123456'   #jira登录密码
            dict['issues_json'] = {'json':{}, 'html':''}
            jira_task_attribute = {'jira_task_type':''}   #任务属性(jira_task_type任务领域)
            

            #step1：查询jira任务信息
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：查询jira任务信息'  # 节点
            #连接jira
            try:
                jira = JIRA(auth=(jira_name, jira_password), options={'server': jira_url})
            except Exception, e:
                is_success = False
                message = '连接jira失败，请检查用户名、密码、jira地址是否正确！'
            assert is_success != False

            #查询任务信息
            try:
                issue = jira.issue(issue_key)
            except Exception, e:
                is_success = False
                message = 'jira获取问题对象报错！'
            assert is_success != False

            #问题key
            if issue.key == None:
                issue_key = ''
            else:
                issue_key = issue.key
            dict['issues_json']['json']['issue_key'] = issue_key 

            #项目名称
            if jira.project(issue.fields.project).name == None:
                project_name = ''
            else:
                project_name = jira.project(issue.fields.project).name
            dict['issues_json']['json']['project_name'] = project_name

            #概要名称
            if issue.fields.summary == None:
                issue_summary = ''
            else:
                issue_summary = issue.fields.summary.encode('utf-8').replace(u'\xa0', u' ')
            dict['issues_json']['json']['issue_summary'] = issue_summary

            #任务类型
            if issue.fields.issuetype.name == None:
                issue_issuetype = ''
            else:
                issue_issuetype = issue.fields.issuetype.name 
            dict['issues_json']['json']['issue_issuetype'] = issue_issuetype

            #提出人
            if str(issue.fields.assignee) == 'None':
                issue_assignee = ''
            else:
                issue_assignee = str(issue.fields.assignee)
            dict['issues_json']['json']['issue_assignee'] = issue_assignee

            #任务状态
            if issue.fields.status == None:
                issue_status = ''
            else:
                issue_status = str(issue.fields.status)
            dict['issues_json']['json']['issue_status'] = issue_status

            #任务概述
            if issue.fields.description == None:
                issue_description = ''
            else:
                issue_description = issue.fields.description.encode('utf-8').replace(u'\xa0', u' ')
            dict['issues_json']['json']['issue_description'] = issue_description 

            is_success = True
            assert is_success == True

            #step2:通过专家系统得到被分配人
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：通过专家系统获取被分配人'  # 节点
            #确定任务领域
            if issue_assignee == '郑 丽艳':
                jira_task_attribute['jira_task_type'] = '理赔'   #任务属性-任务领域
            elif issue_assignee == '邢春雨':
                jira_task_attribute['jira_task_type'] = '其他'   #任务属性-任务领域
            dict['issues_json']['json']['jira_task_type'] = jira_task_attribute['jira_task_type']
            #print jira_task_type.decode('utf-8').encode('gb18030')
            #print jira_task_attribute

            #调用专家系统数据库得到待分配人
            dict = expert_sys().connect_mysql(jira_task_attribute, dict)
            assert dict['logInfo']['code'] == '1'
            #获取待分配人
            tester_name = dict['tester_name']
            if tester_name == '' or tester_name == None:
                is_success = False
                message = '专家系统数据库获取被分配人未成功！'
            dict['issues_json']['json']['tester_name'] = tester_name
            assert is_success != False
            #print tester_name

            #step3:获取待分配人jira测试任务数
            dict = jira_operation3().jira_get_issue3(dict)
            assert dict['logInfo']['code'] == '1'
            #print len(dict['dict['issues_json']['json']['issue_num']'])
            is_success = True
            dict['logInfo']['code'] = '1'   #断言是否异常
            #print dict
            logging.warning(API0000_diy().text_conversion('结束'))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'
            message = traceback.format_exc()
            #print traceback.format_exc()
            logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
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
            issue_key = 'JK001-23808'   #任务编号JK001-23808  JK001-18706
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                msg = '后台传值数有误！'
                execNo = ''
                issue_key = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['issue_key']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                issue_key = rs[2][0]   #任务编号
        dict = {'execNo': execNo, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':''}}
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
        dict = jira_operation2().jira_get_issue2(issue_key, dict)
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
            #print dict
            #打印终端开始符
            dict['issues_json']['html'] = dict['issues_json']['html'] + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:
                if dict['logInfo']['code'] == '1':
                    dict['issues_json']['html'] = dict['issues_json']['html'] + '是否查询成功：成功'
                else:
                    dict['issues_json']['html'] = dict['issues_json']['html'] +  '是否查询成功：不成功；不成功原因：' + dict['logInfo']['msg']
            else:
                if dict['logInfo']['code'] == '1':
                    dict['issues_json']['html'] = dict['issues_json']['html'] + "是否查询成功：成功" 
                else:
                    dict['issues_json']['html'] = dict['issues_json']['html'] + "是否查询成功：不成功"
            #打印终端结束符
            dict['issues_json']['html'] = dict['issues_json']['html'] +  '#'*3 + 'RESULT' + '#'*3
            #print dict['issues_json']['html'].decode('utf-8').encode('gb18030')
            #print (json.dumps(dict['issues_json']['json']).encode('ascii')).decode('unicode-escape')

            #json转化为字符串
            dict['issues_json'] = (json.dumps(dict['issues_json']).encode('ascii')).decode('unicode-escape') 
            print dict['issues_json']
            logging.warning(API0000_diy().text_conversion("dict['issues_json']:\n" + dict['issues_json']))
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())




































































































