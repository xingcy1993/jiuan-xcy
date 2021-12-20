# coding=utf-8

import os
import sys
import xlrd
import traceback
from xLibrary.chunyu.API0000 import *

reload(sys);
sys.setdefaultencoding("utf8")

"""手工计算生存金：
    step1:遍历产品列表，合计各产品生存金
    step2:手工计算检查点存入dict_manual
"""

class calc_API0004:

    def __init__(self):
        pass
        
    def calc_survivalFee(self, sendDate, dict_manual):
        try:
            #初始化
            is_success = True
            message = ''
            unit = '手工计算-生存金:'
            survivalFee = 0   #生存金
            payment = 0   #收付费金额
            transAmount_cbSbAccount = 0   #定义本次累计生息账号交易金额
            #获取dict数据
            product_list = dict_manual['policy_info']['main_risk_info'] + dict_manual['policy_info']['sub_risk_info']   #组装保单产品列表
            
            """step1:遍历产品列表，合计各产品生存金"""
            for i in range (0,len(product_list)):
                policy_status = dict_manual['policy_info']['policy_status']   #保单状态
                effectiveDate = dict_manual['policy_info']['effectiveDate']   #保单生效日期
                productCode = product_list[i]['productCode']   #产品代码
                
                #3237产品：第四个保单周年日起至保险期满日之前（不含保险期满日），若被保险人生存且本合同仍然有效，本公司将于每个保单周年日按年交保险费的10%给付生存保险金
                if productCode == '3237':  
                    #1.获取保单数据
                    stdPremBf = product_list[i]['stdPremBf']   #产品保费
                    total_times_renew = int(dict_manual['public']['total_times_renew'])   #续期次数
                    chargePeriod = int(product_list[i]['chargePeriod'])   #产品缴费期间
                    coveragePeriod = 10   # 保障期间
                    #2.获取未派发的派发生存金列表
                    #(1)初始化派发生存金日期列表
                    sendDate_list = []
                    for policy_years in range(5, 11):
                        sendDate_list.append(API0000_diy().calc_policy_anniversary(effectiveDate, policy_years))
                    #(2)未派发的派发生存金列表 = 初始化派发生存金日期列表-已派发的生存金日期
                    for x in range(0, len(dict_manual['check']['calc_survivalFee'])):
                        already_sendDate = dict_manual['check']['calc_survivalFee'][x]['apply_date']
                        sendDate_list.remove(already_sendDate)
                    #3.派发生存金。如果保单有效且交费期3年已满且申请的派发生存金日期在'未派发生存金日期列表'中，可成功派发出生存金
                    if policy_status == '01' and total_times_renew == chargePeriod-1 and (sendDate in sendDate_list):
                        survivalFee = round((round(float(stdPremBf), 2) * 0.1), 2)   #3237产品生存金=保费*10%
                    else:
                        survivalFee = 0
                #1217CB产品：本合同的年金开始领取日为本合同生效满 5 周年且被保险人达到年金起领年龄后的首个保单周年日。本合同起领年龄分别为 55 周岁、60 周岁、65 周岁三档
                elif productCode == '1217CB':
                    #1.获取保单数据
                    sumAssured = product_list[i]['sumAssured']   #产品保额
                    total_times_renew = int(dict_manual['public']['total_times_renew'])   #续期次数
                    chargePeriod = int(product_list[i]['chargePeriod'])   #产品缴费期间
                    chargeMode = product_list[i]['chargeMode']   #缴费频率
                    planFreq = product_list[i]['planFreq']   #年金/生存金领取方式
                    #2.判断是否达到派发日期
                    if len(dict_manual['check']['calc_survivalFee']) > 0:
                        send_status = True
                    else:
                        if chargeMode == 'S':
                            send_status = True
                        elif chargeMode == 'Y' and (chargePeriod in [3,5]):
                            if total_times_renew == chargePeriod-1:
                                send_status = True
                            else:
                                send_status = False
                        elif chargeMode == 'Y' and (chargePeriod in [10,20]):
                            if total_times_renew >= 4:
                                send_status = True
                            else:
                                send_status = False
                    #3.获取未派发的派发生存金列表
                    #(1)初始化派发生存金日期列表
                    sendDate_list = []
                    for policy_years in range(6, 107):
                        sendDate_list.append(API0000_diy().calc_policy_anniversary(effectiveDate, policy_years))
                    #(2)未派发的派发生存金列表 = 初始化派发生存金日期列表-已派发的生存金日期
                    for x in range(0, len(dict_manual['check']['calc_survivalFee'])):
                        already_sendDate = dict_manual['check']['calc_survivalFee'][x]['apply_date']
                        sendDate_list.remove(already_sendDate)
                    #4.派发生存金。如果保单有效且交费期3年已满且申请的派发生存金日期在'未派发生存金日期列表'中，可成功派发出生存金
                    if policy_status == '01' and send_status == True and (sendDate in sendDate_list):
                        if planFreq == '05':
                            survivalFee = float(sumAssured)   #年领：生存金=保额
                        elif planFreq == '02':
                            survivalFee = round(float(sumAssured) * float(0.085), 2)   #年领：生存金=保额
                else:
                    #非3237产品
                    survivalFee = 0
                #survivalFee = API0000_diy().calc_product_survivalFee(sendDate, productCode, stdPremBf, sumAssured, units, dict)
                #计算各产品生存金合计
                payment = payment + survivalFee   
                """step2:年金使用方式"""
                payOption = product_list[i]['payOption']   #年金使用方式
                    #进累积生息账号时：
                if payOption == '03':
                    transAmount_cbSbAccount = round(float(transAmount_cbSbAccount + survivalFee), 2)   #本次累计生息账号交易金额
                else:
                    abc = 1   
            #dict中存储cbSbAccount_list累计生息账号列表
            if transAmount_cbSbAccount != 0:
                #账号利息存储cbSbAccount_list累计生息账号列表
                interest = API0000_diy().calc_interest_account(dict_manual, sendDate)
                if interest != 0:
                    dict_manual['policy_info']['cbSbAccount']['cbSbAccount_list'].append({'transAmount':interest, 'dealTime': sendDate, 'transCode':'12'})
                    dict_manual['policy_info']['cbSbAccount']['cashAmount'] = round((float(dict_manual['policy_info']['cbSbAccount']['cashAmount']) + interest), 2)
                #生存金存储cbSbAccount_list累计生息账号列表
                dict_manual['policy_info']['cbSbAccount']['cbSbAccount_list'].append({'transAmount':transAmount_cbSbAccount, 'dealTime': sendDate, 'transCode':'8'}) 
                dict_manual['policy_info']['cbSbAccount']['cashAmount'] = round((float(dict_manual['policy_info']['cbSbAccount']['cashAmount']) + transAmount_cbSbAccount), 2)
            if payment != 0:
                """step2:手工计算检查点存入dict_manual"""
                survivalFee_info = {'apply_date':sendDate, 'payment':payment, 'msg': ''}   #定义每期生存金信息
                dict_manual['check']['calc_survivalFee'].append(survivalFee_info)    
                """step3.定义轨迹信息"""
                track_info = {'trackType':'survivalFee', 'trackTime':sendDate, 'trackData':{'payment':payment}, 'msg': ''}
                dict_manual['track_info'].append(track_info)   #存入轨迹信息
            else:
                is_success = False
                message = '某期生存金不满足派发条件'
            assert is_success == True
            assert dict_manual['logInfo']['code'] == '1'
        except Exception, e:
            is_success = False
            dict_manual['logInfo']['code'] = 0
            dict_manual['logInfo']['err'] = unit + str(e)
            print '---err------'
            traceback.print_exc()
            print dict_manual
            exit()
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict_manual = API0000_diy().result(dict_manual, is_success, message, unit)        
        return dict_manual


"""
#模拟dict_manual
dict_manual = {
	'policy_info': {
		'policyNo': '',
		'proposalNo': '',
		'policyChannel': '',
		'policyType': '',
		'organId': '',
		'applicationDate': '2020-11-12',
		'effectiveDate': '2020-11-13',
		'callBackDate': '2020-11-12',
		'end_reason': '',
		'invalid_reason': '',
		'policy_status': '01',
		'holder_info': {
			'familyIncome': '',
			'districtCode': '',
			'driverLicenseType': '',
			'mobilePhone': '',
			'weight': '',
			'annualIncome': '',
			'medicalInsType': '',
			'Industry': '',
			'taxPayerType': '',
			'nationnality1': '',
			'height': '',
			'certiCode': '',
			'educationId': '',
			'pbCertiValidEndDate': '',
			'residentType': '',
			'incomeSource': '',
			'homeTel': '',
			'Email': '',
			'jobClass': '',
			'cityCode': '',
			'name': '',
			'incomeSourceNote': '',
			'workCompany': '',
			'premBudget': '',
			'gender': '',
			'certiType': '',
			'addrDetail': '',
			'isMarried': '',
			'officeTel': '',
			'pbHoldBirth': '',
			'provinceCode': '',
			'jobCode': '',
			'postalCode': '',
			'Nationality': '',
			'sameASInsurd': ''
		},
		'insured_info': [{
			'insuBirth': '1990-01-20'
		}],
		'benf_info': [{}],
		'agent_info': {
			'agent_name': '',
			'channelId': '',
			'partnerId': '',
			'agent_birthday': '',
			'salesChannelText': '',
			'agent_gender': '',
			'headPartner': ''
		},
		'main_risk_info': [{
			'sumAssured': '100000',
			'coveragePeriod': '999',
			'stdPremBf': '100000',
			'chargePeriodType': 'S',
			'payOption': None,
			'planFreq': None,
			'chargePeriod': '1',
			'bonusYearOrAge': '0',
			'units': None,
			'coverPeriodType': 'W',
			'productId': '10038',
			'chargeMode': 'S'
		}],
		'sub_risk_info': [{
			'sumAssured': '100000',
			'coveragePeriod': '999',
			'stdPremBf': '100000',
			'chargePeriodType': 'S',
			'payOption': None,
			'planFreq': None,
			'chargePeriod': '1',
			'bonusYearOrAge': '0',
			'units': None,
			'coverPeriodType': 'W',
			'productId': '10038',
			'chargeMode': 'S'
		}],
		'payment_nb': {
			'payMode': '',
			'payment': ''
		}
	},
	'public': {
		'username_review': '',
		'env_name': '',
		'apply_date': '',
		'interface_ip': '',
		'execNo': '',
		'username_entry': ''
	},
	'logInfo': {
		'msg': '',
		'code': '',
		'result': '',
		'Err': ''
	},
	'track_info': [],
	'check': {
		'calc_renew': [],
		'calc_survivalFee': [],
		'calc_nb': {
			'product': [],
			'payment': ''
		},
		'calc_hesitation_tb': {
			'payment': ''
		},
        'calc_tb':[],
        'calc_loan':[]
	}
}



sendDate = '2020-12-12'   #生存金派发日期
dict_manual = calc_API0004().calc_survivalFee(sendDate, dict_manual)
print dict_manual
"""


