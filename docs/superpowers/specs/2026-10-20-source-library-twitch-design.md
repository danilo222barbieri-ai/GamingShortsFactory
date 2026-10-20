# GSF — Libreria Sorgenti e Twitch

Data: 2026-10-20. Stato: proposta concreta per revisione, runtime non implementato.
Base: main con OAuth PR185, sorgente593a53e. Deploy di quella versione ancora bloccato dalla sospensione Railway; non è prova di OAuth operativo.

## Intento e confini

Il creator deve ritrovare sorgenti reali nel Creator Hub, scegliere una propria clip Twitch e continuare attraverso la pipeline GSF esistente fino a IA, momenti ed Editor. Una sorgente importata deve essere riutilizzabile dopo refresh senza scaricarla nuovamente da Twitch. Upload e Twitch sono attivi; YouTube è predisposto nel modello senza modificare l'OAuth o la pubblicazione YouTube.

Si conserva l'attuale gaming/glass, la Game Bar globale e la navigazione shell. Non si riscrivono Editor, IA, rendering o pubblicazione. Railway resta fermo come richiesto dall'utente. Nessuna registrazione Live, acquisizione HLS, scraping o download VOD non ufficiale.

## Evidenza nel repository

- `web/direct_upload_server.py`: `_twitch_access`, `_twitch_api`, `_twitch_content`, `_twitch_clip_source`, `_twitch_import_start/run` già presenti. OAuth server-side, refresh/validate/revoke e scope `channel:manage:clips` già implementati.
- L'importazione usa `_persist_fallback_source_to_bucket`, `_materialize_bucket_object` e `.direct_upload_ready.json`, con validazione FFprobe e fence contro una nuova sorgente selezionata nel frattempo.
- Il bucket conserva `uploads/<sid>/<upload_id>/...`. Account, sessioni e dati social hanno già infrastruttura di ownership/storage; non viene aggiunto un secondo sistema identità.
- Il Creator Hub ha una vista `live` ancora vuota e un piccolo sheet clip/VOD. Mancano catalogo persistente, deduplica, stato Live, thumbnail e riapertura degli asset importati.
- L'importazione Twitch attuale è limitata a512MiB e120secondi di download, con timeout socket15secondi. Questi limiti non vengono aumentati implicitamente.

## Possibilità ufficiali Twitch

Riferimento: https://dev.twitch.tv/docs/api/reference/

- Get Streams, `GET /helix/streams?user_id=<creator>`: rileva la diretta corrente, titolo, categoria, thumbnail e inizio. Nessuno scope aggiuntivo con user token già disponibile. Non restituisce un flusso media da registrare.
- Get Videos, `GET /helix/videos?user_id=<creator>`: elenca archivio/VOD e highlights pubblicati accessibili. Espone metadati e link Twitch, non download media. Il risultato senza video è uno stato vuoto valido.
- Get Clips e Get Clips Download, `GET /helix/clips/downloads`: download ufficiale delle proprie clip mediante `channel:manage:clips`; `editor_id` coincide col broadcaster autenticato. URL temporanei, mai usati come archivio permanente.
- Get Games risolve gli ID categoria delle clip in nomi con richieste batch; un errore di arricchimento non blocca l'elenco o l'importazione.

Non si mostrano CTA Importa su Live/VOD privi di capacità media ufficiale. Si mostrano stato e limite, con link ufficiale Twitch e collegamento al normale upload GSF per chi possiede già un file autorizzato. La durata Live resta «Iniziata…», non una durata finale inventata. Per VOD senza categoria disponibile non viene attribuita la categoria della diretta attuale.

## Approccio selezionato e alternative

Si aggiunge un catalogo sottile sopra gli asset esistenti, con adattatore Twitch e riuso dei marker/materializzatori attuali. È l'approccio raccomandato: soddisfa persistenza e riuso senza spostare le responsabilità della pipeline.

Una libreria soltanto nel browser non soddisfa refresh, isolamento e deduplica duratura. Un nuovo ingest service/recorder richiederebbe infrastruttura e nuove possibilità media assenti dalle API; non è incluso.

## Modello comune

Tipi: `local_upload`, `twitch_clip`, `twitch_vod`, `twitch_live`, `youtube_vod`, `youtube_live`.

Campi server-side:

- ID opaco stabile; schema1; owner derivato esclusivamente dalla sessione/account verificato.
- Provider, tipo, account esterno proprietario, ID esterno; upload locali identificati dall'upload_id.
- Titolo, thumbnail HTTPS verificata, categoria quando disponibile, data, durata normalizzata, URL pubblico Twitch consentito.
- Capacità esplicite: `can_import`, `can_analyze`, `can_open_editor`; motivo leggibile quando un'azione è indisponibile.
- Stato `discovered`, `importing`, `ready`, `failed`, `unavailable`; upload_id, dimensioni, riferimento bucket e provenienza validata per asset acquisiti.

La risposta pubblica non include token, secret, URL di download firmati, path locali o chiavi bucket. Live/VOD non acquisibili restano metadati; non diventano `ready`.

Identità deduplica: owner GSF + provider + account provider + ID esterno. Gli upload hanno owner + upload_id. Il solo clip_id o SID browser non autorizza la lettura di asset di altri account.

## Persistenza e ownership

Record separati nel bucket esistente sotto un namespace `source-library/<owner>/<source_id>.json`; niente scansioni dell'intero bucket a ogni apertura. Cache locale secondaria, pubblicata soltanto dopo commit durevole. Indice piccolo/paginato per elenco utente; scritture serializzate con le convenzioni esistenti, aggiornamenti che non cancellano record concorrenti.

Il catalogo viene popolato al completamento di upload/importazione. Il primo accesso può registrare sorgenti legacy soltanto se provenienza e owner sono verificabili da record già autorizzati: non si assegna un file a un nuovo account perché usa lo stesso browser/SID. Una sessione guest e un account autenticato rimangono distinti; nessuna migrazione implicita di dati di un account precedentemente connesso. Un errore storage/identità fallisce chiuso e non degrada l'account a guest per leggere o salvare sorgenti.

Il riferimento del bucket resta privato. Un'API riceve source_id, non un percorso scelto dal client. Riattivare da un'altra sessione dello stesso account richiede la verifica della provenienza persistente prima di invocare il materializzatore; non si allargano i controlli dei normali endpoint upload a chiavi arbitrarie.

## Deduplica e recupero

Prima di richiedere un nuovo URL/download Twitch si cerca un record acquisito dello stesso owner/account provider/contenuto e si verifica l'esistenza dell'asset nel bucket. Se l'asset locale corretto esiste, si riusa. Se esiste solo nel bucket, si materializza tramite il percorso GSF esistente senza riscaricare da Twitch. Se entrambi mancano, il record diventa non disponibile e l'utente può richiedere una nuova importazione autorizzata.

Importazioni contemporanee della stessa sorgente si uniscono allo stesso job; l'identificatore resta persistente. Un record `importing` rimasto dopo riavvio non genera attese infinite: si riconciliano oggetto e marker oppure si espone errore riprovabile. Non si promette un trasferimento distribuito exactly-once oltre le garanzie reali dello storage.

Refresh e ritorno alla pagina rileggono lo stato del job. La chiusura della vista ferma i poll del browser, non elimina la sorgente o il progetto. Non si salva mai un URL temporaneo come unica prova di importazione.

## API e pipeline

- GET `/creator-hub/sources`: elenco paginato autorizzato, filtri provider/cartella; Upload e Importati leggono dati locali persistenti, Twitch discovery legge le API ufficiali.
- POST `/creator-hub/sources/activate`: source_id e destinazione `ai`/`editor`, CSRF obbligatorio. Risolve l'asset dal catalogo, applica ownership e fence, riusa il materializzatore/marker esistente. Restituisce stato/job o disponibilità, mai «analisi completata» prima del servizio reale.
- L'endpoint `/social-connect/twitch/import` esistente viene esteso in modo compatibile per deduplica e riferimento catalogo. I client precedenti continuano a ricevere upload_id/preparing e usare lo status attuale.
- Si estende la whitelist dell'adattatore Twitch a `streams` e `games`; OAuth, callback, token storage e pubblicazione YouTube non cambiano.

`Analizza con IA` importa/attiva e passa alla Crea con IA esistente. L'utente riceve i momenti realmente validi: fino a3, anche1 o2, preservando la correzione pre-beta che evita la schermata bloccata quando non ne esistono3.

`Apri nell'Editor` è disponibile per un asset acquisito e coerente; usa il bootstrap attuale. Per una bozza già associata si riapre la bozza esistente. Nessuna ricostruzione degli overlay o reset degli edit per un semplice refresh della libreria. Cambiare sorgente è un'azione esplicita; usa il salvataggio bozza esistente quando necessario. Se il salvataggio/materializzazione fallisce, la sorgente corrente resta intatta. Un import completato dopo una nuova navigazione non forza il cambio pagina.

## Creator Hub

La voce Live e VOD viene trasformata in `Sorgenti`, conservando il target shell `hub` e l'alias legacy `live` per deep link già esistenti. Cartelle Upload, Twitch e YouTube. Dentro Twitch: Live, VOD/Highlights, Clip, Importati.

Upload mostra file realmente acquisiti e disponibili, non tutte le bozze duplicate. Importati mostra gli asset Twitch persistenti. Live mostra una card reale o «Canale offline». VOD e highlights hanno card e link ufficiali, con il limite media chiaro. Clip hanno thumbnail, titolo, categoria quando disponibile, data, durata e CTA; gli asset riutilizzabili mostrano `Importata`.

YouTube mostra lo stato collegamento già esistente e il limite «Importazione sorgenti non ancora disponibile». Nessun elenco video simulato o nuovo scope; i tipi modello predisposti non costituiscono una funzionalità di importazione YouTube.

Si riusano card, header, sheet, back e fitHub del componente attuale. Nessun nuovo iframe o sistema di navigazione. Back/refresh ripristinano provider/cartella/cursore con dati ricaricati dal server; filtri locali non equivalgono a permessi. I fetch sono cancellabili e protetti da epoch per evitare risposte stale su altra cartella/account. Game Bar e safe area restano libere da overlay; i menu rispettano la riserva già presente.

## Errori e limiti

Twitch scollegato: CTA collegamento e accesso agli asset GSF già autorizzati, senza fingere un elenco remoto. Token scaduto: refresh esistente; revocato: riconnetti, progetto conservato. API indisponibile: stato riprovabile, nessun elenco vuoto spacciato per successo. Contenuto eliminato: non disponibile; un asset GSF già acquisito non viene riscaricato inutilmente.

VOD molto lunghi restano metadati e non avviano download/analisi. Clip oltre i limiti reali restituiscono errore chiaro e lasciano il progetto precedente. Nessun download cresce senza limiti. Nessun URL provider non verificato viene usato per redirect/import.

## File previsti per l'implementazione

- Nuovo helper `web/gsf_sources_v422.py`: normalizzazione, ID opachi, capacità, metadati e regole deduplica senza nuova autenticazione.
- `web/direct_upload_server.py`: adattatore/storage catalogo, hook di completamento, API autorizzate e riuso attivazione/import.
- `web/creator_hub_v156_component/index.html`: vista Sorgenti e card, riuso navigazione/sheet.
- Nuovi test `tests/test_source_library_v422.py`; aggiornamento dei test OAuth/Hub pertinenti e delle chiamate bloccanti nel Production Gate. Eventuale aggiornamento mirato del contratto Hub che oggi impone il placeholder vuoto.
- `.env.example` soltanto se serve chiarire configurazione; nessun nuovo secret o servizio previsto.
- Nessuna modifica ai file runtime Editor, Home/IA/render o al protocollo OAuth YouTube. Se un requisito richiede una modifica fuori da questi confini, si documenta prima di allargare la claim.

## Verifica richiesta prima di dichiarare operativo

1. Test reali dei metodi con trasporti provider/storage controllati: account vuoto, offline/live, categorie mancanti, cursor, errore API, refresh/revoca, ownership diversa e SID riutilizzato.
2. Due richieste sulla stessa clip producono un solo download; riapertura da bucket non chiama clips/downloads; oggetto cancellato diventa indisponibile. Riavvio/job incompleto, fallimento persistenza e cambio sorgente durante import non perdono il progetto.
3. Upload reale registrato una sola volta; guest/login e altro account non ereditano dati senza provenienza. CSRF, ID arbitrari, HTML/URL provider non validi e token assenti dalle risposte/log.
4. Chromium e WebKit mobile: cartelle/card/thumb, Game Bar, safe area, Back/deep link/refresh, polling cancellato e zero errori runtime. Desktop conserva il comportamento di accesso oggi approvato.
5. Percorso immagine reale: upload/import controllato → materializzazione esistente → IA →1–3 momenti → Editor → render, senza mockare il comportamento dei componenti GSF. Le risposte Twitch simulate non provano il consenso OAuth reale.
6. Suite attuale e Production Gate senza bypass. Quando Railway torna disponibile: deploy autorizzato, SUCCESS, health e verifica byte/release. Con credenziali e consenso reali: account Twitch → contenuti propri → clip importata → IA → momenti → Editor. Soltanto questo consente di chiamare Twitch operativo.

Variabili: riuso `GSF_TWITCH_CLIENT_ID`, `GSF_TWITCH_CLIENT_SECRET`, `GSF_PUBLIC_APP_URL`, cifratura e bucket già previsti. Nessuna nuova variabile obbligatoria. Mancano ancora le credenziali Twitch e il deploy OAuth verificato; non si dichiarano risolti con test simulati.
