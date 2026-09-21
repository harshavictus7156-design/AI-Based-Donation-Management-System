# Local Development Setup

These instructions describe the current local configuration for Windows PowerShell. The backend expects PostgreSQL and the frontend calls the backend at `http://127.0.0.1:8000/api/`.

## Prerequisites

Install the following before starting:

- Git
- Python compatible with the pinned Django and scientific-computing dependencies
- Node.js and npm
- PostgreSQL

## 1. Clone the repository

```powershell
git clone <repository-url>
cd AI-Donation-System
```

Replace `<repository-url>` with the repository's actual clone URL.

## 2. Create and activate the backend environment

```powershell
cd Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, use the Python interpreter directly or adjust the local execution policy according to your organization's policy. Do not commit the virtual environment.

## 3. Install Python dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The requirements include Django, Django REST Framework, JWT support, PostgreSQL connectivity, Pillow, and the computer-vision/scientific packages used by the repository. The AI modules also import `google-genai` and `python-dotenv`; verify that these packages are available in the environment before using image analysis, because their package names are not explicitly pinned in the checked-in requirements file.

## 4. Configure PostgreSQL

Create a PostgreSQL database named `donation_db` and use a PostgreSQL user that can access it. The active `Backend/donation_system/settings.py` expects:

| Setting | Current value |
| --- | --- |
| Engine | PostgreSQL |
| Database | `donation_db` |
| User | `postgres` |
| Host | `localhost` |
| Port | `5432` |
| Password | Read from `DB_PASSWORD` |

The repository also contains `Backend/config/settings.py`, but `Backend/manage.py` selects `donation_system.settings`; the latter is the active configuration for the commands below.

## 5. Configure environment variables

Create `Backend/.env` yourself. Never copy real credentials into documentation or commit them.

```dotenv
DB_PASSWORD=your_postgresql_password
GEMINI_API_KEY=your_gemini_api_key
```

`DB_PASSWORD` must be available to Django as a process environment variable. In PowerShell, set it for the current session with:

```powershell
$env:DB_PASSWORD = "your_postgresql_password"
```

The Gemini modules load `GEMINI_API_KEY` from `Backend/.env`. Keep the file private. The frontend currently uses a fixed local API base URL in `frontend/src/services/api.js`; no frontend environment variable is required by the current implementation.

## 6. Run migrations

From `Backend` with the virtual environment active:

```powershell
python manage.py check
python manage.py migrate
```

Create an administrative account only if needed for the local project and only through the existing Django management workflow:

```powershell
python manage.py createsuperuser
```

## 7. Start Django

```powershell
python manage.py runserver
```

The API is then available at `http://127.0.0.1:8000/api/`. Django admin is at `http://127.0.0.1:8000/admin/`.

## 8. Install frontend dependencies

Open a second PowerShell window:

```powershell
cd AI-Donation-System\frontend
npm install
```

## 9. Start Vite

```powershell
npm run dev
```

Vite normally serves the frontend at `http://localhost:5173`. The Django CORS configuration allows both `http://localhost:5173` and `http://127.0.0.1:5173`.

## Useful checks

```powershell
# Backend
cd AI-Donation-System\Backend
.\.venv\Scripts\Activate.ps1
python manage.py check

# Frontend
cd ..\frontend
npm run lint
npm run build
```

The application is configured for local development (`DEBUG = True`). Review deployment, secret management, allowed hosts, static files, media storage, and database settings before using it in production.
