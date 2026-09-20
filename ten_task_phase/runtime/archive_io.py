"""Stream only explicitly selected session assets; preserve differing prior copies."""
import filecmp
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile


def extract_stream(stream, run, categories):
    run = Path(run)
    saved = []
    with tarfile.open(fileobj=stream, mode='r|') as archive:
        for member in archive:
            parts = Path(member.name).parts
            if not member.isfile() or len(parts) < 2 or parts[0] not in categories or '..' in parts or Path(member.name).is_absolute():
                raise ValueError('Unsafe session archive member')
            destination = run.joinpath(*parts)
            if not destination.resolve().is_relative_to(run.resolve()):
                raise ValueError('Archive destination escapes run')
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as target:
                staging = Path(target.name)
                with archive.extractfile(member) as source:
                    shutil.copyfileobj(source, target, length=1024 * 1024)
            if destination.exists():
                if filecmp.cmp(destination, staging, shallow=False):
                    staging.unlink()
                    saved.append(str(destination.relative_to(run)))
                    continue
                destination = run / 'recovered_after_interruption' / member.name
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    if filecmp.cmp(destination, staging, shallow=False):
                        staging.unlink()
                        saved.append(str(destination.relative_to(run)))
                        continue
                    raise ValueError('Conflicting recovery copy; original and staged files preserved')
            staging.replace(destination)
            saved.append(str(destination.relative_to(run)))
    return saved


def copy_session_assets(container, run, roots):
    script = """import pathlib,sys,tarfile,json
roots=json.loads(sys.argv[1])
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as out:
 for root,category in roots:
  p=pathlib.Path(root)
  for f in p.rglob('*') if p.exists() else []:
   if f.is_file() and not f.is_symlink():
    out.add(f,arcname=category+'/'+str(f.relative_to(p)),recursive=False)
"""
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(['docker', 'exec', container, 'python3', '-c', script, json.dumps(roots)], stdout=subprocess.PIPE, stderr=errors)
        try:
            saved = extract_stream(process.stdout, run, {category for _, category in roots})
            if process.wait(timeout=30):
                errors.seek(0)
                raise RuntimeError('Session archive failed: ' + errors.read().decode(errors='replace'))
            return saved
        except Exception:
            process.kill()
            process.wait()
            raise
