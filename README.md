# LocalLens — Business Listings Dashboard

**Python Development Intern technical assignment | React + FastAPI + MySQL**

LocalLens collects publicly available OpenStreetMap business listings using the Overpass API, stores them in MySQL, and displays aggregate reports in a responsive React dashboard. It also ships with **600 clearly fictional sample rows** so the UI can be tested without internet access. Sample rows must never be described as scraped data.

## Main features

- **Data collection:** Permission-friendly OpenStreetMap Overpass API requests, sequential requests, error handling, and source IDs to prevent duplicates.
- **Fields:** business name, category, city, address, phone if published, source.
- **Database:** MySQL `listing_master` table with ID, timestamp, `source_ref`, and real/sample origin columns.
- **FastAPI:** `POST /api/listings/bulk`, `GET /api/stats`, `GET /api/listings`, `GET /api/health`, auto docs at `/docs`.
- **React:** total KPI cards, city bar chart, category donut chart, source progress bars, search, filters, pagination, CSV export, phone coverage, real/sample warning.
- **Safety:** honest data labeling, no CAPTCHA bypass, no fabricated phone numbers, no scraped personal details, OpenStreetMap attribution.

## Folder layout

```text
business-listings-dashboard/
  backend/
    app/                    # FastAPI, SQLAlchemy models and schemas
    tests/                  # Data collector unit tests
    requirements.txt
    .env.example
  frontend/
    src/                    # React and dashboard CSS
    package.json
    .env.example
  collector/
    collect_osm.py          # REAL data via public Overpass API
    generate_sample.py      # Fictional data for demo/testing ONLY
  data/
    sample_listings_600.csv # 600 fictional rows, ready to import
  scripts/
    import_csv.py
    remove_samples.py
    validate_submission.py
  sql/
    schema.sql
    database_dump_sample.sql  # DEMO data, not an authentic scrape
  docs/
    demo_video_script.md
    submission_checklist.md
  docker-compose.yml
```

## Quick start on Windows 11 (PowerShell)

**Requirements:** Python 3.11+, Node.js 20+, npm, and MySQL 8. **Option A: Docker Desktop** runs MySQL for you. **Option B:** use an existing local MySQL server instead.

### Step 1 — Start MySQL

From the project folder, if Docker Desktop is installed and running:

```powershell
docker compose up -d
```

This launches MySQL on localhost port `3307`. The user/database/password in `docker-compose.yml` are **development only**. If using MySQL already installed on your laptop instead, create a database named `business_dashboard` in MySQL Workbench and edit `backend/.env` for your correct user, password and port (normally 3306). The API will create the table on its first start.

### Step 2 — Start the FastAPI backend

Open a PowerShell terminal **inside this project's `backend` folder**:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Leave this terminal open. Check these in your browser:

- API health: <http://127.0.0.1:8000/api/health>
- Interactive API docs: <http://127.0.0.1:8000/docs>

If the server cannot connect to MySQL, confirm Docker is running or your `DATABASE_URL` matches your own MySQL installation.

### Step 3 — Import sample data (offline, fictional)

Open a **second** PowerShell terminal in the **project root**:

```powershell
.\backend\.venv\Scripts\python.exe scripts\import_csv.py --file data\sample_listings_600.csv
```

It should report **600 new records** on the first run. Repeating the command reports duplicates instead of inserting copies.

### Step 4 — Start the React frontend

Open a **third** PowerShell terminal in the project's `frontend` folder:

```powershell
Copy-Item .env.example .env
npm install
npm run dev
```

Open <http://localhost:5173> to see the interactive dashboard. If counts don't appear, check API health and click **Refresh**.

## Collect and import 500+ REAL listings

Run the following from the **project root** after your backend is online. Use an email address you control, which identifies your project to the public Overpass server. Requests are sequential and rate-limited.

```powershell
.\backend\.venv\Scripts\python.exe collector\collect_osm.py --email you@example.com --target 500
.\backend\.venv\Scripts\python.exe scripts\import_csv.py --file data\osm_listings.csv
```

The collector checks a limited number of city areas, saves real records to `data/osm_listings.csv`, and prints the exact record count. **Only treat the requirement as met once you have actually collected and imported at least 500 real rows.** The public Overpass server can be slow, unavailable, or return fewer than 500. There is no guarantee of 500 in every run. Don't repeatedly hammer the public endpoint. If real collection fails, describe the sample-data fallback honestly as permitted by the assignment.

You can remove fictional rows after importing real listings:

```powershell
.\backend\.venv\Scripts\python.exe scripts\remove_samples.py
```

This asks for an explicit confirmation and removes sample rows only. Verify after importing:

```sql
SELECT COUNT(*) AS all_records FROM listing_master;
SELECT COUNT(*) AS actual_real_records FROM listing_master WHERE data_origin = 'real';
SELECT city, COUNT(*) AS count FROM listing_master GROUP BY city ORDER BY count DESC;
```

## API reference

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/health` | MySQL connection check |
| POST | `/api/listings/bulk` | Insert 1–5,000 listings, skip duplicate `source_ref` IDs |
| GET | `/api/stats` | Total, real/sample totals, phone availability, groupings |
| GET | `/api/listings` | Filtered and paginated listings |
| GET | `/docs` | Auto-generated FastAPI documentation |

Example POST body:

```json
{
  "listings": [
    {
      "business_name": "Example Store (illustration only)",
      "category": "Grocery",
      "city": "Chennai",
      "address": "Example address (illustration only)",
      "phone": null,
      "source": "Sample dataset",
      "source_ref": "sample:manual:1",
      "data_origin": "sample"
    }
  ]
}
```

## Database dump

- `sql/schema.sql` defines the MySQL database and table.
- `sql/database_dump_sample.sql` has 600 **fictional** records for practice only.
- **To submit a genuine database dump of what you actually imported**, use MySQL Workbench > Server > Data Export > select `business_dashboard` > Export to Self-Contained File > name it `database_dump.sql`. Keep this file in the repository/submission folder. See `docs/submission_checklist.md` for a Docker command too.

## Testing

From the project root, after installing backend dependencies:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend\tests -q
.\backend\.venv\Scripts\python.exe scripts\validate_submission.py
```

Test real API endpoints through `/docs`; those require the running MySQL server. Check frontend at desktop and mobile widths. If you update data, click **Refresh**.

## Challenges and solutions

1. **Scraping terms and rate limits:** Some directories block scraping. Use the official Overpass API with small region queries, polite delays and proper attribution, rather than circumventing protections. This is API-based data collection rather than raw HTML scraping.
2. **Incomplete data:** Phone and full postal address may be missing from OSM. Store an empty phone field and an honest address fallback instead of making up values.
3. **Duplicates:** OSM has stable object IDs. `source_ref` has a MySQL unique constraint and imports use `INSERT IGNORE`.
4. **Offline development:** A separately labeled sample dataset allows testing. The dashboard shows a warning while sample records are present.
5. **Frontend integration:** React fetches aggregated counts directly from FastAPI rather than using hardcoded chart data.

## Licensing and source notes

Data from OpenStreetMap is © OpenStreetMap contributors, licensed under the Open Database License (ODbL). Respect attribution, share-alike requirements for derivatives, and the Overpass endpoint's usage limits. See <https://www.openstreetmap.org/copyright> and <https://wiki.openstreetmap.org/wiki/Overpass_API>.

**Not claimed:** A real scraper run or 500+ real businesses, a deployed frontend, a GitHub repository, or a demo video. These require running the code and taking the final submission steps.

## Publishing on GitHub

Create an empty GitHub repository called `business-listings-dashboard`. In the project root:

```powershell
git init
git add .
git commit -m "Build business listings dashboard with React FastAPI and MySQL"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/business-listings-dashboard.git
git push -u origin main
```

Double-check the repository has both `frontend` and `backend`, and **never upload** local `.env` or credentials. Record the 3–5 minute demo after checking the running app using `docs/demo_video_script.md`.
