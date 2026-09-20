# 错误、运行与来源分项审查

|尝试|归类|具体问题|
|---|---|---|
|[screening_new_CG_1](runs/r-a55562d61d59/run.json)|cohort_completeness_reasoning|区间层统一覆盖判断错误，误排除真实共同区间，48行中仅3行正确。|
|[screening_old_CG_1](runs/r-6c876269dbe4/run.json)|匹配原oracle|原始最终答案完整匹配原oracle。|
|[screening_new_GO_1](runs/r-8224e9cc365a/run.json)|numeric_text_sort|状态、身份和计数正确；溶解氧按TEXT排序，12行选错活动。|
|[screening_old_GO_1](runs/r-24202450d4ad/run.json)|匹配原oracle|原始最终答案完整匹配原oracle。|
|[confirmation_new_CG_1](runs/r-0ee77dc62ed5/run.json)|匹配原oracle|原始最终答案完整匹配原oracle。|
|[confirmation_old_CG_1](runs/r-b90e2f062f85/run.json)|匹配原oracle|原始最终答案完整匹配原oracle。|
|[confirmation_new_GO_1](runs/r-69914a9877c8/run.json)|numeric_text_sort|输出与筛选GO逐字一致；SQL使用ORDER BY c.do，导入列为TEXT。|
|[confirmation_old_GO_1](runs/r-d04075b89074/run.json)|匹配原oracle|原始最终答案完整匹配原oracle。|
|[confirmation_new_CG_2](runs/r-92c02e2f6067/run.json)|numeric_text_sort, output_transcription|保存的状态计算正确；数值排序错误，且最终抄录损坏3个行身份键。消除抄录错误仍不能整行答对。|
|[confirmation_old_CG_2](runs/r-4a02a31cb8e8/run.json)|匹配原oracle|原始最终答案完整匹配原oracle。|
|[confirmation_new_GO_2](runs/r-4df368e8ea7e/run.json)|numeric_text_sort|输出与筛选GO逐字一致；SQL直接排序导入的溶解氧TEXT列。|
|[confirmation_old_GO_2](runs/r-d936d9895abf/run.json)|匹配原oracle|原始最终答案完整匹配原oracle。|
|[confirmation_new_CG_3](runs/r-e5e848752431/run.json)|匹配原oracle|原始最终答案完整匹配原oracle。|
|[confirmation_old_CG_3](runs/r-551a85fda485/run.json)|匹配原oracle|原始最终答案完整匹配原oracle。|
|[confirmation_new_GO_3](runs/r-426fcaec1732/run.json)|output_completeness, parse_failure|计算表216字段全部正确，最终CSV仅12列，丢弃6个必需字段。原评分为NA，不能作为状态推理失败或补零。|
|[confirmation_old_GO_3](runs/r-683967eda07e/run.json)|匹配原oracle|原始最终答案完整匹配原oracle。|

数值排序错误来自模型没有按现有工具说明显式转换TEXT列，不是新增工具限制或改评分制造的错误。CG2另有抄录问题；GO3有实际字段遗漏，原指标为NA，诊断不替换正式成绩。四次旧题完整答案暴露另见[暴露检查](public_exposure_findings.md)。

完整分类、暂时访问失败计数、解析细节、逐字段链接见[error_analysis.json](error_analysis.json)；原始工具失败原文见[tool_health.json](tool_health.json)。
