# coding=utf-8

import sys
import time
import logging
import pymysql
import requests
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *




"""系统退保试算:
       step1:验证录入用户是否可正常登录系统
       step2:登录系统
       step3:退保试算
       step4:退出系统
       step5:定义轨迹信息+检查点信息
             1.定义轨迹信息
             2.定义检查点信息
"""
class sys_API0013:
    def __init__(self):
        pass


    @func_set_timeout(60)#设定函数超执行时间
    def trial_tb(self, validateDate, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('退保试算_开始(预计耗时:20s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            #试算
            rs = self.trial(validateDate, dict) 
            resultData = rs[0]
            dict = rs[1]
            assert dict['logInfo']['code'] == '1'   #断言是否异常 
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('退保试算_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
        finally:
            #dict存入检查点信息
            if dict['logInfo']['code'] == '1':
                dict = self.save_check_info(validateDate, resultData, dict) 
        return dict


    @func_set_timeout(30)#设定函数超执行时间
    def trial(self, validateDate, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp试算开始*(预计耗时:10s)'))
            #初始化
            magicX = ''
            """step1:验证录入用户是否可正常登录系统"""
            #节点初始化
            is_success = ''
            message = ''
            unit = "系统-退保试算_验证录入用户是否可正常登录系统"   #节点
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']
            username = dict['public']['username_entry']
            interface_ip = dict['public']['interface_ip']
            
            #验证用户是否可正常登录系统
            rs = API0000_diy().verify_userlogin(env_name, username, interface_ip)
            is_success = rs[0]
            message = rs[1]
            time.sleep(5)
            """ste2:登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-退保试算_登录系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            assert is_success == True

            """step3:退保试算接口"""
            #节点初始化
            is_success = ''
            unit = '系统-退保试算接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            policyNo = dict['policy_info']['policyNo']
            #调用原子脚本
            response = API0000_pa().trial_tb(magicX, interface_ip, policyNo, validateDate)
            #获取所需响应值
            is_success = response['isSuccess']
            if is_success:
                message = ''
                resultData = response['resultData']
            else:
                message = response['message']
                resultData = ''
            assert is_success == True
            
            """step4:登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-退保试算_登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX, interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'   #记录无异常标识
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*试算_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return resultData,  dict




    @func_set_timeout(30)#设定函数超执行时间
    def save_check_info(self, validateDate, resultData, dict):
        try:
            if dict['logInfo']['code'] == '1': 
                #1.定义检查点信息
                #节点初始化
                is_success = ''
                unit = '系统-退保_定义检查点信息'  # 节点
                message = ''
                product = []   #定义退保产品列表
                payment = 0   #定义总退保金额
                for i in range(0,len(resultData)):
                    #产品代码
                    productCode = str(resultData[i]['productCode'])
                    #现金价值
                    if resultData[i]['presentPrice'] == None:
                        presentPrice = 0
                    else:
                        presentPrice = float(resultData[i]['presentPrice'])
                    #万能账户价值   
                    if resultData[i]['investAmount'] == None:
                        investAmount = 0
                    else:
                        investAmount = float(resultData[i]['investAmount'])
                    #手续费  
                    if resultData[i]['chargeAmount'] == None:
                        chargeAmount = 0
                    else:
                        chargeAmount = float(resultData[i]['chargeAmount'])
                    #欠款余额  
                    if resultData[i]['loanAccountAmount'] == None:
                        loanAccountAmount = 0
                    else:
                        loanAccountAmount = float(resultData[i]['loanAccountAmount'])
                    #退还续期保费    
                    if resultData[i]['refundRenewPrem'] == None:
                        refundRenewPrem = 0
                    else:
                        refundRenewPrem = float(resultData[i]['refundRenewPrem'])
                    #累计生息账号  
                    if resultData[i]['cbSbAccount'] == None:
                        cbSbAccount = 0
                    else:
                        cbSbAccount = float(resultData[i]['cbSbAccount'])
                    #退还未到期风险保险费
                    if resultData[i]['riskChargeFee'] == None:
                        riskChargeFee = 0
                    else:
                        riskChargeFee = float(resultData[i]['riskChargeFee'])
                    #红利累计生息账户
                    if resultData[i]['bonusAccount'] == None:
                        bonusAccount = 0
                    else:
                        bonusAccount = float(resultData[i]['bonusAccount'])
                    #已分红金额扣回  
                    if resultData[i]['bonusAccount'] == None:
                        paidBonus = 0
                    else:
                        paidBonus = float(resultData[i]['paidBonus'])
                    #应付金额  
                    if resultData[i]['surrenderAmount'] == None:
                        paidBonus = 0
                    else:
                        surrenderAmount = float(resultData[i]['surrenderAmount'])

                    #每个产品退保检查点追加到product退保产品列表中
                    product.append({'productCode':productCode, 'presentPrice':presentPrice, 'investAmount':investAmount, 'chargeAmount':chargeAmount, 'loanAccountAmount':loanAccountAmount, 'refundRenewPrem':refundRenewPrem, 'cbSbAccount':cbSbAccount, 'riskChargeFee':riskChargeFee, 'bonusAccount':bonusAccount, 'paidBonus':paidBonus, 'surrenderAmount':surrenderAmount})   
                    #总退保金额
                    payment = payment + surrenderAmount
                #存入dict检查点中
                calc_trial_tb = {'apply_date':validateDate, 'product':product, 'payment':payment, 'msg': ''}   #定义每期续期的续期信息
                dict['check']['calc_trial_tb'].append(calc_trial_tb)
                """2.定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'trial_tb', 'trackTime': validateDate, 'trackData':{'product':product, 'payment':payment}, 'msg': ''}
                dict['track_info'].append(track_info)   #存入轨迹信息
            else:
                message = dict['logInfo']['msg']
                err = dict['logInfo']['err']
                if dict['logInfo']['msg'] == None or dict['logInfo']['msg'] == '':
                    message = str(dict['logInfo']['err'])
                #存入dict检查点中
                calc_trial_tb = {'apply_date':validateDate, 'product':'', 'payment':'', 'msg': message}   #定义每期续期的续期信息
                dict['check']['calc_trial_tb'].append(calc_trial_tb)
                #定义轨迹信息
                track_info = {'trackType':'trial_tb', 'trackTime': validateDate, 'trackData':{'product':'', 'payment':''}, 'msg': message}
                dict['track_info'].append(track_info)   #存入轨迹信息
        except Exception, e:
            dict['logInfo']['code'] = '0'    #记录异常标识
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        finally:
            pass
        return dict


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING , format='%(message)s  %(asctime)s')
    
    #1.自定义录入
    execNo = 'test001'   #测试编号
    env_name = '预生产'
    env_name = env_name.encode('utf-8')
    policyNo = '8088646849048068'
    validateDate = '2021-03-12'   #保全申请日期
    username_entry = 'xcy1'   #保全录入用户名
    interface_ip = API0000_diy().ip_conf(env_name)

    #2.定义dict
    env_name = '预生产'
    env_name = env_name.encode('utf-8')
    dict = {'execNo': execNo, 'policy_info':{'policyNo': policyNo},'public': {'env_name':env_name, 'username_entry': username_entry, 'interface_ip': interface_ip}, 'logInfo': {'code':'0', 'msg':'', 'err':'', 'result':'', 'unit':''}, 'track_info': [], 'check':{'calc_trial_tb':[]}}

    #3.执行脚本
    dict = sys_API0013().trial_tb(validateDate, dict)
    assert dict['logInfo']['code'] == '1'
    print '------------'
    print dict


