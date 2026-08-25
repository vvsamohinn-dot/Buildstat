var db = { companies: [], meta: {} };

function el(selector) {
  return document.querySelector(selector);
}

function metric(company, key) {
  return company.metrics && company.metrics[key] ? company.metrics[key] : null;
}

function val(company, key) {
  var item = metric(company, key);
  return item ? item.value : null;
}

function sortVal(company, key) {
  var item = metric(company, key);
  if (!item) return null;
  return item.sort_value == null ? item.value : item.sort_value;
}

function fmt(number) {
  if (number == null) return "—";
  return new Intl.NumberFormat("ru-RU", {
    notation: Math.abs(number) >= 1000000 ? "compact" : "standard",
    maximumFractionDigits: 1
  }).format(number);
}

function metricValue(company, key, includeUnit) {
  var item = metric(company, key);
  if (!item) return "—";
  var prefix = item.estimated || item.approximate ? "≈" : "";
  var suffix = item.currency ? " " + item.currency : (includeUnit && item.unit ? " " + item.unit : "");
  return prefix + fmt(item.value) + suffix;
}

function metricLabel(company, key, fallback) {
  var item = metric(company, key);
  if (!item) return fallback;
  if (item.estimated) return "оценка · " + fallback;
  if (item.approximate) return "округлено · " + fallback;
  return fallback;
}

function addOptions(id, rows) {
  Array.from(new Set(rows.filter(Boolean))).sort().forEach(function (value) {
    el(id).add(new Option(value, value));
  });
}

function render() {
  var query = el("#q").value.toLowerCase();
  var country = el("#country").value;
  var category = el("#category").value;
  var sort = el("#sort").value;
  var rows = db.companies
    .filter(function (company) {
      return (!query || company.name.toLowerCase().includes(query)) &&
        (!country || company.country === country) &&
        (!category || company.categories.includes(category));
    })
    .sort(function (a, b) {
      var right = sortVal(b, sort);
      var left = sortVal(a, sort);
      return (right == null ? -1 : right) - (left == null ? -1 : left);
    });

  el("#status").textContent = rows.length + " из " + db.companies.length;
  el("#companies").innerHTML = rows.map(function (company, index) {
    return '<article class="company" data-id="' + company.id + '">' +
      '<b>' + String(index + 1) + '</b>' +
      '<div class="identity"><b>' + company.name + '</b><i>' + company.country + " · " + (company.region || "—") + '</i></div>' +
      '<div class="metric"><b>' + metricValue(company, "area") + '</b><i class="' + ((metric(company, "area") || {}).estimated ? "estimate" : "") + '">' + metricLabel(company, "area", "м²") + '</i></div>' +
      '<div class="metric"><b>' + metricValue(company, "objects") + '</b><i>объектов</i></div>' +
      '<div class="metric"><b>' + metricValue(company, "profit") + '</b><i>прибыль</i></div>' +
      '<div class="metric"><b>' + metricValue(company, "valuation") + '</b><i>капитализация</i></div>' +
      '<span>›</span></article>';
  }).join("");

  document.querySelectorAll(".company").forEach(function (node) {
    node.onclick = function () { show(node.dataset.id); };
  });
}

function show(id) {
  var company = db.companies.find(function (item) { return item.id === id; });
  var labels = { area: "Площадь", objects: "Объекты", profit: "Прибыль", valuation: "Капитализация" };
  var rows = Object.keys(labels).map(function (key) {
    var item = metric(company, key);
    if (!item) return "";
    var status = item.estimated ? "Расчётная оценка" : (item.approximate ? "Округлено источником" : "Подтверждено источником");
    return '<tr><td><b>' + labels[key] + '</b></td><td>' + metricValue(company, key, true) + '<small>' + status + '</small></td><td>' + item.period + (item.method ? '<small>' + item.method + '</small>' : '') + '</td></tr>';
  }).join("");
  var sources = company.sources.map(function (source) {
    return '<div class="source"><b>' + source.title + '</b><br><a target="_blank" rel="noopener" href="' + source.url + '">Открыть источник</a></div>';
  }).join("");
  el("#detail").innerHTML = '<small>' + company.country + '</small><h2>' + company.name + '</h2><p>' + company.notes + '</p><table class="metric-table"><thead><tr><th>Показатель</th><th>Значение</th><th>Период и расчёт</th></tr></thead><tbody>' + rows + '</tbody></table><h3>Источники</h3>' + sources;
  el("dialog").showModal();
}

fetch("data/ranking.json")
  .then(function (response) { return response.json(); })
  .then(function (data) {
    db = data;
    addOptions("#country", db.companies.map(function (company) { return company.country; }));
    addOptions("#category", db.companies.flatMap(function (company) { return company.categories; }));
    el("#updated").textContent = "проверено " + db.meta.last_verified;
    el("#stats").innerHTML = [
      ["Компаний", db.companies.length],
      ["Стран", new Set(db.companies.map(function (company) { return company.country; })).size],
      ["С источниками", db.companies.filter(function (company) { return company.sources.length; }).length],
      ["В очереди", db.meta.review_queue_count]
    ].map(function (item) {
      return '<div class="stat"><b>' + item[1] + '</b><em>' + item[0] + '</em></div>';
    }).join("");
    render();
  });

["#q", "#country", "#category", "#sort"].forEach(function (selector) {
  el(selector).oninput = render;
});

el("#close").onclick = function () {
  el("dialog").close();
};
