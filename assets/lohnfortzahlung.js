/* Lohnfortzahlung bei Krankheit (/werkzeuge/lohnfortzahlung/): Art. 324a OR mit Basler, Berner und Zürcher Skala.
   Skalen: Basel nach Merkblatt «Lohn» des Amts für Wirtschaft und Arbeit Basel-Stadt (Stand 1.1.2024), Bern nach den
   Zivilgerichten des Kantons Bern (Dienstjahre 1–19) und der Übersicht der Gerichte Zürich (20–25), Zürich nach der
   Übersicht der Gerichte des Kantons Zürich (1–25). Darüber hinaus keine amtliche Angabe. Rechnet im Browser. */
(function (global) {
  'use strict';
  var SKALEN = {
    basel: { name: 'Basler Skala', stufen: [[1, 1, '3 Wochen'], [2, 3, '2 Monate'], [4, 10, '3 Monate'], [11, 15, '4 Monate'], [16, 20, '5 Monate'], [21, 999, '6 Monate']] },
    bern: { name: 'Berner Skala', stufen: [[1, 1, '3 Wochen'], [2, 2, '1 Monat'], [3, 4, '2 Monate'], [5, 9, '3 Monate'], [10, 14, '4 Monate'], [15, 19, '5 Monate'], [20, 25, '6 Monate']] },
    zuerich: { name: 'Zürcher Skala', stufen: [[1, 1, '3 Wochen']].concat(Array.apply(null, Array(24)).map(function (_, i) { return [i + 2, i + 2, (i + 8) + ' Wochen']; })) }
  };
  function datum(s) { var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || ''); return m ? { j: +m[1], m: +m[2], t: +m[3] } : null; }
  function iso(d) { return d.j + '-' + ('0' + d.m).slice(-2) + '-' + ('0' + d.t).slice(-2); }
  function plusJahre(d, n) {       // gleicher Kalendertag n Jahre später (29.2. -> 28.2.)
    var j = d.j + n, t = d.t, max = new Date(Date.UTC(j, d.m, 0)).getUTCDate();
    return { j: j, m: d.m, t: Math.min(t, max) };
  }
  function vor(a, b) { return iso(a) < iso(b); }
  // Dienstjahr, in dem die Krankheit beginnt (1 = erstes), mit Beginn und Ende des Dienstjahrs
  function dienstjahr(eintrittIso, beginnIso) {
    var e = datum(eintrittIso), k = datum(beginnIso);
    if (!e || !k || vor(k, e)) return null;
    var n = k.j - e.j;
    if (vor(k, plusJahre(e, n))) n--;
    var von = plusJahre(e, n), bisExkl = plusJahre(e, n + 1);
    var bis = new Date(Date.UTC(bisExkl.j, bisExkl.m - 1, bisExkl.t) - 86400000);
    var drei = e.m + 3 > 12 ? { j: e.j + 1, m: e.m - 9, t: e.t } : { j: e.j, m: e.m + 3, t: e.t };
    return { nr: n + 1, von: iso(von), bis: bis.toISOString().slice(0, 10), ersteDreiMonate: vor(k, drei) };
  }
  function anspruch(skala, nr) {
    var s = SKALEN[skala].stufen.filter(function (x) { return nr >= x[0] && nr <= x[1]; })[0];
    return s ? s[2] : null;
  }
  global.Lohnfortzahlung = { dienstjahr: dienstjahr, anspruch: anspruch, SKALEN: SKALEN };
  if (typeof document === 'undefined') return;
  var form = document.getElementById('lf-formular');
  if (!form) return;
  var $ = function (id) { return document.getElementById(id); };
  function el(tag, text, k) { var e = document.createElement(tag); if (text != null) e.textContent = text; if (k) e.className = k; return e; }
  function ch(s) { var d = datum(s); return d ? ('0' + d.t).slice(-2) + '.' + ('0' + d.m).slice(-2) + '.' + d.j : s; }
  function aktualisiere() {
    var aus = $('lf-ergebnis'), meld = $('lf-meldung'), skala = form.querySelector('input[name="lf-skala"]:checked').value;
    aus.innerHTML = ''; meld.textContent = '';
    if ($('lf-kurz').checked) { aus.appendChild(el('p', 'Kein gesetzlicher Anspruch nach Art. 324a OR: Das Arbeitsverhältnis ist auf höchstens drei Monate befristet. Vertrag oder GAV können mehr vorsehen.', 'at-was')); return; }
    var d = dienstjahr($('lf-eintritt').value, $('lf-beginn').value);
    if (!d) { meld.textContent = 'Bitte Eintritt und Beginn der Arbeitsunfähigkeit angeben (Beginn nicht vor dem Eintritt).'; return; }
    var a = anspruch(skala, d.nr);
    var p = el('p', null, 'at-zahl'); p.appendChild(el('strong', a || 'keine Angabe')); p.appendChild(document.createTextNode(' Lohnfortzahlung'));
    aus.appendChild(p);
    aus.appendChild(el('p', SKALEN[skala].name + ', ' + d.nr + '. Dienstjahr (' + ch(d.von) + ' bis ' + ch(d.bis) + '). Der Anspruch gilt für alle Absenzen in diesem Dienstjahr zusammen und beginnt mit dem nächsten Dienstjahr neu.', 'at-was'));
    if (!a) aus.appendChild(el('p', 'Für dieses Dienstjahr haben wir keine amtliche Angabe der ' + SKALEN[skala].name + ' gefunden.', 'at-was'));
    if (d.ersteDreiMonate) aus.appendChild(el('p', 'Achtung: Beginn in den ersten drei Monaten. Nach Art. 324a OR besteht der Anspruch, wenn das Arbeitsverhältnis mehr als drei Monate gedauert hat oder für mehr als drei Monate eingegangen ist. Das Merkblatt des Kantons Basel-Stadt nennt für das erste Dienstjahr grundsätzlich den 4. Anstellungsmonat.', 'at-was lf-achtung'));
  }
  form.addEventListener('input', aktualisiere); form.addEventListener('change', aktualisiere);
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  aktualisiere();
})(typeof window !== 'undefined' ? window : this);
