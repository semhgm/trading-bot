import os
import hashlib
import secrets
from datetime import datetime, timedelta
from database import get_db, init_db
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
TOKEN_EXPIRE_HOURS = 24

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(username: str) -> str:
    import jwt
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> str | None:
    import jwt
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except:
        return None

def login(username: str, password: str) -> str | None:
    conn = get_db()
    cursor = conn.cursor()
    user = cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password))
    ).fetchone()
    conn.close()
    if user:
        return create_token(username)
    return None

def create_default_user():
    """İlk kullanıcıyı .env'den oluştur"""
    init_db()
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    conn = get_db()
    cursor = conn.cursor()
    existing = cursor.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if not existing:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        print(f"[Auth] Varsayılan kullanıcı oluşturuldu: {username}")
    conn.close()