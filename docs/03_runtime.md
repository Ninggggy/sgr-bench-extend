# Codex运行与调度实现

## 实际核对结果

本机为Codex CLI 0.153.4；本地模型缓存包含 `gpt-6-astra`，列出low/medium/high/xhigh/max/ultra。缓存不是账户授权证明。CLI帮助实际支持 `exec`、`--model`、`--json`、`--output-schema`、`--output-last-message`、`--cd`、`--skip-git-repo-check`；当前工作区不是Git仓库。

官方文档将 `codex exec` 用于非交互脚本运行，`--json`提供事件流。选择CLI作为第一版智能工作进程，无需自建API层的工具循环；以后迁移Responses API再单独实现。[官方执行文档](https://learn.chatgpt.com/docs/developer-commands#codex-exec)

## 一次工作进程

下面是已依据本机help核对的调用形状；本轮没有启动此命令。目录和文件应由调度器提前准备。

```sh
codex exec \
  --model gpt-6-astra \
  -c 'model_reasoning_effort="high"' \
  --cd /absolute/path/to/stage-workspace \
  --skip-git-repo-check \
  --sandbox workspace-write \
  --json \
  --output-schema /absolute/path/to/stage-workspace/result.schema.json \
  --output-last-message /absolute/path/to/stage-workspace/result.json \
  - < /absolute/path/to/stage-workspace/prompt.md \
  > /absolute/path/to/stage-workspace/events.jsonl \
  2> /absolute/path/to/stage-workspace/runner.stderr
```

需要网络的检索阶段应通过预先配置的受控MCP工具读取网页；上面的命令本身不会安装或自动配置搜索、抓取和浏览器。生产环境应先验证工具可用性，并保留宿主现有沙箱、审批和认证措施，不用关闭这些措施解决复现问题。

`--output-schema`只约束最终回复形状，不能保证事实正确、网页真实或所有输出资产存在。父进程还需验证文件可解析、声明文件存在、指标来自原始输出、证据定位能复查。不要把CLI退出0当作数据验收通过。

## 上下文与文件隔离

普通workspace-write沙箱主要限制写入，**不能据此声称看不到其他目录的oracle**。新建文件夹或在prompt里说“不许看答案”也不构成完整读取隔离。

生产盲解环境建议采用独立容器/虚拟机或操作系统用户与权限配置：只挂载公开输入、工具运行所需文件和该次输出目录；不挂载原研究目录、模型历史会话、私有oracle、旧题答案仓库或构造者日志。工具服务器不得把构造缓存/私有文件路径暴露给求解者。认证使用运行环境既有方式或受控凭据注入，不把密钥写进题目/事件正文。

角色可见范围：

| 角色 | 可以看到 | 不可看到 |
| --- | --- | --- |
| 网站探索 | 同生态旧题、官方网站、机制文档、历史证据 | 无须接触与任务无关资料 |
| 构造/参考解 | 站点画像、旧题对照、候选私有证据 | 不用最终确认轮输出来反复调题后继续声称确认独立 |
| 盲解A/B | instruction、output_format、固定评测日期、允许工具 | task_id、domain字段、入口提示、oracle、rubric内部答案线索、构造证据、对方结果 |
| 盲攻击 | 与盲解相同公开输入 | oracle、隐藏图、候选答案词表 |
| 证据审计/裁决 | 全部候选材料和已有尝试 | 不把生成的理由当作官方来源 |
| 确认轮求解 | 与普通盲解相同 | 构造/筛选历史与难度标签 |

底题编号与网站标签也可能泄露来源。父进程维护run_id到task_id映射，公开输入只保留随机化的不含语义运行号或完全省略编号。CG和GO不放在同一个求解上下文中。

## 调度逻辑

第一版只需一个Python调度器、普通JSON文件、阶段目录和一个队列；不需要复杂框架。先串行，后续可用有上限的进程池。

```text
for ecosystem in selected_ecosystems:
    profile = explore(ecosystem)
    for opportunity in supported_opportunities(profile):
        candidate = design(opportunity, nearest_old_tasks)
        for revision in bounded_revisions:
            reference = build_reference(candidate)
            pair = render_CG_GO(candidate, reference)
            attempts = fresh_blind_solves(pair)
            attack = fresh_shortcut_attempt(pair)
            audit = inspect_sources_and_dependencies(reference, attempts, attack)
            decision = adjudicate(audit)
            if decision == reject or decision == inconclusive: stop_candidate()
            if decision == revise: candidate = repair(candidate, audit); continue
            break
        if content_validated:
            screening = compare_with_old_tasks_under_same_protocol(pair)
            if plausible_harder_and_solvable:
                confirmation = fresh_confirmation_runs(pair)
                export_only_what_confirmation_supports()
```

`fresh_blind_solves`在内容验证时启动A-CG/A-GO/B-CG/B-GO四个会话；初筛可先每题面一次但不算完整复核。调度器启动全新会话，不从构造会话resume/fork。A/B可使用相同基础提示但分别独立找证据；不要给B“请证明A正确”的目标。

## 每次运行的记录

`run.json`至少包含：run_id、candidate_id、revision、stage、replicate、variant、model、provider、effort、Codex版本、工具配置引用、公开输入路径、开始/结束时间、CLI退出码、是否收到完成事件、结果文件路径、可用token统计、环境错误。

`events.jsonl`保留原始工具事件；网页证据保存URL/参数、响应类型、取得时间及本地内容。不要为捕获细节要求模型输出隐藏思维过程；使用可观察的工具调用、查询结果、简洁决策理由和可执行计算即可。

完成状态拆开：`completed`、`timeout`、`access_error`、`tool_error`、`invalid_output`、`cancelled`。父进程判状态，不能让模型在result里自称通过就改变运行事实。answer_ready与退出码分别保留；有最终答案但后续被停止的情况先按运行器语义判断，不自动丢弃或自动当成功。

## 预算与恢复

建议初始每生态2个候选、每候选最多2次修订，单次最长6000秒，并给整批设置最大模型调用数和总墙钟时长。示例配置是资源估算，不保证成品数。

外层先检查剩余预算再启动阶段，运行中监测进程与事件；超时终止自己启动的工作进程并标记状态。若事件用量只在结束后返回，不能声称能精确限制总token；使用调用数/墙钟硬边界、token软预警。不要反复重试账户额度不足或无权限访问。

恢复时读取已有完成文件和状态，仅恢复未完成阶段；同一次盲解可恢复自身上下文，但不得继承其他角色；若本次难度协议不允许恢复，则按中断规则记录，不额外延长预算。修订产生新revision和新运行目录。原始数据不可用时保留错误并回退到其他可用候选，不自动发布半成品。

## 阶段接口

[stage_registry.json](../stage_registry.json)提供阶段、提示、结果schema和必要资产角色的机器可读设计；当前prepare.py尚未消费该registry，不能称为生产调度已接通。具体交接和工作单见[执行蓝图](07_implementation_blueprint.md)。工作单只由父进程保留，盲阶段不得读取。

## 开发划分

已实现：`prepare.py`可离线盘点正式旧题，按白名单生成求解公开输入，合并阶段prompt和输入JSON，并检查候选状态、公开字段与引用路径的一致性；可选检查引用文件存在且未越界。它不调模型，不提供物理隔离，不自动评分，也不能证明任务通过。

待实现：生产队列/CLI进程管理、隔离运行环境、search/fetch/PDF工具映射、网站响应保存、针对新任务的参考计算与评分器、难度统计和正式导出。优先走通一个候选闭环后再扩展网站适配，避免一次写出十二套未经验证的通用爬虫。
