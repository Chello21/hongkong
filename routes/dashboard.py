from flask import Blueprint, render_template, request, redirect, url_for, flash
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
        "SELECT * FROM data_historis ORDER BY tanggal DESC, kategori ASC LIMIT 40"
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


@bp.route("/dashboard/edit", methods=["POST"])
def edit():
    tanggal = request.form.get("tanggal", "").strip()
    hari = request.form.get("hari", "").strip()

    if not tanggal:
        flash("Tanggal wajib diisi!", "error")
        return redirect(url_for("dashboard.index"))

    # Import needed functions for refreshing analysis
    from routes.input_data import _simpan_ranking
    from modules.chi_square import uji_chi_square_digit, simpan_hasil_uji

    conn = get_conn()
    updated = 0
    for kat in CATEGORIES:
        nilai = request.form.get(f"nilai_{kat}", "").strip()
        if not nilai:
            continue
        if len(nilai) != 4 or not nilai.isdigit():
            flash(f"Nilai {kat} harus 4 digit angka!", "error")
            continue
        
        try:
            # We use INSERT OR REPLACE. Since tanggal and kategori are primary keys,
            # this will update the existing entry for that date and category.
            conn.execute(
                "INSERT OR REPLACE INTO data_historis (tanggal, hari, kategori, nilai) VALUES (?,?,?,?)",
                (tanggal, hari, kat, nilai),
            )
            updated += 1
        except Exception as e:
            flash(f"Error: {e}", "error")

    conn.commit()
    conn.close()

    if updated > 0:
        # Trigger re-analysis for updated categories
        for kat in CATEGORIES:
            nilai = request.form.get(f"nilai_{kat}", "").strip()
            if nilai:
                try:
                    hasil_uji = uji_chi_square_digit(kat)
                    simpan_hasil_uji(kat, hasil_uji)
                    _simpan_ranking(kat)
                except Exception:
                    pass
        flash(f"✅ Berhasil mengupdate {updated} data. Analisis dan prediksi langsung diperbarui!", "success")
        
    return redirect(url_for("dashboard.index"))
