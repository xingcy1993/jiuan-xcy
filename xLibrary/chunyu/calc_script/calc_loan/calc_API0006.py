# coding=utf-8

import sys
import traceback
reload(sys);
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *


"""手工计算贷款组件思路：
    入参：贷款日期、申请贷款金额、dict_manual
    step1:计算产品欠款余额列表：调用“手工计算贷款-产品欠款余额”函数
    step2:遍历产品列表
        1.计算产品现价
        2.计算产品欠款余额
            (1)判断产品欠款余额列表长度
                 ①产品欠款余额列表长度=0，产品欠款余额=0
                 ②产品欠款余额列表长度>0,从产品欠款余额列表获取此产品的欠款余额
            (2)得到产品的欠款余额
        3.计算贷款额度
        4.计算保单内产品总贷款额度
        5.定义每次遍历的产品贷款信息
        6.每次遍历的产品信息追加到product列表中
        7.计算保单实际的贷款金额
            (1)贷款申请金额>=保单总贷款额度时，贷款申请金额 = 保单总贷款额度
            (2)贷款申请金额<保单总贷款额度时，贷款申请金额不变
    step3:手工计算检查点存入dict_manual
    出参：dict_manual
"""
class calc_API0006:

    def __init__(self):
        pass
        
    def calc_loan(self, apply_date, loanApplyAmount, dict_manual):
        try:
            #初始化
            is_success = True
            message = ''
            unit = '手工计算-贷款:'
            payment = 0   #收付费金额:贷款金额
            total_loanAccountLimit = 0   #总限额
            product = []   #定义产品贷款信息列表
            pa_name = 'loan'   #保全代码
            #获取dict数据
            product_list = dict_manual['policy_info']['main_risk_info'] + dict_manual['policy_info']['sub_risk_info']   #组装保单产品列表
            effectiveDate = dict_manual['policy_info']['effectiveDate']   #生效日期
            callBackDate = dict_manual['policy_info']['callBackDate']   #回执日期
            policy_status = dict_manual['policy_info']['policy_status']   #保单状态
            end_reason = dict_manual['policy_info']['end_reason']   #终止原因
            insuBirth = dict_manual['policy_info']['insured_info'][0]['insuBirth']   #被保人生日
            #调用保全通用规则
            rs = API0000_diy().pa_general_rules(pa_name, apply_date, dict_manual)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            #调用贷款保全项规则
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
                #保单无可贷款险种，不可申请此保全项目
            sum_product_support_loan = 0
            for i in range (0,len(product_list)):
                productCode = product_list[i]['productCode']   #产品代码
                if productCode in ('5201','2032','1023','1024','1025','1026','1027','2034'):   #不支持贷款的产品跳过
                    continue
                else:
                    sum_product_support_loan = sum_product_support_loan + 1
            if sum_product_support_loan == 0:
                message = '无可申请此保全项目的险种'
                is_success = False
            assert is_success == True
                #续期保费未缴纳，不可申请此保全项目
            for i in range (0,len(product_list)):
                productCode = product_list[i]['productCode']   #产品代码
                if productCode in ('5201','2032','1023','1024','1025','1026','1027','2034'):   #不支持贷款的产品跳过
                    continue
                liability_state = product_list[i]['liability_state']   #获取产品状态
                if liability_state == '01':   #产品状态非有效跳过
                    if product_list[i]['chargeMode'] == 'S':   #产品趸交时不存在续期保费未缴纳情况
                        sum_product_support_loan = sum_product_support_loan + 1
                    elif product_list[i]['chargeMode'] != 'S':
                        pay_due_date = product_list[i]['pay_due_date']   #获取下期应缴日
                        if pay_due_date == '9999-12-31':   #产品非趸交但缴费期已满，不存在续期保费未缴纳情况
                            sum_product_support_loan = sum_product_support_loan + 1
                        elif pay_due_date != '9999-12-31':   #产品非趸交且缴费期未满，判断是否续期保费未缴纳
                            if apply_date <= pay_due_date:
                                sum_product_support_loan = sum_product_support_loan + 1
            if sum_product_support_loan == 0:
                message = '尚未缴纳续期保费'
                is_success = False
            assert is_success == True
            """step1:调用“手工计算贷款-产品欠款余额”函数，得到产品欠款余额列表"""
            product_loanAccountAmount_list = API0000_diy().calc_loanAccountAmount(dict_manual, apply_date)   #产品欠款余额列表
            """step2:遍历产品列表，合计各产品贷款金"""
            investAmount = 0   #万能账户余额
            for i in range (0,len(product_list)):
                productCode = product_list[i]['productCode']   #产品代码
                loanRate = float(API0000_diy().query_product_loan_rate(productCode, apply_date))   #产品贷款利率
                #3237产品
                if productCode in ('1217CB', '3237'):
                    sumAssured = float(product_list[i]['sumAssured'])
                    stdPremBf = float(product_list[i]['stdPremBf'])
                    FA = stdPremBf   #FA
                    #1.计算现金价值
                    presentPrice = float(API0000_diy().calc_present(dict_manual, apply_date))   #计算现价 
                    #2.计算产品欠款余额
                        #(1)判断产品欠款余额列表长度(2)得到产品的欠款余额
                    if len(product_loanAccountAmount_list)==0:
                            #①产品欠款余额列表长度=0，产品欠款余额=0
                        loanAccountAmount = 0    
                    else:
                            #②产品欠款余额列表长度>0,从产品欠款余额列表获取此产品的欠款余额
                        loanAccountAmount = product_loanAccountAmount_list[i]
                    #3.计算贷款额度
                    loanAccountLimit = round(presentPrice * float(0.8) - loanAccountAmount, 2)     #贷款额度
                elif productCode in ('3267CB1', '3257CA','8233','8237'):
                    sumAssured = float(product_list[i]['sumAssured'])
                    stdPremBf = float(product_list[i]['stdPremBf'])
                    #1.计算万能账户余额+手续费
                    rs = API0000_diy().calc_trial_tb_investAmount(dict_manual, apply_date)
                    investAmount = rs[0]
                    #print 'investAmount:' + str(investAmount)
                    #手续费
                    chargeAmount = API0000_diy().calc_loan_chargeAmount(dict_manual, apply_date, investAmount) 
                    #print 'chargeAmount:' + str(chargeAmount)
                    #未到期风险保费
                    #riskChargeFee = API0000_diy().calc_tb_riskChargeFee(dict_manual, riskamount, apply_date)
                    #2.计算现金价值（实际现价显示为0），参与计算的默认现价=万能账户余额
                    presentPrice = round((float(investAmount) - float(chargeAmount)), 2)  #默认现价
                    #3.计算产品欠款余额
                        #(1)判断产品欠款余额列表长度(2)得到产品的欠款余额
                    if len(product_loanAccountAmount_list)==0:
                            #①产品欠款余额列表长度=0，产品欠款余额=0
                        loanAccountAmount = 0    
                    else:
                            #②产品欠款余额列表长度>0,从产品欠款余额列表获取此产品的欠款余额
                        loanAccountAmount = product_loanAccountAmount_list[i]
                    #4.计算贷款额度
                    loanAccountLimit = round(presentPrice * float(0.8) - loanAccountAmount, 2)     #贷款额度
                else:
                    productCode = productCode   #产品代码
                    presentPrice = 1   #现金价值
                    loanAccountAmount = 0    #贷款欠款
                    loanAccountLimit = round(presentPrice * float(0.8) - loanAccountAmount, 2)     #贷款额度
                    sumAssured = 0
                    stdPremBf = 0
                    #4.计算保单内产品总贷款额度
                total_loanAccountLimit = total_loanAccountLimit + loanAccountLimit   #计算保单内产品总贷款额度
                    #5.定义每次遍历的产品贷款信息
                calc_product_loan = {'productCode':productCode, 'presentPrice':presentPrice, 'investAmount': investAmount, 'loanAccountLimit':loanAccountLimit, 'loanRate':loanRate, 'loanAccountAmount':loanAccountAmount, 'sumAssured':sumAssured, 'stdPremBf':stdPremBf}
                    #6.每次遍历的产品信息追加到product列表中
                product.append(calc_product_loan) 
            #判断贷款申请金额是否超过最大可贷款金额:
            if float(total_loanAccountLimit) < float(loanApplyAmount):
                message = '贷款申请金额不得超过最大可贷款金额:' + str(loanAccountLimit)
                is_success = False
            else:
                payment = float(loanApplyAmount)
                """step3:检查点存入dict_manual中"""
                calc_loan = {'loan_type':'loan', 'apply_date':apply_date, 'product':product, 'payment':payment, 'msg': ''}   #定义贷款信息
                dict_manual['check']['calc_loan'].append(calc_loan) 
                """step4:轨迹信息存入dict_manual中"""
                #定义轨迹信息
                track_info = {'trackType':'loan', 'trackTime':apply_date, 'trackData':{'product':product, 'payment':payment}, 'msg': ''}
                dict_manual['track_info'].append(track_info)   #存入轨迹信息
            assert is_success == True
        except Exception, e:
            is_success = False
            dict_manual['logInfo']['code'] = 0
            dict_manual['logInfo']['err'] = unit + str(e)
            calc_loan = {'loan_type':'loan', 'apply_date':apply_date, 'product':'', 'payment':payment, 'msg': message}   #定义贷款信息
            dict_manual['check']['calc_loan'].append(calc_loan) 
            """step4:轨迹信息存入dict_manual中"""
            #定义轨迹信息
            track_info = {'trackType':'loan', 'trackTime':apply_date, 'trackData':{'product':'', 'payment':payment}, 'msg': message}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息
            print '---err------'
            traceback.print_exc()
            print dict_manual
            exit()
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict_manual, is_success, message, unit)      
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
		'applicationDate': '2016-11-12',
		'effectiveDate': '2016-11-13',
		'callBackDate': '2016-11-12',
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
			'sumAssured': '358900',
			'coveragePeriod': '999',
			'stdPremBf': '100000',
			'chargePeriodType': 'Y',
			'payOption': None,
			'planFreq': None,
			'chargePeriod': '10',
			'bonusYearOrAge': '0',
			'units': None,
			'coverPeriodType': 'Y',
			'productId': '10038',
            'productCode': '3237',
			'chargeMode': 'Y'
		}],
		'sub_risk_info': [],
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
        'calc_loan':[]
	}
}

total_times_renew = 2

apply_date = '2017-03-17'   #保全申请日期
loanApplyAmount = 2000
dict_manual = calc_API0006().calc_loan(apply_date, loanApplyAmount, dict_manual)

apply_date = '2022-10-01'   #保全申请日期
loanApplyAmount = 2000
dict_manual = calc_API0006().calc_loan(apply_date, loanApplyAmount, dict_manual)
print dict_manual['track_info']
"""




