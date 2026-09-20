# WQP数据能力和读取隔离

实际最终配置：Codex CLI 0.153.4，gpt-6-astra/high，原生live web及wqp_data.download/read_text/query_csv；shell/apps/子代理禁用，Codex read-only沙箱；干净Docker镜像、无宿主mount/socket、只读根、cap-drop=ALL、no-new-privileges，临时home/work。仅公开输入/阶段提示/schema、最小配置/认证复制，控制端gold/rules不复制。

新增工具解决完整CSV不能靠网页摘要读取及本地连接/聚合的问题。只允许WQP/EPA官方HTTPS；GET完整响应在50MB内保存；ZIP解压也受同一容量限制。只读分页及SQLite查询只能使用本会话登记的opaque file_id。禁止路径读取、SQL ATTACH、扩展、任意Python/shell及宿主地址。实际容器程序检查：完整2行CSV计数2、求和3；private_read、attach、extension、host_url均被拒绝。没有安装依赖，复用本机现有Python/Node/CLI镜像运行时。

capability_run_01：最初MCP工具漏只读annotation，当前never审批策略拒绝调用；控制端停止，无真实完成事件、无能力评分；记录完整保留。补readOnlyHint=true/destructiveHint=false，符合这些工具不写外部来源的实际性质，没有设置强制approve或关闭审批。

capability_run_02：真实下载1978 TCEQMAIN-10580的Activity/Result及narrowResult，SQL全量复核18/290条、18/14个组织活动复合键，结果键无孤儿。原始CSV、请求、SQL、结果、session、actual_model和isolation均保存。这个切片只测试工具，不是新题oracle或旧题难度运行。

narrowResult实际可用，包含ResultIdentifier；仅称narrow并不代表该参数正确。完整2019新切片仍须独立查来源和能力记录，工具限制/源站失败不计为推理难度。

官方配置依据：https://learn.chatgpt.com/docs/extend/mcp?surface=cli 和 https://learn.chatgpt.com/docs/config-file/config-reference （2026-09-08读取）；当前CLI实际strict-config及日志为执行依据。

## 运行观察补充：原生本地计算
2026-09-08T13:35:35.233457+00:00。原生functions.exec除了编排工具，也允许在返回的数据上运行JavaScript及store/load（没有直接文件系统/网络）；所有r01/r02/r03及后续新旧对照均有此同一能力。r03 A-CG实际用它枚举全部撤回，再以SQL核验。不能把最终工具环境只描述成web+SQL，或称未开放本地计算。归档方式修复、输入清单记录和新增cohort成员集合评分均不改变这项模型能力。
