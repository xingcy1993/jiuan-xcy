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


"""专家系统规则引擎：
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
        遍历事件-交易-规则：
        1.按序号排序
        2.规则引擎
        3.展示结果约定规
"""

#专家系统规则引擎
class sys_API0053:

    def __init__(self):
        pass


    @func_set_timeout(30)#设定函数超执行时间
    def expert_rule_engine(self, flow_code, dict):
        try:
            #执行记录日志
            logging.warning(API0000_diy().text_conversion('专家系统规则引擎_开始'))

            """step1:专家系统-规则解析初始化"""
            #执行记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp'*4 + '规则解析初始化' + '_开始'))
            #调用原子脚本
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            if 'win' in sys.platform:   #windows系统平台
                db_ip = 'localhost'         # 定义数据库ip
                db_user = 'root'      # 定义数据库用户名
                db_password = 'abc123456'   # 定义数据库密码
                db_name = 'test'   #库名
            else:
                db_ip = '10.8.1.157'         # 定义数据库ip
                db_user = 'expert'      # 定义数据库用户名
                db_password = 'expert123'   # 定义数据库密码
                db_name = 'dbexpert'   #库名

            rule_list = []
            dict['out_param'] = []   #出参结果列表
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：读取数据'  # 节点


            #1.解析专家系统-数据结构
            rs = API0000_expert_sys().query_data_structure(flow_code, dict)
            flow_list = rs[0]   #流程列表
            dict = rs[1]
            assert dict['logInfo']['code'] == '1'
            flow_list = dict['flow_list']   #数据结构列表（脚本使用，非前端使用）

            #执行记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp'*4 + '规则解析初始化' + '_结束'))

            """step2:执行脚本"""
            #遍历事件
            for i in range(0, len(flow_list)): 
                event_name = flow_list[i]['name']   #事件名称
                logging.warning(API0000_diy().text_conversion('&nbsp'*4 + '事件-' + event_name))
                #遍历交易
                for j in range(0, len(flow_list[i]['deal'])):
                    deal_name = flow_list[i]['deal'][j]['name']   #交易名称
                    logging.warning(API0000_diy().text_conversion('&nbsp'*8 + '交易-' + deal_name))

                    #遍历具象交易
                    for z in range(0, len(flow_list[i]['deal'][j]['actual_deal'][0]['rule'])):
                        rule_name = flow_list[i]['deal'][j]['actual_deal'][0]['rule'][z]['name']   #规则名称

                        try:
                            db = pymysql.connect(host=db_ip, user=db_user, passwd=db_password, db=db_name, charset='utf8')
                        except Exception, e:
                            is_success = False
                            message = '专家系统数据库连接失败，请检查用户名、密码、ip、库名是否有误！'
                        assert is_success != False

                        #读取规则/公式
                        try:
                            cursor = db.cursor()
                            sql = "SELECT body FROM exp_rule_body WHERE descript='" + rule_name + "'"
                            cursor.execute(sql)
                            result = cursor.fetchall()
                        except Exception, e:
                            is_success = False
                            message = '专家系统数据库查询规则报错，检查sql是否错误或表中的规则是否存在！'
                        assert is_success != False

                        if result == []:
                            is_success = False
                            message = '专家系统数据库查询规则，查询结果为空！'
                        else:
                            rule = result[0][0]   #获取规则
                        assert is_success != False

                        #拆分规则
                        rule_min_list = rule.split("】 【")
                        #插入规则名、交易名、事件名
                        rule_min_list.append(rule_name)   #rule_min_list[5]
                        rule_min_list.append(deal_name)   #rule_min_list[6]
                        rule_min_list.append(event_name)   #rule_min_list[7]
                        #print '----------'
                        #对每个拆分的结果进行优化
                        for m in range(0,len(rule_min_list)):
                            rule_min_list[m] = rule_min_list[m].replace("【", "")
                            rule_min_list[m] = rule_min_list[m].replace("】", "")
                            rule_min_list[m] = rule_min_list[m].replace("'", '"')
                        #print rule_min_list

                        #规则内各值转换格式
                        rule_min_list[0] = int(rule_min_list[0])
                        rule_min_list[3] = json.loads(rule_min_list[3])
                        rule_min_list[4] = json.loads(rule_min_list[4])
                        #存入规则列表中
                        rule_list.append(rule_min_list)
                        #print rule_list

            #规则排序
            temp = ''
            for i in range(0,len(rule_list)):
                for x in range(len(rule_list)-1,-1,-1):
                    for y in range(0,x):
                        if rule_list[x][0] < rule_list[y][0]:
                            temp = rule_list[y]
                            rule_list[y] = rule_list[x]
                            rule_list[x] = temp
            #print rule_list

            #执行规则
            for i in range(0,len(rule_list)):
                #1.日志记录
                logging.warning(API0000_diy().text_conversion('&nbsp'*16 + '执行规则：' + rule_list[i][5]))
                #获取入参字典
                in_param_dict = rule_list[i][3]
                #获取出参字典
                out_param_dict = rule_list[i][4]
                #确定匹配脚本+执行
                if rule_list[i][1] == '数据源获取':
                    if rule_list[i][2] == 'jira':
                        #登录jira
                        if len(list(in_param_dict.keys())) == 3 and in_param_dict.has_key('ip') and in_param_dict.has_key('name') and in_param_dict.has_key('password'):
                            rs = self.jira_login(dict, in_param_dict)
                elif rule_list[i][1] == '查询数据':
                    if rule_list[i][2] == 'jira':
                        #jira查询
                        if len(list(in_param_dict.keys())) == 2 and in_param_dict.has_key('jira') and in_param_dict.has_key('JQL'):
                            rs = self.jira_query(dict, in_param_dict)
                        #获取jira测试任务的待分配人
                        if len(list(in_param_dict.keys())) == 2 and in_param_dict.has_key('jira') and in_param_dict.has_key('jira_key'):
                            rs = self.jira_test_assigner(dict, in_param_dict)
                elif rule_list[i][1] == '更新':
                    if rule_list[i][2] == 'jira':
                        #jira任务分配
                        if len(list(in_param_dict.keys())) == 3 and in_param_dict.has_key('jira') and in_param_dict.has_key('jira_key') and in_param_dict.has_key('assigner'):
                            rs = self.jira_test_assign(dict, in_param_dict)

                #获取脚本出参
                dict = rs[0]
                assert dict['logInfo']['code'] == '1'
                #获取出参
                out_param_dict[list(out_param_dict.keys())[0]] = rs[1]
                #获取展示内容
                result = rs[2]
                display_type = result['type']   #展示类型
                dict['out_param'].append({'order_number':rule_list[i][0], 'out_param_dict':out_param_dict})
                #print '------'
                #print in_param_dict
                #print dict['out_param']

                #记录-结果展示
                #"""
                time.sleep(3)
                result_list = []    #前端展示值（列表
                #每个交易第一条展示。（事件名-交易名-执行结果：）
                event_name = rule_list[i][7]
                deal_name = rule_list[i][6]
                rule_name = rule_list[i][5]
                result_list.append({'type':'title', 'titleName':("[事件：" + event_name + "]" + '-' + "[交易：" + deal_name + "]" + '-' + "[规则：" + rule_name + "]" + '-' + '执行结果展示')})
                #step1:定义展示内容
                if display_type == '文本':
                    content = result['content']   #展示内容
                    #每个交易第二条展示：
                    result_list.append({'type':'title', 'titleName':content})
                elif display_type == '表格':
                    tableHead = result['tableHead']   #表格字段头
                    trList = result['trList']   #表格每行内容
                    result_list.append({'type':'table', 'tableHead':tableHead,'trList':trList})
                """
                #每个交易第一条展示。（事件名-交易名-执行结果：）
                event_name = rule_list[i][7]
                deal_name = rule_list[i][6]
                rule_name = rule_list[i][5]
                result_list = [{ 'type':'title', 'titleName':("[事件：" + event_name + "]" + '-' + "[交易：" + deal_name + "]" + '-' + "[规则：" + rule_name + "]" + '-' + '执行结果展示')}, {'type':'title', 'titleName':'pass'}]
                """
                #step2:调‘执行任务-记录步骤执行信息’接口"
                icode = 'EXEC107'
                execNo = dict['execNo']   #执行编号
                #execNo = '2021090381000000577'
                stepNo = '02'   #步骤编号
                stepTitle = '展示执行结果'   #步骤名称
                stepParams = {}   #步骤执行参数:json字符 ,无则传 “{}”
                stepResult = result_list   #步骤执行结果:json字符 ,无则传 “{}”
                stepError = {}   #步骤执行错误信息:json字符 ,无则传 “{}”
                response = API0000_expert_sys().run_xjob(icode, execNo, stepNo, stepTitle, stepParams, stepResult, stepError)
                if response['header']['istatus'] == '1':
                    is_success = True
                    message = ''
                else:
                    is_success = False
                    message = '不成功' 
                assert is_success == True
                #"""
            #执行记录日志
            logging.warning(API0000_diy().text_conversion('专家系统规则引擎_结束'))
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



    #“入参引擎”函数。解决入参为动态参数问题
    def in_param_engine(self, dict, in_param_dict, out_param_list):
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：入参引擎'  # 节点

            #遍历入参字典
            for i in in_param_dict:
                #判断入参是否为动态参数
                if '.' in in_param_dict[i]:
                    #获取入参序号:1.拆分前的格式为"序号.key"；2对.拆分
                    list = in_param_dict[i].split(".")   #
                    order_number = list[0]   #获取序号
                    key = list[1]   #获取对应的出参key
                    #遍历out_param_list列表
                    for j in range(0, len(out_param_list)):
                        #匹配入参序号与出参序号
                        if int(out_param_list[j]['order_number']) == int(order_number):
                            in_param_dict[i] = out_param_list[j]['out_param_dict'][key]

            dict['logInfo']['code'] = '1'
            is_success = True
        except Exception, e:
            dict['logInfo']['code'] = '0'
            is_success = False
            print traceback.format_exc()
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
        return dict, in_param_dict, out_param_list


    #jira登录
    @func_set_timeout(30)#设定函数超执行时间
    def jira_login(self, dict, in_param_dict):
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            #获取已存入dict的出参列表。默认为[]
            out_param_list = dict['out_param']   
            #调用“入参引擎”函数。解决入参为动态参数问题
            rs = self.in_param_engine(dict, in_param_dict, out_param_list) 
            dict = rs[0]
            in_param_dict = rs[1]
            out_param_list = rs[2]

            #自动读取入参值
            globals().update(in_param_dict)

            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：查询jira任务信息-连接jira'  # 节点
            try:
                jira = JIRA(auth=(name, password), options={'server': ip})
            except Exception, e:
                is_success = False
                message = '连接jira失败，请检查用户名、密码、jira地址是否正确！'
            assert is_success != False
            #定义结果展示格式
            result_dict = {'type':'文本', 'content':str('jira=' + str(jira))}
            dict['logInfo']['code'] = '1'   
            is_success = True
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
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict, jira, result_dict   #出参为 dict ，出参字段， 结果展示内容



    #查询jira任务信息
    def jira_query(self, dict, in_param_dict,):
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            
            run_result = []   #执行结果
            content = []   #结果展示
            key_list = []

            #获取已存入dict的出参列表。默认为[]
            out_param_list = dict['out_param']   
            #调用“入参引擎”函数。解决入参为动态参数问题
            rs = self.in_param_engine(dict, in_param_dict, out_param_list) 
            dict = rs[0]
            in_param_dict = rs[1]
            out_param_list = rs[2]

            #自动读取入参值
            globals().update(in_param_dict)

            #step1：获取查询到的任务对象
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：查询jira任务信息-获取查询到的任务对象'  # 节点
            #查询任务
            try:
                issues = jira.search_issues(JQL, maxResults=-1)
                #print issues
            except Exception, e:
                is_success = False
                message = 'JQL查询任务列表对象报错！'

            #判断是否存在任务
            if len(issues) == 0:
                is_success = False
                message = '未查询到jira任务！'
            assert is_success != False

            #step3：遍历issues_list列表（测试组未完成的'待测试'任务），并展示
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：查询jira任务信息-遍历issues_list列表'  # 节点
            for j in range(0,len(issues)):
                #遍历获取问题对象
                try:
                    issue = jira.issue(issues[j])
                except Exception, e:
                    is_success = False
                    message = 'jira获取问题对象报错！'
                assert is_success != False

                #问题key
                if issue.key == None:
                    issue_key = ''
                else:
                    issue_key = issue.key

                #项目名称
                if jira.project(issue.fields.project).name == None:
                    project_name = ''
                else:
                    project_name = jira.project(issue.fields.project).name  

                #任务类型
                if issue.fields.issuetype.name == None:
                    issue_issuetype = ''
                else:
                    issue_issuetype = issue.fields.issuetype.name

                #提出人
                if str(issue.fields.assignee) == 'None':
                    issue_assignee = ''
                else:
                    issue_assignee = str(issue.fields.assignee)

                #概要名称
                if issue.fields.summary == None:
                    issue_summary = ''
                else:
                    issue_summary = issue.fields.summary.encode('utf-8').replace(u'\xa0', u' ')

                #任务状态
                if issue.fields.status == None:
                    issue_status = ''
                else:
                    issue_status = str(issue.fields.status)

                #存入执行结果run_result
                run_result.append({})
                run_result[-1]['issue_key'] = issue_key 
                run_result[-1]['project_name'] = project_name 
                run_result[-1]['issue_issuetype'] = issue_issuetype
                run_result[-1]['issue_assignee'] = issue_assignee
                run_result[-1]['issue_summary'] = issue_summary
                run_result[-1]['issue_status'] = issue_status  

                #存入展示结果display_result
                #1.表格格式
                content.append([])
                content[-1].append(str(j + 1))
                content[-1].append(issue_key)
                content[-1].append(issue_issuetype)
                content[-1].append(issue_assignee)
                content[-1].append(issue_summary)

                #存入key_list 
                key_list.append(issue_key)
            #结果展示
            result_dict = {'type':'表格', 'tableHead':['序号','任务编号','类型','提出人','概要名称'], 'trList':content}   #结果展示
            #存入dict
            dict['logInfo']['code'] = '1'   #断言是否异常
            is_success = True
            #logging.warning(API0000_diy().text_conversion('结束'))
            #print dict
        except Exception, e:
            dict['logInfo']['code'] = '0'
            is_success = False
            print traceback.format_exc()
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
        return dict, key_list, result_dict


    #查询jire测试任务待分配人
    @func_set_timeout(30)#设定函数超执行时间
    def jira_test_assigner(self, dict, in_param_dict):
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            assigner_list = []
            content = []   #结果展示-表格内容
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：获取jira测试任务待分配人'  # 节点

            #获取已存入dict的出参列表。默认为[]
            out_param_list = dict['out_param']   
            #调用“入参引擎”函数。解决入参为动态参数问题
            rs = self.in_param_engine(dict, in_param_dict, out_param_list) 
            dict = rs[0]
            in_param_dict = rs[1]
            out_param_list = rs[2]

            #自动读取入参值
            globals().update(in_param_dict)

            #测试任务对应待分配人规则
            for i in range(0, len(jira_key)):
                if jira_key[i] == 'JK001-18706':
                    assigner = 'xingchunyu'
                    #assigner = 'chunqing.zhang'
                    assigner_list.append(assigner)
                    #存入展示结果display_result
                #1.表格格式
                content.append([])
                content[-1].append(i + 1)
                content[-1].append(jira_key[i])
                content[-1].append(assigner)
            #结果展示
            result_dict = {'type':'表格', 'tableHead':['序号','任务编号','分配人'], 'trList':content}   #结果展示
            #存入dict
            dict['logInfo']['code'] = '1'   
            is_success = True
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
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict, assigner_list, result_dict



    #jira任务分配
    @func_set_timeout(30)#设定函数超执行时间
    def jira_test_assign(self, dict, in_param_dict):
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            success_list = []
            result_dict = {'type':'文本', 'content':'a'}   #结果展示
            content = []   #结果展示-表格内容

            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：jira任务分配'  # 节点

            #获取已存入dict的出参列表。默认为[]
            out_param_list = dict['out_param']   
            #调用“入参引擎”函数。解决入参为动态参数问题
            rs = self.in_param_engine(dict, in_param_dict, out_param_list) 
            dict = rs[0]
            in_param_dict = rs[1]
            out_param_list = rs[2]

            #自动读取入参值
            globals().update(in_param_dict)

            #jira分配
            for i in range(0, len(jira_key)):
                try:
                    #获取任务对象    
                    issue = jira.issue(jira_key[i])
                    issue.update(
                            {
                                "assignee": {"name": assigner[i]}
                            }
                        )
                    success_list.append(True)
                except Exception, e:
                    is_success = False
                    message = 'jira任务分配不成功！'
                    success_list.append(False)

                #1.表格格式
                content.append([])
                content[-1].append(i + 1)
                content[-1].append(jira_key[i])
                content[-1].append(assigner[i])
                if success_list[i] == True:
                    content[-1].append('分配成功')
                else:
                    content[-1].append('分配不成功')

            #结果展示
            result_dict = {'type':'表格', 'tableHead':['序号','任务编号','分配人','分配结果'], 'trList':content}   #结果展示
            #存入dict
            dict['logInfo']['code'] = '1'   
            is_success = True
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
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict, success_list, result_dict



    @func_set_timeout(30)#设定函数超执行时间
    def result_display(self, dict, in_param_dict):
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            result_dict = {'type':'文本', 'content':'a'}   #结果展示
            success_list = []
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：结果展示'  # 节点

            #获取已存入dict的出参列表。默认为[]
            out_param_list = dict['out_param']   
            #调用“入参引擎”函数。解决入参为动态参数问题
            rs = self.in_param_engine(dict, in_param_dict, out_param_list) 
            dict = rs[0]
            in_param_dict = rs[1]
            out_param_list = rs[2]

            #自动读取入参值
            globals().update(in_param_dict)
            for i in range(0, len(jira_key)):
                pass  
                #print jira_key
                #print assigner
                #print success[i]
            dict['logInfo']['code'] = '1'   
            is_success = True
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
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict, is_success, result_dict


if __name__ == "__main__":
    try:
        #1.初始化
        msg = ''   #执行python脚本前存在的错误信息
        
        begin_time = datetime.datetime.now()   #开始时间
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            flow_code = 'demo1'   #流程编号
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位:脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                flow_code = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['flow_code']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                flow_code = rs[2][0]   #流程编号
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
        dict = sys_API0053().expert_rule_engine(flow_code, dict)
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
            end_time = datetime.datetime.now()   #记录结束时间
            if dict['logInfo']['code'] == '1':
                #打印终端开始符
                print '\n\n' + '#'*3 + 'RESULT' + '#'*3
                print 'success'
                #打印终端结束符
                print '#'*3 + 'RESULT' + '#'*3
            else:
                if dict['logInfo']['msg'] == '节点：查询jira任务信息-获取查询到的任务对象:未查询到jira任务！':
                    print '"""RESULT"""doNothing"""RESULT"""'
                else:
                    print '\n\n' + '#'*3 + 'RESULT' + '#'*3
                    print dict['logInfo']['msg'].decode('utf-8').encode('gb2312')
                    #打印终端结束符
                    print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())











