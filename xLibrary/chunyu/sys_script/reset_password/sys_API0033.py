# coding=utf-8

import re
import sys
import time
import pymysql
import requests
import logging
import traceback
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
import hashlib
sys.setdefaultencoding("utf8")
from xLibrary.chunyu.API0000 import *



"""系统用户密码重置组件脚本:
       step1:登录系统
       step2:系统用户密码重置接口
       step3:登出系统
"""
class sys_API0033:
    def __init__(self):
        pass

    @func_set_timeout(10)#设定函数超执行时间
    def reset_password(self, dict):
        try:
            #初始化
            magicX = ''
            dict['logInfo']['code'] = '0'
            begin_time = datetime.datetime.now()   #开始时间
            #记录日志
            logging.warning(API0000_diy().text_conversion('系统用户密码重置开始(预计耗时:5s)'))
            #获取dict数据
            env_name = dict['public']['env_name']   #环境名
            interface_ip = dict['public']['interface_ip']   #环境ip
            username_entry = dict['public']['username_entry']   #待重置用户名
            old_password = dict['public']['old_password']   #原密码
            new_password = dict['public']['new_password']   #新密码

            """验证新密码格式是否正确"""
            pattern = r"^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,20}$"    #由数字和字母组成，并且要同时含有数字和字母，且长度要在8-20位之间
            if re.match(pattern, new_password) == None:    #匹配
                is_success = False
                message = '录入的密码格式有误！要求：由数字和字母组成，并且要同时含有数字和字母，且长度要在8-20位之间。'
            else:
                message = ''
                is_success = True
            assert is_success == True

            """step1:登录系统"""
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统开始'))
            #节点初始化
            is_success = ''
            unit = '节点:系统-系统用户密码重置_登录系统。'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().login(env_name, username_entry, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            magicX = rs[2]
            assert is_success == True
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登录系统结束'))

            """step3:系统用户密码重置查询接口"""
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*系统用户密码重置开始'))
            #节点初始化
            is_success = ''
            unit = '节点:系统-系统用户密码重置_系统用户密码重置查询接口。'  # 节点
            message = ''
            # 数据库查询原密码的md5格式
            cursor = API0000_diy().db_conf(env_name, 'wift_iiws')
            sql = 'select * from t_user where user_name=' + "'" + username_entry + "'"
            cursor.execute(sql)
            result = cursor.fetchall()
            customerId = str(result[0][0])
            old_password_md5 = str(result[0][2])
            #获取新密码md5
            m = hashlib.md5()
            m.update(new_password)
            new_password_md5 = m.hexdigest()
            print new_password_md5

            #调用原子脚本
            response = API0000_sys_otherapi().checkPassword(magicX, interface_ip, old_password_md5) 
            #获取所需响应值
            if response['success'] == True and response['others'] == True and response['message'] == '获取用户信息失败，请刷新页面':
                is_success = True
                message = ''
            else:
                is_success = False
                message = response['message'] 
            #断言
            assert is_success == True

            #调用原子脚本
            response = API0000_sys_otherapi().reset_password(magicX, interface_ip, old_password_md5, new_password_md5, customerId) 
            #获取所需响应值
            if response['success'] == True and response['message'] == '用户密码更新失败！':
                is_success = True
                message = ''
            else:
                is_success = False
                message = response['message'] 
            #断言
            assert is_success == True

            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*系统用户密码重置结束'))

            """登出系统"""
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登出系统开始'))
            #节点初始化
            is_success = ''
            unit = '节点:系统-系统用户密码重置_登出系统。'  # 节点
            message = ''
            #调用原子脚本
            rs = API0000_sys_otherapi().logout(magicX, interface_ip)
            #获取所需响应值
            is_success = rs[0]
            message = rs[1]
            assert is_success == True
            magicX = ''
            #定义轨迹信息
            track_info = {'trackType':'reset_password', 'trackTime':'', 'trackData':{'serviceCode':serviceCode}, 'msg': ''}
            dict['track_info'].append(track_info)   #存入轨迹信息
            end_time = datetime.datetime.now()   #结束时间
            #存入dict
            dict['logInfo']['code'] = '1'
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*登出系统结束'))
            logging.warning(API0000_diy().text_conversion('系统用户密码重置结束(实际耗时:%s)' % API0000_diy().logger_count_time(begin_time, end_time)))
        except Exception, e:
            dict['logInfo']['err'] = unit + str(e)
            dict['logInfo']['code'] = '0'
            #如果程序报错，且magicX不为空（已经登录），对用户进行解锁
            if magicX != '':
                username_entry = dict['public']['username_entry']    #新契约复核用户
                API0000_sys_otherapi().deblocking(magicX, interface_ip, username_entry)
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('异常位置-' + unit + ':\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)      
        return dict




if __name__ == "__main__":  
    try:
        begin_time = datetime.datetime.now()   #开始时间
        #1.自定义录入+初始化
        execNo = 'test001'   #测试编号
        env_name = '预生产'    #环境类型
        env_name = env_name.encode('utf-8')
        username_entry = 'xcy2'    #待重置密码用户
        old_password = 'abc123456'  #原密码
        new_password = 'abc1234567'   #新密码
        #2.接收参数：第一位为测试编号，第二位json串
        if len(sys.argv) == 2:
            execNo = sys.argv[1]   #测试编号     
        elif len(sys.argv) > 2:
            execNo = sys.argv[1]   #测试编号 
            input_dict = sys.argv[2]   #输入的json串
            input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
            input_dict = json.loads(input_dict)   #json转dict格式
            env_name = input_dict['env_name']    #环境
            username_entry = input_dict['username_entry']    #待重置密码用户
            old_password = input_dict['old_password']    #原密码
            new_password = input_dict['new_password']    #新密码
        interface_ip = API0000_diy().ip_conf(env_name)
        #3.定义dict
        dict = {'execNo': execNo, 'public': {'env_name':env_name, 'username_entry':username_entry, 'old_password':old_password, 'new_password':new_password, 'interface_ip':interface_ip}, 'logInfo': {'code':'0', 'msg':'', 'err':'', 'result':''}, 'track_info':[]}
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
        #5.执行脚本
        dict = sys_API0033().reset_password(dict)
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
    except func_timeout.exceptions.FunctionTimedOut:
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出&' + dict['logInfo']['msg']
        #异常场景-登出系统（防止与用户被挂起）
        if dict['public']['magicX'] != '':
            API0000_sys_otherapi().deblocking(dict['public']['magicX'], dict['public']['interface_ip'], dict['public']['username_entry'])
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*运行异常-用户解锁'))
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:   #windows系统平台
                if dict['logInfo']['code'] == '1':
                    print '系统用户密码重置是否成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('用户名：' + username_entry).decode('utf-8').encode('gb2312')
                    print ('新密码：' + new_password).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '系统用户密码重置是否成功：不成功'.decode('utf-8').encode('gb2312')
                    print '不成功原因：'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('用户名：' + username_entry).decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "系统用户密码重置是否成功：成功,,环境：%s,,用户名：%s,,新密码:%s,,耗时：%s" % (env_name, username_entry, new_password, API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "系统用户密码重置是否成功：不成功,,不成功原因：%s,,环境：%s,,用户名：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, username_entry, API0000_diy().logger_count_time(begin_time, end_time))
                print result_str

            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())

