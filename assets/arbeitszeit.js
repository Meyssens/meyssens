/* Arbeitszeiterfassung (/werkzeuge/arbeitszeit/): Monatsblatt mit Beginn, Ende und Pause pro Tag, Feiertage nach Kanton
   (gleiche Daten wie der Arbeitstage-Rechner), Soll/Ist, Überstunden (Art. 321c OR) und Wochen über der
   Höchstarbeitszeit (Art. 9/12 ArG). PDF (über QRRechnung.pdf) und CSV entstehen im Browser; nichts wird gesendet. */
(function (global) {
  'use strict';
  function minuten(s) { var m = /^(\d{1,2})[:.](\d{2})$/.exec(String(s || '').trim()); return m && +m[1] < 25 && +m[2] < 60 ? +m[1] * 60 + +m[2] : NaN; }
  // Arbeitszeit eines Tages in Minuten; Ende vor Beginn = über Mitternacht
  function tagMinuten(beginn, ende, pauseMin) {
    var b = minuten(beginn), e = minuten(ende), p = +pauseMin || 0;
    if (isNaN(b) || isNaN(e)) return null;
    var d = e - b; if (d < 0) d += 1440;
    return Math.max(0, d - p);
  }
  function hm(min) { var v = min < 0 ? '-' : ''; min = Math.abs(Math.round(min)); return v + Math.floor(min / 60) + ':' + ('0' + (min % 60)).slice(-2); }
  global.Arbeitszeit = { tagMinuten: tagMinuten, hm: hm };

  if (typeof document === 'undefined') return;
  var form = document.getElementById('az-formular');
  if (!form) return;
  var $ = function (id) { return document.getElementById(id); };
  var daten = JSON.parse($('at-daten').textContent), A = global.Arbeitstage;
  var TAGE = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'];
  var kanton = $('az-kanton'), region = $('az-region'), tbody = $('az-tage');
  function el(tag, text, k) { var e = document.createElement(tag); if (text != null) e.textContent = text; if (k) e.className = k; return e; }
  function kantonObj() { return daten.kantone.filter(function (k) { return k.id === kanton.value; })[0]; }
  function regionObj() { var k = kantonObj(); return k.regionen.filter(function (r) { return r.id === region.value; })[0] || k.regionen[0]; }
  function fuelleRegionen() {
    var k = kantonObj(); region.innerHTML = '';
    k.regionen.forEach(function (r) { var o = el('option', r.name); o.value = r.id; region.appendChild(o); });
    $('az-region-grp').hidden = k.regionen.length < 2;
  }
  function monat() { var m = /^(\d{4})-(\d{2})$/.exec($('az-monat').value); return m ? { j: +m[1], m: +m[2] } : null; }

  function baueTabelle() {
    var mo = monat(); tbody.innerHTML = '';
    if (!mo) return;
    var frei = {};
    A.feiertage(daten, regionObj(), mo.j).forEach(function (f) { frei[f.datum.toISOString().slice(0, 10)] = f.name + (f.halb ? ' (ab 12 Uhr)' : ''); });
    var tage = new Date(Date.UTC(mo.j, mo.m, 0)).getUTCDate();
    for (var t = 1; t <= tage; t++) {
      var d = new Date(Date.UTC(mo.j, mo.m - 1, t)), key = d.toISOString().slice(0, 10), wt = d.getUTCDay();
      var tr = el('tr', null, (wt === 0 || wt === 6) ? 'az-we' : (frei[key] ? 'az-ft' : '')); tr.dataset.datum = key;
      tr.appendChild(el('th', TAGE[wt] + ' ' + t + '.')); tr.firstChild.scope = 'row';
      ['beginn', 'ende', 'pause'].forEach(function (f) {
        var td = el('td'), i = el('input', null, 'finput az-' + f);
        i.type = 'text'; i.inputMode = f === 'pause' ? 'numeric' : 'text'; i.placeholder = f === 'pause' ? 'Min.' : 'hh:mm';
        i.setAttribute('aria-label', (f === 'beginn' ? 'Beginn' : f === 'ende' ? 'Ende' : 'Pause in Minuten') + ', ' + TAGE[wt] + ' ' + t + '.');
        td.appendChild(i); tr.appendChild(td);
      });
      tr.appendChild(el('td', '', 'az-summe'));
      tr.appendChild(el('td', frei[key] || '', 'az-notiz'));
      tbody.appendChild(tr);
    }
    beispielFuellen();
  }

  var beispiel = JSON.parse(($('az-beispiel') || { textContent: '{}' }).textContent), beispielAktiv = true;
  function beispielFuellen() {
    if (!beispielAktiv) return;
    Array.prototype.forEach.call(tbody.children, function (tr) {
      var wt = new Date(tr.dataset.datum + 'T00:00:00Z').getUTCDay();
      if (wt === 0 || wt === 6 || tr.classList.contains('az-ft')) return;
      var b = beispiel[tr.dataset.datum] || beispiel.standard;
      if (!b) return;
      tr.querySelector('.az-beginn').value = b[0]; tr.querySelector('.az-ende').value = b[1]; tr.querySelector('.az-pause').value = b[2];
    });
  }

  function rechne() {
    var mo = monat(); if (!mo) return null;
    var soll = parseFloat(String($('az-soll').value).replace(',', '.')), max = +$('az-max').value;
    var istMin = 0, wochen = {}, fehler = [];
    Array.prototype.forEach.call(tbody.children, function (tr) {
      var b = tr.querySelector('.az-beginn').value, e = tr.querySelector('.az-ende').value, p = tr.querySelector('.az-pause').value;
      var m = (b || e) ? tagMinuten(b, e, p) : 0;
      if (m === null) { fehler.push(tr.firstChild.textContent + ': Zeit im Format hh:mm angeben'); m = 0; }
      tr.querySelector('.az-summe').textContent = m ? hm(m) : '';
      istMin += m;
      var d = new Date(tr.dataset.datum + 'T00:00:00Z'), montag = new Date(d.getTime() - ((d.getUTCDay() + 6) % 7) * 86400000).toISOString().slice(0, 10);
      wochen[montag] = (wochen[montag] || 0) + m;
    });
    var von = A.utc(mo.j, mo.m, 1), bis = A.utc(mo.j, mo.m, new Date(Date.UTC(mo.j, mo.m, 0)).getUTCDate());
    var at = A.rechne(daten, regionObj(), von, bis, [1, 2, 3, 4, 5], []).arbeitstage;
    var sollMin = isFinite(soll) && soll > 0 ? Math.round(at * soll / 5 * 60) : 0;
    var ueber = Object.keys(wochen).filter(function (w) { return wochen[w] > max * 60; }).map(function (w) { return { woche: w, min: wochen[w] - max * 60 }; });
    return { istMin: istMin, sollMin: sollMin, saldo: istMin - sollMin, arbeitstage: at, ueberzeit: ueber, fehler: fehler, max: max };
  }

  function aktualisiere() {
    var r = rechne(), aus = $('az-ergebnis'); aus.innerHTML = '';
    if (!r) return;
    var p = el('p', null, 'at-zahl'); p.appendChild(el('strong', hm(r.istMin))); p.appendChild(document.createTextNode(' Stunden gearbeitet'));
    aus.appendChild(p);
    aus.appendChild(el('p', 'Soll: ' + hm(r.sollMin) + ' (' + String(r.arbeitstage).replace('.', ',') + ' Arbeitstage) · Saldo: ' + hm(r.saldo) +
      (r.saldo > 0 ? ' Überstunden' : ''), 'at-was'));
    if (r.ueberzeit.length) aus.appendChild(el('p', 'Über der Höchstarbeitszeit von ' + r.max + ' Stunden: ' + r.ueberzeit.map(function (u) {
      return 'Woche ab ' + u.woche.slice(8, 10) + '.' + u.woche.slice(5, 7) + '. (+' + hm(u.min) + ')'; }).join(', ') + '. Das ist Überzeit (Art. 12 ArG).', 'at-was lf-achtung'));
    $('az-meldung').textContent = r.fehler.slice(0, 3).join(' · ');
  }

  function zeilen() {
    return Array.prototype.map.call(tbody.children, function (tr) {
      return [tr.dataset.datum, tr.firstChild.textContent, tr.querySelector('.az-beginn').value, tr.querySelector('.az-ende').value,
              tr.querySelector('.az-pause').value, tr.querySelector('.az-summe').textContent, tr.querySelector('.az-notiz').textContent];
    });
  }
  function csv() {
    var kopf = ['Datum', 'Tag', 'Beginn', 'Ende', 'Pause (Min.)', 'Arbeitszeit', 'Bemerkung'];
    var text = [kopf].concat(zeilen()).map(function (z) { return z.map(function (x) { return '"' + String(x).replace(/"/g, '""') + '"'; }).join(';'); }).join('\r\n');
    var url = URL.createObjectURL(new Blob(['﻿' + text], { type: 'text/csv;charset=utf-8' }));
    var a = el('a'); a.href = url; a.download = 'arbeitszeit-' + $('az-monat').value + '.csv'; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }
  function pdf(leer) {
    var Q = global.QRRechnung, ops = [], r = rechne(), mo = monat();
    function t(x, y, pt, f, s, a) { ops.push({ t: 'text', x: x, y: y, pt: pt, fett: f, text: Q.bereinige(s), anker: a || 'start' }); }
    function l(x1, y1, x2, y2, w) { ops.push({ t: 'linie', x1: x1, y1: y1, x2: x2, y2: y2, w: w || 0.2 }); }
    var MON = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
    t(20, 18, 14, true, 'Arbeitszeiterfassung ' + MON[mo.m - 1] + ' ' + mo.j);
    t(20, 25, 9, false, 'Name: ' + ($('az-name').value || '______________________________') + '   ·   ' + kantonObj().name + (kantonObj().regionen.length > 1 ? ', ' + regionObj().name : ''));
    var x = [20, 42, 62, 82, 102, 124], y = 34;
    ['Tag', 'Beginn', 'Ende', 'Pause', 'Arbeitszeit', 'Bemerkung'].forEach(function (s, i) { t(x[i], y, 8.5, true, s); });
    y += 2; l(20, y, 190, y, 0.4); y += 4.6;
    zeilen().forEach(function (z) {
      var we = /^(Sa|So)/.test(z[1]);
      if (we || z[6]) ops.push({ t: 'flaeche', x: 20, y: y - 3.5, w: 170, h: 6.2, grau: 0.93 });
      t(x[0], y, 8.5, false, z[1]);
      if (!leer) { t(x[1], y, 8.5, false, z[2]); t(x[2], y, 8.5, false, z[3]); t(x[3], y, 8.5, false, z[4] ? z[4] + ' Min.' : ''); t(x[4], y, 8.5, false, z[5]); }
      t(x[5], y, 8, false, z[6]);
      y += 2.7; l(20, y, 190, y, 0.15); y += 3.5;
    });
    y += 4;
    if (!leer && r) {
      t(20, y, 9.5, true, 'Total ' + hm(r.istMin) + '   ·   Soll ' + hm(r.sollMin) + '   ·   Saldo ' + hm(r.saldo)); y += 6;
      if (r.ueberzeit.length) { t(20, y, 8.5, false, 'Über der Höchstarbeitszeit (' + r.max + ' h): ' + r.ueberzeit.map(function (u) { return 'Woche ab ' + u.woche.slice(8, 10) + '.' + u.woche.slice(5, 7) + '. +' + hm(u.min); }).join(', ')); y += 6; }
    }
    y += 8; l(20, y, 90, y, 0.3); l(110, y, 180, y, 0.3); y += 4;
    t(20, y, 8, false, 'Datum, Unterschrift Mitarbeiter/in'); t(110, y, 8, false, 'Datum, Unterschrift Arbeitgeber');
    t(20, 290, 7, false, 'Erstellt mit meyssens.ch/werkzeuge/arbeitszeit · Allgemeine Vorlage, keine Rechtsberatung.');
    var a = el('a'), url = URL.createObjectURL(new Blob([Q.pdf(null, 'Arbeitszeit ' + $('az-monat').value, ops)], { type: 'application/pdf' }));
    a.href = url; a.download = 'arbeitszeit-' + $('az-monat').value + (leer ? '-leer' : '') + '.pdf'; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }

  fuelleRegionen(); baueTabelle(); aktualisiere();
  kanton.addEventListener('change', function () { fuelleRegionen(); baueTabelle(); aktualisiere(); });
  region.addEventListener('change', function () { baueTabelle(); aktualisiere(); });
  $('az-monat').addEventListener('change', function () { baueTabelle(); aktualisiere(); });
  form.addEventListener('input', function (e) { if (e.target.closest('#az-tage')) beispielAktiv = false; aktualisiere(); });
  $('az-leeren').addEventListener('click', function () { beispielAktiv = false; Array.prototype.forEach.call(tbody.querySelectorAll('input'), function (i) { i.value = ''; }); aktualisiere(); });
  $('az-pdf').addEventListener('click', function () { pdf(false); });
  $('az-pdf-leer').addEventListener('click', function () { pdf(true); });
  $('az-csv').addEventListener('click', csv);
  form.addEventListener('submit', function (e) { e.preventDefault(); });
})(typeof window !== 'undefined' ? window : this);
