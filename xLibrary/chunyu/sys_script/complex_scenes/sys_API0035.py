# coding=utf-8

import sys
import time
import logging
import pymysql
import requests
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *
from xLibrary.chunyu.sys_script.nb.sys_API0001 import sys_API0001
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002
from xLibrary.chunyu.sys_script.loan.sys_API0007 import sys_API0007



"""
一、获取excel数据+组装生命周期列表:   get_excel_date(filename)-->出参business_list, sum_business, product_life_cycle_list
step1:获取excel数据
step2:获取去重复后全部业务场景(business_list)
step3:获取业务数总和数(sum_business)
step4:组装生命周期列表(product_life_cycle_list,格式[[{'business':'','apply_date':''},{},{}],[{},{},{}]],product_life_cycle_list[i]为每一年;product_life_cycle_list[i][j]每一年内每个业务)

二、创建并组装场景脚本.py文件:    create_process_file(filename, business_list, product_life_cycle_list) 
step1:excel获取业务参数
step2:创建场景脚本.py文件
step3:组装场景脚本.py文件
step4:执行场景脚本.py文件

三、创建并组装测试报告.html文件
step1:生成测试报告
step2:执行脚本
"""
class sys_API0035:

    def __init__(self):
        pass





if __name__ == "__main__":
    try:
        begin_time = datetime.datetime.now()   #开始时间
        #1.初始化
        is_run = True   #是否执行python脚本 
        msg = ''   #执行python脚本前存在的错误信息

        applicationDate = '2017-03-01'   #投保日期

        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = 'uat4'
            env_name = env_name.encode('utf-8')
            username_entry = 'xcy1'   #登录系统录入用户
            username_review = 'xcy2'   #登录系统复核用户 
            filename = r'D:\xLibrary\chunyu\doc\product_life_cycle\product_life_cycle_data.xlsx'   #excel测试数据路径
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                username_entry = ''  
                username_review = '' 
                filename = '' 
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','username_entry','username_review']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                username_entry = rs[2][1]   #保全录入用户
                username_review = rs[2][2]   #保全复核用户
                filename = rs[2][3]   #excel测试数据路径
       #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = API0000_diy().define_dict() 
        dict['logInfo'] = {'code':'0', 'msg':msg, 'err':'', 'result':'', 'unit':''}
        dict['policy_info']['applicationDate'] = applicationDate
        dict['public']['env_name'] = env_name
        dict['public']['username_entry'] = username_entry
        dict['public']['username_review'] = username_review
        dict['public']['filename'] = filename
        dict['public']['filename'] = filename
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
            #1.新契约出单
            dict = sys_API0001().nb(env_name, applicationDate, dict)
            policyNo = dict['policy_info']['policyNo']  # 保单号
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #2.保单贷款
            apply_date = '2017-06-01'
            job = 'loan'
            loanApplyAmount = '100'
            dict = sys_API0002().Modify_servertime(apply_date, job, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            dict = sys_API0007().loan(apply_date, loanApplyAmount, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:
                if dict['logInfo']['code'] == '1':
                    print '复杂场景造数（新契约开始）是否成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + policyNo).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print ('复杂场景造数（新契约开始）是否成功：不成功').decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + policyNo).decode('utf-8').encode('gb2312')
                    print '不成功原因:'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "复杂场景造数（新契约开始）是否成功：成功,,环境：%s,,保单号：%s,,耗时：%s" % (env_name, policyNo, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "复杂场景造数（新契约开始）是否成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, policyNo, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())







