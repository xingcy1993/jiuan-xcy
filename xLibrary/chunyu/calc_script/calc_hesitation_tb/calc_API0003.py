#coding=utf-8

import os
import sys
import xlrd
import traceback
from xLibrary.chunyu.API0000 import *

reload(sys);
sys.setdefaultencoding("utf8")

"""手工计算犹豫期退保：
    step1:检查点存入dict_manual中，续期产品保费
    step2:手工计算检查点存入dict_manual
"""

class calc_API0003:

    def __init__(self):
        pass

    def calc_hesitation_tb(self, apply_date, dict_manual):
        try:
            #初始化
            is_success = True
            message = ''
            unit = '手工计算-犹豫期退保:'
            payment = 0   #新契约收费金额
            pa_name = 'hesitation_tb'
            #获取dict数据
            product_list = dict_manual['policy_info']['main_risk_info'] + dict_manual['policy_info']['sub_risk_info']   #组装保单产品列表
            #调用保全通用规则
            rs = API0000_diy().pa_general_rules(pa_name, apply_date, dict_manual)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            #调用退保保全项规则
                #犹豫期天数为0，不允许做犹豫期退保
            sum_product_support_loan = 0
            for i in range (0,len(product_list)):
                productCode = product_list[i]['productCode']   #产品代码
                hesitation_days = API0000_diy().query_product_hesitation_days(productCode)   #获取险种犹豫期天数
                if hesitation_days != 0:
                    sum_product_support_loan  = sum_product_support_loan + 1
            if sum_product_support_loan == 0:
                message = '犹豫期天数为0'
                is_success = False
            assert is_success == True
            """step1:获取dict_manual中，续期产品保费"""
            for i in range (0,len(product_list)):
                payment = float(product_list[i]['stdPremBf']) + float(payment)
            """存入dict"""
            #保单终止、终止原因
            dict_manual['policy_info']['policy_status'] = '03'   
            dict_manual['policy_info']['end_reason'] = '03' 
            #主险/附加险终止
            for i in range(0, len(dict_manual['policy_info']['main_risk_info'])):
                dict_manual['policy_info']['main_risk_info'][i]['liability_state'] = '03'
            for i in range(0, len(dict_manual['policy_info']['sub_risk_info'])):
                dict_manual['policy_info']['sub_risk_info'][i]['liability_state'] = '03' 
            """step2:检查点存入dict_manual中"""
            dict_manual['check']['calc_hesitation_tb']['apply_date'] = apply_date
            dict_manual['check']['calc_hesitation_tb']['payment'] = payment
            dict_manual['check']['calc_hesitation_tb']['msg'] = ''
            """3.定义轨迹信息"""
            #定义轨迹信息
            track_info = {'trackType':'hesitation_tb', 'trackTime':apply_date, 'trackData':{'payment': payment}, 'msg': ''}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息 
            assert is_success == True 
        except Exception, e:
            is_success = False
            dict_manual['logInfo']['code'] = 0
            dict_manual['logInfo']['err'] = unit + str(e)
            dict_manual['check']['calc_hesitation_tb']['apply_date'] = apply_date
            dict_manual['check']['calc_hesitation_tb']['payment'] = payment
            dict_manual['check']['calc_hesitation_tb']['msg'] = message
            track_info = {'trackType':'hesitation_tb', 'trackTime':apply_date, 'trackData':{'payment': payment}, 'msg': message}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息 
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

dict_manual = calc_API0003().calc_hesitation_tb(apply_date, dict_manual)
print dict_manual
"""


