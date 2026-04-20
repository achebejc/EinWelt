#!/usr/bin/env sh
set -e

echo "Waiting for database..."
python -c "import time, os, psycopg2; dsn=os.environ.get('DATABASE_URL'); connected=False; for _ in range(30):     try: psycopg2.connect(dsn).close(); connected=True; break     except Exception: time.sleep(1); print('db ready' if connected else 'db timeout')"

alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
