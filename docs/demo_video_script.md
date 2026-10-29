# Demo video script (3–5 minutes)

Record your actual running application with Windows Snipping Tool screen recording, Clipchamp, or OBS.
**Do not claim a live collector run if only sample data has been imported.**

## 0:00–0:30 — Introduction
"Hello, I am Ahamed Anas. This is LocalLens, my Business Listings Dashboard internship assignment. The frontend uses React, the backend uses FastAPI, and data is stored in MySQL."

## 0:30–1:30 — Data collection
Open `collector/collect_osm.py` and the generated CSV in VS Code. Explain that publicly available OpenStreetMap listings are fetched with the Overpass API; the program extracts name, category, city, address, phone when provided, and source. Show `source_ref` for de-duplication. Mention addresses or phones may be missing.

If you used sample data, SAY: "For this run I used the clearly labeled fictional 600-record backup, because the data source was unavailable. The real collection script is included and documented."

## 1:30–2:20 — Backend APIs
Go to `http://127.0.0.1:8000/docs`. Open `/api/stats`, `/api/listings` and `/api/health`. Show the bulk insert endpoint with real imported rows or sample rows as appropriate.

## 2:20–3:35 — React dashboard
Show total listings, cities, categories and phone coverage. Explain the city bar chart, category donut chart, source breakdown, live MySQL data, business table, filters, and sample-versus-real labels.

## 3:35–4:20 — MySQL database
Open MySQL Workbench (or terminal). Run `SELECT COUNT(*) FROM listing_master;` and show schema. Explain the primary key and unique source reference.

## 4:20–5:00 — Code + conclusion
Show `frontend` and `backend` folders, README, SQL dump, and Github repository (after you upload it). Briefly mention a challenge, like rate limits or incomplete phone fields, and how you handled it. Finish by saying thank you.

### Video tips
- Record 1080p if possible and keep the browser text readable.
- Start the FastAPI server, MySQL, and React app BEFORE recording.
- Show the *real* output; don't present the sample data as scraped data.
- Share an accessible video link with the recruiter, or include it in the submission folder.
