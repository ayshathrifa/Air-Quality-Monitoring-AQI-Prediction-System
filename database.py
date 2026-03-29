import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = 'data/air_quality.db'

def get_connection():
    os.makedirs('data', exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS air_quality (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                lat REAL, lon REAL,
                pm2_5 REAL, pm10 REAL, co REAL,
                no2 REAL, o3 REAL, so2 REAL,
                aqi INTEGER
            )
        ''')
        conn.commit()

def insert_record(data: dict):
    with get_connection() as conn:
        conn.execute('''
            INSERT INTO air_quality (timestamp, lat, lon, pm2_5, pm10, co, no2, o3, so2, aqi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            data.get('lat', 0), data.get('lon', 0),
            data['pm2_5'], data['pm10'], data['co'],
            data['no2'], data['o3'], data['so2'],
            data.get('aqi', 0)
        ))
        conn.commit()

def fetch_records(limit=50) -> list:
    with get_connection() as conn:
        df = pd.read_sql_query(
            'SELECT * FROM air_quality ORDER BY id DESC LIMIT ?', conn, params=(limit,)
        )
    return df.iloc[::-1].to_dict('records')

def fetch_all_df() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query('SELECT * FROM air_quality ORDER BY timestamp', conn)

def get_stats() -> dict:
    with get_connection() as conn:
        df = pd.read_sql_query('SELECT * FROM air_quality ORDER BY id DESC LIMIT 50', conn)
    if df.empty:
        return {'total_records': 0}
    return {
        'total_records': len(df),
        'avg_pm2_5': round(float(df['pm2_5'].mean()), 2),
        'avg_pm10': round(float(df['pm10'].mean()), 2),
        'avg_aqi': round(float(df['aqi'].mean()), 2),
        'max_pm2_5': round(float(df['pm2_5'].max()), 2),
        'min_pm2_5': round(float(df['pm2_5'].min()), 2),
    }

def seed_historical_data():
    """Seed 365 days of synthetic historical data with seasonal patterns if DB is empty."""
    with get_connection() as conn:
        count = conn.execute('SELECT COUNT(*) FROM air_quality').fetchone()[0]
    if count > 0:
        return

    import numpy as np
    np.random.seed(42)
    base_date = pd.Timestamp('2024-01-01')
    records = []

    for day in range(365):
        dt = base_date + pd.Timedelta(days=day)
        month = dt.month
        # Seasonal pattern: winter (Nov-Feb) worst, monsoon (Jul-Sep) best
        if month in [11, 12, 1, 2]:
            base_pm25 = np.random.uniform(80, 160)
        elif month in [7, 8, 9]:
            base_pm25 = np.random.uniform(15, 40)
        elif month in [3, 4, 5]:
            base_pm25 = np.random.uniform(50, 90)
        else:
            base_pm25 = np.random.uniform(40, 70)

        pm10 = base_pm25 * np.random.uniform(1.4, 1.8)
        co = base_pm25 * np.random.uniform(5, 8)
        no2 = base_pm25 * np.random.uniform(0.4, 0.7)
        o3 = np.random.uniform(40, 130)
        so2 = base_pm25 * np.random.uniform(0.1, 0.25)

        if base_pm25 <= 12: aqi = 1
        elif base_pm25 <= 35.4: aqi = 2
        elif base_pm25 <= 55.4: aqi = 3
        elif base_pm25 <= 150.4: aqi = 4
        else: aqi = 5

        records.append({
            'timestamp': dt.strftime('%Y-%m-%d 12:00:00'),
            'lat': 28.6139, 'lon': 77.2090,
            'pm2_5': round(base_pm25, 2), 'pm10': round(pm10, 2),
            'co': round(co, 2), 'no2': round(no2, 2),
            'o3': round(o3, 2), 'so2': round(so2, 2),
            'aqi': aqi
        })

    with get_connection() as conn:
        conn.executemany('''
            INSERT INTO air_quality (timestamp, lat, lon, pm2_5, pm10, co, no2, o3, so2, aqi)
            VALUES (:timestamp, :lat, :lon, :pm2_5, :pm10, :co, :no2, :o3, :so2, :aqi)
        ''', records)
        conn.commit()
    print(f"Seeded {len(records)} historical records into SQLite.")

init_db()
