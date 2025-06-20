import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional
import re

class DataProcessor:
    """Clase para procesar y consolidar datos de jugadores de múltiples fuentes"""
    
    def __init__(self):
        self.position_mapping = {
            # Mapeo de posiciones de diferentes fuentes a nuestro estándar
            'goalkeeper': 'GK', 'gk': 'GK', 'portero': 'GK',
            'centre-back': 'CB', 'cb': 'CB', 'central': 'CB', 'defensa central': 'CB',
            'right-back': 'RB', 'rb': 'RB', 'lateral derecho': 'RB',
            'left-back': 'LB', 'lb': 'LB', 'lateral izquierdo': 'LB',
            'defensive midfield': 'CDM', 'cdm': 'CDM', 'mediocentro defensivo': 'CDM',
            'central midfield': 'CM', 'cm': 'CM', 'centrocampista': 'CM',
            'attacking midfield': 'CAM', 'cam': 'CAM', 'mediapunta': 'CAM',
            'right winger': 'RW', 'rw': 'RW', 'extremo derecho': 'RW',
            'left winger': 'LW', 'lw': 'LW', 'extremo izquierdo': 'LW',
            'centre-forward': 'ST', 'st': 'ST', 'striker': 'ST', 'delantero': 'ST'
        }
        
        self.nationality_mapping = {
            # Mapeo de códigos de país y nombres
            'esp': 'Spain – ESP', 'spain': 'Spain – ESP',
            'fra': 'France – FRA', 'france': 'France – FRA',
            'ger': 'Germany – GER', 'germany': 'Germany – GER',
            'ita': 'Italy – ITA', 'italy': 'Italy – ITA',
            'eng': 'England – ENG', 'england': 'England – ENG',
            'por': 'Portugal – POR', 'portugal': 'Portugal – POR',
            'bra': 'Brazil – BRA', 'brazil': 'Brazil – BRA',
            'arg': 'Argentina – ARG', 'argentina': 'Argentina – ARG',
            'ned': 'Netherlands – NED', 'netherlands': 'Netherlands – NED',
            'bel': 'Belgium – BEL', 'belgium': 'Belgium – BEL',
            'pol': 'Poland – POL', 'poland': 'Poland – POL',
            'cro': 'Croatia – CRO', 'croatia': 'Croatia – CRO',
            'uru': 'Uruguay – URU', 'uruguay': 'Uruguay – URU',
            'nor': 'Norway – NOR', 'norway': 'Norway – NOR',
            'tur': 'Turkey – TUR', 'turkey': 'Turkey – TUR'
        }
    
    def normalize_position(self, position: str) -> str:
        """Normaliza las posiciones a nuestro estándar"""
        if pd.isna(position) or position == "":
            return "Unknown"
            
        pos_clean = str(position).lower().strip()
        return self.position_mapping.get(pos_clean, position)
    
    def normalize_nationality(self, nationality: str) -> str:
        """Normaliza las nacionalidades al formato de la UI"""
        if pd.isna(nationality) or nationality == "":
            return "Unknown"
            
        nat_clean = str(nationality).lower().strip()
        
        # Si ya está en el formato correcto, devolverlo
        if ' – ' in nationality:
            return nationality
            
        # Buscar en el mapeo
        return self.nationality_mapping.get(nat_clean, f"{nationality} – UNK")
    
    def extract_numeric_value(self, value: str, currency_symbol: str = "€") -> float:
        """Extrae valores numéricos de strings con formato monetario"""
        if pd.isna(value) or value == "":
            return 0.0
            
        # Limpiar el string
        clean_value = str(value).replace(currency_symbol, "").replace(",", "").strip()
        
        # Buscar patrones como "25.5M", "1.2K", etc.
        if 'M' in clean_value.upper():
            numeric = re.findall(r'[\d.]+', clean_value)
            if numeric:
                return float(numeric[0]) * 1_000_000
        elif 'K' in clean_value.upper():
            numeric = re.findall(r'[\d.]+', clean_value)
            if numeric:
                return float(numeric[0]) * 1_000
        else:
            # Intentar extraer número directo
            numeric = re.findall(r'[\d.]+', clean_value)
            if numeric:
                return float(numeric[0])
                
        return 0.0
    
    def parse_contract_date(self, date_str: str) -> int:
        """Extrae el año de finalización del contrato"""
        if pd.isna(date_str) or date_str == "":
            return 2025  # Valor por defecto
            
        # Buscar año en el string
        years = re.findall(r'20\d{2}', str(date_str))
        if years:
            return int(years[-1])  # Tomar el último año encontrado
            
        return 2025
    
    def calculate_age_from_birth_date(self, birth_date: str) -> int:
        """Calcula la edad a partir de la fecha de nacimiento"""
        if pd.isna(birth_date) or birth_date == "":
            return 25  # Edad por defecto
            
        try:
            # Buscar año de nacimiento
            years = re.findall(r'19\d{2}|20\d{2}', str(birth_date))
            if years:
                birth_year = int(years[0])
                return 2024 - birth_year
        except:
            pass
            
        return 25
    
    def extract_height_cm(self, height_str: str) -> int:
        """Extrae la altura en centímetros"""
        if pd.isna(height_str) or height_str == "":
            return 175  # Altura por defecto
            
        height_clean = str(height_str).replace(",", ".")
        
        # Buscar patrones como "1,85m" o "185cm"
        if 'm' in height_clean and '.' in height_clean:
            # Formato como "1.85m"
            numeric = re.findall(r'[\d.]+', height_clean)
            if numeric:
                meters = float(numeric[0])
                return int(meters * 100)
        elif 'cm' in height_clean:
            # Formato como "185cm"
            numeric = re.findall(r'\d+', height_clean)
            if numeric:
                return int(numeric[0])
        else:
            # Intentar número directo
            numeric = re.findall(r'\d+', height_clean)
            if numeric:
                cm = int(numeric[0])
                # Si es muy pequeño, probablemente está en metros
                if cm < 3:
                    return cm * 100
                return cm
                
        return 175
    
    def assign_player_profile(self, position: str, stats: Dict) -> str:
        """Asigna un perfil de juego basado en la posición y estadísticas"""
        # Por ahora, perfiles básicos basados en posición
        # TODO: Implementar algoritmo más sofisticado basado en estadísticas
        
        profiles = {
            'GK': ['Sweeper', 'Line Keeper', 'Traditional'],
            'CB': ['Ball Playing', 'Stopper', 'Sweeper'],
            'RB': ['Defensive', 'Progressive', 'Offensive'],
            'LB': ['Defensive', 'Progressive', 'Offensive'],
            'CDM': ['Holding', 'Deep Lying', 'Box-to-Box'],
            'CM': ['Box-to-Box', 'Deep Lying', 'Holding'],
            'CAM': ['Advanced Playmaker', 'Shadow Striker', 'Dribbling Creator'],
            'RW': ['Direct Winger', 'Wide Playmaker', 'Hybrid'],
            'LW': ['Direct Winger', 'Wide Playmaker', 'Hybrid'],
            'ST': ['Poacher', 'Target Man', 'Playmaker']
        }
        
        position_profiles = profiles.get(position, ['All Profiles'])
        
        # Por ahora, asignar aleatoriamente
        # TODO: Implementar lógica basada en estadísticas
        import random
        return random.choice(position_profiles)
    
    def calculate_basic_rating(self, player_data: Dict, position: str) -> int:
        """Calcula un rating básico del jugador (40-99)"""
        # Sistema de rating simplificado por ahora
        # TODO: Implementar algoritmo más sofisticado
        
        base_rating = 60
        
        # Factores de liga (calidad de la liga)
        league_factors = {
            'La Liga': 1.0,
            'EPL': 1.0,
            'Premier League': 1.0,
            'Bundesliga': 0.95,
            'Serie A': 0.9,
            'Ligue 1': 0.85,
            'Primeira Liga': 0.8,
            'Eredivisie': 0.75,
            'Super Lig': 0.7
        }
        
        # Aplicar factor de liga
        league = player_data.get('League', 'Unknown')
        league_factor = league_factors.get(league, 0.7)
        
        # Ajuste por valor de mercado (indicador de calidad)
        market_value = player_data.get('Market_Value', 0)
        if market_value > 50:
            market_bonus = 15
        elif market_value > 20:
            market_bonus = 10
        elif market_value > 10:
            market_bonus = 5
        else:
            market_bonus = 0
        
        # Ajuste por edad (pico de rendimiento)
        age = player_data.get('Age', 25)
        if 24 <= age <= 28:
            age_bonus = 5
        elif 22 <= age <= 30:
            age_bonus = 2
        elif age < 20:
            age_bonus = -5  # Jóvenes con potencial pero menos experiencia
        elif age > 32:
            age_bonus = -3  # Veteranos en declive
        else:
            age_bonus = 0
        
        # Cálculo final
        final_rating = base_rating + (league_factor * 20) + market_bonus + age_bonus
        
        # Asegurar que esté en el rango 40-99
        return max(40, min(99, int(final_rating)))
    
    def process_fbref_player(self, player_row: pd.Series) -> Dict:
        """Procesa un jugador de FBREF y extrae métricas relevantes"""
        processed = {}
        
        # Información básica - probar diferentes variaciones de nombres de columnas
        processed['Name'] = (
            player_row.get('player_name') or 
            player_row.get('Player') or 
            player_row.get('Jugador') or 
            player_row.get('Name') or 
            'Unknown'
        )
        
        # Edad - probar diferentes formatos
        processed['Age'] = (
            player_row.get('Edad') or 
            player_row.get('Age') or 
            player_row.get('age') or 
            25
        )
        
        processed['League'] = player_row.get('Liga', 'Unknown')
        processed['Club'] = player_row.get('Equipo', 'Unknown')
        
        # Métricas de rendimiento - buscar en diferentes formatos de columnas
        # xG por 90 minutos
        xg_columns = ['xG/90', 'xG', 'Expected Goals', 'xG_90', 'xg_90']
        processed['xG_90'] = 0.0
        for col in xg_columns:
            if col in player_row and pd.notna(player_row[col]):
                try:
                    processed['xG_90'] = float(player_row[col])
                    break
                except:
                    continue
        
        # xA por 90 minutos
        xa_columns = ['xAG/90', 'xA/90', 'xA', 'Expected Assists', 'xA_90', 'xa_90']
        processed['xA_90'] = 0.0
        for col in xa_columns:
            if col in player_row and pd.notna(player_row[col]):
                try:
                    processed['xA_90'] = float(player_row[col])
                    break
                except:
                    continue
        
        # Pases completados
        pass_columns = ['Cmp', 'Passes Completed', 'Pases Completados', 'Pass_Cmp']
        processed['Passes_Completed_90'] = 30.0
        for col in pass_columns:
            if col in player_row and pd.notna(player_row[col]):
                try:
                    processed['Passes_Completed_90'] = float(player_row[col])
                    break
                except:
                    continue
        
        # Tackles
        tackle_columns = ['Tkl', 'Tackles', 'Entradas', 'Tkl_90']
        processed['Tackles_90'] = 1.0
        for col in tackle_columns:
            if col in player_row and pd.notna(player_row[col]):
                try:
                    processed['Tackles_90'] = float(player_row[col])
                    break
                except:
                    continue
        
        # Intercepciones
        int_columns = ['Int', 'Interceptions', 'Intercepciones', 'Int_90']
        processed['Interceptions_90'] = 0.5
        for col in int_columns:
            if col in player_row and pd.notna(player_row[col]):
                try:
                    processed['Interceptions_90'] = float(player_row[col])
                    break
                except:
                    continue
        
        return processed
    
    def process_transfermarket_player(self, player_row: pd.Series) -> Dict:
        """Procesa un jugador de Transfermarket"""
        processed = {}
        
        # Información básica
        processed['Name'] = player_row.get('Name', 'Unknown')
        processed['Position'] = self.normalize_position(player_row.get('Position', 'Unknown'))
        processed['Nationality'] = self.normalize_nationality(player_row.get('Nationality', 'Unknown'))
        processed['Height'] = self.extract_height_cm(player_row.get('Height', '175'))
        processed['Foot'] = player_row.get('Foot', 'Right').title()
        
        # Información económica
        processed['Market_Value'] = self.extract_numeric_value(player_row.get('Market Value', '0')) / 1_000_000  # En millones
        processed['Contract_End'] = self.parse_contract_date(player_row.get('Contract Until', '2025'))
        
        # Calcular edad si hay fecha de nacimiento
        if 'Date of Birth/Age' in player_row:
            processed['Age'] = self.calculate_age_from_birth_date(player_row['Date of Birth/Age'])
        
        return processed
    
    def process_capology_player(self, player_row: pd.Series) -> Dict:
        """Procesa un jugador de Capology (datos salariales)"""
        processed = {}
        
        # Información básica
        processed['Name'] = player_row.get('Jugador', 'Unknown')
        
        # Información salarial
        processed['Salary_Annual'] = self.extract_numeric_value(player_row.get('Bruto Anual', '0'))
        processed['Contract_End'] = self.parse_contract_date(player_row.get('Expiración', '2025'))
        
        # Cláusula de rescisión
        clause_value = player_row.get('Cláusula De Rescisión', '')
        processed['Has_Clause'] = "Sí" if clause_value and clause_value != '' else "No"
        processed['Release_Clause'] = self.extract_numeric_value(clause_value) / 1_000_000 if clause_value else 0
        
        return processed
    
    @st.cache_data
    def consolidate_player_data(_self, fbref_df: pd.DataFrame, tm_df: pd.DataFrame, 
                               cap_df: pd.DataFrame, norm_data: Dict) -> pd.DataFrame:
        """Consolida todos los datos de jugadores en un DataFrame unificado"""
        
        consolidated_players = []
        
        # Procesar datos de FBREF como base (tienen las métricas de rendimiento)
        if not fbref_df.empty:
            for _, player_row in fbref_df.iterrows():
                try:
                    player_data = _self.process_fbref_player(player_row)
                    
                    # Buscar datos complementarios en Transfermarket
                    if not tm_df.empty:
                        # Intentar match por nombre (simplificado por ahora)
                        tm_match = tm_df[tm_df['Name'].str.contains(player_data['Name'], case=False, na=False)]
                        if not tm_match.empty:
                            tm_data = _self.process_transfermarket_player(tm_match.iloc[0])
                            player_data.update(tm_data)
                    
                    # Buscar datos salariales en Capology
                    if not cap_df.empty:
                        cap_match = cap_df[cap_df['Jugador'].str.contains(player_data['Name'], case=False, na=False)]
                        if not cap_match.empty:
                            cap_data = _self.process_capology_player(cap_match.iloc[0])
                            player_data.update(cap_data)
                    
                    # Completar campos faltantes con valores por defecto
                    _self._fill_missing_fields(player_data)
                    
                    # Calcular rating
                    player_data['Rating'] = _self.calculate_basic_rating(player_data, player_data.get('Position', 'Unknown'))
                    
                    # Asignar perfil
                    player_data['Profile'] = _self.assign_player_profile(player_data.get('Position', 'Unknown'), player_data)
                    
                    consolidated_players.append(player_data)
                    
                except Exception as e:
                    continue  # Saltar jugadores problemáticos
        
        # Si no hay datos de FBREF, usar Transfermarket como base
        elif not tm_df.empty:
            for _, player_row in tm_df.iterrows():
                try:
                    player_data = _self.process_transfermarket_player(player_row)
                    
                    # Buscar datos salariales
                    if not cap_df.empty:
                        cap_match = cap_df[cap_df['Jugador'].str.contains(player_data['Name'], case=False, na=False)]
                        if not cap_match.empty:
                            cap_data = _self.process_capology_player(cap_match.iloc[0])
                            player_data.update(cap_data)
                    
                    _self._fill_missing_fields(player_data)
                    player_data['Rating'] = _self.calculate_basic_rating(player_data, player_data.get('Position', 'Unknown'))
                    player_data['Profile'] = _self.assign_player_profile(player_data.get('Position', 'Unknown'), player_data)
                    
                    consolidated_players.append(player_data)
                    
                except Exception as e:
                    continue
        
        if consolidated_players:
            return pd.DataFrame(consolidated_players)
        else:
            return pd.DataFrame()
    
    def _fill_missing_fields(self, player_data: Dict) -> None:
        """Completa campos faltantes con valores por defecto"""
        defaults = {
            'Age': 25,
            'Position': 'Unknown',
            'Nationality': 'Unknown',
            'Height': 175,
            'Foot': 'Right',
            'Market_Value': 5.0,
            'Salary_Annual': 1_000_000,
            'Contract_End': 2025,
            'Has_Clause': 'No',
            'Release_Clause': 0,
            'xG_90': 0.1,
            'xA_90': 0.1,
            'Passes_Completed_90': 30,
            'Tackles_90': 1.0,
            'Interceptions_90': 0.5,
            'Distance_Covered_90': 10.0,
            'League': 'Unknown',
            'Club': 'Unknown'
        }
        
        for field, default_value in defaults.items():
            if field not in player_data or pd.isna(player_data[field]):
                player_data[field] = default_value 