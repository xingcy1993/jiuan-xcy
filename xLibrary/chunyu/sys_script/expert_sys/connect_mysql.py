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


class expert_sys:

    def __init__(self):
        pass


    @func_set_timeout(30)#设定函数超执行时间
    def connect_mysql(self, jira_task_attribute, dict):
        try:
            logging.warning(API0000_diy().text_conversion('开始'))
            #print jira_task_attribute
            #初始化
            db_ip = '10.8.1.157'         # 定义数据库ip
            db_user = 'expert'      # 定义数据库用户名
            db_password = 'expert123'   # 定义数据库密码
            db_name = 'dbexpert'   #库名
            tester_name = ''   #待分配人
            rule_name = ''   #规则名称
            jira_task_type = jira_task_attribute['jira_task_type']   #任务领域

            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：调用专家系统数据库获取待分配人'  # 节点

            # 连接数据库
            try:
                db = pymysql.connect(host=db_ip, user=db_user, passwd=db_password, db=db_name, charset='utf8')
            except Exception, e:
                is_success = False
                message = '专家系统数据库连接失败，请检查用户名、密码、ip、库名是否有误！'
            assert is_success != False

            #匹配专家系统规则
            if jira_task_type == '理赔':
                rule_name = 'jira任务分配规则1'
            elif jira_task_type == '其他':
                rule_name = 'jira任务分配规则2'

            #读取规则/公式
            try:
                cursor = db.cursor()
                sql = "SELECT body FROM exp_formula_body WHERE descript='" + rule_name + "'"
                cursor.execute(sql)
                #print sql
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
                #print rule
            assert is_success != False

            #解析规则/公式
            
            try:
                #解析1：规则去除html格式
                pattern = re.compile(r'<[^>]+>',re.S)
                result1 = pattern.sub('', rule)
                
                #解析2：变量转换
                result1 = result1.replace("jira任务类型", "jira_task_type")    #jira任务类型转换jira_task_type
                result1 = result1.replace("测试人员姓名", "tester_name")    #测试人员姓名转换空tester_name
                result1 = result1.replace("&nbsp;", "")    #&nbsp;转换空
                pattern1 = u'【[\w]*[\u4e00-\u9fa5]* . '   #正则匹配去掉【xxx .可能含中英文下划线等 
                result1 = re.sub(pattern1, '', result1)
                #print(result1.decode('utf-8').encode('gb18030'))
                #解析3
                result1 = result1.replace(r"\t", "    ")   #\t转换为tab空格键
                result1 = result1.replace(r"\n", "\n")    #\n转换为换行
                result1 = result1.replace("&nbsp;", "")    #&nbsp;转换为空
                result1 = result1.replace("】", "")    #】转换为空
                #print(result1.decode('utf-8').encode('gb18030'))
            except Exception, e:
                is_success = False
                message = '结息规则/公式报错！'
            assert is_success != False

            #内部执行
            try:
                exec(result1)
            except Exception, e:
                is_success = False
                message = '内部执行规则报错！'
            assert is_success != False

            #存入dict
            dict['tester_name'] = tester_name
            #print tester_name.decode('utf-8').encode('gb18030')
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
            jira_task_attribute = {'jira_task_type':'其他'}   #任务属性
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                msg = '后台传值数有误！'
                execNo = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['jira_task_attribute']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                jira_task_attribute = rs[2][0]   #任务属性
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
        dict = expert_sys().connect_mysql(jira_task_attribute, dict)
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










