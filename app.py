from flask import Flask, request, jsonify, send_file
import os
import pandas as pd
from datetime import datetime
from ocr_utils import extract_text_blocks
from model.load_model import is_financial_ad  # ✅ Updated import

app = Flask(__name__)
UPLOAD_FOLDER = "static"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['image']
    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    blocks, _ = extract_text_blocks(image_path)
    results = []

    for block in blocks:
        if is_financial_ad(block['text']):  # ✅ Updated logic
            results.append({
                "Block ID": block['block_id'],
                "Text": block['text'],
                "Page Number": 1,
                "Date": datetime.today().strftime('%Y-%m-%d')
            })

    df = pd.DataFrame(results)
    output_path = os.path.join(OUTPUT_FOLDER, 'financial_ads_output.xlsx')
    df.to_excel(output_path, index=False)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
