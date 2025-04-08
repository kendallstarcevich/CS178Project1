import pandas as pd

# Load the original calendar CSV
df = pd.read_csv("calendar.csv")

# Remove the $ from the 'price' column and convert it to float
df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)

# Drop the 'adjusted_price' column
df.drop(columns=['adjusted_price'], inplace=True)

# Save the cleaned CSV
df.to_csv("calendar_clean.csv", index=False)

print("✅ Cleaned calendar.csv and saved to calendar_clean.csv")
