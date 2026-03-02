from transformers import BertTokenizer, BertForSequenceClassification
import os

MODEL_NAME = "bert-base-uncased"
SAVE_PATH = "models/bert_intent_model"

os.makedirs(SAVE_PATH, exist_ok=True)

tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=4)

model.save_pretrained(SAVE_PATH)
tokenizer.save_pretrained(SAVE_PATH)

print("Fresh model saved successfully!")