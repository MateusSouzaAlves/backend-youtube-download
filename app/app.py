from flask import Flask, request, jsonify
import subprocess
import uuid
import os

app = Flask(__name__)

# Diretório de saída
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "downloads"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Caminho explícito para o arquivo de cookies
COOKIE_FILE = "/opt/render/project/src/cookies"
print("🧪 Verificando existência do arquivo de cookies:", COOKIE_FILE)
print("🧪 Arquivo existe?", os.path.exists(COOKIE_FILE))


@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    url = data["url"]
    audio_format = data.get("audio_format", "bestaudio")
    video_quality = data.get("video_quality", "best")

    file_id = str(uuid.uuid4())
    output_template = os.path.join(OUTPUT_DIR, f"{file_id}.%(ext)s")

    cmd = [
        "yt-dlp",
        "--cookies", COOKIE_FILE,
        "-f", f"{video_quality}+{audio_format}/best",
        "-o", output_template,
        url
    ]

    print("🧪 Executando comando:", " ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
        for ext in ["mp4", "mkv", "webm"]:
            path = os.path.join(OUTPUT_DIR, f"{file_id}.{ext}")
            if os.path.exists(path):
                return jsonify({
                    "message": "Download successful",
                    "file": f"{file_id}.{ext}"
                })

        return jsonify({"error": "Download completed, but no file found."}), 500

    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Download failed",
            "details": str(e)
        }), 500


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "OK", "message": "yt-dlp API is running"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
