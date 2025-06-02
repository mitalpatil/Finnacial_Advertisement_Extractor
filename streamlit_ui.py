import streamlit as st
from ocr_utils import extract_text_blocks
import cv2
from PIL import Image
import numpy as np
import io
import requests
import os

st.title("📰 Financial Advertisement Extractor")

uploaded_file = st.file_uploader("Upload a newspaper image", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    # Save the uploaded image directly to the 'static/' folder
    image_path = os.path.join("static", "temp_img.jpg")
    with open(image_path, "wb") as f:
        f.write(uploaded_file.read())

    if st.button("🔍 Extract Financial Ads"):
        structured_results, original_img = extract_text_blocks(image_path)

        for result in structured_results:
            x, y, w, h = result["coordinates"]
            cv2.rectangle(original_img, (x, y), (x + w, y + h), (0, 255, 0), 3)

        img_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
        st.image(img_rgb, caption="Detected Advertisement Blocks", use_column_width=True)

        # Send the image to your backend API
        with open(image_path, "rb") as img_file:
            files = {'image': img_file}
            response = requests.post("http://localhost:5000/upload", files=files)

        if response.status_code == 200:
            output_path = os.path.join("outputs", "downloaded_output.xlsx")
            with open(output_path, "wb") as f:
                f.write(response.content)
            st.success("✅ Extracted ads saved to Excel!")
            st.download_button("📥 Download Excel", data=open(output_path, "rb"), file_name="financial_ads_output.xlsx")
        else:
            st.error("❌ Extraction failed. Try again.")
