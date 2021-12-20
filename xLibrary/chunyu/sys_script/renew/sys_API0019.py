#coding=utf-8

import sys
import time
import json
import urllib
import logging
import pymysql
import paramiko
import requests
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys);
sys.setdefaultencoding("utf8")
from datetime import datetime
from xLibrary.chunyu.API0000 import *
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002



"""续期不收费:
    step1:续期前准备
        1.验证用户登录系统 
        2.获取保单最大续期年数
        3.续期前判断保单是否满足续期条件
    step2:续期遍历
        1.执行每期的续期
        2.每期续期收费
        3.定义轨迹信息+检查点信息
"""
class sys_API0019:

    def __init__(self):
        pass

    @func_set_timeout(300)#设定函数超执行时间     
    def renew(self, dict):
        """续期:
                step1:续期前准备
                step2:续期遍历
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #日志打印&nbsp&nbsp&nbsp次数
            if dict['logInfo']['job'][0:14] == 'complex_scenes':   #复杂场景
                dict['logInfo']['job'] = dict['logInfo']['job'][0:14] + '-' + 'renew_nofee'
                space_times = 3
            elif dict['logInfo']['job'] == 'single_invalidation_bacth':   #保单失效（续期不缴费）组件
                dict['logInfo']['job'] = 'renew_nofee'
                space_times = 1
            else:
                space_times = 0
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保单续期后不缴费开始(预计耗时:60s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            pay_due_date = 'xxxx-xx-xx'   #下期应缴日
            """step1:续期前准备"""
            rs = sys_API0019().prepare_renew(space_times, dict)
            maxyears_renew = rs[0]
            dict = rs[1]
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            """step2:续期遍历"""
            rs = sys_API0019().execute_renew(space_times, maxyears_renew, dict)
            pay_due_date = rs[0]
            dict = rs[1]
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保单续期后不缴费结束'))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #记录异常日志
            logging.warning('&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp*异常位置:\n'.decode('utf-8').encode('gbk') + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*执行时间超时退出。'))
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
            #异常场景-登出系统（防止与用户被挂起）
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*运行异常-用户解锁'))
                dict['public']['magicX'] = ''
        finally:
            pass
        return pay_due_date, dict

    @func_set_timeout(30)#设定函数超执行时间    
    def prepare_renew(self, space_times, dict):
        """续期前准备:
            step1:验证用户登录系统 
            step2:获取保单最大续期年数
            step3:续期前判断保单是否满足续期条件
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*验证用户是否可登录系统+获取保单最大续期年度开始(预计耗时:5s)'))  
            """step1:验证用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-续期_验证用户登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            userName = dict['public']['username_entry']   #登录系统用户名
            interface_ip = dict['public']['interface_ip']   #接口ip
            rs = API0000_diy().verify_userlogin(env_name, userName, interface_ip)
            is_success = rs[0]
            message = rs[1]
            unit = rs[2]
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
            cursor = API0000_diy().db_conf(env_name,'wift_pa')
            #查询保单的生效日期、下期应缴日、缴费期间
            cursor.execute(sql)
            result = cursor.fetchall()
            #定义险种剩余交费年限列表
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
                is_success = False
                message = '获取的最大续期年数为0'
            elif len(list) > 0:
                maxyears_renew = list[-1]   #最大续期年数
                is_success = True
                message = ''
            #断言
            assert is_success == True
            dict['logInfo']['code'] = '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*验证用户是否可登录系统+获取保单最大续期年度结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time))) 
        except Exception, e:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return maxyears_renew, dict   

    

    @func_set_timeout(300)#设定函数超执行时间    
    def execute_renew(self, space_times, maxyears_renew, dict):
        """执行每期的续期:
            step1:获取保单下期应缴日
            step2:修改服务器时间
            step3:启动续期批处理
            step4:等待+判断保单续期批处理是否跑成功
        """
        try: 
            begin_time1 = datetime.datetime.now()   #开始时间
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            job = dict['logInfo']['job']   #场景名
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*数据库查询获取下期应缴日开始(预计耗时:5s)'))  
            #初始化
            magicX = ''    #初始化会话id
            #判断保单最大续期次数
            if maxyears_renew == 0:
                is_success = False
                message = '保单已缴费期满'
            else:
                is_success = True
            #断言
            assert is_success == True        
            """step1:获取保单下期应缴日"""
            #节点初始化
            is_success = ''
            unit = '续期不收费操作'  # 节点
            message = ''
            pay_due_date = ''
            list = []    #初始化数据库查询保单险种下期应缴日列表
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            policyNo = dict['policy_info']['policyNo']   #保单号
            sql = "select b.pay_due_date from t_pa_policy a,t_pa_policy_product b where a.policy_id=b.policy_id and a.POLICY_NO='" + policyNo + "'"  
            #调用原子脚本    
            cursor = API0000_diy().db_conf(env_name,'wift_pa')
            cursor.execute(sql)
            result = cursor.fetchall()
            for j in range(0,len(result)): 
                pay_due_date = result[j][0].strftime('%Y-%m-%d %H:%M')
                if (pay_due_date not in list) and pay_due_date[0:4] !='9999':
                    list.append(pay_due_date)
            if len(list) == 0:
                is_success = False
                pay_due_date = ''
                message = '未获取到保单下期应缴日'
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
            end_time1 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*数据库查询获取下期应缴日结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time1, end_time1))) 
            
            """step2:修改服务器时间"""
            dict = sys_API0002().Modify_servertime(pay_due_date, job, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常

            """step3:启动续期批处理"""
            begin_time3 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*启动续期批处理开始(预计耗时:30s)'))
            #调用原子脚本:
                #0.登录系统接口
                    #节点初始化
            #记录日志
            #logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+2) + '*登录系统开始'))
            is_success = ''
            unit = '系统-启动续期批处理_登录系统'  # 节点
            message = ''
                    #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            policyNo = dict['policy_info']['policyNo']   #保单号
            username = dict['public']['username_entry']    #续期登录用户
                    #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]   
            assert is_success == True
            dict['public']['magicX'] = magicX
            #记录日志
            #logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+2) + '*登录系统结束'))
            is_success = ''

            #节点初始化
            is_success = ''
            unit = '系统-续期期启动续期批处理'  # 节点
            message = ''
            #记录日志
            #logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+2) + '*跑续期批处理开始'))
            is_success = ''
            for j in range(0,60):
                #跑批处理
                if j in (0,5,10,15):    #续期批处理遍历四次（解决跑不出来问题；每次遍历存在时间间隔，解决收费多条的异常场景）
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
                    time.sleep(2)    #等待2s

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
                    # 断言
                    assert is_success == True 
                    time.sleep(2)    #等待2s 

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
                    time.sleep(2)    #等待2s

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
                    #断言
                    assert is_success == True
                    time.sleep(2)    #等待2s

                """step4:等待+判断保单续期批处理是否跑成功"""
                #节点初始化
                is_success = ''
                unit = '系统-续期_等待+判断保单续期批处理是否跑成功'  # 节点
                message = ''
                #调用原子脚本:
                rs = API0000_diy().db_conf_update(env_name,'wift_pa')
                db = rs[0]
                cursor = rs[1]
                sql = "select b.ARAP_TIME from t_pa_policy a,t_pa_renew_preprem b where a.POLICY_ID=b.POLICY_ID and a.POLICY_NO=" + policyNo + " and PREM_STATUS='2';"        
                cursor.execute(sql)
                result = cursor.fetchall()
                #print len(result)
                if len(result)==0:
                    is_success = False
                    message = '续期不成功。保单续期批处理未跑出(请检查服务器或者网络是否稳定)'
                    time.sleep(5)
                else:
                    date = result[0][0].strftime('%Y-%m-%d')    #获取查询sql得到的应缴日期
                    #判断数据库查询的下期应缴日pay_due_date与数据库查询的应缴日期ARAP_TIME，绝对值是否小于15天
                    if abs(API0000_diy().cals_different_days(pay_due_date[0:10], date)) <= 27:
                        is_success = True
                        break    #跳出循环
                    else:
                        message = '续期成功，但跑出的续期应收日期与保单下期应缴日大于27天，保单数据问题！'
                db.close()    #断开数据库连接
            # 加入断言
            assert is_success == True
            #记录日志
            #logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+2) + '*跑批处理结束'))
            is_success = ''
            end_time3 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*启动续期批处理结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time3, end_time3))) 

            """step5:关闭批处理"""
            begin_time4 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*关闭续期批处理1001、1003_开始(预计耗时:3s)'))
            #节点初始化
            is_success = ''
            unit = '系统-续期_第' + str(space_times+1) + '期关闭续期批处理'  # 节点
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
            end_time4 = datetime.datetime.now()   #结束时间 
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*关闭续期批处理1001、1003_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time4, end_time4)))

            #记录日志
            #logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+2) + '*登出系统结束'))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['err'] = unit + ':' + str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
                dict['public']['magicX'] = ''
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+2) + '*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
            #节点初始化
            if dict['logInfo']['code'] == '1':
                calc_renew = {}
                #续期收费信息存入dict['check']['calc_renew']中
                calc_renew['apply_date'] = pay_due_date[0:10]   #新契约收费金额
                calc_renew['payment'] = 0   #新契约收费金额
                calc_renew['msg'] = ''   #新契约收费金额
                dict['check']['calc_renew'].append(calc_renew)
                """step2:定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'renew', 'trackTime':pay_due_date[0:10], 'trackData':{'payment': 0}, 'msg': ''}
                dict['track_info'].append(track_info)   #存入轨迹信息
            else:
                calc_renew = {}
                message = dict['logInfo']['msg']
                err = dict['logInfo']['err']
                if dict['logInfo']['msg'] == None or dict['logInfo']['msg'] == '':
                    message = str(dict['logInfo']['err'])
                #续期收费信息存入dict['check']['calc_renew']中
                calc_renew['apply_date'] = pay_due_date[0:10]   #新契约收费金额
                calc_renew['payment'] = 0   #新契约收费金额
                calc_renew['msg'] = message   #新契约收费金额
                dict['check']['calc_renew'].append(calc_renew)
                """step2:定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'renew', 'trackTime':pay_due_date[0:10], 'trackData':{'payment': 0}, 'msg': message}
                dict['track_info'].append(track_info)   #存入轨迹信息
        return pay_due_date, dict 



if __name__ == "__main__":  

    #1.初始化
    job = 'renew_nofee'
    execNo = 'test001'   #测试编号
    env_name = 'uat8'   #环境类型
    env_name = env_name.encode('utf-8')
    policyNo = '8088604074469868'   #保单号
    username = 'xcy1'    #登录系统用户名
    interface_ip = API0000_diy().ip_conf(env_name)   #环境ip
    #2.定义dict
    dict = {'execNo': 'test1', 'policy_info':{'policyNo':policyNo},'public': {'env_name':env_name, 'username_entry':username, 'interface_ip':interface_ip}, 'logInfo': {'code':'0', 'msg':'', 'err':'', 'result':'', 'job':job}, 'track_info': [], 'check':{'calc_renew':[]}, 'track_change':[]}
    dict['logInfo']['unit'] = 'renew'
    #3.定义logging格式
    if 'win' in sys.platform:
        logging_filename = 'D:\\xLibrary\\chunyu\\%s.html' % str(execNo)
    else:
        logging_filename = '/data/xServer/xReport/%s.html' % str(execNo)
    logging.basicConfig(level=logging.WARNING , format='%(message)s   %(asctime)s \n', filename=logging_filename, filemode='a')
    #4.执行脚本
    rs = sys_API0019().renew(dict)
    pay_due_date = rs[0]
    dict = rs[1]

    print '----------------------'
    print policyNo
    print pay_due_date
    print dict











