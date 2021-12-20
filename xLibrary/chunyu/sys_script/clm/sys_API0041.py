# coding=utf-8

import sys
import time
import urllib
import logging
import pymysql
import requests
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002



"""理赔:
       step1:理赔报案:
             1.理赔报案-登录系统
             2.理赔报案-保单查询接口
             3.理赔报案-保单查询提交接口
             4.理赔报案-报案事故信息保存接口
             5.理赔报案-报案事故信息提交接口
       step2:理赔立案:

       step3:理赔理算:

"""
class sys_API0041:

    def __init__(self):
        pass


    @func_set_timeout(300)#设定函数超执行时间
    def clm(self, apply_date, dict):
        """系统理赔:
               step1:理赔
               step2:复核+收费（转进账单）
               step3:定义轨迹信息+检查点信息:
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            space_times = 0   #日志打印空格次数
            if dict['logInfo']['job'][0:14] == 'complex_scenes':   #复杂场景
                space_times = 2
            else:
                space_times = 0
            dict['public']['space_times'] = space_times
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '理赔_开始(预计耗时:60s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            resultData = []
            payment = 0

            #step0:验证用户+修改服务器时间
            dict = self.clm_prepare(apply_date, dict)
            assert dict['logInfo']['code'] == '1'

            #step1：理赔报案
            dict = self.clm_register(apply_date, dict)
            assert dict['logInfo']['code'] == '1'

            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '理赔_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_review'])
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*运行异常-用户解锁'))
                dict['public']['magicX'] = ''
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_review'])
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*运行异常-用户解锁'))
                dict['public']['magicX'] = ''
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*执行时间超时退出'))
        finally:
            #step3:定义轨迹信息+检查点信息:
            pass
        return dict


    #验证用户+修改服务器时间
    @func_set_timeout(120)#设定函数超执行时间
    def clm_prepare(self, apply_date, dict):
        """验证用户+修改服务器时间：
            step1:验证理赔录入用户、复核用户是否可正常登录系统
            step2:判断是否需要修改服务器时间
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            magicX = ''
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            job = dict['logInfo']['job'] 
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*理赔-验证用户是否可正常登陆_开始(预计耗时:30s)'))

            """step1:验证理赔录入用户、复核用户是否可正常登录系统"""
            #节点初始化
            is_success = ''
            message = ''
            unit = '系统-验证理赔录入用户、复核用户是否可正常登录系统'   #节点标识
            #验证理赔录入用户
            rs = API0000_diy().verify_userlogin(env_name, dict['public']['username_entry'], dict['public']['interface_ip'])
            is_success = rs[0]   #是否成功标识
            message = rs[1]   #信息
            # 加入断言
            assert is_success == True

            #验证理赔复核用户
            rs = API0000_diy().verify_userlogin(env_name, dict['public']['username_review'], dict['public']['interface_ip'])
            is_success = rs[0]   #是否成功标识
            message = rs[1]   #信息

            # 加入断言
            assert is_success == True
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*理赔-验证用户是否可正常登陆结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))


            #step2:判断是否需要修改服务器时间
            dict = sys_API0002().Modify_servertime(apply_date, job, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            # 加入断言
            assert is_success == True 
            #存入dict
            dict['logInfo']['code'] = '1'   #记录无异常标识
            dict['public']['magicX'] = ''
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username_entry)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



    @func_set_timeout(120)#设定函数超执行时间
    def clm_register(self, apply_date, dict):
        """step1:理赔报案
                 1.理赔报案-登录系统
                 2.理赔报案-保单查询接口
                 3.理赔报案-保单查询提交接口
                 4.理赔报案-报案事故信息保存接口
                 5.理赔报案-报案事故信息提交接口
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            magicX = ''
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*理赔报案_开始(预计耗时:30s)'))
            """1.理赔报案用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔报案用户登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username_entry = dict['public']['username_entry']    #理赔用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username_entry, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            dict['public']['magicX'] = magicX
            # 加入断言
            assert is_success == True  

            """2.理赔报案_保单查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔报案_保单查询接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            policyNo = dict['policy_info']['policyNo']    #保单号
            caseType = '1'   #保单类型：1-个险
            organCode = ''
            #调用原子脚本
            response = API0000_clm().Register_queryPolicy(magicX, interface_ip, policyNo, caseType) 
            #获取所需响应值
            message = response['message']
            assert response['isSuccess'] == True
            if len(response['resultData']) > 0:
                is_success = True
                message = ''
                custId = str(response['resultData'][0]['customerInfo']['customerId'])  #被保人id
                arouseName = urllib.quote(response['resultData'][0]['customerInfo']['name'].encode('utf-8'))  #被保人
                arouseCertiType = response['resultData'][0]['customerInfo']['certiType']   #证件类型
                arouseCertiNo = response['resultData'][0]['customerInfo']['certiCode']   #证件号
                arouseSex = response['resultData'][0]['customerInfo']['gender']   #性别
                arouseBirthday = response['resultData'][0]['customerInfo']['birthday']   #出生日期
                telephone = response['resultData'][0]['customerInfo']['mobile']
                productName = urllib.quote(response['resultData'][0]['productName'].encode('utf-8'))   #险种名称
                organName = urllib.quote(response['resultData'][0]['organName'].encode('utf-8'))   #机构名称
                grpPolicyNo = response['resultData'][0]['grpPolicyNo'] 
                if grpPolicyNo == None:
                    grpPolicyNo = ''
                productId = str(response['resultData'][0]['productId'])   #险种名称
                organCode1 = response['resultData'][0]['organCode']   #机构代码
                for i in range(0,len(organCode1)):
                    if organCode1[i] == ' ':
                        organCode = organCode + '+'
                    else:
                        organCode = organCode + organCode1[i]
            else:
                is_success = False
                message = '对不起，查询不到相关数据！'
                arouseName = ''
                arouseCertiType = ''
                arouseCertiNo = ''
                arouseSex = ''
                arouseBirthday = ''
                productName = ''
                grpPolicyNo = '' 
                telephone = ''
                productId = ''
                organCode = ''
            # 加入断言
            assert is_success == True 


            """3.理赔报案-保单查询提交接口"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔报案-保单查询提交接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_clm().Register_registerInfo(magicX, interface_ip, arouseName, arouseCertiType, arouseCertiNo, arouseSex, arouseBirthday, telephone, policyNo, productName, organName, grpPolicyNo, productId, organCode, caseType) 
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = '' 
                partitionIndi = str(response['others']['partitionIndi'])
                reportNo = str(response['others']['reportNo'])
                accCustId = str(response['others']['accCustId'])
                mobilePhone = str(response['others']['mobilePhone'])
            else:
                message = response['message'] 
                partitionIndi = ''  
                reportNo = ''
                accCustId = ''
                telephone = ''
                mobilePhone = ''
            # 加入断言
            assert is_success == True


            """4.理赔报案-报案事故信息保存接口"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔报案-报案事故信息保存接口'  # 节点
            message = ''
            #定义
                #报案人信息
            reportName = urllib.quote('熊超')    #报案人姓名
            report_telephone = '17893454545'    #报案人电话
            reportChannel = '01'    #报案渠道。01-电话报案；02-柜面报案；03-微信报案；99-其他方式
            relationShip = '99'   #报案人与出险人关系。00-本人；01-配偶；02-父母；03-子女；05-兄弟姐妹；06-雇主；07-雇员；08-祖父母、外祖父母；09-祖孙、外祖孙；10-监护人；11-被监护人；12-朋友；13-委托；98-未知；99-其他
            reportDate = apply_date   #实际报案日期
                #报案事故信息
            accidentDate = apply_date    #事故日期。YYYY-MM-DD
            claimType = '01'    #案件类型。01-身故；02-伤残；03-重疾；04-医疗；05-轻症疾病；06-豁免；07-全残；08-中症疾病；09-疾病终末期；10-病变手术疾病
            hospitalCode2 = ''   #医院姓名：北京中医药大学东直门医院
            hospitalCode = ''   #医院代码:11010140000444911A2101
            claimNature = '2'    #事故原因。1-疾病；2-意外
            deathCause = '02'    #死亡原因。01-疾病；02-意外；03-自杀；04-他杀；05-其他
            provinceCode = '110000'    #事故地点省
            cityCode = '110100'    #事故地点市
            districtCode = '110114'    #区/县/乡
            accStreet = urllib.quote('建国门东大街110号')    #详细地址
            accDesc = urllib.quote('报案')     #事故描述            
            reportRemark = urllib.quote('报案')    #备注
            #调用原子脚本
            response = API0000_clm().Register_doFinishSubmit(magicX, interface_ip, magicX, interface_ip, partitionIndi , accidentDate, claimNature, cityCode, accDesc, claimType, deathCause, districtCode, reportRemark, hospitalCode2, hospitalCode , provinceCode, accStreet, reportNo, reportName, report_telephone, reportChannel, relationShip, reportDate, accCustId, arouseName, arouseCertiType, arouseCertiNo, arouseSex, mobilePhone, arouseBirthday, arouseAge, policyNo, custId) 
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = '' 
            else:
                message = response['message'] 
            # 加入断言
            assert is_success == True


            """5.理赔报案-报案事故信息提交接口"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔报案-报案事故信息提交接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_clm().Register_doReportSubmit(magicX, interface_ip, partitionIndi, relationShip, accidentDate, claimNature, provinceCode, accStreet, reportNo, reportName, reportChannel, deathCause, cityCode, accDesc, mobilePhone, claimType, claimamout, districtCode, reportRemark, telephone, arouseName, arouseCertiType, arouseCertiNo, custId, policyNo) 
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = '' 
            else:
                message = response['message'] 
            # 加入断言
            assert is_success == True


            """7.理赔-登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔_报案用户登出系统'  # 节点
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
            dict['logInfo']['code'] = '1'   #记录无异常标识
            dict['public']['magicX'] = ''
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*理赔报案_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username_entry)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict


    @func_set_timeout(60)#设定函数超执行时间
    def pa_review(self, apply_date, dict):
        """step2:复核+收费（转进账单）
                1.复核用户登录系统
                2.复核-公共工作池查询接口 
                3.复核-工作池领取任务接口
                4.复核提交接口

                收费（转进账单）:
                step5: BCP支付方式查询接口
                step6: BCP支付方式变更转进账单接口
                7.柜面收付费查询接口
                8.柜面收付费保存接口
                9.柜面收付费审核接口
                10.登出系统
        """
        #初始化
        try:
            begin_time1 = datetime.datetime.now()   #开始时间
            #初始化
            payment = 0
            magicX = ''
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*复核_开始(预计耗时:10s)'))
            """1.复核用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔_复核用户登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username_entry = dict['public']['username_review']    #复核用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name,username_entry, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            dict['public']['magicX'] = magicX
            # 加入断言
            assert is_success == True            

            """2.复核-公共工作池查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔_复核-公共工作池查询接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            policyNo = dict['policy_info']['policyNo']    #保单号
            #调用原子脚本
            response = API0000_pa().queryCsInfoList(magicX, interface_ip, policyNo) 
            #获取所需响应值
            is_success = response['isSuccess']
            if is_success:
                message = ''
                changeId = response['resultData'][0]['changeId']
                partitionIndi = str(response['resultData'][0]['partitionIndi'])
                serviceCode = response['resultData'][0]['serviceCode']
                applyNo = response['resultData'][0]['applyNo']
            else:
                message = response['message']
                changeId = ''
                partitionIndi = ''
                serviceCode = ''
                applyNo = ''
            # 加入断言
            assert is_success == True
            
            """3.复核-工作池领取任务接口"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔_复核-工作池领取任务接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            changeIds = changeId   #组装changeIds
            #调用原子脚本
            response = API0000_pa().processLockCsChange(magicX, interface_ip, changeIds)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            # 加入断言
            assert is_success == True
            
            """4.复核提交接口"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔_复核提交接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_pa().csEffect(magicX, interface_ip, changeId, applyNo, serviceCode, partitionIndi, policyNo)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            # 加入断言
            assert is_success == True
            end_time1 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*复核_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time1, end_time1)))


            """收付费"""
            begin_time2 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*收付费_开始(预计耗时:20s)'))
            """1.BCP支付方式查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔_BCP支付方式查询接口'  # 节点
            message = ''
            #调用原子脚本
            for i in range(0, 60):
                response = API0000_payment().queryBankOffsetSum(magicX, interface_ip, policyNo)
                if response['resultData'] == []:
                    is_success = False
                    message = '未查到保单BCP支付方式'
                    offsetSumId = ''
                    time.sleep(1)
                else:
                    is_success = True
                    message = ''
                    offsetSumId = response['resultData'][0]['offsetSumId']
                    break
            assert is_success == True
            
            """2.BCP支付方式变更转进账单接口"""
            #节点初始化
            is_success = ''
            unit = '系统-BCP支付方式变更转进账单接口'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_payment().doChange2Cash(magicX, interface_ip, offsetSumId)   #转进账单
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            if is_success == False:
                rs = API0000_payment().doChange2Cash1(magicX, interface_ip, offsetSumId)   #转现金交账单
                is_success = rs[0]
                message = rs[1]
            assert is_success == True

            """3.柜面收付费查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔_柜面收付费查询接口'  # 节点
            message = ''
            for k in range(0,120): 
                #调用原子脚本
                rs = API0000_payment().FeeQuery(magicX, interface_ip, policyNo)
                #获取所需响应值
                is_success = rs[0]
                message = rs[1]
                resultData = rs[2]
                if len(resultData)>0:
                    break
                else:
                    time.sleep(0.5)
            payment = float(resultData[0]['amount'])   #收付费金额
            #断言
            assert is_success == True

            """4.柜面收付费保存接口"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔_柜面收付费保存接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            bankEndorse = '123123'  # 银行凭证号码
            feeConfirmDate = apply_date   #收费日期（申请日期）
            internalAccount = '08-400301040007336'  # 公司收费账号
            internalBankCode = '05'  # 收费机构
            feeChannel = 'CASH-10017-AR'  # 支付通道
            cashOrgId = '10017'  # 机构名称
            internalBankName = '中国农业银行绥化市大有支行'  # 所属银行
            #调用原子脚本
            rs = API0000_payment().CashApproveInfoSave(magicX, interface_ip, resultData, bankEndorse, feeConfirmDate, internalAccount, internalBankCode, feeChannel, cashOrgId, internalBankName)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            # 加入断言
            assert is_success == True

            """5.柜面收付费审核接口"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔_柜面收付费审核接口'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_payment().finishFeeFlow(magicX, interface_ip, resultData, bankEndorse, feeConfirmDate, internalAccount, internalBankCode, feeChannel, internalBankName)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            # 加入断言
            assert is_success == True
    
            """6.复核-登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-理赔_理赔-登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX,interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            # 加入断言
            assert is_success == True
            
            """存入dict"""
            dict['logInfo']['code'] = '1'   #记录无异常标识
            dict['public']['magicX'] = ''
            #保单终止、终止原因
            dict['policy_info']['policy_status'] = '03'   
            dict['policy_info']['end_reason'] = '03' 
            #主险/附加险终止
            for i in range(0, len(dict['policy_info']['main_risk_info'])):
                dict['policy_info']['main_risk_info'][i]['liability_state'] = '03'
            for i in range(0, len(dict['policy_info']['sub_risk_info'])):
                dict['policy_info']['sub_risk_info'][i]['liability_state'] = '03'  

            end_time2 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*收付费_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time2, end_time2)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username_entry)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return payment, dict



if __name__ == "__main__":
    try:
        begin_time = datetime.datetime.now()   #开始时间
        #1.初始化
        is_run = True   #是否执行python脚本 
        msg = ''   #执行python脚本前存在的错误信息
        job = 'clm'   #场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = 'uat4'
            env_name = env_name.encode('utf-8')
            policyNo = '8088615170367168'
            apply_date = '2021-12-20'   #申请日期
            username_entry = 'xcy1'   #理赔用户名
            username_review = 'xcy1'   #复核用户名
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo = ''
                apply_date = ''
                username_entry = ''
                username_review = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','policyNo','apply_date','username_entry','username_review']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo = rs[2][1]   #保单号
                apply_date = rs[2][2]   #申请日期
                username_entry = rs[2][3]   #理赔用户
                username_review = rs[2][4]   #复核用户
       #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name,'apply_date':apply_date}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = {'execNo': execNo, 'policy_info':{'policyNo':policyNo, 'main_risk_info':[{'liability_state':''}], 'sub_risk_info':[{'liability_state':''}]},'public': {'env_name':env_name, 'username_entry':username_entry, 'username_review':username_review, 'interface_ip':interface_ip, 'magicX':''}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'', 'job':job}, 'track_info': [], 'check':{'calc_clm':[]}, 'track_change':[]}
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
            #dict = sys_API0002().Modify_servertime(apply_date, job, dict)
            #assert dict['logInfo']['code'] == '1'   #断言是否异常
            dict = sys_API0041().clm(apply_date, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_review'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_review'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
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
                    print '是否理赔成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + policyNo).decode('utf-8').encode('gb2312')
                    print ('申请日期：' + apply_date).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print ('是否理赔成功：不成功').decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + policyNo).decode('utf-8').encode('gb2312')
                    print ('申请日期：' + apply_date).decode('utf-8').encode('gb2312')
                    print '不成功原因:'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "是否理赔成功：成功,,环境：%s,,保单号：%s,,申请日期：%s,,耗时：%s" % (env_name, policyNo, apply_date, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "是否理赔成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,申请日期：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, policyNo, apply_date, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())

