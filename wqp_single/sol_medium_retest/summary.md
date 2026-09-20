# Sol/medium 逐次成绩

此表只包含本轮固定计划；NA不是零分。计数是原解析器识别的条目，不等于未识别CSV中实际包含的数据行；confirmation_new_GO_3的原CSV有12行12列，但缺6个必需字段，原解析计数为0、指标为NA。完整匹配以原评分器的三个指标均1判定；旧004的参考集合不代表公开条件唯一。

## screening

|尝试|状态|Item-F1|Row-F1|P.O.A.|整题匹配|正确字段/参考/预测|正确行/参考/预测|正确顺序对/共有对|
|---|---|---:|---:|---:|---:|---|---|---|
|[screening_new_CG_1](runs/r-a55562d61d59/run.json)|completed|0.1|0.1|1.0|0|54/216/864|3/12/48|3/3|
|[screening_old_CG_1](runs/r-6c876269dbe4/run.json)|completed|1.0|1.0|1.0|1|27/27/27|3/3/3|3/3|
|[screening_new_GO_1](runs/r-8224e9cc365a/run.json)|completed|0.6574074074074074|0.0|1.0|0|142/216/216|0/12/12|66/66|
|[screening_old_GO_1](runs/r-24202450d4ad/run.json)|completed|1.0|1.0|1.0|1|27/27/27|3/3/3|3/3|

|题目/题面|可评分/预定|整题匹配数|Item-F1均值|Row-F1均值|P.O.A.均值|整题正确率|
|---|---:|---:|---:|---:|---:|---:|
|new_cg|1/1|0|0.100000|0.100000|1.000000|0.000000|
|new_go|1/1|0|0.657407|0.000000|1.000000|0.000000|
|old_cg|1/1|1|1.000000|1.000000|1.000000|1.000000|
|old_go|1/1|1|1.000000|1.000000|1.000000|1.000000|

可评分尝试内先平均、CG/GO等权（新、旧、差值）；存在NA时仅为条件描述均值：

- Item-F1: 0.3787037037037037 / 1.0 / -0.6212962962962962
- Row-F1: 0.05 / 1.0 / -0.95
- P.O.A.: 1.0 / 1.0 / 0.0
- whole_task_exact: 0.0 / 1.0 / -1.0

完整预定分母的指标差值：{'Item-F1': -0.6212962962962962, 'Row-F1': -0.95, 'P.O.A.': 0.0, 'whole_task_exact': -1.0}；端到端完整匹配率（解析失败记未交付成功，不作能力零分）：{'new': 0.0, 'old': 1.0}

## confirmation

|尝试|状态|Item-F1|Row-F1|P.O.A.|整题匹配|正确字段/参考/预测|正确行/参考/预测|正确顺序对/共有对|
|---|---|---:|---:|---:|---:|---|---|---|
|[confirmation_new_CG_1](runs/r-0ee77dc62ed5/run.json)|completed|1.0|1.0|1.0|1|216/216/216|12/12/12|66/66|
|[confirmation_old_CG_1](runs/r-b90e2f062f85/run.json)|completed|1.0|1.0|1.0|1|27/27/27|3/3/3|3/3|
|[confirmation_new_GO_1](runs/r-69914a9877c8/run.json)|completed|0.6574074074074074|0.0|1.0|0|142/216/216|0/12/12|66/66|
|[confirmation_old_GO_1](runs/r-d04075b89074/run.json)|completed|1.0|1.0|1.0|1|27/27/27|3/3/3|3/3|
|[confirmation_new_CG_2](runs/r-92c02e2f6067/run.json)|completed|0.49537037037037035|0.0|1.0|0|107/216/216|0/12/12|36/36|
|[confirmation_old_CG_2](runs/r-4a02a31cb8e8/run.json)|completed|1.0|1.0|1.0|1|27/27/27|3/3/3|3/3|
|[confirmation_new_GO_2](runs/r-4df368e8ea7e/run.json)|completed|0.6574074074074074|0.0|1.0|0|142/216/216|0/12/12|66/66|
|[confirmation_old_GO_2](runs/r-d936d9895abf/run.json)|completed|1.0|1.0|1.0|1|27/27/27|3/3/3|3/3|
|[confirmation_new_CG_3](runs/r-e5e848752431/run.json)|completed|1.0|1.0|1.0|1|216/216/216|12/12/12|66/66|
|[confirmation_old_CG_3](runs/r-551a85fda485/run.json)|completed|1.0|1.0|1.0|1|27/27/27|3/3/3|3/3|
|[confirmation_new_GO_3](runs/r-426fcaec1732/run.json)|completed|NA|NA|NA|NA|0/216/0|0/12/0|0/0|
|[confirmation_old_GO_3](runs/r-683967eda07e/run.json)|completed|1.0|1.0|1.0|1|27/27/27|3/3/3|3/3|

|题目/题面|可评分/预定|整题匹配数|Item-F1均值|Row-F1均值|P.O.A.均值|整题正确率|
|---|---:|---:|---:|---:|---:|---:|
|new_cg|3/3|2|0.831790|0.666667|1.000000|0.666667|
|new_go|2/3|0|0.657407|0.000000|1.000000|0.000000|
|old_cg|3/3|3|1.000000|1.000000|1.000000|1.000000|
|old_go|3/3|3|1.000000|1.000000|1.000000|1.000000|

可评分尝试内先平均、CG/GO等权（新、旧、差值）；存在NA时仅为条件描述均值：

- Item-F1: 0.7445987654320988 / 1.0 / -0.2554012345679012
- Row-F1: 0.3333333333333333 / 1.0 / -0.6666666666666667
- P.O.A.: 1.0 / 1.0 / 0.0
- whole_task_exact: 0.3333333333333333 / 1.0 / -0.6666666666666667

完整预定分母的指标差值：{'Item-F1': None, 'Row-F1': None, 'P.O.A.': None, 'whole_task_exact': None}；端到端完整匹配率（解析失败记未交付成功，不作能力零分）：{'new': 0.3333333333333333, 'old': 1.0}

## 逐字段差异与原始作答

- screening_new_CG_1: [字段明细](runs/r-a55562d61d59/scoring/field_differences.json)；[原始答案](runs/r-a55562d61d59/answer.txt)；[原始工具记录](runs/r-a55562d61d59/tool_events.jsonl)。差异记录数 972；类型 {'unmatched_id': 810, 'omitted_row': 162}。
- screening_old_CG_1: [字段明细](runs/r-6c876269dbe4/scoring/field_differences.json)；[原始答案](runs/r-6c876269dbe4/answer.txt)；[原始工具记录](runs/r-6c876269dbe4/tool_events.jsonl)。差异记录数 0；类型 {}。
- screening_new_GO_1: [字段明细](runs/r-8224e9cc365a/scoring/field_differences.json)；[原始答案](runs/r-8224e9cc365a/answer.txt)；[原始工具记录](runs/r-8224e9cc365a/tool_events.jsonl)。差异记录数 74；类型 {'missing_or_different': 74}。
- screening_old_GO_1: [字段明细](runs/r-24202450d4ad/scoring/field_differences.json)；[原始答案](runs/r-24202450d4ad/answer.txt)；[原始工具记录](runs/r-24202450d4ad/tool_events.jsonl)。差异记录数 0；类型 {}。
- confirmation_new_CG_1: [字段明细](runs/r-0ee77dc62ed5/scoring/field_differences.json)；[原始答案](runs/r-0ee77dc62ed5/answer.txt)；[原始工具记录](runs/r-0ee77dc62ed5/tool_events.jsonl)。差异记录数 0；类型 {}。
- confirmation_old_CG_1: [字段明细](runs/r-b90e2f062f85/scoring/field_differences.json)；[原始答案](runs/r-b90e2f062f85/answer.txt)；[原始工具记录](runs/r-b90e2f062f85/tool_events.jsonl)。差异记录数 0；类型 {}。
- confirmation_new_GO_1: [字段明细](runs/r-69914a9877c8/scoring/field_differences.json)；[原始答案](runs/r-69914a9877c8/answer.txt)；[原始工具记录](runs/r-69914a9877c8/tool_events.jsonl)。差异记录数 74；类型 {'missing_or_different': 74}。
- confirmation_old_GO_1: [字段明细](runs/r-d04075b89074/scoring/field_differences.json)；[原始答案](runs/r-d04075b89074/answer.txt)；[原始工具记录](runs/r-d04075b89074/tool_events.jsonl)。差异记录数 0；类型 {}。
- confirmation_new_CG_2: [字段明细](runs/r-92c02e2f6067/scoring/field_differences.json)；[原始答案](runs/r-92c02e2f6067/answer.txt)；[原始工具记录](runs/r-92c02e2f6067/tool_events.jsonl)。差异记录数 163；类型 {'missing_or_different': 55, 'unmatched_id': 54, 'omitted_row': 54}。
- confirmation_old_CG_2: [字段明细](runs/r-4a02a31cb8e8/scoring/field_differences.json)；[原始答案](runs/r-4a02a31cb8e8/answer.txt)；[原始工具记录](runs/r-4a02a31cb8e8/tool_events.jsonl)。差异记录数 0；类型 {}。
- confirmation_new_GO_2: [字段明细](runs/r-4df368e8ea7e/scoring/field_differences.json)；[原始答案](runs/r-4df368e8ea7e/answer.txt)；[原始工具记录](runs/r-4df368e8ea7e/tool_events.jsonl)。差异记录数 74；类型 {'missing_or_different': 74}。
- confirmation_old_GO_2: [字段明细](runs/r-d936d9895abf/scoring/field_differences.json)；[原始答案](runs/r-d936d9895abf/answer.txt)；[原始工具记录](runs/r-d936d9895abf/tool_events.jsonl)。差异记录数 0；类型 {}。
- confirmation_new_CG_3: [字段明细](runs/r-e5e848752431/scoring/field_differences.json)；[原始答案](runs/r-e5e848752431/answer.txt)；[原始工具记录](runs/r-e5e848752431/tool_events.jsonl)。差异记录数 0；类型 {}。
- confirmation_old_CG_3: [字段明细](runs/r-551a85fda485/scoring/field_differences.json)；[原始答案](runs/r-551a85fda485/answer.txt)；[原始工具记录](runs/r-551a85fda485/tool_events.jsonl)。差异记录数 0；类型 {}。
- confirmation_new_GO_3: [字段明细](runs/r-426fcaec1732/scoring/field_differences.json)；[原始答案](runs/r-426fcaec1732/answer.txt)；[原始工具记录](runs/r-426fcaec1732/tool_events.jsonl)。差异记录数 216；类型 {'omitted_row': 216}。
- confirmation_old_GO_3: [字段明细](runs/r-683967eda07e/scoring/field_differences.json)；[原始答案](runs/r-683967eda07e/answer.txt)；[原始工具记录](runs/r-683967eda07e/tool_events.jsonl)。差异记录数 0；类型 {}。
