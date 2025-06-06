import os
import cv2
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from ocr_utils import extract_text
from groq_api import is_financial_ad
from datetime import datetime
import uuid  

model = load_model("model/financial_ad_detector_cnn_model.h5")  

def predict_block(block_img):
    img = cv2.resize(block_img, (256, 256)) / 255.0
    img = np.expand_dims(img, axis=0)
    pred = model.predict(img, verbose=0)
    return "Ad" if pred[0][0] > 0.5 else "Not Ad"

def detect_blocks(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    dilate = cv2.dilate(thresh, kernel, iterations=1)
    contours, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [cv2.boundingRect(c) for c in contours if cv2.boundingRect(c)[2] > 50 and cv2.boundingRect(c)[3] > 50]

def analyze_image_and_classify_blocks(image_path):
    img = cv2.imread(image_path)
    original = img.copy()
    blocks = detect_blocks(img)
    results = []


    page_number = 1
    date_of_publication = datetime.today().strftime('%Y-%m-%d')

    ad_count = 0
    non_ad_count = 0

    for (x, y, w, h) in blocks:
        block_img = img[y:y+h, x:x+w]
        label = predict_block(block_img)

        if label == "Ad":
            ad_count += 1
            text = extract_text(block_img)

            is_financial = is_financial_ad(text)


            if is_financial:
                llm_summary = "YES"
                block_uuid = str(uuid.uuid4())  
                results.append({
                    "Block_ID": block_uuid,
                    "Text": text,
                    "LLM_Summary": llm_summary,
                    "Page Number": page_number,
                    "Date of Publication": date_of_publication
                })

            color = (0, 0, 255)  # Red box for Ad
        else:
            non_ad_count += 1
            color = (0, 255, 0)  # Green box for Not Ad

        cv2.rectangle(original, (x, y), (x+w, y+h), color, 2)
        cv2.putText(original, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)



    os.makedirs("output", exist_ok=True)
    excel_path = "output/results.xlsx"
    pd.DataFrame(results).to_excel(excel_path, index=False)

   
    annotated_dir = image_path.replace("uploads", "annotated")
    os.makedirs(os.path.dirname(annotated_dir), exist_ok=True)
    cv2.imwrite(annotated_dir, original)

    return annotated_dir, excel_path, ad_count, non_ad_count
