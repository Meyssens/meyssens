// /branchen/: Filter-Chips, Suche, weiches Einblenden und Vorschau-Panel. Ohne JavaScript sind die Karten normale Links.
(function () {
  "use strict";
  var raster = document.getElementById("bx-raster");
  if (!raster) return;
  window.bxBereit = true;
  var wurzel = document.documentElement;
  var ruhig = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var zellen = Array.prototype.slice.call(raster.querySelectorAll(".bx-zelle"));
  var chips = Array.prototype.slice.call(document.querySelectorAll(".bx-chip"));
  var feld = document.getElementById("bx-suchfeld");
  var anzahl = document.getElementById("bx-anzahl");
  var leer = document.getElementById("bx-leer");
  var filter = "alle";
  var weich = "cubic-bezier(.2,.7,.2,1)";

  // Einblenden beim Scrollen (die Klasse bx-an setzt die Vorlage nur mit IntersectionObserver und ohne reduzierte Bewegung)
  if (wurzel.classList.contains("bx-an")) {
    var beobachter = new IntersectionObserver(function (eintraege) {
      eintraege.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("ist-da");
          beobachter.unobserve(e.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    document.querySelectorAll(".bx-zelle, .bx-schritt").forEach(function (el) { beobachter.observe(el); });
  }

  function ohneAkzente(t) {
    return t.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }

  function passt(zelle, worte) {
    if (filter !== "alle" && zelle.getAttribute("data-bereiche").split(" ").indexOf(filter) < 0) return false;
    var text = zelle.getAttribute("data-suche");
    return worte.every(function (w) { return text.indexOf(w) >= 0; });
  }

  // Filtern mit FLIP: bleibende Karten gleiten an ihren neuen Platz, neue Karten blenden ein
  function anwenden() {
    var worte = ohneAkzente(feld ? feld.value.trim() : "").split(/\s+/).filter(Boolean);
    var vorher = new Map();
    zellen.forEach(function (z) { if (!z.hidden) vorher.set(z, z.getBoundingClientRect()); });
    var sichtbar = 0;
    zellen.forEach(function (z) {
      z.hidden = !passt(z, worte);
      if (!z.hidden) {
        sichtbar++;
        z.classList.add("ist-da");
      }
    });
    anzahl.textContent = sichtbar === zellen.length ? zellen.length + " Branchen"
      : sichtbar + " von " + zellen.length + " Branchen";
    leer.hidden = sichtbar > 0;
    if (ruhig || !Element.prototype.animate) return;
    zellen.forEach(function (z) {
      if (z.hidden) return;
      var a = vorher.get(z), b = z.getBoundingClientRect();
      if (a) {
        var dx = a.left - b.left, dy = a.top - b.top;
        if (dx || dy) z.animate([{ transform: "translate(" + dx + "px," + dy + "px)" }, { transform: "none" }],
          { duration: 420, easing: weich });
      } else {
        z.animate([{ opacity: 0, transform: "scale(.94)" }, { opacity: 1, transform: "none" }],
          { duration: 360, easing: weich });
      }
    });
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      filter = chip.getAttribute("data-filter");
      chips.forEach(function (c) { c.setAttribute("aria-pressed", c === chip ? "true" : "false"); });
      anwenden();
    });
  });
  if (feld) {
    feld.addEventListener("input", anwenden);
    feld.addEventListener("keydown", function (e) {
      if (e.key === "Enter") e.preventDefault();
    });
  }

  // Vorschau: Klick auf eine Karte öffnet das Panel mit den Bausteinen, Strg/Cmd-Klick öffnet weiter die Branchenseite
  var panel = document.getElementById("bx-panel");
  var inhalt = document.getElementById("bx-panel-inhalt");
  if (!panel || typeof panel.showModal !== "function") return;
  var ausloeser = null;

  function oeffnen(slug, karte) {
    var vorlage = document.getElementById("bx-v-" + slug);
    if (!vorlage) return false;
    inhalt.innerHTML = "";
    inhalt.appendChild(vorlage.content.cloneNode(true));
    ausloeser = karte;
    panel.showModal();
    wurzel.classList.add("bx-offen");
    panel.scrollTop = 0;
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { panel.classList.add("ist-offen"); });
    });
    return true;
  }

  function schliessen() {
    if (!panel.open) return;
    panel.classList.remove("ist-offen");
    var fertig = function () {
      panel.close();
    };
    if (ruhig) fertig(); else setTimeout(fertig, 320);
  }

  panel.addEventListener("close", function () {
    panel.classList.remove("ist-offen");
    wurzel.classList.remove("bx-offen");
    if (ausloeser) ausloeser.focus({ preventScroll: true });
  });
  panel.addEventListener("cancel", function (e) {
    e.preventDefault();
    schliessen();
  });
  panel.addEventListener("click", function (e) {
    if (e.target === panel) schliessen();
  });
  panel.querySelector(".bx-zu").addEventListener("click", schliessen);

  raster.addEventListener("click", function (e) {
    var karte = e.target.closest(".bx-karte");
    if (!karte || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (oeffnen(karte.getAttribute("data-vorschau"), karte)) e.preventDefault();
  });
  raster.querySelectorAll(".bx-karte").forEach(function (k) { k.setAttribute("aria-haspopup", "dialog"); });
})();
