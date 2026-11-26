/* Kaufseiten /automatisierung/ und /preise/ (assets/loesungen.css):
   [data-lz]  Ablauf: die Linie wächst mit dem Scrollen, Symbole füllen sich nacheinander (nur vorwärts, einmalig)
   [data-vn]  Vorher-nachher: einmalig beim Hineinscrollen
   [data-pzf]  Preis-Faktoren: Karten blenden gestaffelt ein, einmalig
   Bei reduzierter Bewegung oder ohne IntersectionObserver wird sofort der Endzustand gesetzt. */
(function () {
  var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var ablaeufe = Array.prototype.slice.call(document.querySelectorAll("[data-lz]"));
  var einmalig = Array.prototype.slice.call(document.querySelectorAll("[data-vn],[data-pzf]"));

  function fertig(liste) {
    liste.forEach(function (el) {
      el.style.setProperty("--p", "1");
      el.classList.add("an");
      el.querySelectorAll(".lz-schritt").forEach(function (s) { s.classList.add("an"); });
    });
  }
  // Länge der Linie: von der Mitte des ersten bis zur Mitte des letzten Symbols (wichtig in der senkrechten Handy-Ansicht)
  function laengen() {
    ablaeufe.forEach(function (el) {
      var ics = el.querySelectorAll(".lz-ic");
      if (ics.length < 2) return;
      var a = ics[0].getBoundingClientRect(), z = ics[ics.length - 1].getBoundingClientRect();
      el.style.setProperty("--lz-h", Math.max(0, Math.round(z.top - a.top)) + "px");
    });
  }
  laengen();
  window.addEventListener("resize", laengen);
  if (still || !("IntersectionObserver" in window)) { fertig(ablaeufe.concat(einmalig)); return; }

  var io = new IntersectionObserver(function (eintraege) {
    eintraege.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("an"); io.unobserve(e.target); }
    });
  }, {threshold: 0.3});
  einmalig.forEach(function (el) { io.observe(el); });

  // Ablauf: Fortschritt aus der Lage im Fenster, nur zunehmend; danach keine Arbeit mehr
  var offen = ablaeufe.map(function (el) {
    return {el: el, p: 0, schritte: Array.prototype.slice.call(el.querySelectorAll(".lz-schritt"))};
  });
  var geplant = false;
  function messen() {
    geplant = false;
    var h = window.innerHeight;
    offen = offen.filter(function (a) {
      var r = a.el.getBoundingClientRect();
      var p = Math.min(1, Math.max(0, (h * 0.85 - r.top) / (r.height + h * 0.35)));
      if (p > a.p) {
        a.p = p;
        a.el.style.setProperty("--p", p.toFixed(3));
        var n = a.schritte.length;
        a.schritte.forEach(function (s, i) { if (p >= (n > 1 ? i / (n - 1) : 0) * 0.98) s.classList.add("an"); });
      }
      return a.p < 1;
    });
    if (!offen.length) { window.removeEventListener("scroll", planen); window.removeEventListener("resize", planen); }
  }
  function planen() { if (!geplant) { geplant = true; requestAnimationFrame(messen); } }
  window.addEventListener("scroll", planen, {passive: true});
  window.addEventListener("resize", planen);
  planen();
})();
