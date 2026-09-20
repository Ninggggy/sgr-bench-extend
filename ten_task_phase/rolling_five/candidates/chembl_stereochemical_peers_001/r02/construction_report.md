# ChEMBL r02：第一次实质来源修复已集成

r02 使用已通过独立审查的 CG/GO 草稿，通过资源类型、真实第 37 版及 2026 年 5 月发行月份支持自然来源发现。公共身份词和表头改为中性 REGISTERED_ID；原 16 条注册身份、标签、顺序和全部化学条件不变。两面与审查草稿完全一致，CG 原三步及字段术语均保留。本次实质修订累计 1/2；r01 和历史报告、分数、成本、原件完整保留。

reference.py 唯一改动是生成中性表头。当前 status/name/prefix/status 读取父目录 resumption_pretest_refresh 的 9 月 13 日 03:15:28–03:15:37 UTC 四份 HTTP 200 原件；原十份材料继续支持独立 connectivity、名称、默认页、schema 和重复观察核验。没有重复联网，也没有无必要复制旧执行输出。完整证据引用见 source_manifest.json 和 reference_report.md。

参考执行与单独公共规则重算均得到 16 行（8 FULL、7 PARTIAL、1 UNSPECIFIED），和 r01 数据行逐字相同。现有 stage_results.validate 已核对完整 candidate schema；候选公开元数据、全部配对条件、当前来源及路径检查通过。原评分器与当前协议评分器逐字一致，七项普通与边界文本夹具通过，CLI 自比三项指标为 1；这些只是评分兼容检查，不是模型得分。prepare --check-files 的最终结果记录在 execution_checks.json。

candidate 状态保留 reference_ready。来源修复的独立开发前审查已经通过，但本次构造不充当开发后最终质量审计、人工验证或难度测试；bulk/外部捷径和未来来源稳定性仍按已有范围保留未知。没有启动模型测试，也没有修改全局清单或账本。下一步由总控登记 Sol/medium CG/GO A。
