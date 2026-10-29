"""Deterministic, clearly fictional records for offline development."""
import csv
from pathlib import Path
from .collect_osm import COLUMNS

CITIES = ['Chennai', 'Bengaluru', 'Hyderabad', 'Coimbatore', 'Madurai', 'Tiruchirappalli']
CATEGORIES = [
    'Restaurant','Pharmacy','Grocery','Electronics','Hotel','Bookstore',
    'Healthcare','Clothing','Fitness','Salon','Education','Repair'
]


def make_samples(n=600):
    return [
        {
            'business_name': f'DEMO {CATEGORIES[i%len(CATEGORIES)]} {i+1:04d} (fictional)',
            'category': CATEGORIES[i%len(CATEGORIES)],
            'city': CITIES[(i//len(CATEGORIES))%len(CITIES)],
            'address': f'Fictional Test Road {i+1}, {CITIES[(i//len(CATEGORIES))%len(CITIES)]} (not a real address)',
            'phone': '',  # Never invent real-seeming public business phone numbers.
            'source': 'Sample dataset',
            'source_ref': f'sample:{i+1:05d}',
            'data_origin': 'sample',
        } for i in range(n)
    ]


def write_sample_csv(rows, path):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8-sig') as file:
        writer=csv.DictWriter(file,fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    write_sample_csv(make_samples(), Path('data/sample_listings_600.csv'))
    print('Created 600 clearly fictional sample records for offline testing')
