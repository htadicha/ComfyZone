# Local Virtual Environment Setup

These steps mirror the Heroku runtime (`python-3.12.0` per `runtime.txt`) and match the `requirements.txt` lock.

## 1. Create/Refresh the Environment

```bash
python3 -m venv .venv
```

## 2. Activate the Environment

| Platform | Command |
| --- | --- |
| macOS / Linux | `source .venv/bin/activate` |
| Windows PowerShell | `.\\.venv\\Scripts\\Activate.ps1` |
| Windows cmd.exe | `.\\venv\\Scripts\\activate.bat` |

To deactivate at any time run:

```bash
deactivate
```

## 3. Install Dependencies

Run inside the activated environment:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Bootstrap the Database

SQLite is now the default local database (written to `db.sqlite3`), so no
extra environment variables are required:

```bash
python manage.py migrate
```

You can still override the database explicitly—e.g. `DATABASE_URL=sqlite:///db.sqlite3 python manage.py migrate`
—when running ad‑hoc scripts or CI jobs.

> **Note:** The current migrations include a duplicate `orders.0002_create_orderitem_table`. If you hit `table "orders_orderitem" already exists`, mark it as applied with:<br>`python manage.py migrate orders 0002 --fake`.

## 5. Collect Static Assets

Before mimicking a Heroku build, gather assets into `staticfiles/`:

```bash
python manage.py collectstatic --noinput
```

WhiteNoise reads from `STATIC_ROOT=staticfiles/`, so this command should succeed locally before deploying.

## 6. Media Storage Options

- By default `USE_AWS=False`, so uploaded assets are written to `media/` on disk.
- To exercise the S3 path locally, export the AWS variables from `.env.example` and set `USE_AWS=True`. The app will then send uploads to your bucket via `django-storages`.

## 7. Notes for Heroku

- Keep `.venv` out of version control; Heroku builds its own environment using `runtime.txt` and `requirements.txt`.
- Use `pip freeze > requirements.txt` after adding packages so Heroku receives the same versions.
- When developing locally, run management commands via `python manage.py <command>` **after** activating the environment to ensure Django 5.2.8 and the matching dependencies are used.

