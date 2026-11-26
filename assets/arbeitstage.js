/* Arbeitstage-Rechner (/werkzeuge/arbeitstage/): rechnet vollständig im Browser, sendet und speichert nichts.
   Feiertage und Regionen stehen als JSON in der Seite (#at-daten), erzeugt aus werkzeuge.py (gleiche Regeln wie die
   Tabellen auf der Seite). Halbe Feiertage (Solothurn, 1. Mai ab 12 Uhr) zählen als halber Arbeitstag. */
(function (global) {
  'use strict';

  function ostersonntag(jahr) {        // Meeus/Jones/Butcher, wie werkzeuge.py
    var a = jahr % 19, b = Math.floor(jahr / 100), c = jahr % 100, d = Math.floor(b / 4), e = b % 4;
    var f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30;
    var i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451);
    var x = h + l - 7 * m + 114;
    return new Date(Date.UTC(jahr, Math.floor(x / 31) - 1, (x % 31) + 1));
  }
  function utc(j, m, t) { return new Date(Date.UTC(j, m - 1, t)); }
  function plusTage(d, n) { return new Date(d.getTime() + n * 86400000); }
  function schluessel(d) { return d.toISOString().slice(0, 10); }

  function feiertage(daten, region, jahr) {    // [{datum, name, halb}]
    return region.tage.map(function (s) {
      var f = daten.feiertage[s];
      var d = f.typ === 'fix' ? utc(jahr, f.wert[0], f.wert[1]) : plusTage(ostersonntag(jahr), f.wert);
      return { datum: d, name: f.name, halb: !!f.halb };
    }).sort(function (a, b) { return a.datum - b.datum; });
  }

  // von, bis: Date (UTC, Mitternacht), beide eingeschlossen; werktage: Array 0=So … 6=Sa; extra: [{datum, anteil, name}]
  function rechne(daten, region, von, bis, werktage, extra) {
    var frei = {}, liste = [];
    for (var j = von.getUTCFullYear(); j <= bis.getUTCFullYear(); j++) {
      feiertage(daten, region, j).forEach(function (f) {
        var k = schluessel(f.datum), anteil = f.halb ? 0.5 : 1;
        if (!frei[k] || frei[k].anteil < anteil) frei[k] = { anteil: anteil, name: f.name, gesetzlich: true };
      });
      (extra || []).forEach(function (x) {
        var d = utc(j, x.monat, x.tag), k = schluessel(d);
        if (!frei[k] || frei[k].anteil < x.anteil) frei[k] = { anteil: x.anteil, name: x.name, gesetzlich: false };
      });
    }
    var n = 0, kalender = 0, wochenende = 0, monate = {};
    for (var d = von; d <= bis; d = plusTage(d, 1)) {
      kalender++;
      var mk = schluessel(d).slice(0, 7);
      if (!monate[mk]) monate[mk] = 0;
      if (werktage.indexOf(d.getUTCDay()) < 0) { wochenende++; continue; }
      var f = frei[schluessel(d)], wert = 1 - (f ? f.anteil : 0);
      n += wert; monate[mk] += wert;
      if (f) liste.push({ datum: new Date(d), name: f.name, anteil: f.anteil, gesetzlich: f.gesetzlich });
    }
    return { arbeitstage: n, kalendertage: kalender, freieWochentage: wochenende, feiertage: liste, monate: monate };
  }

  var API = { ostersonntag: ostersonntag, feiertage: feiertage, rechne: rechne, utc: utc };
  global.Arbeitstage = API;

  // --- Bedienung ---
  if (typeof document === 'undefined') return;
  var form = document.getElementById('at-formular'), quelle = document.getElementById('at-daten');
  if (!form || !quelle) return;
  var daten = JSON.parse(quelle.textContent);
  var kanton = document.getElementById('at-kanton'), region = document.getElementById('at-region');
  var regionGrp = document.getElementById('at-region-grp'), vonF = document.getElementById('at-von'), bisF = document.getElementById('at-bis');
  var ausgabe = document.getElementById('at-ergebnis'), meldung = document.getElementById('at-meldung');
  var MONATE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
  var TAGE = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'];

  function zahl(n) { return String(n).replace('.', ','); }
  function datum(d) { return ('0' + d.getUTCDate()).slice(-2) + '.' + ('0' + (d.getUTCMonth() + 1)).slice(-2) + '.' + d.getUTCFullYear(); }
  function leseDatum(s) { var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || ''); return m ? utc(+m[1], +m[2], +m[3]) : null; }
  function aktuellerKanton() { return daten.kantone.filter(function (k) { return k.id === kanton.value; })[0]; }
  function fuelleRegionen() {
    var k = aktuellerKanton();
    region.innerHTML = '';
    k.regionen.forEach(function (r) { var o = document.createElement('option'); o.value = r.id; o.textContent = r.name; region.appendChild(o); });
    regionGrp.hidden = k.regionen.length < 2;
  }
  function el(tag, text, klasse) { var e = document.createElement(tag); if (text != null) e.textContent = text; if (klasse) e.className = klasse; return e; }

  function aktualisiere() {
    var von = leseDatum(vonF.value), bis = leseDatum(bisF.value);
    meldung.textContent = '';
    if (!von || !bis) { meldung.textContent = 'Bitte beide Daten angeben.'; return; }
    if (bis < von) { meldung.textContent = 'Das Enddatum liegt vor dem Startdatum.'; return; }
    if (bis.getUTCFullYear() - von.getUTCFullYear() > 5) { meldung.textContent = 'Bitte höchstens fünf Jahre auf einmal berechnen.'; return; }
    var k = aktuellerKanton(), r = k.regionen.filter(function (x) { return x.id === region.value; })[0] || k.regionen[0];
    var werktage = Array.prototype.map.call(form.querySelectorAll('input[name="at-tag"]:checked'), function (c) { return +c.value; });
    var extra = Array.prototype.map.call(form.querySelectorAll('input[name="at-extra"]:checked'), function (c) {
      var t = c.value.split('-'); return { monat: +t[0], tag: +t[1], anteil: +t[2], name: c.getAttribute('data-name') };
    });
    var e = rechne(daten, r, von, bis, werktage, extra);
    ausgabe.innerHTML = '';
    var kopf = el('p', null, 'at-zahl');
    kopf.appendChild(el('strong', zahl(e.arbeitstage)));
    kopf.appendChild(document.createTextNode(' Arbeitstage'));
    ausgabe.appendChild(kopf);
    ausgabe.appendChild(el('p', datum(von) + ' bis ' + datum(bis) + ' · ' + k.name + (k.regionen.length > 1 ? ', ' + r.name : '') +
      ' · ' + e.kalendertage + ' Kalendertage, davon ' + e.freieWochentage + ' freie Wochentage', 'at-was'));
    if (e.feiertage.length) {
      ausgabe.appendChild(el('h3', 'Abgezogen'));
      var ul = el('ul', null, 'at-abzug');
      e.feiertage.forEach(function (f) {
        var li = el('li');
        li.appendChild(el('span', TAGE[f.datum.getUTCDay()] + ' ' + datum(f.datum)));
        li.appendChild(document.createTextNode(' ' + f.name + (f.anteil < 1 ? ' (halber Tag)' : '') + (f.gesetzlich ? '' : ' · Ihre Angabe, nicht gesetzlich')));
        ul.appendChild(li);
      });
      ausgabe.appendChild(ul);
    } else {
      ausgabe.appendChild(el('p', 'Im Zeitraum fällt kein Feiertag auf einen Arbeitstag.', 'at-was'));
    }
    var mk = Object.keys(e.monate);
    if (mk.length > 1 && mk.length <= 24) {
      var t = el('table', null, 'qr-tabelle at-monate'), tb = el('tbody');
      var kopfZ = el('tr'); kopfZ.appendChild(el('th', 'Monat')); kopfZ.appendChild(el('th', 'Arbeitstage'));
      var th = el('thead'); th.appendChild(kopfZ); t.appendChild(th);
      kopfZ.children[0].scope = kopfZ.children[1].scope = 'col';
      mk.forEach(function (m) {
        var z = el('tr'), c = el('th', MONATE[+m.slice(5) - 1] + ' ' + m.slice(0, 4)); c.scope = 'row';
        z.appendChild(c); z.appendChild(el('td', zahl(e.monate[m]))); tb.appendChild(z);
      });
      t.appendChild(tb);
      var w = el('div', null, 'tabelle-scroll'); w.appendChild(t); ausgabe.appendChild(w);
    }
  }

  fuelleRegionen();
  kanton.addEventListener('change', function () { fuelleRegionen(); aktualisiere(); });
  form.addEventListener('input', aktualisiere);
  form.addEventListener('change', aktualisiere);
  form.addEventListener('submit', function (e) { e.preventDefault(); aktualisiere(); });
  aktualisiere();
})(typeof window !== 'undefined' ? window : this);
