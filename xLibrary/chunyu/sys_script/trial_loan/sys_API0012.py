# coding=utf-8

import sys
import time
import logging
import requests
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *


"""贷款试算:
    step1：通过保单号查询
        1.登录系统
        2.保全试算接口
        3.登出系统
    step2：创建html文件，以表格形式展示
"""
class sys_API0012:

    def __init__(self):
        pass



    @func_set_timeout(60)#设定函数超执行时间
    def get_actuarial_data(self, dict):
        """获取精算数据（单条获取）:
            step1：通过保全申请号，系统获取精算数据
                1.登录系统
                2.保全试算
                3.登出系统
            step2：创建html文件，以表格形式展示
        """
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''

            #step1:通过保全申请号，系统获取精算数据
            dict = self.query_data(dict)  
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #step2:创建html文件，以表格形式展示
            dict = self.create_html(dict)  
            assert dict['logInfo']['code'] == '1'   #断言是否异常
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                dict['public']['magicX'] = ''
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                dict['public']['magicX'] = ''
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
        finally:
            pass
        return dict



    @func_set_timeout(60)#设定函数超执行时间
    def query_data(self, dict):
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            list = []   #查询的保单精算数据险种列表

            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            policyNo = dict['public']['policyNo']   #保单号
            trial_day = dict['public']['trial_day']   #试算日期
            username_entry = dict['public']['username_entry']    #登录用户

            """step1:登录系统"""
            #节点初始化
            is_success = ''   #是否成功标识
            unit = '登录系统'  # 节点标识
            message = ''   #信息标识
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username_entry, interface_ip)
            #获取所需响应值
            is_success = rs[0]   #是否成功标识
            message = rs[1]   #信息
            magicX = rs[2]   #会话id
            dict['public']['magicX'] = magicX
            # 加入断言
            assert is_success == True
            

            """step2:保全试算"""
            #初始化
            is_success = ''
            unit = '贷款试算接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_pa().trial_loan(env_name, magicX, interface_ip, policyNo, trial_day)
            #获取所需响应值
            is_success = response['isSuccess']
            if is_success:
                message = response['message']
                resultData = response['resultData']
            else:
                message = response['message']
                resultData = ''
                if 'java.util.LinkedHashMap cannot be cast to com.ins.core.model.pa.loan.PaLoanAccountLimitResponse' in message:
                    message = message + '。判断为数据库贷款配置问题，请检查t_pa_loan_rate表，此险种贷款利率是否配置正确！'

            for i in range(0, len(resultData)):
                unit = '贷款试算接口'
                list.append({})
                productName = resultData[i]['productName']   #险种名称
                liabilityState = str(resultData[i]['liabilityState'])   #险种状态
                holderName = resultData[i]['holderName']   #投保人姓名
                insuredName = resultData[i]['insuredName']   #被保人姓名
                sumAssured = resultData[i]['sumAssured']   #保额
                totalPremAf = resultData[i]['totalPremAf']   #保费
                presentPrice = resultData[i]['presentPrice']   #现金价值
                investAmount = resultData[i]['investAmount']   #万能账户余额
                loanAccountAmount = resultData[i]['loanAccountAmount']   #欠款余额
                loanRate = resultData[i]['loanRate']   #贷款利率
                loanAccountLimit = resultData[i]['loanAccountLimit']   #贷款额度

                if str(liabilityState) == '01':
                    liabilityState = '有效'
                elif str(liabilityState) == '02':
                    liabilityState = '中止'
                elif str(liabilityState) == '03':
                    liabilityState = '终止'

                if presentPrice == None:
                    presentPrice = '0'

                if investAmount == None:
                    investAmount = '0'

                list[-1]['productName'] = productName
                list[-1]['liabilityState'] = liabilityState
                list[-1]['holderName'] = holderName
                list[-1]['insuredName'] = insuredName
                list[-1]['sumAssured'] = sumAssured
                list[-1]['totalPremAf'] = totalPremAf
                list[-1]['presentPrice'] = presentPrice
                list[-1]['investAmount'] = investAmount
                list[-1]['loanAccountAmount'] = loanAccountAmount
                list[-1]['loanRate'] = loanRate
                list[-1]['loanAccountLimit'] = loanAccountLimit
            #存入dict
            dict['public']['list'] = list
            # 加入断言
            assert is_success == True


            """step3：登出系统"""
            #节点初始化
            is_success = ''
            unit = '登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX,interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            # 加入断言
            assert is_success == True
            #存入dict
            dict['public']['magicX'] = ''
            dict['logInfo']['code'] = '1'   #记录无异常标识
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username_entry)
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                dict['public']['magicX'] = ''
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



    #生成html文件
    @func_set_timeout(60)#设定函数超执行时间
    def create_html(self, dict):
        try:
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            is_success = ''
            message = ''
            unit = '生成html文件'
            html_file_path = dict['public']['html_file_path']
            list = dict['public']['list']

            #1.创建.html文件
            file = open(html_file_path, 'w')
            rowspan = str(len(list))

            #贷款-第一行+第二行
            message1 = """<html>
    <head>
        <meta charset='utf-8'>
        <title>贷款试算</title>
    </head>
    <body>
        <table table border='2' bordercolor='black' cellspacing='0' cellpadding='5'>
            <tr width='4000'>
                <td>保单号</td>
                <td>险种名称</td>
                <td>险种状态</td>
                <td>投保人姓名</td>
                <td>被保人姓名</td>
                <td>保额</td>
                <td>保费</td>
                <td>现金价值</td>
                <td>万能账户余额</td>
                <td>欠款余额</td>
                <td>贷款利率</td>
                <td>贷款额度</td>
            </tr>""" 
            file.write(message1)

            #第二行及更多行
            for j in range(0, len(list)):
                message2 = """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            """%(dict['public']['policyNo'], list[j]['productName'],list[j]['liabilityState'],list[j]['holderName'],list[j]['insuredName'],list[j]['sumAssured'],list[j]['totalPremAf'],list[j]['presentPrice'],list[j]['investAmount'],list[j]['loanAccountAmount'],list[j]['loanRate'],list[j]['loanAccountLimit'])
                file.write(message2)

            file.write('\n' + '        </table> ' + "\n")
            file.write('    </body> ' + "\n")
            file.write('</html> ' + "\n")
            #关闭html文件
            file.close()
            is_success = True
            dict['logInfo']['code'] = '1'    
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
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
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = '预生产'
            env_name = env_name.encode('utf-8')
            policyNo = '8088627328722168'   #保单号
            trial_day = '2021-10-01'   #试算日期
            username_entry = 'xcy1'   #登录系统用户名
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo = ''   
                trial_day = ''
                username_entry = ''  
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','policyNo','trial_day','username_entry']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo = rs[2][1]   #保单号
                trial_day = rs[2][2]   #试算日期
                username_entry = rs[2][3]   #登录用户
       #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name, 'trial_day':trial_day}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)
        #4.1定义logging文件路径
        if 'win' in sys.platform:
            logging_filename = 'D:\\xLibrary\\chunyu\\%s.html' % str(execNo)
            #判断windows是否存在某文件，存在则删除文件
            if os.path.exists(logging_filename):
                os.remove(logging_filename)
        else:
            logging_filename = '/data/xServer/xReport/%s.html' % str(execNo) 
        #4.2定义logging格式
        logging.basicConfig(level=logging.WARNING , format='%(message)s  &nbsp&nbsp&nbsp&nbsp%(asctime)s <br/><br/>', filename=logging_filename, filemode='a')
        #5.定义dict
        if is_run == True:
            msg = ''
        dict = {'execNo': execNo, 'public': {'env_name':env_name, 'html_file_path':logging_filename, 'username_entry':username_entry, 'interface_ip':interface_ip, 'policyNo':policyNo, 'trial_day':trial_day, 'magicX':''}, 'logInfo': {'code':'0', 'msg': msg, 'err':'', 'result':'', 'unit':''}}
        #6.执行脚本
        if is_run == True:
            dict = sys_API0012().get_actuarial_data(dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            dict['public']['magicX'] = ''
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            dict['public']['magicX'] = ''
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:
                if dict['logInfo']['code'] == '1':
                    print '贷款试算是否成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + policyNo).decode('utf-8').encode('gb2312')
                    print ('试算日期：' + trial_day).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print ('贷款试算是否成功：不成功').decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + policyNo).decode('utf-8').encode('gb2312')
                    print ('试算日期：' + trial_day).decode('utf-8').encode('gb2312')
                    print '不成功原因:'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "贷款试算是否成功：成功,,环境：%s,,保单号：%s,,试算日期：%s,,耗时：%s" % (env_name, policyNo, trial_day, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "贷款试算是否成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,试算日期：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, policyNo, trial_day, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())



