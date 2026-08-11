from flask import Blueprint, render_template, request
from modules.probability import generate_ranking, hitung_skor_digit, prediksi_gabungan
from modules.preprocessing import hitung_frekuensi_digit, get_data_by_category, hitung_ganjil_genap
from database import get_conn
from config import CATEGORIES
import json

bp = Blueprint("hasil_analisis", __name__)


@bp.route("/hasil-analisis")
def index():
    kategori = request.args.get("kat", "HK").upper()
    metode   = request.args.get("metode", "weighted")
    tab      = request.args.get("tab", "ranking")  # tab aktif: ranking | ganjilgenap | prediksi

    if kategori not in CATEGORIES:
        kategori = "HK"

    # ── Data ranking & skor digit ──────────────────────
    ranking    = generate_ranking(kategori, metode=metode, top_n=20)
    skor_digit = hitung_skor_digit(kategori, metode)
    freq_digit = hitung_frekuensi_digit(kategori)

    # Chart.js: frekuensi digit per posisi
    chart_data = {}
    for posisi, freq in freq_digit.items():
        chart_data[posisi] = {
            "labels": [str(d) for d in range(10)],
            "values": [freq[str(d)] for d in range(10)],
        }

    # ── Ganjil / Genap ─────────────────────────────────
    gg = hitung_ganjil_genap(kategori)

    # Chart ganjil/genap per posisi (untuk grouped bar)
    gg_chart = {
        "labels": ["Ribuan", "Ratusan", "Puluhan", "Satuan"],
        "ganjil": [gg["per_posisi"][p]["ganjil"] for p in ["ribuan","ratusan","puluhan","satuan"]],
        "genap":  [gg["per_posisi"][p]["genap"]  for p in ["ribuan","ratusan","puluhan","satuan"]],
    }

    # ── Prediksi Gabungan ──────────────────────────────
    prediksi = prediksi_gabungan(kategori)

    # Riwayat hasil analisis tersimpan
    conn = get_conn()
    riwayat = conn.execute(
        """SELECT * FROM hasil_analisis WHERE kategori=? AND metode=?
           ORDER BY created_at DESC LIMIT 10""",
        (kategori, metode),
    ).fetchall()
    conn.close()

    return render_template(
        "hasil_analisis.html",
        kategori=kategori,
        metode=metode,
        tab=tab,
        ranking=ranking,
        skor_digit=skor_digit,
        chart_data=json.dumps(chart_data),
        gg=gg,
        gg_chart=json.dumps(gg_chart),
        prediksi=prediksi,
        riwayat=[dict(r) for r in riwayat],
        categories=CATEGORIES,
    )
