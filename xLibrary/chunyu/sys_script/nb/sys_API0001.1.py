#coding=utf-8

import os
import sys
import time
import json
import random
import logging
import datetime
import traceback
from openpyxl import load_workbook
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *
from xLibrary.chunyu.sys_script.nb.sys_API0001 import sys_API0001
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002


class sys_API0001_1:

    def __init__(self):
        pass

    @func_set_timeout(180)#设定函数超执行时间 
    def nb(self,env_name, dict):
        """
            step1:存储新契约数据(包含两部分：定义dict、excel获取数据存入dict)
            step2:判断是否需要修改服务器时间
            step3:新契约录入
            step4:新契约复核
            step5:新契约核保
            step6:新契约收费
            step7:新契约回执
            step8:定义轨迹信息+检查点信息
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('新契约出单_开始(预计耗时:不需修改系统时间60s;需修改系统时间1分50s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            job = dict['logInfo']['job']   #场景名
            #获取dict数据
            applicationDate = dict['policy_info']['applicationDate']   #投保日期
            #dict中加入契约类型
            dict['nb_type'] = 'sys_API0001.1'   #契约类型：sys_API0001.1-新契约出单脚本（录入代理人+合作网点+法定受益人）
            #step1:验证代理人+验证契约录入用户、复核用户是否可正常登录系统+存储新契约数据
            dict = sys_API0001().store_nbdata(env_name, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #step2:判断是否需要修改服务器时间
            dict = sys_API0002().Modify_servertime(applicationDate, job, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #step3:新契约录入
            rs = sys_API0001().nb_entry(dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            proposalId = rs[0]
            dict = rs[1]
            #step4:新契约复核
            rs = sys_API0001().nb_review(proposalId, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            magicX = rs[0]
            others = rs[1]
            dict = rs[2]
            if others == '2':   #是否进入人工核保
                #step5:新契约核保
                dict = sys_API0001().nb_uw(magicX, others, dict)
                assert dict['logInfo']['code'] == '1'   #断言是否异常
            #step6:新契约收费
            dict = sys_API0001().nb_payment(magicX, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #step7:新契约回执
            dict = sys_API0001().nb_receipt(magicX, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            dict['logInfo']['unit'] = ''
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('新契约出单_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'   #dict['logInfo']['code']记录异常标识
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n') + traceback.format_exc())
            #异常场景-登出系统（防止与用户被挂起）
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_review'])
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
                dict['public']['magicX'] = ''
        except func_timeout.exceptions.FunctionTimedOut:
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出（可能他人改时间重启服务请检查！）'))
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。（可能他人改时间重启服务请检查！）' + dict['logInfo']['msg']
            #异常场景-登出系统（防止与用户被挂起）
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_review'])
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
                dict['public']['magicX'] = ''
        finally:
            if dict['logInfo']['code'] == '1':
                dict = sys_API0001().save_check_info(dict)
        return dict



        
if __name__ == "__main__":   
    try:
        begin_time = datetime.datetime.now()   #开始时间
        #1.初始化
        is_run = True   #是否执行python脚本 
        msg = ''   #执行python脚本前存在的错误信息
        job = 'nb'   #场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = 'uat7'
            env_name = env_name.encode('utf-8')
            applicationDate = '2021-12-17'   #投保日期
            username_entry = 'xcy1'   #保全录入用户名
            username_review = 'xcy2'   #保全复核用户名
            agent = '10000001-吴文新'   #代理人；10000001-吴文新 ; DT640164655-蒋诗芸
            partner = 'shengtang-盛唐融信保险代理（北京）有限公司'   #合作网点; shengtang-盛唐融信保险代理（北京）有限公司;2100001-大童保险销售服务有限公司浙江分公司
            filename = r'D:\xLibrary\chunyu\doc\product_life_cycle\product_life_cycle_data.xlsx'   #excel测试数据路径 
            #filename = r'C:\Users\9an02\Desktop\product_life_cycle_data.xlsx'
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                applicationDate = ''   
                username_entry = ''  
                username_review = '' 
                agent = ''
                partner = ''
                filename = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','applicationDate','username_entry','username_review','agent','partner','filename']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                applicationDate = rs[2][1]   #保全申请日期
                username_entry = rs[2][2]   #保全录入用户
                username_review = rs[2][3]   #保全复核用户
                agent = rs[2][4]   #代理人
                partner = rs[2][5]   #合作网点
                filename = rs[2][6]   #excel测试数据路径
        #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name,'applicationDate':applicationDate}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = API0000_diy().define_dict() 
        dict['logInfo']['job'] = job
        dict['logInfo']['msg'] = msg
        dict['public']['env_name'] =  env_name    #环境类型
        dict['policy_info']['applicationDate'] =  applicationDate    #投保日期
        dict['public']['filename'] =  filename    #excel测试数据路径
        dict['public']['username_entry'] = username_entry
        dict['public']['username_review'] = username_review
        dict['public']['agent'] = agent.strip()
        dict['public']['partner'] = partner.strip()
        dict['public']['interface_ip'] = API0000_diy().ip_conf(env_name)   #环境ip
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
            dict = sys_API0001_1().nb(env_name, dict)
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_review'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行中出现异常-对登录用户进行解锁'))
            dict['public']['magicX'] = ''
    except func_timeout.exceptions.FunctionTimedOut:    #函数超时异常的捕捉
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出（可能他人改时间重启服务请检查！）'))
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。（可能他人改时间重启服务请检查！）' + dict['logInfo']['msg']
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_review'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
    finally:
        try:
            end_time = datetime.datetime.now()   #记录结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:   #windows系统平台
                if dict['logInfo']['code'] == '1':
                    print '是否出单成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('投保日期：' + applicationDate).decode('utf-8').encode('gb2312')
                    print ('录入的代理人：' + agent.strip()).decode('utf-8').encode('gb2312')
                    print ('录入的合作网点：' + partner.strip()).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('是否修改时间重启应用：' + dict['track_change'][-1]['trackData']['is_Modify_flag'] + '(耗时:' + dict['track_change'][-1]['trackData']['consume_time'] + ')').decode('utf-8').encode('gb2312')
                    print ('新契约出单耗时：' + API0000_diy().logger_count_time1(API0000_diy().logger_count_time(begin_time, end_time), dict['track_change'][-1]['trackData']['consume_time'])).decode('utf-8').encode('gbk')
                    print ('总耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '是否出单成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('投保日期：' + applicationDate).decode('utf-8').encode('gb2312')
                    print ('录入的代理人：' + agent.strip()).decode('utf-8').encode('gb2312')
                    print ('录入的合作网点：' + partner.strip()).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:    #非windows系统平台
                if dict['logInfo']['code'] == '1':
                    result_str = "是否出单成功：成功,,环境：%s,,投保日期：%s,,录入的代理人：%s,,录入的合作网点：%s,,保单号：%s,,是否修改时间重启应用：%s(耗时：%s):,,新契约出单耗时：%s,,总耗时：%s" % (env_name, applicationDate, agent.strip(), partner.strip(), dict['policy_info']['policyNo'], dict['track_change'][-1]['trackData']['is_Modify_flag'], dict['track_change'][-1]['trackData']['consume_time'], API0000_diy().logger_count_time1(API0000_diy().logger_count_time(begin_time, end_time), dict['track_change'][-1]['trackData']['consume_time']), API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "是否出单成功：不成功,,不成功原因：%s,,环境：%s,,投保日期：%s,,录入的代理人：%s,,录入的合作网点：%s,,保单号：%s,,总耗时：%s" % (dict['logInfo']['msg'], env_name, applicationDate, agent.strip(), partner.strip(), dict['policy_info']['policyNo'], API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())







