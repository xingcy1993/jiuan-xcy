#coding=utf-8

import sys
import json
import time
import urllib
import logging
import pymysql
import requests
import traceback
import paramiko
from datetime import datetime
from func_timeout import func_set_timeout
import func_timeout
reload(sys);
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002



"""续期+收费（支持多期续期）：
    step1:续期前准备
        1.验证用户登录系统 
        2.获取保单最大续期年数
        3.续期前判断保单是否满足续期条件
    step2:续期遍历
        1.执行每期的续期
        2.每期续期收费
        3.定义轨迹信息+检查点信息
"""
class sys_API0004:

    def __init__(self):
        pass


    def renew(self, times_renew, dict):
        """续期：
                step1:续期前准备
                step2:续期遍历
        """
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            pay_due_date = 'xxxx-xx-xx'   #初始化下期应交日
            first_year = ''   #初始化第一期下期应缴日
            payment = 0   #初始化收付费金额
            space_times = 0   #日志打印空格次数
            if dict['logInfo']['job'][0:14] == 'complex_scenes':   #复杂场景
                space_times = 2
            else:
                space_times = 0
            dict['public']['space_times'] = space_times
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '保单续期_开始'))
            #多期续期操作
            for times in range(0,int(times_renew)):
                begin_time = datetime.datetime.now()   #开始时间
                #记录日志
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*第%s期续期开始(预计耗时:180s)' % str(times+1)))
                try:
                    if times == 0:
                        """step1:续期前准备"""
                        #调用脚本
                        rs = sys_API0004().prepare_renew(times, dict)
                        #断言
                        assert dict['logInfo']['code'] == '1'   #断言是否异常标识
                        #存入dict
                        maxyears_renew = rs[0]   #获取数据库查询的保单最大续期次数
                        dict = rs[1]   #获取dict
                        dict['public']['maxyears_renew'] = maxyears_renew
                        """step2:续期遍历"""
                    if maxyears_renew == 0:   #数据库查询保单最大续期次数为0时：
                        #存入dict
                        dict['logInfo']['code'] = '0'    #记录异常标识
                        dict['logInfo']['msg'] = '经查询，保单最大续期次数为0!'    #记录信息
                        break    #跳出循环
                    elif maxyears_renew == times and maxyears_renew != 0:   #若已续期的次数达到了最大续期年龄，跳出for循环
                        break    #跳出循环
                    else:   #最大续期次数不为0，且已续期的次数未达到最大续期年龄时
                        #1.执行每期的续期
                        rs = sys_API0004().execute_each_renew(times, first_year, times_renew, maxyears_renew, dict)
                        assert dict['logInfo']['code'] == '1'
                        pay_due_date = rs[0]
                        first_year = rs[1]
                        dict = rs[2]
                        #2.每期续期收费
                        rs = sys_API0004().pay_each_renew(times, maxyears_renew, pay_due_date, dict)
                        assert dict['logInfo']['code'] == '1'
                        dict = rs[0]
                        payment = rs[1]   #收费费金额
                    #每期续期结束
                    end_time = datetime.datetime.now()   #结束时间
                    #记录日志
                    logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*第%s期续期结束(实际耗时:%s)' % (str(times+1),API0000_diy().logger_count_time(begin_time, end_time))))
                except Exception, e:
                    dict['logInfo']['code'] = '0'
                    #记录异常日志
                    logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '异常位置:\n')  + traceback.format_exc())
                except func_timeout.exceptions.FunctionTimedOut:
                    #记录执行时间超时日志
                    logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*执行时间超时退出'))
                    dict['logInfo']['code'] = '0'
                    dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
                    #异常场景-登出系统（防止与用户被挂起）
                    if dict['public']['magicX'] != '':
                        API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*运行异常-用户解锁'))
                        dict['public']['magicX'] = ''
                finally:
                    assert dict['logInfo']['code'] == '1'
                    #3.定义轨迹信息+检查点信息
                    dict = sys_API0004().save_check_info(dict, pay_due_date, payment)
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '保单续期_结束'))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '异常位置:\n')  + traceback.format_exc())
        finally:
            pass
        return dict


    @func_set_timeout(30)#设定函数超执行时间    
    def prepare_renew(self, times, dict):
        """续期前准备:
            step1:验证用户登录系统 
            step2:获取保单最大续期年数
            step3:续期前判断保单是否满足续期条件
        """
        try:
            #初始化
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp*验证用户是否可成功登录系统+数据库查询保单最大续期年数_开始'))
            """step1:验证用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-续期_验证用户登录系统'  # 节点
            message = ''
            maxyears_renew = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            username_entry = dict['public']['username_entry']   #登录系统用户名
            interface_ip = dict['public']['interface_ip']   #接口ip
            #验证用户是否可正常登录系统
            rs = API0000_diy().verify_userlogin(env_name, username_entry, interface_ip)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            """step2:获取保单最大续期年数"""
            #节点初始化
            is_success = ''
            unit = '系统-续期_获取保单最大续期年数'  # 节点
            message = ''
            #dict获取数据+定义数据
            policyNo = dict['policy_info']['policyNo']   #保单号
            sql = "select b.effective_date,b.pay_due_date,b.pay_year from t_pa_policy a,t_pa_policy_product b where a.policy_id=b.policy_id and a.POLICY_NO='" + policyNo + "' and YEAR(b.pay_due_date) not like '%9999%' and b.liability_state='01'"
            #调用原子脚本
            unit = '系统-续期_获取保单最大续期年数_连接数据库'
            cursor = API0000_diy().db_conf(env_name,'wift_pa')
            #查询保单的生效日期、下期应缴日、缴费期间
            unit = '系统-续期_获取保单最大续期年数_数据库查询保单生效日期、下期应缴日、缴费期间'
            cursor.execute(sql)
            result = cursor.fetchall()
            #定义险种剩余交费年限列表
            unit = '系统-续期_获取保单最大续期年数'
            list = []
            for i in range(0,len(result)):
                effective_date = result[i][0]   #生效日期
                pay_due_date = result[i][1]   #下期应缴日
                pay_year = result[i][2]    #缴费期间
                effective_date_year = effective_date.strftime('%Y')   #生效日期所在年
                pay_due_date_year = pay_due_date.strftime('%Y')   #下期应缴日所在年            
                surplus_renew_years = int(effective_date_year) + int(pay_year) - int(pay_due_date_year)    #剩余续期年数
                if len(list) == 0:
                    list.append(surplus_renew_years)
                elif len(list) > 0:
                    if surplus_renew_years > list[-1]:  #遍历保单全部险种，若当前险种的剩余续期年数大于list列表中的最后一个值（即最大值），进行追加
                        list.append(surplus_renew_years)
            #写入dict
            if len(list) == 0:
                maxyears_renew = 0   #最大续期年数
                message = '续期不成功。查询出最大续期年数为0'
            elif len(list) > 0:
                maxyears_renew = list[-1]   #最大续期年数
                message = ''
            is_success = True
            """step3:续期前判断保单是否满足续期条件"""
            #节点初始化 
            #is_success = ''
            #unit = '系统-续期_每期续期前判断保单是否满足续期条件'  # 节点
            #message = ''
            #dict获取数据+定义数据
            #sql = "SELECT DISTINCT t.LIST_ID,t.POLICY_ID,t.ITEM_ID,t.PRODUCT_ID,t.LIAB_ID,t.PREM_STATUS,t.FEE_AMOUNT,t.RENEW_CONFIRM_AMOUNT,t.ARAP_TIME,t.FEE_TIME,t.PREM_TERM, t.PREM_TYPE,t.PARTITION_INDI,t.PRE_DUE_TIME,t.REISSUE_EXPIRY_DATE,p.suspend_reason,p.SUSPEND,p.POLICY_NO,p.PROPOSAL_NO,p.effective_Date POLICY_EFT_DATE,h.HOLDER_CUST_ID,pro.EFFECTIVE_DATE,pro.APPLICATION_DATE,pro.pay_Freq,pro.PAY_PERIOD,pro.PAY_YEAR,pro.COVERAGE_PERIOD,pro.COVER_PERIOD_TYPE,pro.TOTAL_PREM_AF,pro.SUM_ASSURED,pro.DISCNTED_RATE,pro.EXTRA_PREM_AF,pro.STD_PREM_AF,pro.EXTRA_STD_PREM_BF,pro.UNITS,c.JOB_CATE_ID,c.GENDER,c.BIRTHDAY,i.APPLICANT_AGE,pl.BONUS_YEAR_OR_AGE,pl.PAY_PLAN_TYPE,p.SUBMIT_CHANNEL,p.SUB_SALES_CHANNEL,p.ORGAN_ID,ch.NAME hdName,ch.CERTI_TYPE hdCertiType,ch.CERTI_CODE hdCertiCode,ch.mobile holderMobile,(case when (t.PRE_DUE_TIME BETWEEN pp.WAIVER_START AND pp.WAIVER_END) then 'Y' else 'N' end) IS_WAIVER,(case when pro.MAIN_ITEM_ID is null then 'Y' else 'N' end) is_main_item FROM t_pa_renew_preprem t,(select lpn.* from t_pa_policy_change gn,t_pa_policy_product_log lpn,(SELECT max(g.CHANGE_RECORD) CHANGE_RECORD,lp.policy_id,lp.ITEM_ID FROM t_pa_policy_change g,t_pa_policy_product_log lp WHERE lp.POLICY_ID = g.policy_id and lp.CHANGE_ID = g.CHANGE_ID and lp.LIABILITY_STATE != '03' and ((g.STATUES <> '19' and g.SERVICE_ID = '90051') or g.SERVICE_ID <> '90051') group by lp.policy_id,lp.ITEM_ID) vi where gn.policy_id = vi.policy_id and gn.CHANGE_RECORD = vi.CHANGE_RECORD and lpn.CHANGE_ID = gn.CHANGE_ID and lpn.POLICY_ID = gn.policy_id and vi.ITEM_ID = lpn.ITEM_ID ) pro,t_pa_policy_insured i,t_pa_customer_party pt,t_pa_customer_party pth,t_pa_policy_holder h,t_pa_policy_product pp,t_pa_customer c,t_pa_customer ch, t_pa_policy p LEFT JOIN t_pa_pay_plan pl ON (p.POLICY_NO = pl.POLICY_NO AND pl.PAY_ACCOUNT_TYPE='4') WHERE t.POLICY_ID = pro.POLICY_ID and t.ITEM_ID = pro.ITEM_ID and p.POLICY_ID = pro.policy_id and p.policy_id = pp.policy_id and pro.INSURANT_ID = i.INSURED_CUST_ID and i.KEY_ID = pt.busi_relate_id and pt.customer_id= c.CUSTOMER_ID and p.policy_id= c.policy_id and pt.policy_id = p.policy_id and pt.customer_role_type='2' and h.KEY_ID = pth.busi_relate_id and pth.CUSTOMER_ID = ch.CUSTOMER_ID and p.policy_id= ch.policy_id and pth.policy_id = p.policy_id and pth.customer_role_type='1' and h.policy_id = p.policy_id and p.policy_id = t.policy_id and p.policy_id = i.policy_id AND t.PREM_STATUS in ('0','1') and p.POLICY_STATUS = '01' and pro.LIABILITY_STATE = '01' and pp.LIABILITY_STATE = '01' and p.POLICY_NO='" + policyNo + "' AND (DATE_FORMAT(pp.PAY_DUE_DATE,'%Y-%m-%d') <= t.PRE_DUE_TIME or DATE_FORMAT(pp.PAY_DUE_DATE,'%Y-%m-%d') = '9999-01-01') and pro.product_id = pp.PRODUCT_ID and pro.product_id = t.PRODUCT_ID AND NOT EXISTS (SELECT 1 FROM t_pa_renew_reverse_trans trs where trs.policy_id = p.POLICY_ID AND ((trs.pay_due_date = t.PRE_DUE_TIME AND t.PREM_TYPE = '1') OR (trs.pay_due_date = t.REISSUE_EXPIRY_DATE AND t.PREM_TYPE = '2')) AND (trs.bak2 IS NULL OR trs.bak2 LIKE CONCAT('%,', t.PRODUCT_ID ,',%')) ORDER BY trs.UPDATE_TIME DESC LIMIT 1); "
            #调用原子脚本
            #cursor.execute(sql)
            #result = cursor.fetchall()
            #if len(result) > 0:
                #can_renew = True
                #is_success = True
            #else:
                #can_renew = False  
                #is_success = False
                #message = '第'+ str(i+1) +'期续期，保单不满足续期条件'
            dict['logInfo']['code'] = '1'
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp*验证用户是否可成功登录系统+数据库查询保单最大续期年数_结束'))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return maxyears_renew, dict   



    @func_set_timeout(300)#设定函数超执行时间    
    def execute_each_renew(self, times, first_year, times_renew, maxyears_renew, dict):
        """执行每期的续期:
            step1:获取保单下期应缴日
            step2:修改服务器时间
            step3:启动续期批处理
            step4:等待+判断保单续期批处理是否跑成功
            step5:关闭批处理
        """
        try:
            #初始化  
            magicX = ''   #初始化会话id
            job = dict['logInfo']['job']   #场景名
            dict['logInfo']['code'] = '0'   #初始化异常标识 
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            """step1:获取保单下期应缴日"""
            #节点初始化
            is_success = ''    #初始化是否成功标识
            unit = '系统-续期_第' + str(times+1) + '期获取保单下期应缴日'  # 节点
            message = ''    #初始化信息
            pay_due_date = ''    #初始化下期应缴日
            list = []    #初始化数据库查询保单险种下期应缴日列表
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            policyNo = dict['policy_info']['policyNo']   #保单号
            sql = "select b.pay_due_date from t_pa_policy a,t_pa_policy_product b where a.policy_id=b.policy_id and a.POLICY_NO='" + policyNo + "'"  
            #调用原子脚本 
            unit = '系统-续期_第' + str(times+1) + '期获取保单下期应缴日_连接数据库'   
            rs = API0000_diy().db_conf_update(env_name,'wift_pa')
            db = rs[0]
            cursor = rs[1]
            #第一次续期。获取第一次续期的下期应缴日pay_due_date；第一次续期下期应缴日所在年份first_year
            if times == 0:
                unit = '系统-续期_第' + str(times+1) + '期获取保单下期应缴日_数据库查询保单下期应缴日' 
                cursor.execute(sql)
                result = cursor.fetchall()
                for j in range(0,len(result)): 
                    pay_due_date = result[j][0].strftime('%Y-%m-%d %H:%M')
                    if (pay_due_date not in list) and pay_due_date[0:4] !='9999':
                        list.append(pay_due_date)
                if len(list) == 0:
                    is_success = False
                    pay_due_date = ''
                    message = '第'+ str(times+1) + '期续期，续期不成功。未获取到保单下期应缴日'
                elif len(list) == 1:
                    is_success = True
                    pay_due_date = list[0]
                    first_year = pay_due_date[0:4]
                elif len(list) > 1:
                    is_success = False
                    pay_due_date = ''
                    message = '续期不成功。保单下存在不同年份下期应缴日'
                #断言
                assert is_success == True 
            #非第一次续期
            elif times != 0:
                cursor.execute(sql)
                result = cursor.fetchall()
                #获取下期应缴日
                for j in range(0,len(result)): 
                    pay_due_date = result[j][0].strftime('%Y-%m-%d %H:%M')
                    if (pay_due_date not in list) and pay_due_date[0:4] !='9999':
                        list.append(pay_due_date)
                if len(list) == 0:
                    is_success = False
                    pay_due_date = ''
                    message = '第'+ str(times+1) + '期续期，续期不成功。未获取到保单下期应缴日'
                elif len(list) == 1:
                    is_success = True
                    pay_due_date = list[0]
                elif len(list) > 1:
                    is_success = False
                    pay_due_date = ''
                    message = '续期不成功。保单下存在不同年份下期应缴日'
                #断言
                assert is_success == True 
                #判断数据库下期应缴日是否更新
                for j in range(0,120):
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    #获取下期应缴日
                    for z in range(0,len(result)): 
                        pay_due_date = result[z][0].strftime('%Y-%m-%d %H:%M')
                        if (pay_due_date not in list) and pay_due_date[0:4] !='9999':
                            list.append(pay_due_date)
                    if len(list) == 0:
                        is_success = False
                        pay_due_date = ''
                        message = '第'+ str(times+1) + '期续期，续期不成功。未获取到保单下期应缴日'
                    elif len(list) == 1:
                        is_success = True
                        pay_due_date = list[0]
                    elif len(list) > 1:
                        is_success = False
                        pay_due_date = ''
                        message = '续期不成功。保单下存在不同年份下期应缴日'
                    if int(pay_due_date[0:4]) == (int(first_year) + times):
                        break
                    else:
                        time.sleep(1)
                #断言
                assert is_success == True 
            """step2:修改服务器时间"""
            dict = sys_API0002().Modify_servertime(pay_due_date, job, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            time.sleep(5)


            """step3:启动续期批处理"""
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp*跑续期批处理1001、1003_开始(预计耗时:60s)'))
            #节点初始化
            is_success = ''
            unit = '系统-续期_第' + str(times+1) + '期启动续期批处理'  # 节点
            message = ''
            """数据库启动续期批处理
            #调用原子脚本:
            rs = API0000_diy().db_conf_update(env_name,'wift_pa')
            sql = "UPDATE t_batch_job a SET a.IS_ENABLE='Y' WHERE a.`JOB_ID`='1001' OR a.job_id='1003';"
            rs[1].execute(sql)
            rs[0].commit()
            #判断续期批处理是否启动成功
            cursor = API0000_diy().db_conf(env_name,'wift_pa')        
            sql = "select IS_ENABLE from t_batch_job where JOB_ID='1001' OR job_id='1003';" 
            cursor.execute(sql)
            result = cursor.fetchall()     
            if result[0][0] == 'Y' and result[1][0] == 'Y':
                is_success = True
            else:
                is_success = False
                message = '第'+ str(times+1) + '期续期，续期不成功。续期批处理没有启动成功'
            """
            #0.登录系统接口
            #节点初始化
            is_success = ''
            unit = '系统-启动续期批处理_登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            policyNo = dict['policy_info']['policyNo']   #保单号
            username_entry = dict['public']['username_entry']    #续期登录用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username_entry, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2] 
            #断言  
            assert is_success == True
            dict['public']['magicX'] = magicX

            #跑续期批处理、等待+判断保单续期批处理是否跑成功
            for j in range(0,60):
                if j in (0,5,10):    #续期批处理遍历三次（解决跑不出来问题；每次遍历存在时间间隔，解决收费多条的异常场景）
                    #1.启动续期预收费用记录表接口
                    batchSystem = 'PA'
                    jobId = '1001'
                    isEnable = 'Y'
                    jobName = '续期预收费用记录表'   #批处理任务名称
                    jobName = urllib.quote(jobName)
                    response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
                    #获取所需响应值
                    if response['success'] == True and response['message'] == '[续期预收费用记录表]更新成功':
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '续期预收费用记录表批处理启动失败'
                    #断言
                    assert is_success == True
                    time.sleep(2)   #等待2s

                    #2.提交续期预收费用记录表接口
                    #dict获取数据+定义数据
                    policyNo = dict['policy_info']['policyNo']   #保单号
                    business_date = pay_due_date[0:10]
                    #调用原子脚本
                    response = API0000_pa().saveBatchSubmit(magicX, interface_ip, batchSystem, jobId, policyNo, business_date)
                    #获取所需响应值
                    if response['success'] == True:
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '续期预收费用记录表批处理提交失败'
                    # 加入断言
                    assert is_success == True 
                    time.sleep(2)   #等待2s

                    #3.启动续期预收费用记录表接口
                    batchSystem = 'PA'
                    jobId = '1003'
                    isEnable = 'Y'
                    jobName = '续期预收转应收'   #批处理任务名称
                    jobName = urllib.quote(jobName)
                    response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
                    #获取所需响应值
                    if response['success'] == True and response['message'] == '[续期预收转应收]更新成功':
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '续期预收转应收批处理启动失败'
                    #断言
                    assert is_success == True
                    time.sleep(2)   #等待2s

                    #4.提交续期预收费用记录表接口
                    #dict获取数据+定义数据
                    policyNo = dict['policy_info']['policyNo']   #保单号
                    business_date = pay_due_date[0:10]
                    #调用原子脚本
                    response = API0000_pa().saveBatchSubmit(magicX, interface_ip, batchSystem, jobId, policyNo, business_date)
                    #获取所需响应值
                    if response['success'] == True:
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '续期预收转应收批处理提交失败'
                    # 加入断言
                    assert is_success == True
                    time.sleep(2)   #等待2s

                """step4:等待+判断保单续期批处理是否跑成功"""
                #节点初始化
                is_success = ''
                unit = '系统-续期_第' + str(times+1) + '期等待+判断保单续期批处理是否跑成功'  # 节点
                message = ''
                #调用原子脚本:
                unit = '系统-续期_第' + str(times+1) + '期等待+判断保单续期批处理是否跑成功_连接数据库' 
                rs = API0000_diy().db_conf_update(env_name,'wift_pa')
                db = rs[0]
                cursor = rs[1]
                sql = "select b.ARAP_TIME from t_pa_policy a,t_pa_renew_preprem b where a.POLICY_ID=b.POLICY_ID and a.POLICY_NO=" + policyNo + " and PREM_STATUS='2';"        
                cursor.execute(sql)
                unit = '系统-续期_第' + str(times+1) + '期等待+判断保单续期批处理是否跑成功_数据库查询保单实缴日期' 
                result = cursor.fetchall()
                #判断数据库查询结果是否为空（续期批处理是否跑出）
                if len(result)==0:
                    is_success = False
                    message = '第' + str(times+1) + '期续期，续期不成功。保单续期批处理未跑出'
                    time.sleep(5)    #等待5s
                else:
                    date = result[0][0].strftime('%Y-%m-%d')    #获取查询sql得到的应缴日期
                    #判断数据库查询的下期应缴日pay_due_date与数据库查询的应缴日期ARAP_TIME，绝对值是否小于15天
                    if abs(API0000_diy().cals_different_days(pay_due_date[0:10], date)) <= 15:
                        is_success = True
                        break   #跳出循环
                db.close()    #关闭数据库连接
            # 加入断言
            assert is_success == True
            end_time = datetime.datetime.now()   #结束时间 
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp*跑续期批处理1001、1003_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))

            """step5:关闭批处理"""
            begin_time1 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp*关闭续期批处理1001、1003_开始(预计耗时:3s)'))
            #节点初始化
            is_success = ''
            unit = '系统-续期_第' + str(times+1) + '期关闭续期批处理'  # 节点
            message = ''
            #1.关闭续期预收费用记录表批处理接口
            batchSystem = 'PA'
            jobId = '1001'
            isEnable = 'N'
            jobName = '续期预收费用记录表'   #批处理任务名称
            jobName = urllib.quote(jobName)
            response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
            #获取所需响应值
            if response['success'] == True and response['message'] == '[续期预收费用记录表]更新成功':
                is_success = True
                message = ''
            else:
                is_success = False
                message = '续期预收转应收批处理关闭失败'
            #断言
            assert is_success == True

            #2.关闭续期预收费用记录表批处理接口
            batchSystem = 'PA'
            jobId = '1003'
            isEnable = 'N'
            jobName = '续期预收转应收'   #批处理任务名称
            jobName = urllib.quote(jobName)
            response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
            #获取所需响应值
            if response['success'] == True and response['message'] == '[续期预收转应收]更新成功':
                is_success = True
                message = ''
            else:
                is_success = False
                message = '续期预收转应收批处理关闭失败'
            #断言
            assert is_success == True

            #3.登出系统
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX,interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            assert is_success == True 
            dict['logInfo']['code'] = '1'
            dict['public']['magicX'] = ''
            end_time1 = datetime.datetime.now()   #结束时间 
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp*关闭续期批处理1001、1003_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time1, end_time1)))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['err'] = unit + ':' + str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                username_entry = dict['public']['username_entry']   #登录系统用户名
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username_entry)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return pay_due_date, first_year, dict         



    @func_set_timeout(150)#设定函数超执行时间 
    def pay_each_renew(self, times, maxyears_renew, pay_due_date, dict):
        """每期续期收费：
            step1:续期用户登录系统
            step2:BCP支付方式查询接口
            step3:BCP支付方式变更转进账单接口
            step4:柜面收付费查询接口
            step5:柜面收付费保存接口
            step6:柜面收付费审核接口
            step7:综合查询-查询按钮接口
            step8:# 综合查询-险种信息sheet_险种信息查询接口:判断此期续期是否成功
            step9:续期用户登出系统
        """
        try:
            #初始化
            magicX = ''
            dict['logInfo']['code'] = '0'
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            begin_time = datetime.datetime.now()   #开始时间     
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp*续期收费_开始(预计耗时:10s)'))    
            """step1:续期用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-续期_第' + str(times+1) + '期续期用户登录系统'  # 节点
            message = ''
            payment = 0
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            policyNo = dict['policy_info']['policyNo']   #保单号
            username_entry = dict['public']['username_entry']    #续期登录用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username_entry, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]       
            assert is_success == True

            """step2：BCP支付方式查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-续期_第' + str(times+1) + '期BCP支付方式查询接口'  # 节点
            message = ''
            #调用原子脚本
            time.sleep(1)
            for j in range(0, 60):
                response = API0000_payment().queryBankOffsetSum(magicX, interface_ip, policyNo)
                if response['resultData'] == []:
                    is_success = False
                    message = '运维-BCP支付方式变更查询接口，此保单未查询到“银行转账”支付方式的收付费记录。'
                    offsetSumId = ''
                    time.sleep(1)
                else:
                    is_success = True
                    message = ''
                    offsetSumId = response['resultData'][0]['offsetSumId']
                    break
            assert is_success == True
            
            """step3：BCP支付方式变更转进账单接口"""
            #节点初始化
            is_success = ''
            unit = '系统-续期_第' + str(times+1) + '期BCP支付方式变更转进账单接口'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_payment().doChange2Cash(magicX, interface_ip, offsetSumId)   #转进账单
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            if is_success == False:
                rs = API0000_payment().doChange2Cash1(magicX, interface_ip, offsetSumId)   #转现金交账单
                is_success = rs[0]
                message = rs[1]
            assert is_success == True

            """step4：柜面收付费查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-续期_第' + str(times+1) + '期柜面收付费查询接口'  # 节点
            message = ''
            for k in range(0,120): 
                #调用原子脚本
                rs = API0000_payment().FeeQuery(magicX, interface_ip, policyNo)
                #获取所需响应值
                is_success = rs[0]
                message = rs[1]
                resultData = rs[2]
                if len(resultData)>0:
                    break
                else:
                    time.sleep(0.5)
            if len(resultData) == 0:
                message = '未查询到保单续期收付费记录！'
                API0000_payment().doChange2Bank(magicX, interface_ip, offsetSumId)   #转银行转账
                print 1
            else:
                payment = float(resultData[0]['amount'])
            #断言
            assert is_success == True

            """step5：柜面收付费保存接口"""
            #节点初始化
            is_success = ''
            unit = '系统-续期_第' + str(times+1) + '期柜面收付费保存接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            bankEndorse = '123123'  # 银行凭证号码
            feeConfirmDate = pay_due_date[0:10]   #收费日期（保全申请日期）
            internalAccount = '08-400301040007336'  # 公司收费账号
            internalBankCode = '05'  # 收费机构
            feeChannel = 'CASH-10017-AR'  # 支付通道
            cashOrgId = '10017'  # 机构名称
            internalBankName = '中国农业银行绥化市大有支行'  # 所属银行
            #调用原子脚本
            rs = API0000_payment().CashApproveInfoSave(magicX, interface_ip, resultData, bankEndorse, feeConfirmDate, internalAccount, internalBankCode, feeChannel, cashOrgId, internalBankName)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            assert is_success == True

            """step6：柜面收付费审核接口"""
            #节点初始化
            is_success = ''
            unit = '系统-续期_第' + str(times+1) + '期柜面收付费审核接口'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_payment().finishFeeFlow(magicX, interface_ip, resultData, bankEndorse, feeConfirmDate, internalAccount, internalBankCode, feeChannel, internalBankName)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
    
            """step7:综合查询-查询按钮接口"""
            #节点初始化
            is_success = ''
            unit = '系统-续期_第' + str(times+1) + '期综合查询-查询按钮接口：'  # 节点
            message = ''
            #调用原子化脚本:综合查询-查询按钮接口
            response = API0000_queryPolicy().queryPolicy(magicX,interface_ip,policyNo)
            resultData = response['resultData']
            # 返回是否成功，以及错误信息
            if len(resultData) > 0:
                is_success = True
                message = ''
                policyId = resultData[0]['policyId']
                proposalId = resultData[0]['proposalId']
                proposalNo = resultData[0]['proposalNo']
            else:
                is_success = False
                message = '第' + str(times+1) + '期续期，综合查询校验保单是否续期成功，未查询到此保单信息，请手动查询！。'
                policyId = ''
                proposalId = ''
                proposalNo = ''
            assert is_success == True

            """step8:# 综合查询-险种信息sheet_险种信息查询接口:判断此期续期是否成功"""
            #节点初始化
            is_success = ''
            unit = '系统-续期_第' + str(times+1) + '期# 综合查询-险种信息sheet_险种信息查询接口'  # 节点
            message = ''
            for j in range(0,300):
                #调用原子化脚本:综合查询-保单号超链接-险种信息sheet接口   
                response = API0000_queryPolicy().policyDetail(magicX, interface_ip, policyNo, proposalNo, proposalId, policyId)
                if response['success'] == True:
                    is_success = True
                    message = ''
                    query_payDueDate = response['others']['payDueDate']   #获取保单下期应缴日
                else:
                    is_success = ''
                    message = response['message']
                    query_payDueDate = ''
                assert is_success == True
                #判断此期续期是否成功
                if int(maxyears_renew) == times + 1:  #若达到保单的最后一次续期，设置下期应缴日query_payDueDate
                    pay_due_date1 = int(9999)
                else :
                    pay_due_date1 = int(pay_due_date[0:4]) + 1
                if int(query_payDueDate[0:4]) == pay_due_date1:
                    is_success == True
                    message = ''
                    break
                else:
                    time.sleep(1)
                    is_success == False
                    message = '第' + str(times+1) + '期续期收费后查询，综合查询校验保单是否续期成功，综合查询展示的下期应缴日与实际保单下期应缴日不符，请手动查询。'
            assert is_success == True

            """step9：续期用户登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-续期_第' + str(times+1) + '期续期用户登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX,interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            assert is_success == True  
            #存入dict
            total_times_renew = int(dict['public']['total_times_renew'])   #获取已续期次数
            dict['public']['total_times_renew'] = str(total_times_renew + 1)   #每次续期后，续期次数+1
            dict['logInfo']['code'] = '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp*续期收费_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time))) 
        except Exception, e:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['err'] = unit + ':' + str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                username_entry = dict['public']['username_entry']   #登录系统用户名
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username_entry)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict, payment


    """定义轨迹信息+检查点信息"""
    def save_check_info(self, dict, pay_due_date, payment):
        """
           step1:定义轨迹信息
           step2:定义检查点信息
        """   
        try:   
            """step1:定义检查点信息"""
            #节点初始化
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            unit = '定义轨迹信息+检查点信息'
            if dict['logInfo']['code'] == '1':
                calc_renew = {}
                #续期收费信息存入dict['check']['calc_renew']中
                calc_renew['apply_date'] = pay_due_date[0:10]   #r日期
                calc_renew['payment'] = payment   #续期收费金额
                calc_renew['msg'] = ''   #信息
                dict['check']['calc_renew'].append(calc_renew)
                """step2:定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'renew', 'trackTime':pay_due_date[0:10], 'trackData':{'payment': payment}, 'msg': ''}
                dict['track_info'].append(track_info)   #存入轨迹信息
            else:
                calc_renew = {}
                message = dict['logInfo']['msg']
                err = dict['logInfo']['err']
                if dict['logInfo']['msg'] == None or dict['logInfo']['msg'] == '':
                    message = str(dict['logInfo']['err'])
                #续期收费信息存入dict['check']['calc_renew']中
                calc_renew['apply_date'] = pay_due_date[0:10]   #新契约收费金额
                calc_renew['payment'] = payment   #新契约收费金额
                calc_renew['msg'] = message   #新契约收费金额
                dict['check']['calc_renew'].append(calc_renew)
                """step2:定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'renew', 'trackTime':pay_due_date[0:10], 'trackData':{'payment': payment}, 'msg': message}
                dict['track_info'].append(track_info)   #存入轨迹信息
        except Exception, e:
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*定义轨迹信息+检查点信息部分脚本报错:\n')  + traceback.format_exc())
        return dict



        
if __name__ == "__main__":  
    try:
        begin_time = datetime.datetime.now()   #开始时间
        #1.初始化
        msg = ''   #执行python脚本前存在的错误信息
        job = 'renew'   #场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = 'uat4'
            env_name = env_name.encode('utf-8')
            policyNo = '8088615170358368'   #保单号
            times_renew = 1   #续期次数
            username_entry = 'xcy1'   #登录系统用户名
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo = ''   #保单号
                times_renew = ''   #续期次数
                username_entry = ''   #登录系统用户名
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','policyNo','times_renew','username_entry']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo = rs[2][1]   #保单号
                times_renew = rs[2][2]   #续期次数
                username_entry = rs[2][3]   #登录系统用户名
       #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name, 'times_renew':str(times_renew)}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = {'execNo': 'test1', 'policy_info':{'policyNo':policyNo},'public': {'env_name':env_name, 'username_entry': username_entry, 'interface_ip': interface_ip,'total_times_renew':0,'maxyears_renew':0}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'', 'job':job}, 'track_info': [], 'check':{'calc_renew':[]}, 'track_change':[]}
        #5.1定义logging文件路径
        if 'win' in sys.platform:
            logging_filename = 'D:\\xLibrary\\chunyu\\%s.html' % str(execNo)
            #判断windows是否存在某文件，存在则删除文件
            if os.path.exists(logging_filename):
                os.remove(logging_filename)
        else:
            logging_filename = '/data/xServer/xReport/%s.html' % str(execNo) 
        #5.2定义logging格式
        logging.basicConfig(level=logging.WARNING , format='%(message)s  &nbsp&nbsp&nbsp&nbsp%(asctime)s <br/><br/>', filename=logging_filename, filemode='a')
        #6.执行脚本
        if is_run == True:
            dict = sys_API0004().renew(times_renew, dict)
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:   #windows系统平台
                if dict['logInfo']['code'] == '1':
                    print '是否续期成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('录入保单续期次数：' + str(times_renew)).decode('utf-8').encode('gb2312')
                    print ('最大保单续期次数：' + str(dict['public']['maxyears_renew'])).decode('utf-8').encode('gb2312')
                    print ('脚本实际续期次数：' + str(dict['public']['total_times_renew'])).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '是否续期成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('录入保单续期次数：' + str(times_renew)).decode('utf-8').encode('gb2312')
                    print ('最大保单续期次数：' + str(dict['public']['maxyears_renew'])).decode('utf-8').encode('gb2312')
                    print ('脚本实际续期次数：' + str(dict['public']['total_times_renew'])).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "是否续期成功：成功,,环境：%s,,保单号：%s,,录入续期次数：%s,,最大续期次数：%s,,实际续期次数：%s,,耗时：%s" % (env_name, dict['policy_info']['policyNo'], str(times_renew), str(dict['public']['maxyears_renew']), str(dict['public']['total_times_renew']), API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "是否续期成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,录入续期次数：%s,,最大续期次数：%s,,实际续期次数：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, dict['policy_info']['policyNo'], str(times_renew), str(dict['public']['maxyears_renew']), str(dict['public']['total_times_renew']), API0000_diy().logger_count_time(begin_time, end_time))
                print result_str

            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())








