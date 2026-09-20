"""Derive exact inverse-local-time differences from two original tzdb sources.

No expected answer is input. zic compiles source; TZif transitions partition UTC;
their affine local images partition wall time. Overlapping images are folds;
uncovered images are gaps. Only offset sets affect local->UTC interpretation.
"""
from pathlib import Path
import datetime as dt
import json
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
EPOCH = dt.datetime(1970, 1, 1)
START = int((dt.datetime(1992, 1, 1)-EPOCH).total_seconds())
END = int((dt.datetime(1994, 1, 1)-EPOCH).total_seconds())

def tzif(path):
    data = path.read_bytes()
    def header(pos):
        assert data[pos:pos+4] == b'TZif'
        return struct.unpack_from('>6I', data, pos+20)
    counts = header(0)
    width, pos = 4, 44
    if data[4:5] in (b'2', b'3', b'4'):
        g,s,l,t,y,c = counts
        pos += t*5+y*6+c+l*8+s+g
        counts = header(pos)
        pos += 44
        width = 8
    g,s,l,t,y,c = counts
    transitions = struct.unpack_from('>'+('q' if width == 8 else 'i')*t,data,pos)
    pos += width*t
    indices = data[pos:pos+t]
    pos += t
    types = [struct.unpack_from('>lBB',data,pos+6*i) for i in range(y)]
    # Restrict to explicitly represented historical transitions; no footer needed.
    assert transitions[0] < START-86400 and transitions[-1] > END+86400
    segments=[]
    for a,b,k in zip(transitions,transitions[1:],indices):
        off=types[k][0]
        left,right=max(START,a+off),min(END,b+off)
        if left<right: segments.append((left,right,off))
    return segments

def offset_set(segments, instant):
    return tuple(sorted({off for a,b,off in segments if a<=instant<b}))

def label(seconds):
    return (EPOCH+dt.timedelta(seconds=seconds)).isoformat(timespec='seconds')

def run():
    zones=[]
    for line in (ROOT/'2024b_zone1970.tab').read_text().splitlines():
        if not line or line.startswith('#'):continue
        fields=line.split('\t')
        if 'PT' in fields[0].split(','):zones.append(fields[2])
    rows=[]; candidates=[]
    with tempfile.TemporaryDirectory() as temp:
        for version in ('2024a','2024b'):
            subprocess.run(['zic','-d',str(Path(temp)/version),str(ROOT/f'{version}_europe')],check=True)
        for zone in zones:
            old,new=[tzif(Path(temp)/v/zone) for v in ('2024a','2024b')]
            bounds=sorted({START,END}|{x for seg in old+new for x in seg[:2]})
            changed=[]
            for a,b in zip(bounds,bounds[1:]):
                before,after=offset_set(old,a),offset_set(new,a)
                if before==after:continue
                if changed and changed[-1][1]==a and changed[-1][2:]==[before,after]:
                    changed[-1][1]=b
                else:changed.append([a,b,before,after])
            candidates.append({'zone':zone,'included':bool(changed),'interval_count':len(changed),
                'checked_local_cells':len(bounds)-1,
                'reason':'inverse offset sets differ' if changed else 'all local cells have equal inverse offset sets'})
            for a,b,old_set,new_set in changed:
                rows.append({'zone':zone,'start':label(a),'end':label(b),
                    'old_offsets_seconds':list(old_set),'new_offsets_seconds':list(new_set)})
    rows.sort(key=lambda row:(row['zone'],row['start']))
    return {'source_versions':['2024a','2024b'],'local_range':[label(START),label(END)],
            'candidates':candidates,'rows':rows}

if __name__=='__main__':print(json.dumps(run(),indent=2))
