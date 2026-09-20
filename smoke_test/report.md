# arxiv_001 CG 实际隔离运行与评分报告

已完成公开输入生成、真实读取隔离、正式求解前评分检查、真实 Codex 求解、原样提取、确定性评分与离线复算。真实答案位于 `runs/003/`。没有补写答案，没有修改正式旧题，没有因分数重跑。**当前指标为暂定严格匹配，尚未完成论文的全部人工语义规范化；不能把 Row-F1=0 解读为没有找到正确论文。**

## 实际运行

| 项目 | 实测记录 |
|---|---|
| 题目 | 正式 constraint.jsonl 中唯一 arxiv_001；仅 CG |
| 模型 / provider / effort | gpt-6-astra / openai / high；隔离会话 turn_context 核实，不采用模型自报 |
| CLI | codex-cli 0.153.4 |
| 日期 | 2026-09-08，公开输入日期取控制端 Asia/Shanghai 当日 |
| 开始 | 2026-09-08 17:49:28.236 +08:00（09:49:28.236 UTC） |
| 结束 | 2026-09-08 17:54:23.449 +08:00（09:54:23.449 UTC） |
| 墙钟耗时 | 295.215 秒，约 4 分 55 秒 |
| 退出 / 完成事件 | 0 / 收到 turn.completed |
| 运行状态 / 模型自报 | completed / complete，分别保存，不互相替代 |
| 真实工具 | 20 次 exec 包装的原生 web__run 批调用；保留搜索、打开页面的完整请求与响应 |
| token 用量 | CLI 报告 input_tokens=1,677,400；cached_input_tokens=1,515,776；output_tokens=4,828；reasoning_output_tokens=704；不自行推算费用或把这些字段相加 |
| 预算 | 最长 6000 秒；无实质进展 3000 秒终止；本次未触发 |

工具/协议差异：本机没有论文所用的 Serper/fetch/PDF 工具组，使用现有 Codex 原生网页工具；未用 Python、shell、MCP 或宿主工具另行检索。high 也不同于论文 medium。本次是旧题链路验证，不是原论文工具设置或成绩复现。[配置文档](https://learn.chatgpt.com/docs/config-file/config-reference)与本地 CLI help/features 均核对，实际配置留在 solver.config.toml。

运行记录全保留：001 在模型调用前因 docker cp 与只读根冲突失败；002 是第一次 codex exec，因干净基础镜像缺少 CA 包产生 TLS UnknownIssuer，70.063 秒后控制端停止，没有答案；003 补入已有 CA 包后，是唯一一次追加模型调用。没有跳过证书检查。002 即使 CLI 退出码为 0，也因没有完成事件被标为 runtime_error。详见 implementation_notes.md。

## 读取隔离与输入

Docker 干净基础镜像只复用 CLI 运行时与 CA；没有继承旧镜像 home/work。无宿主 bind mount、无 Docker socket、不用 host network；只读根文件系统、cap-drop=ALL、no-new-privileges；全新临时 home/work。仅公开 input、prepare.py render 的盲解 prompt、原始输出 schema 和最小工具配置/已有认证被复制。认证只在容器 tmpfs，回收时不导出认证。没有 resume、fork 或研究对话继承。求解工具不含 shell、apps、MCP、子代理或宿主访问接口。

运行前从同一容器实际读取无敏感探针、正式参考路径、宿主 sessions 路径和 Docker socket，均 ENOENT；Mounts=[]。探针在求解上下文之外运行，没有把探针路径告诉求解者。详见 runs/003/isolation.json。独立会话记录中 cwd=/work，effort=high。输出回收后容器已删除。

公开 JSON 恰好三个键：instruction、output_format、current_date。前两项与正式文件逐字相同；prompt 中没有 task_id。原始结果为 solver_output/result.json；answer.txt 恰好等于其 final_answer，没有增补或重排。Markdown 链接 ID 在评分阶段规范化为裸 ID，原始答案保持完整。

## 三指标与分子分母

公式来自 `chinese_1st_ver/latex/sections/Appendix.tex` 的 Metric Definitions。规则 SCORING.md 和 score.py 在首次求解前确定，之后评分器没有变化。评分结果状态 `provisional_strict`。

| 指标 | 分子 / 分母 | 结果 |
|---|---|---:|
| Item-F1 | 2 × 23 / (36 + 36) = 46/72 | 0.6388888889（63.8889%） |
| Row-F1 | 2 × 0 / (4 + 4) = 0/8 | 0（0%） |
| P.O.A. | 正序共同 ID 对 6 / 全部共同 ID 对 6 | 1（100%） |

Gold 和预测各 4 行，每行 9 字段。共同 ID=4；遗漏 ID、额外 ID、重复 ID 均为空。全 6 对相对顺序正确。没有因解析丢行、空字段或表头问题损失计数。

| arXiv ID | 严格正确字段 / 9 | 全字段正确 |
|---|---:|---|
| 1910.02551 | 5 | 否 |
| 2011.00050 | 6 | 否 |
| 2107.13034 | 6 | 否 |
| 2110.04181 | 6 | 否 |

逐字段原值、规范化值、gold、是否匹配在 scoring/field_differences.json；解析原行在 scoring/parsed.json；计数、ID 差异和全部顺序对在 scoring/scores.json。

## 问题归因与未计分的等价表达

1. **运行环境**：001/002 属输入复制和 CA 证书故障，均已修复。003 无 CLI 错误。模型报告 API 请求失败、IEEE/DOI 页无可读内容，改用可读 arXiv 页面及日本国立国会图书馆的 Crossref 元数据；这些访问限制保留在原始工具记录和 limitations 中。
2. **解析与评分**：Markdown 的四行被完整解析，裸 ID 对齐正确。13 个不相等字段中，4 个 term family 使用 `dataset distillation/condensation`，4 个 primary category 使用 `Machine Learning (cs.LG)`，1 个 cue 使用 `Abstract` 而参考为 `Abstract-only`，1 个 DOI clue 附带会场文字。这 10 项是需要进一步明确确定性语义等价规则/最短线索要求的差异；本次不在看到答案后添加别名提高分数。不能将严格不相等直接认定为 10 个事实错误。
3. **旧题自身**：其余 3 项是 1910.02551、2107.13034、2110.04181 的 cue。模型写 `Title and abstract`；官方当前页面确实标题和摘要均命中，而旧 gold 写 `Title`，与 rubric 的 `Title + Abstract` 定义冲突。仍按原 gold 计分，未改参考。这不是已证明的网页时间漂移：没有历史快照，不能归因到更新时间。证据和链接见 source_audit.md、controller_source_evidence.json。
4. **模型作答**：找到了全部四个参考 ID，顺序、日期、版本和 publication-trail source 均与参考一致；没有补答或挑选结果。若按 rubric 的最短出版线索要求，第一行添加 IJCNN 会场说明较冗长。公开题面未给完整枚举/别名规则，因此本次严格低分不能直接代表研究结果质量。模型的穷尽性声明只作为其声明保存；本次控制端没有重新证明候选全集完整性。

## 检查与复算

正式求解前 13 项人工数据测试全部通过。3×3 样例的预期与结果：完全正确 (1,1,1)；逆序 (1,1,0)；漏行 (.8,.8,1)；错一个非 ID 字段 (8/9,2/3,1)；空答案 (0,0,0)。另含 Markdown 等价、重复 ID（首行错误时也不挑后行）、缺字段、额外 ID、单个共同 ID、版本后缀和解析失败。人工样例没有用于冒充模型答案。

verify_run.py 核验了原题投影、原样提取、实际模型/high、评分器与求解前副本一致，并重新计算全部计数和逐字段差异，结果一致；又通过独立评分入口生成 recomputed/。交付目录按当前认证长字符串进行不输出凭据的匹配扫描，没有发现凭据。详见 verification.json、scoring_tests.txt、credential_check.json。

尚未完成：论文完整的人工语义等价规范化，以及旧参考 cue 冲突的正式裁决。以上局限不阻碍复算本次明确标注的严格指标，但限制对模型能力与正式论文成绩的解释。

## 交付与命令

所有新增文件在 `construction_pipeline/smoke_test/`，保留已有材料和各次运行。README.md 包含依赖、镜像构建及各输出用途；run.py 是复跑入口，score.py 是离线评分入口；003/implementation/ 保留实际求解时的实现副本。工具与网页原始响应在 003/tool_events.jsonl 和 003/sessions/，CLI 原始事件与错误在 events.jsonl、runner.stderr。

从仓库根目录复算已有答案，不再调用模型：

```sh
python3 construction_pipeline/smoke_test/score.py --answer construction_pipeline/smoke_test/runs/003/answer.txt --out construction_pipeline/smoke_test/runs/003/recomputed
python3 construction_pipeline/smoke_test/verify_run.py construction_pipeline/smoke_test/runs/003
```

重新执行一次新求解（产生下一个编号目录，不覆盖 003；会实际使用模型）：

```sh
python3 construction_pipeline/smoke_test/run.py
```
