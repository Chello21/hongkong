from flask import Blueprint, render_template, request
from modules.chi_square import uji_chi_square_digit, simpan_hasil_uji, get_riwayat_uji
from config import CATEGORIES
import json

bp = Blueprint("uji_keacakan", __name__)


@bp.route("/uji-keacakan", methods=["GET", "POST"])
def index():
    kategori = request.args.get("kat", "HK").upper()
    if kategori not in CATEGORIES:
        kategori = "HK"

    hasil = None
    if request.method == "POST":
        kat_uji = request.form.get("kategori", kategori).upper()
        hasil = uji_chi_square_digit(kat_uji)
        simpan_hasil_uji(kat_uji, hasil)
        kategori = kat_uji

    if hasil is None:
        hasil = uji_chi_square_digit(kategori)

    riwayat = get_riwayat_uji(limit=30)

    # Data chart untuk tiap posisi
    chart_data = {}
    for posisi, data in hasil["per_posisi"].items():
        chart_data[posisi] = {
            "labels": [str(d) for d in range(10)],
            "observed": data["observed"],
            "expected": data["expected"],
            "chi2": data["chi2"],
            "p_value": data["p_value"],
        }

    return render_template(
        "uji_keacakan.html",
        hasil=hasil,
        riwayat=riwayat,
        kategori=kategori,
        categories=CATEGORIES,
        chart_data=json.dumps(chart_data),
    )
