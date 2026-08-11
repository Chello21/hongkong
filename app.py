from flask import Flask
from config import SECRET_KEY
from database import init_db

# Import blueprints
from routes.dashboard import bp as dashboard_bp
from routes.input_data import bp as input_data_bp
from routes.hasil_analisis import bp as hasil_analisis_bp
from routes.uji_keacakan import bp as uji_keacakan_bp
from routes.cek_skor import bp as cek_skor_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Inisialisasi database
    init_db()

    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(input_data_bp)
    app.register_blueprint(hasil_analisis_bp)
    app.register_blueprint(uji_keacakan_bp)
    app.register_blueprint(cek_skor_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
