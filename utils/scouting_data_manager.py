import pandas as pd
import streamlit as st
from typing import Optional
import os

from .data_loader import DataLoader
from .data_processor import DataProcessor

class ScoutingDataManager:
    """Gestor principal de datos para la herramienta de Scouting"""
    
    def __init__(self):
        self.loader = DataLoader()
        self.processor = DataProcessor()
        self._cached_data = None
        self._use_real_data = True  # Flag para usar datos reales o de muestra
        
    def get_consolidated_data(self, use_real_data: bool = True) -> pd.DataFrame:
        """Obtiene los datos consolidados de jugadores con caché persistente"""
        
        if not use_real_data:
            # Usar datos de muestra para testing
            return self.loader.get_sample_data()

        # Verificar si hay caché consolidado válido
        if self.loader._is_cache_valid(self.loader.cache_files['consolidated']):
            cached_data = self.loader._load_from_cache(self.loader.cache_files['consolidated'])
            if cached_data is not None:
                return cached_data

        try:
            # Cargar datos con caché individual
            norm_data = self.loader.load_normalization_data()
            fbref_df = self.loader.load_fbref_data()
            tm_df = self.loader.load_transfermarket_data()
            cap_df = self.loader.load_capology_data()
            
            # Consolidar datos
            consolidated_df = self.processor.consolidate_player_data(fbref_df, tm_df, cap_df, norm_data)
            
            if not consolidated_df.empty:
                # Guardar datos consolidados en caché
                self.loader._save_to_cache(consolidated_df, self.loader.cache_files['consolidated'])
                return consolidated_df
            else:
                return self.loader.get_sample_data()
                
        except Exception as e:
            st.error(f"❌ Error cargando datos reales: {e}")
            st.info("🔄 Usando datos de muestra...")
            return self.loader.get_sample_data()
    
    def get_player_data(self, use_real_data: bool = True) -> pd.DataFrame:
        """Método principal para obtener datos de jugadores"""
        return self.get_consolidated_data(use_real_data)
    
    def get_available_leagues(self, df: pd.DataFrame) -> list:
        """Obtiene las ligas disponibles en los datos"""
        # Buscar la columna de liga (puede ser 'League' o 'Liga')
        league_column = None
        if 'League' in df.columns:
            league_column = 'League'
        elif 'Liga' in df.columns:
            league_column = 'Liga'
        
        if league_column:
            leagues = df[league_column].unique().tolist()
            # Filtrar valores vacíos o unknown
            leagues = [l for l in leagues if l and l != 'Unknown']
            return sorted(leagues)
        return []
    
    def get_available_clubs(self, df: pd.DataFrame, league: Optional[str] = None) -> list:
        """Obtiene los clubes disponibles, opcionalmente filtrados por liga"""
        if 'Club' not in df.columns:
            return []
        
        # Determinar la columna de liga
        league_column = None
        if 'League' in df.columns:
            league_column = 'League'
        elif 'Liga' in df.columns:
            league_column = 'Liga'
            
        if league and league != "Todas las ligas" and league_column:
            filtered_df = df[df[league_column] == league]
            clubs = filtered_df['Club'].unique().tolist()
        else:
            clubs = df['Club'].unique().tolist()
        
        # Filtrar valores vacíos o unknown
        clubs = [c for c in clubs if c and c != 'Unknown']
        return sorted(clubs)
    
    def get_available_positions(self, df: pd.DataFrame) -> list:
        """Obtiene las posiciones disponibles en los datos"""
        if 'Position' in df.columns:
            return sorted(df['Position'].unique().tolist())
        return []
    
    def get_available_nationalities(self, df: pd.DataFrame) -> list:
        """Obtiene las nacionalidades disponibles en los datos"""
        if 'Nationality' in df.columns:
            nationalities = df['Nationality'].unique().tolist()
            # Filtrar valores vacíos o unknown
            nationalities = [n for n in nationalities if n and n != 'Unknown']
            return sorted(nationalities)
        return []
    
    def apply_filters(self, df: pd.DataFrame, filters: dict) -> pd.DataFrame:
        """Aplica filtros al DataFrame de jugadores"""
        filtered_df = df.copy()
        
        # Filtro por posición
        if filters.get('position') and filters['position'] != "All":
            filtered_df = filtered_df[filtered_df['Position'] == filters['position']]
        
        # Filtro por perfil (cuando esté implementado)
        if filters.get('profile') and filters['profile'] != "All Profiles":
            filtered_df = filtered_df[filtered_df['Profile'] == filters['profile']]
        
        # Filtro por edad
        if filters.get('age_range'):
            min_age, max_age = filters['age_range']
            filtered_df = filtered_df[(filtered_df['Age'] >= min_age) & (filtered_df['Age'] <= max_age)]
        
        # Filtro por rating
        if filters.get('rating_min'):
            filtered_df = filtered_df[filtered_df['Rating'] >= filters['rating_min']]
        
        # Filtro por altura
        if filters.get('height_range'):
            min_height, max_height = filters['height_range']
            filtered_df = filtered_df[(filtered_df['Height'] >= min_height) & (filtered_df['Height'] <= max_height)]
        
        # Filtro por pie dominante
        if filters.get('foot') and filters['foot'] != "Both":
            filtered_df = filtered_df[filtered_df['Foot'] == filters['foot']]
        
        # Filtro por nacionalidad
        if filters.get('nationality') and filters['nationality'] != "Todos los países":
            # Extraer código del país
            if ' – ' in filters['nationality']:
                country_code = filters['nationality'].split(' – ')[-1]
                filtered_df = filtered_df[filtered_df['Nationality'].str.contains(country_code, case=False, na=False)]
        
        # Filtro por valor de mercado
        if filters.get('market_value'):
            min_value, max_value = filters['market_value']
            filtered_df = filtered_df[(filtered_df['Market_Value'] >= min_value) & (filtered_df['Market_Value'] <= max_value)]
        
        # Filtro por salario
        if filters.get('max_salary'):
            filtered_df = filtered_df[filtered_df['Salary_Annual'] <= filters['max_salary']]
        
        # Filtro por fin de contrato
        if filters.get('contract_year') and filters['contract_year'] != "Todos":
            if isinstance(filters['contract_year'], int):
                filtered_df = filtered_df[filtered_df['Contract_End'] == filters['contract_year']]
        
        # Filtro específico para mercado libre (contratos que terminan en años específicos)
        if filters.get('contract_years') and filters['contract_years'] is not None:
            filtered_df = filtered_df[filtered_df['Contract_End'].isin(filters['contract_years'])]
        
        # Filtro por cláusula de rescisión
        if filters.get('has_clause') and filters['has_clause'] != "Todos":
            filtered_df = filtered_df[filtered_df['Has_Clause'] == filters['has_clause']]
        
        # Filtro por liga
        if filters.get('league') and filters['league'] != "Todas las ligas":
            # Determinar la columna de liga
            league_column = None
            if 'League' in filtered_df.columns:
                league_column = 'League'
            elif 'Liga' in filtered_df.columns:
                league_column = 'Liga'
            
            if league_column:
                filtered_df = filtered_df[filtered_df[league_column] == filters['league']]
        
        # Filtro por club
        if filters.get('club') and filters['club'] != "Todos los clubes":
            filtered_df = filtered_df[filtered_df['Club'] == filters['club']]
        
        return filtered_df
    
    def get_top_players_by_metric(self, df: pd.DataFrame, metric: str, top_n: int = 10) -> pd.DataFrame:
        """Obtiene los top N jugadores por una métrica específica"""
        if metric not in df.columns:
            return pd.DataFrame()
        
        return df.nlargest(top_n, metric)
    
    def get_player_stats_summary(self, df: pd.DataFrame) -> dict:
        """Obtiene un resumen estadístico de los datos de jugadores"""
        if df.empty:
            return {}
        
        summary = {
            'total_players': len(df),
            'total_leagues': df['League'].nunique() if 'League' in df.columns else 0,
            'total_clubs': df['Club'].nunique() if 'Club' in df.columns else 0,
            'avg_age': df['Age'].mean() if 'Age' in df.columns else 0,
            'avg_market_value': df['Market_Value'].mean() if 'Market_Value' in df.columns else 0,
            'avg_rating': df['Rating'].mean() if 'Rating' in df.columns else 0,
            'position_distribution': df['Position'].value_counts().to_dict() if 'Position' in df.columns else {},
            'league_distribution': df['League'].value_counts().to_dict() if 'League' in df.columns else {}
        }
        
        return summary
    
    def search_players(self, df: pd.DataFrame, search_term: str) -> pd.DataFrame:
        """Busca jugadores por nombre"""
        if not search_term or df.empty:
            return df
        
        # Buscar en nombre, club y liga
        mask = (
            df['Name'].str.contains(search_term, case=False, na=False) |
            df['Club'].str.contains(search_term, case=False, na=False) |
            df['League'].str.contains(search_term, case=False, na=False)
        )
        
        return df[mask]
    
    def export_filtered_data(self, df: pd.DataFrame, format: str = 'csv') -> bytes:
        """Exporta los datos filtrados en el formato especificado"""
        if format.lower() == 'csv':
            return df.to_csv(index=False).encode('utf-8')
        elif format.lower() == 'excel':
            import io
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False)
            return buffer.getvalue()
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    def get_comparison_data(self, df: pd.DataFrame, player_names: list) -> pd.DataFrame:
        """Obtiene datos para comparar jugadores específicos"""
        if not player_names or df.empty:
            return pd.DataFrame()
        
        comparison_df = df[df['Name'].isin(player_names)]
        
        # Seleccionar columnas relevantes para comparación
        comparison_cols = [
            'Name', 'Age', 'Position', 'Club', 'League', 'Rating',
            'Market_Value', 'Salary_Annual', 'Height', 'Foot',
            'xG_90', 'xA_90', 'Passes_Completed_90', 'Tackles_90', 'Interceptions_90'
        ]
        
        # Filtrar solo las columnas que existen
        existing_cols = [col for col in comparison_cols if col in comparison_df.columns]
        
        return comparison_df[existing_cols]
    
    def validate_data_quality(self, df: pd.DataFrame) -> dict:
        """Valida la calidad de los datos cargados"""
        if df.empty:
            return {'status': 'error', 'message': 'No hay datos disponibles'}
        
        required_columns = ['Name', 'Age', 'Position', 'Club', 'League']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return {
                'status': 'warning', 
                'message': f'Faltan columnas importantes: {missing_columns}'
            }
        
        # Verificar datos faltantes
        missing_data = df.isnull().sum()
        critical_missing = missing_data[missing_data > len(df) * 0.5]  # Más del 50% faltante
        
        if not critical_missing.empty:
            return {
                'status': 'warning',
                'message': f'Muchos datos faltantes en: {critical_missing.index.tolist()}'
            }
        
        return {
            'status': 'success',
            'message': f'Datos validados correctamente. {len(df)} jugadores disponibles.'
        } 