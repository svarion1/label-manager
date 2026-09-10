# Label Manager

Personal QR label + closet inventory system.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python wsgi.py
```

The app runs on `http://0.0.0.0:5050`.

## Configure for your phone

The QR codes need a URL the phone can actually reach.

**Find your LAN IP** (`ipconfig` on Windows, `ifconfig`/`ip addr` on Linux/macOS). Then:

```bash
export BASE_URL="http://192.168.1.42:5050"
python wsgi.py
```

Print a test label — the QR now encodes the URL your phone can open.

> **Camera note:** browsers only allow camera access on `https://` or `localhost`. Over plain LAN HTTP, the PWA scanner **won't work**. Either:
> - Use the phone's native camera app to open the QR (works fine, opens the detail page), and use the desktop browser to add items, **or**
> - Put a reverse proxy with a self-signed cert in front (Caddy or nginx), or tunnel via `cloudflared`/`tailscale`. Then the PWA scanner works.

## Environment variables

| Var | Default | Purpose |
|-----|---------|---------|
| `DATA_DIR` | `./data` | Where the SQLite DB and uploads live |
| `BASE_URL` | `http://localhost:5050` | Used inside QR codes |
| `SECRET_KEY` | `dev-secret-change-me` | Flask sessions |
| `MAX_UPLOAD_SIZE` | `10485760` | Bytes; 10 MB default |

## Tabs

- **Generate** — add places, print QR labels
- **Closet** — browse places with search, open one to see items
- **Edit** — inline edit, add categories, delete (soft)
- **Scan** — mobile QR scanner (PWA)

## Migrating an old DB

```bash
python scripts/migrate_old_db.py old_places.db data/places.db
```

## Backups

```bash
./backup.sh
```

Add to cron daily — see comments in the script.