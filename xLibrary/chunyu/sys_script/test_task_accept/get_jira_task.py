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


#从专家系统数据库-查询数据结构
class get_jira_task:

    def __init__(self):
        pass


    @func_set_timeout(30)#设定函数超执行时间
    def run(self, flow_code, dict):
        try:
            logging.warning(API0000_diy().text_conversion('开始'))
            #print jira_task_attribute
            #初始化
            db_ip = '10.8.1.157'         # 定义数据库ip
            db_user = 'expert'      # 定义数据库用户名
            db_password = 'expert123'   # 定义数据库密码
            db_name = 'dbexpert'   #库名
            stage = []   #所有节点（流程、事件。。。规则）
            setArr = []   #专家系统结构列表(所有两个上下节点)
            flow = {'flow':[{'stage':[],'setArr':[]}]}   #初始化数据结构串;stage-所有节点（流程、事件。。。规则）；setArr-所有两个上下节点
            event_list = []   #事件列表
            deal_list = []   #交易列表
            actual_deal_list = []   #具象交易列表
            rule_list = []   #交易列表


            """step1:从专家系统数据库-获取数据结构"""
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：根据流程读取专家系统数据结构'  # 节点

            # 连接数据库
            try:
                db = pymysql.connect(host=db_ip, user=db_user, passwd=db_password, db=db_name, charset='utf8')
            except Exception, e:
                is_success = False
                message = '专家系统数据库连接失败，请检查用户名、密码、ip、库名是否有误！'
            assert is_success != False

            #根据流程读取专家系统数据结构
            #查询流程下事件
            try:
                cursor = db.cursor()
                sql = "SELECT a.cn_name 流程名称,c.cn_name 事件名称,c.code 事件编码 FROM exp_flow_define a,exp_flow_layout b,exp_event_define c WHERE a.id = b.master_flow_id AND b.event_id = c.id AND b.node_type = '2' AND a.code = '" + flow_code + "'"
                cursor.execute(sql)
                #print sql
                result = cursor.fetchall()
            except Exception, e:
                is_success = False
                message = '专家系统数据库查询规则报错，检查sql（查询流程下事件）是否错误或表中的规则是否存在！'
            assert is_success != False

            #存入dict
            for i in range(0,len(result)):
                flow_name = ('流程-' + result[i][0]).encode('utf-8').encode('gbk')   #流程名称
                event_name = ('事件-' +result[i][1]).encode('utf-8').encode('gbk')   #流程名称
                #存入stage
                stage.append(flow_name)
                stage.append(event_name)
                #存入setArr
                setArr.append([])
                event_list.append({'name':event_name,'code':result[i][2]})
                setArr[-1].append(flow_name)
                setArr[-1].append(event_name)
            #print setArr
            for i in range(0,len(event_list)):
                #print setArr[i][1]
                pass
            #print event_list
            is_success = True


            #查询事件下交易
            for i in range(0,len(setArr)):
                try:
                    cursor = db.cursor()
                    sql1 = "SELECT c.cn_name 事件名称,e.cn_name 交易名称,e.code 交易编码 FROM exp_event_define c,exp_event_layout d,exp_trans_group e WHERE  c.id = d.event_id AND d.node_type = '8' AND d.trans_id = e.id AND c.code = '" + event_list[i]['code'] + "'"
                    cursor.execute(sql1)
                    #print sql
                    result1 = cursor.fetchall()
                except Exception, e:
                    is_success = False
                    message = '专家系统数据库查询规则报错，检查sql（查询事件下交易）是否错误或表中的规则是否存在！'
                assert is_success != False

                #存入dict
                for i in range(0,len(result1)):
                    event_name = ('事件-' + result1[i][0]).encode('utf-8').encode('gbk')   #事件名称
                    deal_name = ('交易-' + result1[i][1]).encode('utf-8').encode('gbk')   #交易名称
                    #存入stage
                    stage.append(event_name)
                    stage.append(deal_name)
                    #存入setArr
                    setArr.append([])
                    deal_list.append({'name':deal_name,'code':result1[i][2]})
                    setArr[-1].append(event_name)
                    setArr[-1].append(deal_name)
                #print setArr
                for i in range(0,len(deal_name)):
                    #print setArr[i][1]
                    pass
                #print deal_list
                is_success = True


            #查询交易下具象交易
            for i in range(0,len(deal_list)):
                try:
                    cursor = db.cursor()
                    sql2 = "SELECT e.cn_name 交易名称,g.cn_name 具象交易名称,g.code 具象交易编码 FROM exp_trans_group e,exp_trans_group_member f,exp_trans_define g WHERE e.id = f.group_id AND f.trans_id = g.id AND e.code = '" + deal_list[i]['code'] + "'"
                    cursor.execute(sql2)
                    #print sql
                    result2 = cursor.fetchall()
                except Exception, e:
                    is_success = False
                    message = '专家系统数据库查询规则报错，检查sql（查询交易下具象交易）是否错误或表中的规则是否存在！'
                assert is_success != False

                #存入dict
                for i in range(0,len(result2)):
                    deal_name = ('交易-' + result2[i][0]).encode('utf-8').encode('gbk')   #交易名称
                    actual_deal_name = ('具象交易-' + result2[i][1]).encode('utf-8').encode('gbk')   #具象交易名称
                    #存入stage
                    stage.append(deal_name)
                    stage.append(actual_deal_name)
                    #存入setArr
                    setArr.append([])
                    actual_deal_list.append({'name':actual_deal_name,'code':result2[i][2]})
                    setArr[-1].append(deal_name)
                    setArr[-1].append(actual_deal_name)
                #print setArr
                for i in range(0,len(actual_deal_list)):
                    #print setArr[i][1]
                    pass
                #print actual_deal_list
                is_success = True



            #查询具象交易下规则
            for i in range(0,len(actual_deal_list)):
                try:
                    cursor = db.cursor()
                    sql3 = "SELECT g.cn_name 具象交易名称,i.cn_name 规则名称,i.code 规则编码 FROM exp_trans_define g,exp_trans_layout h,exp_rule_define i WHERE g.id = h.trans_id AND h.ref_rule_id = i.id AND g.code = '" + actual_deal_list[i]['code'] + "'"
                    cursor.execute(sql3)
                    #print sql
                    result3 = cursor.fetchall()
                except Exception, e:
                    is_success = False
                    message = '专家系统数据库查询规则报错，检查sql（查询具象交易下规则）是否错误或表中的规则是否存在！'
                assert is_success != False

                #存入dict
                for i in range(0,len(result3)):
                    actual_deal_name = ('具象交易-' + result3[i][0]).encode('utf-8').encode('gbk')   #具象交易名称
                    rule_name = ('规则-' + result3[i][1]).encode('utf-8').encode('gbk')   #规则名称
                    #存入stage
                    stage.append(actual_deal_name)
                    stage.append(rule_name)
                    #存入setArr
                    setArr.append([])
                    rule_list.append({'name':rule_name,'code':result3[i][2]})
                    setArr[-1].append(actual_deal_name)
                    setArr[-1].append(rule_name)
            print len(setArr)
            print setArr
            """
            for i in range(0,len(setArr)):
                print setArr[i][1]
                pass
            """
            """
            for i in range(0,len(rule_list)):
                print rule_list
            """
            is_success = True

            #存入dict
            dict['logInfo']['code'] = '1'   #断言是否异常
            #stage去重
            #print len(stage)
            stage = list(set(stage))
            print len(stage)
            print stage
            #print stage
            #定义总json
            flow = {'flow':[{'stage':stage,'setArr':setArr}]}   #初始化流程串;stage-所有节点（流程、事件。。。规则）；setArr-所有两个上下节点



            """step2:调‘执行任务-记录步骤执行信息’接口"""
            #初始化
            is_success = ''
            unit = '调‘执行任务-记录步骤执行信息’接口'  # 节点
            message = ''
            
            icode = 'query_data_structure'   #接口号
            icode = 'EXEC107'
            execNo = dict['execNo']   #执行编号
            execNo = '2021090381000000577'
            stepNo = '01'   #步骤编号
            stepTitle = '从专家系统数据库-查询数据结构'   #步骤名称
            stepParams = {}   #步骤执行参数:json字符 ,无则传 “{}”
            stepResult = {"a":100}   #步骤执行结果:json字符 ,无则传 “{}”
            stepError = {}   #步骤执行错误信息:json字符 ,无则传 “{}”
            #调用原子脚本
            response = API0000_sys_notherapi().run_xjob(icode, execNo, stepNo, stepTitle, stepParams, stepResult, stepError)
            print response
            logging.warning(API0000_diy().text_conversion('结束'))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'
            message = traceback.format_exc()
            print traceback.format_exc()
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
            flow_code = 'checkdata_tool1'   #流程编号
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                msg = '后台传值数有误！'
                execNo = ''
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
                #print jira_task_attribute
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
        dict = get_jira_task().run(flow_code, dict)
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
        """
        try:
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
            #print (json.dumps(dict['issues_json']['json']).encode('ascii')).decode('unicode-escape')

            #json转化为字符串
            dict['issues_json'] = (json.dumps(dict['issues_json']).encode('ascii')).decode('unicode-escape') 
            print dict['issues_json']
            logging.warning(API0000_diy().text_conversion("dict['issues_json']:\n" + dict['issues_json']))
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())
        """









