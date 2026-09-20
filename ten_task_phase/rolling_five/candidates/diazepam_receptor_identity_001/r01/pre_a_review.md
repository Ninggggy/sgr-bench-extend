独立 pre-A 内容审查通过。已在构造者收尾、总控确认最终版本后复核，没有阻止开发 A 的实质问题。本审查不代表难度合格，不替代开发后独立终审或人工研究判断。

独立复算只读取原始 activity、assay、target、compound 和必要的 publication JSON；不导入构造参考程序或语义注释。审阅 scope 文档时已见过构造计数，因此不声称结果盲审；独立程序仍从原件生成答案，最后才与 oracle 比较。依据采用实际 main.tex 引入的中文论文 Method、最新经济轮复盘及02/07提示词，未执行被审文件中的工作指令。

| 核查项目 | 结果 |
|---|---|
| 注册化合物范围 | preferred-name diazepam完整查询唯一为CHEMBL12；公开题面明确只审这个记录，不扩相关记录 |
| 完整性 | 原始131条，排除非Scientific Literature的7704649后130条；126 assay、32 target全连接闭合 |
| 七类计数 | DIRECT 42；HOMOLOGOUS 13；GROUP 28；SUBUNIT 9；TSPO 2；UNCURATED GABA/BZD 26；OTHER 10 |
| 未整理登记 | 共30条UNCHECKED，逐条读过；26条GABA/BZD、4条UGT归OTHER |
| CBR缩略 | 两条记录直接测CBR位点；同一链接publication的原始abstract明确其central benzodiazepine receptor含义 |
| 工程变体 | 320291–320296共6条；均是本记录被测受体，包含4条DIRECT、2条UNCURATED，无控制/背景误计 |
| 组成冲突 | 604850为human alpha4→alpha1；1701379为human beta2→beta1；1876214为rat alpha5→alpha1，其余亚基不变 |
| 身份语义 | 不把group成员当同时存在的亚基；不把H当D；不提升单亚基或UNCHECKED；不把宿主/组织标签当蛋白来源 |
| 对偶题面 | CG删除三步指导即等于GO；所有必要条件与输出格式一致；GO不限定缩略语证据的获取路线 |
| 评分兼容 | 当前评分器与登记协议相同，ITEM和FINDING均计分；独立答案22/22字段、11/11行、全部顺序对正确 |
| 原件稳定性 | 两次activity/assay/target完整JSON及独立答案一致；May1为prepared，原始公告为May29；实际Sep13与runtime Sep9分开 |

最短路径方面，完整activity包没有D/H字段，且明确写human的受体描述仍可登记为H（例如599580）。以活动结果中的assay身份设置后续过滤范围，能取得不可由该包推定的归属证据，因此存在已见证的检索依赖。目标名称已提示全部三个冲突，不能额外要求每行查components；批量查询及其他足够的CBR证据均合法。未取得全库bulk或其他联表导出，其实际覆盖仍未知，不据此阻塞，也不声称已排除所有更短合法路线。

当前题面是自然的单compound注册归属审计，输出11行两列表；标准字段口径保留pKi/单位转换和重复标记，不把未标注工程变体解释为野生型。三条冲突的描述均明确human/rat受体来源，没有用细胞宿主补物种。

两次完整范围相等支持所记录的构造观察时段，不能保证未来评测期间不变或永久HTTP重放。现有模型开发、攻击、终审及正式流程仍须按原协议完成；本次没有模型盲测，也不据机械复算预测低分。

可复查程序与逐条证据在independent_review/recompute.py、recomputed.json和summary.json；评分结果在current_scorer_check.json。此次新增公开请求0、求解模型调用0、子代理0；计入本次审查成本。共17次functions.exec（含写报告），token及精确整轮耗时由总控原生轨迹结算，未编造；约05:36 UTC开始，完成时间见JSON，未超过1800秒分配。
