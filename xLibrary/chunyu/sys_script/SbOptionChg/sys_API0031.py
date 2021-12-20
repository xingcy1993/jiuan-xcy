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



"""生存给付计划变更:
       step1:保全录入:
            1.保全录入用户登录系统
            2.保全申请接口
            3.保全录入-客户受理信息接口 
            4.保全录入-保存生存给付计划变更信息接口
            5.保全录入-生存给付计划变更提交接口
            6.登出系统
       step2:保全复核:
            1.保全复核用户登录系统
            2.保全复核-保全公共工作池查询接口 
            3.保全复核-工作池领取任务接口
            4.保全复核提交接口
            5.登出系统
       step3:定义轨迹信息+检查点信息:
             1.定义轨迹信息
             2.定义检查点信息
"""
class sys_API0031:

    def __init__(self):
        pass


    @func_set_timeout(180)#设定函数超执行时间
    def SbOptionChg(self, apply_date, dict):
        """系统生存给付计划变更:
               step1:保全录入
               step2:保全复核+保全收费（转进账单）
               step3:定义轨迹信息+检查点信息:
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('生存给付计划变更_开始(预计耗时:60s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            #保全录入
            dict = self.pa_entry(apply_date, dict)  
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #保全复核
            dict = self.pa_review(apply_date, dict) 
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('生存给付计划变更_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
        finally:
            #step3:定义轨迹信息+检查点信息::
            if dict['logInfo']['code'] == '1':
                dict = self.save_check_info(apply_date, dict)
        return dict


    @func_set_timeout(60)#设定函数超执行时间
    def pa_entry(self, apply_date, dict):
        """step1:保全录入
                1.保全录入用户登录系统
                2.保全申请接口
                3.保全录入-客户受理信息接口 
                4.保全录入-保存生存给付计划变更信息接口
                5.保全录入-生存给付计划变更提交接口
                6.登出系统
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全录入_开始(预计耗时:30s)'))
            #初始化
            magicX = ''
            """1.保全录入用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全生存给付计划变更_录入用户登录系统'  # 节点
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
            unit = '系统-保全生存给付计划变更_保全申请接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            policyNo = dict['policy_info']['policyNo']    #保单号
            applyTime = apply_date   #保全申请日期
            applyWay = '3'    #保全申请来源
            applyType = '1'    #保全申请方式
            serviceCode = '50010'  #保全申请项目编号
            policyCodes = ''
            customerId = ''
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

            """3.保全录入-客户受理信息接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全生存给付计划变更_保全录入-客户受理信息接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_pa().findCsApplylication(magicX, interface_ip, env_name, applyTime, applyWay, applyType, serviceCode, policyNo, partitionIndi, changeId, applyNo, subSalesChannel,policyDeliveryMode)
            # 获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''   
                others = response['others']  
            else:
                message = response['message']
                others = ''
            assert is_success == True 
                #连接数据库
            cursor = API0000_diy().db_conf(env_name, 'wift_prop') 
            policyId = others['policyId']
            contactNumber = others['mobile']   #保全电话
            telephone = others['officeTel']   #固定电话
            customerInfoList_old = others['customerInfoList']
            customerInfoList_new = [] 
            for i in range(0,len(customerInfoList_old)):
                if customerInfoList_old[i]['customerRole'] == '01':
                    customerInfoList_new.append({})
                    customerId = str(customerInfoList_old[i]['customerId'])
                    name = customerInfoList_old[i]['name']
                    certiType = customerInfoList_old[i]['certiType']
                    birthday = customerInfoList_old[i]['birthday'] 
                        #执行sql
                    sql = "select CERTI_VALID_END_DATE from t_prop_customer where name='" + name + "' and GLOBAL_CUST_ID='" + customerId + "' ORDER BY update_time desc"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    certiValidEndDate = result[0][0].strftime('%Y-%m-%d')
                    #拼装新的customerInfoList
                    customerInfoList_new[i]['customerId'] = customerId
                    customerInfoList_new[i]['name'] = name
                    customerInfoList_new[i]['certiType'] = certiType
                    customerInfoList_new[i]['birthday'] = birthday
                    customerInfoList_new[i]['certiValidEndDate'] = certiValidEndDate
                    customerInfoList = customerInfoList_new
            # 加入断言
            assert is_success == True 

            """4.保全录入-生存给付计划变更信息保存接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全生存给付计划变更_保全录入-生存给付计划变更信息保存接口'  # 节点
            message = ''
            validationFlag = 'N'   
            SbOptionChgCause = '1'    #挂失原因
            #调用原子脚本
            response = API0000_pa().saveSbOptionChgInfo(magicX, interface_ip, validationFlag, changeId, partitionIndi, policyId, SbOptionChgCause)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            # 加入断言
            assert is_success == True 

            """5.保全录入-生存给付计划变更提交接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全生存给付计划变更_保全录入-生存给付计划变更提交接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            applyTime = applyTime + " 00:00:00"  #组装申请日期applyTime
            #调用原子脚本
            response = API0000_pa().entryConfirm_SbOptionChg(magicX, interface_ip, changeId, applyNo, partitionIndi, policyId, policyNo, subSalesChannel, applyTime, serviceCode, customerInfoList)
            # 获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            # 加入断言
            assert is_success == True 

            """6.保全录入-登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全生存给付计划变更_保全录入-登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX,interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            # 加入断言
            assert is_success == True 
            #存入dict
            dict['logInfo']['code'] = '1'   #记录无异常标识
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全录入_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict


    @func_set_timeout(60)#设定函数超执行时间
    def pa_review(self, apply_date, dict):
        """step2:保全复核
                1.保全复核用户登录系统
                2.保全复核-保全公共工作池查询接口 
                3.保全复核-工作池领取任务接口
                4.保全复核提交接口
                5.登出系统
        """
        #初始化
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全复核_开始(预计耗时:10s)'))
            #初始化
            payment = 0
            magicX = ''
            """1.保全复核用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全生存给付计划变更_保全复核用户登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username = dict['public']['username_review']    #保全复核用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name,username, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            # 加入断言
            assert is_success == True            

            """2.保全复核-保全公共工作池查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全生存给付计划变更_保全复核-保全公共工作池查询接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            policyNo = dict['policy_info']['policyNo']    #保单号
            #调用原子脚本
            response = API0000_pa().queryCsInfoList(magicX, interface_ip, policyNo) 
            #获取所需响应值
            is_success = response['isSuccess']
            if is_success == True and response['resultData'] != []:
                message = ''
                changeId = response['resultData'][0]['changeId']
                partitionIndi = str(response['resultData'][0]['partitionIndi'])
                serviceCode = response['resultData'][0]['serviceCode']
                applyNo = response['resultData'][0]['applyNo']
            elif is_success == True and response['resultData'] == []:
                is_success = False
                message = '保全公共工作池未查询此保单记录！'
            elif is_success == False:
                message = response['message']
                changeId = ''
                partitionIndi = ''
                serviceCode = ''
                applyNo = ''
            assert is_success == True
            
            """3.保全复核-工作池领取任务接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全生存给付计划变更_保全复核-工作池领取任务接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            changeIds = changeId   #组装changeIds
            #调用原子脚本
            response = API0000_pa().processLockCsChange(magicX, interface_ip, changeIds)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            # 加入断言
            assert is_success == True
            
            """4.保全复核提交接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全生存给付计划变更_保全复核提交接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_pa().csEffect(magicX, interface_ip, changeId, applyNo, serviceCode, partitionIndi, policyNo)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            # 加入断言
            assert is_success == True

            """5.保全复核-登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全生存给付计划变更_保全录入-登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX,interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            # 加入断言
            assert is_success == True
            
            """存入dict"""
            #生存给付计划变更状态、挂失原因
            dict['policy_info']['SbOptionChg'] = 'Y'   #生存给付计划变更状态。Y-生存给付计划变更；N-保单为解挂
            dict['policy_info']['SbOptionChg_reason'] = '1'    #生存给付计划变更原因（生存给付计划变更）

            dict['logInfo']['code'] = '1'   #记录无异常标识
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全复核_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
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
    def save_check_info(self, apply_date, dict):
        """step3:定义轨迹信息+检查点信息: 
                 1.定义轨迹信息
                 2.定义检查点信息
        """
        try: 
            if dict['logInfo']['code'] == '1':
                #存入dict检查点中
                calc_SbOptionChg = {'apply_date':apply_date, 'SbOptionChg':'Y', 'msg': ''}   
                dict['check']['calc_SbOptionChg'].append(calc_SbOptionChg)
                """1.定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'SbOptionChg', 'trackTime':apply_date, 'trackData':{'SbOptionChg':'Y'}, 'msg': ''}
                dict['track_info'].append(track_info)   #存入轨迹信息
            else:
                message = dict['logInfo']['msg']
                err = dict['logInfo']['err']
                if dict['logInfo']['msg'] == None or dict['logInfo']['msg'] == '':
                    message = str(dict['logInfo']['err'])
                #存入dict检查点中
                calc_SbOptionChg = {'apply_date':apply_date, 'SbOptionChg':'', 'msg': message}   
                dict['check']['calc_SbOptionChg'].append(calc_SbOptionChg)
                """1.定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'SbOptionChg', 'trackTime':apply_date, 'trackData':{'SbOptionChg':''}, 'msg': message}
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
    job = 'SbOptionChg'   #场景名
    execNo = 'test001'   #测试编号
    env_name = '预生产'
    env_name = env_name.encode('utf-8')
    policyNo = '8088617726343268'
    apply_date = '2021-04-09'   #保全申请日期
    username_entry = 'xingcy'   #保全录入用户名
    username_review = 'xingcy1'   #保全复核用户名
    interface_ip = API0000_diy().ip_conf(env_name)

    #2.定义dict
    dict = {'execNo': execNo, 'policy_info':{'policyNo': policyNo, 'SbOptionChg':'N', 'SbOptionChg_reason':''},'public': {'env_name':env_name, 'username_entry': username_entry, 'username_review': username_review, 'interface_ip': interface_ip}, 'logInfo': {'code':'0', 'msg':'', 'err':'', 'result':'', 'unit':''}, 'track_info': [], 'check':{'calc_SbOptionChg':[]}, 'track_change':[]}

    #3.执行脚本
    dict = sys_API0002().Modify_servertime(apply_date, job, dict)
    assert dict['logInfo']['code'] == '1'   #断言是否异常
    dict = sys_API0031().SbOptionChg(apply_date, dict)
    assert dict['logInfo']['code'] == '1'
    print '-------------'
    print dict








