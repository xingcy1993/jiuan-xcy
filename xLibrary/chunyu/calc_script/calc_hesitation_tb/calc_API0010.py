#coding=utf-8

import os
import sys
import xlrd
import traceback
reload(sys);
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *



"""手工计算犹豫期退保试算：
    step1:检查点存入dict_manual中，续期产品保费
    step2:手工计算检查点存入dict_manual
"""
class calc_API0010:

    def __init__(self):
        pass

    def calc_trial_hesitation_tb(self, apply_date, dict_manual):
        try:
            #初始化
            is_success = True
            message = ''
            unit = '手工计算-犹豫期退保试算:'
            payment = 0   #新契约收费金额

            #调用保全通用规则
            pa_name = 'trial_hesitation_tb'
            rs = API0000_diy().pa_general_rules(pa_name, apply_date, dict_manual)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            #获取dict数据
            product_list = dict_manual['policy_info']['main_risk_info'] + dict_manual['policy_info']['sub_risk_info']   #组装保单产品列表

            """step1:获取dict_manual中，续期产品保费"""
            for i in range (0,len(product_list)):
                payment = float(product_list[i]['stdPremBf']) + float(payment)
                
            """step2:检查点存入dict_manual中"""
            dict_manual['check']['calc_hesitation_tb']['apply_date'] = apply_date
            dict_manual['check']['calc_hesitation_tb']['payment'] = payment 
            dict_manual['check']['calc_hesitation_tb']['msg'] = '' 
            
            """step3:定义轨迹信息"""
            #定义轨迹信息
            track_info = {'trackType':'trial_hesitation_tb', 'trackTime':apply_date, 'trackData':{'payment':payment}, 'msg': ''}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息
            assert is_success == True
            assert dict_manual['logInfo']['code'] == '1'
        except Exception, e:
            is_success = False
            dict_manual['logInfo']['code'] = 0
            dict_manual['logInfo']['err'] = unit + str(e)
            dict_manual['check']['calc_hesitation_tb']['apply_date'] = apply_date
            dict_manual['check']['calc_hesitation_tb']['payment'] = payment 
            dict_manual['check']['calc_hesitation_tb']['msg'] = message 
            track_info = {'trackType':'trial_hesitation_tb', 'trackTime':apply_date, 'trackData':{'payment':payment}, 'msg': message}
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

dict_manual = calc_API0010().calc_trial_hesitation_tb(apply_date, dict_manual)
print dict_manual
"""


