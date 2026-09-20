"""Finish source checks and preregister the one-shot comparison, without invoking models."""
import datetime as dt, importlib.util, json, os, shutil, subprocess, sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
PHASE=BASE.parent
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
    assert not (BASE/'plan.json').exists(),'Do not change registration'
    reviews=json.loads((BASE/'reviews.json').read_text());pre=BASE/'source_checks/pre'
    # Exact main-text equality is evidence about these observations, not permanent stability.
    stapold=PHASE/'rolling_five/candidates/stap_replication_protocol_001/r01/post_development_a/raw'
    now=json.loads((pre/'stap_cohort.response').read_text());old=json.loads((stapold/'cohort.response').read_text())
    assert now['resultList']==old['resultList'] and now['hitCount']==old['hitCount']==49
    for p in pre.glob('stap_PMC*.response'):assert p.read_bytes()==(stapold/p.name.removeprefix('stap_')).read_bytes(),p
    assert len(list(pre.glob('stap_PMC*.response')))==16
    epold=PHASE/'research/europepmc_construct_interim_assets/downloaded_data'
    for p in pre.glob('reuse_d00*.response'):
        if p.name!='reuse_d0001.response':assert p.read_bytes()==(epold/p.name.removeprefix('reuse_')).read_bytes(),p
    eproot=PHASE/'candidates/europemc_reuse_deposit_001/r01';epdest=BASE/'candidates/europemc_reuse_deposit_001'
    for n in ['reference.py','candidate_pool.json']:shutil.copyfile(eproot/n,epdest/n)
    paths={p.stem.removeprefix('reuse_'):str(p) for p in pre.glob('reuse_*.response')}
    paths['d0232']=str(pre/'reuse_d0232.txt')
    paths['d0235']=str(PHASE/'research/europepmc_construct_interim_assets/text_review/review.json')
    put(epdest/'reference_paths.json',paths)
    r=subprocess.run([sys.executable,str(epdest/'reference.py'),str(pre),str(epdest/'reference_paths.json')],capture_output=True,text=True)
    (epdest/'reference.stdout').write_text(r.stdout);(epdest/'reference.stderr').write_text(r.stderr)
    assert r.returncode==0,r.stderr
    assert r.stdout==(epdest/'oracle.psv').read_text()
    for review in reviews:
        cid=review['candidate_id'];dest=BASE/'candidates'/cid
        if cid=='kegg_initial_cdx_001':
            review.update(status='blocked',reason='原题措辞和评分输出已修正，但本轮FDA关键历史文件返回HTTP 404的abuse-detection/excessive-requests拦截页；不换工具绕过。现有私有缓存不能替代盲解可达来源，因此本轮不测。')
            review['evidence_paths'] += [str(pre/'cdx_cap_ssed.response'),str(pre/'cdx_cap_label.response')]
        if cid=='genome_002':
            review.update(status='blocked',reason='已澄清专门图范围并修正标识/输出格式；普通GENOME记录和模块可读，但联合图入口（包括源页面真实链接及旧成功路径）现为HTTP 400。最后native web访问旧合法路径收到明确non-retryable拒绝，之后不重试或换表示。联合状态证据未能确认，不测。')
            review['evidence_paths'] += [str(pre/'genome_joint_known_route.json'),str(BASE/'access_blocks.json')]
        if cid=='europemc_reuse_deposit_001':
            review.update(status='ready',reason='完整10篇索引候选与原范围一致，9篇XML逐字相同，种子和大学公开稿可访问；从本轮原件及原语义注释重算得到同一答案。旧补充材料审查复用，不宣称重新独立语义审计。',legal_path='种子发现及公开数据说明<=3请求；ACCESSION_ID/FIRST_PDATE/OA普通20条搜索1请求；10篇原文<=12请求；相关补充文件按已有记录总计不超过36个，整体<=52。没有向盲解提供该路径或私有材料。',sgr='前步种子GEO身份决定专门字段索引查询；随后逐文区别矩阵复用、基因列表及新实验数据归属。')
            review['evidence_paths'] += [str(epdest/'reference.stdout'),str(epdest/'reference.stderr'),str(pre/'reuse_d0001.response'),str(eproot/'audit_decision.json')]
        if cid=='stap_replication_protocol_001':
            review.update(status='ready',reason='完整49条索引记录与原记录一致，16篇纳排/答案关键全文逐字相同，离线原参考程序重算3行一致。语义注释复用，不冒称人类复审。',legal_path='发现原始文章<=3请求；普通索引20条/页3页；最多49条身份摘要可在发现阶段筛选，原证据只需16篇全文；保留补充查询空间，总路径约22请求。原文逐篇取得，不全量导出全文。',sgr='原始实验文献身份决定CITES/OA索引状态；候选及实验描述决定后续全文和文章版本选择。')
            review['evidence_paths'] += [str(BASE/'reference_checks/stap/scope_checks.json'),str(pre/'stap_cohort.response'),str(PHASE/'rolling_five/candidates/stap_replication_protocol_001/r01/eligibility_annotations.json')]
        put(dest/'review.json',review)
    put(BASE/'reviews.json',reviews)
    put(BASE/'access_blocks.json',{'wateroffice':{'url':'https://wateroffice.ec.gc.ca/report/data_availability_e.html?type=historical&station=08EE004&parameter_type=Flow','result':'native web: not safe to open (non-retryable error)','action':'no retry, representation/tool switch or model trial for this task'},'genome':{'url':'https://www.kegg.jp/kegg-bin/show_organism?menu_type=pathway_maps&org=api+buc','sequence':'constructor curl HTTP400; native web later non-retryable denial; no requests after denial','action':'blocked'},'fda':{'result':'HTTP404 response bodies are abuse/excessive-requests apology pages for distinct original documents','action':'no re-fetch or alternate-tool bypass; task blocked'},'root_probe_note':'An initial guessed gn:T00013 URL resolved to Aquifex; it was discarded as unrelated evidence. The correct buc T00036 identity was obtained from its organism entry.'})
    now=dt.datetime.now(dt.timezone.utc);jobs=[]
    for review in reviews:
        if review['status']!='ready':continue
        for v in ['CG','GO']:
            cid=review['candidate_id'];dest=BASE/'candidates'/cid;label=f'{cid}-polish01-{v.lower()}-once';out=BASE/'runs'/label
            metadata={'candidate_id':cid,'revision':review['revision'],'protocol_version':'ten-task-v2-bounded-retrieval','stage':'comparison','variant':v,'trial':1,'run_id':label,'plan_path':str(BASE/'plan.json')}
            mp=dest/(v+'.job.json');put(mp,metadata)
            jobs.append({'public':str(dest/(v+'.json')),'gold':str(dest/'oracle.psv'),'rules':str(dest/'rules.json'),'stage':str(BASE/'blind.md'),'out':str(out),'label':label,'job_metadata':str(mp)})
    assert len(jobs)==4
    # New limited authorization; no old campaign/ledger is reset or resumed.
    previous=json.loads((PHASE/'rolling_five_campaign.json').read_text())
    assets={k:(str((PHASE/v).resolve()) if k.endswith('_path') else v) for k,v in previous['protocol_assets'].items()}
    campaign={'id':'revised12_20260917','authorization':'User explicitly implemented the 12-task revision + one CG/GO test plan; unrepairable/unreachable tasks are not tested. Global methodology/skills deferred.','started_at':now.isoformat(),'deadline':(now+dt.timedelta(hours=48)).isoformat(),'status':'active','max_sessions':1+len(jobs),'max_blind_sessions':len(jobs),'authorized_blind_ceiling':24,'session_ledger':'session_ledger.jsonl','max_seconds_per_session':6000,'stall_seconds':3000,'maximum_concurrent_model_sessions':4,'repair_retries_allowed':0,'reserved_pending_sessions':0,'current_date':'2026-09-09','protocol_version':'ten-task-v2-bounded-retrieval','protocol_assets':assets,'historical_campaign_preserved':str(PHASE/'rolling_five_campaign.json'),'historical_ledger_preserved':str(PHASE/'rolling_five_session_ledger.jsonl')}
    put(BASE/'campaign.json',campaign)
    (BASE/'session_ledger.jsonl').write_text(json.dumps({'session_number':1,'run_id':'controller-revision-and-review','status':'running','role':'controller','purpose':'construction_and_review','started_at':dt.datetime.fromtimestamp((BASE/'prepare.py').stat().st_birthtime,dt.timezone.utc).isoformat(),'start_time_scope':'first construction artifact write; earlier conversational/preparation time unknown','model':'host_controller_unverified','effort':'unknown','usage':None,'controller_pid':os.getpid(),'note':'Same active user task; no extra model invocation; no fabricated usage or recovery sessions.'})+'\n')
    put(BASE/'plan.json',{'registered_at':now.isoformat(),'deadline':campaign['deadline'],'campaign':str(BASE/'campaign.json'),'ledger':str(BASE/'session_ledger.jsonl'),'model':'gpt-5.6-sol','effort':'medium','role':'blind','purpose':'comparison','trials_per_variant':1,'workers':3,'selection':'All and only candidates with completed preflight; not selected using this batch scores. No retries or added sampling.','stage_change':'Removed obsolete unrestricted bulk permission; task citations use separate evidence field. Current v2 numeric limits, image, tools and shared scoring algorithm unchanged.','formal_admission':False,'jobs':jobs,'blocked':[r['candidate_id'] for r in reviews if r['status']=='blocked']})
    put(BASE/'preflight.json',{'checked_at':now.isoformat(),'ready':[r['candidate_id'] for r in reviews if r['status']=='ready'],'blocked':10,'paired_and_scoring_checks':'offline_checks.json','stap_fulltexts_unchanged':16,'stap_complete_cohort_unchanged':49,'epmc_fulltexts_byte_equal':9,'epmc_complete_cohort':10,'epmc_reference_recomputed':True,'human_expert_review':'not_performed','independent_model_audit':'not_run; this is authorized single-trial diagnosis, not formal admission','shared_scorer_modified':False})
    print('REGISTERED',len(jobs),'trials')
if __name__=='__main__':main()
