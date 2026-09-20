# arxiv_001 CG 单题真实 smoke test

只读正式 `runs/open-source/sgr-bench/constraint.jsonl` 的 `arxiv_001`。控制端可评分，求解端只收到 prepare.py public/render 生成的原题、格式和实际执行日期，以及原 solver_result schema。每次入口创建新编号目录，保留全部旧文件，不挑选高分。

在仓库根目录执行：

```sh
docker build --pull=false -t sgr-smoke-codex:local -f construction_pipeline/smoke_test/Dockerfile construction_pipeline/smoke_test
python3 -m unittest discover -s construction_pipeline/smoke_test -p test_score.py -v
python3 construction_pipeline/smoke_test/run.py
```

需要本机 Docker、Python 3、现有 `eviready-codex:local`（提供 0.153.4 CLI 和 CA 证书）及 `node:22-bookworm-slim` 镜像、有效的 `~/.codex/auth.json`。可用 `--auth /absolute/path/auth.json` 指定已有认证。镜像构建不安装软件包、不复制研究目录或原镜像的 home/work；只有 CLI 运行时及 CA 证书进入干净基础镜像。不复制用户 config、插件或历史会话。主机认证不会写到交付文件。

容器无宿主 bind mount、无 Docker socket、只读根、清空 capabilities、no-new-privileges，临时 home/work。只把公开文件和最小认证/config 经 stdin 写入容器，输出由控制端回收。求解使用 gpt-6-astra/high、原生 live web；shell、apps、MCP、子代理均不开放。保留 CLI read-only 沙箱及认证/TLS 校验。联网由原生网页工具完成，无 Python 网络替代通道。与论文 Serper/fetch/PDF、medium 配置不同，不能视为原论文设置复现。

单次上限 6000 秒，3000 秒无工具进展停止，每 5 秒观察事件。终止只作用于本次创建的容器。默认一次，不自动重试。必须先完成评分测试，再调用模型。运行完成自动提取 JSON 的 `final_answer`，不修改内容，再执行 score.py。

复算已有真实答案（不调用模型）：

```sh
python3 construction_pipeline/smoke_test/score.py --answer construction_pipeline/smoke_test/runs/003/answer.txt --out construction_pipeline/smoke_test/runs/003/recomputed
```

离线核验原始答案提取、重新计数及工具日志：

```sh
python3 construction_pipeline/smoke_test/verify_run.py construction_pipeline/smoke_test/runs/003
```

人工评分样例和真实输出严格分开。评分规则见 SCORING.md。暂定严格评分不自动承认出版会场缩写等语义别名；报告列出未核验等价，不静默加分。

每次目录包含公开输入/提示/schema、配置、隔离探针、原始 JSONL 事件/stderr、run.json、实现副本及人工测试日志。产生答案的运行另外包含 solver_output/result.json、answer.txt、extraction.json、sessions（仅该次隔离会话）、scoring/parsed.json、scores.json、field_differences.json。无真实答案的故障运行不生成伪造的 answer 或零分。

001 是模型调用前的输入复制故障；002 是首次 CLI 调用的 CA 缺失故障；003 是修复后的唯一追加 CLI 调用。详见 report.md 和各目录日志。
