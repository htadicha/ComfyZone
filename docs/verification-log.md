# Local Verification Log

## 2025-12-01

| Command | Context | Result |
| --- | --- | --- |
| `DATABASE_URL=sqlite:///db.sqlite3 python manage.py migrate` | Run inside `.venv` | Applied all migrations; `orders.0002_create_orderitem_table` faked once because it duplicates the OrderItem table already created in `0001`. |
| `DATABASE_URL=sqlite:///db.sqlite3 python manage.py collectstatic --noinput` | Run inside `.venv` | Collected 165 files into `staticfiles/`, matching the WhiteNoise setup. |
| `PYTHONUNBUFFERED=1 DATABASE_URL=sqlite:///db.sqlite3 python manage.py runserver --noreload` | Run inside `.venv` | Server started successfully and reported `http://127.0.0.1:8000/`. Command terminated manually after confirming startup logs. |
| `PYTHONUNBUFFERED=1 DATABASE_URL=sqlite:///db.sqlite3 gunicorn furniture_store.wsgi --bind 127.0.0.1:8001` | Run inside `.venv` | Gunicorn 23.0.0 booted, spawned a sync worker, and shut down cleanly after manual termination. |

These commands validate that the project boots locally using the SQLite fallback defined by `DATABASE_URL`. Use the same environment variable when reproducing the checks.






