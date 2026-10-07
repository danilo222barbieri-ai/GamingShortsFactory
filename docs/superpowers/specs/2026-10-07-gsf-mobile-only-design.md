# GSF Mobile-Only Design

## Goal
Gaming Shorts Factory diventa un prodotto pubblico **mobile-only**. La UI desktop viene congelata e non viene più sviluppata, esposta o raggiungibile dai normali flussi utente. Il backend, l'AI, il rendering, i progetti, i social e la persistenza restano invariati.

## Product decision
- Smartphone: esperienza GSF completa.
- Desktop/laptop: nessuna UI GSF interattiva; viene mostrata solo una schermata pulita che indica che GSF è disponibile da smartphone.
- Tablet/touch device: trattato come mobile quando il dispositivo ha caratteristiche touch/coarse pointer compatibili con l'esperienza mobile.
- Nessun link, pulsante o route pubblica deve offrire una "versione desktop".
- Le route storiche `/desktop-preview` e `/desktop-home` non devono più mostrare una UI alternativa: devono tornare alla root/mobile gate o essere rimosse.

## Mobile as the only visual source
La UI mobile attuale diventa l'unica UI da mantenere. Tutte le correzioni future di Home, Game Bar, Creator Hub, AI, Game Editor, Share/Download e footer vengono fatte esclusivamente sulla mobile.

Non si crea una seconda composizione per desktop, non si mantiene una variante responsive dedicata e non si scala una UI desk parallela.

## Desktop gate
L'app principale deve decidere all'avvio se il dispositivo è compatibile con la UX mobile.

### Mobile allowed
Consentire l'app quando il browser presenta caratteristiche mobile/touch coerenti, includendo iPhone, Android e iPad/touch tablet.

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
- Nessun link interno deve contenere nomi/flag come `desktop`, `desk`, `desktop-preview`, `desktop-home` per offrire una visualizzazione diversa.
- Le route/componenti interne mobile possono restare tecnicamente esistenti per il funzionamento dell'app, ma non devono essere presentate come esperienze desktop pubbliche.

## Scope
### In scope
- Gate mobile/desktop nell'app pubblica.
- Rimozione dei link e delle route desktop pubbliche.
- Consolidamento della mobile come unica esperienza supportata.
- Rifinitura della mobile in fasi successive prima della pubblicazione finale.

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
- Non introdurre startup patcher visuali storici per simulare il mobile-only.
- Non riutilizzare il branch V308 come base: questa direzione parte da `main` pulito.

## Acceptance criteria
1. Da smartphone si apre GSF normalmente con la UI mobile esistente.
2. Da desktop/laptop non compare alcuna UI GSF operativa: solo il mobile gate.
3. `/desktop-preview` e `/desktop-home` non espongono più una UI desktop.
4. Non esistono link visibili verso una visualizzazione desktop.
5. Home, AI, Editor, Creator Hub e Share continuano a funzionare su mobile senza regressioni funzionali.
6. Backend, render e worker restano invariati.
7. Build e test passano prima di qualsiasi deploy in produzione.
8. Railway deve risultare `SUCCESS` prima di considerare pubblicata la versione mobile-only.

## Rollout
Fase 1: mobile-only foundation (gate + rimozione desk pubblica).

Fase 2: rifinitura mobile delle singole pagine, una alla volta, con test e verifica visiva.

Fase 3: pubblicazione finale della mobile come unica esperienza GSF supportata.
