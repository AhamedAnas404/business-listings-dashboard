# START HERE (Windows 11) 🚀

This is your **LocalLens Business Listings Dashboard** internship project.

It contains:
- `frontend/` — React dashboard with charts and search
- `backend/` — Python FastAPI connected to MySQL
- `collector/` — fetches real businesses from OpenStreetMap through the Overpass API
- `data/sample_listings_600.csv` — **600 fictional demo rows, NOT scraped businesses**
- `sql/` — MySQL database schema and a demo-only sample dump
- `docs/` — 3–5 minute video guide and submission checklist

## 1. Install software (one time)

Install **Python 3.11 or newer**, **Node.js 20 or newer**, and **Docker Desktop** (for MySQL). If you already have MySQL 8 installed, you can use that instead. You also need VS Code or any code editor.

## 2. Unzip the project and open the folder

In Windows File Explorer: right-click the ZIP > **Extract All**. Open the extracted `business-listings-dashboard` folder in VS Code. In VS Code, select **Terminal > New Terminal**. This should open PowerShell.

**Important:** Commands below must be run in the right folder. A new terminal in VS Code normally starts at the project root.

## 3. Start MySQL (first PowerShell terminal, project root)

If you installed Docker Desktop, open it and wait until the engine has started. Run:

```powershell
docker compose up -d
```

If using your own MySQL server instead of Docker, create database `business_dashboard` and change the MySQL login/port in `backend/.env` after step 4. See `README.md`.

## 4. Start Python API (second PowerShell terminal)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Keep this terminal open. In a browser, visit **http://127.0.0.1:8000/docs**. You should see the API page.

## 5. Add 600 DEMO rows (third PowerShell terminal, project root)

```powershell
.\backend\.venv\Scripts\python.exe scripts\import_csv.py --file data\sample_listings_600.csv
```

It should say it added 600 rows if the database was empty. These are fictional entries used ONLY for testing.

## 6. Start dashboard (fourth PowerShell terminal)

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open **http://localhost:5173**. You should see charts and a business table.

## 7. Collect REAL listings (needed to claim a real scrape)

After the API is running, open a new terminal **at the project root** and run:

```powershell
.\backend\.venv\Scripts\python.exe collector\collect_osm.py --email YOUR_REAL_EMAIL --target 500
.\backend\.venv\Scripts\python.exe scripts\import_csv.py --file data\osm_listings.csv
```

Replace `YOUR_REAL_EMAIL` with your email to identify requests to the public Overpass API. **Do not upload or share any passwords.** The script prints the actual number collected, which might be below 500 if the service is unavailable or the public dataset is incomplete. Be honest about that number. Do not pretend the fictional rows are real. After getting enough real records, optionally remove demo rows using `scripts/remove_samples.py`.

## 8. Check your results and submit

Make sure:
- The dashboard, charts, filters and API work on **your computer**.
- Your MySQL database contains the claimed number of **real** records.
- You export the **actual** MySQL database to `database_dump.sql`.
- You upload the project to GitHub, including both `frontend/` and `backend/`.
- You record your own 3–5 minute demonstration video.
- You add the GitHub and video links to your submission.

Read `docs/submission_checklist.md` and `docs/demo_video_script.md` for help.

**Current status of this ZIP:** Project source files and fictional demo data are prepared. Python unit tests and structure checks passed. A complete MySQL/React end-to-end test, real 500+ listing collection, GitHub upload and actual demo video have **not** been completed.
