import pathlib,shutil
R=pathlib.Path(__file__).resolve().parents[1];O=R/"dist"
if O.exists():shutil.rmtree(O)
O.mkdir()
for n in ("index.html","styles.css","app.js","METHODOLOGY.md"):shutil.copy2(R/n,O/n)
(O/"data").mkdir();shutil.copy2(R/"data/ranking.json",O/"data/ranking.json");(O/".nojekyll").write_text("")
print("Built",O)
