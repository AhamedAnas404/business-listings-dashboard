"""Import a CSV to the FastAPI bulk endpoint in safe batches.
Example: python scripts/import_csv.py --file data/osm_listings.csv
"""
import argparse
import csv
from pathlib import Path
import requests


def chunks(items, size=100):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='CSV exported by collector or sample generator')
    parser.add_argument('--api', default='http://127.0.0.1:8000')
    args = parser.parse_args()
    with Path(args.file).open('r', encoding='utf-8-sig', newline='') as file:
        records = list(csv.DictReader(file))
    if not records:
        raise SystemExit('CSV is empty. No rows imported.')
    if 'data_origin' not in records[0]:
        raise SystemExit('Missing data_origin field. Do not import unlabelled records.')
    total_added = 0
    for batch in chunks(records):
        response = requests.post(
            f"{args.api.rstrip('/')}/api/listings/bulk",
            json={'listings': batch}, timeout=90
        )
        if not response.ok:
            raise SystemExit(f'Import failed ({response.status_code}): {response.text[:500]}')
        result = response.json()
        total_added += result['inserted']
        print(f"Processed {result['received']}; new: {result['inserted']}; duplicates: {result['duplicates']}")
    print(f'Finished. {total_added} new records added. Check {args.api}/api/stats')


if __name__ == '__main__':
    main()
