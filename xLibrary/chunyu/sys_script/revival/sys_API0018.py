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
from xLibrary.chunyu.sys_script.Modify_servertime.sys_API0002_1 import sys_API0002



"""保单复效:
       step1:保全录入
            1.保全录入用户登录系统
            2.保全申请接口
            3.保全录入-产品信息详细
            4.保全录入-客户受理信息接口
            5.保全录入-支付方式及支付账户接口
            6.保全录入-复效提交接口
            7.登出系统 
       step2:保全复核+保全收费（转进账单）:
            1.保全复核用户登录系统
            2.保全复核-保全公共工作池查询接口 
            3.保全复核-工作池领取任务接口
            4.保全复核提交接口
            5.柜面收付费查询接口
            6.柜面收付费保存接口
            7.柜面收付费审核接口
            8.登出系统 
       step3:定义轨迹信息+检查点信息:
            1.定义轨迹信息
            2.定义检查点信息
"""
class sys_API0018:

    def __init__(self):
        pass


    @func_set_timeout(180)#设定函数超执行时间
    def revival(self, apply_date, scsRevivalInterestFree_flag, changeDetailModel_flag, dict):
        """系统复效:
               step1:保全录入
               step2:保全复核+保全收费（转进账单）
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
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '保单复效_开始(预计耗时:60s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            payment = 0
            csProductCals = ''
            #step1:保全录入
            rs = self.pa_entry(apply_date, scsRevivalInterestFree_flag, changeDetailModel_flag, dict)  
            csProductCals = rs[0]
            dict = rs[1]
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            #step2:保全复核+保全收费（转进账单）
            rs = self.pa_review(apply_date, dict)  
            payment = rs[0]   #收费费金额
            dict = rs[1]
            #断言
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '保单复效_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
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
            if dict['logInfo']['code'] == '1':
                dict = self.save_check_info(apply_date, payment, csProductCals, dict)
        return dict


    @func_set_timeout(60)#设定函数超执行时间
    def pa_entry(self, apply_date, scsRevivalInterestFree_flag, changeDetailModel_flag, dict):
        """step1:保全录入
                1.保全录入用户登录系统
                2.保全申请接口
                3.保全录入-产品信息详细
                4.保全录入-客户受理信息接口
                5.保全录入-支付方式及支付账户接口
                6.保全录入-复效提交接口
                7.登出系统 
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #初始化
            magicX = ''
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全录入_开始(预计耗时:30s)'))
            """1.保全录入用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_保全录入用户登录系统'  # 节点
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
            dict['public']['magicX'] = magicX
            assert is_success == True

            """2.保全申请接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_保全申请接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            policyNo = dict['policy_info']['policyNo']    #保单号
            applyTime = apply_date   #保全申请日期
            applyWay = '3'    #保全申请来源
            applyType = '1'    #保全申请方式
            serviceCode = '30202'  #保全申请项目编号
            #调用原子脚本
            response = API0000_pa().saveCsApplylication(magicX, interface_ip, applyTime, applyWay, applyType, serviceCode, policyNo) 
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
            assert is_success == True

            """3.保全录入-产品信息详细"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_保全录入-产品信息详细'  # 节点
            message = ''        
            #调用原子脚本
            response = API0000_pa().queryCsPolicyProduct(magicX, interface_ip, policyNo, changeId, partitionIndi, applyTime) 
            #获取所需响应值
            is_success = response['isSuccess']
            if is_success:
                message = ''
            else:
                message = response['message']
            #获取所需响应值
            csProductCals = response['resultData']
            for i in range(0,len(csProductCals)):
                csProductCals[i]['applyTime'] = applyTime
                csProductCals[i]['changeFlag'] = 'Y'
            assert is_success == True

            """4.保全录入-客户受理信息接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_保全录入-客户受理信息接口'  # 节点
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
            unit = '系统-保全复效_保全录入-客户受理信息接口_连接数据库'
            cursor = API0000_diy().db_conf(env_name, 'wift_prop') 
            policyId = others['policyId']
            customerInfoList_old = others['customerInfoList']
            customerInfoList_new = []
            for i in range(0,len(customerInfoList_old)):
                customerInfoList_new.append({})
                customerId = str(customerInfoList_old[i]['customerId'])
                name = customerInfoList_old[i]['name']
                certiType = customerInfoList_old[i]['certiType']
                birthday = customerInfoList_old[i]['birthday']
                #查询数据库最后一次修改的证件止期
                sql = "select CERTI_VALID_END_DATE from t_prop_customer where name='" + name + "' and GLOBAL_CUST_ID='" + customerId + "' ORDER BY update_time desc"
                unit = '系统-保全复效_保全录入-客户受理信息接口_数据库查询客户证件止期'
                cursor.execute(sql)
                result = cursor.fetchall()
                certiValidEndDate = result[0][0].strftime('%Y-%m-%d')
                #拼装新的customerInfoList
                customerInfoList_new[i]['customerId'] = customerId
                customerInfoList_new[i]['name'] = name
                customerInfoList_new[i]['certiType'] = certiType
                customerInfoList_new[i]['birthday'] = birthday
                customerInfoList_new[i]['certiValidEndDate'] = certiValidEndDate
                customerInfoList = customerInfoList_new
            assert is_success == True

            """5.保全录入-支付方式及支付账户接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_保全录入-支付方式及支付账户接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            payMode = '01'   #保全收付费方式:00-进展单；01-银行转账
            #调用原子脚本
            response = API0000_pa().queryAccountList(magicX, interface_ip, changeId, partitionIndi, policyId, payMode, serviceCode)
            #获取所需响应值
            is_success = response['isSuccess']
            if is_success:
                message = ''
                accountId = response['resultData'][0]['accountId']
            else:
                message = response['message']
                accountId = ''
            assert is_success == True

            """6.保全录入-复效提交接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_保全录入-复效提交接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            applyTime = applyTime + " 00:00:00"  #组装申请日期applyTime
            #是否免息复效
            if scsRevivalInterestFree_flag == 0:
                scsRevivalInterestFree = {}
            elif scsRevivalInterestFree_flag == 1:
                scsRevivalInterestFree = {"interestFreeReason":"1","feeBearWay":"1","feeBearDept":"1"}
            #是否免息复效
            if changeDetailModel_flag == 0:
                changeDetailModel = {"abnormalTold":"0"}
            elif changeDetailModel_flag == 1:
                changeDetailModel = {"abnormalTold":"1"}
            
            #调用原子脚本
            response = API0000_pa().entryConfirm_revival(magicX, interface_ip, changeId, applyNo, partitionIndi, policyId, policyNo, subSalesChannel, applyTime, serviceCode, csProductCals, scsRevivalInterestFree, changeDetailModel, payMode, accountId, customerInfoList)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
                operNote = response['others']['csChangeOperRecord']['operNote']   #流转的节点
            else:
                message = response['message']
                operNote = ''
            assert is_success == True
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全录入_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))


            cursor1 = API0000_diy().db_conf(env_name, 'wift_cs') 
            sql1 = "SELECT b.change_status FROM t_cs_application a,t_cs_change b WHERE a.apply_id=b.apply_id AND apply_no='" + str(applyNo) + "'"
            unit = '系统-保全复效_保全录入-客户受理信息接口_数据库查询客户证件止期'
            cursor1.execute(sql1)
            result1 = cursor1.fetchall()
            """人工核保"""
            if str(result1[0][0]) == '20':
                begin_time1 = datetime.datetime.now()   #开始时间
                #记录日志
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全核保_开始(预计耗时:20s)'))

                """7.保全核保-查询接口"""
                #节点初始化
                is_success = ''
                unit = '系统-核保_保全查询接口'  # 节点
                message = ''        
                #调用原子脚本
                response = API0000_uw().uwPolicyQuery_pa(magicX, interface_ip, policyNo) 
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

                """8.核保-保全任务领取接口"""
                #节点初始化
                is_success = ''
                unit = '系统-核保_保全任务领取接口'  # 节点
                message = ''        
                #调用原子脚本
                response = API0000_uw().uwLock_pa(magicX, interface_ip, mainId) 
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                else:
                    message = response['message']
                #断言
                assert is_success == True

                """9.核保_获取保单信息接口"""
                #节点初始化
                is_success = ''
                unit = '系统-核保_获取保单信息接口'  # 节点
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
                
                num = 0
                lenght = len(uwProducts)   # 获取险种个数
                for a in range(0, lenght):
                    """10.查询产品承保核保决定接口"""
                    #节点初始化
                    is_success = ''
                    unit = '系统-核保_查询产品承保核保决定接口'  # 节点
                    message = ''
                    #dict获取数据+定义数据
                    productId = uwProducts[a]['productId'] 
                    response = API0000_uw().queryLastProductUnderwriting(magicX, interface_ip, policyNo, productId)
                    #获取所需响应值
                    is_success = response['success']
                    if is_success:
                        message = ''
                        uwItemIdProp = response['others']['lastUwProduct']['uwItemId']
                        propUwId = response['others']['lastUwProduct']['uwId']
                    else:
                        message = response['message']
                        uwItemIdProp = ''
                        propUwId = ''
                    #断言
                    assert is_success == True

                    """11.核保_险种层提交核保决定接口"""
                    #节点初始化
                    is_success = ''
                    unit = '系统-核保_险种层提交核保决定接口'  # 节点
                    message = ''
                    #dict获取数据+定义数据
                    uwDecision = '01'  # 核保决定 01-核保通过
                    decisionComment = 'pass'  # 核保决定描述
                    uwItemId = uwProducts[a]['uwItemId']
                    #调用原子脚本
                    response = API0000_uw().updateUwDecision_pa(magicX, interface_ip, uwItemId, uwId, uwDecision, decisionComment, uwItemIdProp)
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

                """12.核保-保单保全结论判定接口"""
                #节点初始化
                is_success = ''
                unit = '系统-核保_保单保全结论判定-保存接口'  # 节点
                message = ''
                decisionCode = '01'        
                #调用原子脚本
                response = API0000_uw().savePolicyDecision(magicX, interface_ip, mainId, uwId, decisionCode, propUwId, serviceCode) 
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                else:
                    message = response['message']
                #断言
                assert is_success == True

                """12.核保-保单保全结论判定接口"""
                #节点初始化
                is_success = ''
                unit = '系统-保单保全结论判定层-保单核保特别说明接口'  # 节点
                message = ''
                #调用原子脚本
                response = API0000_uw().commitUWComment_pa1(magicX, interface_ip, mainId, uwId, policyId) 
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                else:
                    message = response['message']
                #断言
                assert is_success == True

                """13.核保-保全核保结论提交接口"""
                #节点初始化
                is_success = ''
                unit = '系统-核保_保全核保结论提交接口'  # 节点
                message = ''
                decisionCode = '1'        
                #调用原子脚本
                response = API0000_uw().saveBusiDecision(magicX, interface_ip, mainId, decisionCode, serviceCode) 
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                else:
                    message = response['message']
                #断言
                assert is_success == True

                """14.保全核保层-保单核保特别说明接口"""
                #节点初始化
                is_success = ''
                unit = '系统-保全核保层-保单核保特别说明接口'  # 节点
                message = ''
                #调用原子脚本
                response = API0000_uw().commitUWComment_pa2(magicX, interface_ip, mainId) 
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                else:
                    message = response['message']
                #断言
                assert is_success == True

                """15.保全核保提交接口"""
                #节点初始化
                is_success = ''
                unit = '系统-保全核保提交接口'  # 节点
                message = ''
                #调用原子脚本
                response = API0000_uw().commitUwComplete_uwComplete(magicX, interface_ip, mainId) 
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                else:
                    message = response['message']
                #断言
                assert is_success == True

                """16.保全核保解锁接口"""
                #节点初始化
                is_success = ''
                unit = '系统-保全核保解锁接口'  # 节点
                message = ''
                #调用原子脚本
                response = API0000_uw().uwUnLock(magicX, interface_ip, mainId) 
                #获取所需响应值
                is_success = response['success']
                if is_success:
                    message = ''
                else:
                    message = response['message']
                #断言
                assert is_success == True
                end_time1 = datetime.datetime.now()   #结束时间
                #记录日志
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全核保_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time1, end_time1)))


            """7.保全录入-登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_保全录入/核保-登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX,interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            #存入dict
            dict['public']['magicX'] = ''
            dict['logInfo']['code'] = '1'   #记录无异常标识
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全录入_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return csProductCals, dict


    @func_set_timeout(60)#设定函数超执行时间
    def pa_review(self, apply_date, dict):
        """step2:保全复核+保全收费（转进账单）:
                1.保全复核用户登录系统
                2.保全复核-保全公共工作池查询接口 
                3.保全复核-工作池领取任务接口
                4.保全复核提交接口
                
                保全收费（进账单）:
                5.柜面收付费查询接口
                6.柜面收付费保存接口
                7.柜面收付费审核接口
                8.登出系统 
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #初始化
            payment = 0
            magicX = ''
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全复核_开始(预计耗时:10s)'))
            #dict获取数据+定义数据
            """1.保全复核用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_保全复核用户登录系统'  # 节点
            message = ''
            payment = 0
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
            dict['public']['magicX'] = magicX
            assert is_success == True

            """2.保全复核-保全公共工作池查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_保全复核-保全公共工作池查询接口'  # 节点
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
            unit = '系统-保全复效_保全复核-工作池领取任务接口'  # 节点
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
            assert is_success == True

            """4.保全复核提交接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_保全复核提交接口'  # 节点
            message = ''
            #调用原子脚本
            response = API0000_pa().csEffect(magicX, interface_ip, changeId, applyNo, serviceCode, partitionIndi, policyNo)
            #获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            assert is_success == True

            # 加入断言
            assert is_success == True
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全复核_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))


            """保全收付费"""
            begin_time2 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全收付费_开始(预计耗时:20s)'))
            """1.BCP支付方式查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全贷款_BCP支付方式查询接口'  # 节点
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
            unit = '系统-保全贷款_BCP支付方式变更转进账单接口'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_payment().doChange2Cash1(magicX, interface_ip, offsetSumId)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            assert is_success == True

            """3.柜面收付费查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_柜面收付费查询接口'  # 节点
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

            """4.柜面收付费保存接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_柜面收付费保存接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            bankEndorse = '123123'  # 银行凭证号码
            feeConfirmDate = apply_date   #收费日期
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

            """5.柜面收付费审核接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_柜面收付费审核接口'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_payment().finishFeeFlow(magicX, interface_ip, resultData, bankEndorse, feeConfirmDate, internalAccount, internalBankCode, feeChannel, internalBankName)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
    
            """6.保全复核-登出系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全复效_保全复核-登出系统'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX,interface_ip)
            #获取所需响应值
            magicX = ''
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            """
            #改变dict-保单、险种状态
            dict['policy_info']['policy_status'] = '01'   #保单状态
            dict['policy_info']['invalid_reason'] = ''   #失效原因
            for j in range(0, len(dict['policy_info']['main_risk_info'])):
                dict['policy_info']['main_risk_info'][j]['liability_state'] = '01'   #主险有效
            for j in range(0, len(dict['policy_info']['sub_risk_info'])):
                dict['policy_info']['sub_risk_info'][j]['liability_state'] = '01'   #附加险有效
            """
            dict['logInfo']['code'] = '1'   #记录无异常标识
            dict['public']['magicX'] = ''
            end_time2 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*保全收付费_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time2, end_time2)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return payment, dict


    @func_set_timeout(30)#设定函数超执行时间
    def save_check_info(self, apply_date, payment, csProductCals, dict):
        """step3:定义轨迹信息+检查点信息:
                1.定义轨迹信息
                2.定义检查点信息
        """
        try: 
            if dict['logInfo']['code'] == '1':
                """定义检查点信息"""
                product = []   #定义复效产品列表
                
                for i in range(0, len(csProductCals)):
                    #产品代码
                    productCode = str(csProductCals[i]['productCode'])
                    #欠缴保费金额
                    revivalAmount = float(csProductCals[i]['revivalAmount'])
                    #复效应收利息
                    if csProductCals[i]['revivalInterestAmount'] == None:
                        revivalInterestAmount = 0
                    else:
                        revivalInterestAmount = float(csProductCals[i]['revivalInterestAmount'])
                    #保单贷款本金
                    loanBalance = float(csProductCals[i]['loanBalance'])
                    #保单贷款利息
                    loanInterest = float(csProductCals[i]['loanInterest'])
                    #保单自垫本金
                    zidianAmount = float(csProductCals[i]['zidianAmount'])
                    #保单自垫利息
                    zidianInterestAmount = float(csProductCals[i]['zidianInterestAmount'])
                    #加费金额
                    extraPrem = float(csProductCals[i]['extraPrem'])
                    
                    #每个产品复效检查点追加到product退保产品列表中
                    product.append({'productCode':productCode, 'revivalAmount':revivalAmount, 'revivalInterestAmount':revivalInterestAmount, 'loanBalance':loanBalance, 'loanInterest':loanInterest, 'zidianAmount':zidianAmount, 'zidianInterestAmount':zidianInterestAmount, 'extraPrem':extraPrem}) 
                #存入dict检查点中
                calc_revival = {'apply_date':apply_date, 'product':product, 'payment':payment, 'msg': ''}   
                dict['check']['calc_revival'].append(calc_revival) 
                #定义轨迹信息
                track_info = {'trackType':'revival', 'trackTime':apply_date, 'trackData':{'product':product, 'payment':payment}, 'msg':''}
                dict['track_info'].append(track_info)   #存入轨迹信息
            else:
                message = dict['logInfo']['msg']
                err = dict['logInfo']['err']
                if dict['logInfo']['msg'] == None or dict['logInfo']['msg'] == '':
                    message = str(dict['logInfo']['err'])
                #定义轨迹信息
                track_info = {'trackType':'revival', 'trackTime':apply_date, 'trackData':{'product':'', 'payment':payment}, 'msg': message}
                dict['track_info'].append(track_info)   #存入轨迹信息   
                #存入dict检查点中
                calc_revival = {'apply_date':apply_date, 'product':'', 'payment':payment, 'msg': message}   
                dict['check']['calc_revival'].append(calc_revival) 
        except Exception, e:
            dict['logInfo']['code'] = '0'    #记录异常标识
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        finally:
            pass
        return dict




if __name__ == "__main__":  
    try:
        begin_time = datetime.datetime.now()   #开始时间
        #1.初始化
        msg = ''   #执行python脚本前存在的错误信息
        job = 'revival'   #场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        scsRevivalInterestFree_flag = 0   #是否免息复效。 0-否；1-是
        changeDetailModel_flag = 0   #是否有异常告知。 0-否；1-是
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'
            env_name = '预生产'
            env_name = env_name.encode('utf-8')
            policyNo = '8088622045176868'
            apply_date = '2021-07-05'   #保全申请日期
            #scsRevivalInterestFree_flag = 0   #是否免息复效。 0-否；1-是
            #changeDetailModel_flag = 0   #是否有异常告知。 0-否；1-是
            username_entry = 'xcy1'   #保全录入用户名
            username_review = 'xcy2'    #保全复核用户名
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo = ''
                apply_date = ''   #保全申请日期
                #scsRevivalInterestFree_flag = ''   #是否免息复效。 0-否；1-是
                #changeDetailModel_flag = ''   #是否有异常告知。 0-否；1-是
                username_entry = ''   #保全录入用户名
                username_review = ''    #保全复核用户名
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                #key_list1 = ['env_name','policyNo','apply_date','scsRevivalInterestFree_flag','changeDetailModel_flag','username_entry','username_review']
                key_list1 = ['env_name','policyNo','apply_date','username_entry','username_review']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo = rs[2][1]   #保单号
                apply_date = rs[2][2]   #保全申请日期
                #scsRevivalInterestFree_flag = rs[2][3]   #是否免息复效。 0-否；1-是
                #changeDetailModel_flag = rs[2][4]   #是否有异常告知。 0-否；1-是
                #username_entry = rs[2][5]   #保全录入用户名
                #username_review = rs[2][6]    #保全复核用户名
                username_entry = rs[2][3]   #保全录入用户名
                username_review = rs[2][4]    #保全复核用户名
       #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name, 'apply_date':apply_date}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = {'execNo': execNo, 'policy_info':{'policyNo':policyNo},'public': {'env_name':env_name, 'username_entry': username_entry, 'username_review': username_review, 'interface_ip': interface_ip}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'','job':job}, 'track_info': [], 'check':{"calc_revival":[]}, 'track_change':[]}
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
            dict = sys_API0002().Modify_servertime(apply_date, job, dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常
            dict = sys_API0018().revival(apply_date, scsRevivalInterestFree_flag, changeDetailModel_flag, dict)
            assert dict['logInfo']['code'] == '1'
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:   #windows系统平台
                if dict['logInfo']['code'] == '1':
                    print '是否保单复效成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('保全申请日期：' + apply_date).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '是否保单复效成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('保单号：' + dict['policy_info']['policyNo']).decode('utf-8').encode('gb2312')
                    print ('保全申请日期：' + apply_date).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "是否保单复效成功：成功,,环境：%s,,保单号：%s,,申请日期：%s,,耗时：%s" % (env_name, dict['policy_info']['policyNo'], apply_date, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "是否保单复效成功：不成功,,不成功原因：%s,,环境：%s,,保单号：%s,,申请日期：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, dict['policy_info']['policyNo'], apply_date, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str

            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())








