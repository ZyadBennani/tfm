import pandas as pd

# Try reading with UTF-8 encoding
try:
    df = pd.read_csv('data/raw/Jugadores.csv', encoding='utf-8', sep=';')
    print("Successfully read with UTF-8 encoding")
    print("\nFirst few rows:")
    print(df.head())
except Exception as e:
    print(f"Error reading with UTF-8: {str(e)}") 