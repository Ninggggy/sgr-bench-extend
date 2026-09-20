# r02 参考重算与证据复用

r02 独立执行 reference.py 后得到 16 行：8 FULL、7 PARTIAL、1 UNSPECIFIED。另从当前原始 prefix 与 seed 数据按公共规则独立计算，没有导入 reference.py，也没有读取 oracle 生成结果；生成后逐行比较一致。r01 的 16 条身份、标签和顺序完全保留，只有输出表头改为 REGISTERED_ID。reference.py 与 r01 程序比较，唯一文字改动就是这个生成表头，既有失败保护均保留。

从本目录运行 `python reference.py --out-dir recomputed`。默认 source_manifest.json 的核心 status/name/prefix/status 角色读取 `../resumption_pretest_refresh/`，实测窗口为 2026-09-13 03:15:28.584675–03:15:37.493410 UTC，四次 HTTP 200。全部 JSON 与原保存响应相同；controller 的 acquisition 和本次 refresh_checks.json 均可复查。这些是有缓存标记的实际响应，不证明直接回源新鲜度、永久可用性或未来评估窗口稳定。

原十份材料仍在 `../sources/`。当前核心角色与旧重复 name/prefix 比较，原 connectivity 分支仍提供 43 行及 27 条多组分排除，单组分全集与当前 16 行一致。原 broad-name 42 行只覆盖 2 个目标，default 页无目标；这些是保存的反例证据，不被说成新增检索。原 schema 和官方 InChI/注册语义锚点按 evidence.json 复用；其路径保持有效，不复制旧执行输出。迁移目录时须保留 source_manifest.json 指向的父目录材料。

四碳中心由种子 InChI 的规范编号推导为 13、14、19、20。分类只数非同位素 /t 层的 +/−；? 或缺失不计为指定。原程序继续检查单组分、实际基本层、SMILES 碳标记、完整分页、唯一身份及已观察的绝对立体模式。null 自身 hierarchy 的两个虚拟母体保留，盐记录 CHEMBL2359966 排除；drug chirality 和氮标记不替代四碳分母。参考程序仍是当前有限材料验证器，未知模式、缺失结构或不完整页会报错，不伪造空集。

后续实际评估前后仍按既有规则检查 status、唯一 quinine seed、从发现值构造的完整 prefix 页，并比较 ID 全集及答案相关结构字段。来源变化需复核，访问失败记未解决；seed、scope 或 component 证据改变时再核对 connectivity 分支。共同 runtime date 不是历史源截止日期。

schema_check.json 使用现有 stage_results.validate 检查完整候选 schema；prepare 文件检查另记 execution_checks.json。scorer_compatibility.json 的普通及边界文本夹具仅验证原评分器与中性列名兼容，不是模型表现。已知最短数据路径仍为两次 GET；bulk 和未探测外部捷径、模型难度、人工验证、开发后最终独立审计均未由本次构造证明。
