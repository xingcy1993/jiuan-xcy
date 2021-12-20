# coding=utf-8

import os
import sys
import math
import xlrd
import datetime
import traceback
reload(sys);
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *
from xLibrary.chunyu.calc_script.calc_loan.calc_API0006 import calc_API0006



"""手工计算贷款还款：
    入参：还款日期、dict_manual
    step1:计算还款信息列表
          1.获取贷款待还款列表：
            （1）贷款待还款列表长度为0时：还款信息列表为空
            （2）贷款列表长度>0时,获取最后一次还款在贷款列表中的下标（默认为-1）：
                ①最后一次还款在贷款列表中的下标=贷款列表长度-1，无贷款待还款记录：还款信息列表为空
                ②还款下标=-1，无还款记录。截取待还款的贷款列表
                ③还款下标不等于-1、贷款列表长度-1时，截取待还款的贷款列表
          2.遍历待还款列表，针对每个待还款记录操作如下：
            （1）获取贷款起期
            （2）获取贷款止期
            （3）计算贷款已过日期
            （4）计算贷款6个月的天数
            （5）遍历得到贷款时产品的现价和
            （6）遍历贷款的产品列表：
                ①获取实际贷款金额、产品贷款时的现价、产品贷款利率
                ②计算产品贷款本金：现价/总现价*实际贷款金额
                ③计算产品还款时现价
                ④计算还款利息：
                    ⅰ：还款日期<=贷款日期6个月：计算贷款利息、贷款本息和
                    ⅱ：还款日期>贷款日期6个月：计算资本化利息、未结利息、产品贷款本息和
                ⑤组装每个待还款的产品列表：产品代码、现金价值、贷款利率、贷款本金、资本化利息、未结利息、贷款合计
            （7）计算还款总金额：各产品贷款合计之和
          3.组装还款信息列表：每个贷款的申请日期、贷款还款产品列表
    step2:组装贷款还款列表：贷款类型-还款、还款日期、还款信息列表、还款总金额
    step3: 手工计算检查点存入dict_manual
    出参：dict_manual
"""

class calc_API0007:

    def __init__(self):
        pass
        
    def calc_loan_repayment(self, apply_date, dict_manual):
        try:
            #初始化
            is_success = True
            message = ''
            unit = '手工计算-贷款还款:'
            repayment_list = []   #定义贷款险种欠款列表默认为[]
            list = []   #定义未还款的贷款列表默认为[]
            index = -1   #定义最后一次还款在贷款列表中的下标默认为-1
            payment = 0   #还款金额
            #获取dict数据
            product_list = dict_manual['policy_info']['main_risk_info'] + dict_manual['policy_info']['sub_risk_info']   #组装保单产品列表
            total_times_renew = dict_manual['public']['total_times_renew']   #已续期次数
            effectiveDate = dict_manual['policy_info']['effectiveDate']   #生效日期
            callBackDate = dict_manual['policy_info']['callBackDate']   #回执日期
            policy_status = dict_manual['policy_info']['policy_status']   #保单状态
            end_reason = dict_manual['policy_info']['end_reason']   #终止原因
            insuBirth = dict_manual['policy_info']['insured_info'][0]['insuBirth']   #被保人生日
            #调用保全通用规则
            pa_name = 'loan_repayment'
            rs = API0000_diy().pa_general_rules(pa_name, apply_date, dict_manual)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            """step1:计算还款信息列表"""
            #1.获取贷款待还款列表：
                #（1）贷款待还款列表长度为0时：还款信息列表为空
            if len(dict_manual['check']['calc_loan']) == 0:
                repayment_list = []
                #（2）贷款列表长度>0时,获取最后一次还款在贷款列表中的下标（默认为-1）
            elif len(dict_manual['check']['calc_loan']) > 0:
                for i in range(len(dict_manual['check']['calc_loan'])-1, -1, -1):
                    if dict_manual['check']['calc_loan'][i]['loan_type'] == 'loan_repayment':
                        index = i   #得到最后一次还款在贷款列表中的下标index
                        break
                    #①最后一次还款在贷款列表中的下标=贷款列表长度-1，无贷款待还款记录：还款信息列表为空
                if index == (len(dict_manual['check']['calc_loan'])-1):
                    repayment_list = []
                    #②还款下标=-1，无还款记录。截取待还款的贷款列表
                elif index == -1:
                    list = dict_manual['check']['calc_loan']
                elif index != -1:
                    #③还款下标不等于-1、贷款列表长度-1时，截取待还款的贷款列表
                    list = dict_manual['check']['calc_loan'][int(index+1):int(len(dict_manual['check']['calc_loan'])+1)]
                #调用贷款还款保全项规则
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
                #保单项下无贷款阻断
            if list == []:
                message = '保单项下无贷款'
                is_success = False
            assert is_success == True
            #2.遍历待还款列表，针对每个待还款记录操作如下
            for j in range(0,len(list)):
                product_list = []   #定义产品列表 
            #（1）获取贷款起期
                loan_begin_date = list[j]['apply_date']
                #print 'loan_begin_date:' + str(loan_begin_date)
            #（2）计算贷款已过日期
                loan_passed_days = (datetime.datetime.strptime(apply_date, '%Y-%m-%d') - datetime.datetime.strptime(loan_begin_date, '%Y-%m-%d')).days
                #print 'loan_passed_days:' + str(loan_passed_days)
            #（3）计算贷款第一个6个月的贷款止期
                year = loan_begin_date[0:4]   #年
                month = loan_begin_date[5:7]   #月
                day = loan_begin_date[8:10]   #日
                if (int(month) + 6)>12:
                    year = str(int(year) + 1)
                    month = str(int(month) + 6 - 12)
                    if len(month) == 1:
                        month = '0' + month
                    day = day
                else:
                    year = year
                    month = str(int(month) + 6)
                    if len(month) == 1:
                        month = '0' + month
                    day = day
                loan_begin_end1 = year + '-' + month + '-' + day
                if API0000_diy().isvaild_date(loan_begin_end1):
                    #日期有效：下期应缴日 = 下期应缴日字符串
                    loan_begin_end1 = loan_begin_end1
                else:
                    #日期有效：下期应缴日 = （下期应缴日字符串年份） 拼接 （02-28）
                    loan_begin_end1 = loan_begin_end1[0:4] + '-03-01'
                #print 'loan_begin_end1:' + str(loan_begin_end1)
            #（4）计算贷款第一个6个月的天数
                loan_days1 = (datetime.datetime.strptime(loan_begin_end1, '%Y-%m-%d') - datetime.datetime.strptime(loan_begin_date, '%Y-%m-%d')).days
                #print 'loan_days:' + str(loan_days)
            #（5）遍历得到贷款时产品的现价和
                total_presentPrice = 0   #每次贷款各产品的总现价和
                for i in range(0,len(list[j]['product'])):
                    total_presentPrice = total_presentPrice + round(float(list[j]['product'][i]['presentPrice']), 2)
                    #print round(float(list[j]['product'][i]['presentPrice']), 2)
                #print total_presentPrice
                #print "len(list[j]['product']):" + str(len(list[j]['product']))
            #（6）遍历贷款的产品列表：
                for i in range(0,len(list[j]['product'])):
                    productCode = list[j]['product'][i]['productCode']   #产品代码
                    #①获取实际贷款金额、产品贷款时的现价、产品贷款利率
                    payment1 = round(float(list[j]['payment']), 2)   #每次贷款的实际贷款金额 
                    presentPrice_each_loan = round(float(list[j]['product'][i]['presentPrice']), 2)   #每次贷款时产品现价
                    #loanRate = float(list[j]['product'][i]['loanRate'])   #产品贷款利率
                    #②计算产品贷款本金：现价/总现价*实际贷款金额
                    if total_presentPrice == 0:
                        product_loan_prin = 0
                    else:
                        product_loan_prin = round(presentPrice_each_loan/total_presentPrice*payment1, 2)    #计算产品贷款本金
                    #print 'product_loan_prin:' + str(product_loan_prin)
                    #③计算产品还款时现价
                    FA = float(list[j]['product'][i]['stdPremBf'])   #FA
                    loanRate = float(API0000_diy().query_product_loan_rate(list[j]['product'][i]['productCode'], loan_begin_date))
                        
                    #1.计算现金价值
                    presentPrice = float(API0000_diy().calc_present(dict_manual, apply_date))   #计算现价
                    #④计算还款利息：
                        #ⅰ：还款日期<贷款日期6个月：计算贷款利息、贷款本息和
                    if int(loan_passed_days)<int(loan_days1):
                        interestCapital = 0   #定义资本化利息为0
                        if productCode in ('1205','1206','3208','3211','5207','5206','3209','5201','5202','5211','5242','5225','5241','8204','5213','3213','8211','8212','8213','8214','5214','8216','8217','3245','3249','3247','3248','3243','3247B','3255','3256','3257CA','3258','3257','3264','3265','3267','3267CO','3265CB','3270','3267CB','8233','8237','8233CA1','3257CA1','8237CA1'):
                            loan_interest = round(product_loan_prin *(math.pow(1+loanRate, float(loan_passed_days)/float(365))-1), 2)
                        else:
                            loan_interest = round((product_loan_prin*loanRate*loan_passed_days/float(365)), 2)#计算贷款利息
                        #print 'loan_interest:' + str(loan_interest)
                        principalInterest = round(product_loan_prin + interestCapital + loan_interest, 2)    #贷款本息和
                        #ⅱ：还款日期>贷款日期6个月：计算资本化利息、未结利息、产品贷款本息和
                    else:
                        #计算资本化利息
                        interestCapital = 0   #初始化资本化利息
                        for k in range(0,1000):
                            loanRate = float(API0000_diy().query_product_loan_rate(list[j]['product'][i]['productCode'], loan_begin_date))
                            #print k
                            #j:计算本次贷款每隔6个月的贷款止期
                            year = loan_begin_date[0:4]   #年
                            month = loan_begin_date[5:7]   #月
                            day = loan_begin_date[8:10]   #日
                            if (int(month) + 6)>12:
                                year = str(int(year) + 1)
                                month = str(int(month) + 6 - 12)
                                if len(month) == 1:
                                    month = '0' + month
                                day = day
                            else:
                                year = year
                                month = str(int(month) + 6)
                                if len(month) == 1:
                                    month = '0' + month
                                day = day
                            loan_begin_end = year + '-' + month + '-' + day
                            if API0000_diy().isvaild_date(loan_begin_end):
                                #日期有效：下期应缴日 = 下期应缴日字符串
                                loan_begin_end = loan_begin_end
                            else:
                                #日期有效：下期应缴日 = （下期应缴日字符串年份） 拼接 （02-28）
                                loan_begin_end = loan_begin_end[0:4] + '-03-01'
                            #print 'loan_begin_end:' + str(loan_begin_end)
                            
                            #jj:计算本次贷款每6个月的贷款天数
                            loan_days = (datetime.datetime.strptime(loan_begin_end, '%Y-%m-%d') - datetime.datetime.strptime(loan_begin_date, '%Y-%m-%d')).days
                            #print 'loan_days:' + str(loan_days)
                            #iii:计算本次贷款每6个月资本化利息，并合计
                            if int(loan_passed_days)>=int(loan_days):
                                #计算本次贷款每6个月的资本化利息
                                if productCode in ('1205','1206','3208','3211','5207','5206','3209','5201','5202','5211','5242','5225','5241','8204','5213','3213','8211','8212','8213','8214','5214','8216','8217','3245','3249','3247','3248','3243','3247B','3255','3256','3257CA','3258','3257','3264','3265','3267','3267CO','3265CB','3270','3267CB','8233','8237','8233CA1','3257CA1','8237CA1'):
                                    interestCapital = round(interestCapital + round((product_loan_prin + interestCapital) *(math.pow(1+loanRate, float(loan_days)/float(365))-1), 2), 2)
                                else:
                                    interestCapital = round((interestCapital + round(((product_loan_prin + interestCapital) * loanRate * loan_days/float(365)), 2)), 2)
                                #重新计算贷款剩余天数
                                loan_passed_days = int(loan_passed_days) - int(loan_days)
                                #重新计算6个月的贷款起期
                                #loan_begin_date = API0000_diy().date_add_subtract(loan_begin_end, 1)
                                loan_begin_date = loan_begin_end
                            else:
                                break
                            #print interestCapital
                        if productCode in ('1205','1206','3208','3211','5207','5206','3209','5201','5202','5211','5242','5225','5241','8204','5213','3213','8211','8212','8213','8214','5214','8216','8217','3245','3249','3247','3248','3243','3247B','3255','3256','3257CA','3258','3257','3264','3265','3267','3267CO','3265CB','3270','3267CB','8233','8237','8233CA1','3257CA1','8237CA1'):
                            loan_interest = round((product_loan_prin+interestCapital) *(math.pow(1+loanRate, float(loan_passed_days)/float(365))-1), 2)
                        else:
                            loan_interest = round(((product_loan_prin+interestCapital)*loanRate*int(loan_passed_days)/float(365)), 2)   #未结利息
                        #print 'loan_interest:' + str(loan_interest)
                        principalInterest = round(product_loan_prin + interestCapital + loan_interest, 2)    #险种贷款合计
                    #⑤组装每个待还款的产品列表：产品代码、现金价值、贷款利率、贷款本金、资本化利息、未结利息、贷款合计
                    product = {'productCode':list[j]['product'][i]['productCode'], 'presentPrice': presentPrice, 'loanRate': loanRate, 'loanPrincipal':product_loan_prin, 'interestCapital':interestCapital, 'loanInterest':loan_interest, 'principalInterest':principalInterest}
                    product_list.append(product)
            #（7）计算还款总金额：各产品贷款合计之和
                    payment = round((payment + principalInterest), 2)
        #3.组装还款信息列表：每个贷款的申请日期、贷款还款产品列表                      
                repayment_list.append({'startDate':list[j]['apply_date'], 'product': product_list})
                """step2:组装还款列表：贷款类型-还款、还款日期、还款信息列表、还款总金额""" 
            calc_loan = {'loan_type':'loan_repayment', 'apply_date':apply_date, 'repayment_list':repayment_list, 'payment':payment, 'msg': ''} 
            """step3: 手工计算检查点存入dict_manual"""
            dict_manual['check']['calc_loan'].append(calc_loan)
            """step4: 手工计算轨迹信息存入dict_manual"""
            #定义轨迹信息
            track_info = {'trackType':'loan_repayment', 'trackTime':apply_date, 'trackData':{'repayment_list':repayment_list, 'payment':payment}, 'msg': ''}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息
            assert is_success == True
            assert dict_manual['logInfo']['code'] == '1'
        except Exception, e:
            is_success = False
            dict_manual['logInfo']['code'] = 0
            dict_manual['logInfo']['err'] = unit + str(e)
            calc_loan = {'loan_type':'loan_repayment', 'apply_date':apply_date, 'repayment_list':'', 'payment':payment, 'msg': message} 
            dict_manual['check']['calc_loan'].append(calc_loan)
            track_info = {'trackType':'loan_repayment', 'trackTime':apply_date, 'trackData':{'repayment_list':'', 'payment':payment}, 'msg': message}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息
            print '---err------'
            traceback.print_exc()
            print dict_manual
            exit()
        finally:
            # 加入阻断及错误信息。存入dict_manual['result']中
            dict_manual = API0000_diy().result(dict_manual, is_success, message, unit)        
        return dict_manual

