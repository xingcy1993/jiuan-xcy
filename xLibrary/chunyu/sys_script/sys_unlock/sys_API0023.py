#coding=utf-8

import sys
import time
import json
import logging
import datetime
import requests
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys);
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *



"""
1.登录系统
2.系统解锁
3.登出用户
"""
class sys_API0023:

    def __init__(self):
        pass

    @func_set_timeout(10)#设定函数超执行时间   
    def sys_unlock(self, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('系统用户解锁_开始(预计总耗时:2s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            #1.登录系统
            dict = sys_API0023().login_tool(dict)
            assert dict['logInfo']['code'] == '1'
            #2.系统用户解锁接口
            dict = sys_API0023().deblockingt_tool(dict)
            assert dict['logInfo']['code'] == '1'
            #3.登出系统
            dict = sys_API0023().logout_tool(dict)
            #断言
            assert dict['logInfo']['code'] == '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('系统用户解锁结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = 0
            #异常场景-登出系统（防止与用户被挂起）
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                #记录运行异常-用户解锁日志
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        finally:
            pass
        return dict


    # 登录系统
    def login_tool(self, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录开始日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统_开始(预计耗时:0.5s)'))
            #初始化
            magicX = ''
            unit = '登录系统'  # 节点
            is_success = ''
            message = ''
            dict['logInfo']['code'] = '0'
            # dict取值+定义数据
            env_name = dict['public']['env_name']   #环境名称
            username_entry = dict['public']['username_entry']   #登录用户名
            interface_ip = dict['public']['interface_ip']    #系统ip
            # 调用原子化脚本
            rs = API0000_sys_otherapi().login(env_name, username_entry, interface_ip)
            is_success = rs[0]
            message = rs[1] 
            magicX = rs[2]
            #断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'    #存入无异常标识
            dict['public']['magicX'] = magicX    #存入会话id
            end_time = datetime.datetime.now()   #结束时间
            #记录结束日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



    # 登出系统
    def logout_tool(self, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登出系统_开始(预计耗时:0.5s)'))
            #初始化
            unit = '登出系统'  # 节点
            is_success = ''
            message = ''
            # dict取值+定义数据
            magicX = dict['public']['magicX']
            interface_ip = dict['public']['interface_ip']
            # 调用原子化脚本
            rs = API0000_sys_otherapi().logout(magicX, interface_ip)
            is_success = rs[0]
            message = rs[1] 
            # 加入断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'    #记录无异常标识
            magicX = ''   #登出系统后magicX初始化
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登出系统_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n').decode('utf-8').encode('gbk') + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict


    # 系统用户解锁
    def deblockingt_tool(self, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*系统用户解锁_开始(预计耗时:0.5s)'))
            #初始化
            unit = '系统用户解锁'  # 节点
            is_success = ''
            message = ''
            # dict取值+定义数据
            magicX = dict['public']['magicX']
            interface_ip = dict['public']['interface_ip']
            userName = dict['public']['userName']
            # 调用原子化脚本
            rs = API0000_sys_otherapi().deblocking(magicX, interface_ip, userName)
            is_success = rs[0]
            message = rs[1] 
            # 加入断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'   #存入无异常标识
            magicX = ''    #初始会话id
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*系统用户解锁_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
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
        #2.本地定义/服务端获取-：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = '预生产'   #环境名称
            env_name = env_name.encode('utf-8')
            userName = 'xcy1'    # 待解锁用户名 
        else:    #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                userName = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','userName']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                userName = rs[2][1]   #待解锁用户名
        #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = {'public':{'env_name':env_name,'interface_ip':interface_ip,'magicX':'','userName':userName,'username_entry':'csu200'},'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'', 'job':''}}
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
            dict = sys_API0023().sys_unlock(dict)
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = 0
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            #记录运行异常-用户解锁日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
    except func_timeout.exceptions.FunctionTimedOut:
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:
                if dict['logInfo']['code'] == '1':
                    print '是否解锁成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('被解锁用户为：' + userName).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '是否解锁成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('被解锁用户为：' + userName).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "是否解锁成功：成功,,环境：%s,,被解锁用户为：%s,,耗时：%s" % (env_name, userName, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "是否解锁成功：不成功,,不成功原因：%s,,环境：%s,,被解锁用户为：%s,,耗时:%s" % (dict['logInfo']['msg'], env_name, userName, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())
