import streamlit as st
import os
import pandas as pd
from ad_detector import analyze_image_and_classify_blocks
from pathlib import Path


UPLOAD_DIR = Path("static/uploads")
OUTPUT_DIR = Path("output/annotated")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

st.title("Financial Ad Extractor")

uploaded_file = st.file_uploader("Upload an image file", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:

    img_path = UPLOAD_DIR / uploaded_file.name
    with open(img_path, "wb") as f:
        f.write(uploaded_file.getbuffer())



    with st.spinner("Analyzing image..."):
        try:
            annotated_img_path, excel_path, ad_count, non_ad_count = analyze_image_and_classify_blocks(str(img_path))
        except Exception as e:
            st.error(f"Error during analysis: {e}")
            st.stop()

    st.success("Analysis complete!")

 
    st.image(annotated_img_path, caption="Annotated Image with Detected Blocks", use_column_width=True)

    st.write(f"Detected Ads: {ad_count}")
    st.write(f"Detected Non-Ads: {non_ad_count}")


    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)

        if df.empty:
            st.info("✅ No financial ads were detected in this image.")
        else:

            with open(excel_path, "rb") as f:
                st.download_button(
                    label="Download Excel Report",
                    data=f,
                    file_name="financial_ads_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.warning("⚠️ Excel report not found.")
