#!/usr/bin/env python3
"""Recompute saved Sol results and checks offline; no model sessions or source fetches."""
import pathlib,subprocess,sys
T=pathlib.Path(__file__).resolve().parent
for name,args in [('analyze.py',['--verify']),('check_sources.py',[]),('check_panels.py',[]),('review_public_exposure.py',[]),('classify_exposure.py',[]),('tool_health.py',[]),('ranking_evidence.py',[]),('account.py',[]),('diagnose_first.py',[]),('diagnose_screening_go.py',[]),('diagnose_confirmation_cg2.py',[]),('diagnose_confirmation_go3.py',[]),('error_analysis.py',[]),('verify_delivery.py',[]),('write_report.py',[])]:
 r=subprocess.run([sys.executable,str(T/name),*args],capture_output=True,text=True)
 if r.returncode:sys.stderr.write(r.stdout+r.stderr);raise SystemExit(r.returncode)
 print(name+': passed',flush=True)
