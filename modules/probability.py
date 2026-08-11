"""
probability.py
Menghitung skor probabilitas untuk tiap digit per posisi.
Dua metode: frekuensi relatif sederhana & weighted frequency (exponential decay).
"""

from modules.preprocessing import (
    hitung_frekuensi_digit,
    hitung_frekuensi_weighted,
    hitung_frekuensi_nomor_penuh,
    hitung_frekuensi_weighted_nomor,
)


def hitung_skor_digit(kategori: str, metode: str = "weighted"):
    """
    Hitung skor probabilitas per digit (0-9) untuk setiap posisi.

    Args:
        kategori: "HK", "SGP", atau "SDY"
        metode: "simple" atau "weighted"

    Returns:
        dict per posisi: { 'ribuan': {'0': 0.12, '1': 0.09, ...}, ... }
        Nilai adalah probabilitas (0.0 – 1.0)
    """
    if metode == "weighted":
        freq_map = hitung_frekuensi_weighted(kategori)
    else:
        freq_map = hitung_frekuensi_digit(kategori)

    skor = {}
    for posisi, freq_dict in freq_map.items():
        total = sum(freq_dict.values())
        if total == 0:
            skor[posisi] = {d: 0.0 for d in freq_dict}
        else:
            skor[posisi] = {
                d: round(v / total, 6) for d, v in freq_dict.items()
            }
    return skor


def rekomendasikan_digit_per_posisi(kategori: str, metode: str = "weighted", top_n: int = 3):
    """
    Rekomendasikan top-N digit terbaik per posisi berdasarkan skor.

    Returns:
        dict: { 'ribuan': ['7','3','5'], 'ratusan': [...], ... }
    """
    skor = hitung_skor_digit(kategori, metode)
    rekomendasi = {}
    for posisi, digit_skor in skor.items():
        sorted_digits = sorted(digit_skor.items(), key=lambda x: x[1], reverse=True)
        rekomendasi[posisi] = [d for d, _ in sorted_digits[:top_n]]
    return rekomendasi


def generate_ranking(kategori: str, metode: str = "weighted", top_n: int = 10):
    """
    Generate ranking nomor 4D berdasarkan kombinasi skor digit terbaik.
    Strategi: ambil digit teratas per posisi, kombinasikan, hitung skor gabungan.

    Returns:
        list of (nomor_4d, skor_gabungan) diurutkan descending
    """
    skor = hitung_skor_digit(kategori, metode)
    posisi_order = ["ribuan", "ratusan", "puluhan", "satuan"]

    # Ambil top-5 digit per posisi
    top_per_posisi = {}
    for pos in posisi_order:
        sorted_d = sorted(skor[pos].items(), key=lambda x: x[1], reverse=True)
        top_per_posisi[pos] = sorted_d[:5]

    # Kombinasi Cartesian: ribuan x ratusan x puluhan x satuan
    kombinasi = []
    for r, sr in top_per_posisi["ribuan"]:
        for ra, sra in top_per_posisi["ratusan"]:
            for p, sp in top_per_posisi["puluhan"]:
                for s, ss in top_per_posisi["satuan"]:
                    nomor = r + ra + p + s
                    skor_total = (sr + sra + sp + ss) / 4
                    kombinasi.append((nomor, round(skor_total, 6)))

    kombinasi.sort(key=lambda x: x[1], reverse=True)
    return kombinasi[:top_n]


def cek_skor_nomor(nomor: str, kategori: str, metode: str = "weighted"):
    """
    Cek skor probabilitas untuk nomor tertentu.

    Args:
        nomor: string 4 digit, contoh "7604"
        kategori: "HK", "SGP", "SDY"

    Returns:
        dict: skor per posisi + skor gabungan
    """
    if len(nomor) != 4 or not nomor.isdigit():
        return {"error": "Nomor harus 4 digit angka (0000-9999)"}

    skor = hitung_skor_digit(kategori, metode)
    posisi_order = ["ribuan", "ratusan", "puluhan", "satuan"]
    posisi_nama = ["Ribuan", "Ratusan", "Puluhan", "Satuan"]

    detail = []
    total_skor = 0.0
    for i, (pos, nama) in enumerate(zip(posisi_order, posisi_nama)):
        digit = nomor[i]
        s = skor[pos].get(digit, 0.0)
        total_skor += s
        detail.append({
            "posisi": nama,
            "digit": digit,
            "skor": round(s, 6),
            "persentase": f"{round(s * 100, 2)}%",
        })

    return {
        "nomor": nomor,
        "kategori": kategori,
        "metode": metode,
        "detail": detail,
        "skor_gabungan": round(total_skor / 4, 6),
        "persentase_gabungan": f"{round(total_skor / 4 * 100, 2)}%",
    }


def prediksi_gabungan(kategori: str):
    """
    Prediksi gabungan dari TIGA model:
      1. Weighted Frequency   — data terbaru lebih berbobot
      2. Simple Frequency     — semua data bobotnya sama
      3. Ganjil/Genap Pattern — sesuaikan digit dengan pola dominan per posisi

    Cara kerja:
    - Setiap model vote digit terbaik per posisi (top-1)
    - Skor gabungan = rata-rata skor dari ketiga model
    - Digit pemenang per posisi = yang paling sering dipilih (majority vote)
    - Jika draw, menangkan model dengan skor tertinggi

    Returns:
        dict:
          - nomor_prediksi: str nomor 4D final
          - detail_per_posisi: breakdown voting per posisi
          - skor_model: skor masing-masing model
          - confidence: skor kepercayaan gabungan (0-100%)
    """
    from modules.preprocessing import hitung_ganjil_genap

    posisi_order = ["ribuan", "ratusan", "puluhan", "satuan"]

    # Model 1: Weighted
    skor_w = hitung_skor_digit(kategori, "weighted")
    top_w  = {pos: max(skor_w[pos].items(), key=lambda x: x[1]) for pos in posisi_order}

    # Model 2: Simple
    skor_s = hitung_skor_digit(kategori, "simple")
    top_s  = {pos: max(skor_s[pos].items(), key=lambda x: x[1]) for pos in posisi_order}

    # Model 3: Ganjil/Genap — pilih digit tertinggi yang sesuai pola dominan
    gg_data = hitung_ganjil_genap(kategori)
    top_gg  = {}
    for pos in posisi_order:
        dominan = gg_data["per_posisi"][pos]["dominan"]  # "ganjil" atau "genap"
        # Saring digit sesuai pola, lalu ambil yang skor tertinggi (dari weighted)
        filtered = {
            d: v for d, v in skor_w[pos].items()
            if (int(d) % 2 == 1 and dominan == "ganjil") or
               (int(d) % 2 == 0 and dominan == "genap")
        }
        if filtered:
            best = max(filtered.items(), key=lambda x: x[1])
        else:
            best = max(skor_w[pos].items(), key=lambda x: x[1])
        top_gg[pos] = best

    # Voting per posisi
    detail_per_posisi = {}
    nomor_prediksi    = ""

    for pos in posisi_order:
        votes = {
            "weighted":   top_w[pos],
            "simple":     top_s[pos],
            "ganjil_genap": top_gg[pos],
        }

        # Hitung vote count per digit
        vote_count = {}
        for model, (digit, skor_val) in votes.items():
            if digit not in vote_count:
                vote_count[digit] = {"count": 0, "skor_total": 0.0, "models": []}
            vote_count[digit]["count"]      += 1
            vote_count[digit]["skor_total"] += skor_val
            vote_count[digit]["models"].append(model)

        # Pemenang: terbanyak vote, tiebreak dengan skor tertinggi
        winner_digit = max(
            vote_count.keys(),
            key=lambda d: (vote_count[d]["count"], vote_count[d]["skor_total"])
        )

        detail_per_posisi[pos] = {
            "digit_terpilih": winner_digit,
            "votes": {
                k: {"digit": v[0], "skor": round(v[1] * 100, 2)}
                for k, v in votes.items()
            },
            "vote_count":  vote_count[winner_digit]["count"],
            "konsensus":   vote_count[winner_digit]["count"] == 3,  # semua setuju
        }
        nomor_prediksi += winner_digit

    # Hitung confidence: rata-rata skor digit terpilih dari ketiga model
    total_conf = 0.0
    for pos in posisi_order:
        d = detail_per_posisi[pos]["digit_terpilih"]
        sw = skor_w[pos].get(d, 0.0)
        ss = skor_s[pos].get(d, 0.0)
        sg = skor_w[pos].get(top_gg[pos][0], 0.0)
        total_conf += (sw + ss + sg) / 3

    confidence = round(total_conf / 4 * 100, 2)

    # Skor individu per model
    skor_model = {
        "weighted": round(
            sum(top_w[p][1] for p in posisi_order) / 4 * 100, 2),
        "simple": round(
            sum(top_s[p][1] for p in posisi_order) / 4 * 100, 2),
        "ganjil_genap": round(
            sum(top_gg[p][1] for p in posisi_order) / 4 * 100, 2),
    }

    konsensus_total = sum(
        1 for pos in posisi_order
        if detail_per_posisi[pos]["konsensus"]
    )

    return {
        "nomor_prediksi":    nomor_prediksi,
        "detail_per_posisi": detail_per_posisi,
        "skor_model":        skor_model,
        "confidence":        confidence,
        "konsensus_total":   konsensus_total,  # berapa posisi yang semua model sepakat
        "kategori":          kategori,
    }
