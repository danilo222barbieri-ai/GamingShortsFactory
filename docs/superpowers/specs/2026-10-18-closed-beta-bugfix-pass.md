Gaming Shorts Factory — CLOSED BETA BUGFIX PASS

NON aggiungere nuove feature e NON fare redesign.

Questi sono bug reali rilevati nell'app attualmente online. Correggili mantenendo grafica, struttura e comportamento attuali dove non esplicitamente indicato.

OBIETTIVO:
fare un pass di stabilizzazione UX/mobile prima della closed beta.

1. CREATOR HUB — SCROLL / CONTENUTO TAGLIATO

Il Creator Hub adesso scrolla correttamente, ma scorrendo verso il basso alcune finestre/sezioni non diventano completamente visibili.

Problema:
gli ultimi elementi sembrano finire dietro la Game Bar / safe area oppure il contenitore scrollabile termina troppo presto.

Correggere il layout in modo che:
- tutte le sezioni siano raggiungibili;
- ogni card/finestra possa essere vista completamente;
- l'ultimo elemento abbia spazio sufficiente sopra Game Bar + safe area;
- niente venga tagliato in fondo;
- mantenere lo scroll INTERNO del Creator Hub;
- NON rendere scrollabile la Home.

Testare almeno su:
- iPhone piccolo;
- iPhone standard;
- iPhone grande;
- Android Chrome.

2. CREATOR HUB — FOTO PROFILO

Attualmente non riesco a cambiare la foto profilo.

Verificare l'intero flusso:
tap sulla foto / modifica
→ selezione immagine
→ resize/compressione se necessaria
→ upload/salvataggio
→ aggiornamento immediato avatar
→ persistenza dopo refresh e riapertura app.

Se fallisce il backend, mostrare un errore comprensibile invece di non fare nulla.

3. CREATOR HUB — NOME PROFILO

Non riesco a modificare/salvare il nome.

Sistemare:
- apertura modifica;
- input;
- salvataggio;
- aggiornamento immediato UI;
- persistenza;
- gestione errore.

Non deve essere necessario refreshare manualmente.

4. IMPOSTAZIONI — RIMUOVERE “ACCEDI”

Nel Creator Hub > Impostazioni c'è una riga “Accedi” che in questa struttura è inutile.

Rimuoverla.

Non modificare il resto della gestione account/login/logout se funzionante.

5. NOTIFICHE — TOGGLE NON FUNZIONANTE

Il controllo notifiche appare attivo di default e non permette realmente di disattivarle.

Correggere la logica.

Requisiti:
- toggle realmente cliccabile;
- OFF deve disattivare le notifiche;
- ON deve riattivarle;
- lo stato deve essere persistente;
- dopo refresh deve mantenere la scelta;
- non deve tornare arbitrariamente ON;
- distinguere correttamente preferenza utente e permission del browser;
- se il browser ha negato il permesso, rappresentare correttamente quello stato.

NON iscrivere automaticamente l'utente alle push ignorando la preferenza salvata.

6. ALIVE — “CARICA UN GAMEPLAY” NEL CREATOR HUB

Nel Creator Hub l'effetto Alive / guide ring intorno a “Carica un gameplay” si sposta rispetto al pulsante quando faccio scroll.

Deve essere ancorato al target reale.

Quando la pagina scrolla:
- il ring deve seguire perfettamente l'elemento;
- niente offset progressivo;
- niente posizione calcolata solo all'apertura;
- tenere conto del contenitore scrollabile interno;
- tenere conto della Game Bar e dell'header;
- nessun effetto Alive deve fluttuare in posizione sbagliata.

Preferire l'ancoraggio geometrico al vero elemento DOM rispetto a coordinate hardcoded.

7. CREA CON IA — ANALISI TROPPO LENTA

L'analisi IA è attualmente molto lenta.

NON mascherare semplicemente il problema con un'animazione più veloce.

Profilare l'intero percorso:

upload pronto
→ richiesta analisi
→ eventuale estrazione audio/frame
→ Whisper / analisi eventi
→ motore AI
→ ranking dei momenti
→ risposta al frontend.

Misurare tempi reali di ogni fase.

Cercare:
- lavoro duplicato;
- rianalisi dello stesso video;
- attese sequenziali che possono essere parallele;
- polling troppo lento;
- file ricopiati/materializzati inutilmente;
- inizializzazione ripetuta dei modelli;
- chiamate AI ridondanti;
- elaborazioni fatte sul frontend invece che sul worker;
- cache non sfruttata.

Ottimizzare senza ridurre significativamente la qualità dei momenti scelti.

Voglio nel report finale:
tempo PRIMA / DOPO per un gameplay di test comparabile e breakdown delle fasi principali.

8. ALIVE — GLITCH QUANDO CAMBIO PAGINA

Quando cambio pagina compaiono piccoli glitch grafici delle notifiche/whisper/bubble Alive.

Analizzare in particolare navigazioni tipo:

Home → Creator Hub
Creator Hub → Home
Home → Crea con IA
Crea con IA → Editor
Editor → Crea Short
Game Bar tra pagine diverse.

Possibili sintomi:
- elementi Alive vecchi che restano visibili;
- flash per qualche frame;
- toast sovrapposti;
- guide ring del target precedente;
- bubble duplicata;
- whisper nella posizione sbagliata;
- animazione che riparte mentre la vecchia non è ancora smontata.

Alive deve avere un lifecycle pulito per route.

Quando cambia superficie:
- cancellare observer/listener/timer della pagina precedente;
- smontare gli elementi transitori non più validi;
- mantenere solo lo stato globale che deve realmente sopravvivere;
- evitare doppia inizializzazione;
- evitare duplicate subscription;
- niente flash del vecchio target durante il cambio pagina.

IMPORTANTE:
non risolvere Alive disabilitandolo o riducendolo drasticamente.
Va mantenuto, ma deve essere stabile.

VERIFICA FINALE

Prima di dichiarare completato il task verificare realmente:

- Creator Hub scrolla fino all'ultimo elemento.
- Nessuna card resta nascosta dalla Game Bar.
- Cambio foto profilo funzionante.
- Cambio nome funzionante.
- Riga “Accedi” rimossa.
- Toggle notifiche ON/OFF funzionante e persistente.
- Alive “Carica un gameplay” resta ancorato durante tutto lo scroll.
- Nessun glitch Alive evidente nei cambi pagina.
- Analisi IA misurata e ottimizzata.
- Nessun nuovo errore console/runtime.
- Navigazione esistente non regressa.
- Production Gate verde.
- Deploy Railway completato.
- Production UI Verify verde.

Non chiudere il task soltanto perché i test locali passano.

Alla fine dammi:
- bug trovati;
- causa di ciascun bug;
- fix effettuati;
- tempi IA prima/dopo;
- test eseguiti;
- PR/commit;
- stato Production Gate;
- commit effettivamente promosso su Railway;
- eventuali problemi ancora aperti.

Questa è una stabilizzazione CLOSED BETA: priorità assoluta a affidabilità, velocità e assenza di glitch. Nessuna nuova funzione.

Additional user instruction, 2026-10-19: the entire application must remain portrait when the phone rotates. Use the PWA portrait orientation contract and supported orientation lock without forcing fullscreen. On Safari tabs (OS lock unavailable), show a minimal portrait-required guard; retain project, route and render state underneath. Do not interpret the virtual keyboard as a device rotation.
