# coding=utf-8

import sys
import time
import random
import logging
import pymysql
import requests
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *


"""获取精算数据（理赔查询，单条获取）:
    step1：通过保全申请号，系统获取精算数据
        1.登录系统
        2.综合查询，进行理赔查询
        3.登出系统
    step2：创建html文件，以表格形式展示
"""
class sys_API0049:

    def __init__(self):
        pass



    @func_set_timeout(60)#设定函数超执行时间
    def get_actuarial_data(self, dict):
        """获取精算数据（单条获取）:
            step1：通过保全申请号，系统获取精算数据
                1.登录系统
                2.通过保全申请号，进行理赔查询
                3.综合查询
                4.登出系统
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

            is_success = ''
            message = ''
            unit = ''
            policyNo = ''   #保单号
            productName = ''   #险种名
            applicationDate = ''   #投保日期
            effectiveDate = ''   #生效日
            policyDeliveryDate = ''   #回执日
            chargeMode = ''   #交费方式
            birthday = ''   #被保人生日
            gender = ''   #性别
            sumAssured = ''   #保额
            totalPremAF = ''   #保费
            applyType = ''   #案件类型
            accReason = ''   #事故原因
            accDate = ''   #理赔事故日
            reportDate = ''   #理赔申请日
            calcAmount = ''   #理赔金额
            payAmount = ''   #赔付金额
            list = []

            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username_entry = dict['public']['username_entry']    #登录用户
            policyNo = dict['public']['policyNo']   #保单号
            caseNo = dict['public']['caseNo']   #案件号
            #连接数据库
            cursor = API0000_diy().db_conf(env_name, 'wift_pa') 
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
            

            """step2:综合查询"""
            #节点1：综合查询-查询按钮接口
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            is_success = ''   #是否成功标识
            unit = '综合查询-查询按钮接口'  # 节点标识
            message = ''   #信息标识
            #调用原子脚本
            response = API0000_queryPolicy().queryPolicy(magicX, interface_ip, policyNo)
            isSuccess = response['isSuccess']   #是否成功标识
            resultData = response['resultData']
            #获取所需响应值
            if isSuccess == True and len(resultData) != 0:
                is_success = True
                message = ''
            else:
                is_success = False
                message = '综合查询未查到结果!'
            if is_success == True:
                proposalNo = response['resultData'][0]['proposalNo']
                proposalId = response['resultData'][0]['proposalId']
                policyId = response['resultData'][0]['policyId']
            else:
                proposalNo = ''
                proposalId = ''
                policyId = ''
            #存入dict
            dict['public']['proposalNo'] = proposalNo
            dict['public']['proposalId'] = proposalId
            dict['public']['policyId'] = policyId
            # 加入断言
            assert is_success == True

            #节点2：综合查询-保单信息-日期信息接口
            #初始化
            is_success = ''
            unit = '综合查询-保单信息-日期信息接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_queryPolicy().policyDetail(magicX, interface_ip, policyNo, proposalNo, proposalId, policyId)
            is_success = response['success']
            #获取所需响应值
            if is_success:
                message = response['message']
                applicationDate = response['others']['applicationDate'].replace('-','/')   #投保日期
                effectiveDate = response['others']['effectiveDate'].replace('-','/')   #生效日
                policyDeliveryDate = response['others']['policyDeliveryDate'].replace('-','/')   #回执日
            else:
                message = response['success']
                applicationDate = ''
                effectiveDate = ''
                policyDeliveryDate = ''
            #存入dict
            dict['public']['applicationDate'] = applicationDate
            dict['public']['effectiveDate'] = effectiveDate
            dict['public']['policyDeliveryDate'] = policyDeliveryDate
            # 加入断言
            assert is_success == True


            #节点3：综合查询-客户信息sheet页_被保人信息接口
            #初始化
            is_success = ''
            unit = '综合查询-客户信息sheet页_被保人信息接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_queryPolicy().customerByRole3(magicX, interface_ip, policyNo, policyId, proposalId, proposalNo)
            #获取所需响应值
            is_success = response['isSuccess']
            if is_success:
                message = ''
                birthday = response['resultData'][0]['birthday'].replace('-','/')   #出生日期
                gender = response['resultData'][0]['gender']   #性别
                if gender == '0':
                    gender = '男'
                elif gender == '1':
                    gender = '女'
            else:
                message = response['message']
                birthday = ''
                gender = ''
            #存入dict
            dict['public']['birthday'] = birthday
            dict['public']['gender'] = gender
            # 加入断言
            assert is_success == True

            #节点4：综合查询-险种信息sheet_险种信息查询接口
            #初始化
            is_success = ''
            unit = '综合查询-险种信息sheet_险种信息查询接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_queryPolicy().queryProduct(magicX, interface_ip, policyNo, policyId, proposalId, proposalNo)
            #获取所需响应值
            resultData = response['resultData']
            if response['isSuccess'] == True and len(resultData) > 0:
                message = ''
                is_success = True
                for i in range(0, len(resultData)):
                    list.append({})
                    list[-1]['productId'] = resultData[i]['productId']
                    list[-1]['productName'] = resultData[i]['productName']
                    list[-1]['sumAssured'] = resultData[i]['sumAssured']
                    list[-1]['totalPremAF'] = resultData[i]['totalPremAF']
                    if resultData[i]['units'] != None:
                        list[-1]['sumAssured'] = str(resultData[i]['sumAssured']) + r'(' + str(int(resultData[i]['units'])) + r'份)'
                    #数据库查询产品的交费方式
                    sql = "select a.pay_period from t_pa_policy_product a, t_pa_policy b where a.policy_id=b.policy_id and b.policy_no='" + policyNo + "' and a.product_id = '" + str(resultData[i]['productId']) + "'"
                    unit = '保全查询-满期领取-数据库查询产品缴费方式'
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    chargeMode = result[0][0]
                    if chargeMode == 'S':
                        chargeMode = '趸交' 
                    elif chargeMode == 'Y':
                        chargeMode = '年交'  
                    elif chargeMode == 'M':
                        chargeMode = '月交'
                    list[-1]['chargeMode'] = chargeMode
                    list[-1]['applyType'] = ''
                    list[-1]['accReason'] = ''
                    list[-1]['accDate'] = ''
                    list[-1]['reportDate'] = ''
                    list[-1]['calcAmount'] = ''
                    list[-1]['payAmount'] = ''
            else:
                is_success = False
                message = response['message']

            # 加入断言
            assert is_success == True

            #节点5：综合查询-理赔基本信息sheet页接口
            #初始化
            is_success = ''
            unit = '综合查询-综合查询-理赔基本信息sheet页接口'  # 节点
            message = ''
            businessNo = ''
            #调用原子脚本
            response = API0000_queryPolicy().claimlist(magicX, interface_ip, policyNo, proposalNo, proposalId, policyId)
            #获取所需响应值
            is_success = response['isSuccess']
            if is_success:
                resultData = response['resultData']
            else:
                resultData = []
            if len(resultData) > 0:
                is_success = True
                message = ''
                for i in range(0, len(resultData)):
                    if str(resultData[i]['caseNo']) == caseNo:
                        businessNo = str(resultData[i]['id'])
                        productId = str(resultData[i]['productId'])
                        break
            else:
                is_success = False
                message = response['message']
                businessNo = ''
                productId = ''
            # 加入断言
            assert is_success == True


            #节点6：综合查询-理赔基本信息sheet页接口-理赔详情信息
            #初始化
            is_success = ''
            unit = '综合查询-理赔基本信息sheet页接口-理赔详情信息'  # 节点
            message = ''
            r = str(random.uniform(0,1)) + str(random.randint(1000,9999))
            #调用原子脚本
            response = API0000_queryPolicy().claimdetail(magicX, interface_ip, r, policyNo, proposalNo, proposalId, policyId, businessNo)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                applyType = response['others']['applyType']   #案件类型
                accReason = response['others']['accReason']   #事故原因
                accDate = response['others']['accDate']   #理赔事故日
                reportDate = response['others']['reportDate']   #理赔申请日
                calcAmount = response['others']['calcAmount']   #理赔金额
                payAmount = response['others']['payAmount']   #赔付金额
                #案件类型：码值转中文
                if applyType == '01':
                    applyType = '身故'
                elif applyType == '02':
                    applyType = '伤残'
                elif applyType == '03':
                    applyType = '重疾'
                elif applyType == '04':
                    applyType = '高残'
                elif applyType == '05':
                    applyType = '全残'
                elif applyType == '06':
                    applyType = '一般失能'
                elif applyType == '07':
                    applyType = '重度失能'
                elif applyType == '08':
                    applyType = '医疗'
                elif applyType == '09':
                    applyType = '失业'
                elif applyType == '10':
                    applyType = '特种疾病'
                elif applyType == '11':
                    applyType = '豁免'
                elif applyType == '99':
                    applyType = '其他'
                #事故原因：码值转中文
                if accReason == '1':
                    accReason = '疾病'
                elif accReason == '2':
                    accReason = '意外'
            else:
                applyType = ''   #案件类型
                accReason = ''   #事故原因
                accDate = ''   #理赔事故日
                reportDate = ''   #理赔申请日
                calcAmount = ''   #理赔金额
                payAmount = ''   #赔付金额
            # 加入断言
            assert is_success == True
            #存入dict
            for i in range(0, len(list)):
                if str(list[i]['productId']) == productId:
                    list[i]['applyType'] = applyType
                    list[i]['accReason'] = accReason
                    list[i]['accDate'] = accDate
                    list[i]['reportDate'] = reportDate
                    list[i]['calcAmount'] = calcAmount
                    list[i]['payAmount'] = payAmount
            dict['public']['list'] = list

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
            applicationDate = dict['public']['applicationDate']
            effectiveDate = dict['public']['effectiveDate']
            policyDeliveryDate = dict['public']['policyDeliveryDate']
            birthday = dict['public']['birthday']
            gender = dict['public']['gender']
            policyNo = dict['public']['policyNo']
            #1.创建.html文件
            file = open(html_file_path, 'w')
            rowspan = str(len(list))

            #第一行+第二行
            message1 = """<html>
    <head>
        <meta charset='utf-8'>
        <title>精算数据</title>
    </head>
    <body>
        <table table border='1' bordercolor='black' cellspacing='0' cellpadding='5'>
            <tr width='4000'>
                <td>保单号</td>
                <td>险种名称</td>
                <td>投保日期</td>
                <td>生效日</td>
                <td>回执日</td>
                <td>交费方式</td>
                <td>被保人生日</td>
                <td>性别</td>
                <td>保额</td>
                <td>保费</td>
                <td>案件类型</td>
                <td>事故原因</td>
                <td>理赔事故日</td>
                <td>理赔申请日</td>
                <td>理赔金额</td>
                <td>赔付金额</td>
            </tr>            
            <tr>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td rowspan="%s">%s</td>
                <td rowspan="%s">%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>""" %(rowspan,policyNo,list[0]['productName'],rowspan,applicationDate,rowspan,effectiveDate,rowspan,policyDeliveryDate,list[0]['chargeMode'],rowspan,birthday,rowspan,gender,list[0]['sumAssured'],list[0]['totalPremAF'],list[0]['applyType'],list[0]['accReason'],list[0]['accDate'],list[0]['reportDate'],list[0]['calcAmount'],list[0]['payAmount'])

            #写入
            file.write(message1)

            #第三行及更多行
            for j in range(1, len(list)):
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
                <td>%s</td>
            </tr>
            """%(list[j]['productName'], list[j]['chargeMode'], list[j]['sumAssured'], list[j]['totalPremAF'], list[j]['applyType'], list[j]['accReason'], list[j]['accDate'], list[j]['reportDate'], list[j]['calcAmount'], list[j]['payAmount'])
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
        job = 'get_actuarial_data_clm'   #场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = 'uat7'
            env_name = env_name.encode('utf-8')
            policyNo = '8088617698036768'    #保单号
            caseNo = '71177040817579053'   #案件号
            username_entry = 'xcy1'   #系统登录用户名
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo = ''   
                caseNo = ''
                username_entry = ''  
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','policyNo','caseNo','username_entry']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo = rs[2][1]   #保单号
                caseNo = rs[2][2]   #案件号
                username_entry = rs[2][3]   #登录用户
       #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name}   #录入字段中待校验字典
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
        dict = {'execNo': execNo, 'public': {'env_name':env_name, 'html_file_path':logging_filename, 'username_entry':username_entry, 'interface_ip':interface_ip, 'policyNo':policyNo, 'caseNo':caseNo, 'magicX':''}, 'logInfo': {'code':'0', 'msg': msg, 'err':'', 'result':'', 'job':job}}
        #6.执行脚本
        if is_run == True:
            dict = sys_API0049().get_actuarial_data(dict)
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
                    print '精算数据是否获取成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + policyNo).decode('utf-8').encode('gb2312')
                    print ('案件号：' + caseNo).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print ('精算数据是否获取成功：不成功').decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + policyNo).decode('utf-8').encode('gb2312')
                    print ('案件号：' + caseNo).decode('utf-8').encode('gb2312')
                    print '不成功原因:'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "精算数据是否获取成功：成功,,环境：%s,,保单号：%s,,案件号：%s,,耗时：%s" % (env_name, policyNo, caseNo, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "精算数据是否获取成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,案件号：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, policyNo, caseNo, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())



