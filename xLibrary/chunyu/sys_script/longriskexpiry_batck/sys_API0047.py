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



"""长期险满期批处理:
       step1:sql验证保单是否满足长期险满期终止
       step2:修改服务器时间
       step3:启动长期险满期批处理批处理
             1.登录系统
             2.跑批
             3.判断是否跑批成功（是否保单终止）:
                 1)综合查询_查询按钮接口
       step3:关闭长期险满期批处理批处理     
             1.登出系统
       step4:定义轨迹信息+检查点信息
             1.定义轨迹信息
             2.定义检查点信息
"""
class sys_API0047:

    def __init__(self):
        pass


    @func_set_timeout(300)#设定函数超执行时间
    def longriskexpiry_batck(self, expiryDate, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            space_times = 0   #日志打印空格次数
            if dict['logInfo']['job'][0:14] == 'complex_scenes':   #复杂场景
                space_times = 2
            else:
                space_times = 0
            dict['public']['space_times'] = space_times
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '长期险满期批处理开始(预计耗时:120s)'))
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

            """step1.判断保单是否满足长期险满期终止条件"""
            is_success = ''
            message = ''
            unit = "系统-长期险满期批处理_判断保单是否满足长期险满期终止条件 "   #节点
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            policyNo = dict['policy_info']['policyNo']   #保单号
            sql = "SELECT e.`POLICY_NO`,e.`POLICY_ID`,p.`EXPIRY_DATE` FROM t_pa_policy_product p,t_pa_expiry_plan e WHERE p.`POLICY_ID`=e.`POLICY_ID` AND p.`PRODUCT_ID`= e.`PRODUCT_ID` AND p.`LIABILITY_STATE`!='03' AND e.PAY_STATUS='1' AND e.`EXPIRY_DATE`<'" + expiryDate + "' AND e.`POLICY_NO`='" + policyNo + "'"  
            #调用原子脚本    
            cursor = API0000_diy().db_conf(env_name,'wift_pa')
            cursor.execute(sql)
            result = cursor.fetchall()
            if len(result) == 0:
                is_success = False
                message = '保单不满足长期险满期终止条件，请检查！（满期终止条件为：1.保单非终止状态。2.保单的生存金派发状态为已派发完成。3.跑批日期晚于保单满期日期。）'
            else:
                is_success = True
                message = ''
            assert is_success == True


            """step1.3:验证录入用户是否可正常登录系统"""
            #节点初始化
            is_success = ''
            message = ''
            unit = "系统-长期险满期批处理_验证录入用户是否可正常登录系统"   #节点
            #验证用户是否可正常登录系统
            rs = API0000_diy().verify_userlogin(env_name, username_entry, interface_ip)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True


            """step2:修改服务器时间"""
            #节点初始化
            is_success = ''
            message = ''
            unit = "系统-长期险满期批处理_修改服务器时间"   #节点
            #调用原子脚本
            dict = sys_API0002().Modify_servertime(expiryDate, dict['logInfo']['job'], dict)  
            # 加入断言
            assert dict['logInfo']['code'] == '1'

            """step3:启动长期险满期批处理"""
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            begin_time1 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*启用长期险满期批处理3021开始(预计耗时:60s)'))
            """0.登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-长期险满期批处理_登录系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username_entry, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            dict['public']['magicX'] = magicX
            assert is_success == True
             
            for j in range(0,60):
                #节点初始化
                is_success = ''
                unit = '系统-启动长期险满期批处理批处理'  # 节点
                message = ''
                if j in (0,5,10):
                    #1.启动长期险满期批处理接口
                    batchSystem = 'PA'
                    jobId = '3021'
                    isEnable = 'Y'
                    jobName = '长期险满期批处理'   #批处理任务名称
                    jobName = urllib.quote(jobName)
                    response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
                    #获取所需响应值
                    if response['success'] == True and response['message'] == '[长期险满期批处理]更新成功':
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '长期险满期批处理启动失败'
                    assert is_success == True

                    #2.提交长期险满期批处理接口
                    #dict获取数据+定义数据
                    policyNo = dict['policy_info']['policyNo']   #保单号
                    business_date = expiryDate
                    #调用原子脚本
                    response = API0000_pa().saveBatchSubmit(magicX, interface_ip, batchSystem, jobId, policyNo, business_date)
                    #获取所需响应值
                    if response['success'] == True:
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '长期险满期批处理提交失败'
                    # 加入断言
                    assert is_success == True

                    time.sleep(2)

                #5.判断保单是否满期终止
                sql1 = "select POLICY_STATUS from t_pa_policy where POLICY_NO='" + policyNo + "'"
                #调用原子脚本    
                cursor = API0000_diy().db_conf(env_name,'wift_pa')
                cursor.execute(sql1)
                result1 = cursor.fetchall()
                if str(result1[0][0]) == '03':
                    is_success = True
                    message = ''
                    break
                else:
                    is_success = False
                    message = '保单未满期终止！'
                    time.sleep(2)
                    continue

            #断言
            assert is_success == True
            end_time1 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*启用长期险满期批处理2、4结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time1, end_time1)))


            """step4:关闭批处理"""
            begin_time2 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*关闭长期险满期批处理2、4开始(预计耗时:60s)'))

            #节点初始化
            is_success = ''
            unit = '系统-长期险满期批处理_关闭长期险满期批处理'  # 节点
            message = ''
            #（1）关闭续期预收费用记录表接口
            batchSystem = 'PA'
            jobId = '3021'
            isEnable = 'N'
            jobName = '长期险满期批处理'   #批处理任务名称
            jobName = urllib.quote(jobName)
            response = API0000_pa().saveBatchJob(magicX, interface_ip, batchSystem, jobId, isEnable, jobName)
            #获取所需响应值
            if response['success'] == True and response['message'] == '[长期险满期批处理]更新成功':
                is_success = True
                message = ''
            else:
                is_success = False
                message = '长期险满期批处理关闭失败'

            # 加入断言
            assert is_success == True
            end_time2 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*(space_times+1) + '*关闭长期险满期批处理2、4结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time2, end_time2)))


            #登出系统
            #节点初始化
            is_success = ''
            unit = '系统-长期险满期批处理_登出系统'  # 节点
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
            calc_longriskexpiry_batck = {}
            #生存金派发信息存入dict['check']['calc_longriskexpiry_batck']中
            calc_longriskexpiry_batck['apply_date'] = expiryDate   
            calc_longriskexpiry_batck['payment'] = ''   
            calc_longriskexpiry_batck['msg'] = ''   
            dict['check']['calc_longriskexpiry_batck'].append(calc_longriskexpiry_batck)
            """2.定义轨迹信息"""
            track_info = {'trackType':'longriskexpiry_batck', 'trackTime':expiryDate, 'trackData':{'payment':''}, 'msg': ''}
            dict['track_info'].append(track_info)   #存入轨迹信息
            #存入dict
            dict['logInfo']['code'] = '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '长期险满期批处理结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
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
            calc_longriskexpiry_batck = {}
            #生存金派发信息存入dict['check']['calc_longriskexpiry_batck']中
            calc_longriskexpiry_batck['apply_date'] = expiryDate   #新契约收费金额
            calc_longriskexpiry_batck['payment'] = ''   #新契约收费金额
            calc_longriskexpiry_batck['msg'] = msg   #新契约收费金额
            dict['check']['calc_longriskexpiry_batck'].append(calc_longriskexpiry_batck)
            """2.定义轨迹信息"""
            track_info = {'trackType':'longriskexpiry_batck', 'trackTime':expiryDate, 'trackData':{'payment':''}, 'msg': message}
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
        job = 'longriskexpiry_batck'   #场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = 'uat4'
            env_name = env_name.encode('utf-8')
            policyNo = '8088615170332368'   #保单号3254
            expiryDate = '2031-08-06'   #满期终止日期
            username_entry = 'xcy1'   #登录用户名
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo = ''   
                expiryDate = ''   
                username_entry = ''  
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','policyNo','expiryDate','username_entry']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo = rs[2][1]   #保单号
                expiryDate = rs[2][2]   #派发日期
                username_entry = rs[2][3]   #登录用户名
       #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name,'expiryDate':expiryDate}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)
        #4.定义dict
        dict = {'execNo': execNo, 'policy_info':{'policyNo':policyNo},'public': {'env_name':env_name, 'username_entry':username_entry, 'interface_ip':interface_ip, 'magicX':''}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'', 'job':job}, 'track_info': [], 'check':{'calc_longriskexpiry_batck':[]}, 'track_change':[]}
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
            dict = sys_API0047().longriskexpiry_batck(expiryDate, dict)
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
                    print ('派发日期：' + expiryDate).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '保单生存金派发是否成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('派发日期：' + expiryDate).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "保单生存金派发是否成功：成功,,环境：%s,,保单号：%s,,派发日期：%s,,耗时：%s" % (env_name, dict['policy_info']['policyNo'], expiryDate, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "保单生存金派发是否成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,派发日期：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, dict['policy_info']['policyNo'], expiryDate, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())







