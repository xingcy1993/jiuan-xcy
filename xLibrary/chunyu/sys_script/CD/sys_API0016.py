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



"""系统客户重要资料变更:
       step1:保全录入:
             1.保全录入用户登录系统
             2.查询保单客户角色接口
             3.保全申请接口
             4.保全录入-客户受理信息接口
             5.保全录入-查询被选择改变的客户信息
             6.保全录入-客户重要资料修改接口
             7.保全录入-查询保费变化接口
             8.保全录入-查询客户账号接口
             9.保全录入-添加或更改客户账号信息接口
             10.保全录入-客户重要资料变更提交接口
             11.登出系统
       step2:保全复核:
             1.保全复核用户登录系统
             2.保全复核-保全公共工作池查询接口 
             3.保全复核-工作池领取任务接口
             4.保全复核提交接口
             
             若存在保全收付费（转进账单）:
             5.BCP支付方式查询接口
             6.BCP支付方式变更转进账单接口
             7.柜面收付费查询接口
             8.柜面收付费保存接口
             9.柜面收付费审核接口
             10登出系统
       step3:定义轨迹信息+检查点信息+更改dict信息:
             1.定义轨迹信息
             2.定义检查点信息
             3.更改dict信息:
                (1)改客户信息
                (2)改险种信息
"""
class sys_API0016:

    def __init__(self):
        pass


    @func_set_timeout(180)#设定函数超执行时间
    def CD(self, apply_date, modify_info_dict, dict):
        """系统客户重要资料变更:
               step1:保全录入
               step2:保全复核+保全收费（转进账单）
               step3:定义轨迹信息+检查点信息+更改dict信息:
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('客户重要资料变更_开始(预计耗时:60s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            payment = 0
            policyProductPremChgs = []
            #保全录入
            rs = self.pa_entry(apply_date, modify_info_dict, dict)  
            policyProductPremChgs = rs[0]
            dict = rs[1]
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #保全复核
            rs = self.pa_review(apply_date, policyProductPremChgs, dict)  
            payment = rs[0]
            dict = rs[1]
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('客户重要资料变更_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
        finally:
            #dict存入检查点信息
            if dict['logInfo']['code'] == '1':
                dict = self.save_check_info(apply_date, modify_info_dict, policyProductPremChgs, payment, dict)
        return dict


    @func_set_timeout(90)#设定函数超执行时间
    def pa_entry(self, apply_date, modify_info_dict, dict):
        """step1:保全录入:
                 1.保全录入用户登录系统
                 2.查询保单客户角色接口
                 3.保全申请接口
                 4.保全录入-客户受理信息接口
                 5.保全录入-查询被选择改变的客户信息
                 6.保全录入-客户重要资料修改接口
                 7.保全录入-查询保费变化接口
                 8.保全录入-查询客户账号接口
                 9.保全录入-添加或更改客户账号信息接口
                 10.保全录入-客户重要资料变更提交接口
                 11.登出系统
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全录入_开始(预计耗时:30s)'))
            #初始化
            magicX = ''
            """1.保全录入用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全录入用户登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username = dict['public']['username_entry']    #保全录入用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            # 加入断言
            assert is_success == True 

            """2.查询保单客户角色接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_查询保单客户角色接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            if modify_info_dict['roleType'] != '':
                roleType = modify_info_dict['roleType']   #角色类型:1-投保人；2-被保人；3-受益人；4-代理人（保单无对应角色，默认为被保人）
            else:
                roleType = '2'
            policyNo = dict['policy_info']['policyNo']    #保单号
            serviceCode = '10016'  #保全申请项目编号
            #调用原子脚本
            response = API0000_pa().queryPolicyRoleCustomer(magicX, interface_ip, policyNo, serviceCode)
            #获取所需响应值
            is_success = response['isSuccess']
            customerId = ''
            holder_customerId = ''
            if is_success == True and len(response['resultData']) > 0:
                message = ''
                #遍历resultData:根据客户角色+姓名，获取customerId
                for i in range(0, len(response['resultData'])):
                    if response['resultData'][i]['roleType'] == '1':
                        holder_customerId = response['resultData'][i]['customerId']
                        print 1.0
                    if (response['resultData'][i]['roleType'] == str(roleType)) and (str(response['resultData'][i]['certiCode']) == modify_info_dict['oldcertiCode']):
                        customerId = str(response['resultData'][i]['customerId'])   #客户id
                        print 1.1
                        break
                print 1 
            elif is_success == True and len(response['resultData']) == 0:
                is_success = False
                message = 'The policy has no customer information!'
                print 2
            elif is_success == False:
                message = response['message']
                print 3
            # 加入断言
            if is_success == True and len(response['resultData']) > 0 and customerId == '':
                is_success = False
                message = 'Name mismatch, Please change name!'
                print 4
            assert is_success == True 


            """3.保全申请接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全申请接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            applyTime = apply_date   #保全申请日期
            applyWay = '3'    #保全申请来源
            applyType = '1'    #保全申请方式
            serviceCode = '10016'  #保全申请项目编号
            policyCodes = policyNo
            #调用原子脚本
            response = API0000_pa().saveCsApplylication_CD(magicX, interface_ip, applyTime, applyWay, applyType, serviceCode, policyNo, policyCodes, customerId) 
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
                partitionIndi = str(response['others']['partitionIndi'])
                changeId = response['others']['changeId']
                applyNo = response['others']['applyNo']
                subSalesChannel = response['others']['subSalesChannel']
                policyDeliveryMode = response['others']['policyDeliveryMode']
            else:
                message = response['message']
                partitionIndi = ''
                changeId = ''
                applyNo = ''
                subSalesChannel = ''
                policyDeliveryMode = ''
            # 加入断言
            assert is_success == True 

            """4.保全录入-客户受理信息接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全录入-客户受理信息接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_pa().findCsApplylication(magicX, interface_ip, env_name, applyTime, applyWay, applyType, serviceCode, policyNo, partitionIndi, changeId, applyNo, subSalesChannel,policyDeliveryMode)
            # 获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''   
                others = response['others']  
            else:
                message = response['message']
                others = ''
            assert is_success == True      
                #连接数据库
            cursor = API0000_diy().db_conf(env_name, 'wift_prop') 
            policyId = others['policyId']
            contactNumber = others['mobile']   #保全电话
            telephone = others['officeTel']   #固定电话
            customerInfoList_old = others['customerInfoList']
            customerInfoList_new = []
            for i in range(0,len(customerInfoList_old)):
                customerInfoList_new.append({})
                customerId1 = str(customerInfoList_old[i]['customerId'])
                name1 = customerInfoList_old[i]['name']
                certiType1 = customerInfoList_old[i]['certiType']
                birthday1 = customerInfoList_old[i]['birthday']
                #查询数据库最后一次修改的证件止期
                sql = "select CERTI_VALID_END_DATE from t_prop_customer where name='" + name1 + "' and GLOBAL_CUST_ID='" + customerId1 + "' ORDER BY update_time desc"
                cursor.execute(sql)
                result = cursor.fetchall()
                certiValidEndDate1 = result[0][0].strftime('%Y-%m-%d')
                #拼装新的customerInfoList
                customerInfoList_new[i]['customerId'] = customerId1
                customerInfoList_new[i]['name'] = name1
                customerInfoList_new[i]['certiType'] = certiType1
                customerInfoList_new[i]['birthday'] = birthday1
                customerInfoList_new[i]['certiValidEndDate'] = certiValidEndDate1
                customerInfoList = customerInfoList_new
            # 加入断言
            assert is_success == True 


            """5.保全录入-查询被选择改变的客户信息"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全录入-查询被选择改变的客户信息'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_pa().queryCustomerChangeSelected(magicX, interface_ip, policyNo, partitionIndi, applyNo)
            # 获取所需响应值
            is_success = response['isSuccess']
            if is_success:
                message = ''   
                resultData = response['resultData'] 
            else:
                message = response['message']
                resultData = ''
            # 加入断言
            assert is_success == True 

            """6.保全录入-客户重要资料修改接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全录入-客户信息修改接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            for i in range(0, len(resultData)):
                if str(resultData[i]['customerId']) == customerId:
                    old_name = resultData[i]['name']   #姓名
                    old_gender = resultData[i]['gender']   #性别
                    old_birthday = resultData[i]['birthday']   #出生日期
                    old_certiType = resultData[i]['certiType']   #证件类型
                    old_certiCode = resultData[i]['certiCode']   #证件号码
                    old_jobCateId = resultData[i]['jobCateId']   #职业代码/名称
                    old_income = resultData[i]['income']   #个人年收入（万元）
                    old_familyIncome = resultData[i]['familyIncome']   #家庭年收入（万元）
                    old_incomeSource = resultData[i]['incomeSource']   #收入来源
                    old_incomeSourceNote = resultData[i]['incomeSourceNote']   #收入来源备注
                    old_companyName = resultData[i]['companyName']   #工作单位
                    break
            #客户信息修改接口录入信息:
                #姓名
            name = urllib.quote(old_name.encode("utf-8"))
                #性别
            if modify_info_dict['gender']['is_modify'] == 'Y':
                gender = modify_info_dict['gender']['new']
            else:
                gender = old_gender
                #出生日期
            if modify_info_dict['birthday']['is_modify'] == 'Y':
                birthday = modify_info_dict['birthday']['new']
            else:
                birthday = old_birthday
                #证件类型
            if modify_info_dict['certiType']['is_modify'] == 'Y':
                certiType = modify_info_dict['certiType']['new']
            else:
                certiType = old_certiType
                #证件号码
            if modify_info_dict['certiCode']['is_modify'] == 'Y':
                certiCode = modify_info_dict['certiCode']['new']
            else:
                certiCode = old_certiCode 
                #职业代码/名称
            if modify_info_dict['jobCateId']['is_modify'] == 'Y':
                jobCateId = modify_info_dict['jobCateId']['new']
            else:
                jobCateId = old_jobCateId 
                #职业等级
            cursor = API0000_diy().db_conf(env_name,'wift_iiws')        
            sql = "select * from d_job_category where code='" + str(jobCateId) + "';" 
            cursor.execute(sql)
            result = cursor.fetchall() 
            jobClass = result[0][4]
                #个人年收入（万元）
            if modify_info_dict['income']['is_modify'] == 'Y':
                income = modify_info_dict['income']['new']
            else:
                income = old_income    
                #家庭年收入（万元）
            if modify_info_dict['familyIncome']['is_modify'] == 'Y':
                familyIncome = modify_info_dict['familyIncome']['new']
            else:
                familyIncome = old_familyIncome 
                #收入来源
            if modify_info_dict['incomeSource']['is_modify'] == 'Y':
                incomeSource = modify_info_dict['incomeSource']['new']
            else:
                incomeSource = old_incomeSource 
                #收入来源备注
            if modify_info_dict['incomeSourceNote']['is_modify'] == 'Y':
                incomeSourceNote = modify_info_dict['incomeSourceNote']['new']
            else:
                incomeSourceNote = old_incomeSourceNote
                #工作单位
            if modify_info_dict['companyName']['is_modify'] == 'Y':
                companyName = modify_info_dict['companyName']['new']
            else:
                companyName = old_companyName
            #调用原子脚本
            response = API0000_pa().updateCustomerImpWithSimilar(magicX, interface_ip, name, applyNo, changeId, customerId, gender, birthday, certiType, certiCode, jobCateId, jobClass, income, familyIncome, incomeSource, incomeSourceNote, companyName)
            # 获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            # 加入断言
            assert is_success == True 

            """7.保全录入-查询保费变化接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全录入-查询保费变化接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_pa().queryMsgChgPrem(magicX, interface_ip, applyNo, customerId, name, gender, birthday, certiType, certiCode, jobCateId)
            #获取所需响应值
            is_success = response['isSuccess']
            if is_success:
                message = ''
                policyProductPremChgs = response['resultData']
            else:
                message = response['message']
                policyProductPremChgs = ''                    
            # 加入断言
            assert is_success == True 

            """8.保全录入-查询客户账号接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全录入-查询客户账号接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_pa().customerAccQuery(magicX, interface_ip, holder_customerId, changeId)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
                accountId = response['others'][0]['accountId']
                accountType = response['others'][0]['accouontType']
                accountCode = response['others'][0]['accountCode']
                payMode = response['others'][0]['payMode']
                accountName = response['others'][0]['accountName']
                bankCode = response['others'][0]['bankCode']
                reserveMobile = response['others'][0]['reserveMobile']
            else:
                message = response['message']
            # 加入断言
            assert is_success == True

            """9.保全录入-添加或更改客户账号信息接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全录入-添加或更改客户账号信息接口'  # 节点
            message = ''
            bankAccount = accountCode
            #调用原子脚本
            response = API0000_pa().addOrUpdateCustImpChgAccount(magicX, interface_ip, changeId, accountId, accountType, payMode, accountName, bankCode, bankAccount, reserveMobile)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            # 加入断言
            assert is_success == True 
            
            """10.保全录入-客户重要资料变更提交接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全录入-客户重要资料变更提交接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            applyTime = applyTime + " 00:00:00"  #组装申请日期applyTime
            flag = True
            csProductCals = resultData
            #调用原子脚本
            response = API0000_pa().entryConfirm_CD(magicX, interface_ip, changeId, applyNo, partitionIndi, policyId, policyNo, subSalesChannel, applyTime, serviceCode, policyProductPremChgs, customerInfoList)
            # 获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            # 加入断言
            assert is_success == True 

            """11.保全录入-登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全录入-登出系统'  # 节点
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
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全录入_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return policyProductPremChgs, dict


    @func_set_timeout(90)#设定函数超执行时间
    def pa_review(self, apply_date, policyProductPremChgs, dict):
        """step2:保全复核:
                 1.保全复核用户登录系统
                 2.保全复核-保全公共工作池查询接口 
                 3.保全复核-工作池领取任务接口
                 4.保全复核提交接口
             
                 保全收费（转进账单）:
                 5.BCP支付方式查询接口
                 6.BCP支付方式变更转进账单接口
                 7.柜面收付费查询接口
                 8.柜面收付费保存接口
                 9.柜面收付费审核接口
                 10登出系统
        """
        try:
            begin_time1 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全复核_开始(预计耗时:10s)'))
            #初始化
            payment = 0
            magicX = ''
            """保全复核"""
            """1.保全复核用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全复核用户登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username = dict['public']['username_review']    #保全复核用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name,username, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            # 加入断言
            assert is_success == True 

            """2.保全复核-保全公共工作池查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全复核-保全公共工作池查询接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            policyNo = dict['policy_info']['policyNo']    #保单号
            #调用原子脚本
            response = API0000_pa().queryCsInfoList(magicX, interface_ip, policyNo) 
            #获取所需响应值
            is_success = response['isSuccess']
            if is_success == True and response['resultData'] != []:
                message = ''
                changeId = response['resultData'][0]['changeId']
                partitionIndi = str(response['resultData'][0]['partitionIndi'])
                serviceCode = response['resultData'][0]['serviceCode']
                applyNo = response['resultData'][0]['applyNo']
            elif is_success == True and response['resultData'] == []:
                is_success = False
                message = '保全公共工作池未查询此保单记录！'
            elif is_success == False:
                message = response['message']
                changeId = ''
                partitionIndi = ''
                serviceCode = ''
                applyNo = ''
            assert is_success == True

            """3.保全复核-工作池领取任务接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全复核-工作池领取任务接口'  # 节点
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

            """4.保全复核提交接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全复核提交接口'  # 节点
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
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全复核_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time1, end_time1)))


            """保全收付费"""
            begin_time2 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全收付费_开始(预计耗时:20s)'))

            #判断保单各险种是否存在保费变化
            ispayment = 'F'   #是否收付费标识默认为F      
            for j in range(0, len(policyProductPremChgs)):
                if policyProductPremChgs[j]['premDif'] != 0:
                    ispayment = 'Y'
                    break
            #存在保费变化，进行收付费操作
            if ispayment == 'Y':
                """5.BCP支付方式查询接口"""
                #节点初始化
                is_success = ''
                unit = '系统-保全客户重要资料变更_BCP支付方式查询接口'  # 节点
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
                
                """6.BCP支付方式变更转进账单接口"""
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
                
                """7.柜面收付费查询接口"""
                #节点初始化
                is_success = ''
                unit = '系统-保全客户重要资料变更_柜面收付费查询接口'  # 节点
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

                if len(resultData) == 0:
                    message = '未查询到保单付费记录！'
                else:
                    payment = float(resultData[0]['amount'])  
                    #断言
                    assert is_success == True 
                """8.柜面收付费保存接口"""
                #节点初始化
                is_success = ''
                unit = '系统-保全客户重要资料变更_柜面收付费保存接口'  # 节点
                message = ''
                #dict获取数据+定义数据
                bankEndorse = '123123'  # 银行凭证号码
                feeConfirmDate = apply_date   #收费日期（保全申请日期）
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

                """9.柜面收付费审核接口"""
                #节点初始化
                is_success = ''
                unit = '系统-保全客户重要资料变更_柜面收付费审核接口'  # 节点
                message = ''
                #调用原子脚本
                rs = API0000_payment().finishFeeFlow(magicX, interface_ip, resultData, bankEndorse, feeConfirmDate, internalAccount, internalBankCode, feeChannel, internalBankName)
                #获取所需响应值
                is_success = rs[0]
                message = rs[1]
                # 加入断言
                assert is_success == True 
    
            """10.保全复核-登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全客户重要资料变更_保全复核-登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX,interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            # 加入断言
            assert is_success == True
            dict['logInfo']['code'] = '1'   #记录无异常标识
            end_time2 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*保全收付费_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time2, end_time2)))
        except Exception, e:
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return payment, dict


    @func_set_timeout(30)#设定函数超执行时间
    def save_check_info(self, apply_date, modify_info_dict, policyProductPremChgs, payment, dict):
        """step3:定义轨迹信息+检查点信息+更改dict信息:
                1.定义轨迹信息
                2.定义检查点信息
                3.更改dict信息:
                    (1)改客户信息
                    (2)改险种信息
        """
        try:
            env_name = dict['public']['env_name']   #环境名称
            """1.定义检查点信息"""
            cursor = API0000_diy().db_conf(env_name, 'wift_iiws') 
            product = []   #定义产品列表
            for i in range(0, len(policyProductPremChgs)):    
                #产品id
                productId = str(policyProductPremChgs[i]['productId'])
                productCode = API0000_diy().query_productCode(env_name, productId)   #产品代码
                #产品保费变化值
                premDif = float(policyProductPremChgs[i]['premDif'])
                #定义每个产品的字典内容,并追加到product列表中
                each_product_dict = {'productCode':productCode, 'premDif':premDif}
                product.append(each_product_dict)
            if dict['logInfo']['code'] == '1':
                dict['check']['calc_CD'].append({'apply_date':apply_date, 'product':product, 'payment':payment, 'msg': ''})
                """2.定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'CD', 'trackTime':apply_date, 'trackData':{'product':product, 'payment':payment}, 'msg': ''}
                dict['track_info'].append(track_info)   #存入轨迹信息
                product_list = dict['policy_info']['main_risk_info'] + dict['policy_info']['sub_risk_info']   #组装保单产品列表
                """3.更改dict信息"""
                #(1)更改客户信息
                #角色为投保人时:
                if modify_info_dict['roleType'] == '1':
                    #性别
                    if modify_info_dict['gender']['is_modify'] == 'Y':
                        dict['policy_info']['holder_info']['gender'] = modify_info_dict['gender']['new'] 
                    #出生日期
                    if modify_info_dict['birthday']['is_modify'] == 'Y':
                        dict['policy_info']['holder_info']['pbHoldBirth'] = modify_info_dict['birthday']['new']  
                    #证件类型
                    if modify_info_dict['certiType']['is_modify'] == 'Y':
                        dict['policy_info']['holder_info']['certiType'] = modify_info_dict['certiType']['new']
                    #证件号码
                    if modify_info_dict['certiCode']['is_modify'] == 'Y':
                        dict['policy_info']['holder_info']['certiCode'] = modify_info_dict['certiCode']['new']  
                    #职业代码/名称+职业等级
                    if modify_info_dict['jobCateId']['is_modify'] == 'Y':
                        dict['policy_info']['holder_info']['jobCode'] = modify_info_dict['jobCateId']['new']    
                        cursor = API0000_diy().db_conf(env_name,'wift_iiws')        
                        sql = "select * from d_job_category where code='" + str(modify_info_dict['jobCateId']['new']) + "';" 
                        cursor.execute(sql)
                        result = cursor.fetchall() 
                        dict['policy_info']['holder_info']['jobClass'] = result[0][4]
                    #个人年收入（万元）
                    if modify_info_dict['income']['is_modify'] == 'Y':
                        dict['policy_info']['holder_info']['annualIncome'] = modify_info_dict['income']['new']
                    #家庭年收入（万元）
                    if modify_info_dict['familyIncome']['is_modify'] == 'Y':
                        dict['policy_info']['holder_info']['familyIncome'] = modify_info_dict['familyIncome']['new']
                    #收入来源
                    if modify_info_dict['incomeSource']['is_modify'] == 'Y':
                        dict['policy_info']['holder_info']['incomeSource'] = modify_info_dict['incomeSource']['new']   
                    #收入来源备注
                    if modify_info_dict['incomeSourceNote']['is_modify'] == 'Y':
                        dict['policy_info']['holder_info']['incomeSourceNote'] = modify_info_dict['incomeSourceNote']['new'] 
                    #工作单位
                    if modify_info_dict['companyName']['is_modify'] == 'Y':
                        dict['policy_info']['holder_info']['workCompany'] = modify_info_dict['companyName']['new'] 
                #角色为被保人时:
                elif modify_info_dict['roleType'] == '2':
                    #找到变更的是哪个被保险人
                    for i in range(0,len(dict['policy_info']['insured_info'])):
                        if dict['policy_info']['insured_info'][i]['insuCertiCode'] == modify_info_dict['oldcertiCode']:
                            break    
                    #性别
                    if modify_info_dict['gender']['is_modify'] == 'Y':
                        dict['policy_info']['insured_info'][i]['insuGender'] = modify_info_dict['gender']['new'] 
                    #出生日期
                    if modify_info_dict['birthday']['is_modify'] == 'Y':
                        dict['policy_info']['insured_info'][i]['insuBirth'] = modify_info_dict['birthday']['new']  
                    #证件类型
                    if modify_info_dict['certiType']['is_modify'] == 'Y':
                        dict['policy_info']['insured_info'][i]['insuCertiType'] = modify_info_dict['certiType']['new']
                    #证件号码
                    if modify_info_dict['certiCode']['is_modify'] == 'Y':
                        dict['policy_info']['insured_info'][i]['insuCertiCode'] = modify_info_dict['certiCode']['new']  
                    #职业代码/名称+职业等级
                    if modify_info_dict['jobCateId']['is_modify'] == 'Y':
                        dict['policy_info']['insured_info'][i]['insuWorkCode'] = modify_info_dict['jobCateId']['new']    
                        cursor = API0000_diy().db_conf(env_name,'wift_iiws')        
                        sql = "select * from d_job_category where code='" + str(modify_info_dict['jobCateId']['new']) + "';" 
                        cursor.execute(sql)
                        result = cursor.fetchall() 
                        dict['policy_info']['insured_info'][i]['insujobClass'] = result[0][4]
                    #个人年收入（万元）
                    if modify_info_dict['income']['is_modify'] == 'Y':
                        dict['policy_info']['insured_info'][i]['annualIncome'] = modify_info_dict['income']['new']
                    #收入来源
                    if modify_info_dict['incomeSource']['is_modify'] == 'Y':
                        dict['policy_info']['insured_info'][i]['insuincomeSource'] = modify_info_dict['incomeSource']['new']   
                    #收入来源备注
                    if modify_info_dict['incomeSourceNote']['is_modify'] == 'Y':
                        dict['policy_info']['insured_info'][i]['insuincomeSourceNote'] = modify_info_dict['incomeSourceNote']['new'] 
                    #工作单位
                    if modify_info_dict['companyName']['is_modify'] == 'Y':
                        dict['policy_info']['insured_info'][i]['insuCompany'] = modify_info_dict['companyName']['new'] 
                elif modify_info_dict['roleType'] == '3':
                    pass
                elif modify_info_dict['roleType'] == '4':
                    pass
               #(2)更改产品信息
                for i in range(0, len(policyProductPremChgs)):
                    #产品代码
                    productId = str(policyProductPremChgs[i]['productId'])
                    #产品主附险标识
                    Main_Rider = product_list[i]['Main_Rider']
                    #产品变化前保费
                    premBfChg = policyProductPremChgs[i]['premBfChg']
                    #产品变化后保费
                    premAfChg = policyProductPremChgs[i]['premAfChg']
                    #产品变化前保额
                    amountBfChg = policyProductPremChgs[i]['amountBfChg']
                    #产品变化后保额
                    amountAfChg = policyProductPremChgs[i]['amountAfChg']
                    
                    #改保费
                    if premBfChg != premAfChg:
                        if Main_Rider == 'M':
                            dict['policy_info']['main_risk_info'][i]['stdPremBf'] = str(premAfChg)
                        #若产品为附加险，遍历主险进行替换
                        elif Main_Rider == 'R':
                            dict['policy_info']['sub_risk_info'][i-len(dict['policy_info']['main_risk_info'])]['stdPremBf'] = str(premAfChg)    
                    #改保额
                    if amountBfChg != amountAfChg:
                        if Main_Rider == 'M':
                            dict['policy_info']['main_risk_info'][i]['sumAssured'] = str(amountAfChg)
                        #若产品为附加险，遍历主险进行替换
                        elif Main_Rider == 'R':
                            dict['policy_info']['sub_risk_info'][i-len(dict['policy_info']['main_risk_info'])]['sumAssured'] = str(amountAfChg)
            else:
                message = dict['logInfo']['msg']
                err = dict['logInfo']['err']
                if dict['logInfo']['msg'] == None or dict['logInfo']['msg'] == '':
                    message = str(dict['logInfo']['err'])
                dict['check']['calc_CD'].append({'apply_date':apply_date, 'product':'', 'payment':payment, 'msg': message})
                """2.定义轨迹信息"""
                #定义轨迹信息
                track_info = {'trackType':'CD', 'trackTime':apply_date, 'trackData':{'product':'', 'payment':payment}, 'msg': message}
                dict['track_info'].append(track_info)   #存入轨迹信息
                product_list = dict['policy_info']['main_risk_info'] + dict['policy_info']['sub_risk_info']   #组装保单产品列表
        except Exception, e:
            dict['logInfo']['code'] = '0'    #记录异常标识
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        finally:
            pass
        return dict



if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING , format='%(message)s  %(asctime)s')

    #1.自定义录入
    execNo = 'test001'   #测试编号
    env_name = '预生产'
    env_name = env_name.encode('utf-8')
    policyNo = '8088646849048068'
    apply_date = '2021-04-07'   #保全申请日期
    username_entry = 'xcy1'   #保全录入用户名
    interface_ip = API0000_diy().ip_conf(env_name)
    #2.定义dict
    dict = {'execNo': execNo, 'policy_info': {'policyChannel': u'03', 'organId': '10008', 'effectiveDate': '2016-06-13', 'sub_risk_info': [], 'agent_info': {'agent_name': '', 'channelId': '', 'partnerId': '', 'agent_birthday': '', 'salesChannelText': '', 'agent_gender': '', 'headPartner': ''}, 'proposalNo': '1101021130094152', 'policy_status': '01', 'insured_info': [{'insuBirth': u'1988-01-02', 'insuEmail': 'ZCb86UWCMOj0@189.com', 'insuWeight': '78', 'insuDistrictCode': '110101', 'insuGender': u'0', 'insuCityCode': '110100', 'insuHeight': '178', 'insujobClass': '1', 'taxPayerType': '01', 'insuCertiType': u'2', 'insuMarriage': '20', 'insuPostalCode': '120000', 'insuMobile': u'18089837905', 'homeTel': '010-993433344', 'insuProvinceCode': '110000', 'insuincomeSourceNote': 'wu', 'insuresidentType': '1', 'driverLicenseType': '06', 'annualIncome': '5000000', 'insuCertiValidEndDate': u'2030-01-01', 'insunationnality1': '01', 'insuRelation': u'99', 'insuWorkType': '02', 'insuCertiCode': u'4567343400743', 'insuWorkCode': '0001001', 'insueducationId': '40', 'insuName': u'\u5f20\u56db\u7b2c', 'insuNationatiy': 'CHN', 'officeTel': '010-93456444', 'insuincomeSource': '01', 'insuAddrDetail': '\xe5\xbb\xba\xe5\x9b\xbd\xe9\x97\xa8\xe4\xb8\x9c\xe5\xa4\xa7\xe8\xa1\x9722\xe5\x8f\xb7', 'insumedicalInsType': '01', 'insuCompany': 'apple'}], 'end_reason': '', 'applicationDate': '2016-06-12', 'policyType': 1, 'invalid_reason': '', 'holder_info': {'familyIncome': '100000', 'districtCode': '110101', 'driverLicenseType': '06', 'mobilePhone': u'18909892905', 'weight':'67', 'annualIncome': '100000', 'medicalInsType': '01', 'Industry': '', 'taxPayerType': '01', 'nationnality1': '01', 'height': '167', 'certiCode': u'4567343400742', 'educationId': '40', 'pbCertiValidEndDate': u'2030-01-01', 'residentType':'1', 'incomeSource': '01', 'nationality': 'CHN', 'homeTel': '010-98343543', 'Email': '', 'jobClass': '1', 'cityCode': '110100', 'name': u'\u5f20\u56db\u53c8', 'incomeSourceNote': 'wu', 'workCompany': '\xe4\xb8\x9c\xe6\x96\xb9\xe5\xb0\x8f\xe6\xb8\x85\xe5\x8d\x8e', 'premBudget': '30000', 'gender': u'0', 'certiType': u'2', 'addrDetail': '\xe5\xbb\xba\xe5\x9b\xbd\xe9\x97\xa8\xe4\xb8\x9c\xe5\xa4\xa7\xe8\xa1\x9722\xe5\x8f\xb7', 'isMarried': '20', 'officeTel': '010-98343543', 'pbHoldBirth': u'1988-01-01', 'industry': '03', 'provinceCode': '110000', 'email': 'uWKiC@126.com', 'jobCode': '0001001', 'postalCode': '121200', 'Nationality': '', 'sameASInsurd': u'0'}, 'benf_info': [{}], 'callBackDate': '2016-06-12', 'policyNo': u'8088762766967068', 'main_risk_info': [{'sumAssured': 358900.0, 'coveragePeriod': u'10', 'stdPremBf': 100000, 'chargePeriod': u'3', 'bonusYearOrAge': u'4','chargePeriodType': u'Y', 'payOption': u'03', 'main_risk_num': '1', 'units': '', 'coverPeriodType': u'Y', 'planFreq': u'05', 'chargeMode': u'Y', 'productId':10038}], 'payment_nb': {'payMode': u'00', 'payment': 100000.0}}, 'public': {'username_review': u'xingcy1', 'apply_date': '', 'is_2risk': u'0', 'env_name': '\xe9\xa2\x84\xe7\x94\x9f\xe4\xba\xa7', 'interface_ip': '10.1.6.11', 'execNo': '', 'is_HolderExemption': u'0', 'total_times_renew': 0, 'username_entry': u'xingcy'},'track_info': [{'trackData': {'applicationDate': '2016-06-12', 'policyNo': u'8088762766967068'}, 'trackTime': '2016-06-12', 'trackType': 'nb'}], 'check': {'calc_renew': [], 'calc_hesitation_tb': {'apply_date': '', 'payment': ''}, 'calc_loan': [], 'calc_tb': [], 'calc_trial_tb': [], 'calc_survivalFee': [], 'calc_nb': {'product': [{'productCode': u'3237', 'amount': 358900.0, 'premium': 100000.0}], 'payment': 100000.0}, 'calc_CD':[]}, 'track_change':[]}
    oldcertiCode = '4567343400713'

    modify_info_dict = {
                    'roleType': '2',   #角色类型:1-投保人；2-被保人；3-受益人；4-代理人（保单无对应角色，默认为被保人）
                    'oldcertiCode': oldcertiCode,  #待变更的客户证件号码
                    'gender': {'is_modify':'Y', 'new':'0'},    #性别:0-男，1-女
                    'birthday': {'is_modify':'Y', 'new':'1980-10-10'},     #出生日期
                    'certiType': {'is_modify':'Y', 'new':'21'},     #证件类型
                    'certiCode': {'is_modify':'Y', 'new':'11010116102170170'},     #证件号码
                    'jobCateId': {'is_modify':'Y', 'new':'0001001'},     #职业代码/名称
                    'income': {'is_modify':'Y', 'new':'100'},     #个人年收入（万元）
                    'familyIncome': {'is_modify':'Y', 'new':'100'},    #家庭年收入（万元）
                    'incomeSource': {'is_modify':'Y', 'new':'01'},    #收入来源
                    'incomeSourceNote': {'is_modify':'Y', 'new':'haha'},    #收入来源备注
                    'companyName': {'is_modify':'Y', 'new':'renrenwang'}    #工作单位
                }

    #3.执行脚本
    dict = sys_API0016().CD(apply_date, modify_info_dict, dict)
    assert dict['logInfo']['code'] == '1'
    print '-----------'
    print dict








