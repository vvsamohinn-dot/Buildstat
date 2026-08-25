import json,pathlib
from datetime import date
from validate_data import validate
R=pathlib.Path(__file__).resolve().parents[1];DB=R/"data/ranking.json";C=R/"data/candidates.json";Q=R/"data/review_queue.json"
def review(old,new):
 r=[]
 if new.get("value") is None or not new.get("source_url") or not new.get("period"):r.append("incomplete provenance")
 if new.get("value",0)<0:r.append("negative")
 if old and old.get("value") and new.get("value") is not None:
  if new.get("cumulative") and new["value"]<old["value"]:r.append("cumulative value decreased")
  if abs(new["value"]/old["value"]-1)>.5:r.append("change exceeds 50%")
 return r
def main():
 d=json.loads(DB.read_text(encoding="utf-8"));xs=json.loads(C.read_text(encoding="utf-8")) if C.exists() else [];q=[];rows={x["id"]:x for x in d["companies"]}
 for x in xs:
  c=rows.get(x.get("company_id"));k=x.get("metric")
  if not c or k not in ("area","objects","profit","valuation"):q.append(dict(x,reasons=["unknown target"]));continue
  reasons=review(c["metrics"].get(k),x)
  if reasons:q.append(dict(x,reasons=reasons));continue
  c["metrics"][k]={"value":x["value"],"unit":x.get("unit"),"currency":x.get("currency"),"period":x["period"],"verified_at":str(date.today()),"source_url":x["source_url"]}
 d["meta"]["last_verified"]=str(date.today());d["meta"]["review_queue_count"]=len(q)
 if validate(d):raise SystemExit("validation failed")
 DB.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8");Q.write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8");print("Accepted",len(xs)-len(q),"queued",len(q))
if __name__=="__main__":main()
