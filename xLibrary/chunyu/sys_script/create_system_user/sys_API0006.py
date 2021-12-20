#coding=utf-8

import sys
import time
import json
import urllib
import logging
import datetime
import requests
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys);
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *



"""
1.登录系统
2.雇员管理：新增雇员+用户管理
3.系统管理：用户权限分配
4.进账单权限配置
5.登出用户
"""
class sys_API0006:

    def __init__(self):
        pass
    
    @func_set_timeout(30)#设定函数超执行时间    
    def create_system_user(self, dict):
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('系统新增用户+进账单权限配置开始(预计耗时:5s)'))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            #1.登录系统
            dict = sys_API0006().login_tool(dict)
            assert dict['logInfo']['code'] == '1'
            #2.校验新建的登录用户名是否存在 
            dict = sys_API0006().check_user_name(dict)
            assert dict['logInfo']['code'] == '1'
            #3.雇员管理接口
            dict = sys_API0006().employee_save_tool(dict)
            assert dict['logInfo']['code'] == '1'
            #4.雇员管理_自查询接口
            dict = sys_API0006().employee_query_tool(dict)
            assert dict['logInfo']['code'] == '1'
            #5.雇员管理_用户管理接口
            dict = sys_API0006().employee_userManage_tool(dict)
            assert dict['logInfo']['code'] == '1'
            #6.用户权限管理-查询接口 
            dict = sys_API0006().userManage_queryUser_tool(dict)
            assert dict['logInfo']['code'] == '1'
            #7.用户权限管理-获取可选角色列表
            dict = sys_API0006().userManage_getRoleList_tool(dict)
            assert dict['logInfo']['code'] == '1'
            #8.用户权限管理-分配权限
            dict = sys_API0006().userManage_saveRoles_tool(dict)
            assert dict['logInfo']['code'] == '1'
            #9.进账单权限配置
            dict = sys_API0006().addCashLimitCfg_tool(dict)
            assert dict['logInfo']['code'] == '1'
            #10.登出系统
            dict = sys_API0006().logout_tool(dict)
            #断言
            assert dict['logInfo']['code'] == '1'
            end_time = datetime.datetime.now()   #结束时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('系统新增用户+进账单权限配置结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            if dict['public']['magicX'] != '':
                API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
                logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
                dict['public']['magicX'] = ''
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置:\n')  + traceback.format_exc())
        finally:
            pass
        return dict


    # 登录系统
    def login_tool(self, dict):
        #记录日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统开始'))
        #初始化
        magicX = ''    #初始化会话id
        unit = '登录系统'  # 节点标识
        is_success = ''    #初始化是否成功标识
        message = ''    #初始化信息
        dict['logInfo']['code'] = '0'   #初始化异常标识
        try:
            # dict取值+定义数据
            env_name = dict['public']['env_name']   #环境名称
            username_entry = dict['public']['username_entry']   #登录用户名
            interface_ip = dict['public']['interface_ip']    #系统ip
            # 调用原子化脚本
            rs = API0000_sys_otherapi().login(env_name, username_entry, interface_ip)
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            #断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'    #记录无异常标识
            dict['public']['magicX'] = magicX    #记录会话id
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统结束'))
        return dict



    # 登出系统
    def logout_tool(self, dict):
        try:
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登出系统开始'))
            #初始化
            unit = '登出系统'  # 节点标识
            is_success = ''    #初始化是否成功标识
            message = ''    #初始化信息
            # dict取值+定义数据
            magicX = dict['public']['magicX']
            interface_ip = dict['public']['interface_ip']
            # 调用原子化脚本
            rs = API0000_sys_otherapi().logout(magicX, interface_ip)
            is_success = rs[0]
            message = rs[1] 
            # 加入断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'    #记录无异常标识   
            magicX = ''   #退出后初始化会话id
            dict['public']['magicX'] = ''
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登出系统结束'))
        return dict


    # 校验新建的登录用户名是否存在 
    def check_user_name(self, dict):
        try:
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*校验新建的登录用户名，数据库中是否已经存在_开始'))
            #初始化
            unit = '校验新建的登录用户名是否存在'  # 节点标识
            is_success = ''    #初始化是否成功标识
            message = ''    #初始化信息
            # dict取值+定义数据
            magicX = dict['public']['magicX']
            userName = dict['public']['employee_save']['name']   # 雇员姓名

            #初始化
            is_success = ''
            message = ''
            unit = '连接数据库'
            try:
                #调用原子脚本
                cursor = API0000_diy().db_conf(env_name,'wift_iiws')   #连接数据库
            except:
                is_success = False
                message = '数据库未连接成功，请检查数据库用户名/密码是否正确！'
            else:
                is_success = True
                message = ''
            #断言
            assert is_success == True
            unit = '校验新建的登录用户名是否存在'  # 节点标识

            sql = 'select * from t_user where user_name=' + "'" + userName + "'"
            cursor.execute(sql)
            result = cursor.fetchall()
            if len(result) > 0:
                is_success = False
                message = '数据库查询，欲新建的登录用户名已存在！'
            else:
                is_success = True
                message = ''
 
            # 加入断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'    #记录无异常标识   
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*校验新建的登录用户名，数据库中是否已经存在_结束'))
        return dict



    #雇员管理接口
    def employee_save_tool(self, dict):
        try:
            #记录
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*新增系统用户开始'))
            #初始化
            unit = '雇员管理接口'  # 节点
            is_success = ''   #初始化是否成功标识
            message = ''    #初始化信息
            dict['logInfo']['code'] = '0'    #初始化异常标识
            # dict取值+定义数据
            magicX = dict['public']['magicX']
            interface_ip = dict['public']['interface_ip']
            employeeCode = dict['public']['employee_save']['employeeCode']    # 雇员代码
            gender = dict['public']['employee_save']['gender']   # 雇员性别        
            certiType = dict['public']['employee_save']['certiType']   # 证件类型
            organId = dict['public']['employee_save']['organId']   # 所属机构
            underwritingMark = dict['public']['employee_save']['underwritingMark']   # 首席核保标志
            status = dict['public']['employee_save']['status']   # 状态        
            realName = dict['public']['employee_save']['realName']   # 雇员姓名
            birthday = dict['public']['employee_save']['birthday']   # 雇员生日
            certiCode = dict['public']['employee_save']['certiCode']   # 证件号码        
            title = dict['public']['employee_save']['title']   # 雇员职称
            education = dict['public']['employee_save']['education']   # 教育背景
            if 'win' in sys.platform:
                realName = urllib.quote(realName)
            else:
                realName = urllib.quote(realName.encode('utf-8'))
            # 调用原子化脚本
            rs = API0000_sys_otherapi().employee_save( magicX, interface_ip, employeeCode, gender, certiType, organId, underwritingMark, status, realName, birthday, certiCode, title, education)   
            is_success = rs[0]
            message = rs[1] 
            # 加入断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'    #记录无异常标识
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



    #雇员管理_自查询接口
    def employee_query_tool(self, dict):
        try:
            #初始化
            unit = '雇员管理_自查询接口'  # 节点
            is_success = ''
            message = ''
            dict['logInfo']['code'] = '0'
            # dict取值+定义数据
            magicX = dict['public']['magicX']
            interface_ip = dict['public']['interface_ip']
            employeeCode = dict['public']['employee_save']['employeeCode']    # 雇员代码 
            realName = dict['public']['employee_save']['realName']   # 雇员姓名
            if 'win' in sys.platform:
                realName = urllib.quote(realName)
            else:
                realName = urllib.quote(realName.encode('utf-8'))
            # 调用原子化脚本
            response = API0000_sys_otherapi().employee_query(magicX, interface_ip, realName, employeeCode)  
            # 返回是否成功，以及错误信息
            is_success = response['isSuccess']
            resultData = response['resultData']   #获取查询结果集，遍历结果集获取对应的employeeId
            if is_success:
                message = ''
                for i in range(0,len(resultData)):
                    if response['resultData'][i]['employeeCode'].encode('unicode-escape').decode('string_escape') == employeeCode:
                        employeeId = response['resultData'][i]['employeeId']    #获取employeeId
                    else:
                        employeeId = None
                    # 存入dict
                    dict['public']['employee_save']['employeeId'] = employeeId
            else:
                message = response['message']
            # 加入断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'    #记录无异常标识
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



    #雇员管理_用户管理接口
    def employee_userManage_tool(self, dict):
        try:
            #初始化
            unit = '雇员管理_用户管理接口'  # 节点
            is_success = ''
            message = ''
            dict['logInfo']['code'] = '0'
            # dict取值+定义数据
            magicX = dict['public']['magicX']
            interface_ip = dict['public']['interface_ip']
            employeeCode = dict['public']['employee_save']['employeeCode']    # 雇员代码
            gender = dict['public']['employee_save']['gender']   # 雇员性别        
            certiType = dict['public']['employee_save']['certiType']   # 证件类型
            organId = dict['public']['employee_save']['organId']   # 所属机构
            underwritingMark = dict['public']['employee_save']['underwritingMark']   # 首席核保标志
            status = dict['public']['employee_save']['status']   # 状态        
            userName = dict['public']['employee_save']['name']
            birthday = dict['public']['employee_save']['birthday']   # 雇员生日
            certiCode = dict['public']['employee_save']['certiCode']   # 证件号码        
            title = dict['public']['employee_save']['title']   # 雇员职称
            education = dict['public']['employee_save']['education']   # 教育背景
            
            userPassword = dict['public']['employee_save']['userPassword']   # 密码
            telephone = dict['public']['employee_save']['telephone']   # 电话        
            confirmPassword = dict['public']['employee_save']['confirmPassword']   # 密码确认
            userType = dict['public']['employee_save']['userType']   # 用户类型
            email = dict['public']['employee_save']['email']   # 邮箱  
            realName = dict['public']['employee_save']['realName']
            employeeId = dict['public']['employee_save']['employeeId']

            if 'win' in sys.platform:
                realName = urllib.quote(realName)
            else:
                realName = urllib.quote(realName.encode('utf-8'))

            # 调用原子化脚本
            rs = API0000_sys_otherapi().employee_userManage(magicX, interface_ip, userName, userPassword, gender, telephone, realName, confirmPassword, userType, email, status, employeeId)   
            is_success = rs[0]
            message = rs[1] 
            # 加入断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'    #记录无异常标识
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



    #用户权限管理-查询接口 
    def userManage_queryUser_tool(self, dict):
        try:
            #初始化
            unit = '用户权限管理-查询接口'  # 节点
            is_success = ''
            message = ''
            dict['logInfo']['code'] = '0'
            # dict取值+定义数据
            magicX = dict['public']['magicX']
            interface_ip = dict['public']['interface_ip']
            userName = dict['public']['employee_save']['name']   # 雇员姓名

            # 调用原子化脚本
            rs = API0000_sys_otherapi().userManage_queryUser(magicX, interface_ip, name)   
            is_success = rs[0]
            message = rs[1] 
            # 存入dict
            dict['userId'] = str(rs[2])
            # 加入断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'    #记录无异常标识
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



    #用户权限管理-获取可选角色列表
    def userManage_getRoleList_tool(self, dict):
        try:
            #初始化
            unit = '用户权限管理-获取可选角色列表'  # 节点
            is_success = ''
            message = ''
            dict['logInfo']['code'] = '0'
            # dict取值+定义数据
            magicX = dict['public']['magicX']
            interface_ip = dict['public']['interface_ip']
            userId = dict['userId']
            # 调用原子化脚本
            rs = API0000_sys_otherapi().userManage_getRoleList(magicX, interface_ip, userId)   
            is_success = rs[0]
            message = rs[1] 
            # 存入dict
            dict['roleIds'] = rs[2]
            # 加入断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'    #记录无异常标识
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict



    #用户权限管理-分配权限
    def userManage_saveRoles_tool(self, dict):
        try:
            #初始化
            unit = '用户权限管理-分配权限'  # 节点
            is_success = ''
            message = ''
            dict['logInfo']['code'] = '0'
            # dict取值+定义数据
            magicX = dict['public']['magicX']
            interface_ip = dict['public']['interface_ip']
            userId = dict['userId']
            roleIds = dict['roleIds']
            # 调用原子化脚本
            rs = API0000_sys_otherapi().userManage_saveRoles(magicX, interface_ip, userId, roleIds)   
            is_success = rs[0]
            message = rs[1] 
            # 加入断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'    #记录无异常标识
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*新增系统用户结束'))
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict


    #进账单权限配置
    def addCashLimitCfg_tool(self, dict):
        try:
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*进账单权限配置开始'))
            #初始化
            unit = '进账单权限配置'  # 节点
            is_success = ''
            message = ''
            dict['logInfo']['code'] = '0'
            # dict取值+定义数据
            magicX = dict['public']['magicX']
            interface_ip = dict['public']['interface_ip']
            operatorId = dict['public']['employee_save']['name']   # 雇员姓名
            organId = '10000'
            maxAmount = '99999999'
            minAmount = '0'
            # 调用原子化脚本
            rs = API0000_sys_otherapi().addCashLimitCfg(magicX, interface_ip, organId, operatorId, maxAmount, minAmount)   
            is_success = rs[0]
            message = rs[1] 
            # 加入断言
            assert is_success == True
            #存入dict
            dict['logInfo']['code'] = '1'    #记录无异常标识
        except Exception, e:
            is_success = False
            dict['logInfo']['err'] = unit + ':' + str(e)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*进账单权限配置结束'))
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
            env_name = '预生产'   #环境名称
            env_name = env_name.encode('utf-8')
            employeeCode = 'test3642320'    # 新增雇员代码
            realName = '换不换'   #新增雇员姓名
            name = 'jjqq10'    #新增登录用户名
            gender = '0'     #新增雇员性别
            certiType = '10'   #新增雇员证件类型     
            birthday = '1978-09-09'    #新增雇员出生日期     
            certiCode = '3253253232'    #新增雇员证件号码     
            telephone = '15267890111'    #新增雇员手机号     
            email = '787624988@qq.com'    #新增雇员邮箱 
            userPassword = 'abc1234567'    #新增雇员密码
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''
                env_name = ''
                employeeCode = ''    # 新增雇员代码
                gender = ''     #新增雇员性别
                certiType = ''   #新增雇员证件类型     
                name = ''    #新增雇员姓名 
                realName = ''   #登录用户名    
                birthday = ''    #新增雇员出生日期     
                certiCode = ''    #新增雇员证件号码     
                telephone = ''    #新增雇员手机号     
                email = ''    #新增雇员邮箱 
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','employeeCode','gender','certiType','name','realName','birthday','certiCode','telephone','email']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                employeeCode = rs[2][1]    # 新增雇员代码
                gender = rs[2][2]     #新增雇员性别
                certiType = rs[2][3]   #新增雇员证件类型     
                name = rs[2][4]    #新增雇员姓名 
                realName = rs[2][5]    #登录用户名
                birthday = rs[2][6]    #新增雇员出生日期     
                certiCode = rs[2][7]    #新增雇员证件号码     
                telephone = rs[2][8]    #新增雇员手机号     
                email = rs[2][9]    #新增雇员邮箱 
        #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name,'sys_name':name,'telephone':telephone,'email':email}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #密码
        userPassword = 'abc123456'
        #系统ip
        interface_ip = API0000_diy().ip_conf(env_name)

        #4.定义dict
        if is_run == True:
            msg = ''
        dict = {'public':{'env_name':env_name,'interface_ip':interface_ip,'magicX':'','username_entry':'csu100','employee_save':{'employeeCode':employeeCode,'gender':gender,'certiType':certiType,'organId':'10000','underwritingMark':'1','status':'1','name':name,'realName':realName,'birthday':birthday,'certiCode':certiCode,'title':'1','education':'40','userPassword':userPassword,'telephone':telephone,'confirmPassword':'abc123456','userType':'1','email':email}},'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'', 'unit':''}}
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
            dict = sys_API0006().create_system_user(dict)
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
            dict['public']['magicX'] = ''
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出。'))
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:
                if dict['logInfo']['code'] == '1':
                    print '是否新增成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('新建雇员：（雇员代码：' + str(employeeCode) + '，雇员姓名：' + urllib.unquote(realName) + ')').decode('utf-8').encode('gb2312')
                    print ('新增登录用户名：' + name).decode('utf-8').encode('gb2312')
                    print ('新增用户密码：' + userPassword).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '是否新增成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "是否新增成功：成功,,环境：%s,,新建雇员：（雇员代码：%s，雇员姓名：%s）,,新增登录用户名：%s,,新增用户密码：%s(请及时重置密码),,耗时：%s" % (env_name, str(employeeCode), urllib.unquote(realName), name, userPassword, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "是否新增成功：不成功,,不成功原因：%s,,环境：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())