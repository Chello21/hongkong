from flask import Blueprint, render_template
from modules.preprocessing import get_ringkasan
from database import get_conn
from config import CATEGORIES

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@bp.route("/dashboard")
def index():
    ringkasan = {kat: get_ringkasan(kat) for kat in CATEGORIES}

    # Data terbaru (10 baris per kategori untuk tabel dashboard)
    conn = get_conn()
    data_terbaru = conn.execute(
        "SELECT * FROM data_historis ORDER BY tanggal DESC, kategori ASC LIMIT 30"
    ).fetchall()
    total_uji = conn.execute("SELECT COUNT(*) as c FROM uji_keacakan").fetchone()["c"]
    total_analisis = conn.execute("SELECT COUNT(*) as c FROM hasil_analisis").fetchone()["c"]
    conn.close()

    return render_template(
        "dashboard.html",
        ringkasan=ringkasan,
        data_terbaru=[dict(r) for r in data_terbaru],
        total_uji=total_uji,
        total_analisis=total_analisis,
        categories=CATEGORIES,
    )
