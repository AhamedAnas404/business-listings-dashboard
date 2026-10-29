import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from collector.collect_osm import make_query, parse_elements
from collector.generate_sample import make_samples


def test_osm_parser_preserves_missing_phone_and_real_identity():
    elements = [
        {'type':'node', 'id':42,'lat':13.02,'lon':80.23,
         'tags':{'name':'Test Bakery','shop':'bakery', 'addr:street':'Test Street'}},
        {'type':'node', 'id':42,'lat':13.02,'lon':80.23,
         'tags':{'name':'Test Bakery','shop':'bakery'}},
        {'type':'way', 'id':43,'center':{'lat':13.02,'lon':80.21},
         'tags':{'name':'Test Restaurant','amenity':'restaurant','contact:phone':'+91 000-0000'}},
        {'type':'node', 'id':44,'tags':{'shop':'kiosk'}},
    ]
    rows = parse_elements(elements, 'Chennai')
    assert len(rows) == 2
    assert rows[0]['business_name'] == 'Test Bakery'
    assert rows[0]['phone'] == ''
    assert rows[0]['source_ref'] == 'osm:node:42'
    assert rows[0]['data_origin'] == 'real'
    assert rows[1]['category'] == 'Restaurant'
    assert 'Coordinates:' in rows[1]['address']


def test_sample_records_are_clearly_marked():
    rows = make_samples()
    assert len(rows) == 600
    assert len({r['source_ref'] for r in rows}) == 600
    assert all(r['data_origin'] == 'sample' and r['source'] == 'Sample dataset' for r in rows)
    assert all('fictional' in r['business_name'] for r in rows)
    assert all(not r['phone'] for r in rows)


def test_query_is_bounded():
    q = make_query((12.92,80.12,13.15,80.31))
    assert 'nwr["name"]' in q
    assert 'out center 2500' in q
