#!/usr/bin/env python3
"""Run the existing fixed plan with a bounded pool, without retries or overwrites."""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
import time

B = Path(__file__).resolve().parent


def emit(**entry):
    print(json.dumps(dict(at=dt.datetime.now(dt.timezone.utc).isoformat(), **entry)), flush=True)


def read_meta(out):
    try:
        return json.loads((out / 'run.json').read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def execute(job):
    out = Path(job['out'])
    if out.exists():
        emit(observing_existing=job['label'], run=str(out))
        deadline = dt.datetime.fromisoformat(json.loads((B.parent / 'campaign.json').read_text())['deadline'])
        while True:
            meta = read_meta(out)
            if meta and meta['status'] not in ('preparing', 'running'):
                break
            if dt.datetime.now(dt.timezone.utc) >= deadline:
                raise RuntimeError('Campaign deadline reached while observing existing attempt')
            time.sleep(5)
        rc = 0
    else:
        args = [sys.executable, str(B / 'run.py'), '--public', job['public'],
                '--stage', job['stage'], '--out', str(out), '--label', job['label']]
        for key in ('gold', 'rules', 'schema', 'assets'):
            if job.get(key):
                args += ['--' + key, job[key]]
        log = out.parent / (out.name + '.controller.log')
        log.parent.mkdir(parents=True, exist_ok=True)
        emit(started=job['label'], run=str(out))
        with log.open('x') as stream:
            rc = subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT).returncode
        meta = read_meta(out) or {'status': 'controller_did_not_start'}
    emit(finished=job['label'], status=meta['status'], elapsed_seconds=meta.get('elapsed_seconds'))
    if rc or meta['status'] in ('environment_error', 'runtime_error', 'controller_did_not_start'):
        raise RuntimeError(f"{job['label']}: {meta['status']}; preserve attempt, no automatic retry")
    return meta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--workers', type=int, choices=(2, 4), default=2)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    jobs = plan['jobs']
    # Content solves precede shortcut attempts; comparison jobs retain their existing order.
    if any('_shortcut_' in j['label'] for j in jobs):
        groups = [[j for j in jobs if '_shortcut_' not in j['label']],
                  [j for j in jobs if '_shortcut_' in j['label']]]
    else:
        groups = [jobs]
    for group in groups:
        queue = iter(group)
        with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
            active = {}
            for job in list(next(queue, None) for _ in range(args.workers)):
                if job is not None:
                    active[pool.submit(execute, job)] = job
            while active:
                finished, _ = cf.wait(active, return_when=cf.FIRST_COMPLETED)
                for future in finished:
                    future.result()
                    del active[future]
                for _ in finished:
                    job = next(queue, None)
                    if job is not None:
                        active[pool.submit(execute, job)] = job
    emit(plan_completed=str(args.plan), extra_attempts=0)


if __name__ == '__main__':
    main()
