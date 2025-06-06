from flask import Flask, request, jsonify, send_file
import os
from ad_detector import analyze_image_and_classify_blocks

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    if image.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(image_path)

    try:
        result_image, excel_file = analyze_image_and_classify_blocks(image_path)
        return jsonify({
            "result_image": f"http://127.0.0.1:5000/download/{result_image}",
            "excel_file": f"http://127.0.0.1:5000/download/{excel_file}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download/<path:filename>")
def download_file(filename):
    try:
        return send_file(os.path.join(os.getcwd(), filename), as_attachment=False)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)