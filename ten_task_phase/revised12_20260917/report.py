"""Read-only analysis of completed trials; write batch reports, never rescore or invoke models."""
import csv, datetime as dt, json
from fractions import Fraction
from pathlib import Path
BASE=Path(__file__).resolve().parent
def load(p,default=None):return json.loads(p.read_text()) if p.exists() else default
def aggregate(rows):
    scored=[x for x in rows if x.get('item_f1_exact') is not None]
    mean=sum((Fraction(x['item_f1_exact']) for x in scored),Fraction())/len(scored) if scored else None
    full=sum(x['whole_task_correct'] for x in scored)
    return {'trials':len(rows),'scored':len(scored),'NA':len(rows)-len(scored),'macro_item_f1_exact':str(mean) if mean is not None else None,'macro_item_f1_percent':float(mean*100) if mean is not None else None,'whole_task_correct':full,'whole_task_accuracy_percent':100*full/len(scored) if scored else None}
def main():
    plan=load(BASE/'plan.json');reviews=load(BASE/'reviews.json');rows=[];metas=[]
    for j in plan['jobs']:
        d=Path(j['out']);job=load(Path(j['job_metadata']));m=load(d/'run.json',{});metas.append(m)
        s=load(d/'scoring/scores.json',{});a=load(d/'retrieval_review.json',{});answer=load(d/'solver_output/result.json',{});c=s.get('counts',{});metrics=s.get('metrics') or {}
        valid=isinstance(metrics.get('Item-F1'),(int,float)) and isinstance(c.get('correct_fields'),int) and isinstance(c.get('item_denominator'),int) and c['item_denominator']>0
        value=Fraction(2*c['correct_fields'],c['item_denominator']) if valid else None
        r={'candidate_id':job['candidate_id'],'revision':job['revision'],'variant':job['variant'],'trial':1,'stage':'single_trial_comparison','run_id':job['run_id'],'status':m.get('status','not_started'),'model':m.get('actual_model'),'effort':m.get('actual_effort'),'model_verification':m.get('verification_status'),'item_f1_exact':str(value) if value is not None else None,'item_f1_percent':float(100*value) if value is not None else None,'row_f1':metrics.get('Row-F1'),'whole_task_correct':value==1 and metrics.get('Row-F1')==1 if value is not None else None,'retrieval_compliance':a.get('verdict','pending'),'external_requests':a.get('external_requests'),'access_confounded':a.get('access_confounded'),'capability_score_eligible':a.get('capability_score_eligible',False),'answer_status':answer.get('status'),'limitations':answer.get('limitations',[]),'review_notes':a.get('limitations'),'score_status':s.get('status'),'counts':c,'elapsed_seconds':m.get('elapsed_seconds'),'usage':m.get('usage'),'run_dir':str(d)}
        rows.append(r)
    summaries={}
    for v in ['CG','GO']:
        rr=[r for r in rows if r['variant']==v]
        compliant=[r for r in rr if r['retrieval_compliance']=='passed' and r['model_verification']=='passed' and r['model']=='gpt-5.6-sol' and r['effort']=='medium']
        clean=[r for r in compliant if r['capability_score_eligible']]
        summaries[v]={'raw':aggregate(rr),'compliant':aggregate(compliant),'compliant_without_known_confounds':aggregate(clean)}
    costs={}
    for field in ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens','cache_write_input_tokens']:
        values=[m['usage'][field] for m in metas if isinstance(m.get('usage'),dict) and isinstance(m['usage'].get(field),(int,float))]
        costs[field]=sum(values) if values else None;costs[field+'_known_sessions']=len(values)
    starts=[dt.datetime.fromisoformat(m['started_at']) for m in metas if m.get('started_at')];ends=[dt.datetime.fromisoformat(m['ended_at']) for m in metas if m.get('ended_at')]
    costs.update({'planned_blind_trials':len(rows),'started_blind_trials':len(starts),'completed_blind_trials':sum(m.get('status')=='completed' for m in metas),'sum_worker_seconds':sum(m.get('elapsed_seconds') or 0 for m in metas),'blind_wall_seconds':(max(ends)-min(starts)).total_seconds() if len(ends)==len(rows) and starts else None,'controller_tokens':None,'controller_cost':'unknown; same host conversation, no fabricated model/session accounting','currency_cost':None,'note':'Cached input is included in input; worker durations are not wall time. Shared account quota change is not attributed to this batch.'})
    under=[];cleanunder=[]
    for review in reviews:
        rr=[r for r in rows if r['candidate_id']==review['candidate_id']]
        if len(rr)==2 and all(r['item_f1_exact'] is not None and Fraction(r['item_f1_exact'])<Fraction(7,10) for r in rr):
            under.append(review['candidate_id'])
            if all(r['retrieval_compliance']=='passed' and r['capability_score_eligible'] and r['model_verification']=='passed' for r in rr):cleanunder.append(review['candidate_id'])
    result={'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'phase':'diagnostic_single_trial','selected_bases':12,'tested_bases':len(plan['jobs'])//2,'blocked':plan['blocked'],'results':rows,'summary':summaries,'cost':costs,'raw_both_below_70':under,'unconfounded_compliant_both_below_70':cleanunder,'formal_admissions':0,'formal_admission_note':'One fresh ordinary trial per face only; not the required three-trial-per-face admission round. No historical admission records changed.'}
    result['repair_followup']={r['candidate_id']:r['followup_20260917'] for r in reviews if r.get('followup_20260917')}
    result['delivery_status']='partial_pending_repairs' if any(r['status']=='blocked' for r in reviews) else 'single_trial_batch_reported'
    (BASE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    keys=['candidate_id','revision','variant','trial','stage','status','model','effort','model_verification','item_f1_exact','item_f1_percent','row_f1','whole_task_correct','retrieval_compliance','external_requests','access_confounded','capability_score_eligible','elapsed_seconds','run_id']
    with (BASE/'scores.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    def pct(x):return 'NA' if x is None else f'{x:.2f}%'
    lines=['# 12题修订与单轮盲测','',f'更新时间：{result["generated_at"]}','',f'12题均保存修订副本；{len(plan["jobs"])//2}题通过本轮测前检查，CG/GO各一次，共{len(rows)}个登记试次。其余题的具体阻塞见下表。没有恢复旧构造总控，没有改动全局方法文档或skill。','', '## 每题结果','', '| 题目 | 本轮状态 | CG Item-F1 / Row-F1 | GO Item-F1 / Row-F1 | 获取合规 CG / GO |','|---|---|---:|---:|---|']
    for review in reviews:
        rr={r['variant']:r for r in rows if r['candidate_id']==review['candidate_id']}
        def show(v):
            r=rr.get(v)
            return '未测' if not r else pct(r['item_f1_percent'])+' / '+pct(100*r['row_f1'] if r['row_f1'] is not None else None)
        lines.append(f'| {review["candidate_id"]} | {"暂缓" if review["status"]=="blocked" else "已登记单轮"} | {show("CG")} | {show("GO")} | {rr.get("CG",{}).get("retrieval_compliance","—")} / {rr.get("GO",{}).get("retrieval_compliance","—")} |')
    lines+=['','## 暂缓原因','']
    for r in reviews:
        if r['status']=='blocked':lines.append(f'- **{r["candidate_id"]}**：{r["reason"]}')
    if result['repair_followup']:
        lines+=['','## 暂缓题后续修复（以上原测前记录保留）','','本轮仍为部分交付。下列新核对不等于测试通过；没有新增盲测试次。完整记录见 [暂缓题处理报告](blocked_followup/report.md)。范围调整和公开择优规则尚待用户确认，已知访问拒绝未重试。','']
        for cid,note in result['repair_followup'].items():
            lines.append(f'- **{cid}**：{note.get("finding",note.get("reason","见逐题审查"))}')
    lines+=['','## 汇总口径','', '| 题面 | 原始宏平均 Item-F1 | 原始整题全对率 | 有效评分/登记 | 合规宏平均 Item-F1 | 合规有效评分数 |','|---|---:|---:|---:|---:|---:|']
    for v,s in summaries.items():
        a=s['raw'];c=s['compliant'];lines.append(f'| {v} | {pct(a["macro_item_f1_percent"])} | {pct(a["whole_task_accuracy_percent"])} | {a["scored"]}/{a["trials"]} | {pct(c["macro_item_f1_percent"])} | {c["scored"]} |')
    lines+=['','| 题面 | 已运行 | 数值评分 | NA | 获取合规会话 | 合规且无已知混淆的数值评分 |','|---|---:|---:|---:|---:|---:|']
    for v,s in summaries.items():
        lines.append(f'| {v} | {s["raw"]["trials"]} | {s["raw"]["scored"]} | {s["raw"]["NA"]} | {s["compliant"]["trials"]} | {s["compliant_without_known_confounds"]["scored"]} |')
    lines+=['','未启动的暂缓题不计入 NA、有效评分数或上述均值分母。构造端来源核查不是新的盲测；没有新增盲测成本，总控核查 token/费用未知。']
    lines+=['','整题全对要求Item-F1和Row-F1都等于1。NA、解析失败和缺失结果不补零。原始分数只是与登记参考的确定性比较；访问失败所伴随的数字低分不能解释为能力零分。合规子集存在选择偏差，不代表全部12题。','',f'原始双面单次分数均低于70%：{", ".join(under) or "无"}。',f'同时获取合规且未发现能力解释混淆的双面低于70%候选：{", ".join(cleanunder) or "无"}。','', '本轮不是正式收录复测，不能据此判断双面各三次均值；历史标准收录和用户指定收录均保持原状。','', '## 逐次诊断','']
    for r in rows:lines.append(f'- **{r["run_id"]}**：{r["model"]}/{r["effort"]}，模型核验 {r["model_verification"]}；{r["review_notes"] or "轨迹审核尚未完成"}')
    lines+=['','## 成本','', '```json',json.dumps(costs,ensure_ascii=False,indent=2),'```','', '## 文件与复算','', '- `candidates/<id>/CG.json`、`GO.json`：修订题面；`*_historical.json`：原题。', '- `review.json`：变更、受阻原因和证据路径；`historical_oracle.psv`与`oracle.psv`分别保留历史与本轮参考。受阻题参考不代表质量通过。', '- `plan.json`、`campaign.json`、`session_ledger.jsonl`：事前登记与独立批次用量；原阶段账本未重置。', '- `runs/<run>/answer.txt`、`scoring/`、`tool_events.jsonl`、`retrieval_review.json`：原始回答、评分、实际工具轨迹及审查。', '- `source_checks/`：仅构造者可见的源复核；从未送入盲解容器。', '- `offline_checks.json`：配对条件和机械评分检查；不冒称独立语义审核。', '- `python3 report.py`：从现有运行与审查重新生成汇总，不运行模型、不重新评分。', '- 逐次评分可用原 `runtime/score.py --answer runs/<run>/answer.txt --gold candidates/<id>/oracle.psv --rules candidates/<id>/rules.json --out <新目录>` 离线复算。','', '没有新增正式收录，没有自动继续任务。']
    (BASE/'report.md').write_text('\n'.join(lines)+'\n')
    draft=['# 修订题面（含受阻草稿）','', '测试资格以review.json为准；本文件不代表全部题目已完成质量修复。']
    for review in reviews:
        draft+=['',f'## {review["candidate_id"]} / polish01', '',f'状态：{review["status"]}；{review["reason"]}']
        for v in ['CG','GO']:
            public=load(BASE/'candidates'/review['candidate_id']/(v+'.json'));draft+=['',f'### {v}','',public['instruction'],'',public['output_format']]
    (BASE/'questions.md').write_text('\n'.join(draft)+'\n')
    for v in ['CG','GO']:
        with (BASE/(v+'.revision_drafts.jsonl')).open('w') as f:
            for r in reviews:f.write(json.dumps({'candidate_id':r['candidate_id'],'revision':r['revision'],'status':r['status'],'public':load(BASE/'candidates'/r['candidate_id']/(v+'.json'))},ensure_ascii=False)+'\n')
    print(json.dumps({'trials':len(rows),'scored':sum(r['item_f1_exact'] is not None for r in rows),'summaries':summaries},ensure_ascii=False))
if __name__=='__main__':main()
