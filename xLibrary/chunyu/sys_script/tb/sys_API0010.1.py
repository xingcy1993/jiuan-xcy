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



"""批量退保:
       step1:保全录入:
            1.保全录入用户登录系统
            2.保全申请接口
            3.保全录入-客户受理信息接口
            4.保全录入-产品信息详细
            5.保全录入-支付方式及支付账户接口
            6.保全录入-退保提交接口
            7.登出系统
       step2:保全复核:
            1.保全复核用户登录系统
            2.保全复核-保全公共工作池查询接口 
            3.保全复核-工作池领取任务接口
            4.保全复核提交接口

            保全收费（转进账单）:
            step5: BCP支付方式查询接口
            step6: BCP支付方式变更转进账单接口
            7.柜面收付费查询接口
            8.柜面收付费保存接口
            9.柜面收付费审核接口
            10.登出系统
       step3:定义轨迹信息+检查点信息:
             1.定义轨迹信息
             2.定义检查点信息
"""
class sys_API0010_1:

    def __init__(self):
        pass


    @func_set_timeout(300)#设定函数超执行时间
    def tb(self, apply_date, dict):
        """系统退保:
               step1:保全录入
               step2:保全复核+保全收费（转进账单）
               step3:定义轨迹信息+检查点信息:
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            space_times = 0   #日志打印空格次数
            job = dict['logInfo']['job']
            if job[0:14] == 'complex_scenes':   #复杂场景
                space_times = 2
            else:
                space_times = 0
            dict['public']['space_times'] = space_times
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '退保_开始(预计耗时:60s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            policyNo_list = dict['public']['policyNo_list']   #保单号列表
            policyNo_list = policyNo_list.split(',')
            thread_result_list = []
            magicX1 = ''
            magicX2 = ''

            """step1:验证用户是否可正常登录系统"""
            #节点初始化
            is_success = ''
            message = ''
            unit = "验证录入用户是否可正常登录系统"   #节点
            #验证保全录入用户是否可正常登录系统
            rs = API0000_diy().verify_userlogin(env_name, username_entry, interface_ip)
            is_success = rs[0]
            message = rs[1]
            #验证保全复核用户是否可正常登录系统
            rs = API0000_diy().verify_userlogin(env_name, username_review, interface_ip)
            is_success = rs[0]
            message = rs[1]
            assert is_success == True


            """step2:判断是否需要修改服务器时间"""
            dict = sys_API0002().Modify_servertime(apply_date, dict['logInfo']['job'], dict)
            assert dict['logInfo']['code'] == '1'   #断言是否异常

            """step3:登录系统-保全录入用户、复核与用户"""
            dict = self.login(dict)
            magicX1 = dict['public']['magicX1']   #录入用户会话id
            magicX2 = dict['public']['magicX2']   #复核用户会话id


            #创建线程
            threads = []
            for i in range(0, len(policyNo_list)):
                threads.append(self.myThread("Thread-" + str(i+1), apply_date, policyNo_list[i], dict))

            for t in threads:
                t.setDaemon(True)
                t.start()

            #join()方法，用于等待线程终止
            for t in threads:
                t.join()
                thread_result_list.append(t.get_result())

            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登出系统-保全录入用户、复核用户_开始'))
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登出系统-保全录入用户、复核用户_结束'))
            end_time = datetime.datetime.now()   #结束时间

            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '退保_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['code'] = '0'
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '异常位置:\n')  + traceback.format_exc())
        except func_timeout.exceptions.FunctionTimedOut:
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
            #记录执行时间超时日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '&nbsp&nbsp&nbsp*执行时间超时退出'))
        finally:
            #登出系统
            if magicX1 != '':
                API0000_sys_otherapi().deblocking(magicX1, API0000_diy().ip_conf(env_name), username_entry)
            if magicX2 != '':
                API0000_sys_otherapi().deblocking(magicX2, API0000_diy().ip_conf(env_name), username_review)
            #
            if thread_result_list == []:
                pass
            else:
                dict = {}
        return thread_result_list, magicX1, magicX2, dict



    """登录系统-保全录入用户、复核与用户"""
    @func_set_timeout(120)#设定函数超执行时间
    def login(self, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统-保全录入用户、复核用户_开始(预计耗时:5s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            magicX1 = ''
            magicX2 = ''
            """step1:登录系统-保全录入用户"""
            #节点初始化
            is_success = ''   #是否成功标识
            unit = '节点：系统-保全录入_登录系统'  # 节点标识
            message = ''   #信息标识
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username1 = dict['public']['username_entry']    #保全录入用户
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username1, interface_ip)
            #获取所需响应值
            is_success = rs[0]   #是否成功标识
            message = rs[1]   #信息
            magicX1 = rs[2]   #会话id
            #断言
            assert is_success == True
            dict['public']['magicX1'] = magicX1

            """step3:登录系统-保全复核用户"""
            username2 = dict['public']['username_review']    #保全复核用户
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
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统-保全录入用户、复核与用户_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
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
        def __init__(self, name, apply_date, policyNo, dict):
            threading.Thread.__init__(self)
            self.thread_name = name
            self.apply_date = apply_date
            self.policyNo = policyNo
            self.dict = dict

     
        def run(self):     #把要执行的代码写到run函数里面，线程在创建后会直接运行run函数 
            dict = self.dict
            dict = copy.deepcopy(dict)
            thread_name = self.thread_name
            policyNo = self.policyNo
            apply_date = self.apply_date
            try:
                #保全录入
                resultData = []
                print 1
                rs = sys_API0010_1().pa_entry(apply_date, policyNo, dict, thread_name)  
                resultData = rs[0]
                dict = rs[1]
                assert dict['logInfo']['code'] == '1'   #断言是否异常
                #保全复核+收付费
                payment = 0
                print 2
                rs = sys_API0010_1().pa_review(apply_date, policyNo, dict, thread_name) 
                payment = rs[0]
                dict = rs[1]
                print 3
                assert dict['logInfo']['code'] == '1'   #断言是否异常
            except Exception, e:
                dict['logInfo']['code'] = '0'   #dict['logInfo']['code']记录异常标识
                #记录异常日志
                logging.warning(API0000_diy().text_conversion('异常位置:\n') + traceback.format_exc())
            finally:
                self.result = {'code':dict['logInfo']['code'],'msg':dict['logInfo']['msg'],'policyNo':policyNo}

        #获取线程结果函数
        def get_result(self):
            try:
                return self.result # 如果子线程不使用join方法，此处可能会报没有self.result的错误
            except Exception:
                return None
            return dict




    @func_set_timeout(120)#设定函数超执行时间
    def pa_entry(self, apply_date, policyNo, dict, thread_name):
        """step1:保全录入
                1.保全录入用户登录系统
                2.保全申请接口
                3.保全录入-客户受理信息接口
                4.保全录入-产品信息详细
                5.保全录入-支付方式及支付账户接口
                6.保全录入-退保提交接口
                7.登出系统
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*' + thread_name + ':保全录入_开始(预计耗时:30s)'))
            """1.保全录入用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全退保_录入用户登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username = dict['public']['username_entry']    #保全录入用户 
            magicX = dict['public']['magicX1']

            """2.保全申请接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全退保_保全申请接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            applyTime = apply_date   #保全申请日期
            applyWay = '3'    #保全申请来源
            applyType = '1'    #保全申请方式
            serviceCode = '30300'  #保全申请项目编号
            policyCodes = ''
            customerId = ''
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
            # 加入断言
            assert is_success == True 

            """3.保全录入-客户受理信息接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全退保_保全录入-客户受理信息接口'  # 节点
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
            unit = '系统-保全退保_保全录入-客户受理信息接口_连接数据库'
            cursor = API0000_diy().db_conf(env_name, 'wift_prop') 
            policyId = others['policyId']
            contactNumber = others['mobile']   #保全电话
            telephone = others['officeTel']   #固定电话
            customerInfoList_old = others['customerInfoList']
            customerInfoList_new = [] 
            for i in range(0,len(customerInfoList_old)):
                if customerInfoList_old[i]['customerRole'] == '01':
                    customerInfoList_new.append({})
                    customerId = str(customerInfoList_old[i]['customerId'])
                    name = customerInfoList_old[i]['name']
                    certiType = customerInfoList_old[i]['certiType']
                    birthday = customerInfoList_old[i]['birthday'] 
                        #执行sql
                    sql = "select CERTI_VALID_END_DATE from t_prop_customer where name='" + name + "' and GLOBAL_CUST_ID='" + customerId + "' ORDER BY update_time desc"
                    unit = '系统-保全退保_保全录入-客户受理信息接口_数据库查询客户证件止期'
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
            # 加入断言
            assert is_success == True 
            
            """4.保全录入-产品信息详细"""
           #节点初始化
            is_success = ''
            unit = '系统-保全退保_保全录入-产品信息详细'  # 节点
            message = ''
            #dict获取数据+定义数据
            tb_dict = []   #tb_dict。存入产品的退保数据信息   
            #调用原子脚本
            response = API0000_pa().queryCsPolicyProductBeforeChange(magicX, interface_ip, policyNo, changeId, partitionIndi, serviceCode) 
            #获取所需响应值
            is_success = response['isSuccess']
                #定义退保列表。并存入产品id、产品现价、产品退保限额；
            if is_success:
                message = ''
                resultData = response['resultData']
            else:
                message = response['message']
                resultData = ''
                #组装定义tb_dict产品的退保数据信息 
            for i in range(0,len(resultData)):
                tb_dict.append({})
                tb_dict[i]['productId'] = str(resultData[i]['productId'])   #产品id
                tb_dict[i]['presentPrice'] = str(resultData[i]['presentPrice'])   #产品现价
            # 加入断言
            assert is_success == True 

            """5.保全录入-支付方式及支付账户接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全退保_保全录入-支付方式及支付账户接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            payMode = '01'   #保全收付费方式:01-银行转账
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
            # 加入断言
            assert is_success == True 

            """6.保全录入-退保提交接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全退保_保全录入-退保提交接口'  # 节点
            message = ''
            #dict获取数据+定义数据
            applyTime = applyTime + " 00:00:00"  #组装申请日期applyTime
            flag = True
            csProductCals = resultData
            #调用原子脚本
            response = API0000_pa().entryConfirm_tb(magicX, interface_ip, changeId, applyNo, partitionIndi, policyId, policyNo, subSalesChannel, applyTime, serviceCode, contactNumber, telephone, flag, csProductCals, payMode, accountId, customerInfoList)
            # 获取所需响应值
            is_success = response['success']
            if is_success:
                message = ''
            else:
                message = response['message']
            # 加入断言
            assert is_success == True 

            #存入dict
            dict['logInfo']['code'] = '1'   #记录无异常标识
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*' + thread_name + ':保全录入_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return resultData, dict


    @func_set_timeout(60)#设定函数超执行时间
    def pa_review(self, apply_date, policyNo, dict, thread_name):
        """step2:保全复核+保全收费（转进账单）
                1.保全复核用户登录系统
                2.保全复核-保全公共工作池查询接口 
                3.保全复核-工作池领取任务接口
                4.保全复核提交接口

                保全收费（转进账单）:
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
            space_times = dict['public']['space_times'] + 1   #日志打印空格次数
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*' + thread_name + ':保全复核_开始(预计耗时:10s)'))
            """1.保全复核用户登录系统"""
            #节点初始化
            is_success = ''
            unit = '系统-保全退保_保全复核用户登录系统'  # 节点
            message = ''
            #dict获取数据+定义数据
            env_name = dict['public']['env_name']   #环境名称
            interface_ip = dict['public']['interface_ip']   #接口ip
            username = dict['public']['username_review']    #保全复核用户
            magicX = dict['public']['magicX2']           

            """2.保全复核-保全公共工作池查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全退保_保全复核-保全公共工作池查询接口'  # 节点
            message = ''
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
            unit = '系统-保全退保_保全复核-工作池领取任务接口'  # 节点
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
            unit = '系统-保全退保_保全复核提交接口'  # 节点
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
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*' + thread_name + ':保全复核_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time1, end_time1)))


            """保全收付费"""
            begin_time2 = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*' + thread_name + ':保全收付费_开始(预计耗时:20s)'))
            """1.BCP支付方式查询接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全退保_BCP支付方式查询接口'  # 节点
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
            unit = '系统-保全退保_柜面收付费查询接口'  # 节点
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
            unit = '系统-保全退保_柜面收付费保存接口'  # 节点
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

            """5.柜面收付费审核接口"""
            #节点初始化
            is_success = ''
            unit = '系统-保全退保_柜面收付费审核接口'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_payment().finishFeeFlow(magicX, interface_ip, resultData, bankEndorse, feeConfirmDate, internalAccount, internalBankCode, feeChannel, internalBankName)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            # 加入断言
            assert is_success == True 

            end_time2 = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*space_times + '*' + thread_name + ':保全收付费_结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time2, end_time2)))
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            if message == '':
                message = str(e)
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
        job = 'tb'   #场景名
        magicX1 = ''
        magicX2 = ''
        thread_result_list = []
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = '预生产'
            env_name = env_name.encode('utf-8')
            policyNo_list = '8088612111122268,8088612111122168,8088612111122468'
            apply_date = '2021-11-10'   #保全申请日期
            username_entry = 'xcy1'   #保全录入用户名
            username_review = 'xcy2'   #保全复核用户名
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                policyNo_list = ''
                apply_date = ''
                username_entry = ''
                username_review = ''
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','policyNo_list','apply_date','username_entry','username_review']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                policyNo_list = rs[2][1]   #保单号
                apply_date = rs[2][2]   #保全申请日期
                username_entry = rs[2][3]   #保全录入用户
                username_review = rs[2][4]   #保全复核用户
        #保单号列表去掉空格,中文逗号转换
        policyNo_list = policyNo_list.replace(' ', '')
        policyNo_list = policyNo_list.replace('，', ',')
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
        dict = {'execNo': execNo, 'policy_info':{'main_risk_info':[{'liability_state':''}], 'sub_risk_info':[{'liability_state':''}]},'public': {'env_name':env_name, 'policyNo_list':policyNo_list, 'username_entry':username_entry, 'username_review':username_review, 'interface_ip':interface_ip, 'magicX':''}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'', 'job':job}, 'track_info': [], 'check':{'calc_tb':[]}, 'track_change':[]}
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
            rs = sys_API0010_1().tb(apply_date, dict)
            thread_result_list = rs[0]
            magicX1 = rs[1]
            magicX2 = rs[2]
            dict = rs[3]
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
            end_time = datetime.datetime.now()   #记录结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:
                print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                print ('保全申请日期：' + apply_date).decode('utf-8').encode('gb2312')
                print ('保单号列表：' + policyNo_list).decode('utf-8').encode('gb2312')
                print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                print ('批量退保结果：').decode('utf-8').encode('gb2312')
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
                            run_msg = '，退保不成功原因：' + thread_result_list[j]['msg']
                        print (str(j+1) + '.保单号：' + thread_result_list[j]['policyNo'] + '，是否退保成功：' + run_result + run_msg).decode('utf-8').encode('gb2312')
            else:    #非windows系统平台
                result_str = "环境：%s,,保全申请日期：%s,,保单号列表：%s,,耗时：%s,,批量退保结果：" % (env_name, apply_date, policyNo_list, API0000_diy().logger_count_time(begin_time, end_time))
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
                            run_msg = '，退保不成功原因：' + thread_result_list[j]['msg']
                        result_str = result_str + ',,' + str(j+1) + '.保单号：' + thread_result_list[j]['policyNo'] + '，是否退保成功：' + run_result + run_msg
                if thread_result_list == []:
                    result_str = result_str + ',,不成功原因：' + dict['logInfo']['msg']
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())
