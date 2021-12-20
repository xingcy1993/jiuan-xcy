-- 查询表名
SELECT
	a.TABLE_COMMENT,
	a.TABLE_NAME
FROM
	information_schema. TABLES a
WHERE
	a.TABLE_SCHEMA = 'dbexpert'
  and TABLE_COMMENT like '%业务交易%' 
ORDER BY
	a.TABLE_NAME;


-- 主题域  exp_subject表
-- code业务主题域编号；cn_name业务主题域；en_name业务主题域英文代码;descript业务主题域描述;version版本号
select * from exp_subject



-- 根要素  exp_factor_root
select * from exp_factor_root


-- 要素   exp_factor_busi
select * from exp_factor_busi


-- 对象  exp_object   
select * from exp_object


-- 公式  exp_formula_define公式定义表   exp_formula_param公式参数定义表   exp_formula_body公式体定义表
select * from exp_formula_define
select * from exp_formula_param
select * from exp_formula_body


-- 规则  exp_rule_define规则定义表   exp_rule_param规则参数定义表   exp_rule_body规则体定义表
select * from exp_rule_define
select * from exp_rule_param
select * from exp_rule_body


-- 具象交易  exp_trans_define具象交易定义表   
select * from exp_trans_define

-- 交易  exp_trans_group交易定义表   exp_trans_group_member交易成员表
select * from exp_trans_group
select * from exp_trans_group_member


-- 事件  exp_event_define事件定义表   exp_event_layout事件布局表   exp_event_result事件定义结果表
select * from exp_event_define
select * from exp_event_layout
select * from exp_event_result



-- 流程   exp_flow_define流程定义表   exp_flow_layout流程布局表
select * from exp_flow_define
select * from exp_flow_layout






