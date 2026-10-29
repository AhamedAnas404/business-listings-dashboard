"""Offline sanity check. Run from anywhere within the cloned project."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = [
    'backend/app/main.py', 'backend/app/models.py', 'backend/requirements.txt',
    'frontend/src/App.jsx', 'frontend/src/styles.css', 'frontend/package.json',
    'collector/collect_osm.py', 'collector/generate_sample.py',
    'sql/schema.sql', 'sql/database_dump_sample.sql', 'README.md',
    'docs/demo_video_script.md', 'data/sample_listings_600.csv'
]
missing = [item for item in required if not (ROOT / item).is_file()]
with (ROOT/'data/sample_listings_600.csv').open(encoding='utf-8-sig', newline='') as f:
    sample = list(csv.DictReader(f))
assert not missing, f'Missing files: {missing}'
assert len(sample) == 600, 'Sample should contain exactly 600 records'
assert all(x['data_origin']=='sample' for x in sample), 'Sample origin label missing'
assert len({x['source_ref'] for x in sample}) == 600, 'Duplicate IDs in sample'
print('PASS: expected project files exist')
print('PASS: 600 clearly marked sample records; no duplicates')
print('NEXT: run MySQL, FastAPI, and React. Collect real listings if available.')
