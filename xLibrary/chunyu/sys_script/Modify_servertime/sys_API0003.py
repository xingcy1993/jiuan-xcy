#coding=utf-8

import sys
import time
import json
import logging
import datetime
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding('utf8')
from xLibrary.chunyu.API0000 import *



"""获取当前服务器时间"""
class sys_API0003:

    def __init__(self):
        pass

    """获取当前服务器时间"""
    @func_set_timeout(10)#设定函数超执行时间 
    def Get_servertime(self, dict):        
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('获取服务器时间_开始(预计耗时:1s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            is_success = '' #初始化异常标识
            message = ''    #初始化信息
            unit = '获取服务器时间'    #节点标识
            servicetime = ''    #初始化服务器时间 
            env_name = dict['public']['env_name']    #环境名称
            #获取当期服务器时间
            servicetime = API0000_diy().get_date(env_name)  # 获取当期服务器时间 并转换为正常格式：年-月-日
            #断言
            assert servicetime != ''
            #存入dict
            is_success = True
            dict['public']['servicetime'] = servicetime   #系统时间
            dict['logInfo']['code'] = '1'   #记录无异常标识
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('获取服务器时间_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            message = '获取服务器时间不成功'
            dict['logInfo']['code'] = '0'
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict




if __name__ == "__main__":
    try:
        begin_time = datetime.datetime.now()   #开始时间
        #1.初始化
        is_run = True   #是否执行python脚本 
        msg = ''   #执行python脚本前存在的错误信息
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = 'uat6'   #环境类型
            env_name = env_name.encode('utf-8')
        else:    #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
        #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = {'public': {'env_name':env_name, 'servicetime':''}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'', 'unit':''}}
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
        if is_run == True:
            dict = sys_API0003().Get_servertime(dict)
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出。'))
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:
                if dict['logInfo']['code'] == '1':
                    print '是否获取成功：成功'.decode('utf-8').encode('gb2312')
                    print (env_name + '环境系统时间为：' + dict['public']['servicetime']).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '是否获取成功：不成功（请检查docker密码是否被改动，或者是否环境不稳定）'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "是否获取成功：成功,,%s环境系统时间为：%s,,耗时：%s" % (env_name, dict['public']['servicetime'], API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "是否获取成功：不成功（请检查docker密码是否被改动，或者是否环境不稳定）,,环境：%s,,耗时：%s" % (env_name, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())
