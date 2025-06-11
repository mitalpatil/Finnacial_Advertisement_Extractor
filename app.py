from flask import Flask, request, jsonify, send_file
import os
from pathlib import Path
from werkzeug.utils import secure_filename
from ad_detector import analyze_image_and_classify_blocks
from pdf2image import convert_from_bytes
import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "output/annotated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(uploaded_file.filename)
    file_ext = filename.split(".")[-1].lower()

    results = []
    all_dataframes = []

    try:
        if file_ext in ["jpg", "jpeg", "png"]:
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(image_path)

            result_image, excel_file, ad_count, non_ad_count = analyze_image_and_classify_blocks(image_path)
            results.append({
                "page": 1,
                "result_image": f"/download/{result_image}",
                "excel_file": f"/download/{excel_file}",
                "ads": ad_count,
                "non_ads": non_ad_count
            })


        elif file_ext == "pdf":
            pages = convert_from_bytes(uploaded_file.read())

            for i, page in enumerate(pages):
                page_filename = f"page_{i+1}.jpg"
                page_path = os.path.join(UPLOAD_FOLDER, page_filename)
                page.save(page_path, "JPEG")

                result_image, excel_file, ad_count, non_ad_count = analyze_image_and_classify_blocks(page_path)
                df = pd.read_excel(excel_file)
                all_dataframes.append(df)

                results.append({
                    "page": i + 1,
                    "result_image": f"/download/{result_image}",
                    "excel_file": f"/download/{excel_file}",
                    "ads": ad_count,
                    "non_ads": non_ad_count
                })

            if all_dataframes:
                combined_df = pd.concat(all_dataframes, ignore_index=True)
                combined_excel = os.path.join(OUTPUT_FOLDER, "combined_financial_ads_report.xlsx")
                combined_df.to_excel(combined_excel, index=False)

                results.append({
                    "combined_excel_file": f"/download/{combined_excel}"
                })

        else:
            return jsonify({"error": "Unsupported file type"}), 400

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<path:filename>")
def download_file(filename):
    full_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(full_path):
        return send_file(full_path, as_attachment=False)
    else:
        return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
