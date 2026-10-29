import hashlib
import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, text
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Listing
from .schemas import BulkInsert


@asynccontextmanager
async def lifespan(_: FastAPI):
    # This creates the table if the database exists. Docker creates the database.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title='Business Listings Dashboard API',
    version='1.0.0',
    description='FastAPI, MySQL, and a repeatable OpenStreetMap data pipeline.',
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in os.getenv(
        'ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173'
    ).split(',') if x.strip()],
    allow_credentials=False,
    allow_methods=['GET', 'POST'],
    allow_headers=['Content-Type'],
)
Db = Annotated[Session, Depends(get_db)]


def stable_reference(item: dict) -> str:
    """Consistent ID ensures re-importing the same CSV doesn't double count rows."""
    if item.get('source_ref'):
        return item['source_ref']
    value = '|'.join(str(item.get(k, '')).casefold() for k in (
        'source', 'business_name', 'city', 'address'
    ))
    return 'sha256:' + hashlib.sha256(value.encode('utf-8')).hexdigest()[:32]


def counts(db: Session, field):
    result = db.execute(
        select(field.label('name'), func.count(Listing.id).label('count'))
        .group_by(field)
        .order_by(func.count(Listing.id).desc(), field.asc())
    ).all()
    return [{'name': name, 'count': count} for name, count in result]


@app.get('/api/health')
def health(db: Db):
    try:
        db.execute(text('SELECT 1'))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail='Database is unavailable') from exc
    return {'status': 'ok', 'database': 'connected'}


@app.post('/api/listings/bulk', status_code=201)
def bulk_insert(payload: BulkInsert, db: Db):
    values = []
    for item in payload.listings:
        data = item.model_dump()
        data['source_ref'] = stable_reference(data)
        values.append(data)
    try:
        # MySQL INSERT IGNORE avoids a duplicate when this dataset is re-imported.
        stmt = mysql_insert(Listing).values(values).prefix_with('IGNORE')
        inserted = db.execute(stmt).rowcount
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail='Database insert failed') from exc
    return {'received': len(values), 'inserted': inserted, 'duplicates': len(values) - inserted}


@app.get('/api/stats')
def get_stats(db: Db):
    total = db.scalar(select(func.count(Listing.id))) or 0
    real = db.scalar(select(func.count(Listing.id)).where(Listing.data_origin == 'real')) or 0
    sample = db.scalar(select(func.count(Listing.id)).where(Listing.data_origin == 'sample')) or 0
    with_phone = db.scalar(select(func.count(Listing.id)).where(
        Listing.phone.is_not(None), Listing.phone != ''
    )) or 0
    return {
        'total': total,
        'real': real,
        'sample': sample,
        'with_phone': with_phone,
        'cities': counts(db, Listing.city),
        'categories': counts(db, Listing.category),
        'sources': counts(db, Listing.source),
    }


@app.get('/api/listings')
def list_listings(
    db: Db,
    search: str = Query(default='', max_length=100),
    city: str = Query(default='', max_length=100),
    category: str = Query(default='', max_length=100),
    source: str = Query(default='', max_length=100),
    origin: str = Query(default='', pattern=r'^(|real|sample)$'),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    clauses = []
    if search:
        clauses.append(Listing.business_name.contains(search, autoescape=True))
    if city:
        clauses.append(Listing.city == city)
    if category:
        clauses.append(Listing.category == category)
    if source:
        clauses.append(Listing.source == source)
    if origin:
        clauses.append(Listing.data_origin == origin)
    total = db.scalar(select(func.count(Listing.id)).where(*clauses)) or 0
    items = db.scalars(
        select(Listing).where(*clauses).order_by(Listing.id.desc())
        .offset(offset).limit(limit)
    ).all()
    return {
        'total': total,
        'offset': offset,
        'limit': limit,
        'items': [
            {
                'id': x.id,
                'business_name': x.business_name,
                'category': x.category,
                'city': x.city,
                'address': x.address,
                'phone': x.phone,
                'source': x.source,
                'data_origin': x.data_origin,
                'created_at': x.created_at.isoformat() if x.created_at else None,
            } for x in items
        ],
    }
