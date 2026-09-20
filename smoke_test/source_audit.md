# 控制端旧参考核查（不向求解会话提供）

核查日 2026-09-08；使用控制端 web.open 直接打开下列 arXiv 官方记录。工具返回包含缓存抓取时间，因此只能称本次取回的当前页面，不能证明历史快照或实时数据库绝对完整。没有重新构造候选集，也没有改动正式 JSONL。

- [1910.02551](https://arxiv.org/abs/1910.02551)：页面标题含 Dataset Distillation，摘要开头也含 dataset distillation。primary cs.LG；v1 2019-10-06，v3 2020-05-05；Related DOI 与旧参考一致。旧参考 cue location=Title，但 rubric 将“标题和摘要都有”定义为 Title + Abstract，存在明确的参考/rubric 冲突。
- [2011.00050](https://arxiv.org/abs/2011.00050)：标题无目标短语、摘要含 dataset distillation；primary cs.LG；v1 2020-10-30，v2 2021-03-02；Comments 表明 ICLR 2021 接收。所检查字段支持旧参考。
- [2107.13034](https://arxiv.org/abs/2107.13034)：标题和摘要均含 dataset distillation；primary cs.LG；v1 2021-07-27，v3 2022-01-17；Comments 为 NeurIPS 2021。旧参考 cue location=Title 同样与 rubric 的 Title + Abstract 定义冲突。
- [2110.04181](https://arxiv.org/abs/2110.04181)：标题和摘要均含 dataset condensation；primary cs.LG；v1 2021-10-08，v2 2022-04-21；Journal reference 指向 WACV 2023。旧参考 cue location=Title 同样存在冲突。

三条 cue location 冲突可由本次页面内容观察，但没有历史快照，不能断言由网页更新引起。各记录的日期、版本、分类和出版线索仍有支持，不意味着旧题的全集完整性已被重新证明。正式评分继续逐字采用旧参考，冲突另列，不把符合公开来源的作答简单归因为模型事实错误。

正式题面的公开 instruction 没有完整解释 cue location 枚举、term family 平局规则或出版线索缩写；这些规则在 rubric 中。评分器仅在控制端使用，不向模型泄露。
