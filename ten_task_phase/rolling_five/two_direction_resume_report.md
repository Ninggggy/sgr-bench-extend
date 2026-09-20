# ChEMBL构造与IANA优化：当前交付记录

记录时间：2026-09-12T18:33:15.353937+00:00。本次两项均未形成可测的新定稿，原五题目标仍为0/5。没有新开发、攻击或正式测试，没有合格底题可导出，不把失败或缺失记作零分。

## ChEMBL

完整结构查询的16条记录、普通/边界预检查、两次构造各自重新取证及原始会话均保留。两次实际模型均核验为gpt-6-astra/high。

第一次构造持续连接空闲超时；唯一一次同输入/同配置替代又遇连接空闲超时和连接重置。第二次结束前明确检查容器内完整结果文件不存在；回收后同样无完整答案、题面或参考程序。构造侧曾报告“准备交付”，不能代替实际产物。总控按持续传输故障结束了两次会话，未把一次观察超时当作终止依据。

现有repair_retries_allowed=1已用尽，不再为同一槽换标签、换输入或开第三次调用。这里触发的是该构造槽的基础设施重试限制，**并非已证实账号额度耗尽**；最近额度观察仍有剩余。可恢复材料见[构造停止记录](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/chembl_stereochemical_peers_001/construction_stop.json)、[完整原始范围与预检](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/chembl_stereochemical_peers_001/controller_preflight.json)，失败原件位于runs/chembl-structure-builder-01与02。

## IANA

按一个明确历史身份缺口作有界取证：5次web工具调用、8个请求项，服务实际底层HTTP数未知。取得官方-08草案与最终RFC的认证输入差异、-13变更记录所标记的-09变化；不能据此断言-08就是分配53的规范，-09完整正文覆盖也未闭合。

不要求53只能对应唯一单一版本；有官方支持、定义明确的版本集合或过渡边界也可以。但当前缺少53与该版本/集合/过渡的直接官方关系，不能以任意历史公式对照替代注册身份和兼容性的原研究需求。没有创建r04，累计实质修订仍为1/2，剩余1次。详见[原件跟进报告](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/iana_followup.md)和[原件摘录](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/iana_followup_evidence.json)。

## 已知成本与恢复边界

下表覆盖两个ChEMBL构造尝试（其中第一次发生在本次恢复前）及新IANA取证工作单；不能称作仅本次恢复的净成本。

|工作单|会话秒数|已知输入token|其中缓存输入|已知输出token|完整性|
|---|---|---|---|---|---|
|chembl-structure-builder-01|2122.114|1,318,967|1,189,120|9,205|失败；仅回收部分usage，尾部未知|
|chembl-structure-builder-02|1787.845|1,598,848|1,532,544|8,308|失败；仅回收部分usage，尾部未知|
|IANA历史原件跟进|293.103|1,775,168|1,718,272|8,037|有界取证完成，尚不足改题|

缓存输入是输入的子集。失败会话的run.json没有完整usage，但原始trace恢复了上表部分计数；不能记成全未知或零消耗，未回传尾部仍未知。两次ChEMBL会话时长之和3909.959秒，不是实际经过时间。总控、复核、探索、等待与其他历史成本继续计入原账本。

截至2026-09-12T18:32:14.783408+00:00，本轮账本已知累计输入181,188,022、其中缓存172,782,976、输出1,133,684；这是整个滚动阶段的已记录消耗，不能换算为周额度。货币费用未知，当前总控尾部仍未完全报告。[完整账本汇总](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/run_accounting.json)保留逐工作单来源。

后续未开始的验证预留已释放，历史失败试次未抵扣任何未来新题。原七题/14次满分及复核报告不覆盖、不重复抽样。恢复这两个具体方向需要可用的完整构造产物或合法允许的构造恢复路径，以及IANA缺失的官方身份关系；不能宣称已有新题完成或两面低于70%。
