# 数据、证据与导出格式

## 一题的工作目录

以下是待运行时生成的目录，不是本轮已经存在的数据集。编号仅用于引用，revision用普通递增整数。

```text
campaign/
  campaign.json
  sites/<ecosystem>/site_profile.json
  candidates/<candidate_id>/r01/
    candidate.json
    private/
      source_manifest.json
      sources/
      candidate_universe.jsonl
      inclusion_ledger.jsonl
      state_graph.json
      field_evidence.jsonl
      reference/solve_reference.py
      reference/oracle.psv
      reference/counterfactuals.json
      pair_alignment.json
      content_audit.json
    public/cg.json
    public/go.json
    runs/<opaque_run_id>/
      run.json
      prompt.md
      events.jsonl
      result.json
      runner.stderr
  comparisons/assignment.json
  comparisons/analysis_plan.json
  comparisons/screening.json
  comparisons/confirmation.json
  export/constraint.jsonl
  export/goal.jsonl
```

这是调度器视图。盲解进程只能看复制出去的公开输入和自己的运行目录，不能直接在这棵包含private的目录树下无隔离执行。

## 候选对象

[candidate.schema.json](../schemas/candidate.schema.json)约束候选摘要，不试图在一个JSON里容纳全部原始网页。至少保留：

- `candidate_id / revision / ecosystem / domain / status`：普通身份与阶段；domain继承原数据值。
- `old_task_refs`：1—3个正式旧底题；构造前先指定，改对照应解释原因。
- `research_goal / structural_upgrade`：自然研究问题，以及比具体旧题多了哪个真实依赖。
- `public.cg / public.go`：各自只有instruction和output_format；尚未生成时为null。
- `private`：数据版本、入口、候选范围、谓词、schema、行键、排序、缺失规则、证据与参考计算路径；尚无oracle时路径为null。
- `validation`：内容、难度、人工验证三个独立结论；不因其中一个成功自动填另两个。

状态流：`candidate → reference_ready → content_validated → auto_validated`；另有`needs_revision / rejected / inconclusive`。`auto_validated`在单个候选上指内容成立且独立确认轮支持该候选相对于指定旧题的难度结论；只有结构分析或集合均值下降不能达到此状态。集合级结论独立写入comparisons/confirmation.json，列明全部参评候选；集合确认中的单题可仍为content_validated、difficulty=inconclusive。没有每个候选都必须成品的要求。

集合报告至少标明分析计划、候选ID/revision清单、实际旧题成员、生态覆盖与权重、量纲、各题面运行数、失败处理、主差值及区间的推断范围。固定题集运行波动与题目组成敏感性分别报告。报告中集合层面的“更难”不能复制到candidate.validation.difficulty。

## 必须有的证据字段

| 资产 | 最小内容 |
| --- | --- |
| source_manifest | source_id、官方URL、HTTP方法与查询/请求参数、获取时间、响应状态/类型、保存路径、数据版本、网页或PDF定位方法 |
| candidate_universe | 来源内的原始ID和范围，枚举入口，分页/全量终止依据；不能只保存最终命中 |
| inclusion_ledger | 每个候选的ID、每项谓词结果true/false/unknown、证据引用、最终去留；unknown不自动当false |
| state_graph | 默认状态和目标状态实际响应的引用、节点的来源/参数/可见证据；边类型data/control；控制边须写明哪个证据决定哪个参数 |
| field_evidence | 行键、列名、source_id、定位、原始值、规范化规则；计算字段再列输入键和公式 |
| counterfactuals | 修改哪条依赖、为何是合理错误、实际重算的变化、受影响输出；没有变化也如实记录 |
| pair_alignment | 每个必要谓词在CG和GO中的原文位置，以及阈值/范围/并列规则是否一致 |
| content_audit | 六要求逐项结论、具体失败证据、每题面两份盲解及各一次攻击的运行引用、未决问题 |

每个引用必须能指回实际材料。原始内容涉及再分发限制时，保存和发布按来源规则处理；内部可验证性与公开可发布性分别记录。历史窗口本身不保证当前网页不更新，需要检查版本和获取日期。

## 模型阶段输出

非盲解阶段统一返回[stage_result.schema.json](../schemas/stage_result.schema.json)中的摘要：`status / summary / artifacts / evidence_refs / issues / next_action`。大数据与报告放资产文件，摘要仅引用实际已写文件。

盲解与盲攻击使用[solver_result.schema.json](../schemas/solver_result.schema.json)：`status / final_answer / evidence / limitations`。`final_answer`内是题目要求的表格或NONE；外围JSON只为调度器保存结果，不给评分增加列。父进程的退出/超时事实与模型自报status分别存储。

裁决资产的结构见[decision.schema.json](../schemas/decision.schema.json)。它把candidate内容、candidate难度及报告引用分开；集合级统计另存，不能改变其中的candidate难度字段。

candidate内部的文件引用均相对candidate.json所在目录，父进程接收资产时更新引用；不能把工作单相对campaign根的路径直接混入。离线工具`validate-candidate`检查声明状态的一致性，`--check-files`再检查路径对应文件存在且不越出候选目录；它不验证事实、报告内容或实验结论。

题面作者写出cg.json/go.json后，父进程先校验两字段、共同output_format和语义对齐报告，再将其内容更新到candidate.public；后续公开投影以这个已核对的对象为准。不能让文件与候选内嵌题面各自被不同角色修改。

## 与现有格式衔接

正式导出的CG/GO保留原项目字段：`task_id, domain, autonomy_type, instruction, start_url, output_format, oracle_answer, oracle_output_cardinality, metadata, rubric`。CG使用新底题ID，GO加`-g`。输出schema、oracle和行数必须一致。新ID先与正式50题及工作目录现有编号查重，避免覆盖旧草稿。

导出范围与完成声明对应：默认集合目标通过时，导出确认计划中的完整、内容有效题集，并关联集合报告；成员可保持content_validated，不以全部达到auto_validated为导出前提。若只导出其中单题成绩较难的子集，原集合确认不能自动转作该子集的确认。只有内容成立而难度目标尚未获支持时，导出为内容候选包并注明未完成难度验证。

`metadata`中的状态要求和依赖来自真实状态图；`rubric`中的纳排、规范化、排序来自共同任务定义。构造来源、模型运行和验证说明可写入单独sidecar，由普通task_id关联，不要求旧评测器认识新字段。保留旧项目已经存在的字段，但本方案不新增hash、冻结contract等机制。

公开给求解模型时必须再次做字段投影，不能把导出JSON整行作为prompt输入。尤其不得暴露oracle、真实行数、domain、start_url、内部rubric和状态图。题目自然语言中必需的信息由作者明确写入；投影工具无法识别题面中的答案暗示，仍须语义审计。

## 评分器衔接

优先复用已核验的现有规范化与评分逻辑，针对新schema补普通解析规则。Item-F1匹配的是有行键对齐的正确字段槽位，Row-F1匹配整行；P.O.A.在共有行键上看次序，少于两个共有键时为0。不要把字符相似度、两模型一致率或隐藏推理长度当作论文指标。

落地前应读取并核对实际评分实现的重复行、空表、解析失败和排序语义。本轮工具不重新实现评分器，也没有验证旧项目全部评分代码。难度实验引用原始预测、规范化输出和计分明细，不能只有一张平均分表。
