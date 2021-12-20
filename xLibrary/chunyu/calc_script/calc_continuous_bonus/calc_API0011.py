# coding=utf-8

import os
import sys
import xlrd
import traceback
reload(sys);
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *



"""手工计算持续奖金：
    step1:遍历产品列表
    step2:持续奖金存入万能结息账户
    step3:手工计算检查点存入dict_manual
"""
class calc_API0011:

    def __init__(self):
        pass
        
    def calc_continuous_bonus(self, sendDate, dict_manual):
        try:
            #初始化
            is_success = True
            message = ''
            unit = '手工计算-持续奖金:'
            payment = 0   #收付费金额
               
            #获取dict数据
            product_list = dict_manual['policy_info']['main_risk_info'] + dict_manual['policy_info']['sub_risk_info']   #组装保单产品列表
            
            """step1:遍历产品列表，合计各产品持续奖金"""
            for i in range (0,len(product_list)):
            	productCode = product_list[i]['productCode']   #产品code
                if productCode in ('3257CA','8233','8237'):
                    stdPremBf = float(product_list[i]['stdPremBf'])   #产品保费
                    effectiveDate = dict_manual['policy_info']['effectiveDate']   #生效日期
                    #获取保单年度
                    policy_years = API0000_diy().calc_policy_years(effectiveDate , '9999-12-31', sendDate)

                    #根据保单年度计算对应的持续奖金
                    if int(policy_years) < 7:
                        payment = 0
                    elif int(policy_years) == 7:
                        sum_additional_premium_fee = 0   #初始化前六年度累计追加保费金额为0
                        for i in range(0, len(dict_manual['check']['calc_additional_premium'])):
                            additional_premium_date = dict_manual['check']['calc_additional_premium'][i]['apply_date']   #追加保费日期
                            additional_premium_fee = float(dict_manual['check']['calc_additional_premium'][i]['product'][0]['addInvestAmount'])   #申请追加保费金额
                            if additional_premium_date < API0000_diy().calc_policy_anniversary(effectiveDate, policy_years) and additional_premium_date >= effectiveDate:
                                sum_additional_premium_fee = round((payment + additional_premium_fee), 2)   #前六年度累计追加保费日期
                        if product_list[i]['productCode'] in ('8233','8237'):
                            payment = round(float((stdPremBf + sum_additional_premium_fee) * 0.01), 2)   #持续奖金
                        elif product_list[i]['productCode'] == '3257CA':
                            payment = round(sum_additional_premium_fee * 0.01, 2)   #持续奖金
                    elif int(policy_years) > 7:
                        #本公司将按前一个保单年度内投保人追加保险费的 1%计算持续奖金并转入保单账户
                        for i in range(0, len(dict_manual['check']['calc_additional_premium'])):
                            additional_premium_date = dict_manual['check']['calc_additional_premium'][i]['apply_date']   #追加保费日期
                            additional_premium_fee = float(dict_manual['check']['calc_additional_premium'][i]['product'][0]['addInvestAmount'])   #申请追加保费金额
                            if additional_premium_date < API0000_diy().calc_policy_anniversary(effectiveDate, policy_years) and additional_premium_date >= API0000_diy().calc_policy_anniversary(effectiveDate, int(policy_years)-1):
                                payment = round((payment + additional_premium_fee * 0.01), 2)   #持续奖金
                            else:
                                payment = 0
                if payment > 0:
	                #存入dict万能账户列表中
	                dict_manual['policy_info']['investAmount']['productCode'] = productCode
	                dict_manual['policy_info']['investAmount']['investAmount_list'].append({'transCode':'01', 'investAmoun_detail_list': [{'transAmount':payment, 'dealTime':sendDate}], 'interestCapital':payment})
	                dict_manual['policy_info']['investAmount']['total_interestCapital'] = round((float(dict_manual['policy_info']['investAmount']['total_interestCapital']) + payment), 2)
            """step2:持续奖金存入万能结息账户"""
            is_success = None
            unit = '节点：派发持续奖金_存入万能结息账户：'  # 节点
            message = ''
            #type = 'continuous_bonus'   #补充万能账户记录类型-持续奖金
            #dict_manual = API0000_diy().calc_supplement_investAmount(dict_manual, sendDate, payment, type)
            if payment > 0:
                """step3:手工计算检查点存入dict_manual"""
                is_success = None
                unit = '节点：派发持续奖金_定义检查点信息：'   # 节点
                message = ''
                calc_continuous_bonus = {}
                #持续奖金存入dict['check']['calc_continuous_bonus']中
                calc_continuous_bonus['apply_date'] = sendDate   
                calc_continuous_bonus['payment'] = payment  
                calc_continuous_bonus['msg'] = ''  
                dict_manual['check']['calc_continuous_bonus'].append(calc_continuous_bonus)
                """2.定义轨迹信息"""
                track_info = {'trackType':'continuous_bonus', 'trackTime':sendDate, 'trackData':{'payment':payment}, 'msg': ''}
                dict_manual['track_info'].append(track_info)   #存入轨迹信息
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
		'calc_continuous_bonus': [],
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



sendDate = '2020-12-12'   #持续奖金派发日期
dict_manual = calc_API0011().calc_continuous_bonus(sendDate, dict_manual)
print dict_manual
"""


