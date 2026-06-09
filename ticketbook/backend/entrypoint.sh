#!/bin/sh
set -e

echo "[entrypoint] Initializing database..."
python - << 'PYEOF'
from app import app, db
from seed import seed_data
with app.app_context():
    db.create_all()
    seed_data()
print("[entrypoint] DB ready.")
PYEOF

echo "[entrypoint] Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 app:app
