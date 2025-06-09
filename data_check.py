import pandas as pd
import numpy as np

# Leer el archivo Excel
df = pd.read_excel('Datos/Wyscout Liga/Team Stats Barcelona.xlsx')

# Mostrar información básica
print("Información del DataFrame:")
print(df.info())

print("\nPrimeras 5 filas:")
print(df.head())

print("\nColumnas disponibles:")
print(df.columns.tolist())

# Guardar la información en un archivo de texto
with open('data_analysis.txt', 'w') as f:
    f.write("Información del DataFrame:\n")
    df.info(buf=f)
    f.write("\n\nColumnas disponibles:\n")
    f.write("\n".join(df.columns.tolist())) 