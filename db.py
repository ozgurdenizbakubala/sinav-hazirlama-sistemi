# -*- coding: utf-8 -*-
import sqlite3, os, hashlib, random, string, sys

def _get_db_path():
    """
    Platform bağımsız veritabanı yolu:
    - Windows kurulu: AppData/Local/SinavHazirlamaSistemi/
    - Linux kurulu:   ~/.local/share/SinavHazirlamaSistemi/
    - Geliştirici:    proje klasörü
    """
    if getattr(sys, 'frozen', False):
        if sys.platform == "win32":
            app_data = os.environ.get("LOCALAPPDATA",
                       os.path.join(os.path.expanduser("~"), "AppData", "Local"))
        else:
            app_data = os.path.join(os.path.expanduser("~"), ".local", "share")
        db_dir = os.path.join(app_data, "SinavHazirlamaSistemi")
    else:
        db_dir = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "sinav.db")

DB_PATH = _get_db_path()

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA encoding = 'UTF-8'")
    return conn

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS ayarlar (
            anahtar TEXT PRIMARY KEY,
            deger   TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS kurtarma_kodlari (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            kod        TEXT NOT NULL UNIQUE,
            kullanildi INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS siniflar (
            id  INTEGER PRIMARY KEY AUTOINCREMENT,
            ad  TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS konular (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            ad       TEXT NOT NULL,
            sinif_id INTEGER,
            FOREIGN KEY (sinif_id) REFERENCES siniflar(id) ON DELETE SET NULL,
            UNIQUE(ad, sinif_id)
        );
        CREATE TABLE IF NOT EXISTS sorular (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            konu_id       INTEGER NOT NULL,
            gorsel        BLOB NOT NULL,
            gorsel_temiz  BLOB,
            cevap_metni   TEXT,
            cevap_gorseli BLOB,
            cozum_gorseli BLOB,
            FOREIGN KEY (konu_id) REFERENCES konular(id) ON DELETE CASCADE
        );
    """)
    # Migration: eski tablolara yeni sütunlar ekle
    for col, typ in [
        ("gorsel_temiz","BLOB"), ("cevap_metni","TEXT"),
        ("cevap_gorseli","BLOB"), ("cozum_gorseli","BLOB")
    ]:
        try: c.execute(f"ALTER TABLE sorular ADD COLUMN {col} {typ}")
        except: pass
    try: c.execute("ALTER TABLE konular ADD COLUMN sinif_id INTEGER")
    except: pass
    conn.commit()
    conn.close()

# ── Ayarlar ──
def get_ayar(key):
    with get_conn() as c:
        r = c.execute("SELECT deger FROM ayarlar WHERE anahtar=?", (key,)).fetchone()
    return r[0] if r else None

def set_ayar(key, val):
    with get_conn() as c:
        c.execute("INSERT OR REPLACE INTO ayarlar(anahtar,deger) VALUES(?,?)", (key, val))
        c.commit()

# ── Şifre ──
def hash_pw(pw):
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def uret_kurtarma_kodlari():
    kodlar = []
    for _ in range(32):
        kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        kodlar.append(kod)
    with get_conn() as c:
        for k in kodlar:
            try: c.execute("INSERT INTO kurtarma_kodlari(kod) VALUES(?)", (k,))
            except: pass
        c.commit()
    return kodlar

def kurtarma_kodu_gecerli(kod):
    with get_conn() as c:
        r = c.execute(
            "SELECT id FROM kurtarma_kodlari WHERE kod=? AND kullanildi=0", (kod,)
        ).fetchone()
    return r[0] if r else None

def kurtarma_kodu_kullan(kid):
    with get_conn() as c:
        c.execute("UPDATE kurtarma_kodlari SET kullanildi=1 WHERE id=?", (kid,))
        c.commit()

# ── Sınıflar ──
def get_siniflar():
    with get_conn() as c:
        return c.execute("SELECT id, ad FROM siniflar ORDER BY ad").fetchall()

def sinif_ekle(ad):
    with get_conn() as c:
        c.execute("INSERT INTO siniflar(ad) VALUES(?)", (ad,))
        c.commit()

def sinif_sil(sid):
    with get_conn() as c:
        c.execute("DELETE FROM siniflar WHERE id=?", (sid,))
        c.commit()

# ── Konular ──
def get_konular(sinif_id=None):
    with get_conn() as c:
        if sinif_id is None:
            return c.execute("SELECT id, ad, sinif_id FROM konular ORDER BY ad").fetchall()
        return c.execute(
            "SELECT id, ad, sinif_id FROM konular WHERE sinif_id=? ORDER BY ad", (sinif_id,)
        ).fetchall()

def konu_ekle(ad, sinif_id=None):
    with get_conn() as c:
        c.execute("INSERT INTO konular(ad, sinif_id) VALUES(?,?)", (ad, sinif_id))
        c.commit()

def konu_sil(kid):
    with get_conn() as c:
        c.execute("DELETE FROM konular WHERE id=?", (kid,))
        c.commit()

# ── Sorular ──
def get_sorular(konu_id):
    with get_conn() as c:
        return c.execute(
            "SELECT id, gorsel, gorsel_temiz, cevap_metni, cevap_gorseli, cozum_gorseli "
            "FROM sorular WHERE konu_id=? ORDER BY id", (konu_id,)
        ).fetchall()

def get_sorular_by_sinif_konu(sinif_id=None, konu_ids=None):
    with get_conn() as c:
        if konu_ids:
            ph = ",".join("?"*len(konu_ids))
            return c.execute(
                f"SELECT s.id, COALESCE(s.gorsel_temiz, s.gorsel), k.ad, "
                f"s.cevap_metni, s.cevap_gorseli, s.cozum_gorseli "
                f"FROM sorular s JOIN konular k ON k.id=s.konu_id "
                f"WHERE s.konu_id IN ({ph})", konu_ids
            ).fetchall()
        if sinif_id:
            return c.execute(
                "SELECT s.id, COALESCE(s.gorsel_temiz, s.gorsel), k.ad, "
                "s.cevap_metni, s.cevap_gorseli, s.cozum_gorseli "
                "FROM sorular s JOIN konular k ON k.id=s.konu_id "
                "WHERE k.sinif_id=?", (sinif_id,)
            ).fetchall()
        return c.execute(
            "SELECT s.id, COALESCE(s.gorsel_temiz, s.gorsel), k.ad, "
            "s.cevap_metni, s.cevap_gorseli, s.cozum_gorseli "
            "FROM sorular s JOIN konular k ON k.id=s.konu_id"
        ).fetchall()

def soru_ekle(konu_id, gorsel, gorsel_temiz, cevap_metni, cevap_gorseli, cozum_gorseli):
    with get_conn() as c:
        c.execute(
            "INSERT INTO sorular(konu_id,gorsel,gorsel_temiz,cevap_metni,cevap_gorseli,cozum_gorseli) "
            "VALUES(?,?,?,?,?,?)",
            (konu_id, gorsel, gorsel_temiz, cevap_metni, cevap_gorseli, cozum_gorseli)
        )
        c.commit()

def soru_guncelle(soru_id, gorsel, gorsel_temiz, cevap_metni, cevap_gorseli, cozum_gorseli):
    with get_conn() as c:
        c.execute(
            "UPDATE sorular SET gorsel=?, gorsel_temiz=?, cevap_metni=?, "
            "cevap_gorseli=?, cozum_gorseli=? WHERE id=?",
            (gorsel, gorsel_temiz, cevap_metni, cevap_gorseli, cozum_gorseli, soru_id)
        )
        c.commit()

def soru_sil(soru_id):
    with get_conn() as c:
        c.execute("DELETE FROM sorular WHERE id=?", (soru_id,))
        c.commit()

def get_konu_sinif_istatistik():
    with get_conn() as c:
        return c.execute(
            "SELECT s.ad as sinif, k.ad as konu, COUNT(sr.id) as soru_sayisi "
            "FROM konular k "
            "LEFT JOIN siniflar s ON s.id=k.sinif_id "
            "LEFT JOIN sorular sr ON sr.konu_id=k.id "
            "GROUP BY k.id ORDER BY s.ad, k.ad"
        ).fetchall()
