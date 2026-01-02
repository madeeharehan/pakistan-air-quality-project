import pandas as pd
import os

INPUT_FOLDER = "hourly_data"
OUTPUT_FILE = "pakistan_pm25_cleaned.csv"

all_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".csv")]

print(f"Found {len(all_files)} files")

all_data = []

for file in all_files:
    path = os.path.join(INPUT_FOLDER, file)
    print(f"Processing: {file}")

    try:
        df = pd.read_csv(path)

        # Standardize column names
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        required = {"datetime", "city", "pm25_value"}
        if not required.issubset(df.columns):
            print(f"⚠️ Skipping {file} (missing required columns)")
            continue

        # Clean data
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df["pm25_value"] = pd.to_numeric(df["pm25_value"], errors="coerce")

        df = df.dropna(subset=["datetime", "pm25_value"])
        df = df[(df["pm25_value"] > 0) & (df["pm25_value"] < 1000)]

        # Optional: keep only needed columns
        df = df[["city", "datetime", "pm25_value"]]

        all_data.append(df)

        print(f"✔ Loaded {len(df)} rows")

    except Exception as e:
        print(f"❌ Error processing {file}: {e}")

# Merge everything
if not all_data:
    print("❌ No valid data found.")
    exit()

final_df = pd.concat(all_data, ignore_index=True)
final_df.sort_values("datetime", inplace=True)

final_df.to_csv(OUTPUT_FILE, index=False)

print("\n✅ CLEAN DATASET CREATED")
print(f"Rows: {len(final_df)}")
print(f"Saved as: {OUTPUT_FILE}")
