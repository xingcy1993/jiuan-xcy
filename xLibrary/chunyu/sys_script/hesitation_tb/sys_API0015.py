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
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002




"""系统犹豫期内犹豫期退保申请+撤销:
       step1:保全录入:
             1.保全录入用户登录系统
             2.保全申请接口
             3.保全录入-产品信息详细
       step2:保全撤销
             1.保全撤销查询口
               （1）接口成功:无查询结果；存在查询结果
               （2）接口不成功
             2.保全撤销接口
             3.登出系统
       step3:定义轨迹信息+检查点信息:
             1.定义轨迹信息
             2.定义检查点信息
"""
class sys_API0015:

    def __init__(self):
        pass

    @func_set_timeout(120)#设定函数超执行时间
    def hesitation_tb_csCancle(self, apply_date, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('犹豫期内犹豫期退保申请+撤销_开始(预计耗时:40s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            payment = 0
            #保全录入
            rs = self.pa_entry(apply_date, dict) 
            payment = rs[0]
            dict = rs[1]
            assert dict['logInfo']['code'] == '1'   #断言是否异常 
            #保全撤销
            dict = self.csCancle(dict)  
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('犹豫期内犹豫期退保申请+撤销_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
        finally:
            #dict存入检查点信息
            dict = self.save_check_info(apply_date, payment, dict) 
            assert dict['logInfo']['code'] == '1'   #断言是否异常
        return dict


    @func_set_timeout(60)#设定函数超执行时间
    def pa_entry(self, apply_date, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全录入_开始(预计耗时:30s)'))
            #初始化
            magicX = ''
            """step1:保全录入"""
            """1.保全录入用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全犹豫期退保_保全录入用户登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username = dict['public']['username_entry']    #保全录入用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            # 加入断言
            assert is_success == True 

            """2.保全申请接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全犹豫期退保_保全申请接口'  # 节点
            message = ''
            payment = 0   #定义应付金额默认为0
            #dict获取数据+定义数据
            policyNo = dict['policy_info']['policyNo']    #保单号
            applyTime = apply_date   #保全申请日期
            applyWay = '3'    #保全申请来源
            applyType = '1'    #保全申请方式
            serviceCode = '30100'  #保全申请项目编号
            #调用原子脚本
            response = API0000_pa().saveCsApplylication(magicX, interface_ip, applyTime, applyWay, applyType, serviceCode, policyNo) 
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
                partitionIndi = str(response['others']['partitionIndi'])
                changeId = response['others']['changeId']
                applyNo = response['others']['applyNo']
                subSalesChannel = response['others']['subSalesChannel']
                policyDeliveryMode = response['others']['policyDeliveryMode']
            else:
                message = response['message']
                partitionIndi = ''
                changeId = ''
                applyNo = ''
                subSalesChannel = ''
                policyDeliveryMode = ''
            # 加入断言
            assert is_success == True 

            """3.保全录入-产品信息详细"""
            #节点初始化
            is_success = ''
            unit = '系统-保全犹豫期退保_保全录入-产品信息详细'  # 节点
            message = ''
            #dict获取数据+定义数据
            hesitation_tb_dict = []   #hesitation_tb_dict。存入产品的犹豫期退保数据信息   
            #调用原子脚本
            response = API0000_pa().queryCsPolicyProductBeforeChange(magicX, interface_ip, policyNo, changeId, partitionIndi, serviceCode) 
            #获取所需响应值
            is_success = response['isSuccess']

            if is_success:
                message = ''
                resultData = response['resultData']
            else:
                message = response['message']
                resultData = ''
                #组装定义loan_dict产品的犹豫期退保数据信息 
            for i in range(0,len(resultData)):
                surrenderAmount = float(resultData[i]['surrenderAmount'])   #应付金额
                payment = payment + surrenderAmount   #各产品应付金额合计
            # 加入断言
            assert is_success == True 

            """4.登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-犹退-登出系统'  # 节点
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
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全录入_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
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
        return payment, dict




    @func_set_timeout(60)#设定函数超执行时间
    def csCancle(self, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全撤销_开始(预计耗时:10s)'))

            """1.保全录入用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全犹豫期退保_保全录入用户登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username = dict['public']['username_entry']    #保全录入用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            # 加入断言
            assert is_success == True 
            """step2:保全撤销"""
            #节点初始化
            is_success = ''
            unit = '系统-保全撤销_保全撤销查询接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            policyNo = dict['policy_info']['policyNo']    #保单号
            """1.保全撤销查询接口"""
            #调用原子脚本
            response = API0000_pa().csCancle_queryCsInfoList(magicX, interface_ip, policyNo) 
            #获取所需响应值
            is_success = response['isSuccess']
            resultData = response['resultData']   #查询结果数据
            if is_success:
                #若无查询结果:退出系统，记录日志 result = '保单无挂起保单，无需保全撤销'，结束此函数
                if len(resultData) == 0:
                    """登出系统"""
                    is_success = ''
                    unit = '系统-保全撤销_登出系统'  # 节点
                    message = ''
                    rs = API0000_sys_otherapi().logout(magicX, interface_ip)
                    #获取所需响应值
                    magicX = ''
                    is_success = rs[0]
                    message = rs[1]
                    assert is_success == True
                    #记录日志
                    dict['logInfo']['result'] = '保单无挂起保单，无需保全撤销'
                    
                    #录轨迹信息
                    is_success = ''
                    unit = '系统-保全撤销_定义轨迹信息'  # 节点
                    message = ''
                    #定义轨迹信息
                    track_info = {'trackType':'csCancle', 'trackTime':'', 'trackData':{'serviceCode':''}}   #无保全挂起记录，serviceCode记录为''
                    dict['track_info'].append(track_info)   #存入轨迹信息
                    #结束函数
                    return dict
                #保全撤销接口存在查询结果:遍历每个挂起保全进行撤销
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
                        """2.保全撤销接口"""
                        #调用原子脚本
                        response1 = API0000_pa().csCancle(magicX, interface_ip, applyNo) 
                        #获取所需响应值
                        is_success = response1['success']
                        if is_success:
                            message = ''
                        else:
                            message = response1['message']
                        assert is_success == True
                #保全撤销接口报错
            elif is_success == False:
                message = response['message']
            #断言
            assert is_success == True
            
            """3.登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-犹退-登出系统'  # 节点
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
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全撤销_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
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
        return dict



    @func_set_timeout(30)#设定函数超执行时间
    def save_check_info(self, apply_date, payment, dict):
        try:
            if dict['logInfo']['code'] == '1':
                """1.定义检查点信息"""
                dict['check']['calc_hesitation_tb']['apply_date'] = apply_date
                dict['check']['calc_hesitation_tb']['payment'] = payment
                dict['check']['calc_hesitation_tb']['msg'] = ''
                """2.定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'trial_hesitation_tb', 'trackTime':apply_date, 'trackData':{'payment':payment}, 'msg': ''}
                dict['track_info'].append(track_info)   #存入轨迹信息
            else:
                message = dict['logInfo']['msg']
                err = dict['logInfo']['err']
                if dict['logInfo']['msg'] == None or dict['logInfo']['msg'] == '':
                    message = str(dict['logInfo']['err'])
                """1.定义检查点信息"""
                dict['check']['calc_hesitation_tb']['apply_date'] = apply_date
                dict['check']['calc_hesitation_tb']['payment'] = payment
                dict['check']['calc_hesitation_tb']['msg'] = message
                """2.定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'trial_hesitation_tb', 'trackTime':apply_date, 'trackData':{'payment':payment}, 'msg': message}
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
    job = 'hesitation_tb_csCancle'   #场景名
    execNo = 'test001'   #测试编号
    env_name = '预生产'
    env_name = env_name.encode('utf-8')
    policyNo = '8088619798722268'
    apply_date = '2017-03-12'   #保全申请日期
    username_entry = 'xcy1'   #保全录入用户名
    username_review = 'xcy2'   #保全复核用户名
    interface_ip = API0000_diy().ip_conf(env_name)

    #2.定义dict
    env_name = '预生产'
    env_name = env_name.encode('utf-8')
    dict = {'execNo': execNo, 'policy_info':{'policyNo':policyNo},'public': {'env_name':env_name, 'username_entry':username_entry, 'username_review':username_review, 'interface_ip':interface_ip}, 'logInfo': {'code':'0', 'msg':'', 'err':'', 'result':'', 'unit':''}, 'track_info': [], 'check':{'calc_hesitation_tb':{'apply_date':'', 'payment':''}}, 'track_change':[]}

    #3.调用犹豫期退保api全流程脚本
    dict = sys_API0002().Modify_servertime(apply_date, job, dict)
    assert dict['logInfo']['code'] == '1'   #断言是否异常
    dict = sys_API0015().hesitation_tb_csCancle(apply_date, dict)
    print '-----------------'
    print dict








