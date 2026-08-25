import json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def validate(data):
 errors=[];ids=set()
 if data.get("meta",{}).get("schema_version")!=1:errors.append("bad schema")
 for c in data.get("companies",[]):
  for k in ("id","name","country","categories","comparability_group","metrics","sources"):
   if k not in c:errors.append(c.get("id","?")+": missing "+k)
  if c.get("id") in ids:errors.append("duplicate id")
  ids.add(c.get("id"))
  for name,m in c.get("metrics",{}).items():
   if m.get("value") is not None and (m["value"]<0 or not m.get("period") or not m.get("verified_at")):errors.append(c["id"]+": invalid metric")
   if name in ("profit","valuation") and m.get("value") is not None and not m.get("currency"):errors.append(c["id"]+": missing metric currency")
   if (m.get("estimated") or m.get("approximate")) and not m.get("method"):errors.append(c["id"]+": missing estimate method")
   if m.get("sort_value") is not None and not m.get("sort_currency"):errors.append(c["id"]+": missing sort currency")
  for s in c.get("sources",[]):
   if not s.get("url","").startswith("https://"):errors.append(c["id"]+": invalid source")
 return errors
if __name__=="__main__":
 d=json.loads((ROOT/"data/ranking.json").read_text(encoding="utf-8"));e=validate(d)
 if e:print("\\n".join(e));sys.exit(1)
 print("OK:",len(d["companies"]),"companies")
