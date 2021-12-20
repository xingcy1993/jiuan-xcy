#coding=utf-8

import sys
import time
import urllib
import logging
import requests
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys);
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002
from xLibrary.chunyu.sys_script.renew.sys_API0019 import sys_API0019



"""保单失效（一般失效）:
    step1:续期不收费
    step2:修改服务器时间-宽限期外
    step3:保单-启用失效自垫批处理
        1.登录系统
        2.批处理定义-启用/关闭批处理任务接口
        3.批处理定义-提交批处理任务接口
        4.查询保单是否中止状态
        5.登出系统
"""
class sys_API0017:

    def __init__(self):
        pass


    @func_set_timeout(300)#设定函数超执行时间
    def single_invalidation_bacth(self, dict):
        try:
            begin_time1 = datetime.datetime.now()   #开始时间
            space_times = 0   #日志打印空格次数
            if dict['logInfo']['job'][0:14] == 'complex_scenes':   #复杂场景
                space_times = 2
            else:
                space_times = 0
            dict['public']['space_times'] = space_times
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '保单失效（一般失效）开始(预计耗时:150s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            job = dict['logInfo']['job']
            magicX = ''

            """step1:验证用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '验证用户登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            username_entry = dict['public']['username_entry']   #登录系统用户名
            interface_ip = dict['public']['interface_ip']   #接口ip
            rs = API0000_diy().verify_userlogin(env_name, username_entry, interface_ip)
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
                is_success = False
                message = '获取的最大续期年数为0！（若存在刚修改过系统服务器时间且保单缴费期未满，可以等待几分钟后重试。）'
            elif len(list) > 0:
                maxyears_renew = list[-1]   #最大续期年数
                is_success = True
                message = ''
            #断言
            assert is_success == True

            """step3:保单续期操作不收费"""
            #节点初始化
            is_success = ''
            unit = '系统-保单续期不收费操作'  # 节点
            message = ''
            rs = sys_API0019().renew(dict)
            pay_due_date = rs[0][0:10]   #续期日期
            dict = rs[1]
            message = dict['logInfo']['msg']   #获取sys_API0019()的msg
            #断言
            assert dict['logInfo']['code'] == '1'    #断言是否异常标识
            
            if dict['logInfo']['job'][0:14] == 'complex_scenes':   #复杂场景
                dict['logInfo']['job'] = 'complex_scenes-single_invalidation_bacth'
            else:
                dict['logInfo']['job'] = 'single_invalidation_bacth'

            """step4:修改服务器时间-宽限期外"""
            business_date = API0000_diy().date_add_subtract(pay_due_date, 64)
            dict = sys_API0002().Modify_servertime(business_date, job, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常

            """step5:保单-启用失效自垫批处理"""
            begin_time2 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*登录系统+启用失效批处理开始(预计耗时:30s)'))
            """1.登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username_entry = dict['public']['username_entry']    #保全录入用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name,username_entry, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            # 加入断言
            assert is_success == True 
            dict['public']['magicX'] = magicX

            #启动实现批处理、判断是否保单失效
            for j in range(0,60):
                if j in (0,5,10):
                    """2.启用/关闭批处理任务接口"""
                    #dict获取数据+定义数据
                    batchSystem = 'PA'   #批处理系统类型
                    jobId = '1010'   #批处理任务Id
                    isEnable = 'Y'   #是否启动批处理。Y-启动；N-关闭
                    jobName = '失效自垫批处理'   #批处理任务名称
                    jobName = urllib.quote(jobName)
                    #调用原子脚本
                    response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
                    #获取所需响应值
                    if response['success'] == True and response['message'] == '[失效自垫批处理]更新成功':
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '批处理启动失败'
                    # 加入断言
                    assert is_success == True 
                    time.sleep(2)
                    """3.提交批处理任务接口"""
                    #dict获取数据+定义数据
                    policyNo = dict['policy_info']['policyNo']   #保单号
                    #调用原子脚本
                    response = API0000_pa().saveBatchSubmit(magicX, interface_ip, batchSystem, jobId, policyNo, business_date)
                    #获取所需响应值
                    if response['success'] == True:
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '批处理提交失败'
                    # 加入断言
                    assert is_success == True 
                    time.sleep(2)
                #4.查询保单是否中止状态
                #节点初始化
                is_success = ''
                unit = '系统-综合查询-查询按钮接口'  # 节点
                message = ''
                #调用原子化脚本:综合查询-查询按钮接口
                response = API0000_queryPolicy().queryPolicy(magicX, interface_ip, policyNo)
                resultData = response['resultData']
                # 返回是否成功，以及错误信息
                if len(resultData) > 0:
                    if resultData[0]['policyStatus'] == '02':   #保单状态
                        is_success = True
                        message = ''
                        break
                    else:
                        is_success = False
                        message = '保单未中止，请检查批处理是否被关闭。' 
                        time.sleep(2)
                else:
                    is_success = False
                    message = '综合查询-查询按钮接口未成功'
                    policyStatus = ''
                    time.sleep(2)
            #断言
            assert is_success == True
            end_time2 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*登录系统+启用失效批处理结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time2, end_time2)))
            
            """step6:关闭批处理"""
            begin_time3 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*关闭失效批处理1010_开始(预计耗时:3s)'))
            #节点初始化
            is_success = ''
            unit = '系统-关闭失效批处理'  # 节点
            message = ''
            #1.关闭失效自垫批处理接口
            batchSystem = 'PA'   #批处理系统类型
            jobId = '1010'   #批处理任务Id
            isEnable = 'N'   #是否启动批处理。Y-启动；N-关闭
            jobName = '失效自垫批处理'   #批处理任务名称
            jobName = urllib.quote(jobName)
            #调用原子脚本
            response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
            #获取所需响应值
            if response['success'] == True and response['message'] == '[失效自垫批处理]更新成功':
                is_success = True
                message = ''
            else:
                is_success = False
                message = '批处理关闭失败'
            # 加入断言
            assert is_success == True 

            #存入dict-保单、险种状态
            dict['policy_info']['policy_status'] = '02'   #保单状态
            dict['policy_info']['invalid_reason'] = '一般失效'   #失效原因
            for j in range(0, len(dict['policy_info']['main_risk_info'])):
                dict['policy_info']['main_risk_info'][j]['liability_state'] = '02'   #主险中止
            for j in range(0, len(dict['policy_info']['sub_risk_info'])):
                dict['policy_info']['sub_risk_info'][j]['liability_state'] = '02'   #附加险中止
            """5.登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX,interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            # 加入断言
            assert is_success == True 
            dict['public']['magicX'] = ''

            #存入dict
            dict['logInfo']['code'] = '1'
            dict['public']['invalid_date'] = business_date   #保单失效日期
            end_time3 = datetime.datetime.now()   #结束时间 
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*关闭失效批处理1010_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time3, end_time3)))
            end_time1 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '保单失效（一般失效）结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time1, end_time1)))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username_entry)
                dict['public']['magicX'] = ''
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
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
        job = 'single_invalidation_bacth'   #场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = 'uat4'
            env_name = env_name.encode('utf-8')
            policyNo = '8088615170317668'   #保单号
            username_entry = 'xcy1'   #登录系统用户名
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo = ''       
                username_entry = ''  
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','policyNo','username_entry']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo = rs[2][1]   #保单号
                username_entry = rs[2][2]   #登录系统用户名
       #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = {'execNo': execNo, 'policy_info':{'policyNo':policyNo, 'main_risk_info':[{'liability_state':''}], 'sub_risk_info':[{'liability_state':''}]},'public': {'env_name':env_name, 'username_entry': username_entry, 'interface_ip': interface_ip, 'invalid_date': ''}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'', 'job':job}, 'track_info': [], 'check':{'calc_nb':{'product':[], 'payment':''},'calc_renew':[],'survivalFee':[]}, 'track_change':[]}
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
            dict = sys_API0017().single_invalidation_bacth(dict)
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出。'))
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:   #windows系统平台
                if dict['logInfo']['code'] == '1':
                    print '保单失效（一般失效）是否成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('保单失效日期：' + dict['public']['invalid_date']).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '保单失效（一般失效）是否成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "保单失效（一般失效）是否成功：成功,,环境：%s,,保单号：%s,,保单失效日期：%s,,耗时：%s" % (env_name, dict['policy_info']['policyNo'], dict['public']['invalid_date'], API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "保单失效（一般失效）是否成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, dict['policy_info']['policyNo'], API0000_diy().logger_count_time(begin_time, end_time))
                print result_str

            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())