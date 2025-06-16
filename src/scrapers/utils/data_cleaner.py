import pandas as pd
import numpy as np
from typing import Dict, List

def clean_column_name(column: str) -> str:
    """
    Limpia el nombre de una columna para hacerlo más manejable
    
    Args:
        column: Nombre de la columna a limpiar
        
    Returns:
        Nombre de columna limpio
    """
    # Reemplazar caracteres especiales y espacios
    clean = column.strip()
    clean = clean.replace(' ', '_')
    clean = clean.replace('/', '_per_')
    clean = clean.replace('%', 'pct')
    clean = clean.replace('+/-', 'plus_minus')
    
    return clean

def process_numeric_column(df: pd.DataFrame, column: str) -> pd.Series:
    """
    Procesa una columna numérica, convirtiendo strings a números
    
    Args:
        df: DataFrame que contiene la columna
        column: Nombre de la columna a procesar
        
    Returns:
        Serie con los valores numéricos procesados
    """
    try:
        # Reemplazar valores no numéricos
        df[column] = df[column].replace('--', np.nan)
        
        # Convertir porcentajes
        if '%' in str(df[column].iloc[0]):
            df[column] = df[column].str.rstrip('%').astype('float') / 100.0
        else:
            df[column] = pd.to_numeric(df[column], errors='coerce')
            
        return df[column]
        
    except Exception:
        return df[column]

def split_combined_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Divide columnas que contienen múltiples estadísticas
    
    Args:
        df: DataFrame a procesar
        
    Returns:
        DataFrame con las columnas divididas
    """
    # Lista de columnas a dividir y sus nuevos nombres
    combined_cols = {
        'Shots/90': ['Shots_per_90', 'Shots_on_Target_per_90'],
        'Goals/Shots': ['Goals_per_Shot', 'Goals_per_Shot_on_Target'],
        'Passes/90': ['Passes_per_90', 'Passes_Completed_per_90'],
        'Tackles/Int': ['Tackles_per_90', 'Interceptions_per_90']
    }
    
    for col, new_cols in combined_cols.items():
        if col in df.columns:
            try:
                # Dividir la columna por '/'
                split_data = df[col].str.split('/', expand=True)
                
                # Asignar los valores a las nuevas columnas
                for i, new_col in enumerate(new_cols):
                    df[new_col] = process_numeric_column(split_data, i)
                    
                # Eliminar la columna original
                df = df.drop(columns=[col])
                
            except Exception:
                continue
                
    return df

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula métricas derivadas a partir de las estadísticas base
    
    Args:
        df: DataFrame con las estadísticas base
        
    Returns:
        DataFrame con las métricas derivadas añadidas
    """
    try:
        # Verticality Index
        if all(col in df.columns for col in ['Progressive_Passes', 'Total_Passes']):
            df['Verticality_Index'] = df['Progressive_Passes'] / df['Total_Passes']
            
        # Counter Press Success Rate
        if all(col in df.columns for col in ['Successful_Pressures', 'Pressures']):
            df['CounterPress_Success_pct'] = df['Successful_Pressures'] / df['Pressures']
            
        # Expected Goal Contribution
        if all(col in df.columns for col in ['xG', 'xA']):
            df['xG_Contribution'] = df['xG'] + df['xA']
            
        # Defensive Action Success Rate
        if all(col in df.columns for col in ['Successful_Tackles', 'Tackles']):
            df['Defensive_Action_Success_pct'] = df['Successful_Tackles'] / df['Tackles']
            
    except Exception:
        pass
        
    return df

def clean_fbref_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Función principal que limpia y procesa los datos de FBref
    
    Args:
        df: DataFrame con los datos crudos de FBref
        
    Returns:
        DataFrame limpio y procesado
    """
    # Crear copia para no modificar el original
    df_clean = df.copy()
    
    # Limpiar nombres de columnas
    df_clean.columns = [clean_column_name(col) for col in df_clean.columns]
    
    # Procesar columnas numéricas
    numeric_columns = df_clean.select_dtypes(include=['object']).columns
    for col in numeric_columns:
        df_clean[col] = process_numeric_column(df_clean, col)
        
    # Dividir estadísticas combinadas
    df_clean = split_combined_stats(df_clean)
    
    # Calcular métricas derivadas
    df_clean = calculate_derived_metrics(df_clean)
    
    return df_clean 