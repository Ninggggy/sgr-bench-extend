import io,tarfile,tempfile,unittest
from pathlib import Path
from archive_io import extract_stream
class ArchiveTests(unittest.TestCase):
 def packed(self,entries):
  stream=io.BytesIO()
  with tarfile.open(fileobj=stream,mode='w') as arc:
   for name,data in entries:
    info=tarfile.TarInfo(name);info.size=len(data);arc.addfile(info,io.BytesIO(data))
  stream.seek(0);return stream
 def test_preserves_different_copies(self):
  with tempfile.TemporaryDirectory() as root:
   p=Path(root)
   extract_stream(self.packed([('downloaded_data/a.response',b'first')]),p,{'downloaded_data'})
   extract_stream(self.packed([('downloaded_data/a.response',b'second')]),p,{'downloaded_data'})
   self.assertEqual((p/'downloaded_data/a.response').read_bytes(),b'first')
   self.assertEqual((p/'recovered_after_interruption/downloaded_data/a.response').read_bytes(),b'second')
 def test_blocks_archive_escape(self):
  with tempfile.TemporaryDirectory() as root:
   for name in ['../outside','downloaded_data/../../outside','auth/secret']:
    with self.assertRaises(ValueError):extract_stream(self.packed([(name,b'x')]),root,{'downloaded_data'})
if __name__=='__main__':unittest.main()
