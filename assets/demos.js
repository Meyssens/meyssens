/* Beispiel-Demos und Scroll-Effekte. Ohne Bibliotheken, ohne Netzwerkaufrufe, nichts wird gespeichert.
   Alle Texte stehen im HTML (ansichten.html), das Skript blendet sie nur ein und aus.
   Bei prefers-reduced-motion bleibt alles statisch. */
(function(){
'use strict';
var ruhig = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
var hatIO = 'IntersectionObserver' in window;
function alle(sel, wo){ return Array.prototype.slice.call((wo || document).querySelectorAll(sel)); }

// --- Produktansicht unter dem Hero: --p wächst beim Scrollen von 0 auf 1 ---
alle('[data-buehne]').forEach(function(b){
  if(ruhig || !hatIO){ b.style.setProperty('--p', 1); return; }
  var an = false, raf = 0;
  function rechne(){
    raf = 0;
    var r = b.getBoundingClientRect(), vh = window.innerHeight;
    var p = Math.max(0, Math.min(1, (vh - r.top) / (vh * .7)));
    b.style.setProperty('--p', p.toFixed(3));
  }
  function beimScrollen(){ if(!raf) raf = requestAnimationFrame(rechne); }
  rechne();
  new IntersectionObserver(function(e){
    if(e[0].isIntersecting && !an){ window.addEventListener('scroll', beimScrollen, {passive:true}); an = true; rechne(); }
    else if(!e[0].isIntersecting && an){ window.removeEventListener('scroll', beimScrollen); an = false; }
  }).observe(b);
});

// --- Umfrage: abstimmen, Ergebnis sofort sehen ---
alle('[data-umfrage]').forEach(function(u){
  var opts = alle('.opt', u), knopf = u.querySelector('[data-abstimmen]'), stand = u.querySelector('[data-stand]');
  var basis = opts.map(function(o){ return +o.getAttribute('data-n'); });
  var anfang = stand.textContent;
  knopf.addEventListener('click', function(){
    if(u.classList.contains('abgestimmt')){
      u.classList.remove('abgestimmt');
      opts.forEach(function(o){ o.classList.remove('gewaehlt'); var i = o.querySelector('input'); i.checked = false; i.disabled = false; });
      knopf.textContent = 'Abstimmen';
      stand.textContent = anfang;
      opts[0].querySelector('input').focus();
      return;
    }
    var gewaehlt = u.querySelector('input:checked');
    if(!gewaehlt){ stand.textContent = 'Bitte wählen Sie zuerst eine Antwort.'; return; }
    var summe = 0;
    var zahlen = opts.map(function(o, i){ var n = basis[i] + (o.contains(gewaehlt) ? 1 : 0); summe += n; return n; });
    opts.forEach(function(o, i){
      var pz = Math.round(zahlen[i] / summe * 100);
      o.style.setProperty('--w', pz);
      o.querySelector('.opt-z').textContent = pz + ' %';
      o.classList.toggle('gewaehlt', o.contains(gewaehlt));
      o.querySelector('input').disabled = true;
    });
    u.classList.add('abgestimmt');
    knopf.textContent = 'Nochmals abstimmen';
    stand.textContent = summe + ' Stimmen, davon eine von Ihnen (Beispiel, nicht gespeichert)';
  });
});

// --- Karte: Pins öffnen einen Beispieleintrag, Häuser lassen sich markieren ---
alle('[data-karte]').forEach(function(k){
  var rahmen = k.querySelector('.plan-rahmen'), info = k.querySelector('[data-info]');
  var infoText = info.querySelector('[data-info-text]'), neuText = k.querySelector('[data-neu]');
  var anzahl = k.querySelector('[data-anzahl]'), aktiv = null, belegt = {};
  var vorlage = k.querySelector('.pin');
  function oeffne(pin){
    if(aktiv){ aktiv.classList.remove('aktiv'); aktiv.setAttribute('aria-expanded', 'false'); }
    aktiv = pin;
    pin.classList.add('aktiv'); pin.setAttribute('aria-expanded', 'true');
    var li = k.querySelector('.karte-liste li[data-haus="' + pin.getAttribute('data-haus') + '"]');
    infoText.innerHTML = (li || neuText).innerHTML;
    info.hidden = false;
  }
  function schliesse(){
    info.hidden = true;
    if(aktiv){ aktiv.classList.remove('aktiv'); aktiv.setAttribute('aria-expanded', 'false'); aktiv.focus(); aktiv = null; }
  }
  function setze(haus){
    var id = haus.getAttribute('data-haus');
    if(belegt[id]){ oeffne(belegt[id]); return belegt[id]; }
    var x = +haus.getAttribute('x') + haus.getAttribute('width') / 2, y = +haus.getAttribute('y') + haus.getAttribute('height') / 2;
    var pin = vorlage.cloneNode(true);
    pin.classList.add('neu'); pin.classList.remove('aktiv');
    pin.setAttribute('data-haus', 'neu-' + id);
    pin.setAttribute('aria-label', 'Ihr Beispieleintrag');
    pin.style.left = (x / 480 * 100).toFixed(2) + '%';
    pin.style.top = (y / 300 * 100).toFixed(2) + '%';
    pin.addEventListener('click', function(){ oeffne(pin); });
    rahmen.appendChild(pin);
    belegt[id] = pin;
    anzahl.textContent = +anzahl.textContent + 1;
    oeffne(pin);
    return pin;
  }
  alle('.pin', k).forEach(function(p){
    belegt[p.getAttribute('data-haus')] = p;
    p.addEventListener('click', function(){ aktiv === p && !info.hidden ? schliesse() : oeffne(p); });
  });
  alle('.haus', k).forEach(function(h){ h.addEventListener('click', function(){ setze(h); }); });
  info.querySelector('[data-zu]').addEventListener('click', schliesse);
  k.addEventListener('keydown', function(e){ if(e.key === 'Escape' && !info.hidden) schliesse(); });
  k.querySelector('[data-markieren]').addEventListener('click', function(){
    var frei = alle('.haus', k).filter(function(h){ return !belegt[h.getAttribute('data-haus')]; });
    if(!frei.length) return;
    setze(frei[Math.floor(Math.random() * frei.length)]).focus();
  });
});

// --- Chatbot: Beispielfrage wählen, Antwort erscheint wie getippt ---
alle('[data-chat]').forEach(function(c){
  var verlauf = c.querySelector('[data-verlauf]'), ansage = c.querySelector('[data-ansage]');
  var knoepfe = alle('[data-frage]', c), antworten = alle('.chat-antworten dd', c);
  function blase(art, inhalt){
    var p = document.createElement('p');
    p.className = 'msg ' + art;
    if(inhalt) p.textContent = inhalt;
    verlauf.appendChild(p);
    verlauf.scrollTop = verlauf.scrollHeight;
    return p;
  }
  function fertig(p, quelle){
    p.appendChild(quelle.cloneNode(true));
    verlauf.scrollTop = verlauf.scrollHeight;
    knoepfe.forEach(function(b){ if(!b.classList.contains('gefragt')) b.disabled = false; });
  }
  knoepfe.forEach(function(b){
    b.addEventListener('click', function(){
      var dd = antworten[+b.getAttribute('data-frage')];
      var text = dd.querySelector('span').textContent, quelle = dd.querySelector('a');
      knoepfe.forEach(function(x){ x.disabled = true; });
      b.classList.add('gefragt');
      blase('ich', b.textContent);
      ansage.textContent = text;
      var p = blase('bot');
      if(ruhig){ p.textContent = text; fertig(p, quelle); return; }
      p.innerHTML = '<span class="tippen" aria-hidden="true"><i></i><i></i><i></i></span>';
      setTimeout(function(){
        var span = document.createElement('span'), i = 0;
        p.textContent = ''; p.appendChild(span);
        (function tippe(){
          i += 2;
          span.textContent = text.slice(0, i);
          verlauf.scrollTop = verlauf.scrollHeight;
          if(i < text.length) setTimeout(tippe, 22); else fertig(p, quelle);
        })();
      }, 650);
    });
  });
});

// --- Beteiligung (Gemeinden): Pin hebt den Vorschlag hervor, Unterstützen zählt mit ---
alle('[data-beteiligung]').forEach(function(b){
  var pins = alle('.pin', b), eintraege = alle('.bt-liste li', b);
  function zeige(k){
    pins.forEach(function(p){ var an = p.getAttribute('data-vorschlag') === k; p.classList.toggle('aktiv', an); p.setAttribute('aria-pressed', an ? 'true' : 'false'); });
    eintraege.forEach(function(li){ li.classList.toggle('aktiv', li.getAttribute('data-vorschlag') === k); });
  }
  pins.forEach(function(p){ p.addEventListener('click', function(){ zeige(p.getAttribute('data-vorschlag')); }); });
  eintraege.forEach(function(li){ li.addEventListener('mouseenter', function(){ zeige(li.getAttribute('data-vorschlag')); }); });
  alle('.bt-stimme', b).forEach(function(k){
    k.addEventListener('click', function(){
      var an = k.getAttribute('aria-pressed') !== 'true';
      k.setAttribute('aria-pressed', an ? 'true' : 'false');
      k.querySelector('.bt-zahl').textContent = +k.getAttribute('data-n') + (an ? 1 : 0);
      zeige(k.parentNode.getAttribute('data-vorschlag'));
    });
  });
});

// --- Inhaltsverzeichnis der Langtexte: aktueller Abschnitt wird markiert, sonst keine Bewegung ---
alle('.toc').forEach(function(toc){
  if(!hatIO) return;
  var links = alle('a', toc), nach = {};
  links.forEach(function(a){ nach[a.getAttribute('href').slice(1)] = a; });
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting || !nach[e.target.id]) return;
      links.forEach(function(a){ a.classList.remove('aktiv'); a.removeAttribute('aria-current'); });
      nach[e.target.id].classList.add('aktiv'); nach[e.target.id].setAttribute('aria-current', 'location');
    });
  }, {rootMargin:'0px 0px -70% 0px'});
  Object.keys(nach).forEach(function(id){ var z = document.getElementById(id); if(z) io.observe(z); });
});

// --- Sticky-Abschnitt: aktive Ansicht bestimmt den Text links ---
alle('[data-scrolly]').forEach(function(s){
  if(!hatIO) return;
  var schritte = alle('.schritt', s);
  s.classList.add('an');
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting) return;
      var akt = e.target.parentNode;
      schritte.forEach(function(x){ x.classList.toggle('aktiv', x === akt); });
    });
  }, {rootMargin:'-45% 0px -45% 0px'});
  alle('.schritt-bild', s).forEach(function(b){ io.observe(b); });
});

// --- Bausteine: Ansicht wählen, alle Felder stehen im HTML, nur eines ist sichtbar ---
alle('[data-wahl]').forEach(function(w){
  var knoepfe = alle('[data-wahl-knopf]', w), felder = alle('[data-wahl-feld]', w);
  knoepfe.forEach(function(k){
    k.addEventListener('click', function(){
      knoepfe.forEach(function(x){ x.setAttribute('aria-pressed', x === k ? 'true' : 'false'); });
      felder.forEach(function(f){ f.hidden = f.getAttribute('data-wahl-feld') !== k.getAttribute('data-wahl-knopf'); });
    });
  });
});

// --- Grosse Zahlen: kurz hochzählen, Endwert steht bereits im HTML ---
if(!ruhig && hatIO){
  var zio = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting) return;
      zio.unobserve(e.target);
      var el = e.target, ziel = +el.textContent, t0 = null;
      (function schritt(t){
        if(!t0) t0 = t;
        var f = Math.min(1, (t - t0) / 900);
        el.textContent = Math.round(ziel * (1 - Math.pow(1 - f, 3)));
        if(f < 1) requestAnimationFrame(schritt);
      })(performance.now());
    });
  }, {threshold:.6});
  alle('.zahl strong').forEach(function(z){ zio.observe(z); });
}
// --- Ablauf-Kette: Schritt erscheint beim Scrollen, die Linie zieht sich zum nächsten ---
alle('[data-ablauf]').forEach(function(k){
  if(!k.classList.contains('bewegt')) return;
  var teile = alle('.ablauf-schritt, .ablauf-ende', k);
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting) return;
      // alle Schritte bis zu diesem einblenden, damit die Linie nie Lücken hat
      for(var i = 0; i <= teile.indexOf(e.target); i++){ teile[i].classList.add('an'); io.unobserve(teile[i]); }
    });
  }, {rootMargin:'0px 0px -28% 0px'});
  teile.forEach(function(t){ io.observe(t); });
});

// --- Anfrage zum Ablauf: Schritt vorausfüllen, Namensfeld fokussieren ---
var ablaufForm = document.getElementById('ablauf-anfrage');
if(ablaufForm){
  alle('a[href="#ablauf-anfrage"]').forEach(function(a){
    a.addEventListener('click', function(){
      var schritt = a.getAttribute('data-schritt'), baustein = a.getAttribute('data-baustein'),
          wahl = a.getAttribute('data-ablauf-wahl'), feld = ablaufForm.querySelector('textarea'),
          auswahl = ablaufForm.querySelector('select[name="ablauf"]');
      var zeile = schritt ? 'Interesse am Schritt: ' + schritt : baustein ? 'Interesse am Baustein: ' + baustein : '';
      if(zeile && feld && feld.value.indexOf(zeile) < 0){
        feld.value = (feld.value ? feld.value + '\n' : '') + zeile;
      }
      // Mehrere Ketten auf einer Seite: der Knopf wählt seine Kette im gemeinsamen Formular
      if(wahl && auswahl){ auswahl.value = wahl; }
      if(matchMedia('(pointer: fine)').matches){
        setTimeout(function(){ ablaufForm.querySelector('input[name="name"]').focus({preventScroll:true}); }, ruhig ? 0 : 600);
      }
    });
  });
}

// --- Fester Anfrage-Knopf: erst nach dem Einstieg, nicht wenn ein Formular oder der Cookie-Hinweis sichtbar ist ---
var fest = document.querySelector('[data-anfrage-fest]');
if(fest && ablaufForm){
  var schluss = document.getElementById('anfrage'), raf2 = 0;
  fest.hidden = false;
  function imBild(el){ var r = el.getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; }
  function setze(){
    raf2 = 0;
    var cookie = document.querySelector('.cookie-banner:not(.hidden)');
    var zeigen = scrollY > innerHeight * .9 && !imBild(ablaufForm) &&
      !(schluss && schluss.getBoundingClientRect().top < innerHeight) && !(cookie && cookie.offsetParent);
    fest.classList.toggle('zeigen', zeigen);
  }
  window.addEventListener('scroll', function(){ if(!raf2) raf2 = requestAnimationFrame(setze); }, {passive:true});
  window.addEventListener('resize', setze);
  document.addEventListener('click', function(){ setTimeout(setze, 50); });
  setze();
}

// --- /branchen/: Liste mit Vorschau ab 900px (Tabs: Hover, Fokus und Pfeiltasten wechseln, Klick öffnet die Seite),
// darunter Akkordeon (Tippen klappt auf, nur eine Branche offen). Ohne JavaScript bleibt die verlinkte Liste. ---
var bWahl = document.getElementById('branchen-wahl');
if(bWahl){
  var bListe = document.getElementById('branchen-liste');
  var bPanel = document.getElementById('branchen-panel');
  var bInhalt = bPanel.querySelector('.bpanel-inhalt');
  var bLinks = alle('.bliste-link', bListe);
  var breit = matchMedia('(min-width: 900px)');
  var aktiv = bLinks[0], wechselZeit = 0, hoverZeit = 0;
  var slug = function(l){ return l.getAttribute('data-branche'); };
  var bereich = function(l){ return document.getElementById('ba-' + slug(l)); };
  var kopie = function(l){ return document.getElementById('bv-' + slug(l)).content.cloneNode(true); };
  var belebe = function(el){
    if(ruhig) return;
    el.classList.remove('bvor-an'); void el.offsetWidth; el.classList.add('bvor-an');
  };
  var waehle = function(l){
    if(l === aktiv) return;
    aktiv = l;
    bLinks.forEach(function(x){
      x.setAttribute('aria-selected', x === l ? 'true' : 'false');
      x.tabIndex = x === l ? 0 : -1;
    });
    bPanel.setAttribute('aria-labelledby', l.id);
    clearTimeout(wechselZeit);
    var tausche = function(){
      bInhalt.textContent = '';
      bInhalt.appendChild(kopie(l));
      bInhalt.classList.remove('wechsel');
      belebe(bInhalt);
    };
    if(ruhig){ tausche(); return; }
    bInhalt.classList.add('wechsel');
    wechselZeit = setTimeout(tausche, 120);
  };
  var klappe = function(l){
    var auf = l.getAttribute('aria-expanded') !== 'true';
    bLinks.forEach(function(x){
      var b = bereich(x), ja = auf && x === l;
      x.setAttribute('aria-expanded', ja ? 'true' : 'false');
      if(ja && !b.firstElementChild) b.appendChild(kopie(x));
      b.hidden = !ja;
      if(ja) belebe(b);
    });
    if(auf && l.getBoundingClientRect().top < 80) l.scrollIntoView({block: 'start', behavior: ruhig ? 'auto' : 'smooth'});
  };
  var modus = function(){
    var tabs = breit.matches;
    if(tabs){
      bListe.setAttribute('role', 'tablist');
      bListe.setAttribute('aria-orientation', 'vertical');
      bListe.setAttribute('aria-describedby', 'branchen-hilfe');
      bPanel.setAttribute('role', 'tabpanel');
    } else {
      ['role', 'aria-orientation', 'aria-describedby'].forEach(function(a){ bListe.removeAttribute(a); });
      bPanel.removeAttribute('role');
    }
    bLinks.forEach(function(x){
      if(tabs){
        x.parentNode.setAttribute('role', 'presentation');
        x.setAttribute('role', 'tab');
        x.setAttribute('aria-controls', 'branchen-panel');
        x.setAttribute('aria-selected', x === aktiv ? 'true' : 'false');
        x.tabIndex = x === aktiv ? 0 : -1;
        x.removeAttribute('aria-expanded');
      } else {
        x.parentNode.removeAttribute('role');
        x.setAttribute('role', 'button');
        x.setAttribute('aria-controls', 'ba-' + slug(x));
        x.setAttribute('aria-expanded', bereich(x).hidden ? 'false' : 'true');
        x.removeAttribute('aria-selected');
        x.removeAttribute('tabindex');
      }
    });
  };
  modus();
  if(breit.addEventListener) breit.addEventListener('change', modus); else breit.addListener(modus);

  bLinks.forEach(function(l, i){
    l.addEventListener('mouseenter', function(){
      if(!breit.matches) return;
      clearTimeout(hoverZeit);
      hoverZeit = setTimeout(function(){ waehle(l); }, 70);
    });
    l.addEventListener('mouseleave', function(){ clearTimeout(hoverZeit); });
    l.addEventListener('focus', function(){ if(breit.matches) waehle(l); });
    l.addEventListener('click', function(e){
      if(breit.matches || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      klappe(l);
    });
    l.addEventListener('keydown', function(e){
      if(!breit.matches){
        if(e.key === ' '){ e.preventDefault(); klappe(l); }
        return;
      }
      var n = {ArrowDown: i + 1, ArrowRight: i + 1, ArrowUp: i - 1, ArrowLeft: i - 1, Home: 0, End: bLinks.length - 1}[e.key];
      if(n === undefined) return;
      e.preventDefault();
      bLinks[(n + bLinks.length) % bLinks.length].focus();
    });
  });
  // Kurzfassung des Ablaufs abspielen, sobald die Auswahl sichtbar wird
  if(!ruhig && hatIO){
    var bIo = new IntersectionObserver(function(e){
      if(!e[0].isIntersecting) return;
      belebe(breit.matches ? bInhalt : bereich(aktiv));
      bIo.disconnect();
    }, {threshold: .2});
    bIo.observe(bWahl);
  }
}

})();
