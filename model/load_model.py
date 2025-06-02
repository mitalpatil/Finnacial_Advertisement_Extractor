import os
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv
import openai

# --- Load .env and Groq API Key ---
load_dotenv()
openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"  # Groq's endpoint

# --- Load Hugging Face BERT model ---
MODEL_NAME = "bondarchukb/bert-ads-classification"
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# --- Step 1: Classify if text is an advertisement ---
def classify_ad(text: str) -> int:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = F.softmax(outputs.logits, dim=1)
    prediction = torch.argmax(probs, dim=1).item()
    return prediction  # 0 = non-ad, 1 = ad

# --- Step 2: Use Groq API to check if ad is financial ---
def llm_says_financial(text: str) -> str:
    prompt = (
        f"Is this ad related to finance, investment, insurance, or banking?\n\n"
        f"Ad Text: \"{text}\"\n\n"
        f"Reply with only YES or NO."
    )
    try:
        response = openai.ChatCompletion.create(
            model="llama3-70b-8192",  # or other model available on Groq
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response['choices'][0]['message']['content'].strip().upper()
    except Exception as e:
        print(f"[Groq API Error] {e}")
        return "NO"  # Safe fallback

# --- Step 3: Final decision ---
def is_financial_ad(text: str) -> bool:
    if classify_ad(text) == 1:  # Detected as advertisement
        return llm_says_financial(text) == "YES"
    return False
