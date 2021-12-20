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


"""获取精算数据（保全查询，单条获取）:
    step1：通过保全申请号，系统获取精算数据
        1.登录系统
        2.通过保全申请号，进行保全查询
        3.综合查询
        4.登出系统
    step2：创建html文件，以表格形式展示
"""
class sys_API0037:

    def __init__(self):
        pass



    @func_set_timeout(60)#设定函数超执行时间
    def get_actuarial_data(self, dict):
        """获取精算数据（单条获取）:
            step1：通过保全申请号，系统获取精算数据
                1.登录系统
                2.通过保全申请号，进行保全查询
                3.综合查询
                4.登出系统
            step2：创建html文件，以表格形式展示
        """
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''

            #step1:通过保全申请号，系统获取精算数据
            dict = self.query_data(dict) 
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #step2:创建html文件，以表格形式展示
            dict = self.create_html(dict)  
            assert dict['logInfo']['code'] == '1'   #断言是否异常
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                dict['public']['magicX'] = ''
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                dict['public']['magicX'] = ''
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
        finally:
            pass
        return dict



    @func_set_timeout(60)#设定函数超执行时间
    def query_data(self, dict):
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''

            is_success = ''
            message = ''
            unit = ''
            policyNo = ''   #保单号
            productName = ''   #险种名
            applicationDate = ''   #投保日期
            effectiveDate = ''   #生效日
            policyDeliveryDate = ''   #回执日
            chargeMode = ''   #交费方式
            birthday = ''   #被保人生日
            gender = ''   #性别
            sumAssured = ''   #保额
            totalPremAf = ''   #保费
            applyTime = '**********'   #保全申请日期(YYYY-MM-DD hh-mm-ss)
            applyDay = ''   #保全申请日期(YYYY-MM-DD)
            presentPrice = ''   #申请日现金价值
            loanRate = ''   #贷款利率
            loanAccountLimit = ''   #最大可贷款额度
            loanApplyAmount = ''   #申请贷款金额
            list = []   #险种列表

            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username_entry = dict['public']['username_entry']    #登录用户
            applyNo = dict['public']['applyNo']

            """step1:登录系统"""
            #节点初始化
            is_success = ''   #是否成功标识
            unit = '登录系统'  # 节点标识
            message = ''   #信息标识
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username_entry, interface_ip)
            #获取所需响应值
            is_success = rs[0]   #是否成功标识
            message = rs[1]   #信息
            magicX = rs[2]   #会话id
            dict['public']['magicX'] = magicX
            # 加入断言
            assert is_success == True
            

            """step2:保全查询"""
            #节点1-保全查询接口
            #初始化
            is_success = ''
            unit = '保全查询接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_pa().queryCsInfoList1(magicX, interface_ip, applyNo)
            #获取所需响应值
            isSuccess = response['isSuccess']
            resultData = response['resultData']
            if isSuccess == True and len(resultData) != 0:
                is_success = True
                message = response['message']
                policyNo = response['resultData'][0]['policyNo']   #保单号
                changeId = response['resultData'][0]['changeId']   #changeId
                partitionIndi = str(response['resultData'][0]['partitionIndi'])   #partitionIndi
                applyTime = response['resultData'][0]['applyTime']   #applyTime
                serviceCode = response['resultData'][0]['serviceCode']   #serviceCode
            else:
                is_success = False
                message = '保全查询未查到结果，请检查查询条件是否有误！'
                policyNo = ''
                changeId = ''
                partitionIndi = ''
                applyTime = ''
                serviceCode = ''
            #存入dict
            dict['public']['policyNo'] = policyNo
            dict['public']['changeId'] = changeId
            dict['public']['partitionIndi'] = partitionIndi
            dict['public']['applyTime'] = applyTime
            dict['public']['serviceCode'] = serviceCode
            # 加入断言
            assert is_success == True


            #节点2：保全查询-具体保全项目查询
            dict = self.query_pa_detail(dict)
            if dict['logInfo']['code'] == '0':
                message = dict['logInfo']['msg'][19:]
                unit = dict['logInfo']['msg'][0:18]
            # 加入断言
            assert dict['logInfo']['code'] == '1'


            """step3:综合查询"""
            #节点1：综合查询-查询按钮接口
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            is_success = ''   #是否成功标识
            unit = '综合查询-查询按钮接口'  # 节点标识
            message = ''   #信息标识
            #调用原子脚本
            response = API0000_queryPolicy().queryPolicy(magicX, interface_ip, policyNo)
            isSuccess = response['isSuccess']   #是否成功标识
            resultData = response['resultData']
            #获取所需响应值
            if isSuccess == True and len(resultData) != 0:
                is_success = True
                message = ''
            else:
                is_success = False
                message = '综合查询未查到结果!'
            if is_success == True:
                proposalNo = response['resultData'][0]['proposalNo']
                proposalId = response['resultData'][0]['proposalId']
                policyId = response['resultData'][0]['policyId']
            else:
                proposalNo = ''
                proposalId = ''
                policyId = ''
            #存入dict
            dict['public']['proposalNo'] = proposalNo
            dict['public']['proposalId'] = proposalId
            dict['public']['policyId'] = policyId
            # 加入断言
            assert is_success == True

            #节点2：综合查询-保单信息-日期信息接口
            #初始化
            is_success = ''
            unit = '综合查询-保单信息-日期信息接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_queryPolicy().policyDetail(magicX, interface_ip, policyNo, proposalNo, proposalId, policyId)
            is_success = response['success']
            #获取所需响应值
            if is_success:
                message = response['message']
                applicationDate = response['others']['applicationDate'].replace('-','/')   #投保日期
                effectiveDate = response['others']['effectiveDate'].replace('-','/')   #生效日
                policyDeliveryDate = response['others']['policyDeliveryDate'].replace('-','/')   #回执日
            else:
                message = response['success']
                applicationDate = ''
                effectiveDate = ''
                policyDeliveryDate = ''
            #存入dict
            dict['public']['applicationDate'] = applicationDate
            dict['public']['effectiveDate'] = effectiveDate
            dict['public']['policyDeliveryDate'] = policyDeliveryDate
            # 加入断言
            assert is_success == True


            #节点3：综合查询-客户信息sheet页_被保人信息接口
            #初始化
            is_success = ''
            unit = '综合查询-客户信息sheet页_被保人信息接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_queryPolicy().customerByRole3(magicX, interface_ip, policyNo, policyId, proposalId, proposalNo)
            #获取所需响应值
            is_success = response['isSuccess']
            if is_success:
                message = ''
                birthday = response['resultData'][0]['birthday'].replace('-','/')   #出生日期
                gender = response['resultData'][0]['gender']   #性别
                if gender == '0':
                    gender = '男'
                elif gender == '1':
                    gender = '女'
            else:
                message = response['message']
                birthday = ''
                gender = ''
            #存入dict
            dict['public']['birthday'] = birthday
            dict['public']['gender'] = gender
            dict['public']['applyDay'] = applyTime[0:10].replace('-','/')
            # 加入断言
            assert is_success == True


            """step4：登出系统"""
            #节点初始化
            is_success = ''
            unit = '登出系统'  # 节点
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
            dict['public']['magicX'] = ''
            dict['logInfo']['code'] = '1'   #记录无异常标识
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username_entry)
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                dict['public']['magicX'] = ''
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



    #保全查询-具体保全项目查询
    @func_set_timeout(60)#设定函数超执行时间
    def query_pa_detail(self, dict):
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            list = []
            is_success = ''
            message = ''
            unit = ''
            presentPrice = ''   #申请日现金价值
            loanRate = ''   #贷款利率
            loanAccountLimit = ''   #最大可贷款额度
            loanApplyAmount = ''   #申请贷款金额
            loanAccountAmount = ''   #欠款余额
            surrenderAmount = '应付金额'   #应付金额
            #获取dict数据
            env_name = dict['public']['env_name']
            magicX = dict['public']['magicX']
            interface_ip = dict['public']['interface_ip']
            policyNo = dict['public']['policyNo']
            changeId = dict['public']['changeId']
            partitionIndi = dict['public']['partitionIndi']
            applyTime = dict['public']['applyTime']
            serviceCode = dict['public']['serviceCode']
            applyNo = dict['public']['applyNo']

            #连接数据库
            unit = '连接数据库'
            cursor = API0000_diy().db_conf(env_name, 'wift_pa') 

            #贷款
            if serviceCode == '60400':
                #初始化
                is_success = ''
                unit = '保全查询-保单贷款-保单险种信息列表接口'  # 节点
                message = ''
                validateDate = applyTime[0:10]
                #调用原子脚本
                response = API0000_pa().queryCsPolicyProductBeforeChange3(magicX, interface_ip, policyNo, changeId, partitionIndi, validateDate, serviceCode)
                #获取所需响应值
                is_success = response['isSuccess']
                if is_success:
                    message = ''
                    resultData = response['resultData']
                else:
                    message = response['message']
                    resultData = ''

                for i in range(0, len(resultData)):
                    list.append({})
                    productName = resultData[i]['productName']   #险种名称
                    chargeMode = resultData[i]['chargeMode']   #交费方式
                    sumAssured = resultData[i]['sumAssured']   #保额
                    units = resultData[i]['units']   #份数
                    totalPremAf = resultData[i]['totalPremAf']   #保费
                    presentPrice = resultData[i]['presentPrice']   #申请日现金价值
                    loanRate = resultData[i]['loanRate']   #贷款利率
                    loanAccountLimit = resultData[i]['loanAccountLimit']   #最大可贷款额度
                    loanApplyAmount = resultData[i]['loanApplyAmount']   #申请贷款金额
                    if chargeMode == 'S':
                        chargeMode = '趸交' 
                    elif chargeMode == 'Y':
                        chargeMode = '年交'  
                    elif chargeMode == 'M':
                        chargeMode = '月交' 
                    if units != None:
                        sumAssured = str(sumAssured) + r'(' + str(int(units)) + r'份)'
                    list[-1]['productName'] = productName
                    list[-1]['chargeMode'] = chargeMode
                    list[-1]['sumAssured'] = str(sumAssured)
                    list[-1]['totalPremAf'] = str(totalPremAf)
                    list[-1]['presentPrice'] = presentPrice
                    list[-1]['loanRate'] = loanRate
                    list[-1]['loanAccountLimit'] = loanAccountLimit
                    list[-1]['loanApplyAmount'] = loanApplyAmount
            #公司解约
            elif serviceCode == '30400':
                #初始化
                is_success = ''
                unit = '保全查询-公司解约-查询解约信息接口'  # 节点
                message = ''
                #调用原子脚本
                response = API0000_pa().queryCancelContract(magicX, interface_ip, changeId, partitionIndi)
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                    cancelContractType = response['others']['cancelType']
                else:
                    message = response['message']
                    cancelContractType = ''

                #初始化
                is_success = ''
                unit = '保全查询-公司解约-保单险种信息列表接口'  # 节点
                message = ''
                validateDate = applyTime[0:10]
                #调用原子脚本
                response = API0000_pa().queryCsPolicyProductBeforeChange4(magicX, interface_ip, policyNo, changeId, partitionIndi, cancelContractType)
                #获取所需响应值
                is_success = response['isSuccess']
                if is_success:
                    message = ''
                    resultData = response['resultData']
                else:
                    message = response['message']
                    resultData = ''

                for i in range(0, len(resultData)):
                    list.append({})
                    productName = resultData[i]['productName']   #险种名称
                    chargeMode = resultData[i]['chargeMode']   #交费方式
                    sumAssured = resultData[i]['sumAssured']   #保额
                    units = resultData[i]['units']   #份数
                    totalPremAf = resultData[i]['totalPremAf']   #保费
                    presentPrice = resultData[i]['presentPrice']   #申请日现金价值
                    loanAccountAmount = resultData[i]['loanAccountAmount']   #欠款余额
                    surrenderAmount = resultData[i]['surrenderAmount']   #应付金额
                    if chargeMode == 'S':
                        chargeMode = '趸交' 
                    elif chargeMode == 'Y':
                        chargeMode = '年交'  
                    elif chargeMode == 'M':
                        chargeMode = '月交' 
                    if units != None:
                        sumAssured = str(sumAssured) + r'(' + str(int(units)) + r'份)'
                    list[-1]['productName'] = productName
                    list[-1]['chargeMode'] = chargeMode
                    list[-1]['sumAssured'] = str(sumAssured)
                    list[-1]['totalPremAf'] = str(totalPremAf)
                    list[-1]['presentPrice'] = presentPrice
                    list[-1]['loanAccountAmount'] = loanAccountAmount
                    list[-1]['surrenderAmount'] = surrenderAmount
            #协议退保
            elif serviceCode == '30303':
                #初始化
                is_success = ''
                unit = '保全查询-协议退保-保单险种信息列表接口'  # 节点
                message = ''
                validateDate = applyTime[0:10]
                #调用原子脚本
                response = API0000_pa().queryCsPolicyProductBeforeChange5(magicX, interface_ip, policyNo, changeId, partitionIndi, validateDate)
                #获取所需响应值
                is_success = response['isSuccess']
                if is_success:
                    message = ''
                    resultData = response['resultData']
                else:
                    message = response['message']
                    resultData = ''

                for i in range(0, len(resultData)):
                    list.append({})
                    productName = resultData[i]['productName']   #险种名称
                    chargeMode = resultData[i]['chargeMode']   #交费方式
                    sumAssured = resultData[i]['sumAssured']   #保额
                    units = resultData[i]['units']   #份数
                    totalPremAf = resultData[i]['totalPremAf']   #保费
                    presentPrice = resultData[i]['presentPrice']   #申请日现金价值
                    loanAccountAmount = resultData[i]['loanAccountAmount']   #欠款余额
                    surrenderAmount = resultData[i]['surrenderAmount']   #应付金额
                    if chargeMode == 'S':
                        chargeMode = '趸交' 
                    elif chargeMode == 'Y':
                        chargeMode = '年交'  
                    elif chargeMode == 'M':
                        chargeMode = '月交' 
                    if units != None:
                        sumAssured = str(sumAssured) + r'(' + str(int(units)) + r'份)'
                    list[-1]['productName'] = productName
                    list[-1]['chargeMode'] = chargeMode
                    list[-1]['sumAssured'] = str(sumAssured)
                    list[-1]['totalPremAf'] = str(totalPremAf)
                    list[-1]['presentPrice'] = presentPrice
                    list[-1]['loanAccountAmount'] = loanAccountAmount
                    list[-1]['surrenderAmount'] = surrenderAmount
            #退保/取消险种
            elif serviceCode in ('30300', '30302'):
                #初始化
                is_success = ''
                unit = '保全查询-退保-保单险种信息列表接口'  # 节点
                message = ''
                validateDate = applyTime[0:10]
                #调用原子脚本
                response = API0000_pa().queryCsPolicyProductBeforeChange6(magicX, interface_ip, policyNo, changeId, partitionIndi, validateDate)
                #获取所需响应值
                is_success = response['isSuccess']
                if is_success:
                    message = ''
                    resultData = response['resultData']
                else:
                    message = response['message']
                    resultData = ''

                for i in range(0, len(resultData)):
                    list.append({})
                    productName = resultData[i]['productName']   #险种名称
                    chargeMode = resultData[i]['chargeMode']   #交费方式
                    sumAssured = resultData[i]['sumAssured']   #保额
                    units = resultData[i]['units']   #份数
                    totalPremAf = resultData[i]['totalPremAf']   #保费
                    presentPrice = resultData[i]['presentPrice']   #申请日现金价值
                    loanAccountAmount = resultData[i]['loanAccountAmount']   #欠款余额
                    surrenderAmount = resultData[i]['surrenderAmount']   #应付金额
                    if chargeMode == 'S':
                        chargeMode = '趸交' 
                    elif chargeMode == 'Y':
                        chargeMode = '年交'  
                    elif chargeMode == 'M':
                        chargeMode = '月交' 
                    if units != None:
                        sumAssured = str(sumAssured) + r'(' + str(int(units)) + r'份)'
                    list[-1]['productName'] = productName
                    list[-1]['chargeMode'] = chargeMode
                    list[-1]['sumAssured'] = str(sumAssured)
                    list[-1]['totalPremAf'] = str(totalPremAf)
                    list[-1]['presentPrice'] = presentPrice
                    list[-1]['loanAccountAmount'] = loanAccountAmount
                    list[-1]['surrenderAmount'] = surrenderAmount
            #贷款还款
            elif serviceCode == '60500':
                #初始化
                is_success = ''
                unit = '保全查询-贷款还款-保单险种信息列表接口'  # 节点
                message = ''
                validateDate = applyTime[0:10]
                #调用原子脚本
                response = API0000_pa().queryCsNeedRepayLoanAccount1(magicX, interface_ip, policyNo, changeId, partitionIndi, validateDate, serviceCode)
                #获取所需响应值
                is_success = response['isSuccess']
                if is_success:
                    message = ''
                    resultData = response['resultData']
                else:
                    message = response['message']
                    resultData = ''

                for i in range(0, len(resultData)):
                    unit = '保全查询-贷款还款-保单险种信息列表接口'
                    list.append({})
                    productName = resultData[i]['productName']   #险种名称
                    productId = str(resultData[i]['productId'])   #险种id
                    #chargeMode = resultData[i]['chargeMode']   #交费方式
                    #sumAssured = resultData[i]['sumAssured']   #保额
                    #units = resultData[i]['units']   #份数
                    #totalPremAf = resultData[i]['totalPremAf']   #保费
                    presentPrice = resultData[i]['productPresentPrice']   #申请日现金价值
                    loanPrincipal = resultData[i]['loanPrincipal']   #贷款本金
                    interestCapital = resultData[i]['interestCapital']   #资本化利息
                    loanInterest = resultData[i]['loanInterest']   #未结利息
                    loanRate = resultData[i]['rate']   #贷款利率
                    principalInterest = resultData[i]['principalInterest']   #贷款合计

                    #数据库查询产品的交费方式及份数
                    sql = "select a.pay_period,a.sum_assured,a.units,a.std_prem_bf from t_pa_policy_product a, t_pa_policy b where a.policy_id=b.policy_id and b.policy_no='" + policyNo + "' and a.product_id = '" + productId + "'"
                    unit = '保全查询-贷款还款-保单险种信息列表接口_数据库查询产品缴费方式和份数'
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    unit = '保全查询-贷款还款-保单险种信息列表接口'
                    chargeMode = result[0][0]
                    sumAssured = str(result[0][1])
                    units = result[0][2]
                    totalPremAf = str(result[0][3])

                    if chargeMode == 'S':
                        chargeMode = '趸交' 
                    elif chargeMode == 'Y':
                        chargeMode = '年交'  
                    elif chargeMode == 'M':
                        chargeMode = '月交' 
                    if units != None:
                        sumAssured = str(sumAssured) + r'(' + str(int(units)) + r'份)'
                    list[-1]['productName'] = productName
                    list[-1]['chargeMode'] = chargeMode
                    list[-1]['sumAssured'] = str(sumAssured)
                    list[-1]['totalPremAf'] = str(totalPremAf)
                    list[-1]['presentPrice'] = presentPrice
                    list[-1]['loanPrincipal'] = loanPrincipal
                    list[-1]['interestCapital'] = interestCapital
                    list[-1]['loanInterest'] = loanInterest
                    list[-1]['loanRate'] = loanRate
                    list[-1]['principalInterest'] = principalInterest
            #复效
            elif serviceCode == '30202':
                #初始化
                is_success = ''
                unit = '保全查询-复效-保单险种信息列表接口'  # 节点
                message = ''
                validateDate = applyTime[0:10]
                #调用原子脚本
                response = API0000_pa().queryCsPolicyProduct2(magicX, interface_ip, policyNo, changeId, partitionIndi, validateDate)
                #获取所需响应值
                is_success = response['isSuccess']
                if is_success:
                    message = ''
                    resultData = response['resultData']
                else:
                    message = response['message']
                    resultData = ''

                for i in range(0, len(resultData)):
                    list.append({})
                    productName = resultData[i]['productName']   #险种名称
                    chargeMode = resultData[i]['chargePeriodType']   #交费方式
                    sumAssured = resultData[i]['sumAssured']   #保额
                    units = resultData[i]['units']   #份数
                    totalPremAf = resultData[i]['totalPremAf']   #保费
                    loanBalance = resultData[i]['loanBalance']   #贷款本金
                    loanInterest = resultData[i]['loanInterest']   #贷款利息
                    if chargeMode == 'S':
                        chargeMode = '趸交' 
                    elif chargeMode == 'Y':
                        chargeMode = '年交'  
                    elif chargeMode == 'M':
                        chargeMode = '月交' 
                    if units != None:
                        sumAssured = str(sumAssured) + r'(' + str(int(units)) + r'份)'
                    list[-1]['productName'] = productName
                    list[-1]['chargeMode'] = chargeMode
                    list[-1]['sumAssured'] = str(sumAssured)
                    list[-1]['totalPremAf'] = str(totalPremAf)
                    list[-1]['loanBalance'] = loanBalance
                    list[-1]['loanInterest'] = loanInterest
            #满期领取
            elif serviceCode == '30305':
                #初始化
                is_success = ''
                unit = '保全查询-满期领取-满期险种列表查询接口'  # 节点
                message = ''
                validateDate = applyTime[0:10]
                sum_expiryPayAmount = 0
                #调用原子脚本
                response = API0000_pa().queryExpiryProductList(magicX, interface_ip, policyNo, changeId, partitionIndi, validateDate)
                #获取所需响应值
                is_success = response['isSuccess']
                if is_success:
                    message = ''
                    resultData = response['resultData']
                else:
                    message = response['message']
                    resultData = ''

                for i in range(0, len(resultData)):
                    list.append({})
                    productName = resultData[i]['productName']   #险种名称
                    productId = str(resultData[i]['productId'])   #险种id
                    #chargeMode = resultData[i]['chargePeriodType']   #交费方式
                    sumAssured = resultData[i]['sumAssured']   #保额
                    units = resultData[i]['units']   #份数
                    totalPremAf = resultData[i]['totalPremAf']   #保费
                    expiryAmount = resultData[i]['expiryAmount']   #满期给付金额
                    loanAccountAmount = resultData[i]['loanAccountAmount']   #欠款余额
                    cbSbAccount = resultData[i]['cbSbAccount']   #年金累计生息账号余额
                    bonusAccount = resultData[i]['bonusAccount']   #红利累计生息账户
                    expiryPayAmount = resultData[i]['expiryPayAmount']   #满期应付金额
                    sum_expiryPayAmount = sum_expiryPayAmount + expiryPayAmount
                    #数据库查询产品的交费方式及份数
                    sql = "select a.pay_period,a.sum_assured,a.units,a.std_prem_bf from t_pa_policy_product a, t_pa_policy b where a.policy_id=b.policy_id and b.policy_no='" + policyNo + "' and a.product_id = '" + productId + "'"
                    unit = '保全查询-满期领取-数据库查询产品缴费方式'
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    unit = '保全查询-满期领取-满期险种列表查询接口'
                    chargeMode = result[0][0]

                    if chargeMode == 'S':
                        chargeMode = '趸交' 
                    elif chargeMode == 'Y':
                        chargeMode = '年交'  
                    elif chargeMode == 'M':
                        chargeMode = '月交' 
                    if units != None:
                        sumAssured = str(sumAssured) + r'(' + str(int(units)) + r'份)'
                    list[-1]['productName'] = productName
                    list[-1]['chargeMode'] = chargeMode
                    list[-1]['sumAssured'] = str(sumAssured)
                    list[-1]['totalPremAf'] = str(totalPremAf)
                    list[-1]['expiryAmount'] = str(expiryAmount)
                    list[-1]['loanAccountAmount'] = str(loanAccountAmount)
                    list[-1]['cbSbAccount'] = str(cbSbAccount)
                    list[-1]['bonusAccount'] = str(bonusAccount)
                    list[-1]['expiryPayAmount'] = str(expiryPayAmount)
                    list[-1]['sum_expiryPayAmount'] = str(sum_expiryPayAmount)
            else:
                list = []
                unit = '保全查询接口'
                is_success = False
                message = '经保全查询，非贷款/还款/退保/公司解约/协议退保/取消险种/复效/满期领取保全项目！'
            dict['logInfo']['code'] == '0'
            #print list
            #存入dict
            dict['public']['list'] = list
            # 加入断言
            assert is_success == True
            dict['logInfo']['code'] == '1'
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username_entry)
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



    #生成html文件
    @func_set_timeout(60)#设定函数超执行时间
    def create_html(self, dict):
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            is_success = ''
            message = ''
            unit = '生成html文件'
            html_file_path = dict['public']['html_file_path']
            list = dict['public']['list']
            applicationDate = dict['public']['applicationDate']
            effectiveDate = dict['public']['effectiveDate']
            policyDeliveryDate = dict['public']['policyDeliveryDate']
            birthday = dict['public']['birthday']
            gender = dict['public']['gender']
            applyDay = dict['public']['applyDay']
            serviceCode = dict['public']['serviceCode']
            policyNo = dict['public']['policyNo']
            #1.创建.html文件
            file = open(html_file_path, 'w')
            rowspan = str(len(list))

            #贷款-第一行+第二行
            if serviceCode == '60400':
                message1 = """<html>
    <head>
        <meta charset='utf-8'>
        <title>精算数据</title>
    </head>
    <body>
        <table table border='1' bordercolor='black' cellspacing='0' cellpadding='5'>
            <tr width='4000'>
                <td>保单号</td>
                <td>险种名称</td>
                <td>投保日期</td>
                <td>生效日</td>
                <td>回执日</td>
                <td>交费方式</td>
                <td>被保人生日</td>
                <td>性别</td>
                <td>保额</td>
                <td>保费</td>
                <td>贷款申请日</td>
                <td>申请日现金价值</td>
                <td>贷款利率</td>
                <td>最大可贷款额度</td>
                <td>申请贷款金额</td>
            </tr>
            <tr>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>""" %(rowspan,policyNo,list[0]['productName'],rowspan,applicationDate,rowspan,effectiveDate,rowspan,policyDeliveryDate,list[0]['chargeMode'],rowspan,birthday,rowspan,gender,list[0]['sumAssured'],list[0]['totalPremAf'],rowspan,applyDay,list[0]['presentPrice'],list[0]['loanRate'],list[0]['loanAccountLimit'],list[0]['loanApplyAmount'])
            #公司解约/协议退保
            elif serviceCode in ('30303','30400', '30300', '30302'):
                if serviceCode == '30303':
                    serviceName = '协议退保'
                elif serviceCode == '30400':
                    serviceName = '公司解约'
                elif serviceCode == '30300':
                    serviceName = '退保'
                elif serviceCode == '30302':
                    serviceName = '取消险种'
                message1 = """<html>
    <head>
        <meta charset='utf-8'>
        <title>精算数据</title>
    </head>
    <body>
        <table table border='2' bordercolor='black' cellspacing='0' cellpadding='5'>
            <tr width='4000'>
                <td>保单号</td>
                <td>险种名称</td>
                <td>投保日期</td>
                <td>生效日</td>
                <td>回执日</td>
                <td>交费方式</td>
                <td>被保人生日</td>
                <td>性别</td>
                <td>保额</td>
                <td>保费</td>
                <td>%s申请日</td>
                <td>申请日现金价值</td>
                <td>欠款余额</td>
                <td>应付金额</td>
            </tr>
            <tr>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>""" %(serviceName,rowspan,policyNo,list[0]['productName'],rowspan,applicationDate,rowspan,effectiveDate,rowspan,policyDeliveryDate,list[0]['chargeMode'],rowspan,birthday,rowspan,gender,list[0]['sumAssured'],list[0]['totalPremAf'],rowspan,applyDay,list[0]['presentPrice'],list[0]['loanAccountAmount'],list[0]['surrenderAmount'])
            #贷款还款
            elif serviceCode == '60500':
                message1 = """<html>
    <head>
        <meta charset='utf-8'>
        <title>精算数据</title>
    </head>
    <body>
        <table table border='2' bordercolor='black' cellspacing='0' cellpadding='5'>
            <tr width='4000'>
                <td>保单号</td>
                <td>险种名称</td>
                <td>投保日期</td>
                <td>生效日</td>
                <td>回执日</td>
                <td>交费方式</td>
                <td>被保人生日</td>
                <td>性别</td>
                <td>保额</td>
                <td>保费</td>
                <td>贷款还款申请日</td>
                <td>申请日现金价值</td>
                <td>贷款本金</td>
                <td>资本化利息</td>
                <td>未结利息</td>
                <td>贷款利率</td>
                <td>贷款合计</td>
            </tr>
            <tr>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>""" %(rowspan,policyNo,list[0]['productName'],rowspan,applicationDate,rowspan,effectiveDate,rowspan,policyDeliveryDate,list[0]['chargeMode'],rowspan,birthday,rowspan,gender,list[0]['sumAssured'],list[0]['totalPremAf'],rowspan,applyDay,list[0]['presentPrice'],list[0]['loanPrincipal'],list[0]['interestCapital'],list[0]['loanInterest'],list[0]['loanRate'],list[0]['principalInterest'])
            #复效
            elif serviceCode == '30202':
                message1 = """<html>
    <head>
        <meta charset='utf-8'>
        <title>精算数据</title>
    </head>
    <body>
        <table table border='2' bordercolor='black' cellspacing='0' cellpadding='5'>
            <tr width='4000'>
                <td>保单号</td>
                <td>险种名称</td>
                <td>投保日期</td>
                <td>生效日</td>
                <td>回执日</td>
                <td>交费方式</td>
                <td>被保人生日</td>
                <td>性别</td>
                <td>保额</td>
                <td>保费</td>
                <td>复效申请日</td>
                <td>贷款本金</td>
                <td>贷款利息</td>
            </tr>
            <tr>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>""" %(rowspan,policyNo,list[0]['productName'],rowspan,applicationDate,rowspan,effectiveDate,rowspan,policyDeliveryDate,list[0]['chargeMode'],rowspan,birthday,rowspan,gender,list[0]['sumAssured'],list[0]['totalPremAf'],rowspan,applyDay,list[0]['loanBalance'],list[0]['loanInterest'])
            #满期领取
            elif serviceCode == '30305':
                message1 = """<html>
    <head>
        <meta charset='utf-8'>
        <title>精算数据</title>
    </head>
    <body>
        <table table border='2' bordercolor='black' cellspacing='0' cellpadding='5'>
            <tr width='4000'>
                <td>保单号</td>
                <td>险种名称</td>
                <td>投保日期</td>
                <td>生效日</td>
                <td>回执日</td>
                <td>交费方式</td>
                <td>被保人生日</td>
                <td>性别</td>
                <td>保额</td>
                <td>保费</td>
                <td>满期给付金额</td>
                <td>欠款余额</td>
                <td>年金累计生息账号余额</td>
                <td>红利累计生息账户</td>
                <td>满期应付金额</td>
                <td>满期应付总金额</td>
            </tr>
            <tr>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
            </tr>""" %(rowspan,policyNo,list[0]['productName'],rowspan,applicationDate,rowspan,effectiveDate,rowspan,policyDeliveryDate,list[0]['chargeMode'],rowspan,birthday,rowspan,gender,list[0]['sumAssured'],list[0]['totalPremAf'],list[0]['expiryAmount'],list[0]['loanAccountAmount'],list[0]['cbSbAccount'],list[0]['bonusAccount'],list[0]['expiryPayAmount'],rowspan,list[0]['sum_expiryPayAmount'])
            
            #写入
            file.write(message1)

            #第三行及更多行
            #贷款
            if serviceCode == '60400':
                for j in range(1, len(list)):
                    message2 = """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """%(list[j]['productName'],list[j]['chargeMode'],list[j]['sumAssured'],list[j]['totalPremAf'],list[j]['presentPrice'],list[j]['loanRate'],list[j]['loanAccountLimit'],list[j]['loanApplyAmount'])
                    file.write(message2)
            #协议退保、公司解约、退保、取消险种
            elif serviceCode in ('30303','30400', '30300', '30302'):
                for j in range(1, len(list)):
                    message2 = """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """%(list[j]['productName'],list[j]['chargeMode'],list[j]['sumAssured'],list[j]['totalPremAf'],list[j]['presentPrice'],list[j]['loanAccountAmount'],list[j]['surrenderAmount'])
                    file.write(message2)
            #贷款还款
            elif serviceCode == '60500':
                for j in range(1, len(list)):
                    message2 = """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """%(list[j]['productName'],list[j]['chargeMode'],list[j]['sumAssured'],list[j]['totalPremAf'],list[j]['presentPrice'],list[0]['loanPrincipal'],list[0]['interestCapital'],list[0]['loanInterest'],list[0]['loanRate'],list[0]['principalInterest'])
                    file.write(message2)
            #复效
            elif serviceCode == '30202':
                for j in range(1, len(list)):
                    message2 = """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """%(list[j]['productName'],list[j]['chargeMode'],str(list[j]['sumAssured']),str(list[j]['totalPremAf']),list[j]['loanBalance'],list[0]['loanInterest'])
                    file.write(message2)
            #满期领取
            elif serviceCode == '30305':
                for j in range(1, len(list)):
                    message2 = """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """%(list[j]['productName'],list[j]['chargeMode'],str(list[j]['sumAssured']),str(list[j]['totalPremAf']),list[j]['expiryAmount'],list[0]['loanAccountAmount'],list[0]['cbSbAccount'],list[0]['bonusAccount'],list[0]['expiryPayAmount'])
                    file.write(message2)
            file.write('\n' + '        </table> ' + "\n")
            file.write('    </body> ' + "\n")
            file.write('</html> ' + "\n")
            #关闭html文件
            file.close()
            is_success = True
            dict['logInfo']['code'] = '1'    
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
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
        job = 'get_actuarial_data_pa'   #场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = 'uat7'
            env_name = env_name.encode('utf-8')
            applyNo = 'POS2031072800002'   #保全申请号;自测：公司解约POS2021052600002；贷款POS2021050100064
            username_entry = 'xcy1'   #保全录入用户名
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                applyNo = ''   
                username_entry = ''  
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','applyNo','username_entry']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                applyNo = rs[2][1]   #保全申请号
                username_entry = rs[2][2]   #登录用户
       #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)
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
        #5.定义dict
        if is_run == True:
            msg = ''
        dict = {'execNo': execNo, 'public': {'env_name':env_name, 'html_file_path':logging_filename, 'username_entry':username_entry, 'interface_ip':interface_ip, 'applyNo':applyNo, 'magicX':''}, 'logInfo': {'code':'0', 'msg': msg, 'err':'', 'result':'', 'job':job}}
        #6.执行脚本
        if is_run == True:
            dict = sys_API0037().get_actuarial_data(dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            dict['public']['magicX'] = ''
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
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
                    print '精算数据是否获取成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保全申请号：' + applyNo).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print ('精算数据是否获取成功：不成功').decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保全申请号：' + applyNo).decode('utf-8').encode('gb2312')
                    print '不成功原因:'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "精算数据是否获取成功：成功,,环境：%s,,保全申请号：%s,,耗时：%s" % (env_name, applyNo, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "精算数据是否获取成功：不成功,,不成功原因：%s,,环境：%s,,保全申请号：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, applyNo, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())



