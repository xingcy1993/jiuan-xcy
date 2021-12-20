#coding=utf-8

import os
import sys
import xlrd
import traceback
reload(sys);
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *



"""手工计算客户重要资料变更：
    1.改变dict_manual信息
    2.轨迹信息
    3.检查点存入dict_manual中
"""
class calc_API0009:

    def __init__(self):
        pass

    def calc_CD(self, apply_date, modify_info_dict, dict_manual):
        try:
            #初始化
            is_success = True
            message = ''
            unit = '手工计算-客户重要资料变更:'

            """1.改变dict_manual信息"""
            #角色为投保人时:
            if modify_info_dict['roleType'] == '1':
                #性别
                if modify_info_dict['gender']['is_modify'] == 'Y':
                    dict_manual['policy_info']['holder_info']['gender'] = modify_info_dict['gender']['new'] 
                #出生日期
                if modify_info_dict['birthday']['is_modify'] == 'Y':
                    dict_manual['policy_info']['holder_info']['pbHoldBirth'] = modify_info_dict['birthday']['new']  
                #证件类型
                if modify_info_dict['certiType']['is_modify'] == 'Y':
                    dict_manual['policy_info']['holder_info']['certiType'] = modify_info_dict['certiType']['new']
                #证件号码
                if modify_info_dict['certiCode']['is_modify'] == 'Y':
                    dict_manual['policy_info']['holder_info']['certiCode'] = modify_info_dict['certiCode']['new']  
                #职业代码/名称+职业等级
                if modify_info_dict['jobCateId']['is_modify'] == 'Y':
                    dict_manual['policy_info']['holder_info']['jobCode'] = modify_info_dict['jobCateId']['new']    #职业代码/名称    
                    dict_manual['policy_info']['holder_info']['jobClass'] = API0000_diy().get_jobClass(modify_info_dict['jobCateId']['new'])   #职业等级
                #个人年收入（万元）
                if modify_info_dict['income']['is_modify'] == 'Y':
                    dict_manual['policy_info']['holder_info']['annualIncome'] = modify_info_dict['income']['new']
                #家庭年收入（万元）
                if modify_info_dict['familyIncome']['is_modify'] == 'Y':
                    dict_manual['policy_info']['holder_info']['familyIncome'] = modify_info_dict['familyIncome']['new']
                #收入来源
                if modify_info_dict['incomeSource']['is_modify'] == 'Y':
                    dict_manual['policy_info']['holder_info']['incomeSource'] = modify_info_dict['incomeSource']['new']   
                #收入来源备注
                if modify_info_dict['incomeSourceNote']['is_modify'] == 'Y':
                    dict_manual['policy_info']['holder_info']['incomeSourceNote'] = modify_info_dict['incomeSourceNote']['new'] 
                #工作单位
                if modify_info_dict['companyName']['is_modify'] == 'Y':
                    dict_manual['policy_info']['holder_info']['workCompany'] = modify_info_dict['companyName']['new'] 
            #角色为被保人时:
            elif modify_info_dict['roleType'] == '2':
                #找到变更的是哪个被保险人
                for i in range(0,len(dict_manual['policy_info']['insured_info'])):
                    if dict_manual['policy_info']['insured_info'][i]['insuCertiCode'] == modify_info_dict['oldcertiCode']:
                        break    
                #性别
                if modify_info_dict['gender']['is_modify'] == 'Y':
                    dict_manual['policy_info']['insured_info'][i]['insuGender'] = modify_info_dict['gender']['new'] 
                #出生日期
                if modify_info_dict['birthday']['is_modify'] == 'Y':
                    dict_manual['policy_info']['insured_info'][i]['insuBirth'] = modify_info_dict['birthday']['new']  
                #证件类型
                if modify_info_dict['certiType']['is_modify'] == 'Y':
                    dict_manual['policy_info']['insured_info'][i]['insuCertiType'] = modify_info_dict['certiType']['new']
                #证件号码
                if modify_info_dict['certiCode']['is_modify'] == 'Y':
                    dict_manual['policy_info']['insured_info'][i]['insuCertiCode'] = modify_info_dict['certiCode']['new']  
                #职业代码/名称+职业等级
                if modify_info_dict['jobCateId']['is_modify'] == 'Y':
                    dict_manual['policy_info']['insured_info'][i]['insuWorkCode'] = modify_info_dict['jobCateId']['new']   #职业代码/名称    
                    dict_manual['policy_info']['insured_info'][i]['insujobClass'] = API0000_diy().get_jobClass(modify_info_dict['jobCateId']['new'])   #职业等级
                #个人年收入（万元）
                if modify_info_dict['income']['is_modify'] == 'Y':
                    dict_manual['policy_info']['insured_info'][i]['annualIncome'] = modify_info_dict['income']['new']
                #收入来源
                if modify_info_dict['incomeSource']['is_modify'] == 'Y':
                    dict_manual['policy_info']['insured_info'][i]['insuincomeSource'] = modify_info_dict['incomeSource']['new']   
                #收入来源备注
                if modify_info_dict['incomeSourceNote']['is_modify'] == 'Y':
                    dict_manual['policy_info']['insured_info'][i]['insuincomeSourceNote'] = modify_info_dict['incomeSourceNote']['new'] 
                #工作单位
                if modify_info_dict['companyName']['is_modify'] == 'Y':
                    dict_manual['policy_info']['insured_info'][i]['insuCompany'] = modify_info_dict['companyName']['new'] 
            elif modify_info_dict['roleType'] == '3':
                print 1
            elif modify_info_dict['roleType'] == '4':
                print 1
            #(2)更改产品信息
            #获取dict数据
            product_list = dict_manual['policy_info']['main_risk_info'] + dict_manual['policy_info']['sub_risk_info']   #组装保单产品列表
            effectiveDate = dict_manual['policy_info']['effectiveDate']   #保单生效日期
            insuBirth = dict_manual['policy_info']['insured_info'][0]['insuBirth']   #被保人出生日期
            product = []   #定义产品列表
            payment = 0   #收付费
            #调用保全通用规则
            pa_name = 'CD'
            rs = API0000_diy().pa_general_rules(pa_name, apply_date, dict_manual)
            is_success = rs[0]
            message = rs[1] 
            assert is_success == True

            for i in range (0,len(product_list)):
                Main_Rider = product_list[i]['Main_Rider']
                """step1:手工计算投保年龄"""
                policy_age = API0000_diy().calc_policy_insured_age(effectiveDate, insuBirth)   
                """step2:手工计算产品保额/保费"""
                productCode = str(product_list[i]['productCode'])   #产品代码
                premBfChg = product_list[i]['stdPremBf']   #产品变化前保费
                amountBfChg = product_list[i]['sumAssured']   #产品变化前保额
                units = product_list[i]['units']   #产品变化前份数
                rs = API0000_diy().calc_product_premium(productCode, premBfChg, amountBfChg, units, dict_manual)
                premAfChg = rs[0]   #产品变化后保费
                amountAfChg = rs[1]   #产品变化后保额
                premDif = round(round(float(premAfChg), 2) - round(float(premBfChg), 2), 2)
                product.append({'productCode':productCode, 'premDif':premDif})
                payment = payment + premDif
                #改保费
                if premBfChg != premAfChg:
                    if Main_Rider == 'M':
                        dict_manual['policy_info']['main_risk_info'][i]['stdPremBf'] = str(premAfChg)
                    #若产品为附加险，遍历主险进行替换
                    elif Main_Rider == 'R':
                        dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['stdPremBf'] = str(premAfChg)    
                #改保额
                if amountBfChg != amountAfChg:
                    if Main_Rider == 'M':
                        dict_manual['policy_info']['main_risk_info'][i]['sumAssured'] = str(amountAfChg)
                    #若产品为附加险，遍历主险进行替换
                    elif Main_Rider == 'R':
                        dict_manual['policy_info']['sub_risk_info'][i-len(dict_manual['policy_info']['main_risk_info'])]['sumAssured'] = str(amountAfChg)
              
            """2.检查点存入dict_manual中"""
            dict_manual['check']['calc_CD'].append({'apply_date':apply_date, 'product':product, 'payment':payment, 'msg': ''})
            
            """3.定义轨迹信息"""
            #定义轨迹信息
            track_info = {'trackType':'CD', 'trackTime':apply_date, 'trackData':{'product':product, 'payment':payment}, 'msg': ''}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息 
            assert is_success == True
            assert dict_manual['logInfo']['code'] == '1'
        except Exception, e:
            is_success = False
            dict_manual['logInfo']['code'] = 0
            dict_manual['logInfo']['err'] = unit + str(e)
            dict_manual['check']['calc_CD'].append({'apply_date':apply_date, 'product':'', 'payment':payment, 'msg': message})
            
            """3.定义轨迹信息"""
            #定义轨迹信息
            track_info = {'trackType':'CD', 'trackTime':apply_date, 'trackData':{'product':'', 'payment':payment}, 'msg': message}
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
dict_manual = {'logInfo': {'msg': '', 'code': '1', 'result': '', 'Err': ''}, 'policy_info': {'policyChannel': u'03', 'organId': '10008', 'effectiveDate': '2016-06-13', 'sub_risk_info': [], 'agent_info': {'agent_name': '', 'channelId': '', 'partnerId': '', 'agent_birthday': '', 'salesChannelText': '', 'agent_gender': '', 'headPartner': ''}, 'proposalNo': '1101021130094152', 'policy_status': '01', 'insured_info': [{'insuBirth': u'1988-01-02', 'insuEmail': 'ZCb86UWCMOj0@189.com', 'insuWeight': '78', 'insuDistrictCode': '110101', 'insuGender': u'0', 'insuCityCode': '110100', 'insuHeight': '178', 'insujobClass': '1', 'taxPayerType': '01', 'insuCertiType': u'2', 'insuMarriage': '20', 'insuPostalCode': '120000', 'insuMobile': u'18089837905', 'homeTel': '010-993433344', 'insuProvinceCode': '110000', 'insuincomeSourceNote': 'wu', 'insuresidentType': '1', 'driverLicenseType': '06', 'annualIncome': '5000000', 'insuCertiValidEndDate': u'2030-01-01', 'insunationnality1': '01', 'insuRelation': u'99', 'insuWorkType': '02', 'insuCertiCode': u'4567343400743', 'insuWorkCode': '0001001', 'insueducationId': '40', 'insuName': u'\u5f20\u56db\u7b2c', 'insuNationatiy': 'CHN', 'officeTel': '010-93456444', 'insuincomeSource': '01', 'insuAddrDetail': '\xe5\xbb\xba\xe5\x9b\xbd\xe9\x97\xa8\xe4\xb8\x9c\xe5\xa4\xa7\xe8\xa1\x9722\xe5\x8f\xb7', 'insumedicalInsType': '01', 'insuCompany': 'apple'}], 'end_reason': '', 'applicationDate': '2016-06-12', 'policyType': 1, 'invalid_reason': '', 'holder_info': {'familyIncome': '100000', 'districtCode': '110101', 'driverLicenseType': '06', 'mobilePhone': u'18909892905', 'weight':'67', 'annualIncome': '100000', 'medicalInsType': '01', 'Industry': '', 'taxPayerType': '01', 'nationnality1': '01', 'height': '167', 'certiCode': u'4567343400742', 'educationId': '40', 'pbCertiValidEndDate': u'2030-01-01', 'residentType':'1', 'incomeSource': '01', 'nationality': 'CHN', 'homeTel': '010-98343543', 'Email': '', 'jobClass': '1', 'cityCode': '110100', 'name': u'\u5f20\u56db\u53c8', 'incomeSourceNote': 'wu', 'workCompany': '\xe4\xb8\x9c\xe6\x96\xb9\xe5\xb0\x8f\xe6\xb8\x85\xe5\x8d\x8e', 'premBudget': '30000', 'gender': u'0', 'certiType': u'2', 'addrDetail': '\xe5\xbb\xba\xe5\x9b\xbd\xe9\x97\xa8\xe4\xb8\x9c\xe5\xa4\xa7\xe8\xa1\x9722\xe5\x8f\xb7', 'isMarried': '20', 'officeTel': '010-98343543', 'pbHoldBirth': u'1988-01-01', 'industry': '03', 'provinceCode': '110000', 'email': 'uWKiC@126.com', 'jobCode': '0001001', 'postalCode': '121200', 'Nationality': '', 'sameASInsurd': u'0'}, 'benf_info': [{}], 'callBackDate': '2016-06-12', 'policyNo': u'8088762766967068', 'main_risk_info': [{'Main_Rider':'M', 'sumAssured': 358900.0, 'coveragePeriod': u'10', 'stdPremBf': 100000, 'chargePeriod': u'3', 'bonusYearOrAge': u'4','chargePeriodType': u'Y', 'payOption': u'03', 'main_risk_num': '1', 'units': None, 'coverPeriodType': u'Y', 'planFreq': u'05', 'chargeMode': u'Y', 'productId':10038}], 'payment_nb': {'payMode': u'00', 'payment': 100000.0}}, 'public': {'username_review': u'xingcy1', 'apply_date': '', 'is_2risk': u'0', 'env_name': '\xe9\xa2\x84\xe7\x94\x9f\xe4\xba\xa7', 'interface_ip': '10.1.6.11', 'execNo': '', 'is_HolderExemption': u'0', 'total_times_renew': 0, 'username_entry': u'xingcy'},'track_info': [{'trackData': {'applicationDate': '2016-06-12', 'policyNo': u'8088762766967068'}, 'trackTime': '2016-06-12', 'trackType': 'nb'}], 'check': {'calc_renew': [], 'calc_hesitation_tb': {'apply_date': '', 'payment': ''}, 'calc_loan': [], 'calc_tb': [], 'calc_trial_tb': [], 'calc_survivalFee': [], 'calc_nb': {'product': [{'productCode': u'3237', 'amount': 358900.0, 'premium': 100000.0}], 'payment': 100000.0}, 'calc_CD':[]}}

apply_date = '2016-07-20'   #保全申请日期
oldcertiCode = dict_manual['policy_info']['insured_info'][0]['insuCertiCode']

modify_info_dict = {
                'roleType': '2',   #角色类型:1-投保人；2-被保人；3-受益人；4-代理人（保单无对应角色，默认为被保人）
                'oldcertiCode': oldcertiCode,  #待变更的客户证件号码
                'gender': {'is_modify':'Y', 'new':'0'},    #性别:0-男，1-女
                'birthday': {'is_modify':'Y', 'new':'1980-10-10'},     #出生日期
                'certiType': {'is_modify':'Y', 'new':'2'},     #证件类型
                'certiCode': {'is_modify':'Y', 'new':'11010116102170137'},     #证件号码
                'jobCateId': {'is_modify':'Y', 'new':'0001001'},     #职业代码/名称
                'income': {'is_modify':'Y', 'new':'100'},     #个人年收入（万元）
                'familyIncome': {'is_modify':'Y', 'new':'100'},    #家庭年收入（万元）
                'incomeSource': {'is_modify':'Y', 'new':'01'},    #收入来源
                'incomeSourceNote': {'is_modify':'Y', 'new':'haha'},    #收入来源备注
                'companyName': {'is_modify':'Y', 'new':'renrenwang'}    #工作单位
            }


dict_manual = calc_API0009().calc_CD(apply_date, modify_info_dict, dict_manual)
print dict_manual
"""


