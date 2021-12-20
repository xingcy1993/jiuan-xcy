
#查询流程下事件
SELECT
	a.cn_name 流程名称,
  c.cn_name 事件名称,
  c.code
FROM
	exp_flow_define a,   #流程定义表
	exp_flow_layout b,   #流程布局表
  exp_event_define c   #事件定义
WHERE
	a.id = b.master_flow_id
AND b.event_id = c.id
AND b.node_type = '2'
AND a.code = 'checkdata_tool1'



#查询事件下交易
SELECT
  c.cn_name 事件名称,
  e.cn_name 交易名称,
  e.code 交易编码
FROM
  exp_event_define c,   #事件定义表
  exp_event_layout d,   #事件布局表
  exp_trans_group e   #交易组定义表
WHERE
	c.id = d.event_id
AND d.node_type = '8'
AND d.trans_id = e.id
AND c.code = 'event_code2'


#交易下具象交易
SELECT
  e.cn_name 交易名称,
  g.cn_name 具象交易名称,
  g.code 具象交易编码
FROM
  exp_trans_group e,   #交易组定义表
  exp_trans_group_member f,   #交易组成员表
  exp_trans_define g   #具象交易定义表
WHERE
  e.id = f.group_id
AND f.trans_id = g.id
AND e.code = 'deal_code1'



#具象交易下规则
SELECT
  g.cn_name 具象交易名称,
  i.cn_name 规则名称,
  i.code 规则编码
FROM
  exp_trans_define g,   #具象交易定义表
  exp_trans_layout h,   #具象交易布局表
  exp_rule_define i   #规则定义表
WHERE
	g.id = h.trans_id
AND h.ref_rule_id = i.id
AND g.code = 'actual_deal_code3'
