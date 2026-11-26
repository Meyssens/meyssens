/* Briefe als A4-PDF im Browser (Mahnung, Rechnung, Offerte). Nutzt die PDF- und QR-Funktionen von qr-rechnung.js
   (window.QRRechnung). Eine Seite, Helvetica, Adressfeld für Fenstercouverts (Lage einstellbar, Probedruck empfohlen),
   auf Wunsch mit QR-Zahlteil an der unteren Kante. Nichts wird gesendet oder gespeichert. */
(function (global) {
  'use strict';
  var LINKS = 25, RECHTS = 190, BREITE = RECHTS - LINKS;

  function geld(n) {                       // 1234.5 -> "1 234.50"
    var s = (Math.round(n * 100) / 100).toFixed(2).split('.');
    return s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ').replace(/ /g, ' ') + '.' + s[1];
  }
  function datumCH(d) {                    // Date (UTC) oder ISO-Text -> 31.01.2027
    if (typeof d === 'string') { var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(d); return m ? m[3] + '.' + m[2] + '.' + m[1] : d; }
    return ('0' + d.getUTCDate()).slice(-2) + '.' + ('0' + (d.getUTCMonth() + 1)).slice(-2) + '.' + d.getUTCFullYear();
  }
  function adresszeilen(a) {
    var z = [a.name, a.zusatz, [a.strasse, a.nr].filter(Boolean).join(' '), [a.plz, a.ort].filter(Boolean).join(' ')];
    if (a.land && a.land !== 'CH') z.push(a.land);
    return z.filter(function (x) { return x && x.trim(); });
  }

  // o: {titel, absender:{name,zusatz,strasse,nr,plz,ort,land,kontakt}, empfaenger:{...}, fenster:{x,y}, ortDatum, betreff,
  //     absaetze:[...], tabelle:{spalten:[{titel, breite, rechts}], zeilen:[[...]], summen:[[text, wert, fett]]},
  //     schluss:[...], gruss, unterschrift, fussnote, qr: Eingaben für QRRechnung.erstelle oder null}
  function erstelle(o) {
    var Q = global.QRRechnung, ops = [], fehler = [];
    var k = !!o.qr;                         // mit QR-Zahlteil enger setzen, damit der Brief über dem Zahlteil Platz hat
    var ZL = k ? 4.4 : 4.8, AB = k ? 2 : 2.6;
    function text(x, y, pt, fett, t, anker) { ops.push({ t: 'text', x: x, y: y, pt: pt, fett: !!fett, text: Q.bereinige ? Q.bereinige(t) : t, anker: anker || 'start' }); }
    function linie(x1, y1, x2, y2, w) { ops.push({ t: 'linie', x1: x1, y1: y1, x2: x2, y2: y2, w: w || 0.3 }); }

    // Absender oben links, Kontakt darunter
    var y = 20, abs = adresszeilen(o.absender);
    if (abs.length) { text(LINKS, y, 11, true, abs[0]); y += 5; abs.slice(1).forEach(function (z) { text(LINKS, y, 9, false, z); y += 4.2; }); }
    if (o.absender.kontakt) { text(LINKS, y, 9, false, o.absender.kontakt); }

    // Empfänger im Adressfeld (Fenster); Absenderzeile klein darüber
    var f = o.fenster || { x: 118, y: 52 }, ey = f.y;
    if (abs.length) { text(f.x, ey, 6.5, false, [abs[0]].concat(abs.slice(-1)).join(', ')); }
    ey += 6;
    adresszeilen(o.empfaenger).forEach(function (z) { text(f.x, ey, 10, false, z); ey += 4.6; });

    y = Math.max(f.y + (k ? 35 : 40), ey + (k ? 4 : 6));
    if (o.ortDatum) { text(LINKS, y, 10, false, o.ortDatum); y += k ? 7 : 10; }
    if (o.betreff) {
      Q.umbrechen(o.betreff, BREITE, 11, true).forEach(function (z) { text(LINKS, y, 11, true, z); y += 5.4; });
      y += 3;
    }
    function absatz(t) { Q.umbrechen(t, BREITE, 10, false).forEach(function (z) { text(LINKS, y, 10, false, z); y += ZL; }); y += AB; }
    (o.absaetze || []).forEach(absatz);

    if (o.tabelle) {
      var sp = o.tabelle.spalten, x = LINKS, xs = sp.map(function (s) { var a = x; x += s.breite; return a; });
      y += 1;
      sp.forEach(function (s, i) { text(s.rechts ? xs[i] + s.breite : xs[i], y, 8.5, true, s.titel, s.rechts ? 'end' : 'start'); });
      y += 2; linie(LINKS, y, RECHTS, y, 0.5); y += 4.4;
      o.tabelle.zeilen.forEach(function (z) {
        var hoehe = 1;
        z.forEach(function (zelle, i) {
          var s = sp[i], zeilen = s.rechts ? [String(zelle)] : Q.umbrechen(String(zelle), s.breite - 2, 9, false);
          zeilen.forEach(function (t, k) { text(s.rechts ? xs[i] + s.breite : xs[i], y + k * 4.2, 9, false, t, s.rechts ? 'end' : 'start'); });
          hoehe = Math.max(hoehe, zeilen.length);
        });
        y += hoehe * 4.2 + 1.4;
      });
      linie(LINKS, y - 2.6, RECHTS, y - 2.6, 0.3);
      (o.tabelle.summen || []).forEach(function (s) {
        y += 1;
        text(RECHTS - 40, y, 9.5, !!s[2], s[0], 'end');
        text(RECHTS, y, 9.5, !!s[2], s[1], 'end');
        y += 5;
      });
      y += 3;
    }
    (o.schluss || []).forEach(absatz);
    if (o.gruss) { y += k ? 1 : 2; text(LINKS, y, 10, false, o.gruss); y += k ? 8 : 12; }
    if (o.unterschrift) { text(LINKS, y, 10, false, o.unterschrift); y += 6; }
    if (o.fussnote) { y += 2; Q.umbrechen(o.fussnote, BREITE, 7.5, false).forEach(function (z) { text(LINKS, y, 7.5, false, z); y += 3.4; }); }

    var entw = null;
    if (o.qr) {
      var p = Q.erstelle(o.qr);
      if (!p.ok) return { ok: false, fehler: p.fehler.map(function (f) { return 'QR-Zahlteil: ' + f.text; }) };
      entw = p.entwurf;
    }
    var grenze = entw ? 297 - 105 - 6 : 285;
    if (y > grenze) fehler.push('Zu viel Inhalt für eine Seite' + (entw ? ' mit QR-Zahlteil' : '') + '. Bitte Texte oder Positionen kürzen.');
    if (fehler.length) return { ok: false, fehler: fehler };
    return { ok: true, bytes: Q.pdf(entw, o.titel || 'Brief', ops), hoehe: y };
  }

  function speichere(bytes, name) {
    var url = URL.createObjectURL(new Blob([bytes], { type: 'application/pdf' }));
    var a = document.createElement('a');
    a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }

  // Adressfelder aus einem Formular lesen: Felder mit id präfix-name, -zusatz, -strasse, -nr, -plz, -ort
  function leseAdresse(form, praefix) {
    var a = {};
    ['name', 'zusatz', 'strasse', 'nr', 'plz', 'ort', 'land', 'kontakt'].forEach(function (k) {
      var e = form.querySelector('#' + praefix + '-' + k); a[k] = e ? e.value.trim() : '';
    });
    if (!a.land) a.land = 'CH';
    return a;
  }
  function fenster(form) {
    var links = form.querySelector('#br-fenster-links');
    var x = parseFloat((form.querySelector('#br-fenster-x') || {}).value), y = parseFloat((form.querySelector('#br-fenster-y') || {}).value);
    return { x: isFinite(x) ? x : (links && links.checked ? 22 : 118), y: isFinite(y) ? y : 52 };
  }

  // Fenster rechts/links: Standardabstand vom linken Rand umstellen
  if (typeof document !== 'undefined') {
    document.addEventListener('change', function (e) {
      if (e.target && e.target.name === 'br-fenster') {
        var x = document.getElementById('br-fenster-x');
        if (x) { x.value = e.target.value === 'links' ? 22 : 118; x.dispatchEvent(new Event('input', { bubbles: true })); }
      }
    });
  }

  global.BriefPDF = { erstelle: erstelle, speichere: speichere, geld: geld, datumCH: datumCH, adresszeilen: adresszeilen,
                      leseAdresse: leseAdresse, fenster: fenster, LINKS: LINKS, RECHTS: RECHTS };
})(typeof window !== 'undefined' ? window : this);
