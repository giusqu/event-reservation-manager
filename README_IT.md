# Event Reserervation Manager (ERM)

## 1. Specifica del progetto

ERM e' una API REST costruita con FastAPI per gestire:
- utenti
- eventi
- prenotazioni
- commenti

La piattaforma permette agli utenti di creare eventi, indicando il luogo, la descrizione e il numero massimo di partecipanti prenotabili. Inoltre, tutti gli utenti possono commentare i singoli eventi.

Stack principale:
- FastAPI
- PostgreSQL + SQLAlchemy async
- Alembic per migrazioni
- JWT per autenticazione
- Redis per caching
- Jinja2 per pagine HTML base
- WebSocket per realtime

Funzionalita' principali:
- CRUD utenti/eventi/prenotazioni/commenti
- login con token JWT e endpoint protetti (es. `/users/me`)
- upload immagine utente (solo JPEG) in `static/images/`
- pagine HTML:
  - `/events_page`
  - `/user_page/{user_id}`
  - `/users_page`
  - `/comments`
- realtime:
  - WebSocket `/ws`
  - broadcast `POST /send_message_to_all_websocket_users`
- cache Redis su `GET /long_operation` (TTL 20 secondi)

### Ordine consigliato di utilizzo

1. Prepara configurazione
   - crea `.env` (locale) o `deploy.env` (docker)
   - imposta variabili DB, Redis, JWT e `*_TEST`
2. Avvia infrastruttura
   - PostgreSQL
   - Redis (opzionale)
3. Inizializza schema database con Alembic
   ```powershell
   alembic upgrade head
   ```
4. Avvia API FastAPI
   ```powershell
   python run.py
   ```
   oppure
   ```powershell
   uvicorn src.main:app --reload
   ```
5. Popola dati base  
   Swagger UI http://localhost:8000/docs (locale) oppure http://localhost:9999/docs (docker)
   - crea utente (`POST /users/`)
   - login (`POST /users/login`)
   - crea eventi (`POST /events/`)
   - poi prenotazioni/commenti
6. Usa UI e realtime
   - Jinja2: `/events_page`, `/user_page/{id}`
   - WebSocket: `/ws` + broadcast `POST /send_message_to_all_websocket_users`
7. Esegui test
8. ```powershell
   python run_tests.py
   ```

## 2. Come eseguirlo (locale)

Prerequisiti:
- Python 3.13+
- PostgreSQL
- Redis (da scaricare da sorgente esterna)

Setup:
1. Crea e attiva virtual environment
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Installa dipendenze
   ```powershell
   pip install -r requirements.txt
   ```
3. Crea `.env` (vedi sezione dedicata)
4. Applica migrazioni
   ```powershell
   alembic upgrade head
   ```
5. Avvia app
   ```powershell
   python run.py
   ```
   oppure
   ```powershell
   uvicorn src.main:app --reload
   ```

URL utili:
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## 3. Esecuzione con Docker Compose

```powershell
docker compose up --build
```

Servizi previsti:
- `app` (porta host `9999` -> container `8000`)
- `db` (Postgres su porta interna `1221`)
- `redis` (porta interna `5370`)

## 4. File da creare/editare

File locali:
- `.env` (sviluppo locale, letto da `src/config.py`)
- `deploy.env` (usato da `docker-compose.yaml`)

Esempio in:
- `.env.example`
- `deploy.env.example`

## 5. Come usare Redis

Redis e' usato per cache API. Verifica rapida:
1. Avvia Redis.
2. Chiama due volte `GET /long_operation` in pochi secondi.
3. La seconda risposta arriva da cache.

## 6. Come usare WebSocket

La documentazione interattiva di FastAPI (/docs) non supporta WebSocket direttamente, usa quindi un tool esterno per avviare la connessione

Realtime gia' presente:
- WebSocket `GET /ws` ("ws://localhost:8000/ws")
- Broadcast `POST /send_message_to_all_websocket_users`

## 7. Come usare pytest

I test sono in `tests/` e usano DB di test tramite variabili `*_TEST`.

Prima dei test:
- crea DB test (es. `DB_NAME_TEST=test`)
- compila in `.env`:
  - `DB_HOST_TEST`
  - `DB_PORT_TEST`
  - `DB_NAME_TEST`
  - `DB_USER_TEST`
  - `DB_PASS_TEST`

Comandi:
```powershell
python run_tests.py
```
oppure
```powershell
pytest -v tests/ --asyncio-mode=auto --disable-warnings
```

## 8. Come visualizzare le pagine Jinja2

Le pagine Jinja2 si aprono da browser sugli endpoint HTML, non da Swagger.

In locale:
1. Avvia l'app:
   ```powershell
   python run.py
   ```
   oppure
   ```powershell
   uvicorn src.main:app --reload
   ```
2. Apri:
   - `http://localhost:8000/events_page`
   - `http://localhost:8000/user_page/1` (sostituisci `1` con un `user_id` esistente)
   - `http://localhost:8000/users_page`
   - `http://localhost:8000/comments_page`

   Con Docker cambia porta da 8000 a 9999

> **Nota:** Per vedere contenuti reali servono dati nel database (migrazioni applicate + almeno un utente/evento).

## 9. Altro utile

Migrazioni:
```powershell
alembic revision --autogenerate -m "nome_migrazione"
alembic upgrade head
```

JWT:
1. `POST /users/login` per ottenere `access_token`
2. usa header `Authorization: Bearer <token>` su endpoint protetti

Upload immagini:
- `POST /users/upload_image` accetta solo `image/jpeg`
