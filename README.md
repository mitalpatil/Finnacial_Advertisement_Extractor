# 📰 Financial Advertisement Extractor

**Automated system to extract financial ads from scanned newspaper pages using Computer Vision (CV), CNN, OCR, BERT, and LLMs.**

![App Screenshot](ss.png)

---

## 🚀 Project Overview

This project identifies and extracts **financial advertisements** from scanned or digital newspaper images using a hybrid AI pipeline that integrates:

- A **CNN-based block classifier** trained on real labeled ad data,
- **OCR (PyTesseract/EasyOCR)** for text extraction,
- A **BERT-based classifier** for initial filtering,
- A **LLM (LLaMA 3 / GPT-4)** for final validation of financial context.

Extracted financial ads are saved in **Excel** format for further business analysis or regulatory use.

---

## 🔍 Key Features

- ✅ Detects ad regions using a custom-trained **CNN model**
- ✅ Preprocesses and segments pages using **OpenCV**
- ✅ Extracts text from detected regions via **OCR**
- ✅ Classifies content using **BERT + LLM fallback**
- ✅ Saves outputs (UUID, text, page number, date) to Excel

---

## 🧠 Model Training (CNN)

- 🔬 A **Convolutional Neural Network (ResNet18)** was trained on **50+ manually labeled ad images**.
- 📂 Dataset included financial and non-financial ad blocks cropped from real newspaper scans.
- 🔎 The trained model (`cnn_ad_classifier.pth`) predicts whether a detected image block is a potential advertisement.
- 🎯 Acts as the **first filter** in the extraction pipeline, minimizing OCR and LLM load.

---
## 🖼️ System Architecture
```
Newspaper Image (JPG/PNG/PDF)
│
▼
1️⃣ Image Preprocessing (OpenCV: grayscale, thresholding)
│
▼
2️⃣ Block Detection (Contour Detection)
│
▼
3️⃣ Ad Classification (CNN)
│ ├─→ Non-Ad → Discard
│ └─→ Potential Ad
│
▼
4️⃣ OCR (PyTesseract / EasyOCR)
│
▼
5️⃣ Text Classification
├─ BERT Model → (financial?)
└─ If unsure, fallback to LLM (LLaMA 3 / GPT-4)
│
▼
6️⃣ Excel Export (UUID, Page, Date, Ad Text)
```

---

---

## 🧪 Tech Stack

| Component        | Technology                                |
|------------------|--------------------------------------------|
| Block Detection  | OpenCV, PIL                                |
| CNN Model        | PyTorch, ResNet18                          |
| OCR              | PyTesseract, EasyOCR                       |
| Text Classifier  | BERT (`bondarchukb/bert-ads-classification`) |
| LLM Validator    | LLaMA 3 (via Groq) / GPT-4                 |
| Data Export      | Pandas, Excel                              |
| Frontend         | Streamlit                                  |
| Backend          | Flask                                      |
| Language         | Python                                     |

---

## ⚙️ Setup Instructions

### 1. 🐍 Install Dependencies
```bash
pip install -r requirements.txt
````

### 2. 🚦 Run Backend API (Flask)

```bash
python app.py
 ````

### 3. 💻 Launch Frontend App (Streamlit)

```bash
streamlit run streamlit_ui.py
 ````
### 📌 Use Cases
📊 Financial Analysts: Extract ads for trend analysis

📰 Media Agencies: Automate ad tracking

📈 Marketing Teams: Monitor competitor presence


