import os
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv
from groq import Groq  


load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=groq_api_key)


MODEL_NAME = "bondarchukb/bert-ads-classification"
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model.eval()

def llm_says_financial(text: str) -> str:
    prompt = (
        f"Is this text related to finance, investment, insurance, or banking?\n\n"
        f"Text: \"{text}\"\n\n"
        f"Reply strictly with YES or NO."
    )
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        return response.choices[0].message.content.strip().upper()
    except Exception as e:
        print(f"[Groq API Error] {e}")
        return "NO"


def is_financial_ad(text: str) -> bool:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = F.softmax(outputs.logits, dim=1)
    prediction = torch.argmax(probs, dim=1).item()
    
    if prediction == 1:  
        return llm_says_financial(text) == "YES"
    
    return False
