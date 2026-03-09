import pandas as pd
from database.mongo import collection   # 🔥 same collection object

# Fetch all records
data = list(collection.find())

print("Number of records:", len(data))

if len(data) == 0:
    print("⚠ No data found in MongoDB!")
    exit()

# Convert to DataFrame
df = pd.DataFrame(data)

# Remove MongoDB internal ID
if "_id" in df.columns:
    df = df.drop(columns=["_id"])

# Convert timestamp column
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])

# Save CSV
df.to_csv("chat_data.csv", index=False)

print("✅ Data exported successfully!")