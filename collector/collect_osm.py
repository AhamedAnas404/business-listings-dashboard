"""Collect publicly listed businesses through OpenStreetMap's Overpass API.

This is compliant API-based extraction, not HTML scraping. Public endpoints have
rate limits. Request one area at a time. Never claim these are Google/Justdial data.

Example: python collector/collect_osm.py --email you@example.com --target 500
"""

import argparse
import csv
import json
import time
from pathlib import Path

import requests

# South, West, North, East. Areas are modest and collected sequentially.
CITY_BBOX = {
    'Chennai': (12.92, 80.12, 13.15, 80.31),
    'Bengaluru': (12.90, 77.53, 13.06, 77.69),
    'Hyderabad': (17.35, 78.40, 17.51, 78.56),
    'Coimbatore': (10.96, 76.91, 11.07, 77.05),
    'Madurai': (9.89, 78.09, 9.96, 78.16),
    'Tiruchirappalli': (10.78, 78.65, 10.85, 78.73),
}
ENDPOINT = 'https://overpass-api.de/api/interpreter'
COLUMNS = [
    'business_name', 'category', 'city', 'address', 'phone', 'source',
    'source_ref', 'data_origin'
]


def make_query(bbox):
    area = ','.join(str(x) for x in bbox)
    return f"""[out:json][timeout:55];
(
  nwr["name"]["shop"]({area});
  nwr["name"]["office"]({area});
  nwr["name"]["amenity"~"restaurant|cafe|fast_food|bank|pharmacy|clinic|hospital|fuel|marketplace|school|dentist|doctors"]({area});
);
out center 2500;"""


def parse_elements(elements, city):
    output = []
    seen = set()
    for element in elements:
        tags = element.get('tags') or {}
        name = str(tags.get('name') or '').strip()
        if not name:
            continue
        obj_type = element.get('type')
        obj_id = element.get('id')
        if obj_type not in ('node', 'way', 'relation') or not isinstance(obj_id, int):
            continue
        reference = f'osm:{obj_type}:{obj_id}'
        if reference in seen:
            continue
        seen.add(reference)
        category_type = next((key for key in ('shop', 'amenity', 'office') if key in tags), 'business')
        category = str(tags.get(category_type) or 'business').replace('_',' ').title()
        parts = [
            tags.get('addr:housenumber'), tags.get('addr:street'),
            tags.get('addr:suburb'), tags.get('addr:postcode')
        ]
        address = str(tags.get('addr:full') or '').strip() or ', '.join(
            str(x).strip() for x in parts if x
        )
        if not address:
            # Avoid fabricating an address when only coordinates are available.
            center = element.get('center') or element
            lat, lon = center.get('lat'), center.get('lon')
            if isinstance(lat, (int, float)) and isinstance(lon, (int,float)):
                address = f'Coordinates: {lat:.5f}, {lon:.5f} (street address unavailable)'
            else:
                address = 'Street address unavailable'
        phone = str(tags.get('contact:phone') or tags.get('phone') or '').strip() or None
        output.append({
            'business_name': name[:255], 'category': category[:100], 'city': city,
            'address': address[:1000], 'phone': phone[:100] if phone else '',
            'source': 'OpenStreetMap', 'source_ref': reference, 'data_origin': 'real',
        })
    return output


def fetch_city(city, email, session):
    headers = {'User-Agent': f'LocalLensInternProject/1.0 (contact: {email})'}
    query = make_query(CITY_BBOX[city])
    for attempt in range(2):
        try:
            response = session.post(ENDPOINT, data={'data': query}, headers=headers, timeout=85)
            if response.status_code in (429, 502, 503, 504):
                if attempt == 0:
                    print(f'{city}: server busy ({response.status_code}). Cooling down 30 seconds...')
                    time.sleep(30)
                    continue
                response.raise_for_status()
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict) or 'elements' not in data:
                raise ValueError('Unexpected Overpass response')
            return parse_elements(data['elements'], city)
        except (requests.RequestException, ValueError) as exc:
            if attempt == 0:
                print(f'{city}: request failed ({exc}). Trying once more after a pause...')
                time.sleep(8)
            else:
                print(f'{city}: skipped due to error: {exc}')
    return []


def collect(email, target, path):
    output = []
    seen = set()
    with requests.Session() as session:
        for city in CITY_BBOX:
            print('Requesting:', city)
            batch = fetch_city(city, email, session)
            for row in batch:
                if row['source_ref'] not in seen:
                    seen.add(row['source_ref'])
                    output.append(row)
            print(f'{city}: {len(batch)} fetched; {len(output)} total unique records')
            if len(output) >= target:
                break
            # Be respectful of public infrastructure.
            time.sleep(10)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(output)
    print(f'Wrote {len(output)} REAL OpenStreetMap listings to {path}')
    if len(output) < target:
        print(f'WARNING: Target {target} not met. Retry later or add permissioned sources; never mislabel sample data.')
    print('Attribution: © OpenStreetMap contributors (ODbL)')
    return len(output)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Collect real business listings from Overpass API')
    p.add_argument('--email', required=True, help='Real contact email for request User-Agent')
    p.add_argument('--target', type=int, default=500)
    p.add_argument('--output', default='data/osm_listings.csv')
    args = p.parse_args()
    if args.target <= 0:
        p.error('--target must be positive')
    collect(args.email, args.target, Path(args.output))
