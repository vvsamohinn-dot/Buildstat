import json,pathlib,sys,unittest
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"scripts"))
from validate_data import validate
from update_data import parse_erz,review
class Tests(unittest.TestCase):
 def test_db(self):self.assertEqual(validate(json.loads((R/"data/ranking.json").read_text(encoding="utf-8"))),[])
 def test_decrease(self):self.assertIn("cumulative value decreased",review({"value":100},{"value":90,"source_url":"https://x","period":"2026","cumulative":True}))
 def test_spike(self):self.assertIn("change exceeds 50%",review({"value":100},{"value":200,"source_url":"https://x","period":"2026"}))
 def test_missing(self):self.assertIn("incomplete provenance",review(None,{"value":2,"period":"2026"}))
 def test_erz_parser(self):
  rows=parse_erz("<b>ПИК</b> Введено, м² 19 009 086 МД 931 БД 0 ДАП 11")
  self.assertEqual([x["value"] for x in rows],[19009086,942])
