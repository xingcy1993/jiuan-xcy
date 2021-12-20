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



"""系统贷款还款:
       step1:保全录入
            1.保全录入用户登录系统
            2.保全申请接口
            3.保全录入-客户受理信息接口 
            4.保全录入-还款账号信息接口
            5.保全录入-支付方式及支付账户接口
            6.保全录入提交接口
            7.登出系统
       step2:保全复核+保全收费（转进账单）:
            1.保全复核用户登录系统
            2.保全复核-保全公共工作池查询接口 
            3.保全复核-工作池领取任务接口
            4.保全复核提交接口

            保全收费（进账单）:
            5.柜面收付费查询接口
            6.柜面收付费保存接口
            7.柜面收付费审核接口
            8.登出系统
       step3:定义轨迹信息+检查点信息:
            1.定义轨迹信息
            2.定义检查点信息
"""
class sys_API0008:

    def __init__(self):
        pass


    @func_set_timeout(300)#设定函数超执行时间
    def loan_repayment(self, apply_date, dict):
        """系统贷款还款:
               step1:保全录入
               step2:保全复核+保全收费（转进账单）
               step3:定义轨迹信息+检查点信息:    
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            space_times = 0   #日志打印空格次数
            if dict['logInfo']['job'][0:14] == 'complex_scenes':   #复杂场景
                space_times = 2
            else:
                space_times = 0
            dict['public']['space_times'] = space_times
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '贷款还款_开始(预计耗时:60s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            resultData = []
            payment = 0
            #保全录入
            rs = self.pa_entry(apply_date, dict)  
            resultData = rs[0]
            dict = rs[1]
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #保全复核+收付费
            rs = self.pa_review(apply_date, dict)
            payment = rs[0]   #收费费金额
            dict = rs[1]
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '贷款还款_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_review'])
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*运行异常-用户解锁'))
                dict['public']['magicX'] = ''
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_review'])
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*运行异常-用户解锁'))
                dict['public']['magicX'] = ''
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*执行时间超时退出'))
        finally:
            #step3:定义轨迹信息+检查点信息:
            if dict['logInfo']['code'] == '1':
                dict = self.save_check_info(apply_date, payment, resultData, dict)
        return dict



    @func_set_timeout(120)#设定函数超执行时间
    def pa_entry(self, apply_date, dict):
        """step1:保全录入
                1.保全录入用户登录系统
                2.保全申请接口
                3.保全录入-客户受理信息接口 
                4.保全录入-还款账号信息接口
                5.保全录入-支付方式及支付账户接口
                6.保全录入提交接口
                7.登出系统
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #初始化
            magicX = ''
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全录入_开始(预计耗时:30s)'))
            """1.保全录入用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款还款_保全录入用户登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username = dict['public']['username_entry']    #保全录入用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name,username, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            dict['public']['magicX'] = magicX
            # 加入断言
            assert is_success == True 

            """2.保全申请接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款还款_保全申请接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            policyNo = dict['policy_info']['policyNo']    #保单号
            applyTime = apply_date   #保全申请日期
            applyWay = '3'    #保全申请来源
            applyType = '1'    #保全申请方式
            serviceCode = '60500'  #保全申请项目编号
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
            unit = '系统-保全贷款还款_保全录入-客户受理信息接口'  # 节点
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
            cursor = API0000_diy().db_conf(env_name, 'wift_prop') 
            policyId = others['policyId']
            customerInfoList_old = others['customerInfoList']
            customerInfoList_new = []
                #连接数据库
            unit = '系统-保全贷款_保全录入-客户受理信息接口_连接数据库'
            for i in range(0,len(customerInfoList_old)):
                unit = '系统-保全贷款还款_保全录入-客户受理信息接口'
                customerInfoList_new.append({})
                customerId = str(customerInfoList_old[i]['customerId'])
                name = customerInfoList_old[i]['name']
                certiType = customerInfoList_old[i]['certiType']
                birthday = customerInfoList_old[i]['birthday']
                #查询数据库最后一次修改的证件止期
                sql = "select CERTI_VALID_END_DATE from t_prop_customer where name='" + name + "' and GLOBAL_CUST_ID='" + customerId + "' ORDER BY update_time desc"
                unit = '系统-保全贷款_保全录入-客户受理信息接口_数据库查询客户证件止期'
                cursor.execute(sql)
                result = cursor.fetchall()
                unit = '系统-保全贷款还款_保全录入-客户受理信息接口'
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

            """4.保全录入-还款账号信息接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款还款_保全录入-还款账号信息接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_pa().queryCsNeedRepayLoanAccount(magicX, interface_ip, policyNo, changeId, partitionIndi, serviceCode)
            #获取所需响应值
            is_success = response['isSuccess']
            resultData = response['resultData']
            if is_success:
                message = ''
                #组装csLoanAccounts
                csLoanAccounts = resultData
                for z in range(0, len(csLoanAccounts)):
                    csLoanAccounts[z]['repayFlag'] = 'Y'
                    csLoanAccounts[z]['policyPartialRmtAmount'] = csLoanAccounts[z]['principalInterest']
            else:
                message = response['message']
                csLoanAccounts = ''
            # 加入断言
            assert is_success == True 

            """5.保全录入-支付方式及支付账户接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款还款_保全录入-支付方式及支付账户接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            payMode = '00'   #保全收付费方式:00-进展单；01-银行转账
            #调用原子脚本
            response = API0000_pa().queryAccountList(magicX, interface_ip, changeId, partitionIndi, policyId, payMode, serviceCode)
            # 获取所需响应值
            is_success = response['isSuccess']
            if is_success:
                message = ''
                accountId = response['resultData'][0]['accountId']
            else:
                message = response['message']
                accountId = ''
            # 加入断言
            assert is_success == True 

            """6.保全录入-贷款还款提交接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款还款_保全录入-贷款还款提交接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            applyTime1 = applyTime + " 00:00:00"  #组装申请日期applyTime
            #调用原子脚本
            response = API0000_pa().entryConfirm_loan_repayment(magicX, interface_ip, changeId, applyNo, partitionIndi, policyId, policyNo, subSalesChannel, applyTime1, serviceCode, csLoanAccounts, payMode, accountId, customerInfoList)
            # 获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            # 加入断言
            assert is_success == True 

            """7.保全录入-登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款还款_保全录入-登出系统'  # 节点
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
            dict['public']['magicX'] = ''
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全录入_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*运行异常-用户解锁'))
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return resultData, dict



    @func_set_timeout(60)#设定函数超执行时间
    def pa_review(self, apply_date, dict):
        """step2:保全复核+保全收费（转进账单）:
                1.保全复核用户登录系统
                2.保全复核-保全公共工作池查询接口 
                3.保全复核-工作池领取任务接口
                4.保全复核提交接口

           保全收费（进账单）:
                5.柜面收付费查询接口
                6.柜面收付费保存接口
                7.柜面收付费审核接口
                8.登出系统
        """
        try:
            begin_time1 = datetime.datetime.now()   #开始时间
            #初始化
            payment = 0
            magicX = ''
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全复核_开始(预计耗时:10s)'))
            """1.保全复核用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款还款_保全复核用户登录系统'  # 节点
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
            dict['public']['magicX'] = magicX
            # 加入断言
            assert is_success == True 

            """2.保全复核-保全公共工作池查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款还款_保全复核-保全公共工作池查询接口'  # 节点
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
            unit = '系统-保全贷款还款_保全复核-工作池领取任务接口'  # 节点
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
            unit = '系统-保全贷款还款_保全复核提交接口'  # 节点
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
            end_time1 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全复核_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time1, end_time1)))


            """保全收付费"""
            begin_time2 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全收付费_开始(预计耗时:20s)'))
            """1.柜面收付费查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款还款_柜面收付费查询接口'  # 节点
            message = ''
            for k in range(0,120): 
                #调用原子脚本
                rs = API0000_payment().FeeQuery(magicX, interface_ip, policyNo)
                #获取所需响应值
                is_success = rs[0]
                message = rs[1]
                resultData = rs[2]
                if len(resultData)>0:
                    break
                else:
                    time.sleep(1)
            if len(resultData) == 0:
                message = '未查询到保单付费记录！'
            else:
                payment = float(resultData[0]['amount'])   
            # 加入断言
            assert is_success == True 

            """2.柜面收付费保存接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款还款_柜面收付费保存接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            bankEndorse = '123123'  # 银行凭证号码
            feeConfirmDate = apply_date   #收费日期
            internalAccount = '08-400301040007336'  # 公司收费账号
            internalBankCode = '05'  # 收费机构
            feeChannel = 'CASH-10017-AR'  # 支付通道
            cashOrgId = '10017'  # 机构名称
            internalBankName = '中国农业银行绥化市大有支行'  # 所属银行
            #调用原子脚本
            rs = API0000_payment().CashApproveInfoSave(magicX, interface_ip, resultData, bankEndorse, feeConfirmDate, internalAccount, internalBankCode, feeChannel, cashOrgId, internalBankName)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            # 加入断言
            assert is_success == True 

            """3.柜面收付费审核接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款还款_柜面收付费审核接口'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_payment().finishFeeFlow(magicX, interface_ip, resultData, bankEndorse, feeConfirmDate, internalAccount, internalBankCode, feeChannel, internalBankName)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            # 加入断言
            assert is_success == True 
    
            """4.保全复核用户-登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款还款_保全复核用户-登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX,interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            # 加入断言
            assert is_success == True 
            dict['logInfo']['code'] = '1'   #记录无异常标识
            dict['public']['magicX'] = ''
            end_time2 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全收付费_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time2, end_time2)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*运行异常-用户解锁'))
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return payment, dict



    @func_set_timeout(30)#设定函数超执行时间
    def save_check_info(self, apply_date, payment, resultData, dict):
        """step3:定义轨迹信息+检查点信息:
                1.定义轨迹信息
                2.定义检查点信息
        """      
        try:  
            """1.定义检查点信息"""
            env_name = dict['public']['env_name']   #环境名称
            repayment_list = []   #定义贷款产品列表
            cursor = API0000_diy().db_conf(env_name, 'wift_iiws')            
            for i in range(0, len(resultData)):
                product_list =[]   #定义产品列表
                #产品代码
                sql = 'select * from t_product where product_name=' + "'" + str(resultData[i]['productName']) + "'"
                cursor.execute(sql)
                result = cursor.fetchall()
                productCode = result[0][1]
                #现金价值
                if resultData[i]['productPresentPrice'] == None:
                    presentPrice = 0
                else:
                    presentPrice = float(resultData[i]['productPresentPrice'])
                #贷款利率
                if resultData[i]['rate'] == None:
                    loanRate = 0
                else:
                    loanRate = float(resultData[i]['rate'])
                #贷款本金
                if resultData[i]['loanPrincipal'] == None:
                    loanPrincipal = 0
                else:
                    loanPrincipal = float(resultData[i]['loanPrincipal'])
                #资本化利息
                if resultData[i]['interestCapital'] == None:
                    interestCapital = 0
                else:
                    interestCapital = float(resultData[i]['interestCapital'])
                #未结利息
                if resultData[i]['loanInterest'] == None:
                    loanInterest = 0
                else:
                    loanInterest = float(resultData[i]['loanInterest'])
                #贷款合计
                if resultData[i]['principalInterest'] == None:
                    principalInterest = 0
                else:
                    principalInterest = float(resultData[i]['principalInterest'])
                #贷款开始日期
                startDate = resultData[i]['startDate']
                
                product = {'productCode':productCode, 'presentPrice': presentPrice, 'loanRate': loanRate, 'loanPrincipal':loanPrincipal, 'interestCapital':interestCapital, 'loanInterest':loanInterest, 'principalInterest':principalInterest}
                product_list.append(product)
                #每个产品贷款还款检查点追加到product退保产品列表中
                repayment_list.append({'startDate':startDate, 'product': product_list})
            if dict['logInfo']['code'] == '1':
                #存入dict检查点中
                calc_loan = {'loan_type':'loan_repayment', 'apply_date':apply_date, 'repayment_list':repayment_list, 'payment':payment, 'msg': ''} 
                dict['check']['calc_loan'].append(calc_loan)
                """2.定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'loan_repayment', 'trackTime':apply_date, 'trackData':{'repayment_list':repayment_list, 'payment':payment}, 'msg': ''}
                dict['track_info'].append(track_info)   #存入轨迹信息
            else:
                message = dict['logInfo']['msg']
                err = dict['logInfo']['err']
                if dict['logInfo']['msg'] == None or dict['logInfo']['msg'] == '':
                    message = str(dict['logInfo']['err'])
                #存入dict检查点中
                calc_loan = {'loan_type':'loan_repayment', 'apply_date':apply_date, 'repayment_list':'', 'payment':payment, 'msg': message} 
                dict['check']['calc_loan'].append(calc_loan)
                """2.定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'loan_repayment', 'trackTime':apply_date, 'trackData':{'repayment_list':'', 'payment':payment}, 'msg': message}
                dict['track_info'].append(track_info)   #存入轨迹信息
        except Exception, e:
            dict['logInfo']['code'] = '0'    #记录异常标识
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        finally:
            pass
        return dict




if __name__ == "__main__":
    try:
        begin_time = datetime.datetime.now()   #开始时间
        #1.初始化
        is_run = True   #是否执行python脚本 
        msg = ''   #执行python脚本前存在的错误信息
        job = 'loan_repayment'   #场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = '预生产'
            env_name = env_name.encode('utf-8')
            policyNo = '8088622045171468'
            apply_date = '2020-07-20'   #保全申请日期
            username_entry = 'xcy1'   #保全录入用户名
            username_review = 'xcy2'   #保全复核用户名
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo = ''   
                apply_date = ''   
                username_entry = ''  
                username_review = ''  
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','policyNo','apply_date','username_entry','username_review']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo = rs[2][1]   #保单号
                apply_date = rs[2][2]   #保全申请日期
                username_entry = rs[2][3]   #保全录入用户
                username_review = rs[2][4]   #保全复核用户
       #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name,'apply_date':apply_date}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = {'execNo': execNo, 'policy_info':{'policyNo':policyNo},'public': {'env_name':env_name, 'username_entry':username_entry, 'username_review':username_review, 'interface_ip':interface_ip, 'magicX':''}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'','job':job}, 'track_info': [], 'check':{'calc_loan':[]}, 'track_change':[]}
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
            dict = sys_API0002().Modify_servertime(apply_date, job, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            dict = sys_API0008().loan_repayment(apply_date, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_review'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_review'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:
                if dict['logInfo']['code'] == '1':
                    print '是否贷款还款成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + policyNo).decode('utf-8').encode('gb2312')
                    print ('保全申请日期：' + apply_date).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print ('是否贷款还款成功：不成功').decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + policyNo).decode('utf-8').encode('gb2312')
                    print ('保全申请日期：' + apply_date).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                    print '不成功原因:'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "是否贷款还款成功：成功,,环境：%s,,保单号：%s,,保全申请日期：%s,,耗时：%s" % (env_name, policyNo, apply_date, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "是否贷款还款成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,保全申请日期：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, policyNo, apply_date, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())








