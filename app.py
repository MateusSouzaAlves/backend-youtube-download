from flask import Flask, request, jsonify
from flask_cors import CORS
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)
CORS(app)

# Chave de API definida por variável de ambiente
API_KEY = os.environ.get("API_KEY", "minha-chave-secreta-123")

@app.route("/info", methods=["POST"])
def get_info():
    client_key = request.headers.get("X-API-KEY")
    if client_key != API_KEY:
        return jsonify({"error": "Chave de API inválida ou ausente."}), 401

    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL inválida"}), 400

    try:
        ydl_opts = {
            "quiet": True,
            "cookiefile": "cookies.txt"  # <- Suporte a cookies adicionados aqui
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if "entries" in info:
                info = info["entries"][0]

        response = {
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formats": [
                {
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "height": f.get("height"),
                    "vcodec": f.get("vcodec"),
                    "acodec": f.get("acodec"),
                    "url": f.get("url"),
                }
                for f in info.get("formats", [])
            ],
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
