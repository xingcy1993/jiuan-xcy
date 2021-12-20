#coding=utf-8

import os
import re
import sys
import time
import json
import random
import logging
import datetime
import traceback
from openpyxl import load_workbook
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *



"""数据库查询保全信息组件（录入保全申请号）:
"""
class sys_API0055:

    def __init__(self):
        pass

    @func_set_timeout(10)#设定函数超执行时间 

    def query_autoPaddingPrem(self, dict):
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''

            dict = self.query_sql(dict) 
            assert dict['logInfo']['code'] == '1'   #断言是否异常
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
        finally:
            pass
        return dict


    def query_sql(self, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('数据库查询保全信息_开始(预计耗时:5s;)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            list = []
            env_name = dict['public']['env_name']   #环境类型
            db_ip = dict['public']['db_ip']   #数据库ip
            db_user = dict['public']['db_user']   #数据库登录用户名
            db_password = dict['public']['db_password']   #数据库登录密码
            db_name = dict['public']['db_name']   #数据库库名
            apply_no = dict['public']['apply_no']   #产品编号 

            """step1:连接数据库"""
            #初始化
            is_success = ''
            message = ''
            unit = '数据库查询'
            try:
                #调用原子脚本
                cursor = API0000_diy().db_conf(env_name,'wift_cs')   #连接数据库
            except:
                is_success = False
                message = '数据库未连接成功，请检查数据库用户名/密码是否正确！'
            else:
                is_success = True
                message = ''
            #断言
            assert is_success == True
            
            if env_name == '预生产':
                sql = "SELECT b.policy_no,d.name,c.name,DATE_FORMAT(a.apply_time,'%Y-%m-%d'),b.suspend FROM  wift_cs.t_cs_application a,wift_cs.t_cs_change b,wift_iiws.d_cs_change_status c,wift_iiws.D_LIABILITY_CATEGORY d WHERE a.apply_id=b.apply_id AND b.change_status=c.code AND b.service_code=d.code AND a.apply_no='" + apply_no + "'"
            else:
                sql = "SELECT b.policy_no,d.name,c.name,DATE_FORMAT(a.apply_time,'%Y-%m-%d'),b.suspend FROM  wift_cs_uat.t_cs_application a,wift_cs_uat.t_cs_change b,wift_iiws_uat.d_cs_change_status c,wift_iiws_uat.D_LIABILITY_CATEGORY d WHERE a.apply_id=b.apply_id AND b.change_status=c.code AND b.service_code=d.code AND a.apply_no='" + apply_no + "'"
            cursor.execute(sql)
            result = cursor.fetchall()
            if result == ():
                policy_no = ''          #保单号
                pa_name = ''            #保全项
                pa_status = ''          #保全状态
                pa_date = ''            #保全申请日期
                pa_suspend = ''         #是否锁单
                is_success = False
                message = env_name + '环境数据库下查询不到此保全申请号！'
            else:
                policy_no = result[0][0]          #保单号
                pa_name = result[0][1]            #保全项
                pa_status = result[0][2]          #保全状态
                pa_date = result[0][3]            #保全申请日期
                pa_suspend = result[0][4]         #是否锁单
                is_success = True
                message = ''
            # 加入断言
            assert is_success == True  

            if pa_suspend == 'Y':
                pa_suspend = '是'
            elif pa_suspend == 'N':
                pa_suspend = '否'
            else:
                pa_suspend = '空'

            #存入dict
            dict['public']['policy_no'] = policy_no                  #保单号
            dict['public']['pa_name'] = pa_name                      #保全项
            dict['public']['pa_status'] = pa_status                  #保全状态
            dict['public']['pa_date'] = pa_date                      #保全申请日期
            dict['public']['pa_suspend'] = pa_suspend                #是否锁单
            dict['logInfo']['code'] = '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('数据库查询保全信息_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'   #dict['logInfo']['code']记录异常标识
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n') + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



        
if __name__ == "__main__":   
    try:
        begin_time = datetime.datetime.now()   #记录开始时间
        #1.初始化
        is_run = True   #是否执行python脚本 
        msg = ''   #执行python脚本前存在的错误信息
        #2.脚本执行数据:(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = '预生产'   #环境类型
            env_name = env_name.encode('utf-8')
            db_user = 'dbreadall'   #数据库登录用户名
            db_password = 'Ja_8283317'   #数据库登录密码
            apply_no = 'POS2021072700021'   #保全申请号
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位:脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                db_user = ''
                db_password = ''
                apply_no = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','db_user','db_password','apply_no']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                db_user = rs[2][1]   #数据库登录用户名
                db_password = rs[2][2]   #数据库登录密码
                apply_no = rs[2][3]   #保全申请号
        #录入字段中待校验列表
        key_dict = {'env_name':env_name}
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]

        #定义数据库ip
        if env_name == 'uat4':
            db_ip = '10.1.5.153'   
        elif env_name == 'uat6':
            db_ip = '10.56.1.23'  
        elif env_name == 'uat7':
            db_ip = '10.1.6.9'   
        elif env_name == 'uat8':
            db_ip = '10.1.5.136'   
        elif env_name == '预生产':
            db_ip = '10.1.6.19'  
        #定义库名
        db_name = 'wift_pa'   
        if env_name != '预生产':
            db_name = db_name + '_uat'

        #3.1定义logging文件路径
        if 'win' in sys.platform:
            logging_filename = 'D:\\xLibrary\\chunyu\\%s.html' % str(execNo)
            #判断windows是否存在某文件，存在则删除文件
            if os.path.exists(logging_filename):
                os.remove(logging_filename)
        else:
            logging_filename = '/data/xServer/xReport/%s.html' % str(execNo)
        #3.2定义logging格式
        logging.basicConfig(level=logging.WARNING , format='%(message)s  &nbsp&nbsp&nbsp&nbsp%(asctime)s <br/><br/>', filename=logging_filename, filemode='a')
        
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = {'execNo': execNo, 'public':{'env_name':env_name, 'apply_no':apply_no, 'db_ip':db_ip,'db_user':db_user,'db_password':db_password,'db_name':db_name,'html_file_path':logging_filename},'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':''}}

        #5.执行脚本
        if is_run == True:
            dict = sys_API0055().query_autoPaddingPrem(dict)
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:    #函数超时异常的捕捉
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时'))
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时。' + dict['logInfo']['msg']
    finally:
        try:
            end_time = datetime.datetime.now()   #记录结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:   #windows系统平台
                if dict['logInfo']['code'] == '1':
                    print '数据库查询保全信息是否成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保全申请号：' + dict['public']['apply_no']).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['public']['policy_no']).decode('utf-8').encode('gb2312')
                    print ('保全项：' + dict['public']['pa_name']).decode('utf-8').encode('gb2312')
                    print ('保全状态：' + dict['public']['pa_status']).decode('utf-8').encode('gb2312')
                    print ('保全申请日期：' + dict['public']['pa_date']).decode('utf-8').encode('gb2312')
                    print ('是否锁单：' + dict['public']['pa_suspend']).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '数据库查询保全信息是否成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('保全申请号：' + dict['public']['apply_no']).decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:    #非windows系统平台
                if dict['logInfo']['code'] == '1':
                    result_str = "数据库查询保全信息是否成功：成功,,环境：%s,,保全申请号：%s,,保单号：%s,,保全项：%s,,保全状态：%s,,保全申请日期：%s,,是否锁单：%s,,耗时：%s" % (env_name, dict['public']['apply_no'], dict['public']['policy_no'], dict['public']['pa_name'], dict['public']['pa_status'], dict['public']['pa_date'], dict['public']['pa_suspend'], API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "数据库查询保全信息是否成功：不成功,,不成功原因：%s,,环境：%s,,保全申请号：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, dict['public']['apply_no'], API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())




