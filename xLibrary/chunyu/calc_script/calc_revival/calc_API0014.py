#coding=utf-8

import sys
import traceback
reload(sys);
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *


"""手工-续期不收费失效"""
class calc_API0014:

    def __init__(self):
        pass

    def calc_revival(self, apply_date, scsRevivalInterestFree_flag, changeDetailModel_flag, dict_manual):
        try:
            #初始化
            is_success = True
            message = ''
            unit = '手工计算-保单复效:'
            payment = 0   #收付费金额
            pa_name = 'revival'   #保全代码
            product = []   
            revival_product_list = []   #定义复效产品列表
            #获取dict数据
            effectiveDate = dict_manual['policy_info']['effectiveDate']   #生效日期
            all_product_list = dict_manual['policy_info']['main_risk_info'] + dict_manual['policy_info']['sub_risk_info']   #组装保单产品列表
            #print all_product_list
            #组装复效产品列表
            for i in range(0,len(all_product_list)):
                if all_product_list[i]['liability_state'] == '02':
                    revival_product_list.append(all_product_list[i])

            for i in range (0,len(revival_product_list)):
                productCode = revival_product_list[i]['productCode']   #产品代码
                loanRate = float(API0000_diy().query_product_revival_rate(productCode))   #产品贷款、复效利率
                #print 'loanRate:' + str(loanRate)
                #计算宽限期止期
                pay_due_date = revival_product_list[i]['pay_due_date']   #险种下期应缴日
                #print 'pay_due_date:' + str(pay_due_date)
                policy_years = API0000_diy().calc_policy_years(effectiveDate , pay_due_date, apply_date)   #计算保单申请日期所处的保单年度
                policy_years = int(policy_years) + 1  #模拟保单已续期时的保单年度
                #print 'policy_years:' + str(policy_years)
                policy_anniversary = API0000_diy().calc_policy_anniversary(effectiveDate, policy_years)   #计算保单周年日
                #print 'policy_anniversary:' + str(policy_anniversary)
                grace_period_end_day = API0000_diy().date_add_subtract(policy_anniversary, 60)
                #print 'grace_period_end_day:' + str(grace_period_end_day)
                #计算复效计算利息天数  
                days_revival = float(API0000_diy().cals_different_days(apply_date, grace_period_end_day))
                #print 'days_revival:' + str(days_revival)
                #欠缴保费金额
                revivalAmount = float(revival_product_list[i]['stdPremBf'])
                #print 'revivalAmount:' + str(revivalAmount)
                #复效应收利息
                revivalInterestAmount = round(revivalAmount * loanRate * days_revival / float(365), 2)
                #保单贷款本金
                loanBalance = 0
                #保单贷款利息  
                loanInterest = 0
                #保单自垫本金  
                zidianAmount = 0
                #保单自垫利息  
                zidianInterestAmount = 0
                #加费金额  
                extraPrem = 0
                product.append({'productCode':productCode, 'revivalAmount':revivalAmount, 'revivalInterestAmount':revivalInterestAmount, 'loanBalance':loanBalance,'loanInterest':loanInterest, 'zidianAmount':zidianAmount, 'zidianInterestAmount':zidianInterestAmount, 'extraPrem':extraPrem})
                payment = payment + revivalAmount + revivalInterestAmount + loanBalance + loanInterest + zidianAmount + zidianInterestAmount + extraPrem
            #定义检查点信息
            calc_revival = {'apply_date':apply_date, 'product':product, 'payment':payment, 'msg': ''}   #定义每期续期的续期信息
            dict_manual['check']['calc_revival'].append(calc_revival) 
            #定义轨迹信息
            track_info = {'trackType':'revival', 'trackTime':apply_date, 'trackData':{'product':product, 'payment':payment}, 'msg': ''}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息
            #改变dict-保单、险种状态
            dict_manual['policy_info']['policy_status'] = '01'   #保单状态
            dict_manual['policy_info']['invalid_reason'] = ''   #失效原因
            for j in range(0, len(dict_manual['policy_info']['main_risk_info'])):
                dict_manual['policy_info']['main_risk_info'][j]['liability_state'] = '01'   #主险有效
            for j in range(0, len(dict_manual['policy_info']['sub_risk_info'])):
                dict_manual['policy_info']['sub_risk_info'][j]['liability_state'] = '01'   #附加险有效
            assert is_success == True
            assert dict_manual['logInfo']['code'] == '1'
        except Exception, e:
            is_success = False
            dict_manual['logInfo']['code'] = 0
            dict_manual['logInfo']['err'] = unit + str(e)
            calc_revival = {'apply_date':apply_date, 'product':'', 'payment':payment, 'msg': message}   #定义每期续期的续期信息
            dict_manual['check']['calc_revival'].append(calc_revival)  
            track_info = {'trackType':'revival', 'trackTime':apply_date, 'trackData':{'product':'', 'payment':payment}, 'msg': message}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息
            print '---err------'
            traceback.print_exc()
            print dict_manual
            exit()
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict_manual = API0000_diy().result(dict_manual, is_success, message, unit)
        return dict_manual

