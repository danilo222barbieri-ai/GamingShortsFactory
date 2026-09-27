GAMING SHORTS FACTORY — V77 WEB READY

COSA E' STATO FATTO
- V76 salvata come CORE_STABLE e lasciata intatta.
- Sessione anonima separata per ogni visitatore.
- Upload, AI, editor, file temporanei, export e token social isolati per sessione.
- Pulizia automatica delle sessioni inattive (default 2 ore).
- FFmpeg/ffprobe cercati in modo multipiattaforma; nel Docker sono installati lato server.
- Player video compatibili con hosting web tramite /media e reverse proxy Nginx.
- Nessun Python/FFmpeg richiesto sul computer dell'utente finale.
- Pubblicazione desktop/PowerShell non usata nel flusso web: YouTube e TikTok usano API/OAuth ufficiali quando configurati; Instagram usa Graph API quando configurato.
- Credenziali applicazione tenute fuori dal codice tramite variabili ambiente/secrets.

AVVIO LOCALE
Windows:
  AVVIA_GAMING_SHORTS_FACTORY_V77_WEB_READY.bat
Linux/macOS:
  ./AVVIA_GAMING_SHORTS_FACTORY_V77_WEB_READY.sh

AVVIO WEB CON DOCKER
1. Costruisci:
   docker build -t gaming-shorts-factory-v77 .
2. Avvia:
   docker run --rm -p 8080:8080 --env-file .env gaming-shorts-factory-v77
3. Apri:
   http://localhost:8080

PER UN DOMINIO PUBBLICO
- Imposta GSF_PUBLIC_APP_URL=https://tuo-dominio.example/
- Il provider deve fornire HTTPS.
- Registra esattamente lo stesso redirect URL nelle console OAuth di YouTube/TikTok.
- Non inserire segreti nel file Python o nel repository.

NOTA SOCIAL
Il sito funziona anche senza configurare i social: creazione, editor, render e download restano disponibili.
Per YouTube/TikTok ogni visitatore collega temporaneamente il proprio account alla sessione anonima; i token vengono eliminati insieme alla sessione.
Instagram e' predisposto per Graph API con configurazione server. Il login Meta multiutente puo essere aggiunto come step successivo senza cambiare editor/render.
