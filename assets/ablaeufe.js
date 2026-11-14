/* Animierte Beispiele "Automatisierungen und Schnittstellen" (/unternehmen/#ablaeufe) und Mini-Beispiele der Branchenseiten.
   Ohne JavaScript ist der Endzustand sichtbar. Mit JavaScript läuft der Ablauf einmal, sobald das Beispiel im Bild ist
   (Schritte über data-ab="n"). Knopf: Anhalten, Weiter, Nochmals abspielen. Bei reduzierter Bewegung startet nichts von
   selbst; der Knopf zeigt die Schritte ohne Übergänge.
   Knöpfe mit data-thema füllen das Freitextfeld des Anfrageformulars vor, wenn es noch leer ist. */
(function () {
  var TAKT = 1300;
  var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll("[data-abl-beispiel]").forEach(function (fig) {
    var buehne = fig.querySelector(".abl-buehne");
    var knopf = fig.querySelector(".abl-knopf");
    var teile = Array.prototype.slice.call(buehne.querySelectorAll("[data-ab]"));
    var ende = teile.reduce(function (m, e) { return Math.max(m, +e.getAttribute("data-ab")); }, 0);
    var schritt = ende, uhr = null;

    function zeige(n) {
      schritt = n;
      buehne.setAttribute("data-s", n);
      teile.forEach(function (e) { e.classList.toggle("an", +e.getAttribute("data-ab") <= n); });
    }
    function beschrifte(text) { knopf.textContent = text; }
    function halt() { clearInterval(uhr); uhr = null; }
    function weiter() {
      if (schritt >= ende) { halt(); beschrifte("Nochmals abspielen"); return; }
      zeige(schritt + 1);
      if (schritt >= ende) { halt(); beschrifte("Nochmals abspielen"); }
    }
    function spiele() {
      if (schritt >= ende) { fig.classList.add("spielt"); zeige(0); }
      beschrifte("Anhalten");
      halt();
      uhr = setInterval(weiter, TAKT);
    }

    knopf.hidden = false;
    knopf.addEventListener("click", function () {
      if (uhr) { halt(); beschrifte("Weiter"); } else { spiele(); }
    });

    if (still || !("IntersectionObserver" in window)) { beschrifte("Abspielen"); return; }
    beschrifte("Abspielen");
    var beobachter = new IntersectionObserver(function (eintraege) {
      eintraege.forEach(function (e) {
        if (e.isIntersecting) { beobachter.disconnect(); spiele(); }
      });
    }, {threshold: 0.45});
    beobachter.observe(buehne);
    // Ausserhalb des Bildes anhalten, beim Zurückkehren fortsetzen
    new IntersectionObserver(function (eintraege) {
      eintraege.forEach(function (e) {
        if (!e.isIntersecting && uhr) { halt(); beschrifte("Weiter"); fig.setAttribute("data-pausiert", ""); }
        else if (e.isIntersecting && fig.hasAttribute("data-pausiert")) { fig.removeAttribute("data-pausiert"); spiele(); }
      });
    }, {threshold: 0}).observe(fig);
  });

  document.querySelectorAll("a[data-thema]").forEach(function (a) {
    a.addEventListener("click", function () {
      var ziel = document.querySelector(a.getAttribute("href"));
      var feld = ziel && ziel.querySelector("textarea");
      if (feld && !feld.value.trim()) feld.value = a.getAttribute("data-thema");
    });
  });
})();
