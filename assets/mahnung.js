/* Mahnung mit Verzugszins (/werkzeuge/mahnung/): Berechnung nach Art. 104 OR (effektive Tage / 365, einfacher Zins),
   Brief als PDF über BriefPDF (brief-pdf.js). Alles im Browser, nichts wird gesendet oder gespeichert. */
(function (global) {
  'use strict';
  var TAG = 86400000;

  function zahl(s) {                       // "2'400.50" / "2 400,50" -> 2400.5; ungültig -> NaN
    s = String(s == null ? '' : s).trim().replace(/['’\s]/g, '').replace(',', '.');
    return /^-?\d+(\.\d+)?$/.test(s) ? parseFloat(s) : NaN;
  }
  function datum(s) { var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || ''); return m ? Date.UTC(+m[1], +m[2] - 1, +m[3]) : NaN; }
  function runde(n) { return Math.round((n + Number.EPSILON) * 100) / 100; }

  // Zinstage: Kalendertage vom Verfalltag bzw. Eingang der Mahnung bis zum Stichtag; Zins = Betrag × Satz × Tage / 365
  function verzugszins(betrag, satz, verzugIso, stichtagIso) {
    var tage = Math.round((datum(stichtagIso) - datum(verzugIso)) / TAG);
    if (!isFinite(tage) || tage < 0) tage = 0;
    return { tage: tage, zins: runde(betrag * satz / 100 * tage / 365) };
  }

  var TEXTE = {
    1: { titel: 'Zahlungserinnerung', ein: function (d) {
      return 'Sicher ist es Ihnen entgangen: Unsere Rechnung Nr. ' + d.nr + ' vom ' + d.rdatum + ' über CHF ' + d.betrag +
             ' ist noch offen. Wir bitten Sie, den Betrag bis zum ' + d.frist + ' zu überweisen.'; },
      schluss: 'Falls Sie bereits bezahlt haben, betrachten Sie dieses Schreiben bitte als gegenstandslos. Bei Fragen sind wir gerne für Sie da.' },
    2: { titel: 'Mahnung', ein: function (d) {
      return 'Unsere Rechnung Nr. ' + d.nr + ' vom ' + d.rdatum + ' über CHF ' + d.betrag + ' ist trotz Fälligkeit noch nicht bezahlt. ' +
             'Wir bitten Sie, den offenen Betrag bis zum ' + d.frist + ' zu überweisen.'; },
      schluss: 'Falls sich Ihre Zahlung mit diesem Schreiben gekreuzt hat, danken wir Ihnen und bitten Sie, es als gegenstandslos zu betrachten.' },
    3: { titel: 'Letzte Mahnung', ein: function (d) {
      return 'Trotz unserer bisherigen Schreiben ist unsere Rechnung Nr. ' + d.nr + ' vom ' + d.rdatum + ' über CHF ' + d.betrag +
             ' noch offen. Wir fordern Sie auf, den Betrag bis spätestens ' + d.frist + ' zu bezahlen.'; },
      schluss: 'Erhalten wir die Zahlung nicht fristgerecht, werden wir ohne weitere Mitteilung die Betreibung einleiten.' }
  };

  global.Mahnung = { verzugszins: verzugszins, zahl: zahl };

  // --- Bedienung ---
  if (typeof document === 'undefined') return;
  var form = document.getElementById('mg-formular');
  if (!form) return;
  var B = global.BriefPDF;
  var $ = function (id) { return document.getElementById(id); };
  var ergebnis = $('mg-ergebnis'), meldungen = $('mg-meldungen'), vorschau = $('mg-vorschau'), letzter = null;

  function wert(id) { var e = $(id); return e ? e.value.trim() : ''; }
  function el(tag, text, klasse) { var e = document.createElement(tag); if (text != null) e.textContent = text; if (klasse) e.className = klasse; return e; }

  function lese() {
    var f = [], betrag = zahl(wert('mg-betrag')), satz = zahl(wert('mg-satz'));
    var art = form.querySelector('input[name="mg-art"]:checked').value;
    if (!(betrag > 0)) f.push('Bitte den offenen Betrag in CHF angeben.');
    if (!(satz >= 0) || satz > 30) f.push('Bitte einen Zinssatz zwischen 0 und 30 % angeben.');
    if (isNaN(datum(wert('mg-verzug')))) f.push('Bitte ' + (art === 'frist' ? 'den Verfalltag' : 'das Eingangsdatum der Mahnung') + ' angeben.');
    if (isNaN(datum(wert('mg-stichtag')))) f.push('Bitte den Stichtag angeben.');
    if (!f.length && datum(wert('mg-stichtag')) < datum(wert('mg-verzug'))) f.push('Der Stichtag liegt vor dem Verzugsbeginn.');
    var gebuehr = 0;
    if ($('mg-gebuehr-ja').checked) {
      gebuehr = zahl(wert('mg-gebuehr'));
      if (!(gebuehr > 0)) { f.push('Bitte die vereinbarte Mahngebühr angeben oder das Häkchen entfernen.'); gebuehr = 0; }
    }
    var z = verzugszins(betrag > 0 ? betrag : 0, satz >= 0 ? satz : 0, wert('mg-verzug'), wert('mg-stichtag'));
    return { fehler: f, betrag: betrag, satz: satz, art: art, z: z, gebuehr: gebuehr, stufe: +wert('mg-stufe') };
  }

  function brief(d) {
    var t = TEXTE[d.stufe], zeigen = $('mg-zins-zeigen').checked && d.z.zins > 0;
    var info = { nr: wert('mg-nr') || '[Nr.]', rdatum: B.datumCH(wert('mg-rdatum')) || '[Datum]', betrag: B.geld(d.betrag || 0),
                 frist: B.datumCH(wert('mg-frist')) || '[Frist]' };
    var zeilen = [['Rechnung Nr. ' + info.nr + ' vom ' + info.rdatum, 'CHF', B.geld(d.betrag || 0)]];
    if (zeigen) zeilen.push(['Verzugszins ' + String(d.satz).replace('.', ',') + ' % vom ' + B.datumCH(wert('mg-verzug')) + ' bis ' +
                             B.datumCH(wert('mg-stichtag')) + ' (' + d.z.tage + ' Tage)', 'CHF', B.geld(d.z.zins)]);
    if (d.gebuehr) zeilen.push(['Mahngebühr gemäss Vereinbarung', 'CHF', B.geld(d.gebuehr)]);
    var total = (d.betrag || 0) + (zeigen ? d.z.zins : 0) + d.gebuehr;
    var absaetze = [t.ein(info)];
    if (zeigen) absaetze.push('Seit dem ' + (d.art === 'frist' ? 'Ablauf des ' : '') + B.datumCH(wert('mg-verzug')) +
      ' schulden Sie einen Verzugszins von ' + String(d.satz).replace('.', ',') + ' % pro Jahr (Art. 104 OR). Bis zum ' +
      B.datumCH(wert('mg-stichtag')) + ' beträgt er CHF ' + B.geld(d.z.zins) + '.');
    var abs = B.leseAdresse(form, 'ab'), emp = B.leseAdresse(form, 'em'), qr = null;
    if ($('mq-qr').checked) {
      qr = { konto: wert('mq-iban'), ze_name: abs.name, ze_strasse: abs.strasse, ze_nr: abs.nr, ze_plz: abs.plz, ze_ort: abs.ort,
             ze_land: abs.land, waehrung: 'CHF', betrag: total.toFixed(2), referenz: wert('mq-referenz'),
             mitteilung: t.titel + ' Rechnung ' + info.nr, mit_zahler: true, zp_name: emp.name, zp_strasse: emp.strasse, zp_nr: emp.nr,
             zp_plz: emp.plz, zp_ort: emp.ort, zp_land: emp.land };
    }
    return { titel: t.titel + ' ' + info.nr, absender: abs, empfaenger: emp, fenster: B.fenster(form), ortDatum: wert('mg-ortdatum'),
             betreff: t.titel + ': Rechnung Nr. ' + info.nr, absaetze: absaetze,
             tabelle: { spalten: [{ titel: 'Position', breite: 135 }, { titel: '', breite: 10 }, { titel: 'Betrag', breite: 20, rechts: true }],
                        zeilen: zeilen, summen: [['Total offen CHF', B.geld(total), true]] },
             schluss: [t.schluss], gruss: 'Freundliche Grüsse', unterschrift: [wert('mg-unterschrift'), abs.name].filter(Boolean).join(', '),
             qr: qr, total: total };
  }

  function zeigeVorschau(b) {
    vorschau.innerHTML = '';
    var kopf = el('div', null, 'br-v-kopf');
    B.adresszeilen(b.absender).forEach(function (z, i) { kopf.appendChild(el(i ? 'span' : 'strong', z)); });
    var an = el('div', null, 'br-v-an'); B.adresszeilen(b.empfaenger).forEach(function (z) { an.appendChild(el('span', z)); });
    vorschau.appendChild(kopf); vorschau.appendChild(an);
    vorschau.appendChild(el('p', b.ortDatum, 'br-v-datum'));
    vorschau.appendChild(el('p', b.betreff, 'br-v-betreff'));
    b.absaetze.forEach(function (a) { vorschau.appendChild(el('p', a)); });
    var t = el('table', null, 'br-v-tabelle'), tb = el('tbody');
    b.tabelle.zeilen.forEach(function (z) { var r = el('tr'); r.appendChild(el('td', z[0])); r.appendChild(el('td', 'CHF ' + z[2])); tb.appendChild(r); });
    var s = el('tr', null, 'br-v-total'); s.appendChild(el('td', 'Total offen')); s.appendChild(el('td', 'CHF ' + b.tabelle.summen[0][1])); tb.appendChild(s);
    t.appendChild(tb); vorschau.appendChild(t);
    b.schluss.forEach(function (a) { vorschau.appendChild(el('p', a)); });
    vorschau.appendChild(el('p', b.gruss)); vorschau.appendChild(el('p', b.unterschrift));
    if (b.qr) vorschau.appendChild(el('p', 'QR-Zahlteil über CHF ' + B.geld(b.total) + ' an der unteren Kante', 'br-v-qr'));
  }

  function aktualisiere() {
    var d = lese();
    $('mg-verzug-label').textContent = d.art === 'frist' ? 'Verfalltag (letzter Tag der Zahlungsfrist)' : 'Eingang der ersten Mahnung beim Kunden';
    $('mg-gebuehr-grp').hidden = !$('mg-gebuehr-ja').checked;
    $('mq-qr-felder').hidden = !$('mq-qr').checked;
    ergebnis.innerHTML = '';
    var p = el('p', null, 'at-zahl'); p.appendChild(el('strong', 'CHF ' + B.geld(d.z.zins))); p.appendChild(document.createTextNode(' Verzugszins'));
    ergebnis.appendChild(p);
    ergebnis.appendChild(el('p', d.z.tage + ' Tage zu ' + String(d.satz >= 0 ? d.satz : 0).replace('.', ',') + ' % pro Jahr auf CHF ' +
      B.geld(d.betrag > 0 ? d.betrag : 0) + (d.gebuehr ? ', dazu Mahngebühr CHF ' + B.geld(d.gebuehr) : '') + '.', 'at-was'));
    var b = brief(d);
    ergebnis.appendChild(el('p', 'Total offen am ' + (B.datumCH(wert('mg-stichtag')) || '…') + ': CHF ' + B.geld(b.total), 'mg-total-zeile'));
    meldungen.innerHTML = '';
    if (d.fehler.length) {
      var ul = el('ul'); d.fehler.forEach(function (f) { ul.appendChild(el('li', f)); }); meldungen.appendChild(ul);
    }
    zeigeVorschau(b);
    letzter = d.fehler.length ? null : b;
    $('mg-pdf').disabled = !letzter;
  }

  $('mg-pdf').addEventListener('click', function () {
    if (!letzter) return;
    var r = B.erstelle(letzter);
    if (!r.ok) { meldungen.innerHTML = ''; var ul = el('ul'); r.fehler.forEach(function (f) { ul.appendChild(el('li', f)); }); meldungen.appendChild(ul); return; }
    B.speichere(r.bytes, (letzter.titel || 'Mahnung').replace(/[^\w.-]+/g, '-') + '.pdf');
  });
  $('mg-leeren').addEventListener('click', function () {
    Array.prototype.forEach.call(form.querySelectorAll('input[type="text"], input[type="date"]'), function (e) {
      if (e.id !== 'mg-satz' && e.id !== 'ab-land' && e.id !== 'em-land') e.value = '';
    });
    aktualisiere();
  });
  form.addEventListener('input', aktualisiere);
  form.addEventListener('change', aktualisiere);
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  aktualisiere();
})(typeof window !== 'undefined' ? window : this);
