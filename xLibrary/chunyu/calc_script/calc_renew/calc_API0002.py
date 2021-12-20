#coding=utf-8

import os
import sys
import xlrd
import traceback
from xLibrary.chunyu.API0000 import *

reload(sys);
sys.setdefaultencoding("utf8")

"""手工计算续期：
    step1:获取dict_manual中，续期产品保费
    step2:手工计算检查点存入dict_manual
"""
class calc_API0002:

    def __init__(self):
        pass

    def calc_renew(self, pay_due_date, dict_manual):
        apply_date = pay_due_date
        try:
            #初始化
            is_success = True
            message = ''
            unit = '手工计算-续期:'
            payment = 0   #新契约收费金额
            msg = ''
            #获取dict数据
            policy_status = dict_manual['policy_info']['policy_status']      #保单状态
            if policy_status == '01':
                product_list = dict_manual['policy_info']['main_risk_info'] + dict_manual['policy_info']['sub_risk_info']   #组装保单产品列表
                """step1:获取dict_manual中，续期产品保费"""
                num_renew_product = 0
                for i in range (0,len(product_list)):
                    liability_state = product_list[i]['liability_state']   #获取产品状态
                    product_pay_due_date = product_list[i]['pay_due_date']   #获取产品下期应缴日
                    if liability_state == '01' and pay_due_date[0:10] >= product_pay_due_date:
                        num_renew_product = num_renew_product + 1
                        payment = float(product_list[i]['stdPremBf']) + float(payment)
                        #改变dict中险种信息
                        if i < len(dict_manual['policy_info']['main_risk_info']):
                            surplus_times_renew = int(dict_manual['policy_info']['main_risk_info'][i]['surplus_times_renew']) - 1   #剩余续期次数
                            dict_manual['policy_info']['main_risk_info'][i]['surplus_times_renew'] = surplus_times_renew
                            pay_due_date = dict_manual['policy_info']['main_risk_info'][i]['pay_due_date']   #未续期前的下期应缴日
                            if surplus_times_renew == 0:
                                dict_manual['policy_info']['main_risk_info'][i]['pay_due_date'] = '9999-12-31'
                            elif surplus_times_renew > 0:
                                if dict_manual['policy_info']['main_risk_info'][i]['chargeMode'] == 'S':  #趸交
                                    dict_manual['policy_info']['main_risk_info'][i]['pay_due_date'] = '9999-12-31'
                                elif dict_manual['policy_info']['main_risk_info'][i]['chargePeriodType'] in ('A', 'Y') and dict_manual['policy_info']['main_risk_info'][i]['chargeMode'] == 'Y':   #缴费期间类型(按年交/交至某年龄)+缴费频率按年交
                                    #获取保单生效日期前一日年份
                                    pay_due_date_year = pay_due_date[0:4]   
                                    #初步组装:下期应缴日
                                    pay_due_date = str(int(pay_due_date_year) + 1) + pay_due_date[4:10]
                                    #最终得到:下期应缴日
                                    if API0000_diy().isvaild_date(pay_due_date):
                                        #日期有效:下期应缴日 = 下期应缴日字符串
                                        pay_due_date = pay_due_date
                                    else:
                                        #日期有效:下期应缴日 = （下期应缴日字符串年份） 拼接 （02-28）
                                        pay_due_date = pay_due_date[0:4] + '-02-28'
                                    dict_manual['policy_info']['main_risk_info'][i]['pay_due_date'] = pay_due_date
                                elif dict_manual['policy_info']['main_risk_info'][i]['chargePeriodType'] in ('A', 'M') and dict_manual['policy_info']['main_risk_info'][i]['chargeMode'] == 'M':   #缴费期间类型（按月交/交至某年龄)+缴费频率按月交
                                    pay_due_date_year = pay_due_date[0:4]    #年份
                                    pay_due_date_month = pay_due_date[5:7]    #月份
                                    pay_due_date_day = pay_due_date[8:10]    #日期
                                    #初步组装:下期应缴日
                                    if int(pay_due_date_month)+1 < 10:
                                        pay_due_date = pay_due_date_year + '-0' + str(int(pay_due_date_month)+1) + '-' + pay_due_date_day
                                    elif int(pay_due_date_month)+1 >= 10 and int(pay_due_date_month)+1 < 13:
                                        pay_due_date = pay_due_date_year + '-' + str(int(pay_due_date_month)+1) + '-' + pay_due_date_day
                                    elif int(pay_due_date_month)+1 == 13:
                                        pay_due_date = str(int(pay_due_date_year)+1) + '-01' + '-' + pay_due_date_day
                                    #最终得到:下期应缴日
                                    if API0000_diy().isvaild_date(pay_due_date):
                                        #日期有效:下期应缴日 = 下期应缴日字符串
                                        pay_due_date = pay_due_date
                                    else:
                                        #日期有效:下期应缴日 = （下期应缴日字符串年份） 拼接 （02-28）
                                        pay_due_date = API0000_diy().date_add_subtract(pay_due_date[0:4] + '-03-01', -1)
                                    dict_manual['policy_info']['main_risk_info'][i]['pay_due_date'] = pay_due_date
                        else:
                            surplus_times_renew = int(dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['surplus_times_renew']) - 1#剩余续期次数
                            dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['surplus_times_renew'] = surplus_times_renew
                            pay_due_date = dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['pay_due_date']   #未续期前的下期应缴日
                            if surplus_times_renew == 0:
                                dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['pay_due_date'] = '9999-12-31'
                            elif surplus_times_renew > 0:
                                if dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['chargeMode'] == 'S':  #趸交
                                    dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['pay_due_date'] = '9999-12-31'
                                elif dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['chargePeriodType'] in ('A', 'Y') and dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['chargeMode'] == 'Y':   #缴费期间类型(按年交/交至某年龄)+缴费频率按年交
                                    #获取保单生效日期前一日年份
                                    pay_due_date_year = pay_due_date[0:4]   
                                    #初步组装:下期应缴日
                                    pay_due_date = str(int(pay_due_date_year) + 1) + pay_due_date[4:10]
                                    #最终得到:下期应缴日
                                    if API0000_diy().isvaild_date(pay_due_date):
                                        #日期有效:下期应缴日 = 下期应缴日字符串
                                        pay_due_date = pay_due_date
                                    else:
                                        #日期有效:下期应缴日 = （下期应缴日字符串年份） 拼接 （02-28）
                                        pay_due_date = pay_due_date[0:4] + '-02-28'
                                    dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['pay_due_date'] = pay_due_date
                                elif dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['chargePeriodType'] in ('A', 'M') and dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['chargeMode'] == 'M':   #缴费期间类型（按月交/交至某年龄)+缴费频率按月交
                                    pay_due_date_year = pay_due_date[0:4]    #年份
                                    pay_due_date_month = pay_due_date[5:7]    #月份
                                    pay_due_date_day = pay_due_date[8:10]    #日期
                                    #初步组装:下期应缴日
                                    if int(pay_due_date_month)+1 < 10:
                                        pay_due_date = pay_due_date_year + '-0' + str(int(pay_due_date_month)+1) + '-' + pay_due_date_day
                                    elif int(pay_due_date_month)+1 >= 10 and int(pay_due_date_month)+1 < 13:
                                        pay_due_date = pay_due_date_year + '-' + str(int(pay_due_date_month)+1) + '-' + pay_due_date_day
                                    elif int(pay_due_date_month)+1 == 13:
                                        pay_due_date = str(int(pay_due_date_year)+1) + '-01' + '-' + pay_due_date_day
                                    #最终得到:下期应缴日
                                    if API0000_diy().isvaild_date(pay_due_date):
                                        #日期有效:下期应缴日 = 下期应缴日字符串
                                        pay_due_date = pay_due_date
                                    else:
                                        #日期有效:下期应缴日 = （下期应缴日字符串年份） 拼接 （02-28）
                                        pay_due_date = API0000_diy().date_add_subtract(pay_due_date[0:4] + '-03-01', -1)
                                    dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['pay_due_date'] = pay_due_date
                if num_renew_product == 0:
                    #message = '不存在满足续期的产品'
                    message = '续期不成功'
                    is_success = False
            else:
                #message = '保单非有效状态'
                message = '续期不成功'
                is_success = False
            assert is_success == True
            #存入dict_manual
            total_times_renew = int(dict_manual['public']['total_times_renew'])   #获取已续期次数
            dict_manual['public']['total_times_renew'] = total_times_renew + 1   #每次续期后，续期次数+1
            #step2:检查点存入dict_manual中"""
            renew_info = {'apply_date':apply_date, 'payment':payment, 'msg': ''}   #定义每期续期的续期信息
            dict_manual['check']['calc_renew'].append(renew_info)   
            #step3:轨迹信息存入dict_manual中"""
            #定义轨迹信息
            track_info = {'trackType':'renew', 'trackTime':apply_date, 'trackData':{'payment': payment}, 'msg': ''}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息
            assert is_success == True
            assert dict_manual['logInfo']['code'] == '1'
        except Exception, e:
            is_success = False
            dict_manual['logInfo']['code'] = 0
            dict_manual['logInfo']['err'] = unit + str(e)
            renew_info = {'apply_date':apply_date, 'payment':payment, 'msg': message}   #定义每期续期的续期信息
            dict_manual['check']['calc_renew'].append(renew_info)   
            track_info = {'trackType':'renew', 'trackTime':apply_date, 'trackData':{'payment': payment}, 'msg': message}
            dict_manual['track_info'].append(track_info)  
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


pay_due_date = '2020-12-12'   #续期缴费日期
dict_manual = calc_API0002().calc_renew(pay_due_date, dict_manual)
print dict_manual
#"""


