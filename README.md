# Skin & Hair Care Clinic — Website

A production-ready dynamic website for a professional Skin & Hair Care Clinic, built with Django and Bootstrap 5.

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3.10+, Django 4.2          |
| Database  | PostgreSQL (prod), SQLite (dev)   |
| Frontend  | HTML5, CSS3, JS, Bootstrap 5      |
| Server    | Gunicorn + WhiteNoise             |

## Project Structure

```
Skincare/
├── manage.py
├── skincare_clinic/      # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                 # Homepage, contact, about
├── treatments/           # Treatment categories & details
├── doctors/              # Doctor profiles
├── appointments/         # Appointment booking
├── blog/                 # Blog / articles
├── gallery/              # Before/after gallery
├── templates/            # Global templates
│   ├── base.html
│   └── partials/
├── static/               # CSS, JS, images
└── media/                # User-uploaded files
```

## Quick Start

### 1. Clone & Setup Virtual Environment
```bash
git clone <repo-url>
cd Skincare
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
copy .env.example .env       # Windows
cp .env.example .env         # macOS/Linux
```
Edit `.env` with your settings.

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)
Admin: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

## Environment Variables

See `.env.example` for all configurable variables.

## License

Private — All rights reserved.
