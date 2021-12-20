# coding=utf-8

import sys
import time
import pymysql
import requests
import logging
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *



"""系统保全撤销:
       step1:验证录入用户是否可正常登录系统
       step2:登录系统
       step3:保全撤销查询接口
            1.接口成功:
                （1）无查询结果:
                     登出系统
                     定义轨迹信息
                     记录日志result = '保单无挂起保单，无需保全撤销'
                     结束此函数
                （2）存在查询结果:
                     遍历每个查询结果，保全撤销
            2.接口不成功
"""
class sys_API0014:
    def __init__(self):
        pass

    @func_set_timeout(10)#设定函数超执行时间
    def csCancle(self, dict):
        try:
            #初始化
            magicX = ''
            dict['logInfo']['code'] = '0'
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('保全撤销开始(预计耗时:5s)'))
            """step1:验证录入用户是否可正常登录系统"""
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*验证录入用户是否可正常登录系统开始'))
            #节点初始化
            is_success = ''
            message = ''
            unit = "系统-保全撤销_验证录入用户是否可正常登录系统"   #节点
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']
            username = dict['public']['username_entry']
            interface_ip = dict['public']['interface_ip']
            
            #验证用户是否可正常登录系统
            rs = API0000_diy().verify_userlogin(env_name, username, interface_ip)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*验证录入用户是否可正常登录系统结束'))

            """ste2:登录系统"""
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统开始'))
            #节点初始化
            is_success = ''
            unit = '系统-保全撤销_登录系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            assert is_success == True
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统结束'))

            """step3:保全撤销查询接口"""
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全撤销开始'))
            #节点初始化
            is_success = ''
            unit = '系统-保全撤销_保全撤销查询接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            policyNo = dict['policy_info']['policyNo']    #保单号
            #调用原子脚本
            response = API0000_pa().csCancle_queryCsInfoList(magicX, interface_ip, policyNo) 
            #获取所需响应值
            is_success = response['isSuccess']
            resultData = response['resultData']   #查询结果数据
            """如果1.接口成功；2.接口不成功"""
            if is_success:
                #(1)若无查询结果:退出系统，记录日志 result = '保单无挂起保单，无需保全撤销'，结束此函数
                if len(resultData) == 0:
                    is_success = False
                    message = '保单无挂起保单，无需保全撤销'                
                #(2)保全撤销接口存在查询结果:遍历每个挂起保全进行撤销
                else:
                    #获取查询信息    
                    is_success = ''
                    unit = '系统-保全撤销接口'  # 节点
                    #dict获取数据+定义数据
                    policyNo = dict['policy_info']['policyNo']    #保单号
                    message = ''
                    for i in range(0, len(response['resultData'])):
                        changeId = response['resultData'][i]['changeId']
                        partitionIndi = response['resultData'][i]['partitionIndi']
                        serviceCode = response['resultData'][i]['serviceCode']    #保全受理号
                        applyNo = response['resultData'][i]['applyNo']    #保全受理号
                        #保全撤销接口
                        #调用原子脚本
                        response1 = API0000_pa().csCancle(magicX, interface_ip, applyNo) 
                        #获取所需响应值
                        is_success = response1['success']
                        if is_success:
                            message = ''
                        else:
                            message = response1['message']
                        assert is_success == True
                #接口不成功
            elif is_success == False:
                message = response['message']
            #断言
            assert is_success == True
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全撤销结束'))

            """登出系统"""
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登出系统开始'))
            #节点初始化
            is_success = ''
            unit = '系统-保全撤销_登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            magicX = ''
            #定义轨迹信息
            track_info = {'trackType':'csCancle', 'trackTime':'', 'trackData':{'serviceCode':serviceCode}, 'msg': ''}
            dict['track_info'].append(track_info)   #存入轨迹信息
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登出系统结束'))
            logging.warning(API0000_diy().text_conversion('保全撤销结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
            #存入dict
            dict['logInfo']['code'] = '1'
        except Exception, e:
            dict['logInfo']['err'] = unit + ':' + str(e)
            dict['logInfo']['code'] = '0'
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                username = dict['public']['username_entry']    #新契约复核用户
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置-' + unit + ':\n')  + traceback.format_exc())
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
            env_name = '预生产'    #环境类型
            env_name = env_name.encode('utf-8')
            policyNo = '8088646849041068'    #保单号
            username = 'xcy1'    #登录系统用户名
        else:    #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo = ''
                username = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','policyNo','username']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo = rs[2][1]   #保单号
                username = rs[2][2]   #登录系统用户名
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
        dict = {'execNo': execNo, 'policy_info':{'policyNo':policyNo},'public': {'env_name':env_name, 'username_entry':username, 'interface_ip':interface_ip}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':''}, 'track_info':[]}
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
            dict = sys_API0014().csCancle(dict)
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
    except func_timeout.exceptions.FunctionTimedOut:
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出&' + dict['logInfo']['msg']
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:   #windows系统平台
                if dict['logInfo']['code'] == '1':
                    print '保全撤销是否成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '保全撤销是否成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "保全撤销是否成功：成功,,环境：%s,,保单号：%s,,耗时：%s" % (env_name, dict['policy_info']['policyNo'], API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "保全撤销是否成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, dict['policy_info']['policyNo'], API0000_diy().logger_count_time(begin_time, end_time))
                print result_str

            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())

