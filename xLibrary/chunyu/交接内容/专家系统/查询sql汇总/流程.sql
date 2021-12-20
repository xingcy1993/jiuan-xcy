###流程   exp_flow_define流程定义表   exp_flow_layout流程布局表
#subject_id业务主题域id

select * from exp_flow_define
select * from exp_flow_layout

#exp_flow_define流程定义表
select * from exp_flow_define where code = 'checkdata_tool1' and cn_name = '测试任务受理工具'


select * from exp_flow_layout where master_flow_id = '2021090114132333910' 


select * from exp_flow_layout where master_flow_id = '2021090114132333910' and node_type='2'

 



