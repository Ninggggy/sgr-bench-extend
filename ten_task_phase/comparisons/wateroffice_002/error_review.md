# 旧 Water Office 对照错因复核

本组为预先选定的旧题比较，6 个有效试次全部保留。CG Item-F1 三次均为 13/16，均值 13/16；GO 为 2/9、1、1/5，均值 64/135。它们不影响新题的绝对收录条件。

## 原答案与地理排序冲突

三个 CG 都输出 08EE001 → 08EE005 → 08EE004 → 08EE003，其状态和 KEEP/REJECT 字段与旧答案全部相同，只有三行序号被扣分。[官方 Station Reference Index](https://wateroffice.ec.gc.ca/station_metadata/reference_index_e.html?stnIndex=3491) 给出 Hazelton、Smithers、Quick、Houston 的纬度分别为 55°15′32″、54°46′11″、54°37′06″、54°23′57″N，汇水面积分别为 12,100、8,900、7,340、2,320 平方公里。结合题面指定河段，CG 输出符合下游到上游次序。原答案却将 Quick 放在 Hazelton、Smithers 之前，与该要求冲突。这三次扣分不能归因为求解者地理推理错误。原 oracle、题面、评分均未修改。

## CG/GO 必要条件不一致

CG 要求先取 Historical Results 看似覆盖 1948/1950 且带 Flow 标签的候选，并明确 final_verdict 的 KEEP/REJECT 映射。GO 未保留此前置候选条件及明确的 verdict 映射。GO1、GO3 纳入 Hubert (08EE002)，并把状态用作 verdict；其低分混有范围和输出语义差异，不能作为领域困难证据。GO2 得到原答案满分仍完整保留；该分数并不消除上述地理冲突。

## 答案暴露与解释限制

六份事件记录的针对性公开仓库/答案字段检索未命中（targeted_events_inspection.json）；这不是未接触公开答案的证明。未静默删除高分，也未重跑本组。本复核解释保留的原始确定性成绩，不生成替代旧题分数。首次控制端 urllib 补存网页遇本地 CA 查找失败，requests 不在该 Python 环境；随后使用系统 curl 的正常证书验证补存，没有关闭 TLS 校验。
