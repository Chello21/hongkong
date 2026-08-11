import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = "randomness-analisis-hk-sgp-sdy-2026"
DATABASE_PATH = os.path.join(BASE_DIR, "data.db")

# Konfigurasi kategori
CATEGORIES = ["HK", "SGP", "SDY"]

# Format nomor: 4D (0000-9999), 10000 kemungkinan
NUMBER_RANGE = 10000   # untuk Chi-square Ei
NUMBER_FORMAT = "4D"

# Weighted frequency: decay factor (lebih baru = lebih berbobot)
DECAY_FACTOR = 0.9
