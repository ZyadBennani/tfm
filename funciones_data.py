import pandas as pd

def cargar_datos():
    pases = pd.read_csv("Datos/Barca_2024_25_Passing.csv")
    return pases
