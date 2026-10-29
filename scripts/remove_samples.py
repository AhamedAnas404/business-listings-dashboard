"""Delete only demonstrably fictional sample data, without touching real records."""
import sys
from pathlib import Path
from sqlalchemy import delete, func, select

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from app.database import SessionLocal  # noqa: E402
from app.models import Listing  # noqa: E402


with SessionLocal() as db:
    count = db.scalar(select(func.count(Listing.id)).where(Listing.data_origin == 'sample')) or 0
    print(f'Sample rows to remove: {count}. Real rows will not be removed.')
    if count:
        answer = input('Type DELETE SAMPLE to confirm: ')
        if answer != 'DELETE SAMPLE':
            raise SystemExit('Cancelled, nothing deleted')
        db.execute(delete(Listing).where(Listing.data_origin == 'sample'))
        db.commit()
        print(f'Deleted {count} sample records.')
