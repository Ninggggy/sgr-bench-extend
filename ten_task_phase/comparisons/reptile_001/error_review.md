# 旧 Reptile 001 对照解释

六个预定槽均已有完成结果：CG Item-F1 为17/30、2/3、1，均值67/90；GO为17/28、23/56、0，均值19/56。保留原确定性评分、格式规则及所有高低分；这些是旧题比较，不能改变新题各组严格70%条件。

## 已观察到的公开答案暴露

CG第3次 r-6ad977509c71 实际打开 Hugging Face 公开的 reptile_001-g.json，读取包含oracle_answer的正文，并在中间消息明确引用参考对应表。随后又查看物种页面。最终得到1.0。公开答案暴露证据在public_answer_exposure.json，包括原会话时间、ordinal和原生网页返回正文。后续源页面核查不能消除之前的暴露；1.0仍保留，不能视为独立从源求解。

对其余五次events的定向检查未发现SGR-BENCH、PKUAIWeb、oracle_answer或该题公开JSON路径；这只是已保存轨迹中的未观察，不证明训练数据或所有未命中表述中不存在暴露。

## 格式和表示问题

CG1、CG2及GO1使用Syntypes/Lectotype/Holotype等首字母大写形式，而原oracle使用SYNTYPES/LECTOTYPE/HOLOTYPE。原rules没有大小写归一化，因而这些字段被判错；不能把这种损失当作分类学困难。原行键包含accepted name与old label，两者之一不同会影响整行对齐，原评分保留。

GO3 r-b16f08272ff9 返回25行六列表格，而要求的是单行分号分隔四列；其完整输出保留在answer.txt。原确定性评分得到0，但这主要是输出结构不符，不能解释成未取得实质科学进展或25个分类身份全部错误。没有把该结果改成合规答案或重新求解。

## 范围和语义歧义

CG使用“oldest binomial that is closest to the present”而GO写“most recent historical binomial”，前者自身存在年代方向歧义。部分运行选Asiatyphlops oatesii而oracle为Typhlops oatesii，需要根据真正历史名字顺序另行源审，不静默改旧oracle。

两题面以Boulenger1890印度蛇类标本为范围，但未提供明确枚举的标本子集；GO2和GO3分别列出20和25行，原oracle只有8行。类型所在地“India”与历史BritishIndia、当前地名的对应，以及BMNH记录究竟属于接受名还是其另一历史名字的模式材料，也需要逐条核验。这里不宣称更大集合全部正确，也不宣称旧8行集合已在本阶段完成新的内容验证。

## 恢复

原GO1 r-b9ac95ab18e1 因DNS/provider故障停滞且无final/score。按事先有限基础设施修复规则，用全新隔离 r-b9ac95ab18e1-repair 完成同一试次。原失败、审批证据和成本全部保留；没有将失败补0或缩小分母。已完成的六个旧题槽不再启动。
