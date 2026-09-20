# 离线准备工具

仅依赖Python标准库。以下命令从construction_pipeline目录执行，不调用模型、不访问网站，也不创建真实读取隔离。公开题面投影只能移除不应传入的字段，不能识别instruction正文内的答案提示。

盘点正式50底题及50条GO：

```sh
python3 scripts/prepare.py inventory --out research/old_task_inventory.json
```

为一个旧题生成公开输入，用于验证同协议运行链路：

```sh
python3 scripts/prepare.py public \
  --task ../runs/open-source/sgr-bench/constraint.jsonl \
  --task-id arxiv_001 --date 2026-09-07 \
  --out research/example_public_cg.json

python3 scripts/prepare.py render \
  --stage 04_blind_solver --input research/example_public_cg.json \
  --out research/example_solver_prompt.md
```

新candidate.json使用同一public命令并增加`--variant cg`或`--variant go`；正式GO JSONL用`--task-id arxiv_001-g`。render只接受预设阶段名。盲解、攻击、确认阶段要求输入恰好为instruction/output_format/current_date；混入其他字段会报错。非盲解阶段附加common.md，盲阶段不附加构造说明。

检查候选声明的状态是否自洽：

```sh
python3 scripts/prepare.py validate-candidate \
  --candidate /absolute/path/to/candidate/r01/candidate.json
```

此命令只读取文件并输出检查摘要，不修改或升级候选状态。`reference_ready`、`content_validated`、`auto_validated`须声明非空oracle、参考程序及来源清单路径；后两者还须有完整CG/GO、完全相同的output_format、`validation.content=passed`和非空报告引用。`auto_validated`另外要求**该候选自身**的`validation.difficulty=confirmed_harder`；集合层面的确认结果不能满足此条件，工具也不会将集合结论赋给单题。

默认仅检查上述一致性，以及private内四个已知资产路径和validation.report_paths的相对路径语法：已声明路径须非空，不能是绝对路径或包含`..`。草稿可将参考路径与题面留为null。默认不检查文件存在；增加`--check-files`后，所有这些引用都以candidate.json所在目录为根，须指向实际文件，符号链接解析后也不能越出该目录。

```sh
python3 scripts/prepare.py validate-candidate \
  --candidate /absolute/path/to/candidate/r01/candidate.json --check-files
```

通过仅表示声明之间没有已检查的矛盾，以及选用`--check-files`时所引用文件存在。它不是完整JSON Schema验证，不执行参考程序，不检查报告内容，不能证明来源真实、答案正确、两题面语义等价或单题确实更难。失败返回退出码2；成功摘要明确记录是否检查过实际文件。

四份schema分别描述候选对象、非盲阶段摘要、求解结果与裁决资产的字段形状；候选状态的跨字段要求由上述普通Python检查实现。准备工具尚未实现完整schema验证，也不消费阶段注册表或裁决资产。阶段摘要的`completed`或求解者的`complete`不是内容/难度通过结论。集合确认结果单独保存在comparisons中：其中某个候选仍可为`content_validated`、`difficulty=inconclusive`、人工验证`not_performed`。工具保留这些实际声明，不因集合已确认而更改它们；它也不读取集合报告或判断单题试次数是否足够。

生成文件后，需要外部运行器把公开输入和result schema复制到隔离环境，再按[运行文档](../docs/03_runtime.md)调用Codex。此脚本不读取config.example.json自动执行任务；配置文件是生产调度器的设计输入。

验证公开投影、拒绝私有输入、确认轮提示一致性，以及候选状态与路径检查：

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

这些检查不证明操作系统读取隔离、网站事实正确、新题难度或Codex结构化输出兼容性。脚本允许更新指定输出文件，但拒绝把输出路径设置为同一次命令的输入路径。

目前inventory会如实报告genome_003/004两项配对检查不一致，这是正式CG/GO编号与内容交叉对应造成的已观察问题，见[记录](../research/old_pairing_exceptions.json)。脚本不自动套用映射；生产比较器应按审阅后的映射单独处理，并保留原ID。
