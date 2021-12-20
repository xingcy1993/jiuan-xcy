# coding=utf-8

import sys
import time
import copy
import logging
import pymysql
import requests
import openpyxl
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from openpyxl import load_workbook
from xLibrary.chunyu.API0000 import *
from xLibrary.chunyu.sys_script.nb.sys_API0001 import sys_API0001
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002
from xLibrary.chunyu.sys_script.renew.sys_API0004 import sys_API0004
from xLibrary.chunyu.sys_script.loan.sys_API0007 import sys_API0007
from xLibrary.chunyu.sys_script.loan_repayment.sys_API0008 import sys_API0008
from xLibrary.chunyu.sys_script.hesitation_tb.sys_API0009 import sys_API0009
from xLibrary.chunyu.sys_script.tb.sys_API0010 import sys_API0010
from xLibrary.chunyu.sys_script.send_survivalFee.sys_API0011 import sys_API0011
from xLibrary.chunyu.sys_script.single_invalidation_bacth.sys_API0017 import sys_API0017
from xLibrary.chunyu.sys_script.revival.sys_API0018 import sys_API0018
from xLibrary.chunyu.sys_script.reduce_amount.sys_API0024 import sys_API0024
from xLibrary.chunyu.sys_script.reissue.sys_API0030 import sys_API0030
from xLibrary.chunyu.sys_script.csReversal.sys_API0032 import sys_API0032



"""复杂场景造数组件（非新契约开始）
step1:获取excel数据+组装业务场景列表
step2:校验业务场景列表内信息是否有误
step3:执行脚本
"""
class sys_API0036:

    def __init__(self):
        pass


    def complex_scenes(self, dict):
        """复杂场景造数组件（非新契约开始）:
               step1:获取excel数据+组装业务场景列表
               step2:校验业务场景列表内信息是否有误
               step3:执行脚本
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('复杂场景造数组件（非新契约开始）_开始'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            #step1:获取excel数据+组装业务场景列表
            dict = self.get_excel_date(dict)  
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            business_list = dict['public']['business_list']
            
            #step2:校验业务场景列表内信息是否有误
            dict = self.check_business_list(dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #step3:执行脚本
            dict = self.run_business_list(dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #结束
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('复杂场景造数组件（非新契约开始）_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry_review'])
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
                dict['public']['magicX'] = ''
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry_review'])
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
                dict['public']['magicX'] = ''
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
        finally:
            pass
        return dict



    #获取excel数据+组装业务场景列表
    @func_set_timeout(30)#设定函数超执行时间
    def get_excel_date(self, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*获取excel数据+组装业务场景列表_开始(预计耗时:5s)'))
            #初始化
            is_success = ''
            unit = '获取excel数据+组装业务场景列表'  # 节点
            message = ''
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''            
            filename = dict['public']['filename']   #excel路径
            business_list = []   #定义业务场景列表
            dict['public']['business_list'] = business_list
            #1.获取excel文件对象
            wb = load_workbook(filename)
            #2.获取sheet页对象
            sh = wb['复制场景业务列表']   #产品生命周期sheet
            #3.读取并组装业务场景列表。status为0-未执行；1-执行结束
            for i in range(6,26):
                if sh['B' + str(i)].value != None:
                    business_list.append({'business':sh['B' + str(i)].value, 'row':i, 'status':'0'})
            #4.获取业务场景所需的数据
            for j in range(0, len(business_list)):
                #4-1:(1)判断录入数据1是否录入
                if business_list[j]['business'] in ('保单续期（年交保单，支持多期）','生存金派发','保单贷款','保单贷款还款(清偿)','犹豫期退保','退保','减保','保单补发','保单复效','保全回退'):
                    if sh['C' + str(business_list[j]['row']+1)].value == '' or sh['C' + str(business_list[j]['row']+1)].value == None:
                        is_success = False
                        message = '第' + str(business_list[j]['row']+1) + '行的' + business_list[j]['business'] + '"录入数据1"未录入。'
                    assert is_success != False
                #4-1:(2)判断录入数据2是否录入
                if business_list[j]['business'] in ('保单贷款','减保','保单补发'):
                    if sh['D' + str(business_list[j]['row']+1)].value == '' or sh['D' + str(business_list[j]['row']+1)].value == None:
                        is_success = False
                        message = '第' + str(business_list[j]['row']+1) + '行的' + business_list[j]['business'] + '"录入数据2"未录入。'
                    assert is_success != False
                #4-1:(3)判断录入数据3是否录入
                if business_list[j]['business'] in ('保单补发'):
                    if sh['E' + str(business_list[j]['row']+1)].value == '' or sh['E' + str(business_list[j]['row']+1)].value == None:
                        is_success = False
                        message = '第' + str(business_list[j]['row']+1) + '行的' + business_list[j]['business'] + '"录入数据3"未录入。'
                    assert is_success != False

                #4-2:(1)录入数据1存入dict
                if business_list[j]['business'] in ('保单贷款','保单贷款还款(清偿)','犹豫期退保','退保','减保','保单补发','保单复效','保全回退'):
                    business_list[j]['apply_date'] = sh['C' + str(business_list[j]['row']+1)].value   #保全申请日期
                elif business_list[j]['business'] == '保单续期（年交保单，支持多期）':
                    business_list[j]['times_renew'] = sh['C' + str(business_list[j]['row']+1)].value   #续期次数
                elif business_list[j]['business'] == '生存金派发':
                    business_list[j]['sendDate'] = sh['C' + str(business_list[j]['row']+1)].value   #派发日期 
                #4-2:(2)录入数据2存入dict
                if business_list[j]['business'] == '保单贷款':
                    business_list[j]['loanApplyAmount'] = sh['D' + str(business_list[j]['row']+1)].value   #保全贷款金额
                elif business_list[j]['business'] == '减保':
                    business_list[j]['adjustAmount'] = sh['D' + str(business_list[j]['row']+1)].value   #减保金额
                elif business_list[j]['business'] == '保单补发':
                    business_list[j]['reissueReason'] = sh['D' + str(business_list[j]['row']+1)].value   #补发原因
                #4-2:(3)录入数据3存入dict
                if business_list[j]['business'] == '保单补发':
                    business_list[j]['reissueType'] = sh['E' + str(business_list[j]['row']+1)].value   #补发类型     
            #5.关闭excel文件
            wb.close() 
            #结束
            dict['logInfo']['code'] = '1'
            is_success = True
            dict['public']['business_list'] = business_list
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*获取excel数据+组装业务场景列表_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict




    #校验业务场景列表内信息是否有误
    @func_set_timeout(30)#设定函数超执行时间
    def check_business_list(self,dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*校验业务场景列表内信息是否有误_开始(预计耗时:5s)'))
            #初始化
            is_success = ''
            unit = '校验业务场景列表内信息'  # 节点
            message = ''
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            business_list = dict['public']['business_list']   #业务场景列表
            #1.得到业务场景-录入数据列表
            business_list_temp = copy.deepcopy(business_list)
            for i in range(0,len(business_list_temp)):
                del business_list_temp[i]['business']
                del business_list_temp[i]['row']

            #2.遍历业务场景-录入数据列表并校验
            for j in range(0,len(business_list_temp)):
                key_dict = business_list_temp[j]
                rs = API0000_diy().checkdata_json_check1(key_dict)
                is_success = rs[0]
                message = rs[1] + '(' + '第' + str(business_list[j]['row']) + '行的' + business_list[j]['business'] + ')'
                assert is_success == True
            #结束
            dict['logInfo']['code'] = '1'
            is_success = True
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*校验业务场景列表内信息是否有误_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



    def run_business_list(self,dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行复杂业务场景_开始'))
            #初始化
            is_success = ''
            unit = '执行复杂业务场景'  # 节点
            message = ''
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            business_list = dict['public']['business_list']   #业务场景列表
            #执行复杂业务场景
            for i in range(0,len(business_list)):
                if business_list[i]['business'] == '保单续期（年交保单，支持多期）':
                    #定义场景
                    dict['logInfo']['job'] = dict['logInfo']['job'][0:14] + '-' + 'renew'  
                    #执行业务场景
                    dict = sys_API0004().renew(int(business_list[i]['times_renew']), dict)
                    assert dict['logInfo']['code'] == '1'
                elif business_list[i]['business'] == '保单失效(一般失效)':
                    #定义场景
                    dict['logInfo']['job'] = dict['logInfo']['job'][0:14] + '-' + 'single_invalidation_bacth'
                    #定义场景
                    dict = sys_API0017().single_invalidation_bacth(dict)
                    assert dict['logInfo']['code'] == '1'
                elif business_list[i]['business'] == '生存金派发':
                    #定义场景
                    dict['logInfo']['job'] = dict['logInfo']['job'][0:14] + '-' + 'send_survivalFee'
                    #定义场景
                    dict = sys_API0011().send_survivalFee(business_list[i]['sendDate'], dict)
                    assert dict['logInfo']['code'] == '1' 
                elif business_list[i]['business'] == '保单贷款':
                    #定义场景
                    dict['logInfo']['job'] = dict['logInfo']['job'][0:14] + '-' + 'loan'   
                    #执行业务场景
                    dict = sys_API0002().Modify_servertime(business_list[i]['apply_date'], dict['logInfo']['job'], dict)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                    dict = sys_API0007().loan(business_list[i]['apply_date'], business_list[i]['loanApplyAmount'], dict)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                elif business_list[i]['business'] == '保单贷款还款(清偿)':
                    #定义场景
                    dict['logInfo']['job'] = dict['logInfo']['job'][0:14] + '-' + 'loan_repayment' 
                    #执行业务场景  
                    dict = sys_API0002().Modify_servertime(business_list[i]['apply_date'], dict['logInfo']['job'], dict)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                    dict = sys_API0008().loan_repayment(business_list[i]['apply_date'], dict)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                elif business_list[i]['business'] == '犹豫期退保':
                    #定义场景
                    dict['logInfo']['job'] = dict['logInfo']['job'][0:14] + '-' + 'hesitation_tb'  
                    #执行业务场景 
                    dict = sys_API0002().Modify_servertime(business_list[i]['apply_date'], dict['logInfo']['job'], dict)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                    dict = sys_API0009().hesitation_tb(business_list[i]['apply_date'], dict)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                elif business_list[i]['business'] == '退保':
                    #定义场景
                    dict['logInfo']['job'] = dict['logInfo']['job'][0:14] + '-' + 'tb' 
                    #执行业务场景
                    dict = sys_API0002().Modify_servertime(business_list[i]['apply_date'], dict['logInfo']['job'], dict)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                    dict = sys_API0010().tb(business_list[i]['apply_date'], dict)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                elif business_list[i]['business'] == '减保':
                    #定义场景
                    dict['logInfo']['job'] = dict['logInfo']['job'][0:14] + '-' + 'reduce_amount'   
                    #执行业务场景
                    dict = sys_API0002().Modify_servertime(business_list[i]['apply_date'], dict['logInfo']['job'], dict)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                    dict = sys_API0024().reduce_amount(business_list[i]['apply_date'], business_list[i]['adjustAmount'], dict)
                    assert dict['logInfo']['code'] == '1'
                elif business_list[i]['business'] == '保单补发':
                    #定义场景
                    dict['logInfo']['job'] = dict['logInfo']['job'][0:14] + '-' + 'reissue'   
                    #执行业务场景
                    dict = sys_API0002().Modify_servertime(business_list[i]['apply_date'], dict['logInfo']['job'], dict)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                    dict = sys_API0030().reissue(business_list[i]['apply_date'], business_list[i]['reissueReason'], business_list[i]['reissueType'], dict)
                    assert dict['logInfo']['code'] == '1'
                elif business_list[i]['business'] == '保单复效':
                    #定义场景
                    dict['logInfo']['job'] = dict['logInfo']['job'][0:14] + '-' + 'revival'   
                    #执行业务场景
                    dict = sys_API0002().Modify_servertime(business_list[i]['apply_date'], dict['logInfo']['job'], dict)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                    dict = sys_API0018().revival(business_list[i]['apply_date'], 0, 0, dict)
                    assert dict['logInfo']['code'] == '1'
                elif business_list[i]['business'] == '保全回退':
                    #定义场景
                    dict['logInfo']['job'] = dict['logInfo']['job'][0:14] + '-' + 'csReversal' 
                    #执行业务场景
                    dict = sys_API0002().Modify_servertime(business_list[i]['apply_date'], dict['logInfo']['job'], dict)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                    dict = sys_API0032().csReversal(business_list[i]['apply_date'], dict)
                    assert dict['logInfo']['code'] == '1'
                business_list[i]['status'] = '1'   #当前组件执行完成
            #结束
            end_time = datetime.datetime.now()   #结束时间
            is_success = True
            message = ''
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行复杂业务场景_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            message = dict['logInfo']['msg']
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
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
        job = 'complex_scenes'

        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = 'uat7'
            env_name = env_name.encode('utf-8')
            policyNo = '8088622620904668'   #保单号
            username_entry = 'xcy1'   #登录系统录入用户
            username_review = 'xcy2'   #登录系统复核用户
            username_review_again = ''   #登录系统复核审核用户
            filename = r'D:\xLibrary\chunyu\doc\product_life_cycle\product_life_cycle_data2.xlsx'   #excel测试数据路径
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo = ''
                username_entry = ''  
                username_review = ''
                username_review_again = ''
                filename = '' 
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','policyNo','username_entry','username_review','username_review_again','filename']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo = rs[2][1]
                username_entry = rs[2][2]   #保全录入用户
                username_review = rs[2][3]   #保全复核用户
                username_review_again = rs[2][4]
                filename = rs[2][5]   #excel测试数据路径
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
        interface_ip = API0000_diy().ip_conf(env_name)
        dict['logInfo'] = {'code':'0', 'msg':msg, 'err':'', 'result':'', 'job':job}
        dict['public']['execNo'] = execNo   #编号
        dict['policy_info']['policyNo'] = policyNo   #保单号
        dict['public']['env_name'] = env_name   #环境类型
        dict['public']['username_entry'] = username_entry   #录入用户
        dict['public']['username_review'] = username_review   #复核用户
        dict['public']['username_review_again'] = username_review_again   #复核审核用户名
        dict['public']['interface_ip'] = interface_ip
        dict['public']['filename'] = filename   #excel路径
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
            #1.获取excel数据+组装生命周期列表
            dict = sys_API0036().complex_scenes(dict)
            assert dict['logInfo']['code'] == '1'
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
            #获取用户录入业务场景及执行完成业务场景
            business_list = dict['public']['business_list']
            business_list_input = ''   #获取用户录入业务场景
            business_list_run = ''   #实际执行完成业务场景
            for i in range(0, len(business_list)):
                #获取用户录入业务场景
                if i == 0:
                    business_list_input = business_list[i]['business']
                else:
                    business_list_input = business_list_input + '+' + business_list[i]['business']   #获取用户录入业务场景
                #实际执行完成业务场景
                if business_list[i]['status'] == '1':
                    if i == 0:
                        business_list_run =  business_list[i]['business']
                    else:
                        business_list_run = business_list_run + '+' + business_list[i]['business']   #实际执行完成业务场景
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:
                if dict['logInfo']['code'] == '1':
                    print '复杂场景造数（非新契约开始）是否成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('用户录入业务场景：' + business_list_input).decode('utf-8').encode('gb2312')
                    print ('执行完成业务场景：' + business_list_run).decode('utf-8').encode('gb2312')
                    print ('保单号：' + policyNo).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print ('复杂场景造数（非新契约开始）是否成功：不成功').decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('用户录入业务场景：' + business_list_input).decode('utf-8').encode('gb2312')
                    print ('执行完成业务场景：' + business_list_run).decode('utf-8').encode('gb2312')
                    print ('保单号：' + policyNo).decode('utf-8').encode('gb2312')
                    print '不成功原因:'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "复杂场景造数（非新契约开始）是否成功：成功,,环境：%s,,用户录入业务场景：%s,,执行完成业务场景：%s,,保单号：%s,,耗时：%s" % (env_name, business_list_input, business_list_run, policyNo, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "复杂场景造数（非新契约开始）是否成功：不成功,,不成功原因：%s,,环境：%s,,用户录入业务场景：%s,,执行完成业务场景：%s,,保单号：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, business_list_input, business_list_run, policyNo, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())







