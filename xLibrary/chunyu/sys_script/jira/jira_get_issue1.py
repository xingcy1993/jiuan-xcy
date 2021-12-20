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



class jira_operation1:

    def __init__(self):
        pass


    @func_set_timeout(60)#设定函数超执行时间
    def jira_get_issue1(self, dict):
        try:
            #记录日志
            logging.warning(API0000_diy().text_conversion('开始'))
            #sys.stdout = open(r'C:\Users\9an02\Desktop\test1.txt', mode='w')
            #初始化
            jira_url =  'https://jira.9an-data.com'   #jira地址
            jira_name = 'xingchunyu'   #jira登录用户名
            jira_password = 'Abc123456'   #jira登录密码
            project_list = ['JK001', 'JK002', 'JA001', 'GX001', 'JK005']   #项目列表
            issues_list = []   #问题列表

            #step1：查询jira待测试任务列表
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：查询jira待测试任务列表'  # 节点
            #step1：连接jira
            try:
                jira = JIRA(auth=(jira_name, jira_password), options={'server': jira_url})
            except Exception, e:
                is_success = False
                message = '连接jira失败，请检查用户名、密码、jira地址是否正确！'
            assert is_success != False

            #step2：遍历测试组未完成的'待测试'任务，一一存入issues_list列表中
            for i in range(0,len(project_list)):
                #遍历获取项目对象
                project = jira.project(project_list[i])   
                #定义JQL
                try:
                    JQL = 'project=' + project_list[i] + ' AND (status = 待测试 OR key=JK001-18706) and issuetype in (UAT缺陷, 任务, 测试缺陷, 生产缺陷) AND resolution = Unresolved AND (assignee in (chunqing.zhang, even.gu, yinaizhen, zhangxiangjie, zhouyiwei, zhaoyingna, zhaogh, xingchunyu, wangliuheng, hemeng) OR 测试责任人 in (chunqing.zhang, even.gu, yinaizhen, zhangxiangjie, zhouyiwei, zhaoyingna, zhaogh, xingchunyu, wangliuheng, hemeng)) ORDER BY updated DESC'
                    #JQL = 'project=' + project_list[i] + ' and status = 待测试 and issuetype in (UAT缺陷, 任务, 测试缺陷, 生产缺陷) AND resolution = Unresolved AND (assignee in (chunqing.zhang, even.gu, yinaizhen, zhangxiangjie, zhouyiwei, zhaoyingna, zhaogh, xingchunyu, wangliuheng, hemeng) OR 测试责任人 in (chunqing.zhang, even.gu, yinaizhen, zhangxiangjie, zhouyiwei, zhaoyingna, zhaogh, xingchunyu, wangliuheng, hemeng)) ORDER BY updated DESC'
                except Exception, e:
                    is_success = False
                    message = 'JQL格式错误！'
                assert is_success != False

                #查询任务
                try:
                    issues = jira.search_issues(JQL, maxResults=-1)
                except Exception, e:
                    is_success = False
                    message = 'JQL查询任务列表对象报错！'
                assert is_success != False

                #存入issues_list列表中
                issues_list = issues + issues_list

            #step3：遍历issues_list列表（测试组未完成的'待测试'任务），并展示
            """
            print ('待分配问题总数为' + str(len(issues_list)) + '个').decode('utf-8').encode('gb2312')
            print ''
            print ''
            print ''
            """
            for j in range(0,len(issues_list)):
                dict['issues_json']['json'].append({})
                #遍历获取问题对象
                try:
                    issue = jira.issue(issues_list[j])
                except Exception, e:
                    is_success = False
                    message = 'jira获取问题对象报错！'
                assert is_success != False

                #问题key
                if issue.key == None:
                    issue_key = ''
                else:
                    issue_key = issue.key
                dict['issues_json']['json'][-1]['issue_key'] = issue_key 

                #项目名称
                if jira.project(issue.fields.project).name == None:
                    project_name = ''
                else:
                    project_name = jira.project(issue.fields.project).name
                dict['issues_json']['json'][-1]['project_name'] = project_name   
                  
                #概要名称
                if issue.fields.summary == None:
                    issue_summary = ''
                else:
                    issue_summary = issue.fields.summary.encode('utf-8').replace(u'\xa0', u' ')
                dict['issues_json']['json'][-1]['issue_summary'] = issue_summary

                #任务类型
                if issue.fields.issuetype.name == None:
                    issue_issuetype = ''
                else:
                    issue_issuetype = issue.fields.issuetype.name 
                dict['issues_json']['json'][-1]['issue_issuetype'] = issue_issuetype

                #提出人
                if str(issue.fields.assignee) == 'None':
                    issue_assignee = ''
                else:
                    issue_assignee = str(issue.fields.assignee)
                dict['issues_json']['json'][-1]['issue_assignee'] = issue_assignee

                #任务状态
                if issue.fields.status == None:
                    issue_status = ''
                else:
                    issue_status = str(issue.fields.status)
                dict['issues_json']['json'][-1]['issue_status'] = issue_status
                """  
                #任务概述
                if issue.fields.description == None:
                    issue_description = ''
                else:
                    issue_description = issue.fields.description.encode('utf-8').replace(u'\xa0', u' ') 
                dict['issues_json']['json'][-1]['issue_description'] = issue_description    
                  
                print ('问题：' + issue_key).decode('utf-8').encode('gb18030')
                print ('项目名称：' + project_name).decode('utf-8').encode('gb18030')
                print ''
                print ('概要名称：' + issue_summary).decode('utf-8').encode('gb18030')
                print ''
                print ('任务类型：' + issue_issuetype).decode('utf-8').encode('gb18030')
                print ''
                print ('经办人：' + issue_assignee).decode('utf-8').encode('gb18030')
                print ''
                print ('任务状态：' + issue_status).decode('utf-8').encode('gb18030')
                print ''
                print ('任务概述：' + issue_description).decode('utf-8').encode('gb18030')
                print '------------------------------'
                """
            dict['logInfo']['code'] = '1'   #断言是否异常
            is_success = True
            logging.warning(API0000_diy().text_conversion('结束'))
            #print dict
        except Exception, e:
            dict['logInfo']['code'] = '0'
            is_success = False
            message = traceback.format_exc()
            #print traceback.format_exc()
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            is_success = False
            message = '执行时间超时退出'
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
        finally:
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict





if __name__ == "__main__":
    try:
        #1.初始化
        msg = ''   #执行python脚本前存在的错误信息
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                msg = '后台传值数有误！'
                execNo = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
        dict = {'execNo': execNo, 'issues_json':{'json':[],'html':''}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':''}}
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
        dict = jira_operation1().jira_get_issue1(dict)
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
                else:
                    dict['issues_json']['html'] = dict['issues_json']['html'] +  ('是否查询成功：不成功')
            else:
                if dict['logInfo']['code'] == '1':
                    dict['issues_json']['html'] = dict['issues_json']['html'] + "是否查询成功：成功" 
                else:
                    dict['issues_json']['html'] = dict['issues_json']['html'] + "是否查询成功：不成功"
            #打印终端结束符
            dict['issues_json']['html'] = dict['issues_json']['html'] +  '#'*3 + 'RESULT' + '#'*3
            #print dict['issues_json']['html'].decode('utf-8').encode('gb18030')
            #print chardet.detect(json.dumps(dict['issues_json']))
            #print type(json.dumps(dict['issues_json']))
            #print dict['issues_json']['json']
            dict['issues_json'] = (json.dumps(dict['issues_json']).encode('ascii')).decode('unicode-escape') 
            print dict['issues_json']
            #print (json.dumps(dict['issues_json']).encode('ascii')).decode('unicode-escape')
            logging.warning(API0000_diy().text_conversion("dict['issues_json']:\n" + dict['issues_json']))
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())




































































































