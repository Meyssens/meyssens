/* MWST-Rechner (/werkzeuge/mwst-rechner/): Sätze seit 1.1.2024 (Art. 25 MWSTG), Beträge auf den Rappen gerundet.
   Rechnet im Browser, sendet und speichert nichts. */
(function (global) {
  'use strict';
  function r2(n) { return Math.round((n + Number.EPSILON) * 100) / 100; }
  function zahl(s) {
    s = String(s == null ? '' : s).trim().replace(/['’\s]/g, '').replace(',', '.');
    return /^\d+(\.\d+)?$/.test(s) ? parseFloat(s) : NaN;
  }
  // richtung 'netto': Betrag ohne MWST -> mit; 'brutto': Betrag mit MWST -> ohne (Steuer herausrechnen)
  function rechne(betrag, satz, richtung) {
    if (richtung === 'netto') { var m = r2(betrag * satz / 100); return { netto: r2(betrag), mwst: m, brutto: r2(betrag + m) }; }
    var s = r2(betrag * satz / (100 + satz));
    return { netto: r2(betrag - s), mwst: s, brutto: r2(betrag) };
  }
  global.MwstRechner = { rechne: rechne, zahl: zahl };
  if (typeof document === 'undefined') return;
  var form = document.getElementById('mw-formular');
  if (!form) return;
  var aus = document.getElementById('mw-ergebnis');
  function geld(n) { var s = n.toFixed(2).split('.'); return s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + '.' + s[1]; }
  function aktualisiere() {
    var b = zahl(document.getElementById('mw-betrag').value);
    var satz = parseFloat(form.querySelector('input[name="mw-satz"]:checked').value);
    var richtung = form.querySelector('input[name="mw-richtung"]:checked').value;
    aus.innerHTML = '';
    if (!isFinite(b)) { var p0 = document.createElement('p'); p0.className = 'at-was'; p0.textContent = 'Bitte einen Betrag eingeben, zum Beispiel 1250.50.'; aus.appendChild(p0); return; }
    var r = rechne(b, satz, richtung), satzT = String(satz).replace('.', ',') + ' %';
    var zeilen = [['Betrag ohne MWST', r.netto], ['MWST ' + satzT, r.mwst], ['Betrag mit MWST', r.brutto]];
    var dl = document.createElement('dl'); dl.className = 'mw-liste';
    zeilen.forEach(function (z, i) {
      var dt = document.createElement('dt'), dd = document.createElement('dd');
      dt.textContent = z[0]; dd.textContent = 'CHF ' + geld(z[1]);
      if ((richtung === 'netto' && i === 2) || (richtung === 'brutto' && i === 0)) { dt.className = dd.className = 'mw-ziel'; }
      dl.appendChild(dt); dl.appendChild(dd);
    });
    aus.appendChild(dl);
  }
  form.addEventListener('input', aktualisiere);
  form.addEventListener('change', aktualisiere);
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  aktualisiere();
})(typeof window !== 'undefined' ? window : this);
