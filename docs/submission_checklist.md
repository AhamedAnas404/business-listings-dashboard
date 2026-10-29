# Submission checklist

- [ ] Run the project locally and verify `/api/health` returns `database: connected`.
- [ ] Check 500+ rows in MySQL: `SELECT COUNT(*) FROM listing_master;`.
- [ ] **If claiming 500+ real listings**, verify `SELECT COUNT(*) FROM listing_master WHERE data_origin='real';` is at least 500. Sample rows never count as scraped.
- [ ] Check charts and listings table show data, including source/origin.
- [ ] Run `python -m pytest backend/tests -q`.
- [ ] Make a public or reviewer-accessible GitHub repo, with `/frontend` and `/backend`.
- [ ] Never commit `backend/.env`, DB passwords, API keys or any private details.
- [ ] Give README instructions for Windows 11, Docker or local MySQL.
- [ ] Include `sql/schema.sql` and an **actual** MySQL dump of the final database as `database_dump.sql`.
- [ ] Record an honest 3–5 minute demo video and upload to a shareable location.
- [ ] Share GitHub URL, video URL, README, database dump, and ZIP/PDF requested in the portal.
- [ ] Email `career@honeybeedigital.com` only after confirming the sender and portal are official.
- [ ] Submit before the portal's live countdown ends; email and portal deadline wording differ.

## Export your actual MySQL data
If MySQL runs in Docker, from the **project root** in PowerShell:

```powershell
docker compose exec -T mysql sh -c 'mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" business_dashboard' | Set-Content -Encoding utf8 database_dump.sql
```

This command is a suggested example; verify the output contains `CREATE TABLE` and `INSERT INTO` before submitting. Note PowerShell encoding and client versions can vary.

Alternatively, export the `business_dashboard` database through MySQL Workbench (Server > Data Export, Export to Self-Contained File).
