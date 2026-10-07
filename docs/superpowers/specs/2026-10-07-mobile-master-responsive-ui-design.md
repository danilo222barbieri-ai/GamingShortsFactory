# GSF Mobile Master Responsive UI — Design

## Obiettivo

Gaming Shorts Factory deve avere una sola interfaccia visiva autorevole. La UI mobile approvata diventa la sorgente unica di struttura, stile e ordine dei componenti. Desktop, tablet e mobile mostrano la stessa interfaccia, con dimensioni e spaziature adattate al viewport senza introdurre una seconda composizione desktop.

Il risultato atteso è semplice: aprendo la stessa pagina su iPhone, iPad o Windows/Mac si deve riconoscere immediatamente la stessa UI. Sul desktop gli elementi diventano più grandi e meglio distribuiti, ma non cambiano ordine, forma, gerarchia o comportamento.

## Principio architetturale

Ogni superficie GSF deve avere:

- un solo DOM;
- un solo set di componenti;
- un solo CSS master;
- una sola logica JavaScript per gli stessi controlli;
- scaling fluido per viewport diversi;
- nessun ramo visuale separato desktop/mobile.

Sono vietate nuove varianti del tipo `desktop`, `desk`, `mobile-copy`, `desktop-layout` o blocchi che ricreano la stessa pagina con markup differente.

Le differenze tra viewport devono essere ottenute esclusivamente tramite proprietà responsive della stessa struttura: `clamp()`, `min()`, `max()`, percentuali, `vw`, `vh`, grid/flex fluidi e, solo quando indispensabile, breakpoint che cambiano misure o allineamenti ma non struttura né contenuto.

## Superfici incluse

La regola vale per tutte le superfici principali:

1. Home
2. Crea con IA
3. Game Editor
4. Creator Hub e relative sezioni
5. Condivisione / download finale
6. Game Bar globale
7. Footer globale

Non si modifica la pipeline video, l'AI backend, il worker, il render FFmpeg, le API progetto/bozza, le route o la persistenza.

## Home

La Home mobile approvata è il riferimento visivo master.

Devono restare identici tra mobile e desktop:

- ordine degli elementi;
- palette pastello/metallica;
- Game Bar;
- uploader circolare con anelli e animazioni;
- testi e murales;
- tre CTA `Crea con IA`, `Game Editor`, `Crea Short`;
- icone;
- footer;
- logica upload e stati `empty / uploading / uploaded`.

Su desktop cambia solo la scala:

- il contenitore usa più spazio orizzontale senza diventare una composizione differente;
- il cerchio cresce in modo fluido;
- i murales si allontanano proporzionalmente dal cerchio senza cambiare posizione concettuale;
- le tre CTA mantengono ordine e forma ma crescono in modo proporzionato;
- font e icone crescono tramite valori fluidi;
- Game Bar e footer mantengono struttura e stile;
- la pagina resta senza scroll quando il contenuto rientra nel viewport previsto.

Non deve esistere un “desktop design” alternativo.

## Crea con IA

La stessa superficie usata su mobile viene renderizzata anche su desktop. Su viewport più larghi possono aumentare larghezza utile, dimensione delle card motore, gap, preview e font. Non cambiano ordine dei motori, CTA, percorso utente, stato selezionato o logica backend.

## Game Editor

L'Editor mantiene un solo layout logico e un solo set di controlli. Desktop non deve ricostruire un editor diverso: usa la stessa UI mobile e sfrutta lo spazio aggiuntivo soltanto per ingrandire player, timeline, controlli e distanze. FRAME, CAPTION, LOOK, AUDIO, AI, timeline, safe zone e controlli restano gli stessi.

## Creator Hub

Creator Hub usa gli stessi componenti e le stesse cartelle su tutti i viewport. Profilo, Progetti, Social, Live e Abbonamento non devono avere una seconda struttura desktop. Su monitor larghi aumentano solo dimensioni, colonne disponibili e spaziatura mantenendo gerarchia e azioni identiche.

La Game Bar resta sempre visibile e funzionale.

## Share / Download

La superficie finale mantiene un'unica struttura su mobile e desktop. Social, download, stato finale e CTA non devono essere duplicati per viewport.

## Pulizia del codice visuale

La migrazione deve eliminare la stratificazione visuale storica che può ancora prevalere sulla UI master.

Devono essere rimossi o resi definitivamente non autorevoli:

- vecchi blocchi marcati `DESKTOP` / `DESK`;
- layout visuali V267, V268, V294, V296, V297, V298, V301, V305 e analoghi override storici;
- runtime JavaScript creati esclusivamente per layout desktop separati;
- attributi HTML usati solo per selezionare layout desk;
- media query che ricostruiscono una seconda composizione;
- CSS duplicato che cambia ordine, struttura o componenti tra mobile e desktop.

La pulizia non deve rimuovere logica funzionale, route, upload, AI, Editor, Hub, Share o backend.

## Cache e versioning

La migrazione include una pulizia completa del sistema di cache visuale.

Obiettivi:

- eliminare vecchi cache-key sparsi tra Home, Editor, Hub, AI e Share;
- eliminare query versionate incoerenti come `?v=285`, `?v=287`, `?v=300`, `?v=305`, `?v=306`, `?v=307` quando non sono più necessarie;
- usare un'unica versione finale coerente per tutte le superfici dopo la migrazione;
- aggiornare i key dei componenti Streamlit/custom component con la nuova versione finale;
- impedire che patch di startup più vecchie riscrivano nuovamente cache-key o layout;
- verificare che il browser riceva riferimenti nuovi dopo il deploy e non riutilizzi asset HTML obsoleti;
- mantenere la cache solo dove serve alle prestazioni, senza permetterle di nascondere una nuova UI.

La pulizia riguarda la cache applicativa e i riferimenti versionati del progetto. La cache locale privata del browser dell'utente non viene cancellata remotamente; il deploy deve però cambiare gli identificatori degli asset in modo che il browser richieda la versione nuova senza richiedere interventi manuali.

## Startup e ordine delle patch

Lo startup non deve continuare a ricostruire la UI attraverso decine di patch storiche in conflitto.

La nuova struttura deve avere un punto finale autorevole che:

1. parte dai componenti correnti;
2. applica solo migrazioni ancora necessarie;
3. applica la UI mobile-master responsive;
4. applica il versioning finale della cache;
5. esegue i test finali;
6. avvia Streamlit/Nginx solo se la struttura risultante è valida.

I test intermedi obsoleti che pretendono l'esistenza di una seconda UI desktop non devono più bloccare il deploy.

## Sicurezza della migrazione

La migrazione non può rompere:

- upload;
- materializzazione video;
- scelta 15s / 30s;
- motori AI;
- selezione momenti;
- apertura Editor;
- creazione short finale;
- salvataggio e ripresa bozze/progetti;
- navigazione Game Bar;
- collegamenti Social;
- download finale.

Ogni file Python modificato deve essere compilato durante i test prima del deploy. Ogni componente HTML/JS deve mantenere i marker funzionali richiesti dai test.

## Criteri di accettazione

La migrazione è completata solo quando:

- mobile conserva la UI approvata;
- desktop mostra la stessa UI chiaramente riconoscibile e proporzionata;
- non esiste un secondo markup/layout desktop;
- non esistono vecchi override visuali autorevoli che possano riapparire allo startup;
- Home, AI, Editor, Hub e Share usano una versione cache finale coerente;
- il sito funziona senza richiedere all'utente di svuotare manualmente la cache del browser;
- tutti i test funzionali principali passano;
- Railway raggiunge `SUCCESS`;
- una verifica visiva finale conferma che desktop e mobile differiscono solo per scala e distribuzione dello spazio, non per identità dell'interfaccia.
