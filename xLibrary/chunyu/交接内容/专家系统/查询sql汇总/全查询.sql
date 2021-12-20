#全查询
SELECT
	a.cn_name 流程,
  c.cn_name 事件,
  e.cn_name 交易,
  g.cn_name 具象交易,
  i.cn_name 规则
FROM
	exp_flow_define a,   #流程定义表
	exp_flow_layout b,   #流程布局表
  exp_event_define c,   #事件定义表
  exp_event_layout d,   #事件布局表
  exp_trans_group e,   #交易组定义表
  exp_trans_group_member f,   #交易组成员表
  exp_trans_define g,   #具象交易定义表
  exp_trans_layout h,   #具象交易布局表
  exp_rule_define i   #规则定义表
WHERE
	a.id = b.master_flow_id
AND b.event_id = c.id
AND b.node_type = '2'
AND c.id = d.event_id
AND d.node_type = '8'
AND d.trans_id = e.id
AND e.id = f.group_id
AND f.trans_id = g.id
AND g.id = h.trans_id
AND h.ref_rule_id = i.id
AND a.code = 'checkdata_tool1'




