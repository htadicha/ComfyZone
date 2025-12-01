# Django Furniture E-Commerce Store

A comprehensive Django e-commerce website for a furniture store with full shopping cart, order management, Stripe payments, user authentication, reviews, search, newsletter, and SEO features.

## Features

- **Product Catalog Management**: Categories, products, variations, multiple images, stock tracking
- **Shopping Cart**: Session-based for guests, user-based for authenticated users, cart merging on login
- **Order Management**: Complete order lifecycle, status tracking, email notifications
- **Stripe Payment Integration**: Secure payment processing with webhooks
- **User Authentication**: Email-based auth, email verification, user profiles, address management
- **Reviews & Ratings**: 5-star rating system with moderation
- **Search & Filtering**: Advanced search with category, price, and availability filters
- **Newsletter**: Subscription system with duplicate detection and admin export
- **SEO**: Auto-generated sitemap, robots.txt, meta descriptions
- **Responsive Design**: Bootstrap 5, mobile-first approach

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- PostgreSQL
- Virtual environment (recommended)

### 2. Installation

```bash
# Clone or navigate to the project directory
cd Furniture_store

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE furniture_store;
CREATE USER your_db_user WITH PASSWORD 'your_password';
ALTER ROLE your_db_user SET client_encoding TO 'utf8';
ALTER ROLE your_db_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_db_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE furniture_store TO your_db_user;
```

### 4. Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=furniture_store
DB_USER=your_db_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

SITE_URL=http://localhost:8000
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Collect Static Files

```bash
python manage.py collectstatic
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to see the site.

## Project Structure

```
furniture_store/
├── accounts/          # User authentication and profiles
├── store/            # Product catalog
├── cart/             # Shopping cart
├── orders/           # Order management
├── payments/         # Stripe payment integration
├── reviews/          # Product reviews and ratings
├── marketing/        # Newsletter subscriptions
├── core/             # Base templates, utilities, sitemaps
├── templates/        # Django templates
├── static/           # Static files (CSS, JS, images)
└── media/            # User uploaded files
```

## Key URLs

- Home: `/`
- Shop: `/shop/`
- Cart: `/cart/`
- Checkout: `/payments/checkout/`
- Admin: `/admin/`
- Login: `/accounts/login/`
- Register: `/accounts/register/`

## Testing the Features

1. **User Registration**: Register a new user, check email for verification link
2. **Product Browsing**: Browse products, use search and filters
3. **Shopping Cart**: Add products to cart (works for guests and authenticated users)
4. **Checkout**: Complete checkout with Stripe test cards
5. **Reviews**: Write and edit product reviews
6. **Newsletter**: Subscribe to newsletter from footer

## Stripe Test Cards

- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Use any future expiry date and any CVC

## Notes

- Make sure PostgreSQL is running before running migrations
- Configure email settings for email verification to work
- Set up Stripe webhook endpoint for production
- Use environment variables for all sensitive data
- Run `collectstatic` after any static file changes

## License

This project uses the Furni template by Untree.co (Creative Commons License).


