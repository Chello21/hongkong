import sqlite3
from config import DATABASE_PATH

# ─────────────────────────────────────────────
# DATA SEED: HK / SGP / SDY  (11 Jul – 10 Agt 2026)
# "-" berarti tidak ada keluaran hari itu
# ─────────────────────────────────────────────
SEED_DATA = [
    # tanggal       hari       HK      SGP     SDY
    ("2026-07-11", "Sabtu",   "5490", "6452", "9408"),
    ("2026-07-12", "Minggu",  "6416", "2329", "4205"),
    ("2026-07-13", "Senin",   "9392", "4948", "5694"),
    ("2026-07-14", "Selasa",  "9206", None,   "3402"),
    ("2026-07-15", "Rabu",    "0655", "4087", "2380"),
    ("2026-07-16", "Kamis",   "9064", "5447", "4782"),
    ("2026-07-17", "Jumat",   "8809", None,   "2394"),
    ("2026-07-18", "Sabtu",   "0882", "9418", "6163"),
    ("2026-07-19", "Minggu",  "0447", "0647", "7706"),
    ("2026-07-20", "Senin",   "4610", "9720", "3781"),
    ("2026-07-21", "Selasa",  "2177", None,   "0856"),
    ("2026-07-22", "Rabu",    "1694", "9662", "8866"),
    ("2026-07-23", "Kamis",   "5902", "8863", "5382"),
    ("2026-07-24", "Jumat",   "8701", None,   "2429"),
    ("2026-07-25", "Sabtu",   "0734", "5131", "5214"),
    ("2026-07-26", "Minggu",  "6057", "6431", "1092"),
    ("2026-07-27", "Senin",   "5937", "3064", "1546"),
    ("2026-07-28", "Selasa",  "6583", None,   "0916"),
    ("2026-07-29", "Rabu",    "5305", "8813", "9204"),
    ("2026-07-30", "Kamis",   "0409", "3396", "9057"),
    ("2026-07-31", "Jumat",   "1140", None,   "7801"),
    ("2026-08-01", "Sabtu",   "7292", "5964", "8587"),
    ("2026-08-02", "Minggu",  "6723", "3052", "9135"),
    ("2026-08-03", "Senin",   "0087", "9120", "7037"),
    ("2026-08-04", "Selasa",  "8053", None,   "2448"),
    ("2026-08-05", "Rabu",    "4245", "0715", "6199"),
    ("2026-08-06", "Kamis",   "3634", None,   "4816"),
    ("2026-08-07", "Jumat",   "9943", "7907", "0158"),
    ("2026-08-08", "Sabtu",   "2797", "5102", "2413"),
    ("2026-08-09", "Minggu",  "8620", "7137", "8082"),
    ("2026-08-10", "Senin",   "7604", "3525", "0332"),
]

SEED_DATA_HK_LOTTO = [
    # tanggal       hari      nilai
    ("2026-07-12", "Minggu", "4733"),
    ("2026-07-13", "Senin",  "0267"),
    ("2026-07-14", "Selasa", "3684"),
    ("2026-07-15", "Rabu",   "3156"),
    ("2026-07-16", "Kamis",  "9010"),
    ("2026-07-17", "Jumat",  "0614"),
    ("2026-07-18", "Sabtu",  "1165"),
    ("2026-07-19", "Minggu", "7344"),
    ("2026-07-20", "Senin",  "4957"),
    ("2026-07-21", "Selasa", "8568"),
    ("2026-07-22", "Rabu",   "6880"),
    ("2026-07-23", "Kamis",  "1545"),
    ("2026-07-24", "Jumat",  "1869"),
    ("2026-07-25", "Sabtu",  "6465"),
    ("2026-07-26", "Minggu", "0037"),
    ("2026-07-27", "Senin",  "4937"),
    ("2026-07-28", "Selasa", "7437"),
    ("2026-07-29", "Rabu",   "3930"),
    ("2026-07-30", "Kamis",  "9237"),
    ("2026-07-31", "Jumat",  "2535"),
    ("2026-08-01", "Sabtu",  "8446"),
    ("2026-08-02", "Minggu", "0570"),
    ("2026-08-03", "Senin",  "4885"),
    ("2026-08-04", "Selasa", "8824"),
    ("2026-08-05", "Rabu",   "1739"),
    ("2026-08-06", "Kamis",  "1083"),
    ("2026-08-07", "Jumat",  "6011"),
    ("2026-08-08", "Sabtu",  "5917"),
    ("2026-08-09", "Minggu", "3752"),
    ("2026-08-10", "Senin",  "2983"),
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS data_historis (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal    DATE NOT NULL,
    hari       VARCHAR(20),
    kategori   VARCHAR(10) NOT NULL,
    nilai      VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tanggal, kategori)
);

CREATE TABLE IF NOT EXISTS hasil_analisis (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal_analisis  DATE NOT NULL,
    kategori          VARCHAR(10) NOT NULL,
    nomor_kandidat    VARCHAR(10),
    skor_probabilitas REAL,
    ranking_lengkap   TEXT,
    metode            VARCHAR(20) DEFAULT 'weighted',
    status_final      INTEGER DEFAULT 1,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tanggal_analisis, kategori, metode)
);

CREATE TABLE IF NOT EXISTS uji_keacakan (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal_uji      DATE NOT NULL,
    kategori         VARCHAR(10) NOT NULL,
    chi_square_value REAL,
    p_value          REAL,
    df               INTEGER,
    kesimpulan       TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluasi (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    hasil_analisis_id INTEGER REFERENCES hasil_analisis(id),
    nilai_aktual      VARCHAR(10),
    cocok             INTEGER DEFAULT 0,
    akurasi_model     REAL,
    akurasi_baseline  REAL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()

    # Seed data historis
    for row in SEED_DATA:
        tanggal, hari, hk, sgp, sdy = row
        pairs = [("HK", hk), ("SGP", sgp), ("SDY", sdy)]
        for kategori, nilai in pairs:
            if nilai is None:
                continue
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO data_historis (tanggal, hari, kategori, nilai) VALUES (?,?,?,?)",
                    (tanggal, hari, kategori, nilai),
                )
            except Exception:
                pass
    # Seed data HK Lotto
    for row in SEED_DATA_HK_LOTTO:
        tanggal, hari, nilai = row
        try:
            conn.execute(
                "INSERT OR IGNORE INTO data_historis (tanggal, hari, kategori, nilai) VALUES (?,?,'HK_LOTTO',?)",
                (tanggal, hari, nilai),
            )
        except Exception:
            pass
    conn.commit()
    conn.close()
    print("[DB] Database initialized & seed data loaded.")


if __name__ == "__main__":
    init_db()
