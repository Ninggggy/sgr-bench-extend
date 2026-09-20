"""All fixtures are artificial 3x3 data, NEVER solver output."""
import unittest
from score import parse, score
S=['arXiv ID','x','y']; H='|'.join(S)
R=['9901.00001|A|B','9901.00002|C|D','9901.00003|E|F']
class Tests(unittest.TestCase):
    def check(self, rows, expected):
        r=score(parse(H+'\n'+'\n'.join(R),S),parse(H+'\n'+'\n'.join(rows),S),S)
        for name,v in zip(['Item-F1','Row-F1','P.O.A.'],expected): self.assertAlmostEqual(r['metrics'][name],v)
        return r
    def test_perfect(self): self.check(R,(1,1,1))
    def test_reverse(self): self.check(R[::-1],(1,1,0))
    def test_omitted(self): self.check(R[:2],(.8,.8,1))
    def test_wrong_field(self): self.check([R[0].replace('|A|','|X|'),*R[1:]],(8/9,2/3,1))
    def test_empty(self):
        r=score(parse(H+'\n'+'\n'.join(R),S),parse('',S),S)
        self.assertEqual(list(r['metrics'].values()),[0,0,0])
    def test_markdown(self):
        md='| '+H+' |\n|---|---|---|\n'+'\n'.join('|'+r+'|' for r in R)
        self.assertEqual([r['cells'] for r in parse(md,S)['rows']],[r.split('|') for r in R])
    def test_duplicate(self):
        r=self.check(R+[R[0]],(6/7,6/7,1));self.assertEqual(r['counts']['correct_fields'],9)
    def test_first_duplicate_not_best(self):
        r=self.check([R[0].replace('|A|','|X|'),*R[1:],R[0]],(16/21,4/7,1));self.assertEqual(r['counts']['correct_fields'],8)
    def test_missing_cell(self): self.check([R[0].rsplit('|',1)[0],*R[1:]],(8/9,2/3,1))
    def test_parse_failure(self): self.assertEqual(parse('cannot answer',S)['status'],'parse_failure')
    def test_version_suffix(self): self.check([R[0].replace('9901.00001','9901.00001v2'),*R[1:]],(1,1,1))
    def test_one_shared(self): self.check(R[:1],(.5,.5,0))
    def test_extra(self): self.check(R+['9901.00004|G|H'],(6/7,6/7,1))
if __name__=='__main__': unittest.main(verbosity=2)
