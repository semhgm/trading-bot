import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "trading.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Kullanıcı tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Trade geçmişi tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            price REAL NOT NULL,
            quantity REAL NOT NULL,
            pnl REAL DEFAULT 0,
            commission REAL DEFAULT 0,
            mode TEXT DEFAULT 'simulation',
            reason TEXT DEFAULT 'SIGNAL',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Bot session tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            mode TEXT DEFAULT 'simulation',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            stopped_at TIMESTAMP,
            total_trades INTEGER DEFAULT 0,
            total_pnl REAL DEFAULT 0,
            total_commission REAL DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()
    print("[DB] Tablolar hazır")