"""SQLite storage for LamGo destinations.

The database is created automatically at data/lamgo.db. Existing sample places
are imported once from places_data.py. Open the file with DB Browser for SQLite
to add/edit places in a spreadsheet-like table.
"""
from pathlib import Path
import shutil
import sqlite3
from .paths import user_data_path, user_data_dir

_BUNDLED_DB = Path(__file__).resolve().parent.parent / 'data' / 'lamgo.db'
DB_PATH = Path(user_data_path('lamgo.db', _BUNDLED_DB))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SCHEMA = '''
CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    district TEXT NOT NULL,
    category TEXT NOT NULL,
    rating REAL NOT NULL DEFAULT 0,
    reviews INTEGER NOT NULL DEFAULT 0,
    visit_time TEXT DEFAULT '',
    difficulty TEXT DEFAULT '',
    elevation TEXT DEFAULT '',
    weather TEXT DEFAULT '',
    best_time TEXT DEFAULT '',
    description TEXT DEFAULT '',
    latitude REAL,
    longitude REAL,
    image TEXT DEFAULT '',
    verified_coordinates INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_places_district ON places(district);
CREATE INDEX IF NOT EXISTS idx_places_category ON places(category);
'''


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create tables and import bundled sample places without overwriting edits."""
    from .places_data import PLACES as SAMPLE_PLACES
    with connect() as conn:
        conn.executescript(SCHEMA)
        for p in SAMPLE_PLACES:
            category = 'Mountains & Peaks' if p['type'] == 'Mountains' else p['type']
            conn.execute('''INSERT OR IGNORE INTO places
                (name, district, category, rating, reviews, visit_time, difficulty,
                 elevation, weather, best_time, description, image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (p['name'], p['location'], category, p['rating'], p['reviews'],
                 p['time'], p['difficulty'], p['elevation'], p['weather'],
                 p['best'], p['description'], p['name'].lower().replace(' ', '_')))
        # Keep the category labels consistent with LamGo's current browse filters.
        conn.execute("UPDATE places SET category='Mountains & Peaks', updated_at=CURRENT_TIMESTAMP WHERE category='Mountains'")


def get_places(district=None, category=None, search=None):
    """Return places as dictionaries matching the keys used by existing UI pages."""
    initialize_database()
    sql = 'SELECT * FROM places WHERE 1=1'
    params = []
    if district and district != 'All Districts':
        sql += ' AND lower(district)=lower(?)'
        params.append(district)
    if category and category != 'All Categories':
        sql += ' AND lower(category)=lower(?)'
        params.append(category)
    if search:
        sql += ' AND (name LIKE ? OR district LIKE ? OR category LIKE ? OR description LIKE ?)'
        term = f'%{search}%'
        params.extend([term, term, term, term])
    sql += ' ORDER BY rating DESC, name COLLATE NOCASE'
    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    results = []
    for row in rows:
        p = dict(row)
        # Compatibility keys keep the existing LamGo pages working.
        p.update(location=p['district'], type=p['category'], time=p['visit_time'], best=p['best_time'])
        results.append(p)
    return results


def add_or_update_place(name, district, category, rating=0, reviews=0,
                        visit_time='', difficulty='', elevation='', weather='',
                        best_time='', description='', latitude=None, longitude=None,
                        image='', verified_coordinates=False):
    """Insert or update a destination. Coordinates are optional decimal degrees."""
    if not name.strip() or not district.strip() or not category.strip():
        raise ValueError('Place name, district and category are required.')
    if (latitude is None) != (longitude is None):
        raise ValueError('Enter both latitude and longitude, or leave both empty.')
    if latitude is not None and not (-90 <= float(latitude) <= 90):
        raise ValueError('Latitude must be between -90 and 90.')
    if longitude is not None and not (-180 <= float(longitude) <= 180):
        raise ValueError('Longitude must be between -180 and 180.')
    with connect() as conn:
        conn.execute('''INSERT INTO places
            (name,district,category,rating,reviews,visit_time,difficulty,elevation,
             weather,best_time,description,latitude,longitude,image,verified_coordinates,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)
            ON CONFLICT(name) DO UPDATE SET district=excluded.district,
            category=excluded.category,rating=excluded.rating,reviews=excluded.reviews,
            visit_time=excluded.visit_time,difficulty=excluded.difficulty,
            elevation=excluded.elevation,weather=excluded.weather,best_time=excluded.best_time,
            description=excluded.description,latitude=excluded.latitude,
            longitude=excluded.longitude,image=excluded.image,
            verified_coordinates=excluded.verified_coordinates,updated_at=CURRENT_TIMESTAMP''',
            (name.strip(), district.strip(), category.strip(), float(rating), int(reviews),
             visit_time, difficulty, elevation, weather, best_time, description,
             latitude, longitude, image, int(bool(verified_coordinates))))


# Ensure a usable database exists as soon as this module is imported.
initialize_database()
