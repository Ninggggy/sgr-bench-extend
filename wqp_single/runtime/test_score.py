import unittest
from score import parse,score,norm
class WQPScoring(unittest.TestCase):
 def setUp(self):
  self.r={'columns':['rank','org','site','activity','temperature_C'],'row_key':['org','site','activity'],'fields':{'rank':{'type':'integer'},'temperature_C':{'type':'decimal','units':{'deg C':{},'deg F':{'offset':32,'scale_num':5,'scale_den':9}}}}}
  self.g='1|X|S|A|20.00\n2|Y|S|A|10.00'
 def s(self,p):return score(parse(self.g,self.r['columns']),parse(p,self.r['columns']),self.r)
 def test_composite_identity(self):self.assertEqual(self.s(self.g)['metrics'],{'Item-F1':1,'Row-F1':1,'P.O.A.':1})
 def test_wrong_entity_join(self):self.assertEqual(self.s('1|Z|S|A|20.00')['metrics']['Item-F1'],0)
 def test_rank_not_identity(self):self.assertAlmostEqual(self.s(self.g.replace('1|X','9|X'))['metrics']['Item-F1'],.9)
 def test_duplicate_no_reward(self):self.assertEqual(self.s(self.g+'\n'+self.g)['counts']['correct_rows'],2)
 def test_first_duplicate_wrong_not_best(self):self.assertEqual(self.s('1|X|S|A|19\n'+self.g)['counts']['correct_rows'],1)
 def test_conversion_and_precision(self):
  self.assertEqual(norm('68 deg F','temperature_C',self.r),'20')
  self.assertNotEqual(norm('68.01 deg F','temperature_C',self.r),'20')
  self.assertEqual(self.s(self.g.replace('20.00','68 deg F'))['metrics']['Item-F1'],1)
 def test_missing_extra_fields(self):
  self.assertEqual(self.s('1|X|S|A')['counts']['pred_fields'],5)
  self.assertEqual(self.s(self.g+'|extra')['counts']['correct_rows'],1)
 def test_reverse_order(self):self.assertEqual(self.s('\n'.join(self.g.splitlines()[::-1]))['metrics']['P.O.A.'],0)
 def test_single_shared_zero_poa(self):self.assertEqual(self.s(self.g.splitlines()[0])['metrics']['P.O.A.'],0)
 def test_nonempty_parse_failure(self):self.assertIsNone(self.s('Could not retrieve authoritative records')['metrics'])
 def test_zero_is_valid(self):
  self.g='0|X|S|A|0.00';self.assertEqual(self.s(self.g)['metrics']['Item-F1'],1)
if __name__=='__main__':unittest.main()
