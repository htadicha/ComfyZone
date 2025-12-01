# Heroku Deployment Guide

## Required Environment Variables

| Name | Purpose | Local Notes | Heroku Notes |
| --- | --- | --- | --- |
| `SECRET_KEY` | Django cryptographic signing | Use `.env` secret | Set via Config Var |
| `DEBUG` | Toggle prod safeguards | `True` only locally | `False` in prod |
| `ALLOWED_HOSTS` | Permitted domains | e.g. `localhost,127.0.0.1` | e.g. `your-app.herokuapp.com` |
| `DATABASE_URL` | Postgres connection string | Optional if using local `DB_*` vars | Automatically injected when Postgres addon is added |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Manual DB override | Needed if not using `DATABASE_URL` locally | Typically not set on Heroku |
| `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Stripe payments | Supply test keys | Supply live keys and webhook secret |
| `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | SMTP delivery | Can keep console backend | Use SMTP/SendGrid credentials |
| `SITE_URL` | Used in transactional links | e.g. `http://localhost:8000` | e.g. `https://your-app.herokuapp.com` |

## Development vs Production Setup

### Local Development (.env file)
- **Keep your `.env` file** for local development
- Fill in your local database credentials, Stripe test keys, etc.
- This file is in `.gitignore` and won't be committed

### Heroku Production (Config Vars)
- Heroku uses **Config Vars** instead of `.env` files
- Set these in Heroku Dashboard or via CLI
- Heroku automatically provides `DATABASE_URL` when you add Postgres addon

## Heroku Deployment Steps

### 1. Install Heroku CLI
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

### 2. Login to Heroku
```bash
heroku login
```

### 3. Create Heroku App
```bash
heroku create your-app-name
```

### 4. Add PostgreSQL Addon
```bash
heroku addons:create heroku-postgresql:mini
```
This automatically sets `DATABASE_URL` - no need to configure it manually!

### 5. Set Config Vars in Heroku

#### Option A: Via Heroku Dashboard
1. Go to your app → Settings → Config Vars
2. Add each variable:

```
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app-name.herokuapp.com
STRIPE_PUBLISHABLE_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
SITE_URL=https://your-app-name.herokuapp.com
```

#### Option B: Via CLI
```bash
heroku config:set SECRET_KEY=your-production-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
heroku config:set STRIPE_PUBLISHABLE_KEY=pk_live_your_key
heroku config:set STRIPE_SECRET_KEY=sk_live_your_key
heroku config:set STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
heroku config:set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER=your-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=your-app-password
heroku config:set DEFAULT_FROM_EMAIL=your-email@gmail.com
heroku config:set SITE_URL=https://your-app-name.herokuapp.com
```

### 6. Deploy to Heroku
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Add Heroku remote (if not already added)
heroku git:remote -a your-app-name

# Deploy
git push heroku main
```

### 7. Run Migrations on Heroku
```bash
heroku run python manage.py migrate
```

### 8. Create Superuser on Heroku
```bash
heroku run python manage.py createsuperuser
```

### 9. Collect Static Files
```bash
heroku run python manage.py collectstatic --noinput
```

## Important Notes

### Database
- Heroku automatically provides `DATABASE_URL` when you add Postgres
- The settings.py is configured to use `DATABASE_URL` if available
- No need to set DB_NAME, DB_USER, etc. on Heroku

### Static Files
- WhiteNoise is configured for serving static files
- Run `collectstatic` after deployment
- Static files are served automatically by WhiteNoise

### Media Files
- Heroku's filesystem is ephemeral (files are deleted on restart)
- For production, use **AWS S3** or **Cloudinary** for media storage
- Consider using `django-storages` for S3 integration

### Stripe Webhooks
- Update your Stripe webhook URL to: `https://your-app-name.herokuapp.com/payments/webhook/`
- Use production Stripe keys (`pk_live_` and `sk_live_`) on Heroku
- Keep test keys (`pk_test_` and `sk_test_`) in your local `.env`

### Email
- For production, consider using **SendGrid** (Heroku addon) or **Mailgun**
- Gmail may have rate limits for production use

## Quick Commands

```bash
# View logs
heroku logs --tail

# Run Django shell
heroku run python manage.py shell

# Run any Django command
heroku run python manage.py <command>

# Open app in browser
heroku open

# View config vars
heroku config

# Scale dynos (if needed)
heroku ps:scale web=1
```

## Troubleshooting

### Static files not loading
```bash
heroku run python manage.py collectstatic --noinput
```

### Database connection issues
- Check if Postgres addon is added: `heroku addons`
- Verify DATABASE_URL: `heroku config:get DATABASE_URL`

### Migration errors
```bash
heroku run python manage.py migrate --run-syncdb
```


