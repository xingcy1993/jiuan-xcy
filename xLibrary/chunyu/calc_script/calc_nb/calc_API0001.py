#coding=utf-8
import os
import sys
import xlrd
import traceback
from xLibrary.chunyu.API0000 import *

reload(sys);
sys.setdefaultencoding("utf8")


"""手工计算新契约：
        step1:手工计算投保年龄
        step2:获取产品费率
        step3:手工计算费率公式
        step4:指定产品保额、保费
        step5:手工计算检查点存入dict_manual
"""
class calc_API0001:

    def __init__(self):
        pass
        
    def calc_nb(self, dict_manual):
        try:
            #初始化
            is_success = True
            message = ''
            unit = '手工计算-新契约:'
            premium = 0   #保费
            amount = 0   #保额
            payment = 0   #新契约收费金额
            result = 0   #公式手工计算结果
            #获取dict数据
            product_list = dict_manual['policy_info']['main_risk_info'] + dict_manual['policy_info']['sub_risk_info']   #组装保单产品列表
            applicationDate = dict_manual['policy_info']['applicationDate']   #保单生效日期
            effectiveDate = dict_manual['policy_info']['effectiveDate']   #保单生效日期
            insuBirth = dict_manual['policy_info']['insured_info'][0]['insuBirth']   #被保人出生日期
            #对保单产品列表中每个产品手工计算
            product = []
            for i in range (0,len(product_list)):
                productCode = product_list[i]['productCode']   #产品代码
                """step1:手工计算投保年龄"""
                policy_age = API0000_diy().calc_policy_insured_age(effectiveDate, insuBirth)   
                """step2:手工计算产品保额/保费"""
                stdPremBf = product_list[i]['stdPremBf']   #产品保费
                sumAssured = product_list[i]['sumAssured']   #产品保额
                units = product_list[i]['units']   #产品份数
                rs = API0000_diy().calc_product_premium(productCode, stdPremBf, sumAssured, units, dict_manual)
                premium = float(rs[0])   #产品保费
                amount = float(rs[1])   #产品保额
                #存入dict
                	#(1)计算得到的保额/保费存入dict
                if i<len(dict_manual['policy_info']['main_risk_info']):
                    dict_manual['policy_info']['main_risk_info'][i]['stdPremBf'] = str(premium)   #保费
                    dict_manual['policy_info']['main_risk_info'][i]['sumAssured'] = str(amount)   #保额
                else:
                    dict_manual['policy_info']['main_risk_info'][i-dict_manual['policy_info']['main_risk_info']]['stdPremBf'] = str(premium)   #保费
                    dict_manual['policy_info']['main_risk_info'][i-dict_manual['policy_info']['main_risk_info']]['sumAssured'] = str(amount)   #保额
                	#(2)万能产品的首期万能账户存入dict
                if productCode in ('1205','1206','3208','3211','5207','5206','3209','5201','5202','5211','5242','5225','5241','8204','5213','3213','8211','8212','8213','8214','5214','8216','8217','3245','3249','3247','3248','3243','3247B','3255','3256','3257CA','3258','3257','3264','3265','3267','3267CO','3265CB','3270','3267CB','8233','8237','8233CA1','3257CA1','8237CA1'):
                	deduct_type = 'nb_premium'
                	interestCapital = API0000_diy().calc_first_investAmount(dict_manual, deduct_type)   #计算首期万能账户余额
                	dict_manual['policy_info']['investAmount'] = {"productCode": productCode, "investAmount_list":[{'transCode':'00', 'investAmoun_detail_list': [{'transAmount':interestCapital, 'dealTime':effectiveDate}], 'interestCapital':interestCapital}], "total_interestCapital":interestCapital}
                """step3:手工计算检查点存入dict_manual"""
                #产品列表中每个产品生成一个产品信息product_info
                product_info = {'productCode':productCode,'premium':premium,'amount':amount}
                #产品信息product_info追加到dict_manual['calc_nb']['product']中
                product.append(product_info)
                dict_manual['check']['calc_nb']['product'].append(product_info)
                
                #手工计算保单新契约收费金额
                if i == (len(product_list) - 1):
                    for j in range(0,len(dict_manual['check']['calc_nb']['product'])):
                        payment = float(payment) + float(dict_manual['check']['calc_nb']['product'][j]['premium'])   #计算新契约收费金额
                        dict_manual['check']['calc_nb']['payment'] = payment   #新契约收费金额存入dict_manual['calc_nb']['payment']中 
                        dict_manual['check']['calc_nb']['msg'] = ''   
                """step4:手工计算轨迹信息存入dict_manual"""
                track_info = {'trackType':'nb', 'trackTime':applicationDate, 'trackData':{'product':product, 'payment':payment}, 'msg': ''}
                dict_manual['track_info'].append(track_info)   #存入轨迹信息
            dict_manual['check']['calc_nb']['apply_date'] = applicationDate
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

dict_manual = calc_API0001().calc_nb(dict_manual)
print 
"""
