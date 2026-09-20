"""Fixed LDAP caseIgnoreSubstringsMatch fixture interpreter.
Tables extracted from RFC3454; Unicode3.2 library handles NFKC.
Space/combining predicates implement RFC4518 and verified1757/1758.
"""
from pathlib import Path
import json,re,unicodedata
P=Path(__file__).parent
U=unicodedata.ucd_3_2_0
src=(P/'rfc3454.txt').read_text()
def table(name):return src.split('----- Start Table '+name+' -----')[1].split('----- End Table '+name+' -----')[0]
fold={chr(int(m[1],16)):''.join(chr(int(x,16)) for x in m[2].split()) for m in re.finditer(r'^\s+([0-9A-F]+); ([0-9A-F ]+);',table('B.2'),re.M)}
def ranges(s):
 out=[]
 for part in re.findall(r'\b[0-9A-F]{4,6}(?:-[0-9A-F]{4,6})?\b',s):
  a,*b=part.split('-');out.append((int(a,16),int(b[0],16) if b else int(a,16)))
 return out
def inranges(c,rs):return any(a<=ord(c)<=b for a,b in rs)
prohibited={n:ranges(' '.join(re.findall(r'^\s+([0-9A-F]{4,6}(?:-[0-9A-F]{4,6})?)(?:;|\s*$)',table(n),re.M))) for n in ['A.1','C.8','C.3','C.4','C.5']}
# Explicit map tables copied from RFC4518 2.2; FE00 correction verified860.
nothing=ranges('00AD 1806 034F 180B-180D FE00-FE0F FFFC 0000-0008 000E-001F 007F-0084 0086-009F 06DD 070F 180E 200C-200F 202A-202E 2060-2063 206A-206F FEFF FFF9-FFFB 1D173-1D17A E0001 E0020-E007F 200B')
spaces=ranges('0009-000D 0085 0020 00A0 1680 2000-200A 2028-2029 202F 205F 3000')
combining_text=(P/'rfc4518.txt').read_text().split('Appendix A.  Combining Marks')[1].split('Appendix B.')[0]
marks=ranges(' '.join(line for line in combining_text.splitlines() if re.fullmatch(r'[ 0-9A-F-]+',line) and re.search(r'[0-9A-F]{4}',line)))
def hx(s):return 'FAIL' if s is None else ' '.join(f'U+{ord(c):04X}' for c in s) or 'EMPTY'
def segments(s):
 # A U+0020 followed by a combining mark is a non-space token.
 out=[]
 for i,c in enumerate(s):
  space=c==' ' and (i+1==len(s) or not inranges(s[i+1],marks))
  if out and out[-1][0]==space:out[-1]=(space,out[-1][1]+c)
  else:out.append((space,c))
 return out
def prepare(s,role):
 mapped=''.join('' if inranges(c,nothing) else ' ' if inranges(c,spaces) else c for c in s)
 mapped=''.join(fold.get(c,c) for c in mapped);norm=U.normalize('NFKC',mapped)
 failures=[{'cp':hx(c),'table':name} for c in norm for name,rs in prohibited.items() if inranges(c,rs)]
 if '\ufffd' in norm:failures.append({'cp':'U+FFFD','table':'RFC4518 replacement character'})
 if failures:return None,{'mapped':hx(mapped),'normalized':hx(norm),'failures':failures}
 seg=segments(norm)
 if not any(not k for k,v in seg):out='  ' if role=='attribute' else ' '
 else:
  # All inner nonempty insignificant-space runs become two spaces.
  for i,(k,v) in enumerate(seg):
   if k and i>0 and i<len(seg)-1:seg[i]=(k,'  ')
  if role in ['attribute','initial']:
   if seg[0][0]:seg[0]=(True,' ')
   else:seg.insert(0,(True,' '))
  elif seg[0][0]:seg[0]=(True,' ')
  if role in ['attribute','final']:
   if seg[-1][0]:seg[-1]=(True,' ')
   else:seg.append((True,' '))
  elif seg[-1][0]:seg[-1]=(True,' ')
  out=''.join(v for k,v in seg)
 return out,{'mapped':hx(mapped),'normalized':hx(norm),'prepared':hx(out)}
def compute():
 rows=[];trace=[]
 for f in json.loads((P/'inputs.json').read_text()):
  pp={};tt={}
  for role in ['attribute','initial','any','final']:pp[role],tt[role]=prepare(f[role],role)
  if any(v is None for v in pp.values()):result='UNDEFINED'
  else:
   a,i,m,z=[pp[k] for k in ['attribute','initial','any','final']]
   # Initial and final occupy anchored disjoint regions; any must fit between.
   result='TRUE' if a.startswith(i) and a.endswith(z) and len(i)+len(z)<=len(a) and a.find(m,len(i),len(a)-len(z))>=0 else 'FALSE'
  rows.append([f['id']]+[hx(pp[k]) for k in ['attribute','initial','any','final']]+[result]);trace.append({'id':f['id'],'stages':tt,'result':result})
 return rows,trace
if __name__=='__main__':
 rows,trace=compute();(P/'derived.json').write_text(json.dumps(trace,indent=2)+'\n');(P/'oracle.psv').write_text('case | attribute_prepared | initial_prepared | any_prepared | final_prepared | result\n'+'\n'.join(' | '.join(r) for r in rows)+'\n');print((P/'oracle.psv').read_text())
