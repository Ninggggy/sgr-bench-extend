"""Derive symbolic byte writes from the tagged assembly, not from answer rows.

The source-specific extractor handles the instructions needed for stack
arithmetic and saves. Semantic branch choices are manually verified from source.
It records every saved integer-register byte before the FPU writes, then reports
intersections. VPU writes are expanded as four whole-register groups and CSRs.
This is not a general preprocessor or RISC-V interpreter. Width definitions,
non-E selection, FS/VS conditions, and saved-pointer endpoint are manually
checked in reference.md; unexpected relevant source changes require re-review.
"""
from pathlib import Path
import re, json

ROOT = Path(__file__).parent
SRC = (ROOT/'portContext.h').read_text()
EXT = (ROOT/'freertos_risc_v_chip_specific_extensions.h').read_text()

def body(name):
    return re.search(r'\.macro\s+'+re.escape(name)+r'\b(.*?)\.endm',SRC,re.S).group(1)

def calc(expr, env):
    expr = re.sub(r'/\*.*?\*/', '', expr)
    for name in sorted(env, key=len, reverse=True):
        expr = re.sub(r'\b'+re.escape(name)+r'\b',str(env[name]),expr)
    if re.search(r'[^\d\s()+*/-]',expr):
        raise ValueError(expr)
    return int(eval(expr, {'__builtins__':{}}, {}))

def define(name):
    return re.search(r'^\s*#define\s+'+name+r'\s+([^\n]+)',SRC,re.M).group(1)

def derive(xlen, flen, vs):
    env={'__riscv_flen':flen,'portWORD_SIZE':xlen//8}
    for n in ['portFPU_REG_SIZE','portFPU_REG_COUNT','portFPU_CONTEXT_SIZE']:
        env[n]=calc(define(n),env)
    core_values=re.findall(r'#define\s+portCONTEXT_SIZE\s+([^\n]+)',SRC)
    # __riscv_32e is explicitly absent in the scoped configurations.
    core=calc(core_values[1],env)
    core_sp=-core
    core_slots=[]
    for r,expr in re.findall(r'store_x\s+(x\d+),\s*(.*?)\(\s*sp\s*\)',body('portcontextSAVE_CONTEXT_INTERNAL')):
        a=core_sp+calc(expr,env);core_slots.append((r,a,a+xlen//8))
    ra=next(a for r,a,b in core_slots if r=='x1')
    sp=core_sp
    fpu=body('portcontexSAVE_FPU_CONTEXT')
    moves=re.findall(r'addi\s+sp,\s*sp,\s*([^\n]+)',fpu)
    assert len(moves)==1
    sp+=calc(moves[0],env)
    offset_expr=re.search(r'#define\s+portFPU_REG_OFFSET\(\s*regIndex\s*\)\s*([^\n]+)',SRC).group(1)
    writes=[]
    for kind,reg,index in re.findall(r'(store_[fx])\s+(\w+),\s*portFPU_REG_OFFSET\(\s*(\d+)\s*\)',fpu):
        a=sp+calc(offset_expr,dict(env,regIndex=int(index)))
        writes.append((reg,a,a+(flen//8 if kind=='store_f' else xlen//8)))
    assert len(writes)==33
    f0=next(a for r,a,b in writes if r=='f0')
    fcsr=next((a,b) for r,a,b in writes if r=='t0')
    intersections=[]
    for name,a,b in core_slots:
        for wr,c,d in writes:
            lo,hi=max(a,c),min(b,d)
            if lo<hi:intersections.append({'integer_register':name,'writer':wr,'start':lo,'end':hi})
    v0=None
    later_writes=[]
    if vs=='Dirty':
        t0=None
        for line in body('portcontexSAVE_VPU_CONTEXT').splitlines():
            line=line.split('/*')[0].strip()
            if line.startswith('csrr t0, vlenb'):t0=16
            elif line.startswith('slli t0, t0,'):t0 <<= int(line.rsplit(',',1)[1])
            elif re.match(r'neg\s+t0,\s*t0',line):t0=-t0
            elif re.match(r'addi?\s+sp,\s*sp,',line):
                expr=line.split(',',2)[2].strip();sp+=t0 if expr=='t0' else calc(expr,env)
            elif re.match(r'vs8r\.v\s+v\d+,',line):
                reg=re.search(r'vs8r\.v\s+(v\d+)',line)[1]
                later_writes.append((reg,sp,sp+8*16))
                if reg=='v0':v0=sp
            elif re.match(r'store_x\s+t0,',line):
                expr=re.search(r'store_x\s+t0,\s*(.*?)\(\s*sp\s*\)',line)[1]
                a=sp+calc(expr,env);later_writes.append(('vector_csr',a,a+xlen//8))
        assert v0 is not None
        assert len(later_writes)==8
    assert re.search(r'#define\s+portasmADDITIONAL_CONTEXT_SIZE\s+0',EXT)
    assert re.search(r'\.macro\s+portasmSAVE_ADDITIONAL_REGISTERS\s*\.endm',re.sub(r'/\*.*?\*/','',EXT,flags=re.S),re.S)
    # mstatus/epc are written in the reserved header after optional banks.
    # Their slots do not intersect the earlier general-register slots.
    assert all(not(max(a,sp)<min(b,sp+2*env['portWORD_SIZE'])) for _,a,b in core_slots)
    later_writes.extend([('mstatus',sp+xlen//8,sp+2*xlen//8),('mepc',sp,sp+xlen//8)])
    for name,a,b in core_slots:
        for wr,c,d in later_writes:
            lo,hi=max(a,c),min(b,d)
            if lo<hi:intersections.append({'integer_register':name,'writer':wr,'start':lo,'end':hi})
    row=[f'RV{xlen}F{flen}',vs,str(-sp),str(ra-sp),str(f0-sp),f'[{fcsr[0]-sp},{fcsr[1]-sp})',str(v0-sp) if v0 is not None else 'NONE',
         ';'.join(f"{i['integer_register']}:[{i['start']-sp},{i['end']-sp})" for i in intersections) or 'NONE']
    return {'row':row,'word_bytes':xlen//8,'float_bytes':flen//8,'core_allocation':core,'fpu_allocation':env['portFPU_CONTEXT_SIZE'],'sp_from_entry':sp,'core_slots':core_slots,'fpu_writes':writes,'later_writes':later_writes,'overwrites':intersections}

if __name__=='__main__':
    derived=[derive(x,f,v) for x in (32,64) for f in (32,64) for v in ('Clean','Dirty')]
    cols=['configuration','VS','frame_bytes','ra_offset','f0_offset','fcsr_range','v0_offset','overwritten_integer_bytes']
    (ROOT/'derived.json').write_text(json.dumps(derived,indent=2)+'\n')
    (ROOT/'oracle.psv').write_text(' | '.join(cols)+'\n'+'\n'.join(' | '.join(x['row']) for x in derived)+'\n')
    print((ROOT/'oracle.psv').read_text())
