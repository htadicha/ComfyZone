# 🛋️ ComfyZone – Advanced Django Furniture Commerce Platform

[![Django](https://img.shields.io/badge/Django-5.2.8-092E20?logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![Stripe](https://img.shields.io/badge/Payments-Stripe-blueviolet?logo=stripe)](https://stripe.com/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](#deployment)
[![Docs](https://img.shields.io/badge/Docs-README.md-blue)](#deployment)

## 🌐 Live Demo

**🚀 Staging (Heroku)**: [https://comfyzone.herokuapp.com](https://comfyzone.herokuapp.com) *(replace with your live hostname once deployed)*

> ComfyZone is deploy-ready via the included `Procfile`, `runtime.txt`, and the steps documented in the [Deployment](#deployment) section below.

## 📋 Table of Contents

- [Overview](#overview)
- [Wireframes & Visual References](#wireframes--visual-references)
- [Key Highlights](#key-highlights)
- [Features](#features)
  - [Visitor Functionalities](#-visitor-functionalities)
  - [Registered User Functionalities](#-registered-user-functionalities)
  - [Admin Functionalities](#-admin-functionalities)
  - [Additional Features Available to All Users](#-additional-features-available-to-all-users)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [Configuration & Environment](#configuration--environment)
- [Installation & Local Setup](#installation--local-setup)
- [Usage](#usage)
- [API & URL Surface Area](#api--url-surface-area)
- [Security Features](#security-features)
- [Performance Optimization](#performance-optimization)
- [Testing & Validation](#testing--validation)
- [Deployment](#deployment)
- [Heroku AWS Configuration](#heroku-aws-configuration)
- [Agile Delivery Playbook](#agile-delivery-playbook)
- [Social Media & Marketing Readiness](#social-media--marketing-readiness)
- [Contributing](#contributing)
- [License & Usage Rights](#license--usage-rights)
- [Support](#support)
- [Acknowledgments](#acknowledgments)

## Overview

ComfyZone is a full-stack, production-ready e-commerce experience tailored for premium furniture brands. It combines a polished Bootstrap 5 front end with a modern Django 5.2.8 back end, delivering:

- Custom email-based user accounts with verification
- Robust product catalog, variations, and imagery
- Persistent carts for guests and authenticated users (with seamless merge on login)
- Stripe-powered checkout and order lifecycle automation
- Review, rating, newsletter, sitemap, and SEO modules out of the box

All configuration is sourced from environment variables (via `python-decouple`), making the project safe to deploy to Heroku, Render, Railway, or any WSGI-capable host.

## Wireframes & Visual References

UI mockups are derived directly from the Django templates under `templates/store/` and the shared assets inside `static/images/`. Use these detailed wireframes plus the referenced templates to align designers, developers, and QA:

### Home / Landing Page

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Hero: headline + CTA                                                         │
│ ┌─────────────┐ ┌──────────────────────────────────────────────────────────┐ │
│ │ Value copy  │ │ Lifestyle image                                         │ │
│ │ • H1        │ │ • Lazy-loaded to keep LCP < 2.5s                        │ │
│ │ • Paragraph │ │                                                          │ │
│ │ • CTA pair  │ │                                                          │ │
│ └─────────────┘ └──────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────┤
│ Featured products (3-up cards)                                               │
│ [Card]  [Card]  [Card]                                                       │
│ • Image w/ alt text                                                          │
│ • Title                                                                      │
│ • Price                                                                      │
│ • Quick action icon                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ Why Choose Us                                                                │
│ • 4 feature tiles (Shipping, Shopping ease, Support, Returns)                │
├──────────────────────────────────────────────────────────────────────────────┤
│ Newsletter CTA (footer hero)                                                 │
│ • Email + name inputs                                                        │
│ • Clear consent copy                                                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Notes:**
- Navigation exposes Shop/About/Services/Contact plus account/cart icons.
- Hero CTA buttons route to `shop/` and `about/`.
- Featured products link to `/product/<slug>/`.
- Newsletter form posts to `marketing:subscribe` and feeds Merit LO5 evidence.

### Product Detail Page

```
┌─────────────────────────────┬──────────────────────────────────────────────┐
│ Image carousel (60%)        │ Product info (40%)                           │
│ • Primary image             │ • Product title + price                      │
│ • Thumbnail rail            │ • Rating summary + review count              │
│                             │ • Short description                          │
│                             │ • Stock status + quantity selector           │
│                             │ • Variation selects (color/size)             │
│                             │ • Add to cart button                         │
├─────────────────────────────┴──────────────────────────────────────────────┤
│ Reviews block                                                               
│ • List top 5 approved reviews                                               
│ • CTA: "Manage your review" (auth only)                                     
│ • Guests see login prompt                                                   
├──────────────────────────────────────────────────────────────────────────────┤
│ Related products (4-up grid)                                                 
│ • Cards mirror home layout                                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Key Decisions:**
- **Review CTA** links to the unified CRUD page introduced in this sprint, satisfying LO1.9 + LO1.13 evidence.
- **Metadata**: `meta_description` pulls from `product.meta_description` so SEO snippets match catalog copy.
- **Accessibility**: Carousel controls labelled for screen readers; images carry `alt_text`.

### Additional Page Wireframes

**Checkout (templates/payments/checkout.html)**
```
┌─────────────────────┬─────────────────────────────────────┐
│ Address selection   │ Order summary, taxes, Stripe button │
│ + notes             │ Status badges + audit trail         │
└─────────────────────┴─────────────────────────────────────┘
```

**Storefront Admin (templates/store/admin/*.html)**
```
┌───────────────┬──────────────────────────────────────────┐
│ Filter + search│ Paginated table w/ status badges        │
│ Quick actions  │ Inline links to CRUD + gallery manage   │
└───────────────┴──────────────────────────────────────────┘
```

*Need pixel-perfect references? Reuse the hero/product assets in `static/images/` or capture the templates locally with `python manage.py runserver` + your favorite screenshot tool.*

## Key Highlights

- **Scalable Django architecture** with discrete apps (`accounts`, `store`, `cart`, `orders`, `payments`, `reviews`, `marketing`, `core`).
- **Production safeguards** baked into `furniture_store/settings.py` (WhiteNoise, SSL redirects, secure cookies when `DEBUG=False`).
- **Admin-lite storefront tooling** allowing staff to CRUD products and galleries without Django admin.
- **SEO foundation** via `core.sitemaps.ProductSitemap` + templated `robots.txt`.
- **Newsletter growth engine** with duplicate detection (`marketing` app) and export-friendly admin list.
- **Manual verification log** (`docs/verification-log.md`) capturing the runbook used to validate deployments.

## Features

This section details all functionalities available to different user types on the ComfyZone platform.

---

## 👥 Visitor Functionalities

Visitors (non-authenticated users) can browse and interact with the storefront with limited functionality.

### User Registration

Visitors can create an account by providing their email address, name, and password. The registration process includes:

- **Email-based registration**: Users register using their email address as the username
- **Email verification**: After registration, users receive a verification email with a secure token
- **Account activation**: Users must verify their email before they can log in
- **Resend verification**: Option to request a new verification email if the original is not received

![User Registration](media/site_functionality_pictures/user_registration.png)

*Screenshot: User registration form with email verification workflow*

### Product Browsing & Discovery

- **Product catalog**: Browse all available products with images, prices, and descriptions
- **Product details**: View detailed product information including:
  - Multiple product images in a gallery
  - Product variations (color, size, material) with price adjustments
  - Product specifications and descriptions
  - Customer reviews and ratings (read-only for visitors)

![Product Detail](media/site_functionality_pictures/product_detail.png)

*Screenshot: Product detail page with image gallery, variations, and reviews*

### Shopping Cart (Guest Session)

- **Session-based cart**: Add products to cart without creating an account
- **Cart persistence**: Cart items persist during the browser session
- **Cart merge on login**: Guest cart items automatically merge with user cart upon login
- **Quantity management**: Increase/decrease item quantities using +/- buttons
- **Item removal**: Remove items from cart before checkout

![Shopping Cart](media/site_functionality_pictures/cart.png)

*Screenshot: Shopping cart page with quantity controls and item management*

### Showroom Consultation Request

Visitors can request a personalized showroom consultation with interior design specialists:

- **Lead capture form**: Submit contact information and project details
- **Interest selection**: Specify product or service of interest
- **Consent management**: GDPR-compliant consent tracking
- **Response guarantee**: Specialists respond within one business day

![Showroom Consultation](media/site_functionality_pictures/showroom_consulation.png)

*Screenshot: Showroom consultation request form*

---

## 🔐 Registered User Functionalities

Authenticated users have access to additional features beyond visitor capabilities.

### User Authentication

- **Secure login**: Email and password-based authentication
- **Email verification**: Required before first login
- **Password security**: Secure password hashing and validation
- **Session management**: Automatic session handling with secure cookies

![User Login](media/site_functionality_pictures/registered_user_login.png)

*Screenshot: User login page with email verification reminder*

### Persistent Shopping Cart

- **Database-backed cart**: Cart items persist across sessions and devices
- **Cart synchronization**: Automatic merge of guest cart items on login
- **Cart management**: Full CRUD operations on cart items
- **Variation support**: Add products with specific variations (color, size, etc.)

### Product Reviews & Ratings

Authenticated users who have purchased products can:

- **Write reviews**: Submit detailed product reviews with ratings (1-5 stars)
- **Edit reviews**: Modify existing reviews before or after approval
- **Delete reviews**: Remove their own reviews
- **Verified purchase badge**: Reviews from verified purchases are marked
- **Review moderation**: Reviews require admin approval before publication

![Product Review](media/site_functionality_pictures/product_review.png)

*Screenshot: Product review form with rating and moderation status*

### Checkout & Payment

- **Address management**: Save multiple shipping and billing addresses
- **Default address**: Set preferred addresses for faster checkout
- **Order summary**: Review cart items, quantities, and totals before payment
- **Tax calculation**: Automatic 10% tax calculation
- **Stripe integration**: Secure payment processing via Stripe Checkout
- **Payment confirmation**: Real-time payment status updates

![Checkout Page](media/site_functionality_pictures/checkout.png)

*Screenshot: Checkout page with address selection and order summary*

![Payment Section](media/site_functionality_pictures/payment_section.png)

*Screenshot: Payment processing interface with Stripe integration*

### Order Management

- **Order history**: View all past orders with status tracking
- **Order details**: Detailed view of each order including:
  - Order number and date
  - Items purchased with quantities and prices
  - Shipping and billing addresses (snapshotted)
  - Payment status and transaction details
  - Order status (New → Accepted → Completed/Cancelled)
- **Order confirmation**: Email confirmation sent automatically after successful payment

![Order History](media/site_functionality_pictures/order_history.png)

*Screenshot: Order history page listing all user orders*

![Order Details](media/site_functionality_pictures/order_hsitory_details.png)

*Screenshot: Detailed order view with items, addresses, and payment information*

![Order Confirmation](media/site_functionality_pictures/order_confirmation.png)

*Screenshot: Order confirmation page after successful payment*

### User Profile Management

- **Profile editing**: Update personal information (name, email)
- **Address book**: Manage multiple shipping and billing addresses
- **Default address**: Set and change default addresses
- **Account security**: Change password and manage account settings

---

## 👨‍💼 Admin Functionalities

Staff users have access to administrative tools for managing the storefront.

### Storefront Product Management

Admins can manage products directly from the storefront without accessing Django admin:

- **Product CRUD**: Create, read, update, and delete products
- **Product status**: Toggle product active/inactive status
- **Feature flags**: Mark products as featured for homepage display
- **Image management**: Upload and manage product images with primary image selection
- **Variation management**: Add and configure product variations (color, size, material)
- **Bulk operations**: Search and filter products for efficient management

![Admin Panel from Site](media/site_functionality_pictures/admin_panel_from_site.png)

*Screenshot: Storefront admin interface for product management*

### Admin Dashboard

- **Product overview**: View all products with status indicators
- **Quick actions**: Fast access to create, edit, or delete products
- **Search and filter**: Find products quickly using search and filter options
- **Status management**: Bulk status updates for products
- **Analytics**: View product performance metrics

![Admin Dashboard](media/site_functionality_pictures/admin_panel_dashboard.png)

*Screenshot: Admin dashboard with product management tools*

### Marketing Lead Management

- **Lead dashboard**: View all marketing leads captured from the website
- **Lead status tracking**: Track lead status (New → Contacted → Qualified → Won/Lost)
- **Lead assignment**: Assign leads to team members
- **Export functionality**: Export leads to CSV for CRM integration
- **Newsletter management**: View and manage newsletter subscribers
- **Consent tracking**: Monitor and log user consent for GDPR compliance

### Order Administration

- **Order management**: View and manage all customer orders
- **Status updates**: Update order status (New → Accepted → Completed/Cancelled)
- **Order details**: Access complete order information including customer details
- **Payment tracking**: Monitor payment status and transaction details

### Content Management

- **Category management**: Create and manage product categories with parent/child relationships
- **SEO management**: Set meta descriptions, keywords, and OG tags for products
- **Review moderation**: Approve or reject customer reviews
- **Content updates**: Update site content, terms, privacy policy, etc.

---

## 🔍 Additional Features Available to All Users

### Search & Filtering

- **Full-text search**: Search products by name, description, or keywords
- **Category filtering**: Filter products by category and subcategory
- **Price range**: Filter by minimum and maximum price
- **Stock status**: Filter by in-stock or out-of-stock items
- **Sorting options**: Sort by newest, price (low to high), price (high to low), name, or rating

### SEO & Discoverability

- **Sitemap generation**: Automatic XML sitemap at `/sitemap.xml`
- **Robots.txt**: Search engine directives at `/robots.txt`
- **Meta tags**: SEO-optimized meta descriptions and keywords
- **Open Graph tags**: Social media sharing optimization
- **Canonical URLs**: Prevent duplicate content issues

### Newsletter Subscription

- **Footer subscription**: Newsletter signup form in site footer
- **Double opt-in**: Email confirmation required for subscription
- **Consent logging**: GDPR-compliant consent tracking
- **Unsubscribe**: Easy unsubscribe option in all emails

### Responsive Design

- **Mobile-first**: Fully responsive design for all screen sizes
- **Touch-friendly**: Optimized for mobile and tablet interactions
- **Accessibility**: ARIA labels and keyboard navigation support
- **Cross-browser**: Compatible with all modern browsers

## Technology Stack

### Backend

- Django 5.2.8 (`requirements.txt`)
- Python 3.12.0 (`runtime.txt`)
- PostgreSQL in production with SQLite fallback (automatic via `dj-database-url` + `python-decouple`)
- Stripe SDK 14.x for payments
- Pillow for media handling
- Gunicorn + WhiteNoise for WSGI deployments

### Frontend

- Bootstrap 5 theme (Untree.co Furni variant)
- Vanilla JS + Tiny Slider
- Font Awesome / Material Icons / Feather for iconography

### Tooling & Operations

- `python-decouple` for env management
- `crispy_forms` + `crispy_bootstrap5` for consistent forms
- `dj-database-url` for effortless DATABASE_URL parsing
- Procfile-driven Heroku deployment (`web: gunicorn furniture_store.wsgi --log-file -`)
- Documentation under `docs/` for setup + verification

## Architecture

```text
ComfyZone/
├── accounts/           # Custom user, profiles, addresses
├── cart/               # Persistent + session carts, merge utilities
├── core/               # Context processors, sitemaps, shared URLs
├── marketing/          # Newsletter opt-in/out
├── orders/             # Orders, order items, history views
├── payments/           # Checkout views, Stripe webhooks
├── reviews/            # Moderated reviews
├── store/              # Catalog, storefront pages, staff CRUD views
├── templates/          # Bootstrap pages + emails
├── static/             # CSS, JS, and visual assets
├── media/              # Uploaded product and profile images
├── docs/               # Local setup + verification guides
├── DEPLOYMENT.md       # Detailed Heroku instructions
├── requirements.txt
├── runtime.txt
├── Procfile
└── manage.py
```

### Request Flow & Data Sync

1. **Customer visits storefront** → `store.views.home` renders hero + featured products.
2. **Browse & filter** → `store.views.shop` applies search, filter, sort, and pagination server-side.
3. **Add to cart** → `cart.views.add_to_cart` persists to session or user cart; cart context shows counts everywhere.
4. **Checkout** → `payments.checkout_view` aggregates totals, exposes addresses, and launches Stripe Checkout.
5. **Payment** → Stripe webhook confirms payment intent and updates `payments.Payment` + `orders.Order`.
6. **Post-purchase** → Order emails fire, reviews unlocked, marketing opt-ins captured through footer forms.

## Database Schema

```mermaid
erDiagram
    User ||--|| Profile : "has"
    User ||--|{ Address : "stores"
    User ||--o{ Cart : "owns"
    User ||--o{ Review : "writes"
    User ||--o{ Order : "places"
    User ||--o{ Payment : "initiates"
    User ||--o{ NewsletterSubscriber : "opt-in"

    Category ||--o{ Product : "categorizes"
    Product ||--o{ ProductImage : "displays"
    Product ||--o{ ProductVariation : "offers"
    Product ||--o{ Review : "receives"
    Product ||--o{ OrderItem : "sold as"

    Cart ||--o{ CartItem : "contains"
    Product ||--o{ CartItem : "added to"

    Order ||--o{ OrderItem : "fulfills"
    Order ||--|| Payment : "settles"
    Address ||--o{ Order : "snapshotted in"
```

### 🔗 Key Relationships Explained

- **User ↔ Profile / Address** – one-to-one profile, one-to-many addresses with default enforcement in `Address.save`.
- **Product ↔ Variation/Image** – automatically enforces unique variation combos and a single primary image per SKU.
- **Cart ↔ CartItem** – unique-together constraint on `(cart, product)` plus variation-aware subtotal math.
- **Order ↔ Payment** – one-to-one, with metadata linking Stripe session IDs to internal order numbers.
- **Review ↔ OrderItem** – verified purchases flagged automatically when a review is created.

### Normalization & Indexing

- 3NF schema across apps; derived attributes (average rating, discount) computed on the fly.
- Use PostgreSQL indexes for frequently filtered fields:

```sql
CREATE INDEX idx_product_slug ON store_product(slug);
CREATE INDEX idx_category_parent ON store_category(parent_id);
CREATE INDEX idx_order_number ON orders_order(order_number);
CREATE INDEX idx_payment_tx ON payments_payment(transaction_id);
```

## Configuration & Environment

| Variable | Purpose | Example |
| --- | --- | --- |
| `SECRET_KEY` | Django signing key | `django-insecure-...` |
| `DEBUG` | Toggle prod safeguards | `False` in production |
| `ALLOWED_HOSTS` | Comma-separated domains | `comfyzone.com,www.comfyzone.com` |
| `DATABASE_URL` | Primary DB | `postgres://user:pass@host:5432/db` |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | Optional manual Postgres override | Only needed locally if you skip SQLite |
| `STRIPE_PUBLISHABLE_KEY` / `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` | Payments | Use test keys locally |
| `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | SMTP | Console backend by default |
| `SITE_URL` | Absolute URL in transactional emails | `https://comfyzone.herokuapp.com` |

Reference the [Deployment](#deployment) section above for full Heroku instructions and `docs/local-setup.md` for virtualenv guidance.

## Installation & Local Setup

1. **Clone & enter the repo**

   ```bash
   git clone https://github.com/<you>/ComfyZone.git
   cd ComfyZone-1
   ```

2. **Create a virtual environment (see `docs/local-setup.md`)**

   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Bootstrap environment variables**

   ```bash
   cp .env.example .env  # create one if it does not exist yet
   ```

   Fill in the keys from the table above. Leaving DB vars blank will fall back to SQLite (`db.sqlite3`).

5. **Apply migrations & collect static assets**

   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

6. **Create a superuser and run the dev server**

   ```bash
   python manage.py createsuperuser
   python manage.py runserver
   ```

## Usage

- **Storefront** – visit `http://127.0.0.1:8000/` for the marketing site, `shop/` for the product catalog.
- **Admin dashboard** – `http://127.0.0.1:8000/store/manage/products/` (requires staff flag) provides CRUD tools without entering Django admin.
- **Django admin** – `http://127.0.0.1:8000/admin/` for model-level management and exports.
- **Newsletter** – subscribe/unsubscribe via the footer form; review entries in Django admin (`marketing.NewsletterSubscriber`).
- **Sitemap / robots** – `http://127.0.0.1:8000/sitemap.xml` and `templates/robots.txt`.

## API & URL Surface Area

| Domain | Path(s) | Notes |
| --- | --- | --- |
| Storefront | `/`, `/shop/`, `/product/<slug>/`, `/category/<slug>/`, `/about/`, `/services/`, `/contact/` | Marketing + catalog pages |
| Catalog Admin | `/store/manage/products/…` | Create/update/delete products & galleries (staff-only) |
| Accounts | `/accounts/register/`, `/accounts/login/`, `/accounts/profile/`, `/accounts/verify-email/<token>/`, `/accounts/address/...` | Custom auth workflow |
| Cart | `/cart/`, `/cart/add/<product_id>/`, `/cart/update/<item_id>/`, `/cart/remove/<item_id>/` | Session + persistent cart management |
| Payments | `/payments/checkout/`, `/payments/create-checkout-session/`, `/payments/success/`, `/payments/webhook/` | Stripe checkout + webhook endpoint |
| Orders | `/orders/history/`, `/orders/<order_number>/` | Authenticated order history |
| Reviews | `/reviews/product/<slug>/`, `/reviews/create/<slug>/`, `/reviews/update/<id>/`, `/reviews/delete/<id>/` | Moderated reviews |
| Marketing | `/marketing/subscribe/`, `/marketing/unsubscribe/<email>/` | Newsletter engine |

All endpoints are traditional Django views rendered via templates; there is no external REST API at this time.

## Security Features

- **Custom user model** – email-as-username plus verification tokens prevents duplicate accounts.
- **Env-first secrets** – `python-decouple` loads keys from `.env`/Config Vars; secrets are never hard-coded.
- **Session hardening** – `SESSION_COOKIE_AGE=86400`, `SESSION_SAVE_EVERY_REQUEST`, and secure cookie flags automatically applied when `DEBUG=False`.
- **Transport security** – `SECURE_SSL_REDIRECT`, HSTS, and secure cookies toggle on for production.
- **CSRF & XSS protection** – Django’s default middleware stack + template auto-escaping.
- **Role-based storefront admin** – `@login_required` + `@user_passes_test(is_staff_user)` guard every product-management view.
- **Stripe webhook verification** – signature validation with `STRIPE_WEBHOOK_SECRET` before processing events.

## Performance Optimization

- **Database fallbacks** – local development defaults to SQLite to eliminate setup friction; production switches to Postgres with connection pooling (`conn_max_age=600`).
- **Efficient catalog queries** – shop view layers search, filters, and pagination server-side, minimizing payload sizes.
- **Image management** – `ProductImage` enforces a single primary image for consistent caching; static assets are served via WhiteNoise with hashed filenames.
- **Selective calculations** – rating averages, price discounts, and cart subtotals computed on demand rather than stored, keeping tables lean.
- **Gunicorn + WhiteNoise** – lightweight production stack with gzip/brotli compression when `DEBUG=False`.

## Testing & Validation

Automated Django test modules are scaffolded (`accounts/tests.py`, `store/tests.py`, etc.) and ready for suite expansion. In the meantime, `docs/verification-log.md` captures the exact commands already executed on 2025‑12‑01, including migrations, `collectstatic`, `runserver`, and a Gunicorn smoke test. Validator evidence (flake8, djlint, W3C HTML exports, and broken-link sweeps) is logged in [`docs/evidence/validation-summary.md`](docs/evidence/validation-summary.md) so assessors can review objective proof without rerunning every tool.

### Manual Regression Checklist

| Scenario | Expected Result | Status |
| --- | --- | --- |
| Guest browsing & filtering | `/shop/` search + filters adjust queryset, pagination stable | ✅ Manual |
| Registration & email verification | Verification link disables login until clicked | ✅ Manual (requires SMTP config) |
| Cart merge on login | Session items append/increment user cart in `cart.utils.merge_carts` | ✅ Manual |
| Checkout happy path | Stripe test key charges succeed, order/payment statuses sync | ✅ Manual |
| Newsletter flow | Duplicate signups show info banner, unsubscribes retained | ✅ Manual |
| Sitemap/robots | `/sitemap.xml` and `/robots.txt` return 200 with fresh entries | ✅ Manual |

> Expand the automated suite by adding tests under each app’s `tests.py`, then run `python manage.py test`.

## Deployment

### Required Environment Variables

| Name | Purpose | Local Notes | Heroku Notes |
| --- | --- | --- | --- |
| `SECRET_KEY` | Django cryptographic signing | Use `.env` secret | Set via Config Var |
| `DEBUG` | Toggle prod safeguards | `True` only locally | `False` in prod |
| `ALLOWED_HOSTS` | Permitted domains | e.g. `localhost,127.0.0.1` | e.g. `your-app.herokuapp.com` |
| `DATABASE_URL` | Postgres connection string | Optional if using local `DB_*` vars | Automatically injected when Postgres addon is added |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Manual DB override | Only set when you want local Postgres; otherwise SQLite is automatic | Typically not set on Heroku |
| `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Stripe payments | Supply test keys | Supply live keys and webhook secret |
| `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | SMTP delivery | Can keep console backend | Use SMTP/SendGrid credentials |
| `SITE_URL` | Used in transactional links | e.g. `http://localhost:8000` | e.g. `https://your-app.herokuapp.com` |
| `USE_AWS` | Toggle S3-backed media storage | Leave `False` to store uploads locally | Set `True` so uploads land in S3 |
| `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_SIGNATURE_VERSION`, `AWS_S3_CUSTOM_DOMAIN`, `AWS_LOCATION` | S3 configuration for media | Optional when `USE_AWS=False` | Required when `USE_AWS=True` (use the region code, e.g. `eu-west-1`) |

### Development vs Production Setup

#### Local Development (.env file)

- **Keep your `.env` file** for local development
- Fill in your local database credentials, Stripe test keys, etc.
- This file is in `.gitignore` and won't be committed

#### Heroku Production (Config Vars)

- Heroku uses **Config Vars** instead of `.env` files
- Set these in Heroku Dashboard or via CLI
- Heroku automatically provides `DATABASE_URL` when you add Postgres addon

### Environment Configuration Workflow

1. Copy `.env.example` to `.env` for local development.
2. Update `SECRET_KEY`, Stripe keys, and email credentials with test values.
3. Leave `DEBUG=True` and `ALLOWED_HOSTS=localhost,127.0.0.1` locally; swap to `DEBUG=False` and your production hostname(s) on Heroku.
4. Use either `DATABASE_URL=postgres://...` or the individual `DB_*` variables. `dj-database-url` takes precedence when `DATABASE_URL` is present. If you leave both blank, Django now falls back to SQLite (`db.sqlite3`) for local smoke tests.
5. Commit **only** `.env.example`; keep `.env` out of git. On Heroku, replicate the same key names under Settings → Config Vars or via `heroku config:set KEY=value`.

### Static Files Workflow

- `STATIC_ROOT` is set to `staticfiles/`. Before deploying, run `python manage.py collectstatic --noinput`.
- WhiteNoise is inserted automatically when `DEBUG=False`, so Heroku can serve the collected assets without extra services.
- If you update CSS/JS, re-run `collectstatic` so the hashed files in `staticfiles/` remain in sync.

### Heroku Deployment Steps

#### 1. Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

#### 2. Login to Heroku

```bash
heroku login
```

#### 3. Create Heroku App

```bash
heroku create your-app-name
```

#### 4. Add PostgreSQL Addon

```bash
heroku addons:create heroku-postgresql:mini
```

This automatically sets `DATABASE_URL` - no need to configure it manually!

#### 5. Set Config Vars in Heroku

##### Option A: Via Heroku Dashboard

1. Go to your app → Settings → Config Vars
2. Add each variable:

```env
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
USE_AWS=True
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=eu-west-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_LOCATION=media
```

##### Option B: Via CLI

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
heroku config:set USE_AWS=True
heroku config:set AWS_STORAGE_BUCKET_NAME=your-bucket
heroku config:set AWS_S3_REGION_NAME=eu-west-1
heroku config:set AWS_ACCESS_KEY_ID=your-access-key
heroku config:set AWS_SECRET_ACCESS_KEY=your-secret-key
heroku config:set AWS_LOCATION=media
```

#### 6. Deploy to Heroku

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

#### 7. Run Migrations on Heroku

```bash
heroku run python manage.py migrate
```

#### 8. Create Superuser on Heroku

```bash
heroku run python manage.py createsuperuser
```

#### 9. Collect Static Files

```bash
heroku run python manage.py collectstatic --noinput
```

### Important Notes

#### Database

- Heroku automatically provides `DATABASE_URL` when you add Postgres
- The settings.py is configured to use `DATABASE_URL` if available
- No need to set DB_NAME, DB_USER, etc. on Heroku
- When neither `DATABASE_URL` nor `DB_*` overrides are defined locally, the project uses SQLite automatically so `python manage.py runserver` works out of the box.

#### Static Files

- WhiteNoise is configured for serving static files
- Run `collectstatic` after deployment
- Static files are served automatically by WhiteNoise

#### Media Files

- Heroku's filesystem is ephemeral (files are deleted on restart)
- This project now supports AWS S3 out of the box via `django-storages`.
- Set `USE_AWS=True` plus the AWS credentials listed above so uploaded product images persist.
- Bucket objects are stored under the prefix defined by `AWS_LOCATION` (default `media`).

#### Stripe Webhooks

- Update your Stripe webhook URL to: `https://your-app-name.herokuapp.com/payments/webhook/`
- Use production Stripe keys (`pk_live_` and `sk_live_`) on Heroku
- Keep test keys (`pk_test_` and `sk_test_`) in your local `.env`

#### Email

- For production, consider using **SendGrid** (Heroku addon) or **Mailgun**
- Gmail may have rate limits for production use

### Quick Commands

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

### Quality Gates & Validation Evidence

Run the following before tagging a release. Capture the console output or validator screenshots and log them in [`docs/evidence/validation-summary.md`](docs/evidence/validation-summary.md) so assessors can confirm the artefacts.

| Check | Command / URL | Purpose |
| --- | --- | --- |
| Python style | `flake8 accounts reviews` | Keeps authentication/CRUD code compliant with PEP8. Expand scope when you touch new apps. |
| Template hygiene | `djlint templates/base.html templates/reviews templates/store/home.html templates/store/about.html templates/store/services.html templates/store/terms.html templates/store/privacy.html templates/404.html --check --profile=django` | Catches malformed HTML on the customer-facing pages touched in this remediation; expand the list as you edit other templates. |
| Broken links | `npx broken-link-checker https://your-app.herokuapp.com --recursive --exclude www.facebook.com` | Guarantees no `href="#"` placeholders remain in production. |
| W3C validator | https://validator.w3.org/ | Upload `base.html`, landing pages, and any edited templates after SEO updates. |

### Troubleshooting

#### Static files not loading

```bash
heroku run python manage.py collectstatic --noinput
```

#### Database connection issues

- Check if Postgres addon is added: `heroku addons`
- Verify DATABASE_URL: `heroku config:get DATABASE_URL`

#### Migration errors

```bash
heroku run python manage.py migrate --run-syncdb
```

### Docker (Optional)

```Dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "furniture_store.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Run with:

```bash
docker build -t comfyzone .
docker run --env-file .env -p 8000:8000 comfyzone
```

### AWS / Other Hosts

- Use Elastic Beanstalk or ECS with the Dockerfile above.
- Point static/media storage to S3 + CloudFront via `django-storages` when scaling beyond single dynos.
- Configure HTTPS certificates (ACM / Let's Encrypt) and update `ALLOWED_HOSTS`.

---

## Heroku AWS Configuration

### Current Heroku Config Vars

```
USE_AWS:                 True
AWS_STORAGE_BUCKET_NAME: hawashmart
AWS_S3_REGION_NAME:      Europe (Ireland) eu-west-1
AWS_ACCESS_KEY_ID:       AKIAQRX5V4PXXJFRL2U5
AWS_SECRET_ACCESS_KEY:   [SET - Hidden for security]
AWS_LOCATION:            media
```

### Configuration Analysis

#### ✅ What's Configured Correctly

1. **USE_AWS**: `True` ✅ - AWS is enabled
2. **Bucket Name**: `hawashmart` ✅ - Matches your bucket
3. **Region**: `Europe (Ireland) eu-west-1` ✅ - Will be normalized to `eu-west-1`
4. **Credentials**: Set ✅
5. **AWS_LOCATION**: `media` ✅ - This is correct

#### 🔍 Path Structure

With your current configuration:
- `AWS_LOCATION` = `media`
- `upload_to` = `photos/products/` (after our model fix)
- **Full path** = `media/photos/products/` ✅

This matches what you said: files should be in `media/photos/products/`

### The Issues

#### Issue 1: Region Name Format
**Current:** `Europe (Ireland) eu-west-1`  
**Will be normalized to:** `eu-west-1` ✅

This is fine - the normalization function handles it.

#### Issue 2: Path Mismatch for Existing Files
**Problem:** Files uploaded BEFORE we changed the model are at:
- `media/products/` (old path)

**New uploads will go to:**
- `media/photos/products/` (new path) ✅

#### Issue 3: Permissions
The bucket likely needs public read permissions for images to load.

### What Needs to Be Done

#### Option 1: Update AWS_LOCATION (Not Recommended)
If you want to keep old files accessible, you could change:
```bash
heroku config:set AWS_LOCATION=media/photos --app comfyzone
```

But this would break existing file paths. Not recommended.

#### Option 2: Fix Existing Files (Recommended)
1. Files already uploaded: They're at `media/products/` (old path)
2. New uploads: Will go to `media/photos/products/` (new path) ✅
3. Solution: Re-upload existing images OR move them in S3 Console

#### Option 3: Fix Bucket Permissions
The main issue is likely bucket permissions preventing public access.

### Recommended Actions

1. ✅ **Keep current config** - It's correct for new uploads
2. ✅ **Fix bucket permissions** - Allow public read access
3. ✅ **Re-upload or move existing images** - If you have old images at wrong path
4. ✅ **Verify new uploads work** - Test with a new image upload

### Quick Fix Commands

#### Check if region normalization works:
The region format `Europe (Ireland) eu-west-1` will be normalized to `eu-west-1` automatically.

#### Verify config on Heroku:
```bash
heroku run python manage.py shell --app comfyzone
```

Then:
```python
from django.conf import settings
print(f"AWS_LOCATION: {settings.AWS_LOCATION}")
print(f"AWS_S3_REGION_NAME: {settings.AWS_S3_REGION_NAME}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
```

### Summary

✅ **AWS config is correctly set on Heroku**  
✅ **Path structure will be correct for new uploads**  
⚠️ **Bucket permissions need to be fixed**  
⚠️ **Existing files may need to be re-uploaded**

## Agile Delivery Playbook

Detailed artefacts (board process, sprint logs, and screenshots) now live under [`docs/agile/`](docs/agile/).

### GitHub Issues Workflow

- **Issue templates**: Bug Report, Feature Request, User Story, Epic, Sprint Planning.
- **Labels**:
  - Priority: `critical`, `high`, `medium`, `low`
  - Type: `bug`, `feature`, `enhancement`, `documentation`, `security`, `performance`
  - Surface: `frontend`, `backend`, `database`, `api`, `tests`, `marketing`

### Current Sprint Snapshot

| Story ID | Role & Goal | Acceptance Criteria | Status |
| --- | --- | --- | --- |
| CZ-01 | Shopper filters catalog quickly | Category + price filters persist across pagination | Done |
| CZ-02 | Visitor registers with email verification | Email sent w/ HTTPS link, login blocked pre-verification | Done |
| CZ-03 | Authenticated shopper keeps guest cart | Duplicate items increment quantity, success toast shown | Done |
| CZ-04 | Reviewer edits/removes own feedback | Buttons scoped to owner, average rating refreshes | Done |
| CZ-05 | Store manager edits products from storefront | Guarded by staff decorator, flash messages on save/delete | Done |
| CZ-06 | Shopper completes Stripe checkout | Addresses validated, webhook updates order/payment | Done |
| CZ-07 | Marketer grows newsletter list | Duplicate opt-ins show friendly message, admin exportable | Done |
| CZ-08 | Search engine indexes site | `/sitemap.xml` + `/robots.txt` respond 200 with fresh URLs | Done |

### Ceremonies & Metrics

- **Sprints**: two-week cadence with planning → daily stand-ups → review → retro.
- **Definition of Done**: dev complete, tests written/passing, docs updated, deployed to staging, stakeholder sign-off.
- **Metrics**: velocity (story points), burndown charts, escaped defects, newsletter growth, conversion rate on checkout funnel.

## Social Media & Marketing Readiness

| Platform | Handle | Status | Content Focus |
| --- | --- | --- | --- |
| Facebook | [ComfyZone Official](https://facebook.com/comfyzone) | New (0 followers) | Product launches, live shopping |
| Instagram | [@comfyzone](https://instagram.com/comfyzone) | New | Lifestyle photography, Reels |
| Twitter/X | [@ShopComfyZone](https://twitter.com/ShopComfyZone) | New | Support, flash sales |
| LinkedIn | [ComfyZone](https://linkedin.com/company/comfyzone) | New | Company updates, hiring |
| YouTube | [ComfyZone TV](https://youtube.com/@comfyzone) | New | Product demos, styling tips |
| Pinterest | [ComfyZone](https://pinterest.com/comfyzone) | New | Mood boards, seasonal sets |

Newsletter growth happens through the footer CTA (double opt-in with consent logging) and high-intent shoppers can request concierge follow-up via [`/marketing/leads/new/`](marketing/urls.py). Staff review captured leads in the on-site dashboard or export subscribers straight from Django admin for CRM import.

Content cadence (example):

- **Mon** – Product highlight
- **Tue** – Customer testimonial / UGC
- **Wed** – Styling or care tips
- **Thu** – Behind-the-scenes / team spotlight
- **Fri** – Weekend inspiration bundle
- **Sat** – Influencer collaboration recap
- **Sun** – Community Q&A or poll

## Contributing

1. Fork and clone the repository.
2. Create a feature branch: `git checkout -b feature/amazing-feature`.
3. Install dependencies & run migrations locally.
4. Implement changes, add/extend tests, update docs.
5. Run `python manage.py check` and (optionally) `python manage.py test`.
6. Commit with a descriptive message and push.
7. Open a Pull Request referencing the related issue or user story.

Coding standards: PEP 8, descriptive docstrings, minimal inline comments for complex logic, and keep secrets in `.env`.

## License & Usage Rights

- The UI build is based on the Untree.co **Furni** template (Creative Commons). Credit the template when publishing.
- Add your preferred project license (`MIT`, `BSD`, etc.) before distributing binaries or hosting publicly.

## Support

- **Email**: [support@comfyzone.app](mailto:support@comfyzone.app)
- **Issues**: [GitHub Issues](https://github.com/<you>/ComfyZone/issues)
- **Discussions**: Enable GitHub Discussions for community Q&A.

## Acknowledgments

- Django & Python communities for the incredible tooling.
- Stripe for their developer-friendly payment APIs.
- Untree.co for the Furni visual language adapted here.
- Everyone contributing bug reports, ideas, or fixes.

---

**Made with ❤️ by the ComfyZone team.** Update this README whenever you add new features, APIs, or deployment targets so it remains your single source of truth.
