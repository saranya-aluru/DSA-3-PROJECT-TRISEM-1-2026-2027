"""Accounts: SQLite + salted PBKDF2-SHA256. Stores credentials only, never documents."""
import sqlite3, hashlib, hmac, os, re
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

def _con():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, name TEXT, salt BLOB, pw BLOB)")
    return c

def _hash(pw, salt): return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 200_000)

def register(name, email, pw):
    email = email.strip().lower()
    if not name.strip(): return False, "Enter your name."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email): return False, "Enter a valid email."
    if len(pw) < 8: return False, "Password must be at least 8 characters."
    salt = os.urandom(16)
    try:
        with _con() as c: c.execute("INSERT INTO users VALUES(?,?,?,?)", (email, name.strip(), salt, _hash(pw, salt)))
    except sqlite3.IntegrityError: return False, "An account with this email already exists."
    return True, "Account created. You can log in now."

def login(email, pw):
    row = _con().execute("SELECT name,salt,pw FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    if row and hmac.compare_digest(_hash(pw, row[1]), row[2]): return row[0]
    return None
