# coding=utf-8

import os
import sys
import traceback
reload(sys);
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *



"""手工计算退保试算：
    step1:合计各产品退保金
          1.计算贷款欠款余额
          2.计算现价
          3.合计退保金额
    step2:手工计算检查点存入dict_manual
"""
class calc_API0008:

    def __init__(self):
        pass
        
    def calc_trial_tb(self, apply_date, dict_manual):
        try:
            #初始化
            is_success = True
            message = ''
            unit = '手工计算-退保试算:'
            payment = 0   #收付费金额
            product = []   #定义产品退保信息列表
            total_times_renew = dict_manual['public']['total_times_renew']   #已续期次数
            #获取dict数据
            product_list = dict_manual['policy_info']['main_risk_info'] + dict_manual['policy_info']['sub_risk_info']   #组装保单产品列表
            effectiveDate = dict_manual['policy_info']['effectiveDate']   #生效日期
            callBackDate = dict_manual['policy_info']['callBackDate']   #回执日期
            policy_status = dict_manual['policy_info']['policy_status']   #保单状态
            end_reason = dict_manual['policy_info']['end_reason']   #终止原因
            insuBirth = dict_manual['policy_info']['insured_info'][0]['insuBirth']   #被保人生日
            #调用保全通用规则
            pa_name = 'trial_tb'
            rs = API0000_diy().pa_general_rules(pa_name, apply_date, dict_manual)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            #调用退保试算保全项规则
                #保单未过犹豫期
            sum_product_support_loan = 0
            for i in range (0,len(product_list)):
                productCode = product_list[i]['productCode']   #产品代码
                hesitation_days = API0000_diy().query_product_hesitation_days(productCode)   #获取险种犹豫期天数
                if apply_date > API0000_diy().date_add_subtract(callBackDate, int(hesitation_days)):
                    sum_product_support_loan  = sum_product_support_loan + 1
            if sum_product_support_loan == 0:
                message = '保单未过犹豫期'
                is_success = False
            assert is_success == True
            """step1:合计各产品退保金"""
                #计算欠款余额
            loanAccountAmount = API0000_diy().calc_tb_loanAccountAmount(dict_manual, apply_date)
            for i in range (0,len(product_list)):
                productCode = product_list[i]['productCode']   #产品代码
                #计算现价
                presentPrice = float(API0000_diy().calc_present(dict_manual, apply_date))
                #print 'presentPrice:' + str(presentPrice)
                #万能账户价值
                rs = API0000_diy().calc_trial_tb_investAmount(dict_manual, apply_date)
                investAmount = rs[0]
                riskamount_list = rs[1]
                #print 'investAmount:' + str(investAmount)
                #手续费
                chargeAmount = API0000_diy().calc_loan_chargeAmount(dict_manual, apply_date, investAmount) 
                #print 'chargeAmount:' + str(chargeAmount)
                #退还续期保费
                refundRenewPrem = float(0)   
                #累计生息账号
                cbSbAccount = round(float(dict_manual['policy_info']['cbSbAccount']['cashAmount']) + API0000_diy().calc_interest_account(dict_manual, apply_date), 2) 
                #print 'cbSbAccount:' + str(cbSbAccount)
                #退还未到期风险保险费
                riskChargeFee = 0 - float(API0000_diy().calc_tb_riskChargeFee(dict_manual, riskamount_list, apply_date))
                #print 'riskChargeFee:' + str(riskChargeFee)
                #红利累计生息账户
                bonusAccount = float(0)
                #已分红金额扣回
                paidBonus = float(0)   
                #产品应付金额
                surrenderAmount = round((presentPrice + investAmount - chargeAmount -loanAccountAmount - refundRenewPrem + cbSbAccount - riskChargeFee + bonusAccount -paidBonus), 2)    
                #合计退保金额
                payment = round((payment + surrenderAmount), 2) 
                
                """step2:检查点存入dict_manual中"""
                #定义每次遍历的产品退保信息
                calc_product_tb = {'productCode':productCode, 'presentPrice':presentPrice, 'investAmount':investAmount, 'chargeAmount':chargeAmount, 'loanAccountAmount':loanAccountAmount, 'refundRenewPrem':refundRenewPrem, 'cbSbAccount':cbSbAccount, 'riskChargeFee':riskChargeFee, 'bonusAccount':bonusAccount, 'paidBonus':paidBonus, 'surrenderAmount':surrenderAmount}
                #每次遍历的产品信息追加到product列表中
                product.append(calc_product_tb)
            calc_trial_tb = {'apply_date':apply_date, 'product':product, 'payment':payment, 'msg': ''}   #定义每期续期的续期信息
            dict_manual['check']['calc_trial_tb'].append(calc_trial_tb) 
            """step2:轨迹信息存入dict_manual中"""
            track_info = {'trackType':'trial_tb', 'trackTime': apply_date, 'trackData':{'product':product, 'payment':payment}, 'msg': ''}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息
            assert is_success == True
            assert dict_manual['logInfo']['code'] == '1'
        except Exception, e:
            is_success = False
            dict_manual['logInfo']['code'] = 0
            dict_manual['logInfo']['err'] = unit + str(e)
            calc_trial_tb = {'apply_date':apply_date, 'product':'', 'payment':payment, 'msg': message}   #定义每期续期的续期信息
            dict_manual['check']['calc_trial_tb'].append(calc_trial_tb) 
            track_info = {'trackType':'trial_tb', 'trackTime': apply_date, 'trackData':{'product':'', 'payment':payment}, 'msg': message}
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
		'applicationDate': '2016-09-01',
		'effectiveDate': '2016-09-02',
		'callBackDate': '2016-09-01',
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
			'insuBirth': '1988-01-01'
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
		'username_entry': '',
        'total_times_renew': 2
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
        'calc_trial_tb':[],
        'calc_loan':[{'product': [{'presentPrice': 328248.22, 'productCode': '3237', 'loanAccountAmount': 0, 'sumAssured': 358900.0, 'stdPremBf': 100000.0, 'loanRate': 0.05, 'loanAccountLimit': 262598.58}], 'loan_type': 'loan', 'apply_date': '2020-12-20', 'payment': 1000.0}, {'product': [{'presentPrice': 338961.1, 'productCode': '3237', 'loanAccountAmount': 1040.65, 'sumAssured': 358900.0, 'stdPremBf': 100000.0, 'loanRate': 0.05, 'loanAccountLimit': 270128.23}], 'loan_type': 'loan', 'apply_date': '2021-10-10', 'payment': 1000.0}]
	}
}



apply_date = '2021-12-20'   #保全申请日期
total_times_renew = 2
dict_manual = calc_API0008().calc_trial_tb(apply_date, dict_manual)
print dict_manual['check']
"""


