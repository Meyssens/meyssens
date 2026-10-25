/* Sprachumschaltung der Gemeinden-Seite (DE steht im HTML, FR/IT/EN hier). Aus gemeinden/index.html ausgelagert,
   damit die Seite schneller lädt; wird erst geladen, wenn eine andere Sprache gewählt ist oder war. */
const I18N = {
  en: {
    "nav.pilot":"Pilot","pilot.label":"Pilot","pilot.title":"A no-obligation pilot for your municipality","pilot.lead":"We set up the platform free of charge and personally support your first process for three months, with no contract and no obligation.","pilot.f1.h":"Free setup","pilot.f1.p":"We set up the platform for your municipality free of charge.","pilot.f2.h":"Three months of personal support","pilot.f2.p":"We personally support your first process for three months.","pilot.f3.h":"No contract, no obligation","pilot.f3.p":"The pilot is non-binding. You decide afterwards whether to continue.","pilot.after":"Afterwards, you receive an offer based on the size of your municipality. We will tell you the price before the pilot ends.","pilot.cta":"Request a pilot","waerme.label":"Heat planning","waerme.title":"Heat planning with public participation","waerme.lead":"Public participation in heat planning, simple for residents and for the administration.","waerme.f1.h":"Comments on a map","waerme.f1.p":"Instead of by e-mail or on paper, residents submit their comments directly on a map.","waerme.f2.h":"Organised evaluation","waerme.f2.p":"The administration receives all feedback in an orderly way, in one place.","waerme.f3.h":"For all further processes","waerme.f3.p":"Once set up, you can use the platform for all further participation processes.","waerme.cta":"View demo","ref.lu":"City of Lucerne","ref.zh":"City of Zurich","ref.ls":"City of Lausanne","ref.ge":"Canton of Geneva","ref.eu":"European Commission","ref.more":"more cities","ref.lead":"Decidim — the foundation of Meyssens — is used by more than 400 cities and organisations worldwide","contact.form.anliegen":"Your request","contact.form.anl1":"Request a pilot","contact.form.anl2":"Other question",
    "nav.funktionen":"Features","nav.ablauf":"Process","nav.faq":"FAQ","nav.ueberuns":"About us","nav.demo":"Request a demo",
    "hero.chip":"Now available in Switzerland and Germany",
    "hero.title":"Digital participation<br>for <span class=\"hl\">your municipality.</span>",
    "hero.lead":"Meyssens brings cities and municipalities a ready-to-use civic participation platform — live in 2–4 weeks, personally supported, fairly priced.",
    "hero.btn1":"Watch live demo","hero.btn2":"Request a call",
    "hero.proof":"Trust proven open-source technology from Switzerland",
    "hero.card1.label":"Open source","hero.card1.val":"Open","hero.card1.sub":"No lock-in, data export at any time",
    "hero.card2.label":"Setup","hero.card2.sub":"Weeks to launch",
    "hero.hosting.label":"Hosting","hero.hosting.sub":"Switzerland",
    "hero.cancel.label":"Cancellation","hero.cancel.val":"Monthly","hero.cancel.sub":"no risk",
    "hero.support.label":"Support","hero.support.val":"Personal","hero.support.sub":"direct contact",
    "hero.langs.label":"Languages","hero.langs.sub":"multilingual",
    "funk.label":"Features","funk.title":"Everything your municipality needs",
    "funk.lead":"One platform for all participation processes — from proposals to participatory budgeting.",
    "funk.f1.tag":"Core","funk.f1.h":"Participation processes","funk.f1.p":"Structured processes on urban development, mobility or housing — with clear phases and timelines.","funk.f1.t1":"Informal","funk.f1.t2":"Formal","funk.f1.t3":"Multi-stage",
    "funk.f2.tag":"Voting","funk.f2.h":"Proposals & voting","funk.f2.p":"Residents submit ideas, comment and vote directly on the platform.",
    "funk.f3.tag":"Budget","funk.f3.h":"Participatory budget","funk.f3.p":"The population helps decide how the municipal budget is used — transparently and traceably.",
    "funk.f4.tag":"Events","funk.f4.h":"Events","funk.f4.p":"Publish and manage citizens' meetings, forums and events directly on the platform.",
    "funk.f5.tag":"Report a problem","funk.f5.h":"Report a problem","funk.f5.p":"Residents report damage in public spaces directly via photo and GPS location — the municipality responds transparently.","funk.f5.t1":"Photo upload","funk.f5.t3":"Categories",
    "funk.f6.tag":"Initiatives","funk.f6.h":"Citizen initiatives","funk.f6.p":"Residents launch their own initiatives, collect signatures and officially submit concerns.","funk.f6.t1":"Signatures","funk.f6.t2":"Deadlines","funk.f6.t3":"Official",
    "funk.f7.tag":"Privacy & security","funk.f7.h":"Open source · GDPR-compliant · hosted in Switzerland",
    "funk.f7.p":"Meyssens is built on <a href=\"https://decidim.org\" target=\"_blank\" style=\"color:var(--blue);text-decoration:none;font-weight:500\">Decidim</a> — open source, vetted and aligned with the Federal Council's <a href=\"https://digital.swiss/de/\" target=\"_blank\" style=\"color:var(--blue);text-decoration:none;font-weight:500\">Digital Switzerland 2026 Strategy</a>, which explicitly promotes open-source software in public administration.",
    "funk.f9.tag":"Map","funk.f9.h":"Map survey: place ideas where they arise","funk.f9.p":"Residents drop pins directly on your city or municipality map: “I like it here”, “There is a problem here”, “Idea for this place”. Administration sees at a glance where action is needed and can analyse contributions by category and location. Works on mobile with GPS location, based on OpenStreetMap.","funk.f9.t1":"Pins & categories","funk.f9.t2":"GPS location","funk.f9.t3":"OpenStreetMap","funk.f10.tag":"AI analysis","funk.f10.h":"AI-assisted analysis","funk.f10.p":"Many contributions, little time: on request, an AI summarises feedback, groups it into themes and shows the overall mood. Personal data is removed beforehand and the administration keeps the decision. On request, as an optional add-on module.","funk.f10.t1":"Themes & mood","funk.f10.t2":"Optional","funk.f8.tag":"Support","funk.f8.h":"Personal point of contact","funk.f8.p":"No ticket system, no anonymous hotline — you reach us directly. Fast answers, personal guidance.","funk.f8.t1":"Directly reachable","funk.f8.t2":"Multilingual",
    "ablauf.label":"Process","ablauf.title":"Live in 4 steps","ablauf.lead":"From first contact to launch — fast, straightforward, personally guided.",
    "ablauf.s1.h":"Consultation call","ablauf.s1.p":"We analyse your municipality's needs and show you the demo live.","ablauf.s1.tag":"Free",
    "ablauf.s2.h":"Configuration","ablauf.s2.p":"We set up the platform with your logo, topics and content in 2–4 weeks.","ablauf.s2.tag":"2–4 weeks",
    "ablauf.s3.h":"Training & launch","ablauf.s3.p":"Your team is trained, the platform is activated and we support you at launch.",
    "ablauf.s4.h":"Ongoing operation","ablauf.s4.p":"We handle hosting, updates and support — you focus on the content.","ablauf.s4.tag":"Ongoing",
    
    
    
    
    
    
    
    
    
    
    
    "ref.label":"Technology in use",
    
    "faq.label":"FAQ","faq.title":"Frequently asked questions","faq.lead":"Answers to the most important questions about Meyssens and digital civic participation.",
    "faq.q1":"Do we need our own IT infrastructure?","faq.a1":"No. Meyssens is a fully managed service. We take care of hosting, updates, backups and security. Your municipality needs no server infrastructure of its own and no in-house IT expertise.",
    "faq.q2":"Is a public tender required?","faq.a2":"For small contracts, direct award is often possible; the thresholds depend on your municipality and your country, and we are happy to clarify this with you in a conversation.",
    "faq.q3":"What is Decidim, and why does Meyssens build on it?","faq.a3":"Decidim is an open-source platform for digital democracy, developed by the City of Barcelona. It is used today by more than 400 organisations worldwide — including Zurich, Lucerne, Lausanne and Geneva.",
    "faq.q4":"How long does setup take?","faq.a4":"Usually 2–4 weeks. After a consultation call, we set up the platform with your logo, colours and content. We then train your team and support you through the official launch.",
    "faq.q5":"Which languages are supported?","faq.a5":"The platform supports German, French and Italian. Multilingual municipalities can run the platform entirely in several languages.",
    "faq.q6":"How secure is our residents' data?","faq.a6":"Hosting takes place exclusively in Switzerland. The platform is GDPR-compliant and complies with the Swiss Data Protection Act (DSG). Data is never passed to third parties or used for advertising.",
    "faq.q7":"What happens to our data if we cancel?","faq.a7":"You receive all your data in a standardised format (export). Since Decidim is open source, you can keep running the platform yourself or switch providers at any time. There is no lock-in.",
    "faq.q9":"Do you also work with cities and municipalities in Germany?","faq.a9":"Yes. Meyssens was developed in Switzerland and is open to cities and municipalities in Germany, currently especially in Baden-Württemberg. For customers in Germany, billing is in euros, with an individual pricing plan on request.","faq.q10":"Does the GDPR apply to German municipalities, and is hosting in Switzerland permitted?","faq.a10":"The platform is GDPR-compliant. The European Commission has recognised Switzerland as providing an adequate level of data protection, so data may be transferred to Switzerland without additional safeguards. We are happy to clarify details in a conversation.","faq.q8":"How many residents is the platform suitable for?","faq.a8":"Meyssens suits municipalities of any size — from small municipalities with under 5,000 residents to cities and cantons.",
    "about.label":"About us","about.title":"Your Swiss partner for digital participation","about.role":"Founder, Meyssens",
    "about.card":"Meyssens was founded with a clear mission: to give cities and municipalities access to modern digital civic participation — without major technical overhead and at fair prices.",
    "about.body":"We build on <a href=\"https://decidim.org\" target=\"_blank\" style=\"color:var(--blue);text-decoration:none;font-weight:500\">Decidim</a>, the proven open-source platform used in more than 400 cities worldwide. As a Swiss provider, we know the particularities of municipal administrations in the German-speaking region.",
    "about.quote":"\u201cEvery municipality deserves a modern platform that truly involves its residents.\u201d",
    "about.tech.dsgvo":"GDPR-compliant","about.tech.dsgvo.pill":"Data protection","about.tech.decidim.pill":"Foundation","about.tech.strategie.pill":"Compliant","about.tech.hosting":"Hosted in Switzerland","about.tech.hosting.pill":"Infrastructure","about.tech.langs":"Multilingual DE / FR / IT","about.tech.langs.pill":"Languages",
    "about.stat1.label":"Setup","about.stat1.sub":"to launch","about.stat2.label":"Hosting","about.stat2.sub":"Switzerland",
    "contact.label":"Contact","contact.title":"Ready for the next step?","contact.lead":"Write to us or schedule a free demo presentation for your municipality directly.",
    "contact.email.label":"Email","contact.demo.label":"Demo platform","contact.demo.link":"View demo →","contact.loc.label":"Location",
    "contact.form.vorname":"First name","contact.form.nachname":"Last name","contact.form.gemeinde":"Municipality / organisation",
    
    "contact.form.land":"Country","land.ch":"Switzerland","land.de":"Germany","land.at":"Austria","land.other":"Other country","contact.form.consent":"I have read the <a href=\"#datenschutz\" onclick=\"document.getElementById('datenschutz-modal').style.display='flex'\" style=\"color:var(--blue)\">privacy policy</a> and agree to my details being processed to handle my inquiry.","contact.form.nachricht":"Message (optional)","contact.form.nachricht.ph":"Your questions or requests...","contact.form.submit":"Send inquiry",
    "footer.platform":"Platform","footer.kontakt":"Contact","footer.links":"Links","footer.demo":"Watch live demo →","footer.strategie":"Digital Switzerland Strategy","footer.impressum":"Legal notice","footer.datenschutz":"Privacy policy",
    "footer.copy":"© 2026 Meyssens · Lausen, Basel-Landschaft · Switzerland"
  },

  fr: {
    "nav.pilot":"Pilote","pilot.label":"Pilote","pilot.title":"Un pilote sans engagement pour votre commune","pilot.lead":"Nous mettons en place la plateforme gratuitement et accompagnons personnellement votre première procédure pendant trois mois, sans contrat et sans engagement.","pilot.f1.h":"Mise en place gratuite","pilot.f1.p":"Nous mettons en place la plateforme pour votre commune gratuitement.","pilot.f2.h":"Trois mois d'accompagnement personnel","pilot.f2.p":"Nous accompagnons personnellement votre première procédure pendant trois mois.","pilot.f3.h":"Sans contrat, sans engagement","pilot.f3.p":"Le pilote est sans engagement. Vous décidez ensuite si vous souhaitez continuer.","pilot.after":"Ensuite, vous recevez une offre adaptée à la taille de votre commune. Nous vous communiquons le prix avant la fin du pilote.","pilot.cta":"Demander un pilote","waerme.label":"Planification thermique","waerme.title":"Planification thermique avec participation citoyenne","waerme.lead":"La participation du public à la planification thermique, simple pour la population et pour l'administration.","waerme.f1.h":"Prises de position sur une carte","waerme.f1.p":"Au lieu de les envoyer par e-mail ou sur papier, les habitants déposent leurs prises de position directement sur une carte.","waerme.f2.h":"Évaluation structurée","waerme.f2.p":"L'administration reçoit toutes les contributions de manière ordonnée, en un seul endroit.","waerme.f3.h":"Pour toutes les procédures suivantes","waerme.f3.p":"Une fois en place, la plateforme peut être utilisée pour toutes les autres procédures de participation.","waerme.cta":"Voir la démo","ref.lu":"Ville de Lucerne","ref.zh":"Ville de Zurich","ref.ls":"Ville de Lausanne","ref.ge":"Canton de Genève","ref.eu":"Commission européenne","ref.more":"autres villes","ref.lead":"Decidim — la base de Meyssens — est utilisé dans plus de 400 villes et organisations à travers le monde","contact.form.anliegen":"Votre demande","contact.form.anl1":"Demander un pilote","contact.form.anl2":"Autre question",
    "nav.funktionen":"Fonctions","nav.ablauf":"Déroulement","nav.faq":"FAQ","nav.ueberuns":"À propos","nav.demo":"Demander une démo",
    "hero.chip":"Disponible en Suisse et en Allemagne",
    "hero.title":"Participation numérique<br>pour <span class=\"hl\">votre commune.</span>",
    "hero.lead":"Meyssens offre aux villes et communes une plateforme de participation citoyenne clé en main — en ligne en 2 à 4 semaines, accompagnement personnalisé, tarifs équitables.",
    "hero.btn1":"Voir la démo live","hero.btn2":"Demander un entretien",
    "hero.proof":"Faites confiance à une technologie open source suisse éprouvée",
    "hero.card1.label":"Open source","hero.card1.val":"Ouvert","hero.card1.sub":"Sans dépendance, export des données à tout moment",
    "hero.card2.label":"Mise en place","hero.card2.sub":"Semaines jusqu'au lancement",
    "hero.hosting.label":"Hébergement","hero.hosting.sub":"Suisse",
    "hero.cancel.label":"Résiliation","hero.cancel.val":"Mensuelle","hero.cancel.sub":"sans risque",
    "hero.support.label":"Support","hero.support.val":"Personnel","hero.support.sub":"contact direct",
    "hero.langs.label":"Langues","hero.langs.sub":"multilingue",
    "funk.label":"Fonctions","funk.title":"Tout ce dont votre commune a besoin",
    "funk.lead":"Une plateforme pour tous les processus de participation — des propositions au budget participatif.",
    "funk.f1.tag":"Cœur","funk.f1.h":"Processus de participation","funk.f1.p":"Processus structurés sur le développement urbain, la mobilité ou le logement — avec des phases et des échéances claires.","funk.f1.t1":"Informel","funk.f1.t2":"Formel","funk.f1.t3":"Multi-étapes",
    "funk.f2.tag":"Vote","funk.f2.h":"Propositions & votes","funk.f2.p":"Les citoyennes et citoyens soumettent des idées, commentent et votent directement sur la plateforme.",
    "funk.f3.tag":"Budget","funk.f3.h":"Budget participatif","funk.f3.p":"La population décide de l'utilisation du budget communal — de manière transparente et traçable.",
    "funk.f4.tag":"Événements","funk.f4.h":"Événements","funk.f4.p":"Publiez et gérez assemblées citoyennes, forums et événements directement sur la plateforme.",
    "funk.f5.tag":"Signaler un dommage","funk.f5.h":"Signaler un dommage","funk.f5.p":"Les citoyennes et citoyens signalent les dommages dans l'espace public par photo et localisation GPS — la commune réagit de manière transparente.","funk.f5.t1":"Photo","funk.f5.t3":"Catégories",
    "funk.f6.tag":"Initiatives","funk.f6.h":"Initiatives citoyennes","funk.f6.p":"Les citoyennes et citoyens lancent leurs propres initiatives, récoltent des signatures et déposent officiellement leurs demandes.","funk.f6.t1":"Signatures","funk.f6.t2":"Délais","funk.f6.t3":"Officiel",
    "funk.f7.tag":"Protection des données & sécurité","funk.f7.h":"Open source · conforme RGPD · hébergement en Suisse",
    "funk.f7.p":"Meyssens repose sur <a href=\"https://decidim.org\" target=\"_blank\" style=\"color:var(--blue);text-decoration:none;font-weight:500\">Decidim</a> — open source, vérifié et conforme à la <a href=\"https://digital.swiss/de/\" target=\"_blank\" style=\"color:var(--blue);text-decoration:none;font-weight:500\">Stratégie Suisse numérique 2026</a> du Conseil fédéral, qui encourage explicitement les logiciels open source dans l'administration.",
    "funk.f9.tag":"Carte","funk.f9.h":"Sondage cartographique : situer les idées là où elles naissent","funk.f9.p":"Les habitants placent des repères directement sur la carte de votre ville ou commune : « Ici, j'aime », « Ici, il y a un problème », « Idée pour ce lieu ». L'administration voit d'un coup d'œil où agir et peut analyser les contributions par catégorie et lieu. Fonctionne sur mobile avec localisation GPS, sur la base d'OpenStreetMap.","funk.f9.t1":"Repères & catégories","funk.f9.t2":"Localisation GPS","funk.f9.t3":"OpenStreetMap","funk.f10.tag":"Analyse IA","funk.f10.h":"Analyse assistée par IA","funk.f10.p":"Beaucoup de contributions, peu de temps : sur demande, une IA résume les retours, les regroupe par thèmes et montre le climat général. Les données personnelles sont supprimées au préalable et l'administration garde la décision. Sur demande, en module complémentaire optionnel.","funk.f10.t1":"Thèmes & climat","funk.f10.t2":"Optionnel","funk.f8.tag":"Support","funk.f8.h":"Interlocuteur personnel","funk.f8.p":"Pas de système de tickets, pas de hotline anonyme — vous nous joignez directement. Réponses rapides, accompagnement personnalisé.","funk.f8.t1":"Joignable directement","funk.f8.t2":"Multilingue",
    "ablauf.label":"Déroulement","ablauf.title":"En ligne en 4 étapes","ablauf.lead":"Du premier contact jusqu'au lancement — rapide, simple, accompagné personnellement.",
    "ablauf.s1.h":"Entretien de conseil","ablauf.s1.p":"Nous analysons les besoins de votre commune et vous montrons la démo en direct.","ablauf.s1.tag":"Gratuit",
    "ablauf.s2.h":"Configuration","ablauf.s2.p":"Nous configurons la plateforme avec votre logo, vos thèmes et vos contenus en 2 à 4 semaines.","ablauf.s2.tag":"2–4 semaines",
    "ablauf.s3.h":"Formation & lancement","ablauf.s3.p":"Votre équipe est formée, la plateforme est activée et nous vous accompagnons au démarrage.",
    "ablauf.s4.h":"Exploitation continue","ablauf.s4.p":"Nous assurons l'hébergement, les mises à jour et le support — vous vous concentrez sur les contenus.","ablauf.s4.tag":"Permanent",
    
    
    
    
    
    
    
    
    
    
    
    "ref.label":"Technologie utilisée",
    
    "faq.label":"FAQ","faq.title":"Questions fréquentes","faq.lead":"Réponses aux questions les plus importantes sur Meyssens et la participation citoyenne numérique.",
    "faq.q1":"Avons-nous besoin de notre propre infrastructure informatique ?","faq.a1":"Non. Meyssens est un service entièrement géré. Nous nous occupons de l'hébergement, des mises à jour, des sauvegardes et de la sécurité. Votre commune n'a besoin ni de sa propre infrastructure serveur ni de compétences informatiques internes.",
    "faq.q2":"Un appel d'offres public est-il nécessaire ?","faq.a2":"Pour les petits mandats, une attribution directe est souvent possible ; les seuils dépendent de votre commune et de votre pays, nous le clarifions volontiers avec vous lors d'un entretien.",
    "faq.q3":"Qu'est-ce que Decidim et pourquoi Meyssens l'utilise-t-il ?","faq.a3":"Decidim est une plateforme open source pour la démocratie numérique, développée par la Ville de Barcelone. Elle est utilisée aujourd'hui par plus de 400 organisations dans le monde — dont Zurich, Lucerne, Lausanne et Genève.",
    "faq.q4":"Combien de temps dure la mise en place ?","faq.a4":"En général 2 à 4 semaines. Après un entretien de conseil, nous configurons la plateforme avec votre logo, vos couleurs et vos contenus. Nous formons ensuite votre équipe et vous accompagnons lors du lancement officiel.",
    "faq.q5":"Quelles langues sont prises en charge ?","faq.a5":"La plateforme prend en charge l'allemand, le français et l'italien. Les communes plurilingues peuvent exploiter la plateforme entièrement dans plusieurs langues.",
    "faq.q6":"Quelle est la sécurité des données de nos habitantes et habitants ?","faq.a6":"L'hébergement se fait exclusivement en Suisse. La plateforme est conforme au RGPD et à la loi suisse sur la protection des données (LPD). Les données ne sont jamais transmises à des tiers ni utilisées à des fins publicitaires.",
    "faq.q7":"Qu'advient-il de nos données en cas de résiliation ?","faq.a7":"Vous recevez toutes vos données dans un format standardisé (export). Decidim étant open source, vous pouvez continuer à exploiter la plateforme vous-même ou changer de prestataire à tout moment. Aucun verrouillage propriétaire.",
    "faq.q9":"Travaillez-vous aussi avec des villes et communes en Allemagne ?","faq.a9":"Oui. Meyssens a été développé en Suisse et est ouvert aux villes et communes en Allemagne, actuellement surtout dans le Bade-Wurtemberg. Pour les clients en Allemagne, la facturation se fait en euros, avec un plan tarifaire individuel sur demande.","faq.q10":"Le RGPD s'applique-t-il aux communes allemandes, et l'hébergement en Suisse est-il autorisé ?","faq.a10":"La plateforme est conforme au RGPD. La Commission européenne a reconnu à la Suisse un niveau de protection des données adéquat, de sorte que les données peuvent être transférées en Suisse sans garanties supplémentaires. Nous clarifions volontiers les détails lors d'un entretien.","faq.q8":"Pour combien d'habitants la plateforme convient-elle ?","faq.a8":"Meyssens convient aux communes de toutes tailles — des petites communes de moins de 5'000 habitants jusqu'aux villes et cantons.",
    "about.label":"À propos","about.title":"Votre partenaire suisse pour la participation numérique","about.role":"Fondateur, Meyssens",
    "about.card":"Meyssens a été fondé avec une mission claire : permettre aux villes et communes d'accéder à une participation citoyenne numérique moderne — sans lourdeur technique et à des prix équitables.",
    "about.body":"Nous misons sur <a href=\"https://decidim.org\" target=\"_blank\" style=\"color:var(--blue);text-decoration:none;font-weight:500\">Decidim</a>, la plateforme open source éprouvée, utilisée dans plus de 400 villes à travers le monde. En tant que prestataire suisse, nous connaissons les particularités des administrations communales dans l'espace germanophone.",
    "about.quote":"« Chaque commune mérite une plateforme moderne qui implique réellement ses citoyennes et citoyens. »",
    "about.tech.dsgvo":"Conforme RGPD","about.tech.dsgvo.pill":"Protection des données","about.tech.decidim.pill":"Base","about.tech.strategie.pill":"Conforme","about.tech.hosting":"Hébergement en Suisse","about.tech.hosting.pill":"Infrastructure","about.tech.langs":"Multilingue DE / FR / IT","about.tech.langs.pill":"Langues",
    "about.stat1.label":"Mise en place","about.stat1.sub":"jusqu'au lancement","about.stat2.label":"Hébergement","about.stat2.sub":"Suisse",
    "contact.label":"Contact","contact.title":"Prêt pour la prochaine étape ?","contact.lead":"Écrivez-nous ou convenez directement d'une présentation de démo gratuite pour votre commune.",
    "contact.email.label":"E-mail","contact.demo.label":"Plateforme de démo","contact.demo.link":"Voir la démo →","contact.loc.label":"Lieu",
    "contact.form.vorname":"Prénom","contact.form.nachname":"Nom","contact.form.gemeinde":"Commune / organisation",
    
    "contact.form.land":"Pays","land.ch":"Suisse","land.de":"Allemagne","land.at":"Autriche","land.other":"Autre pays","contact.form.consent":"J'ai lu la <a href=\"#datenschutz\" onclick=\"document.getElementById('datenschutz-modal').style.display='flex'\" style=\"color:var(--blue)\">déclaration de confidentialité</a> et j'accepte le traitement de mes données pour répondre à ma demande.","contact.form.nachricht":"Message (facultatif)","contact.form.nachricht.ph":"Vos questions ou souhaits...","contact.form.submit":"Envoyer la demande",
    "footer.platform":"Plateforme","footer.kontakt":"Contact","footer.links":"Liens","footer.demo":"Voir la démo live →","footer.strategie":"Stratégie numérique CH","footer.impressum":"Mentions légales","footer.datenschutz":"Protection des données",
    "footer.copy":"© 2026 Meyssens · Lausen, Bâle-Campagne · Suisse"
  },
  it: {
    "nav.pilot":"Pilota","pilot.label":"Progetto pilota","pilot.title":"Un progetto pilota senza impegno per il vostro comune","pilot.lead":"Configuriamo gratuitamente la piattaforma e accompagniamo personalmente la vostra prima procedura per tre mesi, senza contratto e senza impegno.","pilot.f1.h":"Configurazione gratuita","pilot.f1.p":"Configuriamo la piattaforma per il vostro comune gratuitamente.","pilot.f2.h":"Tre mesi di accompagnamento personale","pilot.f2.p":"Accompagniamo personalmente la vostra prima procedura per tre mesi.","pilot.f3.h":"Senza contratto, senza impegno","pilot.f3.p":"Il progetto pilota non è vincolante. Decidete poi se continuare.","pilot.after":"In seguito ricevete un'offerta in base alle dimensioni del vostro comune. Vi comunichiamo il prezzo prima della fine del progetto pilota.","pilot.cta":"Richiedere un progetto pilota","waerme.label":"Pianificazione termica","waerme.title":"Pianificazione termica con partecipazione dei cittadini","waerme.lead":"La partecipazione pubblica alla pianificazione termica, semplice per la popolazione e per l'amministrazione.","waerme.f1.h":"Osservazioni su una mappa","waerme.f1.p":"Invece che per e-mail o su carta, gli abitanti inviano le loro osservazioni direttamente su una mappa.","waerme.f2.h":"Valutazione ordinata","waerme.f2.p":"L'amministrazione riceve tutti i contributi in modo ordinato, in un unico posto.","waerme.f3.h":"Per tutte le procedure successive","waerme.f3.p":"Una volta configurata, la piattaforma può essere usata per tutte le altre procedure partecipative.","waerme.cta":"Vedere la demo","ref.lu":"Città di Lucerna","ref.zh":"Città di Zurigo","ref.ls":"Città di Losanna","ref.ge":"Cantone di Ginevra","ref.eu":"Commissione europea","ref.more":"altre città","ref.lead":"Decidim — la base di Meyssens — è utilizzato in oltre 400 città e organizzazioni nel mondo","contact.form.anliegen":"La vostra richiesta","contact.form.anl1":"Richiedere un progetto pilota","contact.form.anl2":"Altra domanda",
    "nav.funktionen":"Funzioni","nav.ablauf":"Procedura","nav.faq":"FAQ","nav.ueberuns":"Chi siamo","nav.demo":"Richiedi una demo",
    "hero.chip":"Ora disponibile in Svizzera e in Germania",
    "hero.title":"Partecipazione digitale<br>per <span class=\"hl\">il vostro comune.</span>",
    "hero.lead":"Meyssens offre a città e comuni una piattaforma di partecipazione civica pronta all'uso — online in 2–4 settimane, accompagnamento personale, prezzi equi.",
    "hero.btn1":"Guarda la demo live","hero.btn2":"Richiedi un colloquio",
    "hero.proof":"Affidatevi a una tecnologia open source svizzera collaudata",
    "hero.card1.label":"Open source","hero.card1.val":"Aperto","hero.card1.sub":"Nessun vincolo, esportazione dei dati in ogni momento",
    "hero.card2.label":"Configurazione","hero.card2.sub":"Settimane fino al lancio",
    "hero.hosting.label":"Hosting","hero.hosting.sub":"Svizzera",
    "hero.cancel.label":"Disdetta","hero.cancel.val":"Mensile","hero.cancel.sub":"nessun rischio",
    "hero.support.label":"Supporto","hero.support.val":"Personale","hero.support.sub":"contatto diretto",
    "hero.langs.label":"Lingue","hero.langs.sub":"multilingue",
    "funk.label":"Funzioni","funk.title":"Tutto ciò di cui il vostro comune ha bisogno",
    "funk.lead":"Una piattaforma per tutti i processi di partecipazione — dalle proposte al bilancio partecipativo.",
    "funk.f1.tag":"Base","funk.f1.h":"Processi di partecipazione","funk.f1.p":"Processi strutturati su sviluppo urbano, mobilità o abitazione — con fasi e tempistiche chiare.","funk.f1.t1":"Informale","funk.f1.t2":"Formale","funk.f1.t3":"Multi-fase",
    "funk.f2.tag":"Votazione","funk.f2.h":"Proposte & votazione","funk.f2.p":"Cittadine e cittadini presentano idee, commentano e votano direttamente sulla piattaforma.",
    "funk.f3.tag":"Bilancio","funk.f3.h":"Bilancio partecipativo","funk.f3.p":"La popolazione decide come utilizzare il bilancio comunale — in modo trasparente e tracciabile.",
    "funk.f4.tag":"Eventi","funk.f4.h":"Eventi","funk.f4.p":"Pubblicate e gestite assemblee cittadine, forum ed eventi direttamente sulla piattaforma.",
    "funk.f5.tag":"Segnala un danno","funk.f5.h":"Segnala un danno","funk.f5.p":"Cittadine e cittadini segnalano danni nello spazio pubblico direttamente con foto e posizione GPS — il comune risponde in modo trasparente.","funk.f5.t1":"Foto","funk.f5.t3":"Categorie",
    "funk.f6.tag":"Iniziative","funk.f6.h":"Iniziative popolari","funk.f6.p":"Cittadine e cittadini lanciano proprie iniziative, raccolgono firme e presentano ufficialmente le loro richieste.","funk.f6.t1":"Firme","funk.f6.t2":"Scadenze","funk.f6.t3":"Ufficiale",
    "funk.f7.tag":"Protezione dei dati & sicurezza","funk.f7.h":"Open source · conforme RGPD · hosting in Svizzera",
    "funk.f7.p":"Meyssens si basa su <a href=\"https://decidim.org\" target=\"_blank\" style=\"color:var(--blue);text-decoration:none;font-weight:500\">Decidim</a> — open source, verificato e in linea con la <a href=\"https://digital.swiss/de/\" target=\"_blank\" style=\"color:var(--blue);text-decoration:none;font-weight:500\">Strategia Svizzera digitale 2026</a> del Consiglio federale, che promuove esplicitamente il software open source nell'amministrazione.",
    "funk.f9.tag":"Mappa","funk.f9.h":"Sondaggio su mappa: collocare le idee dove nascono","funk.f9.p":"I cittadini inseriscono segnaposto direttamente sulla mappa della vostra città o comune: «Qui mi piace», «Qui c'è un problema», «Idea per questo luogo». L'amministrazione vede a colpo d'occhio dove intervenire e può analizzare i contributi per categoria e luogo. Funziona anche da mobile con posizione GPS, su base OpenStreetMap.","funk.f9.t1":"Segnaposto & categorie","funk.f9.t2":"Posizione GPS","funk.f9.t3":"OpenStreetMap","funk.f10.tag":"Analisi IA","funk.f10.h":"Analisi assistita da IA","funk.f10.p":"Molti contributi, poco tempo: su richiesta, un'IA riassume i riscontri, li raggruppa per temi e mostra il clima generale. I dati personali vengono rimossi prima e l'amministrazione mantiene la decisione. Su richiesta, come modulo aggiuntivo opzionale.","funk.f10.t1":"Temi & clima","funk.f10.t2":"Opzionale","funk.f8.tag":"Supporto","funk.f8.h":"Referente personale","funk.f8.p":"Nessun sistema di ticket, nessuna hotline anonima — ci contattate direttamente. Risposte rapide, accompagnamento personale.","funk.f8.t1":"Contatto diretto","funk.f8.t2":"Multilingue",
    "ablauf.label":"Procedura","ablauf.title":"Online in 4 passi","ablauf.lead":"Dal primo contatto al lancio — veloce, semplice, con accompagnamento personale.",
    "ablauf.s1.h":"Colloquio di consulenza","ablauf.s1.p":"Analizziamo le esigenze del vostro comune e vi mostriamo la demo dal vivo.","ablauf.s1.tag":"Gratuito",
    "ablauf.s2.h":"Configurazione","ablauf.s2.p":"Configuriamo la piattaforma con il vostro logo, temi e contenuti in 2–4 settimane.","ablauf.s2.tag":"2–4 settimane",
    "ablauf.s3.h":"Formazione & lancio","ablauf.s3.p":"Il vostro team viene formato, la piattaforma attivata e vi accompagniamo al lancio.",
    "ablauf.s4.h":"Gestione continua","ablauf.s4.p":"Ci occupiamo di hosting, aggiornamenti e supporto — voi vi concentrate sui contenuti.","ablauf.s4.tag":"Permanente",
    
    
    
    
    
    
    
    
    
    
    
    "ref.label":"Tecnologia utilizzata",
    
    "faq.label":"FAQ","faq.title":"Domande frequenti","faq.lead":"Risposte alle domande più importanti su Meyssens e la partecipazione civica digitale.",
    "faq.q1":"Abbiamo bisogno di una nostra infrastruttura IT?","faq.a1":"No. Meyssens è un servizio interamente gestito. Ci occupiamo di hosting, aggiornamenti, backup e sicurezza. Il vostro comune non necessita di infrastruttura server propria né di competenze IT interne.",
    "faq.q2":"È necessario un bando pubblico?","faq.a2":"Per piccoli incarichi è spesso possibile un affidamento diretto; i limiti dipendono dal vostro comune e dal vostro paese, ne parliamo volentieri in un colloquio.",
    "faq.q3":"Che cos'è Decidim e perché Meyssens lo utilizza?","faq.a3":"Decidim è una piattaforma open source per la democrazia digitale, sviluppata dalla Città di Barcellona. Oggi è utilizzata da oltre 400 organizzazioni nel mondo — tra cui Zurigo, Lucerna, Losanna e Ginevra.",
    "faq.q4":"Quanto dura la configurazione?","faq.a4":"Generalmente 2–4 settimane. Dopo un colloquio di consulenza, configuriamo la piattaforma con il vostro logo, i vostri colori e contenuti. Successivamente formiamo il vostro team e vi accompagniamo al lancio ufficiale.",
    "faq.q5":"Quali lingue sono supportate?","faq.a5":"La piattaforma supporta tedesco, francese e italiano. I comuni plurilingue possono gestire la piattaforma interamente in più lingue.",
    "faq.q6":"Quanto sono sicuri i dati delle nostre abitanti e dei nostri abitanti?","faq.a6":"L'hosting avviene esclusivamente in Svizzera. La piattaforma è conforme al RGPD e alla legge svizzera sulla protezione dei dati (LPD). I dati non vengono mai ceduti a terzi né utilizzati a fini pubblicitari.",
    "faq.q7":"Cosa succede ai nostri dati in caso di disdetta?","faq.a7":"Ricevete tutti i vostri dati in un formato standardizzato (esportazione). Essendo Decidim open source, potete continuare a gestire la piattaforma autonomamente o cambiare fornitore in qualsiasi momento. Nessun vincolo.",
    "faq.q9":"Lavorate anche con città e comuni in Germania?","faq.a9":"Sì. Meyssens è stato sviluppato in Svizzera ed è aperto a città e comuni in Germania, attualmente soprattutto nel Baden-Württemberg. Per i clienti in Germania la fatturazione avviene in euro, con un piano tariffario individuale su richiesta.","faq.q10":"Il RGPD vale per i comuni tedeschi, ed è consentito l'hosting in Svizzera?","faq.a10":"La piattaforma è conforme al RGPD. La Commissione europea ha riconosciuto alla Svizzera un livello adeguato di protezione dei dati, quindi i dati possono essere trasferiti in Svizzera senza garanzie aggiuntive. Chiariamo volentieri i dettagli in un colloquio.","faq.q8":"Per quanti abitanti è adatta la piattaforma?","faq.a8":"Meyssens è adatto a comuni di ogni dimensione — da piccoli comuni con meno di 5'000 abitanti fino a città e cantoni.",
    "about.label":"Chi siamo","about.title":"Il vostro partner svizzero per la partecipazione digitale","about.role":"Fondatore, Meyssens",
    "about.card":"Meyssens è stato fondato con una missione chiara: offrire a città e comuni l'accesso a una partecipazione civica digitale moderna — senza grandi oneri tecnici e a prezzi equi.",
    "about.body":"Puntiamo su <a href=\"https://decidim.org\" target=\"_blank\" style=\"color:var(--blue);text-decoration:none;font-weight:500\">Decidim</a>, la collaudata piattaforma open source utilizzata in oltre 400 città nel mondo. Come fornitore svizzero, conosciamo le particolarità delle amministrazioni comunali nell'area germanofona.",
    "about.quote":"«Ogni comune merita una piattaforma moderna che coinvolga davvero le cittadine e i cittadini.»",
    "about.tech.dsgvo":"Conforme RGPD","about.tech.dsgvo.pill":"Protezione dati","about.tech.decidim.pill":"Base","about.tech.strategie.pill":"Conforme","about.tech.hosting":"Hosting in Svizzera","about.tech.hosting.pill":"Infrastruttura","about.tech.langs":"Multilingue DE / FR / IT","about.tech.langs.pill":"Lingue",
    "about.stat1.label":"Configurazione","about.stat1.sub":"fino al lancio","about.stat2.label":"Hosting","about.stat2.sub":"Svizzera",
    "contact.label":"Contatto","contact.title":"Pronti per il prossimo passo?","contact.lead":"Scriveteci o fissate direttamente una presentazione demo gratuita per il vostro comune.",
    "contact.email.label":"E-mail","contact.demo.label":"Piattaforma demo","contact.demo.link":"Guarda la demo →","contact.loc.label":"Sede",
    "contact.form.vorname":"Nome","contact.form.nachname":"Cognome","contact.form.gemeinde":"Comune / organizzazione",
    
    "contact.form.land":"Paese","land.ch":"Svizzera","land.de":"Germania","land.at":"Austria","land.other":"Altro paese","contact.form.consent":"Ho letto l'<a href=\"#datenschutz\" onclick=\"document.getElementById('datenschutz-modal').style.display='flex'\" style=\"color:var(--blue)\">informativa sulla privacy</a> e acconsento al trattamento dei miei dati per gestire la richiesta.","contact.form.nachricht":"Messaggio (facoltativo)","contact.form.nachricht.ph":"Le vostre domande o richieste...","contact.form.submit":"Invia richiesta",
    "footer.platform":"Piattaforma","footer.kontakt":"Contatto","footer.links":"Link","footer.demo":"Guarda la demo live →","footer.strategie":"Strategia digitale CH","footer.impressum":"Note legali","footer.datenschutz":"Protezione dei dati",
    "footer.copy":"© 2026 Meyssens · Lausen, Basilea Campagna · Svizzera"
  }
};

// Übersetzungen der Beispielansichten (Gerätefenster)
Object.assign(I18N.fr, {"g.demo.titel": "Participer à la commune exemple", "g.beispiel": "Exemple", "g.beispielansicht": "Aperçu d'exemple", "g.demo.prozess": "Processus participatif", "g.demo.frage": "Comment réaménager la place du village ?", "g.demo.ph1": "Recueillir des idées", "g.demo.ph2": "Vote", "g.demo.ph3": "Mise en œuvre", "g.demo.v0": "Plus de bancs près de la fontaine", "g.demo.o0": "Place du village", "g.demo.v1": "Supports à vélos près de l'école", "g.demo.o1": "École", "g.demo.v2": "Abri à l'arrêt de bus", "g.demo.o2": "Arrêt de bus", "g.demo.unterstuetzen": "Soutenir", "g.demo.hinweis": "Exemple au contenu fictif. Cliquez sur un repère ou soutenez une proposition. Rien n'est enregistré.", "g.ablauf1.titel": "Notes d'entretien", "g.a1.kopf": "Premier entretien", "g.a1.p1": "Besoins de la commune", "g.a1.p2": "Voir la démo en direct", "g.a1.p3": "Définir les prochaines étapes", "g.a1.fuss": "Gratuit et sans engagement", "g.ablauf2.titel": "Configuration", "g.a2.name": "Commune exemple", "g.a2.themen": "Thèmes", "g.a2.t1": "Mobilité", "g.a2.t2": "Logement", "g.a2.t3": "Espaces publics", "g.a2.inhalte": "Contenus", "g.a2.fuss": "Logo, thèmes et contenus de votre commune", "g.ablauf3.titel": "Page d'accueil de la plateforme", "g.a3.p1": "Réaménagement de la place du village", "g.a3.p2": "Budget participatif", "g.a3.offen": "Ouvert", "g.a3.bald": "Bientôt", "g.a3.fuss": "Plateforme mise en ligne", "g.ablauf4.titel": "Exploitation", "g.a4.s1": "Suisse", "g.a4.s2": "en continu", "g.a4.s3": "personnel", "g.a4.fuss": "Vous vous occupez des contenus.", "g.plan.platz": "Place", "g.plan.schule": "École", "g.plan.strasse": "Rue du village"});
Object.assign(I18N.it, {"g.demo.titel": "Partecipare nel comune di esempio", "g.beispiel": "Esempio", "g.beispielansicht": "Vista di esempio", "g.demo.prozess": "Processo partecipativo", "g.demo.frage": "Come riqualificare la piazza del paese?", "g.demo.ph1": "Raccogliere idee", "g.demo.ph2": "Votazione", "g.demo.ph3": "Attuazione", "g.demo.v0": "Più panchine vicino alla fontana", "g.demo.o0": "Piazza del paese", "g.demo.v1": "Rastrelliere per bici presso la scuola", "g.demo.o1": "Scuola", "g.demo.v2": "Pensilina alla fermata del bus", "g.demo.o2": "Fermata del bus", "g.demo.unterstuetzen": "Sostenere", "g.demo.hinweis": "Esempio con contenuti inventati. Fate clic su un segnaposto o sostenete una proposta. Nulla viene salvato.", "g.ablauf1.titel": "Note del colloquio", "g.a1.kopf": "Primo colloquio", "g.a1.p1": "Esigenze del comune", "g.a1.p2": "Vedere la demo dal vivo", "g.a1.p3": "Definire i prossimi passi", "g.a1.fuss": "Gratuito e senza impegno", "g.ablauf2.titel": "Configurazione", "g.a2.name": "Comune di esempio", "g.a2.themen": "Temi", "g.a2.t1": "Mobilità", "g.a2.t2": "Abitare", "g.a2.t3": "Spazi pubblici", "g.a2.inhalte": "Contenuti", "g.a2.fuss": "Logo, temi e contenuti del vostro comune", "g.ablauf3.titel": "Pagina iniziale della piattaforma", "g.a3.p1": "Riqualificazione della piazza", "g.a3.p2": "Bilancio partecipativo", "g.a3.offen": "Aperto", "g.a3.bald": "Prossimamente", "g.a3.fuss": "Piattaforma attivata", "g.ablauf4.titel": "Esercizio", "g.a4.s1": "Svizzera", "g.a4.s2": "continui", "g.a4.s3": "personale", "g.a4.fuss": "Voi vi occupate dei contenuti.", "g.plan.platz": "Piazza", "g.plan.schule": "Scuola", "g.plan.strasse": "Via del paese"});
Object.assign(I18N.en, {"g.demo.titel": "Take part in Sample Town", "g.beispiel": "Example", "g.beispielansicht": "Sample view", "g.demo.prozess": "Participatory process", "g.demo.frage": "How should the village square be redesigned?", "g.demo.ph1": "Collect ideas", "g.demo.ph2": "Vote", "g.demo.ph3": "Implementation", "g.demo.v0": "More benches by the fountain", "g.demo.o0": "Village square", "g.demo.v1": "Bike racks at the school", "g.demo.o1": "School", "g.demo.v2": "Shelter at the bus stop", "g.demo.o2": "Bus stop", "g.demo.unterstuetzen": "Support", "g.demo.hinweis": "Example with made-up content. Click a pin or support a proposal. Nothing is saved.", "g.ablauf1.titel": "Meeting notes", "g.a1.kopf": "First meeting", "g.a1.p1": "The municipality's needs", "g.a1.p2": "See the demo live", "g.a1.p3": "Agree on next steps", "g.a1.fuss": "Free and non-binding", "g.ablauf2.titel": "Setup", "g.a2.name": "Sample Town", "g.a2.themen": "Topics", "g.a2.t1": "Mobility", "g.a2.t2": "Housing", "g.a2.t3": "Public space", "g.a2.inhalte": "Content", "g.a2.fuss": "Your municipality's logo, topics and content", "g.ablauf3.titel": "Platform home page", "g.a3.p1": "Redesign of the village square", "g.a3.p2": "Participatory budget", "g.a3.offen": "Open", "g.a3.bald": "Coming soon", "g.a3.fuss": "Platform is live", "g.ablauf4.titel": "Operations", "g.a4.s1": "Switzerland", "g.a4.s2": "ongoing", "g.a4.s3": "personal", "g.a4.fuss": "You take care of the content.", "g.plan.platz": "Square", "g.plan.schule": "School", "g.plan.strasse": "Village street"});

function applyLang(lang){
  document.documentElement.lang = lang;
  document.querySelectorAll('.lang-btn').forEach(b=>b.classList.toggle('active', b.dataset.lang===lang));
  if(lang==='de'){
    document.querySelectorAll('[data-i18n-original]').forEach(el=>{
      if(el.hasAttribute('data-i18n')) el.textContent = el.getAttribute('data-i18n-original');
      if(el.hasAttribute('data-i18n-html')) el.innerHTML = el.getAttribute('data-i18n-original');
    });
    document.querySelectorAll('[data-i18n-ph-original]').forEach(el=>{ el.placeholder = el.getAttribute('data-i18n-ph-original'); });
    localStorage.setItem('meyssens_lang','de');
    updateCookieBannerLang('de');
    return;
  }
  const dict = I18N[lang];
  if(!dict) return;
  document.querySelectorAll('[data-i18n]').forEach(el=>{
    const key = el.getAttribute('data-i18n');
    if(!el.hasAttribute('data-i18n-original')) el.setAttribute('data-i18n-original', el.textContent);
    if(dict[key]) el.textContent = dict[key];
  });
  document.querySelectorAll('[data-i18n-html]').forEach(el=>{
    const key = el.getAttribute('data-i18n-html');
    if(!el.hasAttribute('data-i18n-original')) el.setAttribute('data-i18n-original', el.innerHTML);
    if(dict[key]) el.innerHTML = dict[key];
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>{
    const key = el.getAttribute('data-i18n-placeholder');
    if(!el.hasAttribute('data-i18n-ph-original')) el.setAttribute('data-i18n-ph-original', el.placeholder);
    if(dict[key]) el.placeholder = dict[key];
  });
  localStorage.setItem('meyssens_lang', lang);
  updateCookieBannerLang(lang);
}

// Knöpfe und gespeicherte Sprache verbindet das kleine Ladeskript in gemeinden/index.html
