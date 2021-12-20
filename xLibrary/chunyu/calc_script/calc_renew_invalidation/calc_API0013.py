#coding=utf-8
import os
import sys
import xlrd
from xLibrary.chunyu.API0000 import API0000_diy

reload(sys);
sys.setdefaultencoding("utf8")

"""手工-续期不收费失效"""
class calc_API0013:

    def __init__(self):
        pass

    def calc_renew_invalidation(self, pay_due_date, dict_manual):
        try:
            #初始化
            calc_renew = {}
            #存入检查点信息
            calc_renew['apply_date'] = pay_due_date[0:10]   #新契约收费金额
            calc_renew['payment'] = 0   #新契约收费金额
            calc_renew['msg'] = ''   #新契约收费金额
            dict_manual['check']['calc_renew'].append(calc_renew)
            #定义轨迹信息
            track_info = {'trackType':'renew', 'trackTime':pay_due_date[0:10], 'trackData':{'payment': 0}, 'msg': ''}
            dict_manual['track_info'].append(track_info)   #存入轨迹信息
            #改变dict-保单、险种状态
            dict_manual['policy_info']['policy_status'] = '02'   #保单状态
            dict_manual['policy_info']['invalid_reason'] = '失效'   #失效原因
            for j in range(0, len(dict_manual['policy_info']['main_risk_info'])):
                dict_manual['policy_info']['main_risk_info'][j]['liability_state'] = '02'   #主险中止
            for j in range(0, len(dict_manual['policy_info']['sub_risk_info'])):
                dict_manual['policy_info']['sub_risk_info'][j]['liability_state'] = '02'   #附加险中止
        except Exception, e:
            print 'err'
        finally:
            print 'calc_API0013-success'
        return dict_manual

