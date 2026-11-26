/* Ferienanspruch-Rechner (/werkzeuge/ferien/): Art. 329a OR (4 Wochen, bis zum vollendeten 20. Altersjahr 5 Wochen,
   anteilig für ein unvollständiges Dienstjahr) und Ferienzuschlag bei Stundenlohn (Ferienwochen / (52 − Ferienwochen)).
   Rechnet im Browser, sendet und speichert nichts. */
(function (global) {
  'use strict';
  var TAG = 86400000;
  function zahl(s) { s = String(s == null ? '' : s).trim().replace(/['’\s]/g, '').replace(',', '.'); return /^\d+(\.\d+)?$/.test(s) ? parseFloat(s) : NaN; }
  function datum(s) { var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || ''); return m ? Date.UTC(+m[1], +m[2] - 1, +m[3]) : NaN; }
  function r1(n) { return Math.round((n + Number.EPSILON) * 10) / 10; }
  function r2(n) { return Math.round((n + Number.EPSILON) * 100) / 100; }
  // Ferientage = Wochen × Arbeitstage pro Woche × (Tage im Zeitraum / Tage im Dienstjahr)
  function ferientage(wochen, tageProWoche, vonIso, bisIso, dienstjahrTage) {
    var tage = Math.round((datum(bisIso) - datum(vonIso)) / TAG) + 1;
    var anteil = Math.min(1, Math.max(0, tage / (dienstjahrTage || 365)));
    return { tage: tage, anteil: anteil, ferientage: r1(wochen * tageProWoche * anteil) };
  }
  function zuschlag(wochen) { return r2(wochen / (52 - wochen) * 100); }
  global.Ferien = { ferientage: ferientage, zuschlag: zuschlag };
  if (typeof document === 'undefined') return;
  var form = document.getElementById('fe-formular');
  if (!form) return;
  var $ = function (id) { return document.getElementById(id); };
  function el(tag, text, k) { var e = document.createElement(tag); if (text != null) e.textContent = text; if (k) e.className = k; return e; }
  function z(n) { return String(n).replace('.', ','); }
  function aktualisiere() {
    var aus = $('fe-ergebnis'), meld = $('fe-meldung'), w = zahl($('fe-wochen').value), t = zahl($('fe-tage').value);
    var jung = $('fe-jung').checked, voll = $('fe-voll').checked;
    $('fe-zeitraum').hidden = voll;
    aus.innerHTML = ''; meld.textContent = '';
    if (!(w > 0 && w < 52) || !(t > 0 && t <= 7)) { meld.textContent = 'Bitte Ferienwochen (z. B. 4) und Arbeitstage pro Woche (z. B. 5 oder 2,5) angeben.'; return; }
    var min = jung ? 5 : 4;
    if (w < min) meld.textContent = 'Gesetzliches Minimum: ' + min + ' Wochen (Art. 329a OR). Der Rechner rechnet mit ' + min + ' Wochen.';
    var wochen = Math.max(w, min);
    var r = voll ? { ferientage: r1(wochen * t), anteil: 1 } : ferientage(wochen, t, $('fe-von').value, $('fe-bis').value, 365);
    if (!voll && (isNaN(datum($('fe-von').value)) || isNaN(datum($('fe-bis').value)) || datum($('fe-bis').value) < datum($('fe-von').value))) {
      meld.textContent = 'Bitte einen gültigen Zeitraum im Dienstjahr angeben.'; return;
    }
    var p = el('p', null, 'at-zahl'); p.appendChild(el('strong', z(r.ferientage))); p.appendChild(document.createTextNode(' Ferientage'));
    aus.appendChild(p);
    aus.appendChild(el('p', z(wochen) + ' Wochen × ' + z(t) + ' Arbeitstage pro Woche' + (voll ? ' für ein ganzes Dienstjahr.' :
      ' × ' + z(r1(r.anteil * 100)) + ' % des Dienstjahrs (' + r.tage + ' von 365 Tagen).'), 'at-was'));
    var proz = zuschlag(wochen), lohn = zahl($('fe-lohn').value);
    aus.appendChild(el('h3', 'Bei Stundenlohn'));
    aus.appendChild(el('p', 'Ferienzuschlag: ' + z(proz.toFixed(2)) + ' % (' + z(wochen) + ' / ' + z(52 - wochen) + ')' +
      (lohn > 0 ? ' · bei CHF ' + lohn.toFixed(2) + ' pro Stunde: CHF ' + r2(lohn * proz / 100).toFixed(2) + ' Zuschlag, zusammen CHF ' + r2(lohn * (1 + proz / 100)).toFixed(2) : ''), 'at-was'));
  }
  form.addEventListener('input', aktualisiere); form.addEventListener('change', aktualisiere);
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  aktualisiere();
})(typeof window !== 'undefined' ? window : this);
