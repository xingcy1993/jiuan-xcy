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



"""保单回执（数据库插入回执日期）组件:
    step1:连接数据库
    step2:判断保单是否存在
    step3:执行sql插入回执日期
    step4:查询是否插入成功
"""
class sys_API0033:

    def __init__(self):
        pass

    @func_set_timeout(10)#设定函数超执行时间 
    def nb_receipt(self, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('保单回执（数据库插入回执日期）_开始(预计耗时:5s;)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            env_name = dict['public']['env_name']   #环境类型
            db_ip = dict['public']['db_ip']   #数据库ip
            db_user = dict['public']['db_user']   #数据库登录用户名
            db_password = dict['public']['db_password']   #数据库登录密码
            db_name = dict['public']['db_name']   #数据库库名
            callBackDate = dict['public']['callBackDate']   #回执日期
            policyNo = dict['public']['policyNo']   #保单号 

            """step1:连接数据库"""
            #初始化
            is_success = ''
            message = ''
            unit = '连接数据库'
            try:
                #调用原子脚本
                db = API0000_diy().connect_db(db_ip, db_user, db_password, db_name)
                # 使用cursor()方法获取操作游标 
                cursor = db.cursor()
            except:
                is_success = False
                message = '数据库未连接成功，请检查数据库用户名/密码是否正确！'
            else:
                is_success = True
                message = ''
            #断言
            assert is_success == True

            """step2:判断保单是否存在"""
            is_success = ''
            message = ''
            unit = '保单验证'
            sql = "select * from " + db_name + ".t_pa_policy where policy_no='" + policyNo + "'"
            # 执行sql语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            if len(results) != 0:
                is_success = True
                message = ''
            else:
                is_success = False
                message = env_name + '环境，保单不存在！'
            # 加入断言
            assert is_success == True

            """step3:执行sql插入回执日期"""
            #初始化
            is_success = ''
            message = ''
            unit = '执行sql插入回执日期'
            #定义sql
            sql = "UPDATE " + db_name + ".t_pa_policy SET POLICY_DELIVERY_DATE='" +callBackDate + "' WHERE POLICY_NO='" + policyNo + "';"
            try:
                # 执行sql语句
                cursor.execute(sql)
                # 提交到数据库执行
                db.commit()
            except:
                is_success = False
                message = '执行sql插入回执日期未成功，请检查数据库用户权限是否支持改sql！'
            else:
                is_success = True
                message = ''
            #断言
            assert is_success == True

            """step4:查询是否插入回执日期成功"""
            #初始化
            is_success = ''
            message = ''
            unit = '查询是否插入回执日期成功'
            sql = "select POLICY_DELIVERY_DATE from " + db_name + ".t_pa_policy where policy_no='" + policyNo + "'"
            # 执行sql语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            if results[0][0].strftime('%Y-%m-%d') == callBackDate:
                is_success = True
                message = ''
            else:
                is_success = False
                message = '回执日期未插入成功！'
            # 加入断言
            assert is_success == True

            #存入dict
            dict['logInfo']['code'] = '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('保单回执（数据库插入回执日期）_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
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
            callBackDate = '2021-05-19'   #保单回执日期
            policyNo = '8088618973999068'   #保单号
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位:脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                db_user = ''
                db_password = ''
                callBackDate = ''
                policyNo = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','db_user','db_password','callBackDate','policyNo']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                db_user = rs[2][1]   #数据库登录用户名
                db_password = rs[2][2]   #数据库登录密码
                callBackDate = rs[2][3]   #保单回执日期
                policyNo = rs[2][4]   #保单号
        #录入字段中待校验列表
        key_dict = {'env_name':env_name,'callBackDate':callBackDate}
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

        #3.定义dict
        if is_run == True:
            msg = ''
        dict = {'execNo': execNo, 'public':{'env_name':env_name, 'policyNo':policyNo,'callBackDate':callBackDate,'db_ip':db_ip,'db_user':db_user,'db_password':db_password,'db_name':db_name},'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':''}}

        #4.1定义logging文件路径
        if 'win' in sys.platform:
            logging_filename = 'D:\\xLibrary\\chunyu\\%s.html' % str(execNo)
            #判断windows是否存在某文件，存在则删除文件
            if os.path.exists(logging_filename):
                os.remove(logging_filename)
        else:
            logging_filename = '/data/xServer/xReport/%s.html' % str(execNo)
        #4.2定义logging格式
        logging.basicConfig(level=logging.WARNING , format='%(message)s  &nbsp&nbsp&nbsp&nbsp%(asctime)s <br/><br/>', filename=logging_filename, filemode='a')
        #5.执行脚本
        if is_run == True:
            dict = sys_API0033().nb_receipt(dict)
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
                    print '是否保单回执（数据库插入回执日期）成功:成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['public']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('回执日期：' + dict['public']['callBackDate']).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '是否保单回执（数据库插入回执日期）成功:不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['public']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('回执日期：' + dict['public']['callBackDate']).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:    #非windows系统平台
                if dict['logInfo']['code'] == '1':
                    result_str = "是否保单回执（数据库插入回执日期）成功：成功,,环境：%s,,保单号：%s,,回执日期：%s,,耗时：%s" % (env_name, dict['public']['policyNo'], dict['public']['callBackDate'], API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "是否保单回执（数据库插入回执日期）成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,回执日期：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, dict['public']['policyNo'], dict['public']['callBackDate'], API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())







