"""
preprocessing.py
Menghitung frekuensi tiap angka/digit dari data historis.
Analisis dilakukan pada level digit: angka 0-9 per posisi (ribuan, ratusan, puluhan, satuan)
"""

from database import get_conn
from config import DECAY_FACTOR
import numpy as np


def get_data_by_category(kategori: str):
    """Ambil semua data historis untuk satu kategori, diurutkan dari terlama ke terbaru."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT tanggal, nilai FROM data_historis WHERE kategori=? ORDER BY tanggal ASC",
        (kategori,),
    ).fetchall()
    conn.close()
    return [(r["tanggal"], r["nilai"]) for r in rows]


def hitung_frekuensi_digit(kategori: str):
    """
    Hitung frekuensi kemunculan tiap digit (0-9) di setiap posisi:
    posisi 0 = ribuan, 1 = ratusan, 2 = puluhan, 3 = satuan

    Returns:
        dict: { 'ribuan': {0:n, 1:n, ...}, 'ratusan': {...}, ... }
    """
    data = get_data_by_category(kategori)
    posisi_nama = ["ribuan", "ratusan", "puluhan", "satuan"]
    result = {p: {str(d): 0 for d in range(10)} for p in posisi_nama}

    for _, nilai in data:
        if len(nilai) == 4:
            for i, pos in enumerate(posisi_nama):
                digit = nilai[i]
                result[pos][digit] = result[pos].get(digit, 0) + 1

    return result


def hitung_frekuensi_weighted(kategori: str):
    """
    Weighted frequency: data lebih baru diberi bobot lebih besar.
    Bobot = DECAY_FACTOR^(N-1-i), di mana i = indeks dari terlama.
    """
    data = get_data_by_category(kategori)
    posisi_nama = ["ribuan", "ratusan", "puluhan", "satuan"]
    result = {p: {str(d): 0.0 for d in range(10)} for p in posisi_nama}
    N = len(data)

    for i, (_, nilai) in enumerate(data):
        bobot = DECAY_FACTOR ** (N - 1 - i)
        if len(nilai) == 4:
            for j, pos in enumerate(posisi_nama):
                digit = nilai[j]
                result[pos][digit] = result[pos].get(digit, 0.0) + bobot

    return result


def hitung_frekuensi_nomor_penuh(kategori: str):
    """Hitung frekuensi tiap nomor 4D secara penuh (bukan per digit)."""
    data = get_data_by_category(kategori)
    freq = {}
    for _, nilai in data:
        freq[nilai] = freq.get(nilai, 0) + 1
    return freq


def hitung_frekuensi_weighted_nomor(kategori: str):
    """Weighted frequency untuk nomor penuh 4D."""
    data = get_data_by_category(kategori)
    N = len(data)
    freq = {}
    for i, (_, nilai) in enumerate(data):
        bobot = DECAY_FACTOR ** (N - 1 - i)
        freq[nilai] = freq.get(nilai, 0.0) + bobot
    return freq


def get_ringkasan(kategori: str):
    """Ringkasan statistik sederhana untuk dashboard."""
    data = get_data_by_category(kategori)
    if not data:
        return {}
    nilai_list = [int(v) for _, v in data]
    return {
        "total_data": len(data),
        "rata_rata": round(np.mean(nilai_list), 2),
        "std_dev": round(np.std(nilai_list), 2),
        "min": min(nilai_list),
        "max": max(nilai_list),
        "tanggal_awal": data[0][0],
        "tanggal_akhir": data[-1][0],
    }


def hitung_ganjil_genap(kategori: str):
    """
    Analisis ganjil/genap dari data historis.

    Returns dict berisi:
    - per_posisi: { 'ribuan': {'ganjil': n, 'genap': n, 'pct_ganjil': %, 'pct_genap': %}, ... }
    - keseluruhan: ganjil/genap dari nilai 4D penuh (pakai digit satuan sebagai penentu)
    - tren_10: ganjil/genap dari 10 data terbaru (tren terkini)
    - detail_terakhir: list 10 data terbaru beserta label ganjil/genapnya
    """
    data = get_data_by_category(kategori)
    posisi_nama = ["ribuan", "ratusan", "puluhan", "satuan"]

    per_posisi = {
        p: {"ganjil": 0, "genap": 0} for p in posisi_nama
    }

    keseluruhan = {"ganjil": 0, "genap": 0}
    tren_10 = {"ganjil": 0, "genap": 0}
    detail_terakhir = []

    for idx, (tgl, nilai) in enumerate(data):
        if len(nilai) != 4:
            continue

        # Per posisi
        for i, pos in enumerate(posisi_nama):
            d = int(nilai[i])
            if d % 2 == 1:
                per_posisi[pos]["ganjil"] += 1
            else:
                per_posisi[pos]["genap"] += 1

        # Keseluruhan: berdasarkan digit satuan (penentu ganjil/genap nomor)
        satuan = int(nilai[3])
        label = "ganjil" if satuan % 2 == 1 else "genap"
        keseluruhan[label] += 1

        # Tren 10 terbaru
        is_recent = idx >= len(data) - 10
        if is_recent:
            tren_10[label] += 1
            detail_terakhir.append({
                "tanggal": tgl,
                "nilai": nilai,
                "label": label,
            })

    # Hitung persentase per posisi
    for pos in posisi_nama:
        total = per_posisi[pos]["ganjil"] + per_posisi[pos]["genap"]
        if total > 0:
            per_posisi[pos]["pct_ganjil"] = round(per_posisi[pos]["ganjil"] / total * 100, 1)
            per_posisi[pos]["pct_genap"]  = round(per_posisi[pos]["genap"]  / total * 100, 1)
            per_posisi[pos]["dominan"]    = "ganjil" if per_posisi[pos]["ganjil"] >= per_posisi[pos]["genap"] else "genap"
        else:
            per_posisi[pos]["pct_ganjil"] = 0
            per_posisi[pos]["pct_genap"]  = 0
            per_posisi[pos]["dominan"]    = "-"

    # Persentase keseluruhan
    total_all = keseluruhan["ganjil"] + keseluruhan["genap"]
    keseluruhan["pct_ganjil"] = round(keseluruhan["ganjil"] / total_all * 100, 1) if total_all else 0
    keseluruhan["pct_genap"]  = round(keseluruhan["genap"]  / total_all * 100, 1) if total_all else 0
    keseluruhan["dominan"]    = "ganjil" if keseluruhan["ganjil"] >= keseluruhan["genap"] else "genap"

    # Persentase tren 10 terbaru
    total_tren = tren_10["ganjil"] + tren_10["genap"]
    tren_10["pct_ganjil"] = round(tren_10["ganjil"] / total_tren * 100, 1) if total_tren else 0
    tren_10["pct_genap"]  = round(tren_10["genap"]  / total_tren * 100, 1) if total_tren else 0
    tren_10["dominan"]    = "ganjil" if tren_10["ganjil"] >= tren_10["genap"] else "genap"

    return {
        "per_posisi": per_posisi,
        "keseluruhan": keseluruhan,
        "tren_10": tren_10,
        "detail_terakhir": list(reversed(detail_terakhir)),  # terbaru di atas
    }
