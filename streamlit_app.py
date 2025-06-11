import streamlit as st
import os
import pandas as pd
from ad_detector import analyze_image_and_classify_blocks
from pathlib import Path
from pdf2image import convert_from_bytes
from PIL import Image


UPLOAD_DIR = Path("static/uploads")
OUTPUT_DIR = Path("output/annotated")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

st.title("Financial Ad Extractor")


uploaded_file = st.file_uploader("Upload an image or PDF file", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    file_type = uploaded_file.type


    if file_type == "application/pdf":
        st.info("PDF detected. Extracting pages...")

        try:
            pages = convert_from_bytes(uploaded_file.read())
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            st.stop()

        all_reports = []

        for i, page_img in enumerate(pages):
            img_path = UPLOAD_DIR / f"page_{i+1}.jpg"
            page_img.save(img_path, "JPEG")

            with st.spinner(f"Analyzing page {i+1}..."):
                try:
                    annotated_img_path, excel_path, ad_count, non_ad_count = analyze_image_and_classify_blocks(str(img_path))
                except Exception as e:
                    st.error(f"Error on page {i+1}: {e}")
                    continue

            st.success(f"✅ Page {i+1} analysis complete!")
            st.image(annotated_img_path, caption=f"Page {i+1} Annotated", use_column_width=True)
            st.write(f"Detected Ads: {ad_count}")
            st.write(f"Detected Non-Ads: {non_ad_count}")

            if os.path.exists(excel_path):
                df = pd.read_excel(excel_path)
                all_reports.append(df)

        if all_reports:
            combined_df = pd.concat(all_reports, ignore_index=True)
            combined_excel_path = OUTPUT_DIR / "combined_financial_ads_report.xlsx"
            combined_df.to_excel(combined_excel_path, index=False)

            with open(combined_excel_path, "rb") as f:
                st.download_button(
                    label="Download Combined Excel Report",
                    data=f,
                    file_name="combined_financial_ads_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No ads found in any of the PDF pages.")

    else:
        img_path = UPLOAD_DIR / uploaded_file.name
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Analyzing image..."):
            try:
                annotated_img_path, excel_path, ad_count, non_ad_count = analyze_image_and_classify_blocks(str(img_path))
            except Exception as e:
                st.error(f"Error during analysis: {e}")
                st.stop()

        st.success("✅ Analysis complete!")
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
