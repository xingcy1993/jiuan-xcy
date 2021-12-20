#coding=utf-8

import re
import sys
import time
import json
import logging
import traceback
import datetime
from func_timeout import func_set_timeout
import func_timeout
reload(sys)
sys.setdefaultencoding('utf8')
from xLibrary.chunyu.API0000 import *



"""修改服务器时间：
       step1：获取当期服务器时间
       step2：若当前时间与预修改时间不相同，修改服务器时间
              若当前时间与预修改时间相同，不修改服务器时间
"""
class sys_API0002:

    def __init__(self):
        pass

    @func_set_timeout(120)#设定函数超执行时间 
    def Modify_servertime(self, to_modify_datetime, job, dict):
        """修改服务器时间：
               step1：获取当期服务器时间
               step2：若当前时间与预修改时间不相同，修改服务器时间
                      若当前时间与预修改时间相同，不修改服务器时间
        """
        try:
            begin_time = datetime.datetime.now()   #开始时间
            #打印附加内容
            node = ''
            #日志打印&nbsp&nbsp&nbsp次数
            if dict['logInfo']['job'] == 'Modify_servertime':   #修复服务器时间组件
                times = 0
            elif dict['logInfo']['job'] == 'nb':   #新契约出单组件
                times = 1
            elif dict['logInfo']['job'] == 'clm':   #理赔
                times = 1
            elif dict['logInfo']['job'] in ('send_survivalFee','longriskexpiry_batck'):   #生存金派发组件、长期险满期终止批处理组件
                times = 1
            elif dict['logInfo']['job'] == 'single_invalidation_bacth':
                times = 1
                node = '到宽限期外'
            elif dict['logInfo']['job'] == 'bonus_send_batch':   #分红批处理组件
                times = 1
            elif dict['logInfo']['job'] == 'bonus_settlement_batch':   #分红结息批处理组件
                times = 1
            elif dict['logInfo']['job'] == 'renew':   #续期组件
                times = 3
            elif dict['logInfo']['job'] == 'renew_nofee':   #续期不收费
                times = 2
            elif dict['logInfo']['job'] == 'tb':   #退保
                times = 1
            elif dict['logInfo']['job'] == '1query_policy_loan_info':   #查询保单贷款信息数据
                times = 1
            elif dict['logInfo']['job'][0:14] == 'complex_scenes':   #复杂场景
                if dict['logInfo']['job'] == 'complex_scenes-renew':
                    times = 5
                elif dict['logInfo']['job'] == 'complex_scenes-single_invalidation_bacth':
                    times = 3
                    node = '到宽限期外'
                elif dict['logInfo']['job'] == 'complex_scenes-renew_nofee':
                    times = 4
                else:
                    times = 2
            else:
                times = 0
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*times + '*修改服务器时间%s_开始(预计耗时:60s)'%node))
            #初始化
            dict['logInfo']['code'] = '0'
            dict['logInfo']['msg'] = ''
            dict['logInfo']['err'] = ''
            dict['logInfo']['result'] = ''
            is_success = '' #初始化是否成功标识
            message = ''   #初始化信息
            unit = "系统-修改服务器时间"   #节点标识
            old_servicetime = ''   #修改前时间

            #去除两端空格
            to_modify_datetime = to_modify_datetime.strip()

            #冒号替换
            to_modify_datetime = to_modify_datetime.replace('：', ':')

            #正则表达式
            pattern = r'^\d{4}-\d{1,2}-\d{1,2}( \d{1,2}:\d{1,2})?$'   #正则表达式:YYYY-MM-DD hh:mm
            if re.match(pattern, to_modify_datetime) == None:    #匹配
                message = '录入日期格式有误！'
                is_success = False
            else:
                message = ''
                is_success = True
            assert is_success == True

            #分别获取YYYY-MM-DD和hh:mm进行判断
            list = to_modify_datetime.split(' ')
            #未录入hh:mm，补充00:00
            if len(list) == 1:
                time_value = '00:00'
            for i in range(0, len(list)):
                if i == 0:
                    list_date = list[0].split('-')
                    year = list_date[0]   #年
                    month = list_date[1]   #月
                    day = list_date[2]   #日
                    if int(year) < 1900 or int(year) > 2099:
                        message = '录入的年,超出范围！'
                        is_success = False
                    assert is_success == True

                    if month == '0' or month == '00' or (int(month) > 0 and int(month) < 13)==False:
                        message = '录入的月,超出范围！'
                        is_success = False
                    assert is_success == True

                    if day == '0' or day == '00' or (int(day) > 0 and int(day) < 32)==False:
                        message = '录入的日,超出范围！'
                        is_success = False
                    assert is_success == True

                    if len(month) == 1:
                        month = '0' + month
                    if len(day) == 1:
                        day = '0' + day
                    #组装YYYY-MM-DD
                    date_value = year + '-' + month + '-' + day
                    if API0000_diy().isvaild_date(date_value) == False:
                        message = '录入的日期不存在！'
                        is_success = False
                    assert is_success == True
                elif i == 1:
                    list_time = list[1].split(':')
                    hour = list_time[0]
                    minute = list_time[1]
                    if int(hour) < 0 or int(hour) > 23:
                        message = '录入的时,超出范围！'
                        is_success = False
                    assert is_success == True

                    if int(minute) < 0 or int(minute) > 60:
                        message = '录入的分,超出范围！'
                        is_success = False
                    assert is_success == True

                    if len(hour) == 1:
                        hour = '0' + hour
                    if len(minute) == 1:
                        minute = '0' + minute
                    time_value = hour + ':' + minute
            to_modify_datetime = date_value + ' ' + time_value

            #dict获取数据+定义数据
            env_name = dict['public']['env_name']
            """step1:获取当期服务器时间"""
            old_servicetime = API0000_diy().get_date(env_name)  # 获取当期服务器时间 并转换为正常格式：年-月-日
            #print 'old_servicetime:' + old_servicetime
            """step2：若当前时间与预修改时间不相同(YYYY-MM-DD hh)，修改服务器时间"""
            if (dict['logInfo']['job'] == 'Modify_servertime' and old_servicetime[0:13] != to_modify_datetime[0:13]) or (dict['logInfo']['job'] != 'Modify_servertime' and old_servicetime[0:10] != to_modify_datetime[0:10]): 
                is_Modify_flag = '是'   #是否修复服务器时间标识
                new_servicetime = API0000_diy().modify_date(to_modify_datetime , env_name)   # 修改成功后，获取当期服务器时间 并转换为正常格式：年-月-日
                #print 'new_servicetime:' + new_servicetime
                if new_servicetime[0:13] == to_modify_datetime[0:13]:
                    is_success = True
                    message = ''
                else:
                    is_success = False
                    message = '修改时间后，查询系统最新时间与欲修改的时间不一致'
            else:
                is_success = True 
                message = ''
                is_Modify_flag = '否'   #是否修复服务器时间标识
            # 加入断言
            assert is_success == True
            
            #存入dict
            dict['public']['old_servicetime'] = old_servicetime
            dict['public']['to_modify_datetime'] = to_modify_datetime
            dict['logInfo']['code'] = '1'   #记录无异常标识
            end_time = datetime.datetime.now()   #结束时间

            #记录轨迹信息
            if is_Modify_flag == '是':
                consume_time = API0000_diy().logger_count_time(begin_time, end_time)   #耗时   
            elif is_Modify_flag == '否':
                consume_time = '0秒'
            track_change = {'job':job, 'to_modify_datetime':to_modify_datetime, 'trackData':{'is_Modify_flag':is_Modify_flag, 'is_success_Modify':is_success, 'consume_time':consume_time}, 'msg': message}
            dict['track_change'].append(track_change)   #存入轨迹信息
            #记录日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*times + '*修改服务器时间%s_结束(实际耗时:%s)' % (node, API0000_diy().logger_count_time(begin_time, end_time))))
            time.sleep(10)
        except Exception, e:
            is_success = False
            dict['logInfo']['code'] = '0'    #记录异常标识
            dict['logInfo']['err'] = unit + ':' + str(e)
            dict['logInfo']['msg'] = '修改服务器时间不成功（请检查录入时间是否有误，或者是否环境不稳定）'
            #记录异常日志
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp'*times + '*异常位置:\n')  + traceback.format_exc())
        finally:
            # 加入阻断及错误信息。存入dict['result']中
            dict = API0000_diy().result(dict, is_success, message, unit)
        return dict


if __name__ == "__main__":
    #后台执行命令：python /data/xServer/xLibrary/chunyu/sys_script/Modify_servertime/sys_API0002.py 2021031681000000273 "{'env_name':'uat8','to_modify_datetime':'2022-12-28'}"
    try:
        begin_time = datetime.datetime.now()   #开始时间
        #1.初始化
        is_run = True   #是否执行python脚本 
        msg = ''   #执行python脚本前存在的错误信息
        job = 'Modify_servertime'   #修改时间的场景名
        #2.本地定义/服务端获取-脚本执行数据：(1)win系统（本地）:自定义数据(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
        if 'win' in sys.platform:   #(1)win系统（本地）
            execNo = 'test001'   #测试编号
            env_name = '预生产'   #环境类型
            env_name = env_name.encode('utf-8')
            to_modify_datetime = '2021-06-22 09:44'   #修改时间为 
        else:   #(2)服务器端:接收并校验参数数据（第一位为测试编号，第二位json串）
            if len(sys.argv) != 3:   #判读后台出参数量（3位：脚本路径+测试编号+json串）
                is_run = False
                msg = '后台传值数有误！'
                execNo = ''   #测试编号
                env_name = ''  #环境类型
                to_modify_datetime = ''   #修改时间为 
            elif len(sys.argv) == 3:
                execNo = sys.argv[1]   #测试编号
                input_dict = sys.argv[2]   #输入的json串
                input_dict = input_dict.replace("'", '"')   #json转dict，需要把‘单引号’转换为‘双引号’
                #后台传值json串中字段列表
                key_list1 = ['env_name','to_modify_datetime']
                #checkdata界面录入字段-后台传值json-脚本，字段是否存在及读取字段值。不存在时为''
                rs = API0000_diy().checkdata_json_check(input_dict,key_list1)
                is_run = rs[0] 
                msg = rs[1]
                env_name = rs[2][0]   #环境类型
                to_modify_datetime = rs[2][1]   #修改时间为 
        #3.校验录入字段是否符合规范
        key_dict = {'env_name':env_name}   #录入字段中待校验字典
        if msg == '':
            rs = API0000_diy().checkdata_json_check1(key_dict)
            is_run = rs[0]
            msg = rs[1]
        #4.定义dict
        if is_run == True:
            msg = ''
        dict = {'execNo': execNo, 'public': {'env_name':env_name, 'to_modify_datetime':to_modify_datetime}, 'logInfo': {'code':'0', 'msg':msg, 'err':'', 'result':'','job':job}, 'track_change':[]}
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
            dict = sys_API0002().Modify_servertime(to_modify_datetime, job, dict)
    except Exception, e:   #常见异常的捕捉
        dict['logInfo']['code'] = '0'
        #记录异常日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*异常位置:\n')  + traceback.format_exc())
    except func_timeout.exceptions.FunctionTimedOut:
        #记录执行时间超时日志
        logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*执行时间超时退出'))
        dict['logInfo']['code'] = '0'
        dict['logInfo']['msg'] = '执行时间超时退出。' + dict['logInfo']['msg']
    finally:
        try:
            end_time = datetime.datetime.now()   #结束时间
            #打印终端开始符
            print '\n\n' + '#'*3 + 'RESULT' + '#'*3
            if 'win' in sys.platform:
                if dict['logInfo']['code'] == '1':
                    print '是否修改成功：成功'.decode('utf-8').encode('gb2312')
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
                    print ('修改前时间为：' + dict['public']['old_servicetime']).decode('utf-8').encode('gb2312')
                    print ('修改后时间为：' + dict['public']['to_modify_datetime'] + ':00').decode('utf-8').encode('gb2312')
                    print ('耗时：' + API0000_diy().logger_count_time(begin_time, end_time)).decode('utf-8').encode('gbk')
                else:
                    print '不成功原因:'.decode('utf-8').encode('gb2312'),;API0000_diy().solve_terminal_garbled(dict['logInfo']['msg'])
                    print ('环境：' + env_name).decode('utf-8').encode('gb2312')
            else:
                if dict['logInfo']['code'] == '1':
                    result_str = "是否修改成功：成功,,环境：%s,,修改前时间为：%s,,修改后时间为：%s,,耗时：%s" % (env_name, dict['public']['old_servicetime'], str(to_modify_datetime),API0000_diy().logger_count_time(begin_time, end_time))
                else:
                    result_str = "是否修改成功：不成功,,不成功原因：%s,,修改时间为：%s,,环境：%s,,耗时：%s" % (dict['logInfo']['msg'], env_name, to_modify_datetime,API0000_diy().logger_count_time(begin_time, end_time))
                print result_str
            #打印终端结束符
            print '#'*3 + 'RESULT' + '#'*3
        except Exception, e:
            logging.warning(API0000_diy().text_conversion('&nbsp&nbsp&nbsp*组件结果展示部分脚本报错:\n')  + traceback.format_exc())
