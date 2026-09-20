"""Independent inverse implementation using fold candidates and UTC round trips."""
from pathlib import Path
from zoneinfo import ZoneInfo
import datetime as dt, json, platform, shutil, subprocess, tempfile
import recompute as r

def run():
    checks=[]
    zones=[line.split('\t')[2] for line in (r.ROOT/'2024b_zone1970.tab').read_text().splitlines() if line and not line.startswith('#') and 'PT' in line.split('\t')[0].split(',')]
    with tempfile.TemporaryDirectory() as tmp:
        for v in ('2024a','2024b'):
            subprocess.run(['zic','-d',str(Path(tmp)/v),str(r.ROOT/f'{v}_europe')],check=True)
        for zone in zones:
            for v in ('2024a','2024b'):
                path=Path(tmp)/v/zone
                with path.open('rb') as f:z=ZoneInfo.from_file(f)
                seg=r.tzif(path)
                bounds={r.START,r.END}|{x for s in seg for x in s[:2]}
                points=sorted({b+d for b in bounds for d in (-1,0,1) if r.START<=b+d<r.END})
                for x in points:
                    local=r.EPOCH+dt.timedelta(seconds=x);actual=set()
                    for fold in (0,1):
                        aware=local.replace(tzinfo=z,fold=fold)
                        back=aware.astimezone(dt.timezone.utc).astimezone(z).replace(tzinfo=None)
                        if back==local:actual.add(int(aware.utcoffset().total_seconds()))
                    expected=set(r.offset_set(seg,x))
                    assert actual==expected,(v,zone,local,actual,expected)
                    checks.append({'release':v,'zone':zone,'local':local.isoformat(),'offsets':sorted(actual)})
    return {'checks_passed':len(checks),'python':platform.python_version(),'zic_path':shutil.which('zic'),'zic_version':subprocess.run(['zic','--version'],capture_output=True,text=True).stdout.strip(),'compile_options':'zic -d TEMP/RELEASE RELEASE_europe; no leap file; defaults otherwise','limitation':'Both inversion algorithms share compiled TZif semantics; manual source derivation is separate.','checks':checks}
if __name__=='__main__':print(json.dumps(run(),indent=2))
