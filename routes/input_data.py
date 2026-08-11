from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_conn
from modules.chi_square import uji_chi_square_digit, simpan_hasil_uji
from modules.probability import generate_ranking
from config import CATEGORIES
import json

bp = Blueprint("input_data", __name__)


@bp.route("/input-data", methods=["GET"])
def index():
    conn = get_conn()
    # Tampilkan data historis lengkap, urut terbaru dulu
    rows = conn.execute(
        "SELECT * FROM data_historis ORDER BY tanggal DESC, kategori ASC"
    ).fetchall()
    conn.close()

    # Susun per tanggal
    grouped = {}
    for r in rows:
        tgl = r["tanggal"]
        if tgl not in grouped:
            grouped[tgl] = {"tanggal": tgl, "hari": r["hari"]}
        grouped[tgl][r["kategori"]] = r["nilai"]

    table_rows = sorted(grouped.values(), key=lambda x: x["tanggal"], reverse=True)
    return render_template("input_data.html", table_rows=table_rows, categories=CATEGORIES)


@bp.route("/input-data/tambah", methods=["POST"])
def tambah():
    tanggal = request.form.get("tanggal", "").strip()
    hari = request.form.get("hari", "").strip()

    if not tanggal:
        flash("Tanggal wajib diisi!", "error")
        return redirect(url_for("input_data.index"))

    conn = get_conn()
    inserted = 0
    for kat in CATEGORIES:
        nilai = request.form.get(f"nilai_{kat}", "").strip()
        if not nilai:
            continue
        if len(nilai) != 4 or not nilai.isdigit():
            flash(f"Nilai {kat} harus 4 digit angka!", "error")
            conn.close()
            return redirect(url_for("input_data.index"))
        try:
            conn.execute(
                "INSERT OR REPLACE INTO data_historis (tanggal, hari, kategori, nilai) VALUES (?,?,?,?)",
                (tanggal, hari, kat, nilai),
            )
            inserted += 1
        except Exception as e:
            flash(f"Error: {e}", "error")

    conn.commit()
    conn.close()

    if inserted > 0:
        # Trigger analisis otomatis setelah input baru
        for kat in CATEGORIES:
            nilai = request.form.get(f"nilai_{kat}", "").strip()
            if nilai:
                try:
                    hasil_uji = uji_chi_square_digit(kat)
                    simpan_hasil_uji(kat, hasil_uji)
                    _simpan_ranking(kat)
                except Exception:
                    pass
        flash(f"✅ Berhasil menambah {inserted} data. Analisis diperbarui otomatis!", "success")
    return redirect(url_for("input_data.index"))


@bp.route("/input-data/hapus/<int:item_id>", methods=["POST"])
def hapus(item_id):
    conn = get_conn()
    conn.execute("DELETE FROM data_historis WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    flash("Data berhasil dihapus.", "success")
    return redirect(url_for("input_data.index"))


def _simpan_ranking(kategori: str):
    """Helper: generate & simpan ranking ke hasil_analisis."""
    from datetime import date
    ranking = generate_ranking(kategori, metode="weighted", top_n=10)
    if not ranking:
        return
    top_nomor, top_skor = ranking[0]
    ranking_json = json.dumps(ranking)
    today = date.today().isoformat()

    conn = get_conn()
    conn.execute(
        """INSERT OR REPLACE INTO hasil_analisis
           (tanggal_analisis, kategori, nomor_kandidat, skor_probabilitas, ranking_lengkap, metode)
           VALUES (?,?,?,?,?,?)""",
        (today, kategori, top_nomor, top_skor, ranking_json, "weighted"),
    )
    conn.commit()
    conn.close()
