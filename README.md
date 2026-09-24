# 🤝 SmartDonate AI — Intelligent Donation Management System

An AI-powered donation management and resource matching platform deployed entirely as a single unified **Streamlit** application. 

SmartDonate AI seamlessly connects community donors with verified non-profit organizations (NGOs) and platform administrators through Google Gemini Vision image scanning, intelligent priority matching, allocation tracking, and doorstep pickup coordination.

---

## 🌟 Highlights & Features

- **One Single Deployable App**: Built 100% in Python and Streamlit. Requires zero Node.js / Vercel / Render dependencies.
- **AI-Powered Image Analysis**: Upload a photo of donation items and let Google Gemini AI automatically detect item names, categories, and estimated quantities.
- **Intelligent Resource Matching Engine**: Algorithmically scores and matches donations against active, urgent requirements of approved NGOs (weighted by Priority: High > Medium > Low > Urgent, plus quantity compatibility).
- **Multi-Role Workspaces**:
  - **👤 Donor Workspace**: Submit item donations with AI image analysis, view matching NGOs, allocate items, schedule/cancel doorstep pickups, track status (Pending, Accepted, Rejected, Collected), view community leaderboard ranking, notifications, and profile.
  - **🏢 NGO Workspace**: Publish and manage active resource requirements with fulfillment progress tracking, review incoming allocations (Accept / Reject with reason), coordinate pickups (Confirmed, Dispatched, Delivered), update organization credentials, and view impact analytics.
  - **🛡️ Administrator Workspace**: Review and approve/reject NGO registrations, toggle donor active status, oversee platform-wide donations, requirements, allocations, and pickups, and monitor system health.
- **Interactive Analytics**: Real-time Plotly charts for resource category distributions, status funnels, and contribution trends.
- **In-App Notifications**: Real-time workflow notifications across all donor and NGO events.
- **Leaderboard & Badges**: Community donor leaderboard with points calculation and tier badges (Champion Gold, Master Silver, Leader Bronze, Top Philanthropist).

---

## 🏗️ Architecture

```text
AI-Based-Donation-Management-System-main/
│
├── app.py                          # Main Streamlit Application Entrypoint
│
├── src/
│   ├── config.py                   # Secrets loader (st.secrets & env vars)
│   ├── database.py                 # ORM initialization & connection layer
│   ├── auth.py                     # Authentication & PBKDF2 password hashing
│   ├── models.py                   # Data models re-export
│   ├── utils.py                    # Badges, formatting helpers, file handlers
│   │
│   ├── services/                   # Python Business Logic Layer
│   │   ├── ai_service.py           # Gemini Vision & AI matching algorithm
│   │   ├── donation_service.py     # Donation CRUD, allocations, and pickups
│   │   ├── donor_service.py        # Donor profile, stats, and leaderboard
│   │   ├── ngo_service.py          # NGO registration, requirements, approvals
│   │   ├── admin_service.py        # Platform oversight & admin statistics
│   │   └── notification_service.py # In-app notification creation and reads
│   │
│   ├── components/                 # Reusable UI Components
│   │   ├── navbar.py               # Header & role navigation
│   │   ├── cards.py                # Metric KPI cards & donation/NGO cards
│   │   ├── charts.py               # Plotly interactive charts
│   │   └── notifications_drawer.py # Notifications center view
│   │
│   └── views/                      # Modular Page Views
│       ├── home.py                 # Public landing page with impact stats
│       ├── auth_views.py           # Multi-role Login & Registrations
│       ├── donor_views.py          # Complete Donor Workspace
│       ├── ngo_views.py            # Complete NGO Workspace
│       └── admin_views.py          # Complete Administrator Workspace
│
├── assets/
│   └── styles.css                  # Custom modern CSS styling
│
├── .streamlit/
│   └── config.toml                 # Streamlit server & theme configuration
│
├── requirements.txt                # Production dependencies
├── .gitignore                      # Git ignore rules
└── README.md                       # Documentation & Deployment guide
```

---

## 🚀 Local Setup & Running

### 1. Clone & Navigate to Repository
```bash
git clone https://github.com/your-username/AI-Based-Donation-Management-System.git
cd AI-Based-Donation-Management-System
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Streamlit Community Cloud Deployment

Deploying the application to **Streamlit Community Cloud** takes under 2 minutes:

1. Push your repository to **GitHub**.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in.
3. Click **"New app"**.
4. Select your **Repository**, **Branch**, and set the **Main file path** to:
   ```text
   app.py
   ```
5. Click **"Advanced settings..."** -> **"Secrets"**.
6. Paste your required secrets (see template below) and click **"Save"**.
7. Click **"Deploy!"**.

---

## 🔒 Streamlit Secrets Configuration

Configure the following secrets in your Streamlit Cloud dashboard under **App Settings → Secrets** (or locally in `.streamlit/secrets.toml`):

```toml
# =========================================================
# SMARTDONATE AI — STREAMLIT SECRETS CONFIGURATION
# =========================================================

# Google Gemini API Key for AI Image Analysis (Optional: Fallback heuristic used if omitted)
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

# Administrator Account Credentials
ADMIN_EMAIL = "admin@donation.org"
ADMIN_PASSWORD = "YOUR_SECURE_ADMIN_PASSWORD"

# Secret Key for Security
SECRET_KEY = "YOUR_CUSTOM_APP_SECRET_KEY"

# Database Configuration (Optional: SQLite is used by default if omitted)
# For PostgreSQL (e.g. Supabase, Neon, AWS RDS, ElephantSQL):
# DB_ENGINE = "postgresql"
# DB_NAME = "donation_db"
# DB_USER = "postgres"
# DB_PASSWORD = "YOUR_POSTGRES_PASSWORD"
# DB_HOST = "YOUR_DB_HOST"
# DB_PORT = "5432"
# Or provide a full connection string:
# DATABASE_URL = "postgresql://user:password@host:5432/dbname"
```

---

## 🔑 Default Administrator Credentials

When starting for the first time, you can log in as Admin using the configured credentials:
- **Email:** `admin@donation.org`
- **Password:** `admin123` *(or the value configured in `ADMIN_PASSWORD`)*
- **Role Selection:** `Administrator`