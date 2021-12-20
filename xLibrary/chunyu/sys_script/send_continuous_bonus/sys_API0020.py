# coding=utf-8

import sys
import time
import urllib
import logging
import pymysql
import requests
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002



"""派发持续奖金:
       step1:验证录入用户是否可正常登录系统
       step2:修改服务器时间
       step3:启动单量-派发持续奖金批处理
             1.登录系统
             2.派发持续奖金批处理
       step4:判断派发持续奖金批处理是派发成功:
             1.综合查询_查询按钮接口
             2.综合查询-万能账号信息sheet页_账号记录接口
             3.登出系统
       step5:定义轨迹信息+检查点信息
             1.定义轨迹信息
             2.定义检查点信息
"""
class sys_API0020:

    def __init__(self):
        pass


    @func_set_timeout(300)#设定函数超执行时间
    def send_continuous_bonus(self, sendDate, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('持续奖金派发批处理开始(预计耗时:120s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            magicX = ''
            """step1:验证录入用户是否可正常登录系统"""
            #节点初始化
            is_success = ''
            message = ''
            unit = "系统-派发持续奖金_验证录入用户是否可正常登录系统"   #节点
            payment= 0
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']
            username = dict['public']['username_entry']
            interface_ip = dict['public']['interface_ip']
            policyNo = dict['policy_info']['policyNo']  # 保单号
            
            #验证用户是否可正常登录系统
            rs = API0000_diy().verify_userlogin(env_name, username, interface_ip)
            is_success = rs[0]
            message = rs[1]
            """step2:修改服务器时间"""
            begin_time1 = datetime.datetime.now()   #开始时间
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*修改服务器时间开始(预计耗时:60s)'))
            #节点初始化
            is_success = ''
            message = ''
            unit = "系统-派发持续奖金_修改服务器时间"   #节点
            #调用原子脚本
            old_servicetime = API0000_diy().get_date(env_name)  # 获取当期服务器时间 并转换为正常格式:年-月-日
            #若当前时间与预修改时间不相同，修改服务器时间
            if old_servicetime != sendDate: 
                new_servicetime = API0000_diy().modify_date(sendDate, env_name)   # 修改成功后，获取当期服务器时间 并转换为正常格式:年-月-日
                if new_servicetime == sendDate:
                    is_success = True
                else:
                    is_success = False
            elif old_servicetime == sendDate:
                is_success = True  
            # 加入断言
            assert is_success == True
            end_time1 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*修改服务器时间(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time1, end_time1)))

            """step3:启动派发持续奖金批处理"""
            begin_time2 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统+启用持续奖金派发批处理开始(预计耗时:60s)'))
            #1.登录系统
            #节点初始化
            is_success = ''
            unit = '系统-派发持续奖金_登录系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            assert is_success == True
            
            #2.派发持续奖金批处理
            for j in range(0,60):
                #节点初始化
                is_success = ''
                unit = '系统-派发持续奖金_启动派发持续奖金批处理'  # 节点
                message = ''
                if j in (0,5,10):
                    #(1)启动批处理-调用原子脚本:
                    batchSystem = 'PA'
                    jobId = '3002'
                    isEnable = 'Y'
                    jobName = '持续奖金派发批处理'   #批处理任务名称
                    jobName = urllib.quote(jobName)
                    response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
                    #获取所需响应值
                    if response['success'] == True and response['message'] == '[持续奖金派发批处理]更新成功':
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '持续奖金派发批处理启动失败'
                    assert is_success == True
                    time.sleep(2)

                    #(2)提交年金派发批处理接口
                    #dict获取数据+定义数据
                    policyNo = dict['policy_info']['policyNo']   #保单号
                    business_date = sendDate
                    #调用原子脚本
                    response = API0000_pa().saveBatchSubmit(magicX, interface_ip, batchSystem, jobId, policyNo, business_date)
                    #获取所需响应值
                    if response['success'] == True:
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '持续奖金派发批处理提交失败'
                    # 加入断言
                    assert is_success == True
            
                #3.判断派发持续奖金批处理是派发成功          
                #(1)综合查询_查询按钮接口
                #节点初始化
                is_success = ''
                unit = '系统-派发持续奖金_综合查询_查询按钮接口'  # 节点
                message = ''
                #dict获取数据+定义数据
                policyNo = dict['policy_info']['policyNo']
                #调用原子脚本:
                response = API0000_queryPolicy().queryPolicy(magicX, interface_ip, policyNo)
                #获取所需响应值
                resultData = response['resultData']
                # 返回是否成功，以及错误信息
                if len(resultData) > 0:
                    is_success = True
                    message = ''
                    policyId = resultData[0]['policyId']
                    proposalId = resultData[0]['proposalId']
                    proposalNo = resultData[0]['proposalNo']
                else:
                    is_success = False
                    message = response['message']
                    policyId = ''
                    proposalId = ''
                    proposalNo = ''
                assert is_success == True

                #(2)综合查询-万能账号信息sheet页_账号记录接口
                #节点初始化
                is_success = ''
                unit = '系统-派发持续奖金_综合查询-万能账号信息sheet页_账号记录接口'  # 节点
                message = ''
                #调用原子脚本:
                response = API0000_queryPolicy().universal_account(magicX, interface_ip, policyNo, proposalNo, proposalId, policyId)
                #获取所需响应值
                resultData = response['resultData']
                # 返回是否成功，以及错误信息
                if len(resultData) > 2:
                    seconds = int(str(resultData[-2]['startDate'])[0:10])   #（倒数第二位记录）截取时间戳10位再转为整型
                    if time.strftime("%Y-%m-%d", time.localtime(seconds)) == str(sendDate):
                        is_success = True
                        message = ''
                        payment = float(resultData[-2]['interestCapital'])
                        break 
                    else:
                        is_success = False
                        message = '持续奖金派发不成功'
                        time.sleep(1)
                        continue
                else:
                    is_success = False
                    message = '持续奖金派发不成功'
                    time.sleep(1)
                    continue
            #断言
            assert is_success == True
            
            #4.登出系统
            #节点初始化
            is_success = ''
            unit = '系统-派发持续奖金_登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX, interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            end_time2 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统+启用持续奖金派发批处理结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time2, end_time2)))
            
            """step4:定义轨迹信息+检查点信息"""            
            """1.定义检查点信息"""
            calc_continuous_bonus = {}
            #生存金派发信息存入dict['check']['calc_continuous_bonus']中
            calc_continuous_bonus['apply_date'] = sendDate   
            calc_continuous_bonus['payment'] = payment  
            calc_continuous_bonus['msg'] = ''  
            dict['check']['calc_continuous_bonus'].append(calc_continuous_bonus)
            """2.定义轨迹信息"""
            track_info = {'trackType':'continuous_bonus', 'trackTime':sendDate, 'trackData':{'payment':payment}, 'msg': ''}
            dict['track_info'].append(track_info)   #存入轨迹信息
            #存入dict
            dict['logInfo']['code'] = '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('持续奖金派发批处理结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['err'] = unit + ':' + str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                username = dict['public']['username_entry']    
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
            #记录异常dict
            message = dict['logInfo']['msg']
            err = dict['logInfo']['err']
            if dict['logInfo']['msg'] == None or dict['logInfo']['msg'] == '':
                message = str(dict['logInfo']['err'])
            calc_continuous_bonus = {}
            #生存金派发信息存入dict['check']['calc_continuous_bonus']中
            calc_continuous_bonus['apply_date'] = sendDate   
            calc_continuous_bonus['payment'] = payment  
            calc_continuous_bonus['msg'] = message  
            dict['check']['calc_continuous_bonus'].append(calc_continuous_bonus)
            """2.定义轨迹信息"""
            track_info = {'trackType':'continuous_bonus', 'trackTime':sendDate, 'trackData':{'payment':payment}, 'msg': message}
            dict['track_info'].append(track_info)   #存入轨迹信息
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)        
        return dict



if __name__ == "__main__": 
    logging.basicConfig(level=logging.WARNING , format='%(message)s  %(asctime)s')

    #1.自定义录入
    job = 'send_continuous_bonus'   #场景名
    execNo = 'test001'   #测试编号
    env_name = '预生产'
    env_name = env_name.encode('utf-8')
    policyNo = '8088617726341868'
    sendDate = '2027-03-11'   #持续奖金派发日期
    username_entry = 'xcy1'   #保全录入用户名
    interface_ip = API0000_diy().ip_conf(env_name)

    #2.定义dict
    env_name = '预生产'
    env_name = env_name.encode('utf-8')
    dict = {'execNo': execNo, 'policy_info':{'policyNo':policyNo},'public': {'env_name':env_name, 'username_entry':username_entry, 'interface_ip':interface_ip}, 'track_info': [], 'logInfo': {'code':'0', 'msg':'', 'err':'', 'result':'','unit':''}, 'check':{'calc_continuous_bonus':[]}, 'track_change':[]}

    #3.执行脚本
    dict = sys_API0002().Modify_servertime(sendDate, job, dict)
    assert dict['logInfo']['code'] == '1'   #断言是否异常
    dict = sys_API0020().send_continuous_bonus(sendDate, dict)
    print dict








