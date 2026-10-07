# GSF Mobile-Only Design

## Goal
Gaming Shorts Factory diventa un prodotto pubblico **mobile-only**. La UI desktop viene congelata e non viene più sviluppata, esposta o raggiungibile dai normali flussi utente. Il backend, l'AI, il rendering, i progetti, i social e la persistenza restano invariati.

## Product decision
- Smartphone: esperienza GSF completa.
- Desktop/laptop: nessuna UI GSF interattiva; viene mostrata solo una schermata pulita che indica che GSF è disponibile da smartphone.
- Tablet mobile/touch compatibile: consentito quando il browser si identifica come dispositivo mobile/tablet.
- Nessun link, pulsante o route pubblica deve offrire una "versione desktop".
- Le route storiche `/desktop-preview` e `/desktop-home` non devono più mostrare una UI alternativa: devono tornare alla root/mobile gate o essere rimosse.

## Mobile as the only visual source
La UI mobile attuale diventa l'unica UI da mantenere. Tutte le correzioni future di Home, Game Bar, Creator Hub, AI, Game Editor, Share/Download e footer vengono fatte esclusivamente sulla mobile.

Non si crea una seconda composizione per desktop, non si mantiene una variante responsive dedicata e non si scala una UI desk parallela.

## Desktop gate
L'accesso pubblico deve distinguere browser mobile/tablet da desktop prima di offrire la UI operativa.

### Mobile allowed
Consentire l'app a iPhone, Android, iPad e browser mobile/tablet compatibili.

### Desktop blocked
Su desktop/laptop mostrare una pagina statica minimale con:
- titolo GSF;
- messaggio "GSF è disponibile da smartphone";
- nessun accesso a Home, editor, AI, Creator Hub o Share;
- nessun bottone "visualizza versione desktop" o equivalente.

La prima release non richiede QR code o nuove dipendenze: YAGNI. Potrà essere aggiunto più avanti senza cambiare l'architettura.

## Routes and links
- Rimuovere ogni link pubblico verso `/desktop-preview` e `/desktop-home`.
- Le due route storiche devono redirigere alla root oppure cessare di servire una UI alternativa.
- Nessun link interno deve offrire una visualizzazione desk alternativa.
- Le route/componenti interne mobile possono restare tecnicamente esistenti per il funzionamento dell'app, ma non devono essere presentate come esperienze desktop pubbliche.

## Mobile fixes included in this release
### 1. Motore IA: rimuovere la line-up e ricomporre la pagina
La barra/percorso `1 Motore / 2 Momento / 3 Editor / 4 Crea Short / 5 Pronto` viene rimossa dalla pagina mobile Motore IA.

Lo spazio recuperato viene usato per rendere più leggibili titolo, scelta durata e quattro motori. La sezione con le **3 migliori giocate** resta sotto ai motori e deve essere raggiungibile con lo scroll interno della pagina, senza comprimere tutto in una singola schermata.

Non devono cambiare i quattro motori reali, la selezione del momento, l'apertura del Game Editor o la creazione diretta dello Short.

### 2. Scroll: Home fissa, pagine interne scrollabili
La Home resta una schermata fissa senza scrolling della pagina principale.

Le pagine interne che possono superare l'altezza dello schermo — Motore IA, Creator Hub, Game Editor e Share/Download quando necessario — devono avere scrolling **interno alla propria superficie**, senza trascinare la Home sottostante e senza creare doppio scroll del browser.

La Game Bar e i controlli globali non devono perdere lo stato durante lo scroll interno.

### Mini-player dei momenti
Nei mini-player delle 3 migliori giocate, il tap sul video apre la riproduzione fullscreen. Uscendo dal fullscreen o tornando indietro si ritorna alla stessa pagina Motore IA con selezione e stato conservati.

Su iPhone/iPad usare il fullscreen video nativo quando disponibile; sugli altri browser usare la Fullscreen API con fallback senza perdere il momento selezionato.

## Scope
### In scope
- Gate mobile/desktop nell'app pubblica.
- Rimozione dei link e delle route desktop pubbliche.
- Consolidamento della mobile come unica esperienza supportata.
- Rimozione line-up Motore IA e nuova impaginazione mobile.
- Home fissa e scrolling soltanto interno alle pagine secondarie.
- Fullscreen dei mini-player con ritorno allo stato precedente.

### Out of scope
- Nuova UI desktop.
- Porting desktop della mobile.
- Modifiche al pipeline video/FFmpeg.
- Modifiche al worker AI.
- Modifiche a upload, progetto/bozza, social API, autenticazione o persistenza salvo quanto strettamente necessario al gate.

## Safety / regression constraints
- Non modificare la pipeline render V100.4: libx264, preset medium, CRF 14, H.264 High, AAC, 60 fps, 1080x1920.
- Non cambiare il comportamento dei motori AI.
- Non cambiare i contratti di salvataggio progetti/bozze.
- Non cambiare i collegamenti funzionali della Game Bar mobile.
- Non introdurre nuovi startup patcher visuali storici per simulare il mobile-only.
- Non riutilizzare il branch V308 come base: questa direzione parte da `main` pulito.

## Acceptance criteria
1. Da smartphone si apre GSF normalmente con la UI mobile esistente.
2. Da desktop/laptop non compare alcuna UI GSF operativa: solo il mobile gate.
3. `/desktop-preview` e `/desktop-home` non espongono più una UI desktop.
4. Non esistono link visibili verso una visualizzazione desktop.
5. La pagina Motore IA non mostra più la line-up a 5 step.
6. Titolo, durata e 4 motori IA hanno più spazio; le 3 migliori giocate sono sotto e raggiungibili con scroll interno.
7. La Home non scorre; le pagine interne scorrono nella propria superficie senza doppio scroll.
8. Tap su un mini-player apre fullscreen e l'uscita riporta alla pagina con stato conservato.
9. Home, AI, Editor, Creator Hub e Share continuano a funzionare su mobile senza regressioni funzionali.
10. Backend, render e worker restano invariati.
11. Build e test passano prima di qualsiasi deploy in produzione.
12. Railway deve risultare `SUCCESS` prima di considerare pubblicata la versione mobile-only.

## Rollout
Fase 1: mobile-only foundation (gate + rimozione desk pubblica).

Fase 2: correzioni mobile incluse in questa release (Motore IA, scroll interno, mini-player fullscreen).

Fase 3: rifinitura mobile delle singole pagine, una alla volta, con test e verifica visiva.

Fase 4: pubblicazione finale della mobile come unica esperienza GSF supportata.
