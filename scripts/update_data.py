import html,json,pathlib,re,urllib.request
from datetime import date
from validate_data import validate
R=pathlib.Path(__file__).resolve().parents[1];DB=R/"data/ranking.json";C=R/"data/candidates.json";Q=R/"data/review_queue.json"
ERZ_URL="https://erzrf.ru/top-zastroyshchikov/rf?topType=4"
ERZ_NAMES={"pik":"ПИК","samolet":"ГК Самолет","setl":"Холдинг Setl Group","lsr":"Группа ЛСР","fsk":"ГК ФСК","dogma":"DOGMA","brusnika":"Брусника"}
def parse_erz(page):
 text=html.unescape(re.sub(r"<[^>]+>"," ",page));text=re.sub(r"\s+"," ",text)
 out=[]
 for company_id,name in ERZ_NAMES.items():
  start=text.find(name)
  if start<0:continue
  part=text[start:start+1000]
  area=re.search(r"Введено, м²\s*([0-9 ]+)",part)
  homes=re.search(r"МД\s*([0-9 ]+).*?ДАП\s*([0-9 ]+)",part)
  if not area:continue
  period="с 2016 по "+str(date.today())
  out.append({"company_id":company_id,"metric":"area","value":int(area.group(1).replace(" ","")),"unit":"м²","period":period,"source_url":ERZ_URL,"cumulative":True})
  if homes:out.append({"company_id":company_id,"metric":"objects","value":int(homes.group(1).replace(" ",""))+int(homes.group(2).replace(" ","")),"unit":"домов","period":period,"source_url":ERZ_URL,"cumulative":True})
 return out
def fetch_erz():
 req=urllib.request.Request(ERZ_URL,headers={"User-Agent":"BuildStat/1.0 (+https://github.com/vvsamohinn-dot/Buildstat)"})
 with urllib.request.urlopen(req,timeout=30) as response:return parse_erz(response.read().decode("utf-8"))
def review(old,new):
 r=[]
 if new.get("value") is None or not new.get("source_url") or not new.get("period"):r.append("incomplete provenance")
 if new.get("value",0)<0:r.append("negative")
 if old and old.get("value") and new.get("value") is not None:
  if new.get("cumulative") and new["value"]<old["value"]:r.append("cumulative value decreased")
  if abs(new["value"]/old["value"]-1)>.5:r.append("change exceeds 50%")
 return r
def main():
 d=json.loads(DB.read_text(encoding="utf-8"));xs=json.loads(C.read_text(encoding="utf-8")) if C.exists() else []
 try:xs+=fetch_erz()
 except Exception as exc:print("ЕРЗ временно недоступен, сохраняю текущие данные:",exc)
 q=[];rows={x["id"]:x for x in d["companies"]}
 for x in xs:
  c=rows.get(x.get("company_id"));k=x.get("metric")
  if not c or k not in ("area","objects","profit","valuation"):q.append(dict(x,reasons=["unknown target"]));continue
  reasons=review(c["metrics"].get(k),x)
  if reasons:q.append(dict(x,reasons=reasons));continue
  c["metrics"][k]={"value":x["value"],"unit":x.get("unit"),"currency":x.get("currency"),"period":x["period"],"verified_at":str(date.today()),"source_url":x["source_url"]}
 d["meta"]["last_verified"]=str(date.today());d["meta"]["review_queue_count"]=len(q)
 if validate(d):raise SystemExit("validation failed")
 DB.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");Q.write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print("Accepted",len(xs)-len(q),"queued",len(q))
if __name__=="__main__":main()
