#!/usr/bin/env python3
"""Prüft im Browser (Playwright/Chromium) den Textkontrast aller Buttons und Button-Links.

Aufruf im Projektordner, während ein lokaler Server läuft:
  python3 -m http.server 8766 --bind 127.0.0.1 &
  python3 kontrast_buttons.py [--basis http://127.0.0.1:8766] [--json ausgabe.json]

Seiten: alle URLs aus sitemap.xml plus /404.html.
Elemente: button, input[type=submit|button|reset], [role=button], Links mit "btn"/"cta" im Klassennamen,
.nav-btn sowie alle Links mit eigener Hintergrundfarbe oder eigenem Hintergrundbild.
Zustände: normal, hover, focus, active (per DevTools-Protokoll erzwungen, inkl. Vorfahren),
Breiten: 1280 px (Desktop) und 390 px (Handy), jeweils hell und mit prefers-color-scheme: dark.
Textfarbe: jede Textstelle im Element (auch in <span>), Hintergrund: Farben der Vorfahren übereinander
gelegt; bei Verläufen zählt die ungünstigste Verlaufsfarbe. Grenze 4.5:1 (Text), 3:1 für Buttons nur mit Symbol.
Ausgabe: alles unter der Grenze, gruppiert. Exitcode 1, wenn etwas unter der Grenze liegt.
Nur sichtbare Elemente; geschlossene Dialoge und das zugeklappte Handy-Menü werden nicht geprüft.
"""
import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent

MARKIEREN = r"""
() => {
  const kand = new Set();
  const sel = 'button, input[type=submit], input[type=button], input[type=reset], [role=button], ' +
              'a[class*="btn"], a[class*="cta"], .nav-btn';
  document.querySelectorAll(sel).forEach(e => kand.add(e));
  document.querySelectorAll('a').forEach(a => {
    const cs = getComputedStyle(a);
    const m = cs.backgroundColor.match(/[\d.]+/g);
    const alpha = m ? (m.length > 3 ? +m[3] : 1) : 0;
    if (alpha > 0 || cs.backgroundImage !== 'none') kand.add(a);
  });
  let i = 0;
  for (const e of document.querySelectorAll('*')) {
    if (!kand.has(e)) continue;
    const r = e.getBoundingClientRect();
    if (r.width < 1 || r.height < 1 || !e.checkVisibility({visibilityProperty: true})) continue;
    e.setAttribute('data-ka', i++);
  }
  return i;
}
"""

MESSEN = r"""
() => {
  const parse = c => {
    let m = c.match(/^rgba?\(([^)]+)\)/);
    if (m) { const p = m[1].split(/[\s,\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
    m = c.match(/^color\(srgb ([^)]+)\)/);
    if (m) { const p = m[1].split(/[\s\/]+/).filter(Boolean).map(Number); return [p[0]*255, p[1]*255, p[2]*255, p.length > 3 ? p[3] : 1]; }
    return null;
  };
  const verlaufFarben = img => (img.match(/rgba?\([^)]+\)|color\(srgb [^)]+\)/g) || []).map(parse).filter(Boolean);
  const ueber = (oben, unten) => {
    const a = oben[3];
    return [oben[0]*a + unten[0]*(1-a), oben[1]*a + unten[1]*(1-a), oben[2]*a + unten[2]*(1-a), 1];
  };
  const lum = c => {
    const f = v => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v + 0.055)/1.055, 2.4); };
    return 0.2126*f(c[0]) + 0.7152*f(c[1]) + 0.0722*f(c[2]);
  };
  const kontrast = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05)/(Math.min(x, y) + 0.05); };
  const hex = c => '#' + c.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, '0')).join('');

  // Hintergrund-Kandidaten: Schichten von aussen nach innen übereinanderlegen
  const hintergruende = e => {
    const schichten = [];
    let bild = false;
    for (let n = e; n && n.nodeType === 1; n = n.parentElement) {
      const cs = getComputedStyle(n);
      const farbe = parse(cs.backgroundColor) || [0, 0, 0, 0];
      const img = cs.backgroundImage;
      let verlauf = [];
      if (img && img !== 'none') {
        verlauf = verlaufFarben(img);
        if (/url\(/.test(img)) bild = true;
      }
      schichten.push({farbe, verlauf});
      if (farbe[3] >= 1 && !verlauf.length) break;
      if (verlauf.length && verlauf.every(v => v[3] >= 1)) break;
    }
    let basis = [[255, 255, 255, 1]];
    for (let k = schichten.length - 1; k >= 0; k--) {
      const s = schichten[k];
      let neu = basis.map(b => s.farbe[3] > 0 ? ueber(s.farbe, b) : b);
      if (s.verlauf.length) neu = neu.flatMap(b => s.verlauf.map(v => ueber(v, b)));
      basis = neu;
    }
    return {basis, bild};
  };

  const raus = [];
  document.querySelectorAll('[data-ka]').forEach(e => {
    const {basis, bild} = hintergruende(e);
    // Textfarben: Elternelemente aller sichtbaren Textstellen
    const farben = new Map();
    const tw = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
    let t;
    while ((t = tw.nextNode())) {
      if (!t.textContent.trim()) continue;
      const p = t.parentElement;
      if (!p.checkVisibility({visibilityProperty: true})) continue;
      farben.set(p, getComputedStyle(p).color);
    }
    let text = (e.innerText || e.value || '').trim().replace(/\s+/g, ' ');
    const nurSymbol = !farben.size && !(e.tagName === 'INPUT' && e.value);
    if (e.tagName === 'INPUT' && e.value) farben.set(e, getComputedStyle(e).color);
    if (nurSymbol) { farben.set(e, getComputedStyle(e).color); text = e.getAttribute('aria-label') || e.title || '(Symbol)'; }
    let schlechtest = null;
    for (const [p, c] of farben) {
      const fg = parse(c);
      if (!fg) continue;
      for (const b of basis) {
        const fgDeckend = fg[3] < 1 ? ueber(fg, b) : fg;
        const k = kontrast(fgDeckend, b);
        if (!schlechtest || k < schlechtest.k) {
          // Hintergrund des Textes selbst (z. B. Span mit eigenem Hintergrund) berücksichtigen
          schlechtest = {k, fg: hex(fgDeckend), bg: hex(b)};
        }
      }
    }
    if (!schlechtest) return;
    const cls = (typeof e.className === 'string' ? e.className : '').trim().split(/\s+/).filter(Boolean).slice(0, 3).join('.');
    const sec = e.closest('section[id], footer, header, nav, [id]');
    raus.push({i: +e.getAttribute('data-ka'), el: e.tagName.toLowerCase() + (cls ? '.' + cls : ''),
               text: text.slice(0, 50), ort: sec ? (sec.id ? '#' + sec.id : sec.tagName.toLowerCase()) : '',
               k: Math.round(schlechtest.k * 100)/100, fg: schlechtest.fg, bg: schlechtest.bg,
               grenze: nurSymbol ? 3 : 4.5, bild});
  });
  return raus;
}
"""

ZUSTAENDE = {
    "normal": (None, None),
    "hover": (["hover"], ["hover"]),
    "focus": (["focus", "focus-visible"], ["focus-within"]),
    "active": (["active", "hover", "focus"], ["active", "hover", "focus-within"]),
}
ANSICHTEN = {"desktop": {"width": 1280, "height": 900}, "handy": {"width": 390, "height": 844}}
SCHEMAS = ("light", "dark")


def seiten():
    xml = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    pfade = [re.sub(r"^https://meyssens\.ch", "", u) for u in re.findall(r"<loc>([^<]+)</loc>", xml)]
    return pfade + ["/404.html"]


def eltern_karte(knoten, eltern=None, karte=None):
    karte = {} if karte is None else karte
    # nur Elemente (nodeType 1) als Eltern führen, das Dokument selbst nicht
    karte[knoten["nodeId"]] = eltern
    weiter = knoten["nodeId"] if knoten.get("nodeType") == 1 else None
    for kind in knoten.get("children", []):
        eltern_karte(kind, weiter, karte)
    return karte


async def pruefe_seite(context, basis, pfad):
    page = await context.new_page()
    await page.goto(basis + pfad, wait_until="load")
    await page.add_style_tag(content="*,*::before,*::after{transition:none!important;animation:none!important}")
    await page.evaluate(MARKIEREN)
    cdp = await context.new_cdp_session(page)
    await cdp.send("DOM.enable")
    await cdp.send("CSS.enable")
    doc = await cdp.send("DOM.getDocument", {"depth": -1, "pierce": False})
    karte = eltern_karte(doc["root"])
    ids = (await cdp.send("DOM.querySelectorAll", {"nodeId": doc["root"]["nodeId"], "selector": "[data-ka]"}))["nodeIds"]
    ergebnis = []
    for zustand, (selbst, vorfahren) in ZUSTAENDE.items():
        if selbst is None:
            ergebnis += [dict(r, zustand=zustand) for r in await page.evaluate(MESSEN)]
            continue
        for i, nid in enumerate(ids):
            kette = []
            n = karte.get(nid)
            while n is not None:
                kette.append(n)
                n = karte.get(n)
            await cdp.send("CSS.forcePseudoState", {"nodeId": nid, "forcedPseudoClasses": selbst})
            for a in kette:
                await cdp.send("CSS.forcePseudoState", {"nodeId": a, "forcedPseudoClasses": vorfahren})
            for r in await page.evaluate(MESSEN):
                if r["i"] == i:
                    ergebnis.append(dict(r, zustand=zustand))
            await cdp.send("CSS.forcePseudoState", {"nodeId": nid, "forcedPseudoClasses": []})
            for a in kette:
                await cdp.send("CSS.forcePseudoState", {"nodeId": a, "forcedPseudoClasses": []})
    await page.close()
    return ergebnis


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--basis", default="http://127.0.0.1:8766")
    ap.add_argument("--json")
    args = ap.parse_args()
    alle, anzahl = [], 0
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        for schema in SCHEMAS:
            for ansicht, vp in ANSICHTEN.items():
                context = await browser.new_context(viewport=vp, color_scheme=schema,
                                                    is_mobile=ansicht == "handy", has_touch=ansicht == "handy")
                for pfad in seiten():
                    for r in await pruefe_seite(context, args.basis, pfad):
                        anzahl += 1
                        alle.append(dict(r, seite=pfad, ansicht=ansicht, schema=schema))
                await context.close()
        await browser.close()
    schlecht = [r for r in alle if r["k"] < r["grenze"]]
    if args.json:
        Path(args.json).write_text(json.dumps(schlecht, ensure_ascii=False, indent=1), encoding="utf-8")
    elemente = len({(r["seite"], r["ansicht"], r["schema"], r["i"]) for r in alle})
    print("%d Seiten, %d Button-Vorkommen (alle Breiten/Schemas), %d Messungen mit 4 Zuständen"
          % (len(seiten()), elemente, anzahl))
    # gruppieren: gleiches Element, gleicher Zustand, gleiche Farben
    gruppen = {}
    for r in schlecht:
        key = (r["el"], r["text"], r["ort"], r["zustand"], r["fg"], r["bg"], r["k"])
        g = gruppen.setdefault(key, {"seiten": set(), "ansichten": set(), "schemas": set(), "bild": r["bild"]})
        g["seiten"].add(r["seite"])
        g["ansichten"].add(r["ansicht"])
        g["schemas"].add(r["schema"])
    if not gruppen:
        print("Kein Button unter 4.5:1 (Symbol-Buttons unter 3:1).")
        return 0
    print("Unter der Grenze: %d Fälle in %d Gruppen\n" % (len(schlecht), len(gruppen)))
    for (el, text, ort, zustand, fg, bg, k), g in sorted(gruppen.items(), key=lambda x: (x[0][6], x[0][0])):
        s = sorted(g["seiten"])
        print("%5.2f:1  %-7s %s auf %s  %s \"%s\" %s  [%s; %s]%s\n         Seiten (%d): %s"
              % (k, zustand, fg, bg, el, text, ort, "/".join(sorted(g["ansichten"])), "/".join(sorted(g["schemas"])),
                 "  (Hintergrundbild, von Hand prüfen)" if g["bild"] else "", len(s),
                 ", ".join(s[:6]) + (" ..." if len(s) > 6 else "")))
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
