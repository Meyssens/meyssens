/* Rechnung (/werkzeuge/rechnung/) und Offerte (/werkzeuge/offerte/): Positionen mit MWST nach Art. 25 MWSTG,
   Brief als A4-PDF über BriefPDF, Rechnung auf Wunsch mit QR-Zahlteil. Alles im Browser, nichts wird gesendet.
   MWST: Steuer pro Satz auf der Summe der Nettobeträge, auf den Rappen gerundet (das Gesetz kennt keine Rundungsregel;
   die Musterrechnung der ESTV zeigt Rappenbeträge). Runden des Totals auf 5 Rappen nur auf Wunsch (Praxis). */
(function (global) {
  'use strict';
  var SAETZE = [8.1, 2.6, 3.8, 0];        // seit 1.1.2024 (Art. 25 MWSTG); 0 = ohne MWST
  var MAX_POS = 12;

  function zahl(s) {
    s = String(s == null ? '' : s).trim().replace(/['’\s]/g, '').replace(',', '.');
    return /^-?\d+(\.\d+)?$/.test(s) ? parseFloat(s) : NaN;
  }
  function runde(n, auf) { auf = auf || 0.01; return Math.round((n + Number.EPSILON) / auf) * auf; }
  function r2(n) { return Math.round((n + Number.EPSILON) * 100) / 100; }

  // positionen: [{menge, preis, satz}], pflichtig: bool, fuenfer: bool
  function rechne(positionen, pflichtig, fuenfer) {
    var netto = 0, gruppen = {};
    positionen.forEach(function (p) {
      var b = r2(p.menge * p.preis);
      netto = r2(netto + b);
      var s = pflichtig ? p.satz : 0;
      gruppen[s] = r2((gruppen[s] || 0) + b);
    });
    var mwst = [], steuer = 0;
    Object.keys(gruppen).map(Number).sort(function (a, b) { return b - a; }).forEach(function (s) {
      if (!pflichtig || s === 0) return;
      var t = r2(gruppen[s] * s / 100);
      mwst.push({ satz: s, basis: gruppen[s], steuer: t });
      steuer = r2(steuer + t);
    });
    var total = r2(netto + steuer), gerundet = fuenfer ? r2(runde(total, 0.05)) : total;
    return { netto: netto, mwst: mwst, steuer: steuer, total: total, rundung: r2(gerundet - total), zuZahlen: gerundet };
  }

  global.Beleg = { rechne: rechne, zahl: zahl, SAETZE: SAETZE };

  // --- Bedienung ---
  if (typeof document === 'undefined') return;
  var form = document.getElementById('bl-formular');
  if (!form) return;
  var B = global.BriefPDF, ART = form.getAttribute('data-art');   // 'rechnung' oder 'offerte'
  var $ = function (id) { return document.getElementById(id); };
  var liste = $('bl-positionen'), ergebnis = $('bl-ergebnis'), meldungen = $('bl-meldungen'), vorschau = $('bl-vorschau'), letzter = null;
  function wert(id) { var e = $(id); return e ? e.value.trim() : ''; }
  function el(tag, text, klasse) { var e = document.createElement(tag); if (text != null) e.textContent = text; if (klasse) e.className = klasse; return e; }
  function satzText(s) { return String(s).replace('.', ',') + ' %'; }

  var zaehler = 0;
  function neueZeile(p) {
    p = p || {};
    if (liste.children.length >= MAX_POS) return;
    var n = ++zaehler, z = el('div', null, 'bl-pos');
    z.innerHTML =
      '<div class="fgrp bl-text"><label class="flabel" for="bl-t' + n + '">Beschreibung</label><input class="finput" type="text" id="bl-t' + n + '" maxlength="120"></div>' +
      '<div class="fgrp"><label class="flabel" for="bl-m' + n + '">Menge</label><input class="finput" type="text" inputmode="decimal" id="bl-m' + n + '"></div>' +
      '<div class="fgrp"><label class="flabel" for="bl-e' + n + '">Einheit</label><input class="finput" type="text" id="bl-e' + n + '" maxlength="12"></div>' +
      '<div class="fgrp"><label class="flabel" for="bl-p' + n + '">Preis CHF</label><input class="finput" type="text" inputmode="decimal" id="bl-p' + n + '"></div>' +
      '<div class="fgrp"><label class="flabel" for="bl-s' + n + '">MWST</label><select class="fselect finput" id="bl-s' + n + '">' +
      SAETZE.map(function (s) { return '<option value="' + s + '">' + (s ? satzText(s) : 'ohne') + '</option>'; }).join('') + '</select></div>' +
      '<button type="button" class="qr-klein bl-weg" aria-label="Position entfernen">Entfernen</button>';
    z.querySelector('#bl-t' + n).value = p.text || '';
    z.querySelector('#bl-m' + n).value = p.menge || '';
    z.querySelector('#bl-e' + n).value = p.einheit || '';
    z.querySelector('#bl-p' + n).value = p.preis || '';
    z.querySelector('#bl-s' + n).value = String(p.satz != null ? p.satz : 8.1);
    z.querySelector('.bl-weg').addEventListener('click', function () { z.remove(); aktualisiere(); });
    liste.appendChild(z);
  }

  function lesePositionen(f) {
    var aus = [];
    Array.prototype.forEach.call(liste.children, function (z, i) {
      var t = z.querySelector('[id^="bl-t"]').value.trim(), m = zahl(z.querySelector('[id^="bl-m"]').value);
      var e = z.querySelector('[id^="bl-e"]').value.trim(), p = zahl(z.querySelector('[id^="bl-p"]').value);
      var s = parseFloat(z.querySelector('[id^="bl-s"]').value);
      if (!t && !z.querySelector('[id^="bl-m"]').value.trim() && !z.querySelector('[id^="bl-p"]').value.trim()) return;
      if (!t) f.push('Position ' + (i + 1) + ': Beschreibung fehlt.');
      if (!isFinite(m)) f.push('Position ' + (i + 1) + ': Menge als Zahl angeben.');
      if (!isFinite(p)) f.push('Position ' + (i + 1) + ': Preis als Zahl angeben.');
      aus.push({ text: t, menge: isFinite(m) ? m : 0, einheit: e, preis: isFinite(p) ? p : 0, satz: s });
    });
    if (!aus.length) f.push('Bitte mindestens eine Position erfassen.');
    return aus;
  }

  function lese() {
    var f = [], pflichtig = $('bl-pflichtig').checked;
    var pos = lesePositionen(f);
    if (pflichtig && !/^CHE-\d{3}\.\d{3}\.\d{3}( ?MWST)?$/.test(wert('bl-uid'))) f.push('Bitte die MWST-Nummer im Format CHE-123.456.789 MWST angeben.');
    var hinweise = [], leistung = wert('bl-leistungsjahr');
    var jahr = parseInt((wert('bl-datum') || '').slice(0, 4), 10);
    if (pflichtig && (jahr >= 2028 || /20(2[89]|[3-9]\d)/.test(leistung))) hinweise.push('Für Leistungen ab 2028 sind die MWST-Sätze noch nicht festgelegt (Abstimmung vom 29.11.2026 und Vorlagen im Parlament). Bitte die Sätze vor dem Versand prüfen.');
    return { fehler: f, hinweise: hinweise, pos: pos, pflichtig: pflichtig, r: rechne(pos, pflichtig, $('bl-fuenfer') && $('bl-fuenfer').checked) };
  }

  function dokument(d) {
    var r = d.r, nr = wert('bl-nr') || '[Nr.]', titel = ART === 'rechnung' ? 'Rechnung' : 'Offerte';
    var abs = B.leseAdresse(form, 'ab'), emp = B.leseAdresse(form, 'em');
    if (d.pflichtig && wert('bl-uid')) abs.kontakt = [abs.kontakt, wert('bl-uid').replace(/( ?MWST)?$/, ' MWST')].filter(Boolean).join(' · ');
    var zeilen = d.pos.map(function (p, i) {
      return [String(i + 1), p.text, String(p.menge).replace('.', ','), p.einheit, B.geld(p.preis),
              d.pflichtig ? (p.satz ? satzText(p.satz) : 'ohne') : '', B.geld(r2(p.menge * p.preis))];
    });
    var summen = [];
    if (d.pflichtig) {
      summen.push(['Total ohne MWST', B.geld(r.netto)]);
      r.mwst.forEach(function (m) { summen.push(['MWST ' + satzText(m.satz) + ' auf ' + B.geld(m.basis), B.geld(m.steuer)]); });
    }
    if (r.rundung) summen.push(['Rundung', B.geld(r.rundung)]);
    summen.push(['Total CHF', B.geld(r.zuZahlen), true]);
    var absaetze = [], schluss = [];
    var info = [];
    if (ART === 'rechnung') {
      info.push('Rechnungsdatum: ' + (B.datumCH(wert('bl-datum')) || '…'));
      if (wert('bl-leistungsjahr')) info.push('Leistung: ' + wert('bl-leistungsjahr'));
      if (wert('bl-referenz')) info.push('Ihre Referenz: ' + wert('bl-referenz'));
      var tage = parseInt(wert('bl-frist'), 10);
      if (tage > 0) info.push('Zahlbar innert ' + tage + ' Tagen' + (wert('bl-datum') ? ', bis ' + B.datumCH(new Date(Date.parse(wert('bl-datum')) + tage * 86400000)) : ''));
    } else {
      info.push('Datum: ' + (B.datumCH(wert('bl-datum')) || '…'));
      if (wert('bl-referenz')) info.push('Objekt: ' + wert('bl-referenz'));
      if (wert('bl-gueltig')) info.push('Gültig bis ' + B.datumCH(wert('bl-gueltig')));
    }
    absaetze.push(info.join(' · '));
    if (wert('bl-einleitung')) absaetze.push(wert('bl-einleitung'));
    if (!d.pflichtig && $('bl-hinweis-ohne').checked) schluss.push('Nicht MWST-pflichtig.');
    if (ART === 'offerte') {
      if ($('bl-ungefaehr') && $('bl-ungefaehr').checked) schluss.push('Die Preise sind ungefähre Angaben (Kostenschätzung). Zeichnet sich eine wesentliche Überschreitung ab, informieren wir Sie vorher.');
      if ($('bl-unverbindlich') && $('bl-unverbindlich').checked) schluss.push('Diese Offerte ist unverbindlich.');
      else if (wert('bl-gueltig')) schluss.push('An diese Offerte sind wir bis zum ' + B.datumCH(wert('bl-gueltig')) + ' gebunden.');
    }
    if (wert('bl-schluss')) schluss.push(wert('bl-schluss'));
    var qr = null;
    if (ART === 'rechnung' && $('rq-qr').checked) {
      qr = { konto: wert('rq-iban'), ze_name: abs.name, ze_strasse: abs.strasse, ze_nr: abs.nr, ze_plz: abs.plz, ze_ort: abs.ort,
             ze_land: abs.land, waehrung: 'CHF', betrag: r.zuZahlen.toFixed(2), referenz: wert('rq-referenz'),
             mitteilung: 'Rechnung ' + nr, mit_zahler: true, zp_name: emp.name, zp_strasse: emp.strasse, zp_nr: emp.nr,
             zp_plz: emp.plz, zp_ort: emp.ort, zp_land: emp.land };
    }
    return { titel: titel + ' ' + nr, absender: abs, empfaenger: emp, fenster: B.fenster(form), ortDatum: wert('bl-ort'),
             betreff: titel + ' Nr. ' + nr, absaetze: absaetze,
             tabelle: { spalten: [{ titel: 'Pos.', breite: 8 }, { titel: 'Beschreibung', breite: 70 }, { titel: 'Menge', breite: 15, rechts: true },
                                  { titel: '', breite: 3 }, { titel: 'Einheit', breite: 14 }, { titel: 'Preis', breite: 18, rechts: true },
                                  { titel: d.pflichtig ? 'MWST' : '', breite: 15, rechts: true }, { titel: 'Betrag', breite: 22, rechts: true }],
                        zeilen: zeilen.map(function (z) { return [z[0], z[1], z[2], '', z[3], z[4], z[5], z[6]]; }), summen: summen },
             schluss: schluss, gruss: 'Freundliche Grüsse', unterschrift: [wert('bl-unterschrift'), abs.name].filter(Boolean).join(', '),
             fussnote: ART === 'offerte' && $('bl-annahme') && $('bl-annahme').checked ? 'Offerte angenommen: Ort, Datum, Unterschrift ______________________________________' : '',
             qr: qr, r: r };
  }

  function zeigeVorschau(b, d) {
    vorschau.innerHTML = '';
    var kopf = el('div', null, 'br-v-kopf');
    B.adresszeilen(b.absender).forEach(function (z, i) { kopf.appendChild(el(i ? 'span' : 'strong', z)); });
    if (b.absender.kontakt) kopf.appendChild(el('span', b.absender.kontakt));
    var an = el('div', null, 'br-v-an'); B.adresszeilen(b.empfaenger).forEach(function (z) { an.appendChild(el('span', z)); });
    vorschau.appendChild(kopf); vorschau.appendChild(an);
    vorschau.appendChild(el('p', b.ortDatum, 'br-v-datum'));
    vorschau.appendChild(el('p', b.betreff, 'br-v-betreff'));
    b.absaetze.forEach(function (a) { vorschau.appendChild(el('p', a)); });
    var t = el('table', null, 'br-v-tabelle'), tb = el('tbody');
    d.pos.forEach(function (p) {
      var r = el('tr'); r.appendChild(el('td', p.text + ' · ' + String(p.menge).replace('.', ',') + (p.einheit ? ' ' + p.einheit : '') + ' à ' + B.geld(p.preis) + (d.pflichtig ? ' · ' + (p.satz ? satzText(p.satz) : 'ohne MWST') : '')));
      r.appendChild(el('td', 'CHF ' + B.geld(r2(p.menge * p.preis)))); tb.appendChild(r);
    });
    b.tabelle.summen.forEach(function (s) { var r = el('tr', null, s[2] ? 'br-v-total' : ''); r.appendChild(el('td', s[0])); r.appendChild(el('td', 'CHF ' + s[1])); tb.appendChild(r); });
    t.appendChild(tb); vorschau.appendChild(t);
    b.schluss.forEach(function (a) { vorschau.appendChild(el('p', a)); });
    vorschau.appendChild(el('p', b.gruss)); vorschau.appendChild(el('p', b.unterschrift));
    if (b.fussnote) vorschau.appendChild(el('p', b.fussnote, 'br-v-qr'));
    if (b.qr) vorschau.appendChild(el('p', 'QR-Zahlteil über CHF ' + B.geld(b.r.zuZahlen) + ' an der unteren Kante', 'br-v-qr'));
  }

  function aktualisiere() {
    var d = lese();
    $('bl-uid-grp').hidden = !d.pflichtig;
    $('bl-ohne-grp').hidden = d.pflichtig;
    if ($('rq-qr')) $('rq-qr-felder').hidden = !$('rq-qr').checked;
    $('bl-neu').disabled = liste.children.length >= MAX_POS;
    ergebnis.innerHTML = '';
    var p = el('p', null, 'at-zahl'); p.appendChild(el('strong', 'CHF ' + B.geld(d.r.zuZahlen))); p.appendChild(document.createTextNode(' Total'));
    ergebnis.appendChild(p);
    var teile = [d.pos.length + (d.pos.length === 1 ? ' Position' : ' Positionen')];
    if (d.pflichtig) { teile.push('ohne MWST CHF ' + B.geld(d.r.netto)); d.r.mwst.forEach(function (m) { teile.push('MWST ' + satzText(m.satz) + ': CHF ' + B.geld(m.steuer)); }); }
    else teile.push('ohne MWST-Ausweis');
    if (d.r.rundung) teile.push('Rundung ' + B.geld(d.r.rundung));
    ergebnis.appendChild(el('p', teile.join(' · '), 'at-was'));
    meldungen.innerHTML = '';
    var alle = d.fehler.concat(d.hinweise);
    if (alle.length) { var ul = el('ul'); alle.forEach(function (f) { ul.appendChild(el('li', f)); }); meldungen.appendChild(ul); }
    var b = dokument(d);
    zeigeVorschau(b, d);
    letzter = d.fehler.length ? null : b;
    $('bl-pdf').disabled = !letzter;
  }

  // Beispielpositionen aus der Seite (JSON), damit Seite und Tests dieselben Werte nutzen
  var beispiel = JSON.parse(($('bl-beispiel') || { textContent: '[]' }).textContent);
  beispiel.forEach(neueZeile);
  if (!beispiel.length) neueZeile();
  $('bl-neu').addEventListener('click', function () { neueZeile(); aktualisiere(); });
  $('bl-pdf').addEventListener('click', function () {
    if (!letzter) return;
    var r = B.erstelle(letzter);
    if (!r.ok) { meldungen.innerHTML = ''; var ul = el('ul'); r.fehler.forEach(function (f) { ul.appendChild(el('li', f)); }); meldungen.appendChild(ul); return; }
    B.speichere(r.bytes, letzter.titel.replace(/[^\w.-]+/g, '-') + '.pdf');
  });
  $('bl-leeren').addEventListener('click', function () {
    Array.prototype.forEach.call(form.querySelectorAll('input[type="text"], input[type="date"], textarea'), function (e) {
      if (!/-land$/.test(e.id) && e.id !== 'bl-frist') e.value = '';
    });
    liste.innerHTML = ''; neueZeile(); aktualisiere();
  });
  form.addEventListener('input', aktualisiere);
  form.addEventListener('change', aktualisiere);
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  aktualisiere();
})(typeof window !== 'undefined' ? window : this);
