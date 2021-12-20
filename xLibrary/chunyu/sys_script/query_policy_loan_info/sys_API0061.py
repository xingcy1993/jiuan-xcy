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



"""查询保单下贷款信息数据（录入计算日期+改系统时间）:
       step1:验证录入用户是否可正常登录系统
       step2:修改服务器时间
       step3:登录系统
       step4：:综合查询_查询按钮接口
       step5:登出系统
       step6:创建html文件，以表格形式展示
"""
class sys_API0061:

    def __init__(self):
        pass


    @func_set_timeout(300)#设定函数超执行时间
    def query_policy_loan_info(self, apply_date, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            space_times = 0   #日志打印空格次数
            if dict['logInfo']['job'][0:14] == 'complex_scenes':   #复杂场景
                space_times = 2
            else:
                space_times = 0
            dict['public']['space_times'] = space_times
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '查询保单下贷款信息数据开始(预计耗时:120s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            is_success = False
            message = ''
            unit = '查询保单下贷款信息数据'
            magicX = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']
            username_entry = dict['public']['username_entry']
            interface_ip = dict['public']['interface_ip']
            policyNo = dict['policy_info']['policyNo']
            list = []

            """step1.1验证录入用户是否可正常登录系统"""
            #节点初始化
            is_success = ''
            message = ''
            unit = "系统-验证录入用户是否可正常登录系统"   #节点
            #验证用户是否可正常登录系统
            rs = API0000_diy().verify_userlogin(env_name, username_entry, interface_ip)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True


            """step1.2数据库下保单是否存在"""
            #连接数据库
            cursor = API0000_diy().db_conf(env_name,'wift_pa')   #连接数据库
            sql = "select * from t_pa_policy where policy_no = '" + policyNo + "'"
            cursor.execute(sql)
            result = cursor.fetchall()
            if result == []:
                is_success = False
                message = '数据库下查询不到保单号存在险种！'
            else:
                is_success = True
                message = ''
            # 加入断言
            assert is_success == True 


            """step2:修改服务器时间"""
            #节点初始化
            is_success = ''
            message = ''
            unit = "修改服务器时间"   #节点
            #调用原子脚本
            dict = sys_API0002().Modify_servertime(apply_date, dict['logInfo']['job'], dict)  
            # 加入断言
            assert dict['logInfo']['code'] == '1'


            """step3:登录系统"""
            #节点初始化
            is_success = ''
            unit = '登录系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username_entry, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            dict['public']['magicX'] = magicX
            assert is_success == True


            """step4：综合查询"""
            #1.综合查询_查询按钮接口
            #节点初始化
            is_success = ''
            unit = '综合查询_查询按钮接口'  # 节点
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

            #2.综合查询-保全贷款信息sheet页接口
            #节点初始化
            is_success = ''
            unit = '综合查询-保全贷款信息sheet页接口'  # 节点
            message = ''
            #调用原子脚本:
            response = API0000_queryPolicy().loanmain(magicX, interface_ip, policyNo, proposalNo, proposalId, policyId)
            #获取所需响应值
            if response['isSuccess'] == True and len(response['resultData']) > 0:
                is_success = True
                message = ''
                resultData = response['resultData']
            elif response['isSuccess'] == True and len(response['resultData']) == 0:
                is_success = False
                message = '保单下不存在贷款记录！'
                resultData = response['resultData']
            elif response['isSuccess'] == False:
                is_success = False
                message = response['message']
                resultData = '' 
            #断言
            assert is_success == True

            """step5：登出系统"""
            #节点初始化
            is_success = ''
            unit = '登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX, interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            dict['public']['magicX'] = ''

            #存入dict
            for i in range(0, len(resultData)):
                list.append({})
                product_code = str(resultData[i]['productCode'])   #产品编码
                product_name = str(resultData[i]['productName'])     #产品名称
                loanPrincipal = str(resultData[i]['loanPrincipal'])   #贷款本金
                rate = str(resultData[i]['rate'])   #利率
                capitalizedInterest = str(resultData[i]['capitalizedInterest'])   #资本化利息
                loanInterest = str(resultData[i]['loanInterest'])   #未结利息
                sum = str(float(loanPrincipal) + float(capitalizedInterest) + float(loanInterest))   #本利和
                endingOfLoanTerm = str(resultData[i]['endingOfLoanTerm'])   #贷款周期截止日期
                dealTime = str(resultData[i]['dealTime'])   #结算日期

                list[-1]['product_code'] = product_code   #产品编码
                list[-1]['product_name'] = product_name   #产品名称
                list[-1]['loanPrincipal'] = loanPrincipal   #贷款本金
                list[-1]['rate'] = rate   #利率
                list[-1]['capitalizedInterest'] = capitalizedInterest   #资本化利息
                list[-1]['loanInterest'] = loanInterest   #未结利息
                list[-1]['sum'] = sum   #本利和
                list[-1]['endingOfLoanTerm'] = endingOfLoanTerm   #贷款周期截止日期
                list[-1]['dealTime'] = dealTime   #结算日期
            dict['public']['list'] = list

            """step6:创建html文件，以表格形式展示"""
            dict = self.create_html(dict)  
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            dict['logInfo']['code'] = '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '查询保单下贷款信息数据结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
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
            file = open(html_file_path, 'a')
            rowspan = str(len(list))

            #第一行
            message1 = """<html>
    <head>
        <meta charset='utf-8'>
        <title>精算数据</title>
    </head>
    <body>
        <table table border='1' bordercolor='black' cellspacing='0' cellpadding='5'>
            <tr width='4000'>
                <td>产品编码</td>
                <td>产品名称</td>
                <td>贷款本金</td>
                <td>利率</td>
                <td>资本化利息</td>
                <td>未结利息</td>
                <td>本利和</td>
                <td>贷款周期截止日期</td>
                <td>结算日期</td> 
            </tr>""" 

            #写入
            file.write(message1)

            #第三行及更多行
            for j in range(0, len(list)):
                message = """
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
            </tr>
            """%(list[j]['product_code'], list[j]['product_name'], list[j]['loanPrincipal'], list[j]['rate'], list[j]['capitalizedInterest'], list[j]['loanInterest'], list[j]['sum'], list[j]['endingOfLoanTerm'], list[j]['dealTime'])
                file.write(message)
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
        job = 'query_policy_loan_info'   #场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = '预生产'
            env_name = env_name.encode('utf-8')
            policyNo = '8088550236692768'   #保单号
            apply_date = '2022-01-01'   #计算日期
            username_entry = 'xcy1'   #登录用户名
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo = ''   
                apply_date = ''   
                username_entry = ''  
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','policyNo','apply_date','username_entry']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo = rs[2][1]   #保单号
                apply_date = rs[2][2]   #计算日期
                username_entry = rs[2][3]   #登录用户名
       #校验录入字段是否符合规范
        key_dict = {'env_name':env_name,'apply_date':apply_date}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)
        #3.1定义logging文件路径
        if 'win' in sys.platform:
            logging_filename = 'D:\\xLibrary\\chunyu\\%s.html' % str(execNo)
            #判断windows是否存在某文件，存在则删除文件
            if os.path.exists(logging_filename):
                os.remove(logging_filename)
        else:
            logging_filename = '/data/xServer/xReport/%s.html' % str(execNo)
        #3.2定义logging格式
        logging.basicConfig(level=logging.WARNING , format='%(message)s  &nbsp&nbsp&nbsp&nbsp%(asctime)s <br/><br/>', filename=logging_filename, filemode='a')
        
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = {'execNo': execNo, 'policy_info':{'policyNo':policyNo},'public': {'env_name':env_name, 'html_file_path':logging_filename, 'username_entry':username_entry, 'interface_ip':interface_ip, 'magicX':''}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'', 'job':job}, 'track_info': [], 'check':{'calc_survivalFee':[]}, 'track_change':[]}

        #6.执行脚本
        if is_run == True:
            dict = sys_API0061().query_policy_loan_info(apply_date, dict)
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
                    print '查询保单下贷款信息数据是否成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('计算日期：' + apply_date).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '查询保单下贷款信息数据是否成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('计算日期：' + apply_date).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "查询保单下贷款信息数据是否成功：成功,,环境：%s,,保单号：%s,,计算日期：%s,,耗时：%s" % (env_name, dict['policy_info']['policyNo'], apply_date, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "查询保单下贷款信息数据是否成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,计算日期：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, dict['policy_info']['policyNo'], apply_date, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())







