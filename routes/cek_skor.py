from flask import Blueprint, render_template, request
from modules.probability import cek_skor_nomor, generate_ranking
from config import CATEGORIES
import json

bp = Blueprint("cek_skor", __name__)


@bp.route("/cek-skor", methods=["GET", "POST"])
def index():
    kategori = request.args.get("kat", "HK").upper()
    metode = request.args.get("metode", "weighted")
    hasil_cek = None
    nomor_input = ""

    if request.method == "POST":
        nomor_input = request.form.get("nomor", "").strip().zfill(4)
        kategori = request.form.get("kategori", "HK").upper()
        metode = request.form.get("metode", "weighted")
        hasil_cek = cek_skor_nomor(nomor_input, kategori, metode)

    # Top rekomendasi saat ini
    ranking = generate_ranking(kategori, metode=metode, top_n=5)

    return render_template(
        "cek_skor.html",
        kategori=kategori,
        metode=metode,
        hasil_cek=hasil_cek,
        nomor_input=nomor_input,
        ranking=ranking,
        categories=CATEGORIES,
    )
