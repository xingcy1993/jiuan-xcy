#coding=utf-8

import os
import sys
import time
import json
import random
import logging
import datetime
import traceback
import threading
from openpyxl import load_workbook
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *
from xLibrary.chunyu.sys_script.nb.sys_API0001 import sys_API0001
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002


#新契约多线程出单 
class sys_API0001_2:

    def __init__(self):
        pass

    @func_set_timeout(180)#设定函数超执行时间 
    def nb(self,env_name, dict):
        """
            step1:存储新契约数据(包含两部分：定义dict、excel获取数据存入dict)
            step2:判断是否需要修改服务器时间
            step3:登录系统-新契约录入用户、复核与用户
            多线程
            step4:新契约录入
            step5:新契约复核
            step6:新契约核保
            step7:新契约收费
            step8:新契约回执
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
            thread_result_list = []
            magicX1 = ''
            magicX2 = ''
            #获取dict数据
            applicationDate = dict['policy_info']['applicationDate']   #投保日期
            nb_time = dict['public']['nb_time']   #出单次数
            #dict中加入契约类型
            dict['nb_type'] = 'sys_API0001.2'   #契约类型：sys_API0001.2-新契约出单脚本（多线程出单）
            #step1:验证代理人+验证契约录入用户、复核用户是否可正常登录系统+存储新契约数据
            dict = sys_API0001().store_nbdata(env_name, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #step2:判断是否需要修改服务器时间
            dict = sys_API0002().Modify_servertime(applicationDate, job, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #step3:登录系统-新契约录入用户、复核与用户
            dict = self.login(dict)
            magicX1 = dict['public']['magicX1']   #录入用户会话id
            magicX2 = dict['public']['magicX2']   #复核用户会话id
            #创建线程
            threads = []
            for i in range(0, int(nb_time)):
                threads.append(self.myThread("Thread-" + str(i+1), dict))

            for t in threads:
                t.setDaemon(True)
                t.start()

            #join()方法，用于等待线程终止
            for t in threads:
                t.join()
                thread_result_list.append(t.get_result())

            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登出系统-新契约录入用户、复核用户_开始'))
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登出系统-新契约录入用户、复核用户_结束'))
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('新契约出单_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n') + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出（可能他人改时间重启服务请检查！）'))
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。（可能他人改时间重启服务请检查！）' + dict['logInfo']['msg']
        finally:
            if thread_result_list == []:
                pass
            else:
                dict = {}
        return thread_result_list, magicX1, magicX2, dict



    """登录系统-新契约录入用户、复核与用户"""
    @func_set_timeout(120)#设定函数超执行时间
    def login(self, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统-新契约录入用户、复核用户_开始(预计耗时:5s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            magicX1 = ''
            magicX2 = ''
            """step1:登录系统-新契约录入用户"""
            #节点初始化
            is_success = ''   #是否成功标识
            unit = '节点：系统-新契约录入_登录系统'  # 节点标识
            message = ''   #信息标识
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username1 = dict['public']['username_entry']    #新契约录入用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username1, interface_ip)
            #获取所需响应值
            is_success = rs[0]   #是否成功标识
            message = rs[1]   #信息
            magicX1 = rs[2]   #会话id
            #断言
            assert is_success == True
            dict['public']['magicX1'] = magicX1

            """step2:登录系统-新契约复核用户"""
            username2 = dict['public']['username_review']    #新契约复核用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username2, interface_ip)
            #获取所需响应值
            is_success = rs[0]   #是否成功标识
            message = rs[1]   #信息
            magicX2 = rs[2]   #会话id
            #断言
            assert is_success == True
            dict['public']['magicX2'] = magicX2

            dict['logInfo']['code'] = '1' 
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统-新契约录入用户、复核与用户_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0' 
            dict['logInfo']['err'] = unit + str(e)
            #记录日志
            logging.warning(API0000_diy().text_conversion('异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



    """多线程"""
    class myThread (threading.Thread):   #继承父类threading.Thread
        def __init__(self, name, dict):
            threading.Thread.__init__(self)
            self.name = name
            self.dict = dict
     
        def run(self):     #把要执行的代码写到run函数里面，线程在创建后会直接运行run函数 
            dict = self.dict
            dict = copy.deepcopy(dict)
            name = self.name
            try:
                #step:新契约录入
                rs = sys_API0001_2().nb_entry(dict, name)
                assert dict['logInfo']['code'] == '1'   #断言是否异常
                proposalId = rs[0]
                dict = rs[1]

                #step4:新契约复核
                rs = sys_API0001_2().nb_review(proposalId, dict, name)
                assert dict['logInfo']['code'] == '1'   #断言是否异常
                others = rs[0]
                dict = rs[1]
                if others == '2':   #是否进入人工核保
                    #step5:新契约核保
                    dict = sys_API0001_2().nb_uw(dict['public']['magicX2'], others, dict, name)
                    assert dict['logInfo']['code'] == '1'   #断言是否异常
                #step6:新契约收费
                dict = sys_API0001_2().nb_payment(dict['public']['magicX2'], dict, name)
                assert dict['logInfo']['code'] == '1'   #断言是否异常
                #step7:新契约回执
                dict = sys_API0001_2().nb_receipt(dict['public']['magicX2'], dict, name)
                assert dict['logInfo']['code'] == '1'   #断言是否异常
            finally:
                self.result = {'code':dict['logInfo']['code'],'msg':dict['logInfo']['msg'],'policyNo':dict['policy_info']['policyNo']}

        #获取线程结果函数
        def get_result(self):
            try:
                return self.result # 如果子线程不使用join方法，此处可能会报没有self.result的错误
            except Exception:
                return None
            return dict



    """新契约录入"""
    @func_set_timeout(120)#设定函数超执行时间
    def nb_entry(self, dict, thread_name):
        """
           step1:登录系统-新契约录入用户
           step2:投保单号提交接口
           step3:保单基本信息录入接口
           step4:投保人信息录入接口
           step5:投保人告知接口
           step6:被保人信息录入接口
           step7:被保人查询接口
           step8:被保人告知接口
           step9:收费方式信息录入接口
           step10:险种信息录入接口
           step11:新契约录入提交接口
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*' + thread_name + ':新契约录入_开始(预计耗时:20s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            magicX = dict['public']['magicX1'] 
            interface_ip = dict['public']['interface_ip']
            
            """step2:投保单号提交接口"""
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：系统-新契约录入_投保单号提交接口'  # 节点
            #dict获取数据+定义数据
            proposalNo = API0000_diy().random_proposalNo()  # 投保单号（随机生成投保单号）
            proposalNo = str(int(proposalNo) + int(thread_name[-1]))
            dict['policy_info']['proposalNo'] = proposalNo
            policyType = 1  # 保单类型：1-个险
            #调用原子脚本
            response = API0000_nb().entry_newProposal(magicX, interface_ip, policyType, proposalNo)
            #获取所需响应值
            is_success = response['success']
            if is_success == True:
                others = response['others']
                # 获取生成的保单号
                policyNo = others['policyNo']
                # 获取服务器时间
                registDate = others['registDate']
                # 获取proposalId
                proposalId = others['proposalId']
                message = ''
            else:
                policyNo = ''
                registDate = ''
                proposalId = ''
                message = response['message']
            #断言
            assert is_success == True
            dict['policy_info']['policyNo'] = policyNo  # 保单号
            
            """step3:保单基本信息录入接口"""
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：系统-新契约录入_保单基本信息录入接口'  # 节点
            #dict获取数据+定义数据     
                #投保日期 
            applicationDate = dict['policy_info']['applicationDate']   
                #定义生效日期 effectiveDate
            date1 = datetime.datetime.strptime(applicationDate, '%Y-%m-%d')
            date2 = date1 + datetime.timedelta(days=1)
            effectiveDate = date2.strftime('%Y-%m-%d')
                #保单基本信息
            organId = dict['policy_info']['organId']   #所属机构
            policyChannel = dict['policy_info']['policyChannel']   #公司渠道
            channelId = dict['policy_info']['channelId']   #销售组织
            salesChannelText = dict['policy_info']['salesChannelText']   #销售渠道名
            salesChannel = dict['policy_info']['salesChannel']   #销售渠道id
            headPartner = dict['policy_info']['headPartner']   #合作机构
            partnerId = dict['policy_info']['partnerId']   #合作网点
            agentId = dict['policy_info']['agentId']   #代理人
            submitChannel = dict['policy_info']['submitChannel']   #提交渠道
            subSalesChannel = dict['policy_info']['subSalesChannel']
            tellerCode = dict['policy_info']['tellerCode']   #柜员代码
            sellerCode = dict['policy_info']['sellerCode']   #销售人员代码
            sellerName = dict['policy_info']['sellerName']   #销售人员姓名
            autoPaddingPrem = dict['policy_info']['autoPaddingPrem']   #是否自垫
            disputedType = dict['policy_info']['disputedType']   #争议方式
            policyDeliveryMode = dict['policy_info']['policyDeliveryMode']   #递送方式
            #调用原子脚本
            response = API0000_nb().proposal_updateProposalInfo(magicX, interface_ip, proposalNo, policyNo, proposalId, organId, policyChannel, channelId, salesChannelText, salesChannel, headPartner, partnerId, tellerCode, sellerCode, sellerName, agentId, submitChannel, subSalesChannel, applicationDate, effectiveDate, autoPaddingPrem, disputedType, policyDeliveryMode)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            #断言
            assert is_success == True           

            """step4:投保人信息录入接口"""
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：系统-新契约录入_投保人信息录入接口'  # 节点
            #dict获取数据+定义数据
            is_HolderExemption = dict['public']['is_HolderExemption']
            if dict['policy_info']['holder_info']['sameASInsurd'] == '1' or is_HolderExemption == '1': #投被保人为同一人，和投保人豁免，sameASInsurd均录入1
                sameASInsurd = '1'
            else:
                sameASInsurd = ''
            Holder_name = dict['policy_info']['holder_info']['name']   # 投保人姓名
            Holder_gender = dict['policy_info']['holder_info']['gender']   # 投保人性别
            Holder_Birth = dict['policy_info']['holder_info']['pbHoldBirth']   # 投保人出生日期
            Holder_certiType = dict['policy_info']['holder_info']['certiType']   # 投保人证件类型
            Holder_certiCode = dict['policy_info']['holder_info']['certiCode']   # 投保人证件号码
            Holder_CertiValidEndDate = dict['policy_info']['holder_info']['pbCertiValidEndDate']   # 投保人证件止期
            Holder_nationality = dict['policy_info']['holder_info']['Holder_nationality']   # 投保人国籍
            Holder_mobilePhone = dict['policy_info']['holder_info']['mobilePhone']   # 投保人手机号
            Holder_officeTel = dict['policy_info']['holder_info']['officeTel']  # 投保人固定电话
            Holder_isMarried = '20'  # 婚姻状况
            Holder_height = '167'  # 身高/CM
            Holder_weight = '67'  # 体重 /KG
            Holder_officeTel = '010-98343543'  # 固定电话
            Holder_homeTel = '010-98343543'  # 家庭电话
            Holder_industry = '03'  # 工作行业
            Holder_workCompany = '东方小清华'  # 工作单位/学校名称
            Holder_email = API0000_diy().random_email()  # 电子邮箱
            Holder_jobCode = '0001001'  # 职业代码/名称
            Holder_jobClass = '1'  # 职业等级
            Holder_driverLicenseType = '06'  # 驾照类型
            Holder_nationnality1 = '01'  # 民族
            Holder_educationId = '40'  # 学位
            Holder_medicalInsType = '04'  # 医保类型
            Holder_incomeSource = '01'  # 收入来源
            Holder_incomeSourceNote = 'wu'  # 收入来源备注
            Holder_annualIncome = '5000000'  # 年收入/万元（系统自动转换为30万元）
            Holder_familyIncome = '5000000'  # 家庭年收入/万元（系统自动转换为30万元）
            Holder_premBudget = '30000'  # 保费预算/元
            Holder_residentType = '1'  # 居民类型
            Holder_taxPayerType = '01'  # 税收居民类型
            Holder_postalCode = '121200'  # 邮编
            Holder_provinceCode = '110000'  # 省份
            Holder_cityCode = '110100'  # 市区
            Holder_districtCode = '110101'  # 地区
            Holder_addrDetail = '建国门东大街22号'  # 详细地址
            #调用原子脚本
            response = API0000_nb().savePersonalHolder(magicX, interface_ip, proposalNo, policyChannel, sameASInsurd, Holder_name, Holder_gender, Holder_Birth, Holder_certiType, Holder_certiCode, Holder_CertiValidEndDate, Holder_isMarried, Holder_height, Holder_weight, Holder_mobilePhone, Holder_officeTel, Holder_homeTel, Holder_industry, Holder_workCompany, Holder_email, Holder_jobCode, Holder_jobClass, Holder_driverLicenseType, Holder_nationality, Holder_nationnality1, Holder_educationId, Holder_medicalInsType, Holder_incomeSource, Holder_incomeSourceNote, Holder_annualIncome, Holder_familyIncome, Holder_premBudget, Holder_residentType, Holder_taxPayerType, Holder_postalCode, Holder_provinceCode, Holder_cityCode, Holder_districtCode, Holder_addrDetail)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                others = response['others']
                customerId = others['customerId']
                message = ''
            else:
                customerId = ''
                message = response['message']
            #断言
            assert is_success == True
            
            """step5:投保人告知接口""" 
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：系统-新契约录入_投保人告知接口'  # 节点
            #dict获取数据+定义数据
            result = '[{"id":"505004","value":"Y"},{"id":"5050045001","value":""}]'   #告知内容
            #调用原子脚本
            response = API0000_nb().Holder_saveNotifyInfo(magicX, interface_ip, proposalId, result, customerId)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            #断言
            assert is_success == True
            
            """step6:被保人信息录入接口"""            
            if (is_HolderExemption == '0' and dict['policy_info']['holder_info']['sameASInsurd'] == '0') or is_HolderExemption == '1':
                #节点初始化
                is_success = ''
                message = ''
                unit = '节点：系统-新契约录入_被保人信息录入接口'  # 节点
                #dict获取数据+定义数据
                insuRelation = dict['policy_info']['insured_info'][0]['insuRelation']   # 被保人与投保人关系
                if insuRelation == '00':
                    insucustomerId = customerId
                else:
                    insucustomerId = ''
                insuName = dict['policy_info']['insured_info'][0]['insuName']  # 被保人姓名
                insuGender = dict['policy_info']['insured_info'][0]['insuGender']  # 被保人性别
                insuBirth = dict['policy_info']['insured_info'][0]['insuBirth']  # 被保人出生日期
                insuCertiType = dict['policy_info']['insured_info'][0]['insuCertiType']  # 被保人证件类型
                insuCertiCode = dict['policy_info']['insured_info'][0]['insuCertiCode']  # 被保人证件号码
                insuCertiValidEndDate =dict['policy_info']['insured_info'][0]['insuCertiValidEndDate']  # 被保人证件止期
                insuNationatiy = dict['policy_info']['insured_info'][0]['insuNationatiy']  # 被保人国籍
                insuMobile = dict['policy_info']['insured_info'][0]['insuMobile']  # 被保人手机号
                insuofficeTel = dict['policy_info']['insured_info'][0]['officeTel']  # 被保人固定电话
                insuHeight = '178'  # 身高/CM
                insuWeight = '78'  # 体重/KG
                insuMarriage = '20'  # 婚姻状况
                if API0000_diy().calc_policy_insured_age(effectiveDate, insuBirth) <= 6:
                    insuWorkCode = '2147001'   #职业代码/名称-学龄前儿童
                elif (API0000_diy().calc_policy_insured_age(effectiveDate, insuBirth) > 6 and API0000_diy().calc_policy_insured_age(effectiveDate, insuBirth) < 18):
                    insuWorkCode = '0000001'   #职业代码/名称-儿童、18岁前儿童
                else:
                    insuWorkCode = '0001001'  #职业代码/名称-内勤
                insujobClass = '1'  # 职业等级
                insuEmail = API0000_diy().random_email()  # 电子邮箱
                insuWorkType = '02'  # 工作行业
                insuCompany = 'apple'  # 工作单位/学校名称
                insunationnality1 = '01'  # 民族
                insumedicalInsType = '04'  # 医保类型
                insudriverLicenseType = '06'  # 驾照类型
                insuhomeTel = '010-993433344'  # 家庭电话
                insuincomeSource = '01'  # 收入来源
                insuincomeSourceNote = 'wu'  # 收入来源备注
                insuannualIncome = '5000000'  # 年收入/万元
                insuresidentType = '1'  # 居民类型
                insutaxPayerType = '01'  # 税收居民类型
                insueducationId = '40'  # 学位
                insuPostalCode = '120000'  # 邮编
                insuProvinceCode = '110000'  # 省
                insuCityCode = '110100'  # 市
                insuDistrictCode = '110101'  # 区
                insuAddrDetail = '建国门东大街22号'  # 详细地址
                #调用原子脚本
                response = API0000_nb().savePersonalInsured(magicX, interface_ip, proposalId, insucustomerId, policyChannel, insuRelation, insuName, insuGender, insuBirth, insuHeight, insuWeight, insuMarriage, insuCertiType, insuCertiCode, insuCertiValidEndDate, insuWorkCode, insujobClass, insuEmail, insuWorkType, insuCompany, insuMobile, insuNationatiy, insunationnality1, insuofficeTel, insumedicalInsType, insudriverLicenseType, insuhomeTel, insuincomeSource, insuincomeSourceNote, insuannualIncome, insuresidentType, insutaxPayerType, insueducationId, insuPostalCode, insuProvinceCode, insuCityCode, insuDistrictCode, insuAddrDetail)
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                else:
                    message = response['message']
                #断言
                assert is_success == True
            
            """step7:被保人查询接口"""
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：系统-新契约录入_被保人查询接口'  # 节点
            #调用原子脚本
            response = API0000_nb().queryPersonalInsured(magicX, interface_ip, proposalNo)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                others = response['others']
                message = ''
            else:
                others = ''
                message = response['message']
            # 根据判断是否豁免，确定出被保人insuId、被保人姓名、被保人insucustomerId、豁免投保人insuId、豁免投保人姓名、豁免投保人insucustomerId
            if len(others) == 1:
                insuId = others[0]['insuId']  # 被保人insuId
                insuName = others[0]['insuName']  # 被保人姓名
                insucustomerId = others[0]['insucustomerId']  # 被保人insucustomerId
                insuId1 = ''  # 豁免投保人insuId
                insuName1 = ''  # 豁免投保人姓名
                insucustomerId1 = ''  # 豁免投保人insucustomerId
            elif len(others) == 2:
                # 判断豁免投保人处于others中的第几位
                for i in range(0, 2):
                    if others[i]['insuName'] == dict['policy_info']['holder_info']['name']:
                        j = i  # 得到豁免投保人处于others中的位置
                        # 判断录入的被保人处于others中的第几位
                        if j == 0:
                            k = 1
                        elif j == 1:
                            k = 0;
                insuId = others[k]['insuId']  # 被保人insuId
                insuName = others[k]['insuName']  # 被保人姓名
                insucustomerId = others[k]['insucustomerId']  # 被保人insucustomerId
                insuId1 = others[j]['insuId']  # 豁免投保人insuId
                insuName1 = others[j]['insuName']  # 豁免投保人姓名
                insucustomerId1 = others[j]['insucustomerId']  # 豁免投保人insucustomerId
            assert is_success == True 
                       
            """step8:被保人告知接口"""
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：系统-新契约录入_被保人告知接口'  # 节点
            #dict获取数据+定义数据
            result = '[{"id":"505004","value":"Y"},{"id":"5050045001","value":""}]'   #告知内容
            # 1.投保人非豁免、投被保人关系不为同一人时录入;2.投保人豁免时录入
            #调用原子脚本
            if (is_HolderExemption == '0' and dict['policy_info']['holder_info']['sameASInsurd'] == '0') or is_HolderExemption == '1':
                response = API0000_nb().Insured_saveNotifyInfo(magicX, interface_ip, proposalId, result, insucustomerId)
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                else:
                    message = response['message']
                #断言
                assert is_success == True
            
            """step9:收费方式信息录入接口"""
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：系统-新契约录入_收费方式信息录入接口'  # 节点
            #dict获取数据+定义数据
            payMode = dict['policy_info']['payment_nb']['payMode']
            name = dict['policy_info']['holder_info']['name']  # 账户名(投保人姓名)
            bankCode = dict['policy_info']['payment_nb']['bankCode']  # 开户银行
            bankAccount = '64556' + str(random.randint(100000000000,999999999999)) # 银行卡号
            reserveMobile = '13556546366'  # 银行预留手机号
            #调用原子脚本
            response = API0000_nb().payModeSave(magicX, interface_ip, proposalId, payMode, name, bankCode, bankAccount, reserveMobile)
            #获取所需响应值
            # 返回是否成功，以及错误信息
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            #断言
            assert is_success == True
            
            """step10:险种信息录入接口"""
            is_success = ''
            message = ''
            unit = '节点：系统-新契约录入_险种信息录入接口-主险1'  # 节点
            is_2risk = dict['public']['is_2risk']  #是否双主险
            sub_risk_info1 = []   #初始化-主险1附加险
            sub_risk_info2 = []   #初始化-主险2附加险

            #拆分双主险下的附加险
            if is_2risk == '1':
                for i in range(0, len(dict['policy_info']['sub_risk_info'])):
                    if dict['policy_info']['sub_risk_info'][i]['belong_mainrisk_productId'] == 'main_risk_1':
                        sub_risk_info1.append(dict['policy_info']['sub_risk_info'][i])
                    elif dict['policy_info']['sub_risk_info'][i]['belong_mainrisk_productId'] == 'main_risk_2':
                        sub_risk_info2.append(dict['policy_info']['sub_risk_info'][i])
            else:
                sub_risk_info1 = dict['policy_info']['sub_risk_info']

            ##先录入主险1
                #dict获取数据+定义数据
            productId = dict['policy_info']['main_risk_info'][0]['productId']  # 险种id
            chargeMode = dict['policy_info']['main_risk_info'][0]['chargeMode']  # 缴费频率
            coverPeriodType = dict['policy_info']['main_risk_info'][0]['coverPeriodType']  # 保障期间类型
            coveragePeriod = dict['policy_info']['main_risk_info'][0]['coveragePeriod']  # 保障期间
            chargePeriodType = dict['policy_info']['main_risk_info'][0]['chargePeriodType']  # 缴费期间类型
            chargePeriod = dict['policy_info']['main_risk_info'][0]['chargePeriod']  # 缴费期间
            sumAssured = dict['policy_info']['main_risk_info'][0]['sumAssured']  # 保额
            stdPremBf = dict['policy_info']['main_risk_info'][0]['stdPremBf']  # 保费
            units = dict['policy_info']['main_risk_info'][0]['units']  # 份数
            planFreq = dict['policy_info']['main_risk_info'][0]['planFreq']  # 年金领取方式 或 年金/生存金领取方式
            payOption = dict['policy_info']['main_risk_info'][0]['payOption']  # 年金使用方式
            bonusYearOrAge = dict['policy_info']['main_risk_info'][0]['bonusYearOrAge']  # 领取年期或年龄
            renew = dict['policy_info']['main_risk_info'][0]['renew']  # 是否续保
            mainItemId = ''
                #调用原子脚本
            response = API0000_nb().saveProductInfo(magicX, interface_ip, proposalId, productId, mainItemId, insuId, chargeMode, coverPeriodType, coveragePeriod, chargePeriodType, chargePeriod, units, sumAssured, stdPremBf, planFreq, payOption, bonusYearOrAge, headPartner, organId, renew)
                #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
                others = response['others']
                mainItemId1 = others['itemId']
                sys_stdPremBf = others['stdPremBf']   #保费
                sys_sumAssured = others['sumAssured']   #保额
            else:
                message = response['message']
                mainItemId1 = ''
                sys_stdPremBf = ''
                sys_sumAssured = ''

                #存入dict
            dict['policy_info']['main_risk_info'][0]['stdPremBf'] = sys_stdPremBf  # 保费
            dict['policy_info']['main_risk_info'][0]['sumAssured'] = sys_sumAssured  # 保额
            ##录入主险1-豁免附加险
            if is_HolderExemption == '1':
                is_success = ''
                message = ''
                unit = '节点：系统-新契约录入_险种信息录入接口-主险1_豁免附加险'  # 节点
                #dict获取数据+定义数据
                productId1 = sub_risk_info1[0]['productId']  # 险种id
                chargeMode1 = sub_risk_info1[0]['chargeMode']  # 缴费频率
                coverPeriodType1 = sub_risk_info1[0]['coverPeriodType']  # 保障期间类型
                coveragePeriod1 = sub_risk_info1[0]['coveragePeriod']  # 保障期间
                chargePeriodType1 = sub_risk_info1[0]['chargePeriodType']  # 缴费期间类型
                chargePeriod1 = sub_risk_info1[0]['chargePeriod']  # 缴费期间
                sumAssured1 = sub_risk_info1[0]['sumAssured']  # 保额
                stdPremBf1 = sub_risk_info1[0]['stdPremBf']  # 保费
                units1 = sub_risk_info1[0]['units']  # 份数
                planFreq1 = sub_risk_info1[0]['planFreq']  # 年金领取方式 或 年金/生存金领取方式
                payOption1 = sub_risk_info1[0]['payOption']  # 年金使用方式
                bonusYearOrAge1 = sub_risk_info1[0]['bonusYearOrAge']  # 领取年期或年龄
                renew1 = sub_risk_info1[0]['renew']  # 是否续保
                #调用原子脚本
                response = API0000_nb().saveProductInfo(magicX, interface_ip, proposalId, productId1, mainItemId1, insuId1, chargeMode1, coverPeriodType1, coveragePeriod1, chargePeriodType1, chargePeriod1, units1, sumAssured1, stdPremBf1, planFreq1, payOption1, bonusYearOrAge1, headPartner, organId, renew1)   
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                    others = response['others']
                    sys_stdPremBf = others['stdPremBf']   #保费
                    sys_sumAssured = others['sumAssured']   #保额
                else:
                    message = response['message']
                    sys_stdPremBf = ''
                    sys_sumAssured = ''

                    #存入sub_risk_info1
                sub_risk_info1[0]['stdPremBf'] = sys_stdPremBf  # 保费
                sub_risk_info1[0]['sumAssured'] = sys_sumAssured  # 保额
            ##判断存在附加险不存在豁免险时
            if is_HolderExemption == '0' and len(sub_risk_info1) > 0:
                is_success = ''
                message = ''
                unit = '节点：系统-新契约录入_险种信息录入接口-非豁免的附加险'  # 节点
                for i in range(0, len(sub_risk_info1)):
                    #dict获取数据+定义数据
                    productId1 = sub_risk_info1[i]['productId']  # 险种id
                    chargeMode1 = sub_risk_info1[i]['chargeMode']  # 缴费频率
                    coverPeriodType1 = sub_risk_info1[i]['coverPeriodType']  # 保障期间类型
                    coveragePeriod1 = sub_risk_info1[i]['coveragePeriod']  # 保障期间
                    chargePeriodType1 = sub_risk_info1[i]['chargePeriodType']  # 缴费期间类型
                    chargePeriod1 = sub_risk_info1[i]['chargePeriod']  # 缴费期间
                    sumAssured1 = sub_risk_info1[i]['sumAssured']  # 保额
                    stdPremBf1 = sub_risk_info1[i]['stdPremBf']  # 保费
                    units1 = sub_risk_info1[i]['units']  # 份数
                    planFreq1 = sub_risk_info1[i]['planFreq']  # 年金领取方式 或 年金/生存金领取方式
                    payOption1 = sub_risk_info1[i]['payOption']  # 年金使用方式
                    bonusYearOrAge1 = sub_risk_info1[i]['bonusYearOrAge']  # 领取年期或年龄
                    renew1 = sub_risk_info1[i]['renew']   #是否续保
                    # 调用原子化脚本
                    response = API0000_nb().saveProductInfo(magicX, interface_ip, proposalId, productId1, mainItemId1, insuId, chargeMode1, coverPeriodType1, coveragePeriod1, chargePeriodType1, chargePeriod1, units1, sumAssured1, stdPremBf1, planFreq1, payOption1, bonusYearOrAge1, headPartner, organId, renew1) 
                    #获取所需响应值
                    is_success = response['success']
                    if is_success:
                        message = ''
                        others = response['others']
                        sys_stdPremBf = others['stdPremBf']   #保费
                        sys_sumAssured = others['sumAssured']   #保额
                    else:
                        message = response['message']
                        sys_stdPremBf = ''
                        sys_sumAssured = ''

                        #存入sub_risk_info1
                    sub_risk_info1[i]['stdPremBf'] = sys_stdPremBf  # 保费
                    sub_risk_info1[i]['sumAssured'] = sys_sumAssured  # 保额
            ##判断存在附加险也存在豁免险时
            elif is_HolderExemption == '1' and len(sub_risk_info1) > 1:
                is_success = ''
                message = ''
                unit = '节点：系统-新契约录入_险种信息录入接口-非豁免的附加险'  # 节点
                for i in range(1, len(sub_risk_info1)):
                    productId1 = sub_risk_info1[i]['productId']  # 险种id
                    chargeMode1 = sub_risk_info1[i]['chargeMode']  # 缴费频率
                    coverPeriodType1 = sub_risk_info1[i]['coverPeriodType']  # 保障期间类型
                    coveragePeriod1 = dsub_risk_info1[i]['coveragePeriod']  # 保障期间
                    chargePeriodType1 = sub_risk_info1[i]['chargePeriodType']  # 缴费期间类型
                    chargePeriod1 = sub_risk_info1[i]['chargePeriod']  # 缴费期间
                    sumAssured1 = sub_risk_info1[i]['sumAssured']  # 保额
                    stdPremBf1 = sub_risk_info1[i]['stdPremBf']  # 保费
                    units1 = sub_risk_info1[i]['units']  # 份数
                    planFreq1 = sub_risk_info1[i]['planFreq']  # 年金领取方式 或 年金/生存金领取方式
                    payOption1 = sub_risk_info1[i]['payOption']  # 年金使用方式
                    bonusYearOrAge1 = sub_risk_info1[i]['bonusYearOrAge']  # 领取年期或年龄
                    renew1 = sub_risk_info1[i]['renew']  # 是否续保
                    # 调用原子化脚本
                    response = API0000_nb().saveProductInfo(magicX, interface_ip, proposalId, productId1, mainItemId1, insuId, chargeMode1, coverPeriodType1, coveragePeriod1, chargePeriodType1, chargePeriod1, units1, sumAssured1, stdPremBf1, planFreq1, payOption1, bonusYearOrAge1, headPartner, organId, renew1) 
                    #获取所需响应值
                    is_success = response['success']
                    if is_success:
                        message = ''
                        others = response['others']
                        sys_stdPremBf = others['stdPremBf']   #保费
                        sys_sumAssured = others['sumAssured']   #保额
                    else:
                        message = response['message']
                        sys_stdPremBf = ''
                        sys_sumAssured = ''

                        #存入sub_risk_info1
                    sub_risk_info1[i]['stdPremBf'] = sys_stdPremBf  # 保费
                    sub_risk_info1[i]['sumAssured'] = sys_sumAssured  # 保额
            ##存在双主险时-录入第二个主险 
            if is_2risk == '1':
                is_success = ''
                message = ''
                unit = '节点：系统-新契约录入_险种信息录入接口-录入第二个主险'  # 节点
                productId2 = dict['policy_info']['main_risk_info'][-1]['productId']  # 险种id
                chargeMode2 = dict['policy_info']['main_risk_info'][-1]['chargeMode']  # 缴费频率
                coverPeriodType2 = dict['policy_info']['main_risk_info'][-1]['coverPeriodType']  # 保障期间类型
                coveragePeriod2 = dict['policy_info']['main_risk_info'][-1]['coveragePeriod']  # 保障期间
                chargePeriodType2 = dict['policy_info']['main_risk_info'][-1]['chargePeriodType']  # 缴费期间类型
                chargePeriod2 = dict['policy_info']['main_risk_info'][-1]['chargePeriod']  # 缴费期间
                sumAssured2 = dict['policy_info']['main_risk_info'][-1]['sumAssured']  # 保额
                stdPremBf2 = dict['policy_info']['main_risk_info'][-1]['stdPremBf']  # 保费
                units2 = dict['policy_info']['main_risk_info'][-1]['units']  # 份数
                planFreq2 = dict['policy_info']['main_risk_info'][-1]['planFreq']  # 年金领取方式 或 年金/生存金领取方式
                payOption2 = dict['policy_info']['main_risk_info'][-1]['payOption']  # 年金使用方式
                bonusYearOrAge2 = dict['policy_info']['main_risk_info'][-1]['bonusYearOrAge']  # 领取年期或年龄
                renew2 = dict['policy_info']['main_risk_info'][-1]['renew']  # 是否续保
                mainItemId2 = ''  # 主险标识
                # 调用原子化脚本      
                response = API0000_nb().saveProductInfo(magicX, interface_ip, proposalId, productId2, mainItemId2, insuId, chargeMode2, coverPeriodType2, coveragePeriod2, chargePeriodType2, chargePeriod2, units2, sumAssured2, stdPremBf2, planFreq2, payOption2, bonusYearOrAge2, headPartner, organId, renew2) 
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                    others = response['others']
                    mainItemId2 = others['itemId']
                    sys_stdPremBf = others['stdPremBf']   #保费
                    sys_sumAssured = others['sumAssured']   #保额
                else:
                    message = response['message']
                    mainItemId2 = ''
                    sys_stdPremBf = ''
                    sys_sumAssured = ''

                    #存入dict
                dict['policy_info']['main_risk_info'][-1]['stdPremBf'] = sys_stdPremBf  # 保费
                dict['policy_info']['main_risk_info'][-1]['sumAssured'] = sys_sumAssured  # 保额
                assert is_success == True

                #主险2附加险
                for i in range(0, len(sub_risk_info2)):
                    is_success = ''
                    message = ''
                    unit = '节点：系统-新契约录入_险种信息录入接口-双主险附加险'  # 节点
                    #dict获取数据+定义数据
                    productId3 = sub_risk_info2[i]['productId']  # 险种id
                    chargeMode3 = sub_risk_info2[i]['chargeMode']  # 缴费频率
                    coverPeriodType3 = sub_risk_info2[i]['coverPeriodType']  # 保障期间类型
                    coveragePeriod3 = sub_risk_info2[i]['coveragePeriod']  # 保障期间
                    chargePeriodType3 = sub_risk_info2[i]['chargePeriodType']  # 缴费期间类型
                    chargePeriod3 = sub_risk_info2[i]['chargePeriod']  # 缴费期间
                    sumAssured3 = sub_risk_info2[i]['sumAssured']  # 保额
                    stdPremBf3 = sub_risk_info2[i]['stdPremBf']  # 保费
                    units3 = sub_risk_info2[i]['units']  # 份数
                    planFreq3 = sub_risk_info2[i]['planFreq']  # 年金领取方式 或 年金/生存金领取方式
                    payOption3 = sub_risk_info2[i]['payOption']  # 年金使用方式
                    bonusYearOrAge3 = sub_risk_info2[i]['bonusYearOrAge']  # 领取年期或年龄
                    renew3 = sub_risk_info2[i]['renew']   #是否续保
                    # 调用原子化脚本
                    response = API0000_nb().saveProductInfo(magicX, interface_ip, proposalId, productId3, mainItemId2, insuId, chargeMode3, coverPeriodType3, coveragePeriod3, chargePeriodType3, chargePeriod3, units3, sumAssured3, stdPremBf3, planFreq3, payOption3, bonusYearOrAge3, headPartner, organId, renew3) 
                    #获取所需响应值
                    is_success = response['success']
                    if is_success:
                        message = ''
                        others = response['others']
                        sys_stdPremBf = others['stdPremBf']   #保费
                        sys_sumAssured = others['sumAssured']   #保额
                    else:
                        message = response['message']
                        sys_stdPremBf = ''
                        sys_sumAssured = ''

                        #存入sub_risk_info2
                    sub_risk_info2[i]['stdPremBf'] = sys_stdPremBf  # 保费
                    sub_risk_info2[i]['sumAssured'] = sys_sumAssured  # 保额
                assert is_success == True
            dict['policy_info']['sub_risk_info'] = sub_risk_info1 + sub_risk_info2
            """step11:新契约录入提交前规则校验接口"""
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：系统-新契约录入_提交前规则校验接口'  # 节点
            #调用原子脚本
            response = API0000_nb().valiDateRule(magicX, interface_ip, proposalId)
            #获取所需响应值
            if response['success'] == True:
                is_success = True
                message = ''
            else:
                is_success = False
                message = response['message']
            #断言
            assert is_success == True  
            """step12:新契约录入提交接口"""
            #节点初始化
            is_success = ''
            message = ''
            unit = '节点：系统-新契约录入_提交接口'  # 节点
            #调用原子脚本
            response = API0000_nb().reviewProposal(magicX, interface_ip, proposalId)
            #获取所需响应值
            if (response['success'] == True) and (response['message'] == ''):
                is_success = True
                others = ''
                message = ''
            else:
                is_success = False
                others = response['others']
                if others != None:
                    for i in range(0, len(others)):
                        if i == 0:
                            message = response['message'] + ':1.' + others[i]['issueContent']
                        else:
                            message = message + str(i+1) + '.' + others[i]['issueContent']
                else:
                    message = response['message']
            #断言
            assert is_success == True       

            """存入dict"""
                #保单信息
            dict['policy_info']['proposalNo'] = proposalNo  # 投保单号
            dict['policy_info']['policyType'] = policyType  # 保单号类型
            dict['policy_info']['effectiveDate'] = effectiveDate  # 生效日期
            dict['policy_info']['organId'] = organId  # 所属机构
            dict['policy_info']['policyChannel'] = policyChannel  # 公司渠道
                #投保人信息
            dict['policy_info']['holder_info']['isMarried'] = Holder_isMarried  # 婚姻状况
            dict['policy_info']['holder_info']['height'] = Holder_height  # 身高/CM
            dict['policy_info']['holder_info']['weight'] = Holder_weight  # 体重 /KG
            dict['policy_info']['holder_info']['officeTel'] = Holder_officeTel  # 固定电话
            dict['policy_info']['holder_info']['homeTel'] = Holder_homeTel  # 家庭电话
            dict['policy_info']['holder_info']['industry'] = Holder_industry  # 工作行业
            dict['policy_info']['holder_info']['workCompany'] = Holder_workCompany  # 工作单位/学校名称
            dict['policy_info']['holder_info']['email'] = Holder_email  # 电子邮箱
            dict['policy_info']['holder_info']['jobCode'] = Holder_jobCode  # 职业代码/名称
            dict['policy_info']['holder_info']['jobClass'] = Holder_jobClass  # 职业等级
            dict['policy_info']['holder_info']['driverLicenseType'] = Holder_driverLicenseType  # 驾照类型
            dict['policy_info']['holder_info']['nationality'] = Holder_nationality  # 国籍/地区
            dict['policy_info']['holder_info']['nationnality1'] = Holder_nationnality1  # 民族
            dict['policy_info']['holder_info']['educationId'] = Holder_educationId  # 学位
            dict['policy_info']['holder_info']['medicalInsType'] = Holder_medicalInsType  # 医保类型
            dict['policy_info']['holder_info']['incomeSource'] = Holder_incomeSource  # 收入来源
            dict['policy_info']['holder_info']['incomeSourceNote'] = Holder_incomeSourceNote  # 收入来源备注
            dict['policy_info']['holder_info']['annualIncome'] = Holder_annualIncome  # 年收入/万元（系统自动转换为30万元）
            dict['policy_info']['holder_info']['familyIncome'] = Holder_familyIncome  # 家庭年收入/万元（系统自动转换为30万元）
            dict['policy_info']['holder_info']['premBudget'] = Holder_premBudget  # 保费预算/元
            dict['policy_info']['holder_info']['residentType'] = Holder_residentType  # 居民类型
            dict['policy_info']['holder_info']['taxPayerType'] = Holder_taxPayerType  # 税收居民类型
            dict['policy_info']['holder_info']['postalCode'] = Holder_postalCode  # 邮编
            dict['policy_info']['holder_info']['provinceCode'] = Holder_provinceCode  # 省份
            dict['policy_info']['holder_info']['cityCode'] = Holder_cityCode  # 市区
            dict['policy_info']['holder_info']['districtCode'] = Holder_districtCode  # 地区
            dict['policy_info']['holder_info']['addrDetail'] = Holder_addrDetail   # 详细地址
                #被保人信息
                #①非投保人豁免，投被保人不为同一人时
            if dict['public']['is_HolderExemption'] == '0' and dict['policy_info']['holder_info']['sameASInsurd'] == '0':
                dict['policy_info']['insured_info'][0]['insucustomerId'] = insucustomerId   #客户id
                dict['policy_info']['insured_info'][0]['insuHeight'] = insuHeight   # 身高/CM
                dict['policy_info']['insured_info'][0]['insuWeight'] = insuWeight   # 体重/KG
                dict['policy_info']['insured_info'][0]['insuMarriage'] = insuMarriage   # 婚姻状况
                dict['policy_info']['insured_info'][0]['insuWorkCode'] = insuWorkCode   # 职业代码/名称
                dict['policy_info']['insured_info'][0]['insujobClass'] = insujobClass   # 职业等级
                dict['policy_info']['insured_info'][0]['insuEmail'] = insuEmail   # 电子邮箱
                dict['policy_info']['insured_info'][0]['insuWorkType'] = insuWorkType   # 工作行业
                dict['policy_info']['insured_info'][0]['insuCompany'] = insuCompany   # 工作单位/学校名称
                dict['policy_info']['insured_info'][0]['insuNationatiy'] = insuNationatiy   # 国籍/地区
                dict['policy_info']['insured_info'][0]['insunationnality1'] = insunationnality1   # 民族
                dict['policy_info']['insured_info'][0]['officeTel'] = insuofficeTel   # 固定电话
                dict['policy_info']['insured_info'][0]['insumedicalInsType'] = insumedicalInsType   # 医保类型
                dict['policy_info']['insured_info'][0]['driverLicenseType'] = insudriverLicenseType   # 驾照类型
                dict['policy_info']['insured_info'][0]['homeTel'] = insuhomeTel   # 家庭电话
                dict['policy_info']['insured_info'][0]['insuincomeSource'] = insuincomeSource   # 收入来源
                dict['policy_info']['insured_info'][0]['insuincomeSourceNote'] = insuincomeSourceNote   # 收入来源备注
                dict['policy_info']['insured_info'][0]['annualIncome'] = insuannualIncome   # 年收入/万元
                dict['policy_info']['insured_info'][0]['insuresidentType'] = insuresidentType   # 居民类型
                dict['policy_info']['insured_info'][0]['taxPayerType'] = insutaxPayerType   # 税收居民类型
                dict['policy_info']['insured_info'][0]['insueducationId'] = insueducationId   # 学位
                dict['policy_info']['insured_info'][0]['insuPostalCode'] = insuPostalCode   # 邮编
                dict['policy_info']['insured_info'][0]['insuProvinceCode'] = insuProvinceCode   # 省
                dict['policy_info']['insured_info'][0]['insuCityCode'] = insuCityCode   # 市
                dict['policy_info']['insured_info'][0]['insuDistrictCode'] = insuDistrictCode   # 区
                dict['policy_info']['insured_info'][0]['insuAddrDetail'] = insuAddrDetail   # 详细地址
                #②非投保人豁免，投被保人为同一人时：
            elif dict['public']['is_HolderExemption'] == '0' and dict['policy_info']['holder_info']['sameASInsurd'] == '1':
                dict['policy_info']['insured_info'][0]['insucustomerId'] = insucustomerId   #客户id
                dict['policy_info']['insured_info'][0]['insuHeight'] = Holder_height   # 身高/CM
                dict['policy_info']['insured_info'][0]['insuWeight'] = Holder_weight   # 体重/KG
                dict['policy_info']['insured_info'][0]['insuMarriage'] = Holder_isMarried   # 婚姻状况
                dict['policy_info']['insured_info'][0]['insuWorkCode'] = Holder_jobCode   # 职业代码/名称
                dict['policy_info']['insured_info'][0]['insujobClass'] = Holder_jobClass   # 职业等级
                dict['policy_info']['insured_info'][0]['insuEmail'] = Holder_email   # 电子邮箱
                dict['policy_info']['insured_info'][0]['insuWorkType'] = Holder_industry   # 工作行业
                dict['policy_info']['insured_info'][0]['insuCompany'] = Holder_workCompany   # 工作单位/学校名称
                dict['policy_info']['insured_info'][0]['insuNationatiy'] = Holder_nationality   # 国籍/地区
                dict['policy_info']['insured_info'][0]['insunationnality1'] = Holder_nationnality1   # 民族
                dict['policy_info']['insured_info'][0]['officeTel'] = Holder_officeTel   # 固定电话
                dict['policy_info']['insured_info'][0]['insumedicalInsType'] = Holder_medicalInsType   # 医保类型
                dict['policy_info']['insured_info'][0]['driverLicenseType'] = Holder_driverLicenseType   # 驾照类型
                dict['policy_info']['insured_info'][0]['homeTel'] = Holder_homeTel   # 家庭电话
                dict['policy_info']['insured_info'][0]['insuincomeSource'] = Holder_incomeSource   # 收入来源
                dict['policy_info']['insured_info'][0]['insuincomeSourceNote'] = Holder_incomeSourceNote   # 收入来源备注
                dict['policy_info']['insured_info'][0]['annualIncome'] = Holder_annualIncome   # 年收入/万元
                dict['policy_info']['insured_info'][0]['insuresidentType'] = Holder_residentType   # 居民类型
                dict['policy_info']['insured_info'][0]['taxPayerType'] = Holder_taxPayerType   # 税收居民类型
                dict['policy_info']['insured_info'][0]['insueducationId'] = Holder_educationId   # 学位
                dict['policy_info']['insured_info'][0]['insuPostalCode'] = Holder_postalCode   # 邮编
                dict['policy_info']['insured_info'][0]['insuProvinceCode'] = Holder_provinceCode   # 省
                dict['policy_info']['insured_info'][0]['insuCityCode'] = Holder_cityCode   # 市
                dict['policy_info']['insured_info'][0]['insuDistrictCode'] = Holder_districtCode   # 区
                dict['policy_info']['insured_info'][0]['insuAddrDetail'] = Holder_addrDetail   # 详细地址
                #③非投保人豁免，投被保人为同一人时：
            elif dict['public']['is_HolderExemption'] == '1':
                dict['policy_info']['insured_info'][0]['insucustomerId'] = insucustomerId   #客户id
                dict['policy_info']['insured_info'][0]['insuHeight'] = insuHeight   # 身高/CM
                dict['policy_info']['insured_info'][0]['insuWeight'] = insuWeight   # 体重/KG
                dict['policy_info']['insured_info'][0]['insuMarriage'] = insuMarriage   # 婚姻状况
                dict['policy_info']['insured_info'][0]['insuWorkCode'] = insuWorkCode   # 职业代码/名称
                dict['policy_info']['insured_info'][0]['insujobClass'] = insujobClass   # 职业等级
                dict['policy_info']['insured_info'][0]['insuEmail'] = insuEmail   # 电子邮箱
                dict['policy_info']['insured_info'][0]['insuWorkType'] = insuWorkType   # 工作行业
                dict['policy_info']['insured_info'][0]['insuCompany'] = insuCompany   # 工作单位/学校名称
                dict['policy_info']['insured_info'][0]['insuNationatiy'] = insuNationatiy   # 国籍/地区
                dict['policy_info']['insured_info'][0]['insunationnality1'] = insunationnality1   # 民族
                dict['policy_info']['insured_info'][0]['officeTel'] = insuofficeTel   # 固定电话
                dict['policy_info']['insured_info'][0]['insumedicalInsType'] = insumedicalInsType   # 医保类型
                dict['policy_info']['insured_info'][0]['driverLicenseType'] = insudriverLicenseType   # 驾照类型
                dict['policy_info']['insured_info'][0]['homeTel'] = insuhomeTel   # 家庭电话
                dict['policy_info']['insured_info'][0]['insuincomeSource'] = insuincomeSource   # 收入来源
                dict['policy_info']['insured_info'][0]['insuincomeSourceNote'] = insuincomeSourceNote   # 收入来源备注
                dict['policy_info']['insured_info'][0]['annualIncome'] = insuannualIncome   # 年收入/万元
                dict['policy_info']['insured_info'][0]['insuresidentType'] = insuresidentType   # 居民类型
                dict['policy_info']['insured_info'][0]['taxPayerType'] = insutaxPayerType   # 税收居民类型
                dict['policy_info']['insured_info'][0]['insueducationId'] = insueducationId   # 学位
                dict['policy_info']['insured_info'][0]['insuPostalCode'] = insuPostalCode   # 邮编
                dict['policy_info']['insured_info'][0]['insuProvinceCode'] = insuProvinceCode   # 省
                dict['policy_info']['insured_info'][0]['insuCityCode'] = insuCityCode   # 市
                dict['policy_info']['insured_info'][0]['insuDistrictCode'] = insuDistrictCode   # 区
                dict['policy_info']['insured_info'][0]['insuAddrDetail'] = insuAddrDetail   # 详细地址
                dict['policy_info']['insured_info'][0]['insucustomerId'] = insucustomerId1   #客户id
                dict['policy_info']['insured_info'][1]['insuHeight'] = Holder_height   # 身高/CM
                dict['policy_info']['insured_info'][1]['insuWeight'] = Holder_weight   # 体重/KG
                dict['policy_info']['insured_info'][1]['insuMarriage'] = Holder_isMarried   # 婚姻状况
                dict['policy_info']['insured_info'][1]['insuWorkCode'] = Holder_jobCode   # 职业代码/名称
                dict['policy_info']['insured_info'][1]['insujobClass'] = Holder_jobClass   # 职业等级
                dict['policy_info']['insured_info'][1]['insuEmail'] = Holder_email   # 电子邮箱
                dict['policy_info']['insured_info'][1]['insuWorkType'] = Holder_industry   # 工作行业
                dict['policy_info']['insured_info'][1]['insuCompany'] = Holder_workCompany   # 工作单位/学校名称
                dict['policy_info']['insured_info'][1]['insuNationatiy'] = Holder_nationality   # 国籍/地区
                dict['policy_info']['insured_info'][1]['insunationnality1'] = Holder_nationnality1   # 民族
                dict['policy_info']['insured_info'][1]['insuofficeTel'] = Holder_officeTel   # 固定电话
                dict['policy_info']['insured_info'][1]['insumedicalInsType'] = Holder_medicalInsType   # 医保类型
                dict['policy_info']['insured_info'][1]['insudriverLicenseType'] = Holder_driverLicenseType   # 驾照类型
                dict['policy_info']['insured_info'][1]['insuhomeTel'] = Holder_homeTel   # 家庭电话
                dict['policy_info']['insured_info'][1]['insuincomeSource'] = Holder_incomeSource   # 收入来源
                dict['policy_info']['insured_info'][1]['insuincomeSourceNote'] = Holder_incomeSourceNote   # 收入来源备注
                dict['policy_info']['insured_info'][1]['annualIncome'] = Holder_annualIncome   # 年收入/万元
                dict['policy_info']['insured_info'][1]['insuresidentType'] = Holder_residentType   # 居民类型
                dict['policy_info']['insured_info'][1]['insutaxPayerType'] = Holder_taxPayerType   # 税收居民类型
                dict['policy_info']['insured_info'][1]['insueducationId'] = Holder_educationId   # 学位
                dict['policy_info']['insured_info'][1]['insuPostalCode'] = Holder_postalCode   # 邮编
                dict['policy_info']['insured_info'][1]['insuProvinceCode'] = Holder_provinceCode   # 省
                dict['policy_info']['insured_info'][1]['insuCityCode'] = Holder_cityCode   # 市
                dict['policy_info']['insured_info'][1]['insuDistrictCode'] = Holder_districtCode   # 区
                dict['policy_info']['insured_info'][1]['insuAddrDetail'] = Holder_addrDetail   # 详细地址
            dict['logInfo']['code'] = '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*' + thread_name + ':新契约录入_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'
            dict['logInfo']['err'] = unit + str(e)
            #记录日志
            logging.warning(API0000_diy().text_conversion('异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return proposalId, dict


    """新契约复核"""
    @func_set_timeout(60)#设定函数超执行时间
    def nb_review(self,proposalId, dict, thread_name):
        """
           step2:新契约复核updatePropStatus接口
           step3:新契约复核提交接口
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*' + thread_name + ':新契约复核_开始(预计耗时:10s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            magicX = dict['public']['magicX2']   #初始化会话id
            interface_ip = dict['public']['interface_ip']

            """step2:登录系统-新契约复核updatePropStatus接口"""
            #节点初始化
            is_success = ''   #是否成功标识
            unit = '节点：系统-新契约复核_新契约复核updatePropStatus接口'  # 节点
            message = ''   #信息
            #调用原子脚本
            response = API0000_nb().updatePropStatus(magicX, interface_ip, proposalId)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            #断言
            assert is_success == True
            
            """step3:登录系统-新契约复核提交接口"""
            #节点初始化
            is_success = ''
            unit = '节点：系统-新契约复核_新契约复核提交接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            personUW = 'false'   #是否强制人工核保
            #调用原子脚本
            response = API0000_nb().confirmProposal(magicX, interface_ip, proposalId, personUW)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                others = response['others']   # others为1时自动核保通过；为2时人工核保
                message = ''
            else:
                others = ''
                message = response['message']
            #断言
            assert is_success == True 
            dict['logInfo']['code'] = '1' 
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*' + thread_name + ':新契约复核_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0' 
            dict['logInfo']['err'] = unit + str(e)
            #记录日志
            logging.warning(API0000_diy().text_conversion('异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return others, dict


    """新契约核保"""
    @func_set_timeout(30)#设定函数超执行时间
    def nb_uw(self, magicX, others, dict, thread_name):
        """
           step1:判断自动核保或人工核保
           step2:新契约人工核保_核保共享池查询接口
           step3:新契约人工核保_锁定任务接口
           step4:新契约人工核保_获取保单信息接口
           step5:新契约人工核保_险种层提交核保决定接口
           step6:新契约人工核保_契约核保结论提交接口
        """
        
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*' + thread_name + ':新契约核保_开始(预计耗时:10s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            """step1:判断自动核保或人工核保"""
            if others == '1':  #新契约自核通过
                pass
            elif others == '2':   #进入新契约人工核保
                """step2:新契约人工核保_核保共享池查询接口"""
                #节点初始化
                is_success = ''
                unit = '节点：系统-新契约人工核保_核保共享池查询接口'  # 节点
                message = ''
                #dict获取数据+定义数据
                interface_ip = dict['public']['interface_ip']   #接口ip
                policyNo = dict['policy_info']['policyNo']  # 保单号
                #调用原子脚本
                response = API0000_uw().uwPolicyQuery_nb(magicX, interface_ip, policyNo)
                #获取所需响应值
                is_success = response['isSuccess']
                if is_success:
                    resultData = response['resultData']
                    uwId = resultData[0]['uwId']
                    mainId = resultData[0]['mainId']
                    message = ''
                else:
                    uwId = ''
                    mainId = ''
                    message = ''
                    message = response['message']
                #断言
                assert is_success == True
                
                """step3:新契约人工核保_锁定任务接口"""
                #节点初始化
                is_success = ''
                unit = '节点：系统-新契约人工核保_锁定任务接口'  # 节点
                message = ''
                #调用原子脚本
                response = API0000_uw().uwLock_nb(magicX, interface_ip, mainId)
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                else:
                    message = response['message']
                #断言
                assert is_success == True

                """step4:新契约人工核保_获取保单信息接口"""
                #节点初始化
                is_success = ''
                unit = '节点：系统-新契约人工核保_获取保单信息接口'  # 节点
                message = ''
                #调用原子脚本
                response = API0000_uw().uw_queryPersonalPolicy(magicX, interface_ip, uwId, mainId)
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    others = response['others']
                    uwProducts = others['uwProducts']   # 核保险种信息
                    message = ''
                else:
                    uwProducts = ''
                    message = response['message']
                #断言
                assert is_success == True
                
                """step5:新契约人工核保_险种层提交核保决定接口"""
                #节点初始化
                is_success = ''
                unit = '节点：系统-新契约人工核保_险种层提交核保决定接口'  # 节点
                message = ''
                #dict获取数据+定义数据
                uwDecision = '01'  # 核保决定 01-核保通过
                decisionComment = '核保通过'  # 核保决定描述
                uwExceptTxt = ''  # 除外责任

                num = 0
                lenght = len(uwProducts)   # 获取险种个数
                for a in range(0, lenght):
                    uwItemId = uwProducts[a]['uwItemId']
                    #调用原子脚本
                    response = API0000_uw().updateUwDecision_nb(magicX, interface_ip, uwItemId, uwId, uwDecision, decisionComment, uwExceptTxt, policyNo)
                    #获取所需响应值
                    is_success = response['success']
                    if is_success:
                        num = num + 1
                if num == lenght:
                    is_success = True
                    message = ''
                else:
                    is_success = False
                    message = '险种层提交核保决定未成功'
                #断言
                assert is_success == True

                """step6:新契约人工核保_契约核保结论提交接口"""
                #节点初始化
                is_success = ''
                unit = '节点：系统-新契约人工核保_契约核保结论提交接口'  # 节点
                message = ''
                #dict获取数据+定义数据
                uwPolicyDecision = '01'  # 保单核保结论 01-标准通过
                #调用原子脚本
                response = API0000_uw().commitUwComplete(magicX, interface_ip, uwId, uwPolicyDecision)
                #获取所需响应值
                status = response['status']
                uwStatus = response['result']['uwStatus']
                if status == '0':
                    is_success = True
                    message = ''
                else:
                    is_success = False
                    message = response['message']
                """
                if status == '0':
                    if uwStatus != '04':
                        is_success = True
                        message = ''
                    else:
                        is_success = False
                        message = '核保通过。新契约进入双录，请手动进行双录处理！'
                else:
                    is_success = False
                    message = response['message']
                """
                #断言
                assert is_success == True
                dict['logInfo']['code'] == '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*' + thread_name + ':新契约核保_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] == '0'
            dict['logInfo']['err'] = unit + str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                username = dict['public']['username_review']    #新契约复核用户
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
            #记录日志
            logging.warning(API0000_diy().text_conversion('异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict


    """新契约收费"""
    @func_set_timeout(180)#设定函数超执行时间
    def nb_payment(self, magicX, dict, thread_name):
        """
           step1:柜面收付费查询接口
           step2:柜面收付费保存接口
           step3:柜面收付费审核接口
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*' + thread_name + ':新契约收费_开始(预计耗时:30s)'))
            """step1:柜面收付费查询接口"""
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            is_success = ''   #初始化是否成功标识
            unit = '节点：系统-新契约收费_柜面收付费查询接口'  # 节点
            message = ''   #初始化信息
            payment = 0   #初始化收付费金额 
            #dict获取数据+定义数据
            interface_ip = dict['public']['interface_ip']   #接口ip
            policyNo = dict['policy_info']['policyNo']  # 保单号
            proposalNo = dict['policy_info']['proposalNo']  #投保单号

            for i in range(0, 60):  #收付费查询(每1秒查询一次，最大40次，直到查到结果便结束查询)
                #调用原子脚本
                rs = API0000_payment().FeeQuery(magicX, interface_ip, policyNo)
                is_success = rs[0]
                message = rs[1]
                resultData = rs[2]
                len_resultData = rs[3]
                if len_resultData > 0:
                    payment = float(resultData[0]['amount'])
                    break
                else:
                    payment = 0
                    is_success = False
                    message = '此保单未查询到待新契约收费记录！'
                    time.sleep(1)
                    #判断是否进入双录
                    if i in (5,10,20,30,40,50):
                        #连接数据库
                        cursor = API0000_diy().db_conf(env_name,'wift_prop')   #连接数据库
                        sql = "select proposal_status from t_proposal where PROPOSAL_NO='" + proposalNo + "'"
                        cursor.execute(sql)
                        result = cursor.fetchall()
                        proposal_status = str(result[0][0])   #新契约状态
                        if proposal_status == '46':
                            is_success = False
                            message = '经数据库查询，新契约进入双录，请手动进行双录处理！'
                            break  
            #存入dict
            dict['policy_info']['payment_nb']['payment'] = payment  # 新契约收费金额                    
            assert is_success == True

            """step2:柜面收付费保存接口"""    
            #节点初始化
            is_success = ''
            unit = '节点：系统-新契约收费_柜面收付费保存接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            bankEndorse = '123123'  # 银行凭证号码
            feeConfirmDate = dict['policy_info']['applicationDate']  # 费用确认日期
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
            assert is_success == True

            """step3:柜面收付费审核接口"""    
            #节点初始化
            is_success = ''
            unit = '节点：系统-新契约收费_柜面收付费审核接口'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_payment().finishFeeFlow(magicX, interface_ip, resultData, bankEndorse, feeConfirmDate, internalAccount, internalBankCode, feeChannel, internalBankName)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            assert is_success == True 

            """step4:验证收费后新契约状态是否流转"""
            #节点初始化
            is_success = ''
            unit = '节点：系统-新契约收费_验证收费后节点是否流转'  # 节点
            message = ''         
            #遍历
            for i in range(0, 60):
                #连接数据库
                cursor = API0000_diy().db_conf(env_name,'wift_prop')   #连接数据库
                sql1 = "select proposal_status from t_proposal where PROPOSAL_NO='" + proposalNo + "'"
                cursor.execute(sql1)
                result1 = cursor.fetchall()
                proposal_status1 = str(result1[0][0])
                if proposal_status1 == '61':
                    is_success = False
                    message = '经数据库查询，新契约收费成功后，保单状态仍为“待收费”状态，120s节点未流转，请检查是否环境问题或者产品犹豫期是否未配置！'
                    time.sleep(2)
                    continue
                if proposal_status1 == '81':
                    is_success = True
                    message = ''
                    break
            assert is_success == True

            dict['logInfo']['code'] == '1' 
            end_time = datetime.datetime.now()   #结束时间 
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*' + thread_name + ':新契约收费_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))   
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] == '0'
            dict['logInfo']['err'] = unit + str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                username = dict['public']['username_review']    #新契约复核用户
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
            #记录日志
            logging.warning(API0000_diy().text_conversion('异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict
            


    """新契约回执"""
    @func_set_timeout(90)#设定函数超执行时间
    def nb_receipt(self, magicX, dict, thread_name):
        """
           step1:保单确认回执查询接口
           step2:保单确认回执接口
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*' + thread_name + ':新契约回执_开始(预计耗时:30s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            """step1:保单确认回执查询接口"""
            #节点初始化
            is_success = ''    #初始化是否成功标识
            unit = '节点：系统-新契约回执_保单确认回执查询接口'  # 节点
            message = ''    #初始化信息
            #dict获取数据+定义数据
            interface_ip = dict['public']['interface_ip']  # 接口ip
            policyNo = dict['policy_info']['policyNo']  # 保单号
            for i in range(0, 200):
                #调用原子脚本
                response = API0000_nb().query_policyReceiptConfirm(magicX, interface_ip, policyNo)
                #获取所需响应值
                is_success = response['isSuccess']
                if is_success:
                    message = ''
                    resultData = response['resultData']
                else:
                    message = response['message']
                    resultData = ''
                #重复发送接口请求
                if resultData != '' and resultData != None:
                    break
                else:
                    time.sleep(0.5)
            assert is_success == True 
            
            """step2:保单确认回执接口"""
            #节点初始化
            #time.sleep(2)
            is_success = ''
            unit = '节点：系统-新契约回执_保单确认回执接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            proposalNo = dict['policy_info']['proposalNo']  # 投保单号
            callBackDate = dict['policy_info']['effectiveDate']  # 回执日期
            callBackWay = '01'  # 回执方式
            appointVisitStartTime = ''  # 预约回访起始日期
            appointVisitEndTime = ''  # 预约回访终止日期
            for j in range(0, 3):
                #调用原子脚本
                response = API0000_nb().policyReceiptConfirm(magicX, interface_ip, policyNo, proposalNo, callBackDate, callBackWay, appointVisitStartTime, appointVisitEndTime)
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                    break
                else:
                    message = response['message']
                    if message == '' or message == None:
                        message = '保单确认回执接口未回执成功，建议通过数据库sql插入保单回执日期！'
                    time.sleep(1)
            #断言
            assert is_success == True    
            
            #存入dict:
            dict['policy_info']['policy_status'] = '01'   #保单状态。01有效；02失效
            dict['policy_info']['callBackDate'] = callBackDate   #回执日期
            dict['logInfo']['code'] = '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*' + thread_name + ':新契约回执_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] == '0'
            dict['logInfo']['err'] = unit + str(e)
            #记录日志
            logging.warning(API0000_diy().text_conversion('异常位置-' + unit + ':\n')  + traceback.format_exc())
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
        job = 'nb'   #场景名
        magicX1 = ''
        magicX2 = ''
        thread_result_list = []
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = '预生产'
            env_name = env_name.encode('utf-8')
            applicationDate = '2022-02-01'   #投保日期
            username_entry = 'xcy1'   #保全录入用户名
            username_review = 'xcy2'   #保全复核用户名
            agent = '10000001-吴文新'   #代理人；10000001-吴文新 ; DT640164655-蒋诗芸
            partner = 'shengtang-盛唐融信保险代理（北京）有限公司'   #合作网点; shengtang-盛唐融信保险代理（北京）有限公司;2100001-大童保险销售服务有限公司浙江分公司
            nb_time = '2'   #出单次数
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
                nb_time = ''
                filename = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','applicationDate','username_entry','username_review','agent','partner','nb_time','filename']
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
                nb_time = rs[2][6]   #出单次数
                filename = rs[2][7]   #excel测试数据路径
        #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name,'applicationDate':applicationDate, 'nb_time':str(nb_time)}   #录入字段中待校验字典
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
        dict['policy_info']['applicationDate'] =  applicationDate.strip()    #投保日期
        dict['public']['filename'] =  filename    #excel测试数据路径
        dict['public']['username_entry'] = username_entry.strip()
        dict['public']['username_review'] = username_review.strip()
        dict['public']['agent'] = agent.strip()
        dict['public']['partner'] = partner.strip()
        dict['public']['nb_time'] = str(nb_time).strip()
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
            rs = sys_API0001_2().nb(env_name, dict)
            thread_result_list = rs[0]
            magicX1 = rs[1]
            magicX2 = rs[2]
            dict = rs[3]
    except Exception, e:   #常见异常的捕捉
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:    #函数超时异常的捕捉
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出（可能他人改时间重启服务请检查！）'))
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。（可能他人改时间重启服务请检查！）' + dict['logInfo']['msg']
    finally:
        try:
            if is_run == True:
                #登出系统
                if magicX1 != '':
                    API0000_sys_otherapi().deblocking(magicX1, API0000_diy().ip_conf(env_name), username_entry)
                if magicX2 != '':
                    API0000_sys_otherapi().deblocking(magicX2, API0000_diy().ip_conf(env_name), username_review)
            end_time = datetime.datetime.now()   #记录结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:   #windows系统平台
                print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                print ('投保日期：' + applicationDate).decode('utf-8').encode('gb2312')
                print ('录入的代理人：' + agent.strip()).decode('utf-8').encode('gb2312')
                print ('录入的合作网点：' + partner.strip()).decode('utf-8').encode('gb2312')
                print ('总耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                print ('录入的出单次数：' + str(nb_time)).decode('utf-8').encode('gb2312')
                print ('多线程出单结果：').decode('utf-8').encode('gb2312')
                if thread_result_list == []:
                    print '[]'
                else:
                    for j in range(0, len(thread_result_list)):
                        #执行结果
                        if thread_result_list[j]['code'] == '0':
                            run_result = '不成功'
                        elif thread_result_list[j]['code'] == '1':
                            run_result = '成功'
                        #出单不成功原因
                        if thread_result_list[j]['msg'] == '':
                            run_msg = ''
                        else:
                            run_msg = '，出单不成功原因：' + thread_result_list[j]['msg']
                        print (str(j+1) + '.保单号：' + thread_result_list[j]['policyNo'] + '，是否出单成功：' + run_result + run_msg).decode('utf-8').encode('gb2312')
                if thread_result_list == []:
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
            else:    #非windows系统平台
                result_str = "环境：%s,,投保日期：%s,,录入的代理人：%s,,录入的合作网点：%s,,总耗时：%s,,录入的出单次数：%s次,,多线程出单结果：" % (env_name, applicationDate, agent.strip(), partner.strip(), API0000_diy().logger_count_time(begin_time, end_time), str(nb_time))
                if thread_result_list == []:
                    result_str = result_str + ',,' + '[]'
                else:
                    for j in range(0, len(thread_result_list)):
                        #执行结果
                        if thread_result_list[j]['code'] == '0':
                            run_result = '不成功'
                        elif thread_result_list[j]['code'] == '1':
                            run_result = '成功'
                        #出单不成功原因
                        if thread_result_list[j]['msg'] == '':
                            run_msg = ''
                        else:
                            run_msg = '，出单不成功原因：' + thread_result_list[j]['msg']
                        result_str = result_str + ',,' + str(j+1) + '.保单号：' + thread_result_list[j]['policyNo'] + '，是否出单成功：' + run_result + run_msg
                if thread_result_list == []:
                    result_str = result_str + ',,不成功原因：' + dict['logInfo']['msg']
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())








