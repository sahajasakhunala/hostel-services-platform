# HostelFlow Installation Guide

Follow these steps to set up and run HostelFlow locally.

## 1. Clone the Repository
```bash
git clone https://github.com/sahajasakhunala/hostel-services-platform.git
cd hostel-services-platform
```

## 2. Set Up Virtual Environment
Create a clean virtual Python environment and install dependencies:
```bash
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
```

## 3. Configuration Setup
Copy `.env.example` to `.env` and fill in your local MySQL settings:
```bash
cp .env.example .env
```
Ensure your `.env` contains valid credentials:
```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-hostelflow-local-only

DB_HOST=localhost
DB_PORT=3306
DB_NAME=hostelflow_db
DB_USER=root
DB_PASSWORD=your_password
```

## 4. Run Verification & Start Flask
Run the full platform verification test suite to ensure setup is correct, then launch the Flask dev server:
```bash
# Verify setup
.\venv\Scripts\python tests/run_full_verification.py

# Launch server
python run.py
```
Open `http://localhost:5000` in your web browser.
