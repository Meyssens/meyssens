/* Anfrageformular "Pilot anfragen" (Gemeinden- und Unternehmen-Seite).

   ANFRAGE_ZIEL ist die einzige Einstellung: die Adresse, an die das Formular sendet,
   zum Beispiel ein Formspree-Endpoint wie "https://formspree.io/f/XXXXXXXX".
   Solange sie leer ist, öffnet das Formular ein vorbefülltes E-Mail an lionel@meyssens.ch. */
var ANFRAGE_ZIEL = "";

(function () {
  var MAIL = "lionel@meyssens.ch";
  var T = {
    de: {
      leer: {organisation: "Bitte geben Sie Ihre Gemeinde oder Organisation an.", name: "Bitte geben Sie Ihren Namen an.", email: "Bitte geben Sie Ihre E-Mail-Adresse an."},
      email: "Bitte geben Sie eine gültige E-Mail-Adresse an, zum Beispiel name@beispiel.ch.",
      einw: "Bitte bestätigen Sie die Einwilligung zur Datenverarbeitung.",
      pruefen: function (n) { return n === 1 ? "Bitte prüfen Sie das markierte Feld." : "Bitte prüfen Sie die " + n + " markierten Felder."; },
      sende: "Die Anfrage wird gesendet …",
      dankTitel: "Vielen Dank für Ihre Anfrage.",
      dank: "Ihre Angaben sind bei uns eingegangen. Lionel Nickelsen meldet sich persönlich bei Ihnen.",
      mailTitel: "Bitte E-Mail absenden",
      mail: "Ihr E-Mail-Programm öffnet sich mit einer vorbereiteten Nachricht. Die Anfrage ist erst unterwegs, wenn Sie diese E-Mail absenden.",
      mailNochmal: "E-Mail erneut öffnen",
      fehlerSenden: "Das Senden hat leider nicht geklappt.",
      perMail: "Anfrage stattdessen per E-Mail senden",
      betreff: "Pilot anfragen",
      L: {organisation: "Gemeinde / Organisation", name: "Name", email: "E-Mail", thema: "Thema oder Anliegen", seite: "Gesendet von"}
    },
    fr: {
      leer: {organisation: "Veuillez indiquer votre commune ou organisation.", name: "Veuillez indiquer votre nom.", email: "Veuillez indiquer votre adresse e-mail."},
      email: "Veuillez indiquer une adresse e-mail valide, par exemple nom@exemple.ch.",
      einw: "Veuillez confirmer votre consentement au traitement des données.",
      pruefen: function (n) { return n === 1 ? "Veuillez vérifier le champ signalé." : "Veuillez vérifier les " + n + " champs signalés."; },
      sende: "La demande est en cours d'envoi …",
      dankTitel: "Merci pour votre demande.",
      dank: "Vos informations nous sont parvenues. Lionel Nickelsen vous répondra personnellement.",
      mailTitel: "Veuillez envoyer l'e-mail",
      mail: "Votre programme de messagerie s'ouvre avec un message préparé. La demande n'est transmise qu'une fois cet e-mail envoyé.",
      mailNochmal: "Rouvrir l'e-mail",
      fehlerSenden: "L'envoi n'a malheureusement pas fonctionné.",
      perMail: "Envoyer la demande par e-mail",
      betreff: "Demande de pilote",
      L: {organisation: "Commune / organisation", name: "Nom", email: "E-mail", thema: "Sujet ou demande", seite: "Envoyé depuis"}
    },
    it: {
      leer: {organisation: "Indicate il vostro comune o la vostra organizzazione.", name: "Indicate il vostro nome.", email: "Indicate il vostro indirizzo e-mail."},
      email: "Indicate un indirizzo e-mail valido, ad esempio nome@esempio.ch.",
      einw: "Confermate il consenso al trattamento dei dati.",
      pruefen: function (n) { return n === 1 ? "Verificate il campo segnalato." : "Verificate i " + n + " campi segnalati."; },
      sende: "Invio della richiesta in corso …",
      dankTitel: "Grazie per la vostra richiesta.",
      dank: "I vostri dati ci sono pervenuti. Lionel Nickelsen vi risponderà personalmente.",
      mailTitel: "Inviate l'e-mail",
      mail: "Il vostro programma di posta si apre con un messaggio preparato. La richiesta viene trasmessa solo quando inviate questa e-mail.",
      mailNochmal: "Riaprire l'e-mail",
      fehlerSenden: "Purtroppo l'invio non è riuscito.",
      perMail: "Inviare la richiesta per e-mail",
      betreff: "Richiesta progetto pilota",
      L: {organisation: "Comune / organizzazione", name: "Nome", email: "E-mail", thema: "Tema o richiesta", seite: "Inviato da"}
    },
    en: {
      leer: {organisation: "Please enter your municipality or organisation.", name: "Please enter your name.", email: "Please enter your email address."},
      email: "Please enter a valid email address, for example name@example.ch.",
      einw: "Please confirm your consent to data processing.",
      pruefen: function (n) { return n === 1 ? "Please check the highlighted field." : "Please check the " + n + " highlighted fields."; },
      sende: "Sending your request …",
      dankTitel: "Thank you for your request.",
      dank: "We have received your details. Lionel Nickelsen will get back to you personally.",
      mailTitel: "Please send the email",
      mail: "Your email program opens with a prepared message. The request is only on its way once you send this email.",
      mailNochmal: "Open the email again",
      fehlerSenden: "Unfortunately, sending did not work.",
      perMail: "Send the request by email instead",
      betreff: "Pilot request",
      L: {organisation: "Municipality / organisation", name: "Name", email: "Email", thema: "Topic or request", seite: "Sent from"}
    }
  };

  function text() {
    var l = (document.documentElement.lang || "de").slice(0, 2);
    return T[l] || T.de;
  }

  function mailLink(f, tx) {
    var e = f.elements, nl = "\r\n";
    var zeilen = [
      tx.L.organisation + ": " + e.organisation.value.trim(),
      tx.L.name + ": " + e.name.value.trim(),
      tx.L.email + ": " + e.email.value.trim()
    ];
    if (e.thema.value.trim()) zeilen.push("", tx.L.thema + ":", e.thema.value.trim());
    zeilen.push("", tx.L.seite + ": " + location.href.split("#")[0]);
    return "mailto:" + MAIL + "?subject=" + encodeURIComponent(tx.betreff + ": " + e.organisation.value.trim()) +
           "&body=" + encodeURIComponent(zeilen.join(nl));
  }

  function zeigeDank(f, titel, inhalt, link) {
    var d = f.parentNode.querySelector(".anfrage-dank");
    d.querySelector("h3").textContent = titel;
    var p = d.querySelector("p");
    p.textContent = inhalt;
    if (link) {
      p.appendChild(document.createTextNode(" "));
      var a = document.createElement("a");
      a.href = link.href;
      a.textContent = link.text;
      p.appendChild(a);
    }
    f.hidden = true;
    d.hidden = false;
    d.focus();
  }

  document.querySelectorAll("form[data-anfrage]").forEach(function (f) {
    var pflicht = [f.elements.organisation, f.elements.name, f.elements.email, f.elements.einwilligung];
    var status = f.querySelector(".anfrage-status");
    var versucht = false;

    function setzeFehler(feld, meldung) {
      var p = document.getElementById(feld.id + "-fehler");
      if (meldung) {
        feld.setAttribute("aria-invalid", "true");
        p.textContent = meldung;
        p.hidden = false;
      } else {
        feld.removeAttribute("aria-invalid");
        p.textContent = "";
        p.hidden = true;
      }
    }

    function pruefe(feld) {
      var tx = text(), meldung = "";
      if (feld.type === "checkbox") {
        if (!feld.checked) meldung = tx.einw;
      } else {
        var wert = feld.value.trim();
        // data-leer: eigene Meldung der Seite (nur Deutsch, z. B. "Unternehmen" statt "Gemeinde")
        if (!wert) meldung = (feld.dataset.leer && tx === T.de) ? feld.dataset.leer : tx.leer[feld.name];
        else if (feld.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(wert)) meldung = tx.email;
      }
      setzeFehler(feld, meldung);
      return !meldung;
    }

    // Nach dem ersten Absendeversuch Fehler beim Verlassen eines Felds sofort aktualisieren
    pflicht.forEach(function (feld) {
      feld.addEventListener(feld.type === "checkbox" ? "change" : "blur", function () { if (versucht) pruefe(feld); });
    });

    f.addEventListener("submit", function (e) {
      e.preventDefault();
      versucht = true;
      var tx = text();
      var falsch = pflicht.filter(function (feld) { return !pruefe(feld); });
      if (falsch.length) {
        status.className = "anfrage-status err";
        status.textContent = tx.pruefen(falsch.length);
        falsch[0].focus();
        return;
      }
      status.className = "anfrage-status";
      status.textContent = "";

      // Honeypot ausgefüllt: vermutlich ein Bot, nichts senden
      if (f.elements._gotcha && f.elements._gotcha.value) {
        zeigeDank(f, tx.dankTitel, tx.dank);
        return;
      }

      if (!ANFRAGE_ZIEL) {
        var link = mailLink(f, tx);
        window.location.href = link;
        zeigeDank(f, tx.mailTitel, tx.mail, {href: link, text: tx.mailNochmal});
        return;
      }

      var knopf = f.querySelector('button[type="submit"]');
      knopf.disabled = true;
      status.textContent = tx.sende;
      fetch(ANFRAGE_ZIEL, {method: "POST", body: new FormData(f), headers: {"Accept": "application/json"}})
        .then(function (r) {
          if (!r.ok) throw new Error("Senden fehlgeschlagen");
          zeigeDank(f, tx.dankTitel, tx.dank);
        })
        .catch(function () {
          status.className = "anfrage-status err";
          status.textContent = tx.fehlerSenden + " ";
          var a = document.createElement("a");
          a.href = mailLink(f, tx);
          a.textContent = tx.perMail;
          status.appendChild(a);
        })
        .then(function () { knopf.disabled = false; });
    });
  });
})();
