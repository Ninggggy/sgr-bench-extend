"""Refresh local partial-delivery report from existing runs; does not launch models."""
import json
from pathlib import Path
from fractions import Fraction
from account import account
from admission import export

P = Path(__file__).resolve().parents[1]

def refresh():
    summary = export(P / 'admission_manifest.json', P / 'exports')
    costs = account()
    campaign = json.loads((P / 'campaign.json').read_text())
    (P / 'run_accounting.json').write_text(json.dumps(costs, ensure_ascii=False, indent=2) + '\n')
    old = []
    for batch in sorted((P / 'comparisons').glob('*/batch.json')):
        rows = []
        for job in json.loads(batch.read_text())['jobs']:
            d = Path(job['out'])
            m = json.loads((d / 'run.json').read_text()) if (d / 'run.json').exists() else {}
            r = {'run_id': d.name, 'status': m.get('status', 'not_started'),
                 'variant': m.get('variant'), 'trial': m.get('trial')}
            score = d / 'controller_scoring/scores.json'
            if not score.exists():
                score = d / 'scoring_stdout.txt'
            if m.get('status') == 'completed' and score.exists():
                s = json.loads(score.read_text())
                if s.get('counts', {}).get('item_denominator'):
                    r['scores'] = s
                    r['item_f1_exact'] = str(Fraction(2 * s['counts']['correct_fields'], s['counts']['item_denominator']))
            rows.append(r)
        # An approved repaired slot remains a separate original failure record;
        # count its actual completed replacement once, never erase the failure.
        repaired = []
        saved_summary = batch.parent / 'results_summary.json'
        if saved_summary.exists():
            prior = json.loads(saved_summary.read_text())
            known = {r['run_id'] for r in rows}
            for r in prior.get('trials', []):
                actual = r.get('actual_run_id', r.get('run_id'))
                if actual and actual not in known and r.get('verification_status') == 'passed' and r.get('scores'):
                    repaired.append({**r, 'run_id': actual})
        old.append({'task_id': batch.parent.name, 'trials': rows, 'approved_completed_repairs': repaired,
                    'review_path': str((batch.parent / 'error_review.md').relative_to(P))})
    (P / 'comparisons/current_completion.json').write_text(json.dumps(old, ensure_ascii=False, indent=2))
    complete = sum('scores' in r for t in old for r in t['trials']) + sum(len(t['approved_completed_repairs']) for t in old)
    active = [r for r in costs['runs'] if r.get('status') in ['running', 'preparing']]
    text = ['# 新增 10 底题阶段：部分交付', '',
        f"更新：{costs['at']}。正式收录 **{summary['accepted_count']}/10** 个底题，缺口 **{10-summary['accepted_count']}** 个。", '',
        'JSONL 包含标准收录与用户指定例外收录。标准收录须质量审计通过且 CG、GO 各三次均分分别严格低于70%；WQP r03 与 arxiv_historical_title_002/r03 按2026-09-10用户明确指令计入，历史SGR、难度及完整标准判定保留，不冒称通过标准复测。尚未收齐十题。', '',
        '## 收录清单与复测', '',
        '| 底题版本 | CG 三次 Item-F1 | CG 均值 | GO 三次 Item-F1 | GO 均值 | 结论 |',
        '|---|---|---|---|---|---|']
    for r in summary['candidates']:
        if r['status'] == 'user_designated_exception' and not r['CG']['trials']:
            text.append('| ' + r['candidate_id'] + ' r' + str(r['revision']) + ' | 历史记录保留 | 不作标准复测均值 | 历史记录保留 | 不作标准复测均值 | 用户指定收录 |')
            continue
        groups = []
        for v in ['CG', 'GO']:
            vals = [t['Item-F1_exact'] for t in r[v]['trials']]
            vals += ['待完成/未验证'] * (3-len(vals))
            groups.extend([', '.join(vals), r[v].get('mean_exact', '不可判定')])
        text.append('| ' + ' | '.join([r['candidate_id'] + ' r' + str(r['revision']), *groups, r['status']]) + ' |')
    text += ['', '逐题六个 run_id、实际模型/档位、完整计分及内容、SGR、语义和两题面实质错误审计见 exports/admission_report.json。原始参考程序、证据和逐字段依据见 candidates，全部运行及失败尝试见 runs 和 session_ledger.jsonl。', '',
        '这些复测是用于收录的筛选成绩，不能冒称无偏独立评估、单题统计认证，或证明难于原全部五十题。没有人类专家验证。', '',
        '## 对照与候选进展', '',
        f'预选五道旧题共有 30 个预定槽，目前已有 {complete} 个有效成绩（包含 Reptile 原失败槽的一次事前允许修复，原失败和成本另行保留）。不能把失败槽补零。已完成组不得重跑。', '',
        'ChemExpo 的类别范围与数字格式、KEGG 的行键/路径标识、Reptile 的公开答案暴露和类型大小写、Water Office 的原答案排序冲突及 GO 条件遗漏、WQP 的站点选择不唯一分别记录于 comparisons 下各 error_review.md。旧题成绩不改变新题绝对门槛。', '',
        'NVD r01 两个初筛均满分，开发淘汰。Europe PMC Grubman r01 内容通过但实质错误受访问故障混淆，不收录；Lau 与 Reptile neotype 调查没有获得可确认的唯一答案，不冒建已验证题。Europe PMC BALF r01 已有完整14篇范围、三对参考答案及两套复算，但首次盲解被服务方安全检查中断，未返回数值分数；GO未启动，不补零或绕过拦截，仍未内容审计。', '',
        '## 成本与恢复', '',
        f"累计 {costs['model_work_sessions']}/300 次模型工作会话；阶段墙钟 {costs['wall_clock_seconds']/3600:.3f}/48 小时；剩余 {costs['remaining_sessions']} 次。金额不可得，记录 null；实际 token 用量和失败的最后可观察用量见 run_accounting.json，不以零替代。", '',
        '历史控制会话的超时记录保留于 research/controller_accounting_correction.json。用户于2026-09-10明确更新口径：6000秒会话上限和3000秒无实质进展上限继续适用于构造、审计、盲解等工作会话；总控按原300次/48小时阶段边界持续协调，原截止为2026-09-11T09:30:08Z。当前总控实际81号会话持续累计成本，上下文恢复不新建会话或重置用量。', '',
        '恢复先读 progress.md、campaign.json、analysis_plan 和真实 run.json/容器状态。普通测试计划和已有六槽收录轮不得重复登记、替换高分或对同版本重抽样。只按事前有限修复规则处理真实基础设施故障。不要重建已登记盲解镜像或重跑结束批次。', '',
        '当前账本显示仍在运行的会话：']
    text += ['- ' + str(r.get('label', r.get('thread_id', 'controller'))) for r in active]
    text += ['', '复算入口见 README.md 和 runtime/README_admission.md；report.py 仅重新生成本地报告、导出和成本清单，不启动任何模型或对外发布。']
    if campaign.get('termination_request'):
        stopped = bool(campaign.get('ended_at'))
        text[0] = '# SGR-Bench：r03 判定后停止' + ('（已停止）' if stopped else '（最终判定进行中）')
        text[2] = f"更新：{costs['at']}。当前保留 **{summary['accepted_count']} 个底题**，其中标准收录 {summary.get('standard_accepted_count', summary['accepted_count'])} 个、用户指定例外 {summary.get('user_designated_count', 0)} 个。"
        text[4] = text[4].replace('尚未收齐十题。', '原十题目标已由用户取消；保留历史目标与缺口，不宣称凑齐十题。')
        text += ['', '## 当前结束口径', '',
                 '用户要求只完成 arxiv_historical_title_002/r03 的最终测试、审计与收录判定，然后停止。其他候选和来源探索已终止；不新增 r04、不追加同版本抽样、不自动继续。', '',
                 '逐次测试、正式复测均值及最终审计见 [r03 最终判定](candidates/arxiv_historical_title_002/r03/FINAL_DECISION.md)。']
        if stopped:
            text = [line.replace('当前总控实际81号会话持续累计成本，上下文恢复不新建会话或重置用量。',
                                 '总控实际81号会话已结束，按真实连续时长记录成本；上下文恢复未新建会话或重置用量。')
                    for line in text]
            text = ['本阶段已按用户要求停止。以后可离线读取和复算现有产物；不得自动恢复构造、重新登记复测或重抽已测版本。新的模型工作需要用户另行提出任务。'
                    if line.startswith('恢复先读 progress.md') else line for line in text]
            if not active:
                text += ['', '所有相关模型工作与来源探测均已结束；账本无活跃会话。']
            text += ['', f"阶段停止时间：{campaign['ended_at']}。停止原因：{campaign.get('ending_reason', 'user_requested_stop_after_r03')}。"]
    (P / 'DELIVERY.md').write_text('\n'.join(text) + '\n')
    print(json.dumps({'accepted_count': summary['accepted_count'], 'old_direct_plan_completed': complete,
                      'sessions': costs['model_work_sessions'], 'report': str(P / 'DELIVERY.md')}))

if __name__ == '__main__':
    refresh()
