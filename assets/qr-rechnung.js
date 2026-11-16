/* QR-Rechnung erstellen (meyssens.ch/werkzeuge/qr-rechnung/)
   Läuft vollständig im Browser: keine Übertragung der Eingaben, kein Speichern, keine externen Dienste.
   Grundlage: Schweizer Implementation Guidelines QR-Rechnung der SIX, Version 2.4 (gültig ab 14.11.2026).
   QR-Code: qrcode-generator (assets/qrcode.js, MIT), Fehlerkorrekturstufe M, UTF-8.
   Kern (Prüfung, QR-Inhalt, Layout, SVG, PDF) ist ohne Browser nutzbar (Tests), die Bedienung nur mit Formular. */
(function (global) {
  'use strict';

  var PT = 25.4 / 72;           // 1 Punkt in mm
  var MM = 72 / 25.4;           // 1 mm in Punkt
  var HOEHE = 105, BREITE = 210, QUITTUNG = 62;

  // Zeichenbreiten Helvetica und Helvetica-Bold (Adobe AFM, 1/1000 em) für U+0020 bis U+007E
  var W_NORMAL = [278,278,355,556,556,889,667,191,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,
    278,278,584,584,584,556,1015,667,667,722,722,667,611,778,722,278,500,667,556,833,722,778,667,778,722,667,611,722,667,
    944,667,667,611,278,278,278,469,556,333,556,556,500,556,556,278,556,556,222,222,500,222,833,556,556,556,556,333,500,
    278,556,500,722,500,500,500,334,260,334,584];
  var W_FETT = [278,333,474,556,556,889,722,238,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,
    333,333,584,584,584,611,975,722,722,722,722,667,611,778,722,278,556,722,611,833,722,778,667,778,722,667,611,722,667,
    944,667,667,611,333,278,333,584,556,333,556,611,556,611,556,333,611,611,278,278,556,278,889,611,611,611,611,389,556,
    333,611,556,778,556,556,500,389,280,389,584];

  // Zeichen ausserhalb von U+0020–U+007E und U+00A0–U+00FF, die das Werkzeug zulässt (SIX-Zeichensatz und im PDF darstellbar)
  var ZUSATZ = { '€': 0x80, 'Š': 0x8A, 'Œ': 0x8C, 'Ž': 0x8E, 'š': 0x9A, 'œ': 0x9C, 'ž': 0x9E, 'Ÿ': 0x9F };
  // Typografische Zeichen, die nicht zum SIX-Zeichensatz gehören, werden ersetzt
  var ERSATZ = { '‘': "'", '’': "'", '‚': "'", '‛': "'", '′': "'", '“': '"', '”': '"', '„': '"',
    '–': '-', '—': '-', '−': '-', '…': '...', ' ': ' ', ' ': ' ', ' ': ' ', ' ': ' ', '\t': ' ' };

  function bereinige(s) {
    s = String(s == null ? '' : s).replace(/[\r\n]+/g, ' ');
    var aus = '';
    for (var i = 0; i < s.length; i++) aus += ERSATZ.hasOwnProperty(s[i]) ? ERSATZ[s[i]] : s[i];
    return aus.replace(/ {2,}/g, ' ').trim();
  }

  function zeichenErlaubt(ch) {
    var c = ch.charCodeAt(0);
    return (c >= 0x20 && c <= 0x7E) || (c >= 0xA0 && c <= 0xFF) || ZUSATZ.hasOwnProperty(ch);
  }

  function unerlaubt(s) {
    var falsch = [];
    for (var i = 0; i < s.length; i++) if (!zeichenErlaubt(s[i]) && falsch.indexOf(s[i]) < 0) falsch.push(s[i]);
    return falsch;
  }

  // Breite eines Textes in mm
  function breite(text, pt, fett) {
    var t = fett ? W_FETT : W_NORMAL, w = 0;
    for (var i = 0; i < text.length; i++) {
      var c = text.charCodeAt(i);
      if (c < 32 || c > 126) {
        var b = text[i].normalize ? text[i].normalize('NFD').charCodeAt(0) : 0;
        c = b >= 32 && b <= 126 ? b : -1;
      }
      w += c < 0 ? 556 : t[c - 32];
    }
    return w / 1000 * pt * PT;
  }

  function umbrechen(text, max, pt, fett) {
    var zeilen = [], zeile = '';
    text.split(' ').forEach(function (wort) {
      var probe = zeile ? zeile + ' ' + wort : wort;
      if (breite(probe, pt, fett) <= max) { zeile = probe; return; }
      if (zeile) zeilen.push(zeile);
      zeile = '';
      while (breite(wort, pt, fett) > max) {         // sehr lange Wörter hart trennen
        var n = wort.length;
        while (n > 1 && breite(wort.slice(0, n), pt, fett) > max) n--;
        zeilen.push(wort.slice(0, n));
        wort = wort.slice(n);
      }
      zeile = wort;
    });
    if (zeile) zeilen.push(zeile);
    return zeilen;
  }

  // --- Prüfziffern ---
  function mod97(ziffern) {
    var rest = 0;
    for (var i = 0; i < ziffern.length; i += 7) rest = parseInt(String(rest) + ziffern.slice(i, i + 7), 10) % 97;
    return rest;
  }
  function alsZiffern(s) {
    return s.replace(/[A-Z]/g, function (b) { return String(b.charCodeAt(0) - 55); });
  }
  function ibanGueltig(iban) {
    return mod97(alsZiffern(iban.slice(4) + iban.slice(0, 4))) === 1;
  }
  function istQrIban(iban) {
    var iid = parseInt(iban.slice(4, 9), 10);
    return /^\d{5}$/.test(iban.slice(4, 9)) && iid >= 30000 && iid <= 31999;
  }
  var TAFEL = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5];
  function mod10(ziffern) {
    var u = 0;
    for (var i = 0; i < ziffern.length; i++) u = TAFEL[(u + parseInt(ziffern[i], 10)) % 10];
    return (10 - u) % 10;
  }
  function qrReferenz(nummer) {
    // 26 Ziffern (links mit Nullen aufgefüllt) plus Prüfziffer nach Modulo 10 rekursiv (Anhang B)
    var z = String(nummer).replace(/\s/g, '');
    if (!/^\d{1,26}$/.test(z) || /^0+$/.test(z)) return null;
    z = ('00000000000000000000000000' + z).slice(-26);
    return z + mod10(z);
  }
  function scorReferenz(basis) {
    // Creditor Reference ISO 11649: RF + Prüfziffern (Modulo 97-10) + 1 bis 21 alphanumerische Zeichen
    var b = String(basis).replace(/\s/g, '').toUpperCase();
    if (!/^[A-Z0-9]{1,21}$/.test(b)) return null;
    var p = 98 - mod97(alsZiffern(b + 'RF00'));
    return 'RF' + (p < 10 ? '0' : '') + p + b;
  }
  function scorGueltig(r) {
    return /^RF\d{2}[A-Z0-9]{1,21}$/.test(r) && mod97(alsZiffern(r.slice(4) + r.slice(0, 4))) === 1;
  }

  // --- Darstellung im Sichtteil ---
  function gruppen(s, n) { return s.replace(new RegExp('(.{' + n + '})', 'g'), '$1 ').trim(); }
  function zeigeIban(i) { return gruppen(i, 4); }
  function zeigeReferenz(typ, r) {
    if (typ === 'QRR') return r.slice(0, 2) + ' ' + gruppen(r.slice(2), 5);
    return gruppen(r, 4);
  }
  function zeigeBetrag(b) {
    var teile = b.split('.');
    return teile[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + '.' + teile[1];
  }

  // --- Prüfung der Eingaben ---
  var LAENGE = { name: 70, strasse: 70, nr: 16, plz: 16, ort: 35 };

  function pruefe(e) {
    var f = [], d = {};
    function fehler(feld, text) { f.push({ feld: feld, text: text }); }
    function text(feld, wert, max, pflicht, bezeichnung) {
      var v = bereinige(wert);
      if (!v) { if (pflicht) fehler(feld, bezeichnung + ' fehlt.'); return ''; }
      if (v.length > max) fehler(feld, bezeichnung + ': höchstens ' + max + ' Zeichen (jetzt ' + v.length + ').');
      var falsch = unerlaubt(v);
      if (falsch.length) {
        // Latin Extended-A und Ș/Ț erlaubt die SIX, dieses Werkzeug kann sie im PDF aber nicht darstellen
        var six = falsch.every(function (ch) { var c = ch.charCodeAt(0); return (c >= 0x100 && c <= 0x17F) || (c >= 0x218 && c <= 0x21B); });
        fehler(feld, bezeichnung + ': Zeichen «' + falsch.join('», «') + (six
          ? '» kann dieses Werkzeug nicht darstellen. Bitte durch einen Buchstaben ohne Zeichen ersetzen.'
          : '» ist für die QR-Rechnung nicht zulässig.'));
      }
      return v;
    }
    function adresse(p, pflicht, wer) {
      var a = {
        name: text(p + 'name', e[p + 'name'], LAENGE.name, pflicht, 'Name ' + wer),
        strasse: text(p + 'strasse', e[p + 'strasse'], LAENGE.strasse, false, 'Strasse ' + wer),
        nr: text(p + 'nr', e[p + 'nr'], LAENGE.nr, false, 'Hausnummer ' + wer),
        plz: text(p + 'plz', e[p + 'plz'], LAENGE.plz, pflicht, 'Postleitzahl ' + wer),
        ort: text(p + 'ort', e[p + 'ort'], LAENGE.ort, pflicht, 'Ort ' + wer),
        land: bereinige(e[p + 'land'] || 'CH').toUpperCase()
      };
      if (a.nr && !a.strasse) fehler(p + 'strasse', 'Strasse ' + wer + ' fehlt (die Hausnummer steht allein).');
      if (/^[A-Z]{1,3}-/.test(a.plz)) fehler(p + 'plz', 'Postleitzahl ' + wer + ' ohne vorangestellten Landescode angeben.');
      if (!/^[A-Z]{2}$/.test(a.land)) fehler(p + 'land', 'Land ' + wer + ': zweistelliger Landescode, zum Beispiel CH.');
      return a;
    }

    var konto = String(e.konto || '').replace(/\s/g, '').toUpperCase();
    if (!konto) fehler('konto', 'IBAN oder QR-IBAN fehlt.');
    else if (!/^(CH|LI)\d{2}[0-9A-Z]{17}$/.test(konto)) fehler('konto', 'Die IBAN muss mit CH oder LI beginnen und 21 Zeichen haben.');
    else if (!ibanGueltig(konto)) fehler('konto', 'Die Prüfziffer der IBAN stimmt nicht. Bitte Tippfehler prüfen.');
    d.konto = konto;
    d.qrIban = /^(CH|LI)/.test(konto) && konto.length === 21 && istQrIban(konto);

    d.empfaenger = adresse('ze_', true, 'Zahlungsempfänger');

    d.waehrung = e.waehrung === 'EUR' ? 'EUR' : 'CHF';
    var betrag = String(e.betrag || '').replace(/['’\s]/g, '').replace(',', '.');
    if (betrag) {
      if (!/^\d{1,9}(\.\d{1,2})?$/.test(betrag)) fehler('betrag', 'Betrag: Zahl mit höchstens zwei Nachkommastellen, zum Beispiel 1590.00.');
      else {
        var cent = Math.round(parseFloat(betrag) * 100);
        if (cent < 1) fehler('betrag', 'Der Betrag muss mindestens 0.01 betragen oder leer bleiben.');
        else betrag = (cent / 100).toFixed(2);
      }
    }
    d.betrag = betrag;

    var ref = String(e.referenz || '').replace(/\s/g, '').toUpperCase();
    if (!ref) d.referenzTyp = 'NON';
    else if (/^RF/.test(ref)) d.referenzTyp = 'SCOR';
    else d.referenzTyp = 'QRR';
    d.referenz = ref;
    if (d.qrIban) {
      if (d.referenzTyp !== 'QRR') fehler('referenz', 'Mit einer QR-IBAN ist eine QR-Referenz (27 Ziffern) Pflicht.');
      if (d.waehrung !== 'CHF') fehler('waehrung', 'QR-IBAN und QR-Referenz sind seit Version 2.4 nur noch für Rechnungen in CHF zulässig.');
    } else if (d.referenzTyp === 'QRR' && konto) {
      fehler('referenz', /^\d+$/.test(ref) ? 'Eine QR-Referenz ist nur mit einer QR-IBAN zulässig. Mit einer normalen IBAN: RF-Referenz oder keine Referenz.'
        : 'Referenz unbekannt: RF-Referenz (beginnt mit RF) oder bei QR-IBAN 27 Ziffern.');
    }
    if (d.referenzTyp === 'QRR' && d.qrIban) {
      if (!/^\d{27}$/.test(ref)) fehler('referenz', 'Die QR-Referenz hat genau 27 Ziffern (26 plus Prüfziffer).');
      else if (/^0+$/.test(ref)) fehler('referenz', 'Die QR-Referenz darf nicht nur aus Nullen bestehen.');
      else if (mod10(ref.slice(0, 26)) !== parseInt(ref[26], 10)) fehler('referenz', 'Die Prüfziffer der QR-Referenz stimmt nicht.');
    }
    if (d.referenzTyp === 'SCOR' && (ref.length < 5 || ref.length > 25 || !scorGueltig(ref)))
      fehler('referenz', 'Die RF-Referenz ist ungültig (5 bis 25 Zeichen, Prüfziffer an 3. und 4. Stelle).');

    d.mitteilung = text('mitteilung', e.mitteilung, 140, false, 'Zusätzliche Informationen');

    d.zahler = e.mit_zahler ? adresse('zp_', true, 'Zahlungspflichtiger') : null;

    if (!f.length) {
      d.inhalt = nutzdaten(d);
      if (d.inhalt.length > 997) fehler('mitteilung', 'Der Inhalt des QR-Codes ist zu lang (höchstens 997 Zeichen).');
    }
    return { ok: !f.length, fehler: f, daten: d };
  }

  // --- Inhalt des Swiss QR Codes (Kapitel 4.2.2), Zeilen mit CR+LF, ohne Zeilenschaltung am Ende ---
  function adressZeilen(a) {
    return a ? ['S', a.name, a.strasse, a.nr, a.plz, a.ort, a.land] : ['', '', '', '', '', '', ''];
  }
  function nutzdaten(d) {
    var z = ['SPC', '0200', '1', d.konto].concat(adressZeilen(d.empfaenger), ['', '', '', '', '', '', ''],
      [d.betrag, d.waehrung], adressZeilen(d.zahler), [d.referenzTyp, d.referenzTyp === 'NON' ? '' : d.referenz, d.mitteilung, 'EPD']);
    return z.join('\r\n');
  }

  function qrMatrix(inhalt) {
    var lib = global.qrcode;
    lib.stringToBytes = lib.stringToBytesFuncs['UTF-8'];
    var qr = lib(0, 'M');
    qr.addData(inhalt, 'Byte');
    qr.make();
    var n = qr.getModuleCount(), m = [];
    if (n > 117) throw new Error('QR-Code grösser als Version 25');
    for (var r = 0; r < n; r++) { var zeile = []; for (var c = 0; c < n; c++) zeile.push(qr.isDark(r, c)); m.push(zeile); }
    return m;
  }

  // --- Layout in mm, Ursprung oben links am Zahlteil mit Empfangsschein (210 x 105 mm) ---
  function anzeigeAdresse(a) {
    var z = [a.name];
    if (a.strasse) z.push(a.strasse + (a.nr ? ' ' + a.nr : ''));
    z.push((a.land !== 'CH' ? a.land + '-' : '') + a.plz + ' ' + a.ort);
    return z;
  }

  function entwurf(d, matrix) {
    var ops = [];
    function txt(x, y, pt, fett, t, anker) { ops.push({ t: 'text', x: x, y: y, pt: pt, fett: !!fett, text: t, anker: anker || 'start' }); }
    function linie(x1, y1, x2, y2, w) { ops.push({ t: 'linie', x1: x1, y1: y1, x2: x2, y2: y2, w: w }); }
    function ecken(x, y, w, h) {
      var s = 0.75;                                    // 0,75 Pkt.
      [[x, y, 1, 1], [x + w, y, -1, 1], [x, y + h, 1, -1], [x + w, y + h, -1, -1]].forEach(function (e) {
        linie(e[0], e[1], e[0] + 3 * e[2], e[1], s);
        linie(e[0], e[1], e[0], e[1] + 2 * e[3], s);
      });
    }
    // Block mit Überschrift und Werten; gibt neue y-Position zurück
    function block(x, y, max, kopfPt, wertPt, ueberschrift, werte, abstand) {
      var a = kopfPt * PT, b = wertPt * PT * 1.18;
      txt(x, y + kopfPt * 0.75 * PT, kopfPt, true, ueberschrift);
      y += a * 1.25;
      werte.forEach(function (w) {
        umbrechen(w, max, wertPt, false).forEach(function (zeile) { txt(x, y + wertPt * 0.75 * PT, wertPt, false, zeile); y += b; });
      });
      return y + abstand;
    }

    // Trennlinien und Hinweis (Kapitel 3.7: PDF zum elektronischen Versand)
    linie(0, 0, BREITE, 0, 0.5);
    linie(QUITTUNG, 0, QUITTUNG, HOEHE, 0.5);
    txt(BREITE / 2, -1.6, 7, false, 'Vor der Einzahlung abzutrennen', 'middle');

    var konto = [zeigeIban(d.konto)].concat(anzeigeAdresse(d.empfaenger));
    var ref = d.referenzTyp !== 'NON' ? zeigeReferenz(d.referenzTyp, d.referenz) : null;

    // Empfangsschein: Titel 11 Pkt. fett, Überschriften 6 Pkt. fett, Werte 8 Pkt.
    var x = 5, max = 52, y;
    txt(x, 5 + 11 * 0.72 * PT, 11, true, 'Empfangsschein');
    y = 12;
    y = block(x, y, max, 6, 8, 'Konto / Zahlbar an', konto, 2.2);
    if (ref) y = block(x, y, max, 6, 8, 'Referenz', [ref], 2.2);
    if (d.zahler) y = block(x, y, max, 6, 8, 'Zahlbar durch', anzeigeAdresse(d.zahler), 0);
    else { txt(x, y + 6 * 0.75 * PT, 6, true, 'Zahlbar durch (Name/Adresse)'); y += 3; ecken(x, y, 52, 20); y += 20; }
    var quittungEnde = y;
    txt(x, 70, 6, true, 'Währung'); txt(x + 12, 70, 6, true, 'Betrag');
    txt(x, 73.6, 8, false, d.waehrung);
    if (d.betrag) txt(x + 12, 73.6, 8, false, zeigeBetrag(d.betrag));
    else ecken(27, 71.5, 30, 10);
    txt(QUITTUNG - 5, 84.5, 6, true, 'Annahmestelle', 'end');

    // Zahlteil: Titel 11 Pkt. fett, Überschriften 8 Pkt. fett, Werte 10 Pkt.
    var px = QUITTUNG + 5;
    txt(px, 5 + 11 * 0.72 * PT, 11, true, 'Zahlteil');
    ops.push({ t: 'qr', x: px, y: 17, groesse: 46, matrix: matrix });
    ops.push({ t: 'kreuz', x: px + 23 - 3.5, y: 17 + 23 - 3.5 });
    txt(px, 70.8, 8, true, 'Währung'); txt(px + 13, 70.8, 8, true, 'Betrag');
    txt(px, 75.4, 10, false, d.waehrung);
    if (d.betrag) txt(px + 13, 75.4, 10, false, zeigeBetrag(d.betrag));
    else ecken(px + 11, 72, 40, 15);       // Abbildung 5: unter «Betrag», bis zum Bereich Angaben

    var ax = px + 46 + 5, amax = BREITE - 5 - ax;
    y = 5;
    y = block(ax, y, amax, 8, 10, 'Konto / Zahlbar an', konto, 2.6);
    if (ref) y = block(ax, y, amax, 8, 10, 'Referenz', [ref], 2.6);
    if (d.mitteilung) y = block(ax, y, amax, 8, 10, 'Zusätzliche Informationen', [d.mitteilung], 2.6);
    if (d.zahler) y = block(ax, y, amax, 8, 10, 'Zahlbar durch', anzeigeAdresse(d.zahler), 0);
    else { txt(ax, y + 8 * 0.75 * PT, 8, true, 'Zahlbar durch (Name/Adresse)'); y += 4; ecken(ax, y, 65, 25); y += 25; }

    var platz = [];
    if (quittungEnde > 67.5) platz.push('Empfangsschein');
    if (y > 95) platz.push('Zahlteil');
    return { ops: ops, zuLang: platz };
  }

  // --- SVG (Vorschau und Download), Einheiten in mm ---
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function zahl(n) { return (Math.round(n * 1000) / 1000).toString(); }
  function qrPfad(op) {
    var n = op.matrix.length, m = op.groesse / n, p = '';
    for (var r = 0; r < n; r++) {
      for (var c = 0; c < n; c++) {
        if (!op.matrix[r][c]) continue;
        var s = c; while (c + 1 < n && op.matrix[r][c + 1]) c++;
        p += 'M' + zahl(op.x + s * m) + ' ' + zahl(op.y + r * m) + 'h' + zahl((c - s + 1) * m) + 'v' + zahl(m) + 'h-' + zahl((c - s + 1) * m) + 'z';
      }
    }
    return p;
  }
  function kreuzTeile(x, y) {
    // 7 x 7 mm: weisser Rand, schwarzes Quadrat, weisses Kreuz
    var i = 0.35, q = 7 - 2 * i, bw = q * 3.3 / 18.4, bl = q * 11 / 18.4, m = 3.5;
    return [
      { x: x, y: y, w: 7, h: 7, farbe: 'w' },
      { x: x + i, y: y + i, w: q, h: q, farbe: 's' },
      { x: x + m - bw / 2, y: y + m - bl / 2, w: bw, h: bl, farbe: 'w' },
      { x: x + m - bl / 2, y: y + m - bw / 2, w: bl, h: bw, farbe: 'w' }
    ];
  }
  function svg(entw, mitKopf) {
    var teile = [];
    entw.ops.forEach(function (o) {
      if (o.t === 'text') teile.push('<text x="' + zahl(o.x) + '" y="' + zahl(o.y) + '" font-size="' + zahl(o.pt * PT) + '"' +
        (o.fett ? ' font-weight="bold"' : '') + (o.anker !== 'start' ? ' text-anchor="' + o.anker + '"' : '') + '>' + esc(o.text) + '</text>');
      else if (o.t === 'linie') teile.push('<line x1="' + zahl(o.x1) + '" y1="' + zahl(o.y1) + '" x2="' + zahl(o.x2) + '" y2="' + zahl(o.y2) +
        '" stroke="#000" stroke-width="' + zahl(o.w * PT) + '"/>');
      else if (o.t === 'qr') teile.push('<path fill="#000" d="' + qrPfad(o) + '"/>');
      else if (o.t === 'kreuz') kreuzTeile(o.x, o.y).forEach(function (k) {
        teile.push('<rect x="' + zahl(k.x) + '" y="' + zahl(k.y) + '" width="' + zahl(k.w) + '" height="' + zahl(k.h) + '" fill="' + (k.farbe === 's' ? '#000' : '#fff') + '"/>');
      });
    });
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -6 210 111" width="210mm" height="111mm"' +
      (mitKopf ? '' : ' role="img" aria-label="Vorschau des Zahlteils mit Empfangsschein"') + '>' +
      '<rect x="0" y="-6" width="210" height="111" fill="#fff"/>' +
      '<g font-family="Helvetica, Arial, \'Liberation Sans\', sans-serif" fill="#000">' + teile.join('') + '</g></svg>';
  }

  // --- PDF (A4, Zahlteil unten), Schriften Helvetica und Helvetica-Bold, WinAnsiEncoding ---
  function pdfText(s) {
    var aus = '';
    for (var i = 0; i < s.length; i++) {
      var ch = s[i], c = ZUSATZ.hasOwnProperty(ch) ? ZUSATZ[ch] : ch.charCodeAt(0);
      if (c > 255) c = 63;
      if (c === 40 || c === 41 || c === 92) aus += '\\';
      aus += String.fromCharCode(c);
    }
    return aus;
  }
  function pdf(entw, titel) {
    var oben = 297 - HOEHE;                           // Zahlteil an der unteren Kante
    function X(x) { return zahl(x * MM); }
    function Y(y) { return zahl((297 - oben - y) * MM); }
    var s = [];
    entw.ops.forEach(function (o) {
      if (o.t === 'text') {
        var x = o.x;
        if (o.anker === 'end') x -= breite(o.text, o.pt, o.fett);
        if (o.anker === 'middle') x -= breite(o.text, o.pt, o.fett) / 2;
        s.push('BT /' + (o.fett ? 'F2' : 'F1') + ' ' + o.pt + ' Tf ' + X(x) + ' ' + Y(o.y) + ' Td (' + pdfText(o.text) + ') Tj ET');
      } else if (o.t === 'linie') {
        s.push(zahl(o.w) + ' w 0 J ' + X(o.x1) + ' ' + Y(o.y1) + ' m ' + X(o.x2) + ' ' + Y(o.y2) + ' l S');
      } else if (o.t === 'qr') {
        var n = o.matrix.length, m = o.groesse / n, r = [];
        for (var i = 0; i < n; i++) for (var c = 0; c < n; c++) {
          if (!o.matrix[i][c]) continue;
          var a = c; while (c + 1 < n && o.matrix[i][c + 1]) c++;
          r.push(X(o.x + a * m) + ' ' + Y(o.y + (i + 1) * m) + ' ' + zahl((c - a + 1) * m * MM) + ' ' + zahl(m * MM) + ' re');
        }
        s.push('0 g ' + r.join(' ') + ' f');
      } else if (o.t === 'kreuz') {
        kreuzTeile(o.x, o.y).forEach(function (k) {
          s.push((k.farbe === 's' ? '0' : '1') + ' g ' + X(k.x) + ' ' + Y(k.y + k.h) + ' ' + zahl(k.w * MM) + ' ' + zahl(k.h * MM) + ' re f');
        });
        s.push('0 g');
      }
    });
    var inhalt = '0 G 0 g\n' + s.join('\n') + '\n';
    var objekte = [
      '<< /Type /Catalog /Pages 2 0 R >>',
      '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
      '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.276 841.89] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>',
      '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',
      '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>',
      '<< /Length ' + inhalt.length + ' >>\nstream\n' + inhalt + 'endstream',
      '<< /Title (' + pdfText(titel || 'QR-Rechnung') + ') /Producer (meyssens.ch QR-Rechnung, im Browser erstellt) >>'
    ];
    var aus = '%PDF-1.4\n%âãÏÓ\n', stellen = [];
    objekte.forEach(function (o, i) { stellen.push(aus.length); aus += (i + 1) + ' 0 obj\n' + o + '\nendobj\n'; });
    var xref = aus.length;
    aus += 'xref\n0 ' + (objekte.length + 1) + '\n0000000000 65535 f \n';
    stellen.forEach(function (p) { aus += ('000000000' + p).slice(-10) + ' 00000 n \n'; });
    aus += 'trailer\n<< /Size ' + (objekte.length + 1) + ' /Root 1 0 R /Info 7 0 R >>\nstartxref\n' + xref + '\n%%EOF\n';
    var bytes = new Uint8Array(aus.length);
    for (var j = 0; j < aus.length; j++) bytes[j] = aus.charCodeAt(j) & 255;
    return bytes;
  }

  function erstelle(eingaben) {
    var p = pruefe(eingaben);
    if (!p.ok) return p;
    var e = entwurf(p.daten, qrMatrix(p.daten.inhalt));
    if (e.zuLang.length) {
      p.ok = false;
      p.fehler.push({ feld: 'mitteilung', text: 'Zu viel Text für ' + e.zuLang.join(' und ') + '. Bitte Namen oder Zusätzliche Informationen kürzen.' });
      return p;
    }
    p.entwurf = e;
    return p;
  }

  var BEISPIEL = {   // Beispiel 2 aus Anhang A der SIX Implementation Guidelines (erfundene Daten)
    konto: 'CH44 3199 9123 0008 8901 2', ze_name: 'Max Muster & Söhne', ze_strasse: 'Musterstrasse', ze_nr: '123',
    ze_plz: '8000', ze_ort: 'Seldwyla', ze_land: 'CH', waehrung: 'CHF', betrag: '1949.75',
    referenz: '21 00000 00003 13947 14300 09017', mitteilung: 'Auftrag vom 15.10.2020', mit_zahler: true,
    zp_name: 'Simon Muster', zp_strasse: 'Musterstrasse', zp_nr: '1', zp_plz: '8000', zp_ort: 'Seldwyla', zp_land: 'CH'
  };

  var QR = { pruefe: pruefe, nutzdaten: nutzdaten, qrMatrix: qrMatrix, entwurf: entwurf, svg: svg, pdf: pdf, erstelle: erstelle,
    qrReferenz: qrReferenz, scorReferenz: scorReferenz, mod10: mod10, ibanGueltig: ibanGueltig, istQrIban: istQrIban,
    breite: breite, BEISPIEL: BEISPIEL };
  global.QRRechnung = QR;

  // --- Bedienung im Browser ---
  if (typeof document === 'undefined') return;
  var form = document.getElementById('qr-formular');
  if (!form) return;
  var vorschau = document.getElementById('qr-vorschau'), meldungen = document.getElementById('qr-meldungen');
  var marke = document.getElementById('qr-marke'), knoepfe = form.querySelectorAll('[data-qr-download]');
  var inhaltAnzeige = document.getElementById('qr-inhalt'), refHinweis = document.getElementById('qr-ref-hinweis');
  var zahlerFelder = document.getElementById('qr-zahler-felder'), letzte = null, timer = null;

  function werte() {
    var e = {};
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.id || el.type === 'button') return;
      e[el.id.replace(/^qr-/, '').replace(/-/g, '_')] = el.type === 'checkbox' ? el.checked : el.value;
    });
    return e;
  }
  function setze(e) {
    Object.keys(e).forEach(function (k) {
      var el = document.getElementById('qr-' + k.replace(/_/g, '-'));
      if (!el) return;
      if (el.type === 'checkbox') el.checked = !!e[k]; else el.value = e[k];
    });
    zahlerFelder.hidden = !document.getElementById('qr-mit-zahler').checked;
  }
  function leer(e) {
    return !Object.keys(e).some(function (k) { return k !== 'waehrung' && k !== 'ze_land' && k !== 'zp_land' && k !== 'mit_zahler' && e[k]; });
  }
  function zeigeBeispiel() {
    var p = erstelle(BEISPIEL);
    vorschau.innerHTML = svg(p.entwurf);
    marke.textContent = 'Beispiel';
    inhaltAnzeige.textContent = p.daten.inhalt;
  }
  function aktualisiere() {
    var e = werte();
    zahlerFelder.hidden = !e.mit_zahler;
    Array.prototype.forEach.call(form.querySelectorAll('[aria-invalid]'), function (el) { el.removeAttribute('aria-invalid'); });
    knoepfe.forEach(function (k) { k.disabled = true; });
    var konto = String(e.konto || '').replace(/\s/g, '').toUpperCase();
    refHinweis.textContent = konto.length === 21 && istQrIban(konto)
      ? 'QR-IBAN erkannt: 27-stellige QR-Referenz nötig, nur in CHF.'
      : 'Mit normaler IBAN: RF-Referenz oder leer lassen.';
    if (leer(e)) { letzte = null; meldungen.innerHTML = ''; zeigeBeispiel(); return; }
    var p = erstelle(e);
    if (!p.ok) {
      letzte = null;
      meldungen.innerHTML = '<p class="qr-fehler-titel">Noch nicht vollständig:</p><ul>' + p.fehler.map(function (f) {
        var el = document.getElementById('qr-' + f.feld.replace(/_/g, '-'));
        if (el) el.setAttribute('aria-invalid', 'true');
        return '<li><a href="#qr-' + f.feld.replace(/_/g, '-') + '">' + esc(f.text) + '</a></li>';
      }).join('') + '</ul>';
      marke.textContent = 'Unvollständig';
      vorschau.classList.add('qr-blass');
      return;
    }
    vorschau.classList.remove('qr-blass');
    letzte = p;
    meldungen.innerHTML = '<p class="qr-ok">Alle Angaben sind formal gültig. Bitte vor dem Versand mit Ihrer Bank-App testen.</p>';
    vorschau.innerHTML = svg(p.entwurf);
    marke.textContent = 'Ihre Vorschau';
    inhaltAnzeige.textContent = p.daten.inhalt;
    knoepfe.forEach(function (k) { k.disabled = false; });
  }
  function speichere(daten, typ, name) {
    var url = URL.createObjectURL(new Blob([daten], { type: typ }));
    var a = document.createElement('a');
    a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }
  form.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(aktualisiere, 150); });
  form.addEventListener('change', aktualisiere);
  form.addEventListener('submit', function (ev) { ev.preventDefault(); });
  document.getElementById('qr-pruefziffer').addEventListener('click', function () {
    var e = werte(), konto = String(e.konto || '').replace(/\s/g, '').toUpperCase(), feld = document.getElementById('qr-referenz');
    var r = konto.length === 21 && istQrIban(konto) ? qrReferenz(String(e.referenz).replace(/\D/g, '')) : scorReferenz(String(e.referenz).replace(/^RF\d{0,2}/i, ''));
    if (r) { feld.value = r; aktualisiere(); }
    else { refHinweis.textContent = 'Bitte zuerst eine Nummer eingeben: bei QR-IBAN nur Ziffern (bis 26), sonst Buchstaben und Ziffern (bis 21).'; }
  });
  document.getElementById('qr-beispiel').addEventListener('click', function () { setze(BEISPIEL); aktualisiere(); });
  document.getElementById('qr-leeren').addEventListener('click', function () { form.reset(); aktualisiere(); });
  knoepfe.forEach(function (k) {
    k.addEventListener('click', function () {
      if (!letzte) return;
      if (k.getAttribute('data-qr-download') === 'pdf') speichere(pdf(letzte.entwurf, 'QR-Rechnung ' + letzte.daten.empfaenger.name), 'application/pdf', 'qr-rechnung.pdf');
      else speichere('<?xml version="1.0" encoding="UTF-8"?>\n' + svg(letzte.entwurf, true), 'image/svg+xml', 'qr-zahlteil.svg');
    });
  });
  aktualisiere();
})(typeof window !== 'undefined' ? window : globalThis);
