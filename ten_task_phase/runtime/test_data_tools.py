import tempfile,unittest,pathlib
import data_tools as d
class ToolTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();d.DATA=pathlib.Path(self.tmp.name);d.REG.clear()
 def tearDown(self):self.tmp.cleanup()
 def test_numeric_roundtrip(self):
  f=d.register(b'id,value\na,10\nb,2\nc,9\n','.csv',{})
  r=d.query({'tables':{'x':f},'sql':'select id, CAST(value AS REAL) as value from x order by CAST(value AS REAL)'})
  self.assertEqual([x[0] for x in r['rows']],['b','c','a'])
  r2=d.query({'tables':{'x':r['file_id']},'sql':'select id from x order by CAST(value AS REAL)'})
  self.assertEqual([list(r) for r in r2['rows']],[['b'],['c'],['a']])
 def test_json_tsv(self):
  f=d.register(b'{"rows":[{"x":"a","v":10},{"x":"b","v":2}]}','.json',{})
  t=d.tabulate({'file_id':f,'format':'json','json_path':['rows']})
  self.assertEqual(t['columns'],['x','v']);self.assertEqual(t['total_rows'],2)
  f=d.register(b'a\t1\nb\t2\n','.txt',{})
  t=d.tabulate({'file_id':f,'format':'tsv','columns':['id','n']});self.assertEqual(t['rows'],[['a','1'],['b','2']])
 def test_xlsx_shared_and_sparse(self):
  import io,zipfile
  f=io.BytesIO()
  with zipfile.ZipFile(f,'w') as z:
   z.writestr('xl/sharedStrings.xml','<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>name</t></si><si><t>amount</t></si><si><t>sample</t></si></sst>')
   z.writestr('xl/worksheets/sheet1.xml','<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row><row><c r="A2" t="s"><v>2</v></c><c r="B2"><v>12.5</v></c></row><row><c r="B3"><v>0</v></c></row></sheetData></worksheet>')
  fid=d.register(f.getvalue(),'.xlsx',{})
  result=d.tabulate({'file_id':fid,'format':'xlsx'})
  self.assertEqual(result['columns'],['name','amount']);self.assertEqual(result['rows'],[['sample','12.5'],['','0']])
 def test_readonly_downloaded_database(self):
  import sqlite3
  src=d.DATA/'fixture.db';c=sqlite3.connect(src);c.execute('CREATE TABLE daily(station TEXT,flow REAL)');c.executemany('INSERT INTO daily VALUES (?,?)',[('A',2.5),('A',3.5),('B',9.0)]);c.commit();c.close()
  fid=d.register(src.read_bytes(),'.response',{})
  r=d.query_database({'file_id':fid,'sql':'SELECT station,AVG(flow) AS mean FROM daily GROUP BY station ORDER BY mean'})
  self.assertEqual(r['rows'],[('A',3.0),('B',9.0)])
  for sql in ['DELETE FROM daily','ATTACH DATABASE "/tmp/x" AS other','SELECT load_extension("x")','PRAGMA writable_schema=ON']:
   with self.assertRaises(Exception):d.query_database({'file_id':fid,'sql':sql})
  with self.assertRaises(ValueError):d.query_database({'file_id':'../../auth.json','sql':'SELECT 1'})
 def test_boundaries(self):
  for u in ['file:///etc/passwd','https://localhost/','https://rest.kegg.jp@evil.com/','https://rest.kegg.jp:8443/']:
   with self.assertRaises(ValueError):d.check_url(u)
  with self.assertRaises(ValueError):d.read({'file_id':'../../auth.json'})
  f=d.register(b'id,n\na,1\n','.csv',{})
  for sql in ['ATTACH DATABASE "/tmp/x" AS y','select readfile("/etc/passwd")','delete from x']:
   with self.assertRaises(Exception):d.query({'tables':{'x':f},'sql':sql})
if __name__=='__main__':unittest.main()
