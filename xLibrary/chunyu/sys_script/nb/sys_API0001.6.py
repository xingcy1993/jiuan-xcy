#coding=utf-8

import os
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
from xLibrary.chunyu.sys_script.nb.sys_API0001 import sys_API0001
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002


"""承保前撤单:
    1.验证录入用户是否可正常登录系统
    2.登录系统
    3.承保前撤单查询接口
    4.承保前撤单提交接口
    5.退出系统
"""
class sys_API0001_6:

    def __init__(self):
        pass

    @func_set_timeout(180)#设定函数超执行时间 
    def policyCancle(self,env_name, dict):

        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('承保前撤单_开始(预计耗时:不需修改系统时间60s;需修改系统时间1分50s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            job = dict['logInfo']['job']   #场景名
            magicX = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']
            username_entry = dict['public']['username_entry']
            interface_ip = dict['public']['interface_ip']
            proposalNo = dict['public']['proposalNo']   #投保单号
            withdrawalReason = dict['public']['withdrawalReason'][0:2]   #撤单原因

            """step1:验证录入用户是否可正常登录系统"""
            #节点初始化
            is_success = ''
            message = ''
            unit = "验证录入用户是否可正常登录系统"   #节点
            #验证用户是否可正常登录系统
            rs = API0000_diy().verify_userlogin(env_name, username_entry, interface_ip)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True

            """step2:登录系统"""
            #节点初始化
            is_success = ''
            unit = '登录系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username_entry, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            dict['public']['magicX'] = magicX
            assert is_success == True

            #step3:承保前撤单查询接口
            #初始化
            is_success = ''
            message = ''
            unit = '承保前撤单查询接口'
            policyNo = ''   #保单号
            #调用原子脚本
            response = API0000_nb().queryPolicyCancle(magicX, interface_ip, proposalNo, policyNo)
            #获取所需响应值
            if response['isSuccess'] == True:
                if len(response['resultData']) > 0:
                    is_success = True
                    message = ''
                    resultData = response['resultData']
                else:
                    is_success = False
                    message = '承保前撤单查询接口未查询到数据！'  
                    resultData = ''
            else:
                is_success = False
                message = response['message']
                resultData = ''
            # 加入断言
            assert is_success == True

            #判断保单状态是否满足撤单
            if str(resultData[0]['policyStatus']) not in ('11','12','21','22'):
                is_success = False
                message = '新契约状态不满足‘承保前撤保！’'
            assert is_success == True

            #step4:承保前撤单提交接口
            #初始化
            is_success = ''
            message = ''
            unit = '承保前撤单提交接口'
            policyNo = ''   #保单号
            withDraw = 'pass'   #撤单说明
            policyType = resultData[0]['policyType']   #保单类型
            #调用原子脚本
            response = API0000_nb().withDrawproposal(magicX, interface_ip, proposalNo, policyNo, withDraw, policyType, withdrawalReason)
            #获取所需响应值
            if response['success'] == True and response['message'] == '撤件成功':
                is_success = True
                message = ''
            else:
                is_success = False
                message = response['message']
            # 加入断言
            assert is_success == True

            #step4:登出系统
            #初始化
            is_success = ''
            unit = '登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX, interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            assert is_success == True

            #存入dict
            dict['public']['magicX'] = ''
            dict['logInfo']['code'] = '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('承保前撤单_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'   #dict['logInfo']['code']记录异常标识
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n') + traceback.format_exc())
            #异常场景-登出系统（防止与用户被挂起）
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
                dict['public']['magicX'] = ''
        except func_timeout.exceptions.FunctionTimedOut:
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出（可能他人改时间重启服务请检查！）'))
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。（可能他人改时间重启服务请检查！）' + dict['logInfo']['msg']
            #异常场景-登出系统（防止与用户被挂起）
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
                dict['public']['magicX'] = ''
        finally:
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



        
if __name__ == "__main__":   
    try:
        begin_time = datetime.datetime.now()   #开始时间
        #1.初始化
        is_run = True   #是否执行python脚本 
        msg = ''   #执行python脚本前存在的错误信息
        job = 'policyCancle'   #场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = '预生产'
            env_name = env_name.encode('utf-8')
            proposalNo = '9657612342235005'   #投保单号
            withdrawalReason = '01-客户申请'   #撤单原因。01-客户申请；03-银行撤件
            username_entry = 'xcy1'   #登录系统用户
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                proposalNo = ''   
                withdrawalReason = '' 
                username_entry = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','proposalNo','withdrawalReason','username_entry']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                proposalNo = rs[2][1]   #投保单号
                withdrawalReason = rs[2][2]   #撤单原因
                username_entry = rs[2][3]   #登录系统用户
        #去除两端空格
        proposalNo = proposalNo.strip()   
        withdrawalReason = withdrawalReason.strip()   
        username_entry = username_entry.strip()   
        #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name,'withdrawalReason':withdrawalReason[0:2]}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = {'execNo': execNo, 'public': {'env_name':env_name, 'proposalNo':proposalNo, 'withdrawalReason':withdrawalReason, 'username_entry':username_entry, 'interface_ip':interface_ip, 'magicX':''}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'', 'job':job}, 'track_info': []}

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
            dict = sys_API0001_6().policyCancle(env_name, dict)
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
    except func_timeout.exceptions.FunctionTimedOut:    #函数超时异常的捕捉
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出（可能他人改时间重启服务请检查！）'))
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。（可能他人改时间重启服务请检查！）' + dict['logInfo']['msg']
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
    finally:
        try:
            end_time = datetime.datetime.now()   #记录结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:   #windows系统平台
                if dict['logInfo']['code'] == '1':
                    print '是否承保前撤单成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('投保单号：' + proposalNo).decode('utf-8').encode('gb2312')
                    print ('撤单原因：' + withdrawalReason).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '是否承保前撤单成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('投保单号：' + proposalNo).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:    #非windows系统平台
                if dict['logInfo']['code'] == '1':
                    result_str = "是否承保前撤单成功：成功,,环境：%s,,投保单号：%s,,撤单原因：%s,,耗时：%s" % (env_name, proposalNo, withdrawalReason, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "是否承保前撤单成功：不成功,,不成功原因：%s,,环境：%s,,投保单号：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, proposalNo, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())







