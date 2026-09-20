# 评分规则（首次模型调用前确定）

唯一 gold 来源：正式 constraint.jsonl 中恰好一条 arxiv_001；不使用历史得分或作答。公式依据 chinese_1st_ver/latex/sections/Appendix.tex 第 3–39 行。9 字段，包括 ID。保留旧参考原文，不验证或改写事实。

按无版本后缀的 arXiv ID 对齐。只规范化 Unicode NFKC、首尾/连续空白、Markdown 强调/代码/链接外壳、ID 的 arXiv URL/前缀/版本后缀、出版线索的 DOI 前缀。不改日期事实、大小写、会场名称，不添加语义别名。因此本实现明确是**暂定严格评分**，不是完整 reviewer-defined semantic canonicalization。非严格相等的可能语义等价在报告单列，不给未验证奖励。

支持原生竖线、Markdown 表格、TSV、带表头 CSV。缺少字面表头记问题，不把可解析内容直接判零。缺字段保留空槽并记错，每行至少按 schema 的 9 槽计分母；额外列也计分母、整行不得分。重复 ID 第一行参与匹配和顺序评分，所有重复行计分母但零额外奖励，绝不依据 gold 选更好行。空答案/NONE 为零行；非空但无法解析为表则标 parse_failure，不冒充真实空答案，不产生指标。忽略的非表格文本逐行保存。

Item-F1 = 2Citem/(Ngold+Npred)，Row-F1 = 2Crow/(Rgold+Rpred)，P.O.A. = 相对顺序正确共同 ID 对数/共同 ID 对数。少于两个共同 ID 时为 0；不排序预测。所有计数、遗漏/额外/重复 ID、逐字段差异及每一顺序对都保存。

test_score.py 只使用人工 3×3 样例；完全正确 (1,1,1)、逆序 (1,1,0)、漏行 (.8,.8,1)、错一非 ID 字段 (8/9,2/3,1)、空答案 (0,0,0)，另外检查 Markdown、重复 ID（包括首行错误、后行正确）、缺字段、额外 ID、单个共同 ID、版本后缀、解析失败。
