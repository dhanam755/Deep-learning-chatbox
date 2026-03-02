import pandas as pd
import pickle
import os
from sklearn.preprocessing import LabelEncoder

# Load your dataset
df = pd.read_csv("data/intents.csv")

labels = df["intent"].tolist()

label_encoder = LabelEncoder()
label_encoder.fit(labels)

os.makedirs("models", exist_ok=True)

with open("models/label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

print("Label encoder saved successfully!")