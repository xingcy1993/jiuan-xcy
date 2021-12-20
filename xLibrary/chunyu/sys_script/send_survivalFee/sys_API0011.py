# coding=utf-8

import sys
import time
import urllib
import pymysql
import logging
import requests
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002



"""派发生存金:
       step1:验证
             1.判断保单是否存在待派发生存金
             2.判断录入的派发日期是否符合保单生存金派发日期
             3.验证录入用户是否可正常登录系统
       step2:修改服务器时间
       step3:启动派发生存金批处理
             1.登录系统
             2.跑批
             3.判断生存金是否派发成功:
                 1)综合查询_查询按钮接口
                 2)综合查询_生存给付信息sheet_账户交易记录查询接口
       step3:关闭派发生存金批处理     
             1.登出系统
       step4:定义轨迹信息+检查点信息
             1.定义轨迹信息
             2.定义检查点信息
"""
class sys_API0011:

    def __init__(self):
        pass


    @func_set_timeout(300)#设定函数超执行时间
    def send_survivalFee(self, sendDate, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            space_times = 0   #日志打印空格次数
            if dict['logInfo']['job'][0:14] == 'complex_scenes':   #复杂场景
                space_times = 2
            else:
                space_times = 0
            dict['public']['space_times'] = space_times
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '生存金派发批处理开始(预计耗时:120s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            magicX = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']
            username_entry = dict['public']['username_entry']
            interface_ip = dict['public']['interface_ip']

            """step1.1:判断保单是否存在待派发生存金"""
            is_success = ''
            message = ''
            unit = "系统-派发生存金_判断保单是否存在待派发生存金"   #节点
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            policyNo = dict['policy_info']['policyNo']   #保单号
            sql = "select PAY_DUE_DATE from t_pa_pay_plan where POLICY_NO = '" + policyNo + "' and pay_plan_type = '1' and PAY_STATUS = '1'"  
            #调用原子脚本    
            cursor = API0000_diy().db_conf(env_name,'wift_pa')
            cursor.execute(sql)
            result = cursor.fetchall()
            if len(result) == 0:
                is_success = False
                message = '保单不存在生存金。'
            else:
                is_success = True
                message = ''
            assert is_success == True

            """step1.2:判断录入的派发日期是否符合保单生存金派发日期"""
            #节点初始化
            is_success = ''
            message = ''
            unit = "系统-派发生存金_判断录入的派发日期是否符合数据库中保单派发生存金的日期"   #节点
            list_result = []   #定义数据库查询保单派发生存金日期列表
            #遍历数据库查询数据库查询保单派发生存金日期，并存入列表
            for i in range(0,len(result)):
                list_result.append(result[i][0].strftime('%Y-%m-%d'))
            #判断派发日期是否在数据库查询保单派发生存金日期列表中
            if sendDate in list_result:
                is_success = True
                message = ''
            else:
                is_success = False
                message = '录入的派发日期，与数据库中保单派发生存金的日期不符，请重新确认！' 
            assert is_success == True

            """step1.3:验证录入用户是否可正常登录系统"""
            #节点初始化
            is_success = ''
            message = ''
            unit = "系统-派发生存金_验证录入用户是否可正常登录系统"   #节点
            #验证用户是否可正常登录系统
            rs = API0000_diy().verify_userlogin(env_name, username_entry, interface_ip)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True


            """step2:修改服务器时间"""
            #节点初始化
            is_success = ''
            message = ''
            unit = "系统-派发生存金_修改服务器时间"   #节点
            #调用原子脚本
            dict = sys_API0002().Modify_servertime(sendDate, dict['logInfo']['job'], dict)  
            # 加入断言
            assert dict['logInfo']['code'] == '1'

            """step3:启动派年金派发批处理"""
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            begin_time1 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*启用生存金派发批处理2、4开始(预计耗时:60s)'))
            """0.登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-派发生存金_登录系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username_entry, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            dict['public']['magicX'] = magicX
            assert is_success == True
            """
            #调用原子脚本:
            rs = API0000_diy().db_conf_update(env_name,'wift_pa')
            sql = "UPDATE t_batch_job a SET a.IS_ENABLE='Y' WHERE a.`JOB_ID` in ('2','4');"
            rs[1].execute(sql)
            rs[0].commit()
            #判断续期批处理是否启动成功
            cursor = API0000_diy().db_conf(env_name,'wift_pa')        
            sql = "select IS_ENABLE from t_batch_job where JOB_ID in('2','4');" 
            cursor.execute(sql)
            result = cursor.fetchall()     
            if result[0][0] == 'Y' and result[1][0] == 'Y':
                is_success = True
            else:
                is_success = False
                message = '派发生存金批处理没有启动成功'
            # 加入断言
            assert is_success == True
            """                
            for j in range(0,60):
                #节点初始化
                is_success = ''
                unit = '系统-派发生存金_启动派发生存金批处理'  # 节点
                message = ''
                if j in (0,5,10):
                    #1.启动续期预收费用记录表接口
                    batchSystem = 'PA'
                    jobId = '2'
                    isEnable = 'Y'
                    jobName = '年金派发批处理'   #批处理任务名称
                    jobName = urllib.quote(jobName)
                    response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
                    #获取所需响应值
                    if response['success'] == True and response['message'] == '[年金派发批处理]更新成功':
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '年金派发批处理启动失败'
                    assert is_success == True

                    #2.提交年金派发批处理接口
                    #dict获取数据+定义数据
                    policyNo = dict['policy_info']['policyNo']   #保单号
                    business_date = sendDate
                    #调用原子脚本
                    response = API0000_pa().saveBatchSubmit(magicX, interface_ip, batchSystem, jobId, policyNo, business_date)
                    #获取所需响应值
                    if response['success'] == True:
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '年金派发批处理接口提交失败'
                    # 加入断言
                    assert is_success == True

                    #3.启动计算年金首期派发日及派发截止日批处理接口
                    batchSystem = 'PA'
                    jobId = '4'
                    isEnable = 'Y'
                    jobName = '计算年金首期派发日及派发截止日批处理'   #批处理任务名称
                    jobName = urllib.quote(jobName)
                    response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
                    #获取所需响应值
                    if response['success'] == True and response['message'] == '[计算年金首期派发日及派发截止日批处理]更新成功':
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '计算年金首期派发日及派发截止日批处理启动失败'
                    # 加入断言
                    assert is_success == True 
                    time.sleep(2)

                    #4.提交续期预收费用记录表接口
                    #dict获取数据+定义数据
                    policyNo = dict['policy_info']['policyNo']   #保单号
                    business_date = sendDate
                    #调用原子脚本
                    response = API0000_pa().saveBatchSubmit(magicX, interface_ip, batchSystem, jobId, policyNo, business_date)
                    #获取所需响应值
                    if response['success'] == True:
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '计算年金首期派发日及派发截止日批处理提交失败'
                    # 加入断言
                    assert is_success == True 
                    time.sleep(2)

                #5.判断生存金是否派发成功
                #(1)综合查询_查询按钮接口
                #节点初始化
                is_success = ''
                unit = '系统-派发生存金_综合查询_查询按钮接口'  # 节点
                message = ''
                #dict获取数据+定义数据
                policyNo = dict['policy_info']['policyNo']
                #调用原子脚本:
                response = API0000_queryPolicy().queryPolicy(magicX, interface_ip, policyNo)
                #获取所需响应值
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
                    message = response['message']
                    policyId = ''
                    proposalId = ''
                    proposalNo = ''
                assert is_success == True

                #(2)综合查询_生存给付信息sheet_账户交易记录查询接口
                #节点初始化
                is_success = ''
                unit = '系统-派发生存金_综合查询_生存给付信息sheet_账户交易记录查询接口'  # 节点
                message = ''
                sys_survivalFee_dict = {}
                list = []   #定义空数组，为了存储账户交易记录中的生存金信息
                #调用原子脚本:
                response = API0000_queryPolicy().survivalPayAccount(magicX, interface_ip, policyNo, proposalNo, proposalId, policyId)
                #获取所需响应值
                resultData = response['resultData']
                # 返回是否成功，以及错误信息
                if len(resultData) > 0:
                    is_success = True
                    message = ''
                else:
                    is_success = False
                    message = response['message']
                #存储账户交易记录中的生存金信息:①判断resultData是否有值②若有值，遍历resultData中transCode=8的生存金信息存储到list中③若无值，等待1s，返回for循环重新查询
                if len(resultData) == 0:
                    is_success = False
                    message = '生存金未跑出，请检查t_prod_fund_settle_rate表中-险种累计生息账户利息是否未配置或配置重复！'
                    time.sleep(1)
                    continue
                else:
                    for j in range(0,len(resultData)):
                        if resultData[j]['transCode'] == '8':
                            list.append(resultData[j])
                #判断list列表中存储的最后一期生存金信息是否为本次欲跑出的生存金:①判断list是否有值②若有值且list中最后一个险种信息中dealTime=派发日期，跳出for循环③若有值单list中最后一个险种信息中dealTime不=派发日期，等待1s，返回for循环重新查询④若无值，等待1s，返回for循环重新查询
                if len(list) == 0:
                    is_success = False
                    message = '生存金未跑出，请检查t_prod_fund_settle_rate表中-险种累计生息账户利息是否未配置或配置重复！'
                    time.sleep(2)
                    continue
                elif (len(list)>0 and (list[-1]['dealTime'] != sendDate)):
                    is_success = False
                    message = '生存金未跑出，请检查t_prod_fund_settle_rate表中-险种累计生息账户利息是否未配置或配置重复！'
                    time.sleep(2)
                    continue
                elif (len(list)>0 and (list[-1]['dealTime'] == sendDate)):
                    is_success = True
                    message = ''
                    sys_survivalFee_dict['transAmount'] = list[-1]['transAmount']
                    sys_survivalFee_dict['dealTime'] = list[-1]['dealTime']
                    break
            #断言
            assert is_success == True
            end_time1 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*启用生存金派发批处理2、4结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time1, end_time1)))


            """step4:关闭批处理"""
            begin_time2 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*关闭生存金派发批处理2、4开始(预计耗时:60s)'))

            #节点初始化
            is_success = ''
            unit = '系统-派发生存金_关闭派发生存金批处理'  # 节点
            message = ''
            #（1）关闭续期预收费用记录表接口
            batchSystem = 'PA'
            jobId = '2'
            isEnable = 'N'
            jobName = '年金派发批处理'   #批处理任务名称
            jobName = urllib.quote(jobName)
            response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
            #获取所需响应值
            if response['success'] == True and response['message'] == '[年金派发批处理]更新成功':
                is_success = True
                message = ''
            else:
                is_success = False
                message = '年金派发批处理关闭失败'
            assert is_success == True

            #（2）关闭计算年金首期派发日及派发截止日批处理接口
            batchSystem = 'PA'
            jobId = '4'
            isEnable = 'N'
            jobName = '计算年金首期派发日及派发截止日批处理'   #批处理任务名称
            jobName = urllib.quote(jobName)
            response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
            #获取所需响应值
            if response['success'] == True and response['message'] == '[计算年金首期派发日及派发截止日批处理]更新成功':
                is_success = True
                message = ''
            else:
                is_success = False
                message = '计算年金首期派发日及派发截止日批处理启动失败'
            # 加入断言
            assert is_success == True
            end_time2 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*关闭生存金派发批处理2、4结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time2, end_time2)))


            #登出系统
            #节点初始化
            is_success = ''
            unit = '系统-派发生存金_登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX, interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            dict['public']['magicX'] = ''

            """step5:定义轨迹信息+检查点信息"""            
            """1.定义检查点信息"""
            calc_survivalFee = {}
            #生存金派发信息存入dict['check']['calc_survivalFee']中
            calc_survivalFee['apply_date'] = sendDate   #新契约收费金额
            calc_survivalFee['payment'] = float(list[-1]['transAmount'])   #新契约收费金额
            calc_survivalFee['msg'] = ''   #新契约收费金额
            dict['check']['calc_survivalFee'].append(calc_survivalFee)
            """2.定义轨迹信息"""
            track_info = {'trackType':'survivalFee', 'trackTime':sendDate, 'trackData':{'payment':float(list[-1]['transAmount'])}, 'msg': ''}
            dict['track_info'].append(track_info)   #存入轨迹信息
            #存入dict
            dict['logInfo']['code'] = '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '生存金派发批处理结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['err'] = unit + ':' + str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                username_entry = dict['public']['username_entry']    #新契约复核用户
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username_entry)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*异常位置-' + unit + ':\n')  + traceback.format_exc())
            #记录异常dict
            msg = dict['logInfo']['msg']
            err = dict['logInfo']['err']
            if dict['logInfo']['msg'] == None or dict['logInfo']['msg'] == '':
                msg = str(dict['logInfo']['err'])
            calc_survivalFee = {}
            #生存金派发信息存入dict['check']['calc_survivalFee']中
            calc_survivalFee['apply_date'] = sendDate   #新契约收费金额
            calc_survivalFee['payment'] = ''   #新契约收费金额
            calc_survivalFee['msg'] = msg   #新契约收费金额
            dict['check']['calc_survivalFee'].append(calc_survivalFee)
            """2.定义轨迹信息"""
            track_info = {'trackType':'survivalFee', 'trackTime':sendDate, 'trackData':{'payment':''}, 'msg': message}
            dict['track_info'].append(track_info)   #存入轨迹信息 
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)  
        return dict



if __name__ == "__main__":  
    try:
        begin_time = datetime.datetime.now()   #开始时间
        #1.初始化
        is_run = True   #是否执行python脚本 
        msg = ''   #执行python脚本前存在的错误信息
        job = 'send_survivalFee'   #场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = '预生产'
            env_name = env_name.encode('utf-8')
            policyNo = '8088633856324468'   #保单号
            sendDate = '2022-02-02'   #派发日期
            username_entry = 'xcy1'   #登录用户名
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo = ''   
                sendDate = ''   
                username_entry = ''  
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','policyNo','sendDate','username_entry']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo = rs[2][1]   #保单号
                sendDate = rs[2][2]   #派发日期
                username_entry = rs[2][3]   #登录用户名
       #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name,'sendDate':sendDate}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)
        #4.定义dict
        dict = {'execNo': execNo, 'policy_info':{'policyNo':policyNo},'public': {'env_name':env_name, 'username_entry':username_entry, 'interface_ip':interface_ip, 'magicX':''}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'', 'job':job}, 'track_info': [], 'check':{'calc_survivalFee':[]}, 'track_change':[]}
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
            dict = sys_API0011().send_survivalFee(sendDate, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:   #windows系统平台
                if dict['logInfo']['code'] == '1':
                    print '保单生存金派发是否成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('派发日期：' + sendDate).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '保单生存金派发是否成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('派发日期：' + sendDate).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "保单生存金派发是否成功：成功,,环境：%s,,保单号：%s,,派发日期：%s,,耗时：%s" % (env_name, dict['policy_info']['policyNo'], sendDate, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "保单生存金派发是否成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,派发日期：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, dict['policy_info']['policyNo'], sendDate, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())







