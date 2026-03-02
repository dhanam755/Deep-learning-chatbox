import torch
import pickle
from transformers import BertTokenizer, BertForSequenceClassification
from config import MODEL_PATH

tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)

with open("models/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

model.eval()

def predict_intent(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=1).item()

    confidence = torch.softmax(logits, dim=1).max().item()

    print("Predicted:", predicted_class)
    print("Confidence:", confidence)

    return predicted_class, confidence