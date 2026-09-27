GAMING SHORTS FACTORY V77 — DEPLOY BETA SU RAILWAY
===================================================

OBIETTIVO
- Pubblicare la V77 su un URL HTTPS accessibile da PC e telefono.
- Nessun account utente: ogni visitatore usa una sessione anonima separata.
- I file di lavoro vengono eliminati automaticamente dopo 2 ore di inattività.

PREREQUISITI
1) Account Railway: https://railway.com/
2) Railway CLI installata su Windows.
   Metodo consigliato se hai Node.js 16+:
      npm i -g @railway/cli
   In alternativa usa Scoop:
      scoop install railway

DEPLOY DA POWERSHELL
1) Estrai questa cartella, poi apri PowerShell dentro la cartella.
2) Login:
      railway login
3) Crea un nuovo progetto:
      railway init
   Nome suggerito: gaming-shorts-factory
4) Pubblica:
      railway up
5) Apri la dashboard:
      railway open

NELLA DASHBOARD RAILWAY
1) Service > Settings > Networking > Public Networking > Generate Domain.
2) Copia l'URL HTTPS generato, per esempio:
      https://gaming-shorts-factory-production.up.railway.app
3) Service > Variables: aggiungi
      GSF_WEB_MODE=1
      GSF_SESSION_TTL_SECONDS=7200
      GSF_RUNTIME_ROOT=/data/gsf-runtime
      GSF_PUBLIC_APP_URL=https://IL-TUO-DOMINIO.up.railway.app/
4) Per mantenere una sessione durante restart/redeploy:
   Service > Volumes > Add Volume
   Mount Path:
      /data
5) Dopo le variabili/volume, esegui Redeploy.

TEST BETA
- Apri l'URL dal PC e carica un video corto/medio.
- Apri lo stesso URL dal telefono su rete mobile.
- Verifica: upload, motori, editor, render finale, download.
- Apri anche una finestra anonima/secondo browser: le due sessioni non devono vedere i file l'una dell'altra.

SOCIAL
- YouTube e TikTok richiedono le credenziali OAuth e un URL HTTPS pubblico definitivo.
- Prima del collegamento social, verifica il flusso video completo sul dominio Railway.
- Instagram richiede configurazione Meta/Graph API.

IMPORTANTE SUI VIDEO MOLTO GRANDI
Railway richiede che il corpo di una richiesta HTTP termini l'upload entro 5 minuti.
Per la prima beta usa file che si caricano comodamente entro questo limite.
Per la release pubblica, il passo successivo consigliato è upload diretto su object storage/bucket,
così i gameplay grandi non passano attraverso la richiesta Streamlit principale.

NOTE
- Il Dockerfile è già pronto e Railway lo rileva automaticamente.
- Nginx espone Streamlit e /media sulla stessa porta pubblica.
- FFmpeg viene installato dentro il container.
- La V76 CORE_STABLE è inclusa solo come backup e non viene avviata.
