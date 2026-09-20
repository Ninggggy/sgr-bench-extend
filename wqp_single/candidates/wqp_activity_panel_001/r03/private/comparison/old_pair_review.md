# 旧对照预先选择及语义核查

主对照：waterquality_004（在新候选任何求解/评分前指定）。同为TCEQ河流主干站点联合资格筛选；旧题输出3站×9列，侧重站点类别记录起讫时间。新候选拟研究活动层共同指标与可比采样条件。最终规模尚未确定。

waterquality_005-g的instruction引用“fixed nine-group order specified in the task”，但公开instruction/output_format并未列出九类或次序，也未说明River/Stream、湖库/出口排除等条件。其CG与GO不适合作同义题面对照；不修改原题，不把该歧义计作新题难度。

waterquality_004两种公开题面均给出六类、1993–2001及起年≤1993/止年≥2001；这是记录区间包络条件，官方页明确date ranges may contain gap years，不能解读为每年均有资料。私有rubric提到“best common start year”，公开题面未明确此排名；upper/middle/lower也未给出精确分段边界。故已可核验三个原oracle站点的字段，并不等于证明仅此三站符合公开语义。

官方网页工具返回三个站点：10924、10897、10892的HUC、六类起始年均与原oracle一致；common_start_year分别为六起年最大值。原始网页工具响应见old004_web_read.json；抓取标注依次为2个月、2周、3周前，不伪称三个页面均为当日源站快照。直接HTTP及站点候选枚举结果另存sources/；当前仍在取证。

评分使用原oracle、显式站点行键、整数年份、无事实修订。若不能解决唯一性问题，未来可报告相对原oracle的运行分数，不能解释为经完整语义验证的新旧能力差。
