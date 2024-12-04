import pandas as pd

# Read the original CSV file
df = pd.read_csv("dataset/credits.csv")

# Calculate the number of rows for each file
total_rows = len(df)
split_size = total_rows // 3

# Split the dataframe into three parts
df_1 = df.iloc[:split_size]
df_2 = df.iloc[split_size:2 * split_size]
df_3 = df.iloc[2 * split_size:]

# Save the parts into new CSV files
df_1.to_csv("dataset/credit_1.csv", index=False)
df_2.to_csv("dataset/credit_2.csv", index=False)
df_3.to_csv("dataset/credit_3.csv", index=False)

print("File has been split into credit_1.csv, credit_2.csv, and credit_3.csv")

