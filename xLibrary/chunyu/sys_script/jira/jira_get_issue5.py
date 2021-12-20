# coding=utf-8

import re
import os
import sys
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *
from jira import JIRA



class jira_operation5:

    def __init__(self):
        pass


    @func_set_timeout(60)#设定函数超执行时间
    def jira_get_issue5(self, dict):
        try:
            sys.stdout = open(r'C:\Users\9an02\Desktop\test3.txt', mode='w')
            #初始化
            jira_url =  'https://jira.9an-data.com'   #jira地址
            jira_name = 'xingchunyu'   #jira登录用户名
            jira_password = 'Abc123456'   #jira登录密码
            project_list = ['JK001', 'JA001', 'GX001', 'JK005']   #项目列表
            issues_list_temp = []   #临时项目列表
            issues_list = []  #项目列表
            zhaoyingna_dict = {'issue_assignee':'赵影娜', 'list':[]}   #赵影娜
            zhaogh_dict = {'issue_assignee':'赵桂红', 'list':[]}   #赵桂红
            yinaizhen_dict = {'issue_assignee':'尹爱珍', 'list':[]}   #尹爱珍
            zhangchunqing_dict = {'issue_assignee':'张纯清', 'list':[]}   #张纯清
            zhangxiangjie_dict = {'issue_assignee':'张祥杰', 'list':[]}   #张祥杰
            even_dict = {'issue_assignee':'even', 'list':[]}   #even
            zhouyiwei_dict = {'issue_assignee':'周艺伟', 'list':[]}   #周艺伟
            hemeng_dict = {'issue_assignee':'何萌', 'list':[]}   #何萌
            wangliuheng_dict = {'issue_assignee':'王留恒', 'list':[]}   #王留恒
            other_dict = {'issue_assignee':'其他', 'list':[]}   #其他
            #step1：连接jira
            jira = JIRA(auth=(jira_name, jira_password), options={'server': jira_url})

            #step2：遍历测试组未完成的非'待测试'任务，存入issues_list_temp列表中
            for i in range(0,len(project_list)):
                #遍历获取项目对象
                project = jira.project(project_list[i])   
                #定义JQL
                JQL = 'project=' + project_list[i] + ' and status != 待测试 and issuetype in (UAT缺陷, 任务, 测试缺陷, 生产缺陷) AND resolution = Unresolved AND (assignee in (chunqing.zhang, even.gu, yinaizhen, zhangxiangjie, zhouyiwei, zhaoyingna, zhaogh, xingchunyu, wangliuheng, hemeng) OR 测试责任人 in (chunqing.zhang, even.gu, yinaizhen, zhangxiangjie, zhouyiwei, zhaoyingna, zhaogh, xingchunyu, wangliuheng, hemeng)) ORDER BY updated DESC'
                #查询任务
                issues = jira.search_issues(JQL, maxResults=-1)
                #存入issues_list_temp列表中
                issues_list_temp = issues + issues_list_temp


            #step3：遍历issues_list_temp列表，对每个测试人员筛选生成单独的字典，最终全部存入issues_list列表中。
            for i in range(0, len(issues_list_temp)):
                #遍历获取问题对象
                issue = jira.issue(issues_list_temp[i])
                if issue.fields.assignee.name == 'zhaoyingna':
                    zhaoyingna_dict['list'].append(issues_list_temp[i])
                elif issue.fields.assignee.name == 'zhaogh':
                    zhaogh_dict['list'].append(issues_list_temp[i])
                elif issue.fields.assignee.name == 'yinaizhen':
                    yinaizhen_dict['list'].append(issues_list_temp[i])
                elif issue.fields.assignee.name == 'chunqing.zhang':
                    zhangchunqing_dict['list'].append(issues_list_temp[i])
                elif issue.fields.assignee.name == 'zhangxiangjie':
                    zhangxiangjie_dict['list'].append(issues_list_temp[i])
                elif issue.fields.assignee.name == 'even.gu':
                    even_dict['list'].append(issues_list_temp[i])
                elif issue.fields.assignee.name == 'zhouyiwei':
                    zhouyiwei_dict['list'].append(issues_list_temp[i])
                elif issue.fields.assignee.name == 'hemeng':
                    hemeng_dict['list'].append(issues_list_temp[i])
                elif issue.fields.assignee.name == 'wangliuheng':
                    wangliuheng_dict['list'].append(issues_list_temp[i])
                else:
                    other_dict['list'].append(issues_list_temp[i])

            #存入issues_list列表中
            if zhaoyingna_dict['list'] !=[]:
                issues_list.append(zhaoyingna_dict)
            if zhaogh_dict['list'] !=[]:
                issues_list.append(zhaogh_dict)
            if yinaizhen_dict['list'] !=[]:
                issues_list.append(yinaizhen_dict)
            if zhangchunqing_dict['list'] !=[]:
                issues_list.append(zhangchunqing_dict)
            if zhangxiangjie_dict['list'] !=[]:
                issues_list.append(zhangxiangjie_dict)
            if even_dict['list'] !=[]:
                issues_list.append(even_dict)
            if zhouyiwei_dict['list'] !=[]:
                issues_list.append(zhouyiwei_dict)
            if hemeng_dict['list'] !=[]:
                issues_list.append(hemeng_dict)
            if wangliuheng_dict['list'] !=[]:
                issues_list.append(wangliuheng_dict)
            if other_dict['list'] !=[]:
                issues_list.append(other_dict)

            #step4：遍历issues_list列表（测试组未完成的非'待测试'任务），根据测试人员进行展示
            for j in range(0,len(issues_list)):
                print (issues_list[j]['issue_assignee'] + '当前任务数为：' + str(len(issues_list[j]['list'])) + '个').decode('utf-8').encode('gb2312') 
                for k in range(0,len(issues_list[j]['list'])):
                    #遍历获取问题对象
                    issue = jira.issue(issues_list[j]['list'][k])

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
                    #概要名称
                    if issue.fields.summary == None:
                        issue_summary = ''
                    else:
                        issue_summary = issue.fields.summary 
                    #任务类型
                    if issue.fields.issuetype.name == None:
                        issue_issuetype = ''
                    else:
                        issue_issuetype = issue.fields.issuetype.name 
                    #提出人
                    if str(issue.fields.assignee) == None:
                        issue_assignee = ''
                    else:
                        issue_assignee = str(issue.fields.assignee)
                    #任务状态
                    if str(issue.fields.status) == None:
                        issue_status = ''
                    else:
                        issue_status = str(issue.fields.status)
                    #任务概述
                    if issue.fields.description == None:
                        issue_description = ''
                    else:
                        issue_description = issue.fields.description     
                        
                    print ('问题：' + issue_key).decode('utf-8').encode('gb18030')
                    print ''
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
                print '------------------------------' 
            dict['logInfo']['code'] = '1'   #断言是否异常
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
        finally:
            #step3:定义轨迹信息+检查点信息:
            pass
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
        dict = {'execNo': execNo, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':''}}
        #5.1定义logging文件路径
        if 'win' in sys.platform:
            logging_filename = 'D:\\xLibrary\\chunyu\\%s.html' % str(execNo)
            #判断windows是否存在某文件，存在则删除文件
            if os.path.exists(logging_filename):
                os.remove(logging_filename)
        else:
            logging_filename = '/data/xServer/xReport/%s.html' % str(execNo) 
        #6.执行脚本
        dict = jira_operation5().jira_get_issue5(dict)
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
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:
                if dict['logInfo']['code'] == '1':
                    print '是否分配成功：成功'.decode('utf-8').encode('gb2312')
                else:
                    print ('是否分配成功：不成功').decode('utf-8').encode('gb2312')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "是否分配成功：成功" 
                else:
                    result_str = "是否分配成功：不成功"
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())














































































































