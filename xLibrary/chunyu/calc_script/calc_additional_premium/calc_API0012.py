# coding=utf-8

import os
import sys
import xlrd
import traceback
reload(sys);
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *



"""手工计算追加保费:
    step1:遍历产品列表
    step2:追加保费存入万能结息账户
    step3:手工计算检查点存入dict_manual
"""
class calc_API0012:

    def __init__(self):
        pass
        
    def calc_additional_premium(self, sendDate, addInvestAmount, dict_manual):
        try:
            #初始化
            is_success = True
            message = ''
            unit = '手工计算-追加保费:'
            payment = 0
            product = []
            #获取dict数据
            product_list = dict_manual['policy_info']['main_risk_info'] + dict_manual['policy_info']['sub_risk_info']   #组装保单产品列表
            effectiveDate = dict_manual['policy_info']['effectiveDate']   #生效日期
            callBackDate = dict_manual['policy_info']['callBackDate']   #回执日期
            policy_status = dict_manual['policy_info']['policy_status']   #保单状态
            end_reason = dict_manual['policy_info']['end_reason']   #终止原因
            insuBirth = dict_manual['policy_info']['insured_info'][0]['insuBirth']   #被保人生日
            #调用保全通用规则
            pa_name = 'additional_premium'
            rs = API0000_diy().pa_general_rules(pa_name, sendDate, dict_manual)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            #调用追加保费保全项规则
                #保单未过犹豫期
            sum_product_support_loan = 0
            for i in range (0,len(product_list)):
                productCode = product_list[i]['productCode']   #产品代码
                hesitation_days = API0000_diy().query_product_hesitation_days(productCode)   #获取险种犹豫期天数
                if sendDate > API0000_diy().date_add_subtract(callBackDate, int(hesitation_days)):
                    sum_product_support_loan  = sum_product_support_loan + 1
            if sum_product_support_loan == 0:
                message = '保单未过犹豫期'
                is_success = False
            assert is_success == True
                #保单生效满两年后，才可以申请追加
            third_policy_anniversary = API0000_diy().calc_policy_anniversary(effectiveDate, 3)   #获取第三年度保单周年日
            if sendDate < third_policy_anniversary:
                is_success = False
                message = '保单生效满两年后，才可以申请追加'
            assert is_success == True
                #追加下限不能低于1000
            if float(addInvestAmount) < 1000:
                is_success = False
                message = '追加下限不能低于1000'
            assert is_success == True
                #追加保费需是1000的整数倍
            if float(addInvestAmount)%float(1000) != 0:
                is_success = False
                message = '追加保费需是1000的整数倍'
            assert is_success == True 

            """step1:遍历产品列表，合计各产品追加保费"""
            product = []
            for i in range (0,len(product_list)):
                if product_list[i]['productCode'] in ('1205','1206','3208','3211','3267CB1','5207','5206','3209','5201','5202','5211','5242','5225','5241','8204','5213','3213','8211','8212','8213','8214','5214','8216','8217','3245','3249','3247','3248','3243','3247B','3255','3256','3257CA','3258','3257','3264','3265','3267','3267CO','3265CB','3270','3267CB','8233','8237','8233CA1','3257CA1','8237CA1'):
                    productCode = product_list[i]['productCode']   #产品code
                    #a.计算初始扣费
                    deduct_type = 'add_premium'
                    chargeAmount = API0000_diy().calc_initial_deduct(productCode, deduct_type, addInvestAmount)  
                    #f.计算追加保费首次进入万能账户金额
                    interestCapital = round((float(addInvestAmount) - chargeAmount), 2)  
                    #存入dict万能账户列表中
                    dict_manual['policy_info']['investAmount']['productCode'] = productCode
                    dict_manual['policy_info']['investAmount']['investAmount_list'].append({'transCode':'02', 'investAmoun_detail_list': [{'transAmount':interestCapital, 'dealTime':sendDate}], 'interestCapital':interestCapital})
                    dict_manual['policy_info']['investAmount']['total_interestCapital'] = round((float(dict_manual['policy_info']['investAmount']['total_interestCapital']) + interestCapital), 2)
                    #定义product列表
                    product.append({'productCode':productCode, 'addInvestAmount':float(addInvestAmount), 'chargeAmount': chargeAmount, 'surrenderAmount':interestCapital}) 
            if product != []:
                """step3:手工计算检查点存入dict_manual"""
                unit = '节点:派发追加保费_定义检查点信息:'  # 节点
                message = ''
                calc_additional_premium = {}
                #追加保费存入dict['check']['calc_additional_premium']中
                calc_additional_premium = {'apply_date':sendDate, 'product':product, 'payment':float(addInvestAmount), 'msg': ''}  
                dict_manual['check']['calc_additional_premium'].append(calc_additional_premium)
                """2.定义轨迹信息"""
                track_info = {'trackType':'additional_premium', 'trackTime':sendDate, 'trackData':{'product':product, 'payment':float(addInvestAmount)}, 'msg': ''}
                dict_manual['track_info'].append(track_info)   #存入轨迹信息
            assert is_success == True
        except Exception, e:
            is_success = False
            dict_manual['logInfo']['code'] = 0
            dict_manual['logInfo']['err'] = unit + str(e)
            calc_additional_premium = {'apply_date':sendDate, 'product':'', 'payment':float(addInvestAmount), 'msg': message}  
            dict_manual['check']['calc_additional_premium'].append(calc_additional_premium)
            track_info = {'trackType':'additional_premium', 'trackTime':sendDate, 'trackData':{'product':'', 'payment':float(addInvestAmount)}, 'msg': message}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息
            print '---err------'
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
        'calc_additional_premium': [],
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



sendDate = '2020-12-12'   #追加保费派发日期
dict_manual = calc_API0011().calc_additional_premium(sendDate, dict_manual)
print dict_manual
"""


