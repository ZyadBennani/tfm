import pandas as pd
import numpy as np
from datetime import datetime

def split_and_convert(value, index=0):
    """Helper function to split and convert values"""
    try:
        if isinstance(value, str):
            return float(value.split('/')[index].strip())
        elif isinstance(value, (int, float)):
            return float(value)
        else:
            return np.nan
    except:
        return np.nan

def clean_and_transform_data(excel_path):
    """
    Limpia y transforma los datos del Excel de Wyscout para el análisis del Barça
    """
    # Leer el Excel
    df = pd.read_excel(excel_path)
    
    print("\nColumnas originales:")
    print(df.columns.tolist())
    
    # Filtrar solo los datos del Barcelona (eliminar filas de "Opponents")
    df = df[df['Team'] == 'Barcelona'].copy()
    
    print("\nPrimeras filas de datos originales:")
    print(df.head())
    
    # Convertir columnas combinadas
    for col in df.columns:
        if '/' in str(col):
            parts = col.split('/')
            total_col = parts[0].strip()
            df[total_col] = df[col].apply(lambda x: split_and_convert(x, 0))
            if len(parts) > 1:
                for i, part in enumerate(parts[1:], 1):
                    accurate_col = part.strip()
                    df[accurate_col] = df[col].apply(lambda x: split_and_convert(x, i))
    
    print("\nColumnas después de la transformación:")
    print(df.columns.tolist())
    
    # Limpiar y transformar columnas
    transformed_data = {
        'Match_ID': range(1, len(df) + 1),
        'Date': pd.to_datetime(df['Date']),
        'xG': df['xG'].astype(float),
        'Goals': df['Goals'].astype(float),
        'Total_shots': df['Shots'].astype(float),
        'Shots_on_target': df['on target'].astype(float),
        'Total_passes': df['Passes'].astype(float),
        'Total_passes_accurate': df['accurate'].astype(float),
        'Forward_passes': df['Forward passes'].astype(float),
        'Forward_passes_accurate': df['accurate'].astype(float),
        'Long_passes': df['Long passes'].astype(float),
        'Long_passes_accurate': df['accurate'].astype(float),
        'Recoveries_High': df['Recoveries / Low / Medium / High'].apply(lambda x: split_and_convert(x, 3)),
        'Recoveries_Medium': df['Recoveries / Low / Medium / High'].apply(lambda x: split_and_convert(x, 2)),
        'Recoveries_Low': df['Recoveries / Low / Medium / High'].apply(lambda x: split_and_convert(x, 1)),
        'Possession_Losses_High': df['Losses / Low / Medium / High'].apply(lambda x: split_and_convert(x, 3)),
        'Counterattacks_with_shots': df['Counterattacks / with shots'].apply(lambda x: split_and_convert(x, 1)),
        'Deep_completed_passes': df['Deep completed passes'].astype(float),
        'Crosses_accurate': df['Crosses / accurate'].apply(lambda x: split_and_convert(x, 1)),
        'Aerial_duels_won': df['Aerial duels / won'].apply(lambda x: split_and_convert(x, 1)),
        'Aerial_duels_total': df['Aerial duels / won'].apply(lambda x: split_and_convert(x, 0)),
        'Set_pieces_with_shots': df['Set pieces / with shots'].apply(lambda x: split_and_convert(x, 1)),
        'Match_tempo': df['Match tempo'].astype(float),
        'Positional_attacks': df['Positional attacks / with shots'].apply(lambda x: split_and_convert(x, 0)),
        'Interceptions': df['Interceptions'].astype(float),
        'Clearances': df['Clearances'].astype(float),
        'PPDA': df['PPDA'].astype(float)
    }
    
    # Crear DataFrame limpio
    df_clean = pd.DataFrame(transformed_data)
    
    # Crear DataFrame de partido (para métricas de liga)
    df_match = pd.DataFrame({
        'Match_ID': df_clean['Match_ID'],
        'Date': df_clean['Date'],
        'PSxGA': df['PSxGA'].astype(float),
        'PPDA_league_avg': df['PPDA'].astype(float).mean()
    })
    
    return df_clean, df_match

if __name__ == "__main__":
    # Ruta al archivo Excel
    excel_path = 'Datos/Wyscout Liga/Team Stats Barcelona.xlsx'
    
    # Transformar datos
    print("Iniciando transformación de datos...")
    df_team, df_match = clean_and_transform_data(excel_path)
    
    # Verificar datos antes de guardar
    print("\nVerificando datos transformados:")
    print("\nColumnas en df_team:")
    print(df_team.columns.tolist())
    print("\nPrimeras filas de df_team:")
    print(df_team.head())
    
    # Guardar los DataFrames procesados
    df_team.to_csv('Datos/processed/team_stats.csv', index=False)
    df_match.to_csv('Datos/processed/match_stats.csv', index=False)
    
    print("\nDatos guardados exitosamente en:")
    print("- Datos/processed/team_stats.csv")
    print("- Datos/processed/match_stats.csv") 