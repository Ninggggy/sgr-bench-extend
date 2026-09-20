# economic_nvd_daily_001 / r01 完整参考与配对构造记录

结论：已从保存的官方原始响应构建完整参考与英文 CG/GO。现场 oracle 为 228 行，覆盖 35 个 CVE、143 个零覆盖 UUID。622 行纳排账本中 true=228、false=394、unknown=0。JavaScript 与独立 SQLite 路径逐行一致。阶段返回 inconclusive：本环境不能执行 Python、不能落盘或运行既有 scorer，也没有进行后续正式盲评期间的稳定性复核。这里不是另一次可行性检查；完整产物已包含在阶段文件包中。

## 时间、权限与交付

- 用户输入的协议 current_date=2026-09-09 保留；实际 environment_context 日期为 2026-09-11，未修改任何运行配置。
- 授权现场评估范围为 2026-09-11 至 2026-09-13 UTC。实际首个本轮数据请求 2026-09-11T18:34:59.391602+00:00，最后数据响应 2026-09-11T19:05:56.987019+00:00。修改索引核验截止 2026-09-11T19:05:53.000 UTC。没有声称取得 9 月 9 日历史证据，也没有重新施加历史重放要求。
- 实际执行 237 次下载：235 个公开 API 响应及 2 个官方文档资源；全部 HTTP 200。另通过 web.open 检查文档页，得到无正文的应用外壳。原始 d0001 仅从已有注册资产读取；不冒填其旧请求元数据。
- 工作区只读，没有 shell/Python 执行工具。所有路径是 CSV 阶段包中的真实文件条目，尚未写入工作区。包内保留完整响应文本、请求元数据、UTF-8 SHA-256 及旧原始 d0001；与下载工具报告的响应字节数全部一致。
- 没有启动代理、其他模型、盲解、盲攻击、评分、对外发送或发布。私有证据包不得进入盲环境。

## 范围、分页和身份

主日查询 sources/d0027.json 的 resultsPerPage=64、startIndex=0、totalResults=64，vulnerabilities 长度 64。查询日期参数为 2003-11-17T00:00:00.000 至 2003-11-17T23:59:59.999，resultsPerPage=2000。所有 published 均为 2003-11-17T05:00:00.000；日期指现行 published 字段，不是 2003 年历史快照。

64 个不同 CVE 中 59 个含配置。5 个 Rejected CVE 保留在 candidate_universe.jsonl 中，因没有配置而不产生 criterion 行。新的单 CVE 切片 sources/d0335.json 确认 CVE-2003-0964 属于该日、Rejected、无 configurations。

递归遍历每个 configuration 下所有容器与 cpeMatch，产生 622 个出现项、622 个不同 CVE–UUID 组合、381 个唯一 UUID。所有出现项 vulnerable=true。完整源文本中的 matchCriteriaId 键数也为 622。SQL 用 configurations/nodes/children 递归 CTE 独立遍历；序列上界 1023，实际源中最大数组长度 86。两条路径的全行集合一致，而不只比较计数。

59 个按 CVE 的 Match 查询均为一页，resultsPerPage 上限设为 500，最大实际返回 86。逐 CVE 的 UUID 集合与配置完全相等，没有遗漏、额外 UUID、重复批次身份或跨批次修订冲突。381 个 UUID 全部 Active。所有 criteria 与四种版本边界均一致。

重要修正：先前报告“版本边界全空”错误。旧 d0001 与本轮 d0027 内容相同，却均含 6 个带 versionEndIncluding 的配置出现项，涉及 fetchmail、两个不同命名空间的 mod_gzip、openslp、sun:jre 和 ibm:db2_universal_database。原始字段及准确行键见 reference/normalized_occurrences.jsonl 与 reference/independent_configurations.csv；本轮 SQL d0173 列出六行。未调整 oracle 迎合任何旧答案或成绩。

## 覆盖语义与决定性证据

初始日响应给出 CVE、UUID、criteria、vulnerable 和版本范围，不能证明 Match 状态或字典覆盖。已发现的 CVE ID 决定后续 by-CVE Match 参数；发现的 UUID 和 Match 返回状态再决定字典请求。state_graph.json 和 reference/request_plan.json 保存这一依赖及完整请求身份集。

官方页面 https://nvd.nist.gov/developers/products 返回外壳 sources/d0028.html。其真实加载脚本 sources/d0029.js 含文档正文：
- 字符偏移 1653069–1654490：CPE matchCriteriaId 参数返回与指定 UUID 关联的字典记录。
- 偏移 1671800–1673399：matches 是官方字典名称/ID 配对，cpeLastModified 记录这些值的更新时间。
- 偏移 1660100–1664200：Match 修改时间查询比较 lastModified 与 cpeLastModified 的较新者；相关字典名称新增、修改、弃用都会更新后者。
这些属于本次实际取得的官方描述，不是搜索摘要或模型记忆。原始脚本整体保留，可按偏移复查。

238 个唯一 UUID 的非空 matches 列表按上述官方语义排除“字典零覆盖”。再按 (CPE part, vendor, product) 分组、选每组最小的已覆盖 UUID，执行 28 个精确字典检查；全部 137 个返回名称与 ID 同 Match 列表完全一致。这是独立接口的分层核验，不声称对另外 210 个有覆盖 UUID 也执行了精确字典查询。

143 个 UUID 省略 matches，最初一律视作待核。已为全部 143 个取得成功的精确 matchCriteriaId 字典响应，均 totalResults=0、products=[]。没有把遗漏字段或 API 错误当作零，也没有添加 noDeprecated 过滤；deprecated 字典记录仍算有记录。每个纳入行都有自己的精确 UUID 零响应定位。相同 UUID 在不同 CVE 中保留不同结果行；重叠 criteria 不合并。

## 独立复算和现场稳定性

1. JavaScript 参考函数直接读取 source_manifest.json 指向的原始文件，递归抽取、验证分页/身份/版本边界、建立三值纳排和字段证据，输出排序后的 oracle。
2. SQLite 从原始 CVE CSV 的 JSON 字段进行独立递归，联合全部 59 个原始 Match 批次，再连接包含原始精确字典 JSON 的来源表 d0314。d0315 得到 228 行，与 JavaScript 三列顺序逐行完全一致。原始 SQL、全量中间 CSV、工具资产号和比较结果随包保存。
3. 新取得的宽日期查询 sources/d0333.json 覆盖 2003-11-16 至 2003-11-18，完整响应仍为 64 条，均属 11 月 17 日。SQLite 从该新响应重新抽取 622 行，与旧源全行 EXCEPT 双向比较：缺失 0、新增 0（d0341）。
4. sources/d0334.json 重新获取完整日范围，64 个 CVE 的整个记录与初始响应相等。sources/d0336.json 的完整修改索引在 18:34:32–19:05:53 UTC 返回 22 条、单页结束；与相关 381 个 UUID 的交集为空。JavaScript 与 SQL d0343 分别验证这一交集。相关 Match 的最新主响应修订时间为 2026-01-15T19:22:14.243，早于核验窗口。

这些检查覆盖本轮相关范围与字典关联修订，支持本轮构造期间稳定。它们不等于响应 timestamp 是数据版本、不保证不存在所有瞬时变化，也不认证本轮结束后的评估或整个 9 月 13 日未来状态。正式测试时必须再从公开来源复核完整相关范围和变化，不能用构造缓存补足盲环境。

## 已执行的反事实

reference/counterfactuals.json 由真实源计算，列出每个变化行与错误借用的覆盖身份：
- 把同 CVE、同其他 CPE 分量及版本边界的 wildcard update 覆盖误用于具体 update UUID：228 行变成 222 行，漏掉 6 行。
- 跨 CVE 全局按 UUID 去重：228 行变成 143 行，漏掉 85 行。
- 忽略 vulnerable 标志不改变本数据中的行。它是业务资格条件，但本轮不声称该标志带来有效难度。
不以请求数量、数组大小或这些反事实宣称盲测难度、模型能力或实验成绩。

## 实际执行命令与结果

以下是本轮真实工具操作的可复查形式；每个公开请求的完整 URL、参数、请求/接收时间、状态、响应文件和终止依据都在 source_manifest.json。

- mcp__wqp_data__download({url: <manifest 中逐条 URL>})：237 次均 HTTP 200。
- mcp__wqp_data__read_text({file_id, offset, limit:30000})：分页拼接完整保存文本；第一次尝试超大 limit 被工具截到 30000，随后改为完整分页。
- mcp__wqp_data__tabulate({file_id:"d0027",format:"json",json_path:["vulnerabilities"]})：d0089，64 行。
- mcp__wqp_data__query_csv({tables:{c:"d0089"},sql:<reference/extract_configurations.sql>})：d0101，622 行。
- 全部 59 个 Match 原始文件 tabulate 后 UNION：d0167，622 行。
- reference/join_match.sql：d0250，622 行；状态 Active=622，待精确覆盖确认=228。
- reference/oracle_independent.sql，以 j=d0250、d=d0314：d0315，228 行，与 JS 完全一致。
- functions.exec 中执行 solveReference(sourceFiles, sourceManifest)：实际运行两次；后一次含 28 个有覆盖字典检查，oracle 不变。源代码为 reference/solve_reference.js。
- functions.exec 中执行 checkStability(sourceFiles, sourceManifest)：64 个 CVE 相等、381 个相关 UUID、22 条修改记录、相关修改 0。源代码为 reference/check_stability.js。
- SQL 新切片双向集合比较 d0341：622、622、0、0；SQL 修改索引连接 d0343：22、0。
- 行键唯一 228，输出恰好三列、标识格式有效、没有空值或分隔符冲突，排序确定。
- SHA-256 实现通过空串及 abc 标准向量，并核对所有已知响应字节数，无差异。
- SQL json_tree 不可用，实际报错为 OperationalError: vtable constructor failed: json_tree，改用标量 JSON 与递归 CTE。CSV 重载将 NULL 转为空 TEXT；d0106/d0107 的初次范围统计无效，已以 NULLIF 修正为 d0171/d0173。没有把这两个中间结果当作事实。

未执行的控制器命令（不是成功日志）：

```bash
python3 reference/verify_controller.py --stage <materialized-stage> --run <new-run-directory>
```

该脚本实际调用 reference/solve_reference.py，从原始 JSON 重建 JSONL/PSV，验证原始 JSON 的 SHA-256、范围和修订覆盖，再与本包的实际 JS/SQL 结果逐字段比较，保存真正的 stdout、stderr 和比较状态。现阶段没有 Python 退出码或测试成功记录。使用新运行目录，保留旧 revision 和原始运行。

## CG/GO 与尚未完成事项

cg.json 和 go.json 各只有 instruction、output_format。共同输出三列 cve_id|matchCriteriaId|criteria、同一身份键、排序和 NONE 规则。pair_alignment.json 对 25 个必要条件逐项引用两题原文。只有 CG 添加四个研究步骤；GO 保留全部业务资格、时间、缺失、重叠和输出条件。英文语言检查及两种合理解释的处理见 language_review.md 和对照文件。没有公开网站名或入口 URL，没有泄露中间赢家或答案 ID。

现有 scorer、stage schema 文件及语言示例文件没有通过可用资源/文件工具暴露；不声称已经读取或执行。系统响应 schema 已用于阶段结果，表格输出按本次授权的最小三列定义准备。控制器仍需核对既有 scorer 的格式契约并实际执行 Python。完整正式评估期的现场稳定性仍需在真正测试时复核；本轮没有运行盲解或冒填成绩。
