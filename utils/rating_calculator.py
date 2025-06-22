import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
import logging

class RatingCalculator:
    """Sistema completo de cálculo de rating para jugadores de fútbol"""
    
    def __init__(self, profiles_file_path: str = "rating_profiles.xlsx"):
        self.profiles_file_path = profiles_file_path
        self.profiles_data = {}
        self.league_multipliers = {
            'Premier League': 2.0, 'La Liga': 2.0, 'Serie A': 2.0, 
            'Bundesliga': 2.0, 'Ligue 1': 2.0,
            'Liga Portugal': 1.5, 'Eredivisie': 1.5, 'Süper Lig': 1.5,
            'default': 1.0
        }
        self._load_profiles()
    
    def _load_profiles(self):
        """Cargar perfiles desde Excel"""
        try:
            if not os.path.exists(self.profiles_file_path):
                print(f"⚠️ Archivo no encontrado: {self.profiles_file_path}")
                return
            
            df = pd.read_excel(self.profiles_file_path, sheet_name='Profiles')
            self.profiles_data = self._parse_profiles_structure(df)
            print(f"✅ {len(self.profiles_data)} perfiles cargados")
            
        except Exception as e:
            print(f"❌ Error cargando perfiles: {str(e)}")
    
    def _parse_profiles_structure(self, df: pd.DataFrame) -> Dict:
        """Parsear estructura del Excel"""
        profiles = {}
        
        # Perfiles conocidos basados en el análisis previo
        known_profiles = [
            (0, 'GK - Sweeper'), (5, 'CB - Ball‑Playing'), (10, 'LB/RB - Defensive'),
            (15, 'CDM - Deep‑Lying'), (20, 'CM - Box‑to‑Box'), (25, 'CAM - Advanced Playmaker'),
            (30, 'LW/RW - Wide Playmaker'), (35, 'ST - Target Man')
        ]
        
        # Datos de métricas hardcodeados basados en el análisis del Excel
        hardcoded_profiles = {
            'Sweeper': {
                'sin_balon': {'#OPA /90': 20, 'Crosses Stopped %': 13, 'PSxG +/-': 17},
                'con_balon': {'Headed shots /90': 13, 'Shots /90': 16.66, 'Key passes /90': 16.67, 'npxG /90': 16.67}
            },
            'Ball Playing': {
                'sin_balon': {'Blocks /90': 16.66, 'Clearances /90': 16.67, 'Aerial Win %': 16.67},
                'con_balon': {'Progressive passes /90': 20, 'Pass Completion %': 16.67, 'Long Pass Cmp %': 13}
            },
            'Box-to-Box': {
                'sin_balon': {'Tackles+Interceptions /90': 20, 'Ball Recoveries /90': 16.67, 'Fouls Committed /90': 16.67},
                'con_balon': {'Progressive passes /90': 17, 'Pass Completion %': 16.67, 'Key passes /90': 20}
            },
            'Advanced Playmaker': {
                'sin_balon': {'Interceptions Att 3rd /90': 16.67, 'Ball Recoveries /90': 16.67},
                'con_balon': {'Touches in box /90': 16.66, 'Key passes /90': 20, 'Progressive passes /90': 13}
            },
            'Wide Playmaker': {
                'sin_balon': {'Ball Recoveries /90': 16.67, 'Fouls Drawn /90': 16.67},
                'con_balon': {'xA /90': 17, 'Key passes /90': 20, 'Progressive passes /90': 13}
            },
            'Target Man': {
                'sin_balon': {'Aerial Duels Contested /90': 20, 'Offsides /90': 16.67},
                'con_balon': {'Headed shots /90': 13, 'Shots /90': 16.66, 'Goals /90': 20, 'npxG /90': 16.67}
            }
        }
        
        # Usar datos hardcodeados como fallback
        profiles.update(hardcoded_profiles)
        
        # Intentar parsing dinámico como backup
        profile_columns = []
        for i, col in enumerate(df.columns):
            if any(x in str(col) for x in ['GK', 'CB', 'LB', 'RB', 'CDM', 'CM', 'CAM', 'LW', 'RW', 'ST']):
                profile_columns.append((i, col))
        
        # Procesar cada perfil dinámicamente (si funciona, sobrescribe hardcoded)
        for col_idx, profile_name in profile_columns:
            try:
                profile_data = self._extract_profile_metrics(df, col_idx)
                if profile_data and len(profile_data['sin_balon']) + len(profile_data['con_balon']) > 2:
                    clean_name = self._clean_profile_name(profile_name)
                    profiles[clean_name] = profile_data
            except Exception as e:
                continue
        
        return profiles
    
    def _extract_profile_metrics(self, df: pd.DataFrame, start_col: int) -> Optional[Dict]:
        """Extraer métricas de un perfil"""
        try:
            profile_data = {'sin_balon': {}, 'con_balon': {}}
            
            # Procesar todas las filas
            for row_idx in range(len(df)):
                row = df.iloc[row_idx]
                
                # Sin balón (columnas +1 y +2)
                if start_col + 1 < len(row) and start_col + 2 < len(row):
                    metric = str(row.iloc[start_col + 1]).strip()
                    weight = row.iloc[start_col + 2]
                    
                    if (metric and metric != 'nan' and metric != 'NaN' and 
                        'Metric' not in metric and len(metric) > 2 and
                        not pd.isna(weight) and str(weight).replace('.','').isdigit()):
                        try:
                            profile_data['sin_balon'][metric] = float(weight)
                        except:
                            pass
                
                # Con balón (columnas +3 y +4)  
                if start_col + 3 < len(row) and start_col + 4 < len(row):
                    metric = str(row.iloc[start_col + 3]).strip()
                    weight = row.iloc[start_col + 4]
                    
                    if (metric and metric != 'nan' and metric != 'NaN' and 
                        'Metric' not in metric and len(metric) > 2 and
                        not pd.isna(weight) and str(weight).replace('.','').isdigit()):
                        try:
                            profile_data['con_balon'][metric] = float(weight)
                        except:
                            pass
            
            # Validar que tiene métricas
            total_metrics = len(profile_data['sin_balon']) + len(profile_data['con_balon'])
            return profile_data if total_metrics > 0 else None
            
        except Exception as e:
            print(f"Error procesando perfil col {start_col}: {str(e)}")
            return None
    
    def _clean_profile_name(self, name: str) -> str:
        """Limpiar nombres de perfiles"""
        mapping = {
            'GK - Sweeper': 'Sweeper', 'GK - Line Keeper': 'Line Keeper', 
            'GK - Traditional': 'Traditional', 'CB - Ball‑Playing': 'Ball Playing',
            'CB - Stopper': 'Stopper', 'CB - Sweeper': 'Sweeper',
            'LB/RB - Defensive': 'Defensive', 'LB/RB - Progressive': 'Progressive',
            'LB/RB - Offensive': 'Offensive', 'CDM - Deep‑Lying': 'Deep Lying',
            'CDM - Box‑to‑Box Destroyer': 'Holding', 'CDM - Holding': 'Holding',
            'CM - Box‑to‑Box': 'Box-to-Box', 'CM - Playmaker': 'Playmaker',
            'CM - Defensive': 'Defensive', 'CAM - Advanced Playmaker': 'Advanced Playmaker',
            'CAM - Shadow Striker': 'Shadow Striker', 'CAM - Dribbling Creator': 'Dribbling Creator',
            'LW/RW - Wide Playmaker': 'Wide Playmaker', 'LW/RW - Direct Winger': 'Direct Winger',
            'LW/RW - Hybrid': 'Hybrid', 'ST - Target Man': 'Target Man',
            'ST - Poacher': 'Poacher', 'ST - Playmaker': 'Playmaker'
        }
        return mapping.get(name, name)
    
    def calculate_player_rating(self, player_data: Dict, position: str, profile: str) -> float:
        """Calcular rating de un jugador"""
        try:
            profile_key = self._find_profile_key(position, profile)
            if not profile_key:
                return self._calculate_basic_rating(player_data)
            
            profile_config = self.profiles_data[profile_key]
            base_rating = self._calculate_weighted_rating(player_data, profile_config)
            final_rating = self._apply_modifiers(base_rating, player_data)
            
            return max(40, min(99, round(final_rating, 1)))
            
        except Exception as e:
            return self._calculate_basic_rating(player_data)
    
    def _find_profile_key(self, position: str, profile: str) -> Optional[str]:
        """Encontrar clave del perfil"""
        # Buscar coincidencia exacta
        for key in self.profiles_data.keys():
            if profile.lower() in key.lower():
                return key
        
        # Buscar por posición
        position_keywords = {
            'GK': ['sweeper', 'line keeper', 'traditional'],
            'CB': ['ball playing', 'stopper', 'sweeper'],
            'RB': ['defensive', 'progressive', 'offensive'],
            'LB': ['defensive', 'progressive', 'offensive'],
            'CDM': ['deep lying', 'holding'],
            'CM': ['box-to-box', 'playmaker', 'defensive'],
            'CAM': ['advanced playmaker', 'shadow striker', 'dribbling creator'],
            'RW': ['wide playmaker', 'direct winger', 'hybrid'],
            'LW': ['wide playmaker', 'direct winger', 'hybrid'],
            'ST': ['target man', 'poacher', 'playmaker']
        }
        
        keywords = position_keywords.get(position, [])
        for keyword in keywords:
            for key in self.profiles_data.keys():
                if keyword.lower() in key.lower():
                    return key
        
        return None
    
    def _calculate_weighted_rating(self, player_data: Dict, profile_config: Dict) -> float:
        """Calcular rating con pesos"""
        total_score = 0
        total_weight = 0
        
        # Sin balón
        for metric, weight in profile_config['sin_balon'].items():
            value = self._get_metric_value(player_data, metric)
            if value is not None:
                normalized = self._normalize_metric(metric, value)
                total_score += normalized * (weight / 100)
                total_weight += weight / 100
        
        # Con balón
        for metric, weight in profile_config['con_balon'].items():
            value = self._get_metric_value(player_data, metric)
            if value is not None:
                normalized = self._normalize_metric(metric, value)
                total_score += normalized * (weight / 100)
                total_weight += weight / 100
        
        if total_weight > 0:
            return 40 + (total_score / total_weight) * 0.59
        else:
            return 65
    
    def _get_metric_value(self, player_data: Dict, metric: str) -> Optional[float]:
        """Obtener valor de métrica con mapeo"""
        mapping = {
            '#OPA /90': ['Saves', 'OPA_90'],
            'PSxG +/-': ['PSxG', 'Post_Shot_xG'],
            'Save %': ['Save_Percentage', 'Save_Pct'],
            'Tackles /90': ['Tackles_90', 'Tackles'],
            'Interceptions /90': ['Interceptions_90', 'Interceptions'],
            'Pass Completion %': ['Pass_Completion_Percentage', 'Pass_Pct'],
            'Goals /90': ['Goals_90', 'Goals'],
            'npxG /90': ['npxG_90', 'npxG'],
            'xA /90': ['xA_90', 'xA'],
            'Shots /90': ['Shots_90', 'Shots'],
            'Key passes /90': ['Key_Passes_90', 'Key_Passes']
        }
        
        # Buscar directo
        if metric in player_data:
            return float(player_data[metric]) if pd.notna(player_data[metric]) else None
        
        # Buscar en mapeo
        alternatives = mapping.get(metric, [])
        for alt in alternatives:
            if alt in player_data:
                return float(player_data[alt]) if pd.notna(player_data[alt]) else None
        
        # Búsqueda flexible
        clean_metric = metric.lower().replace(' ', '_').replace('/', '_').replace('-', '_')
        for key in player_data.keys():
            if clean_metric in key.lower():
                return float(player_data[key]) if pd.notna(player_data[key]) else None
        
        return None
    
    def _normalize_metric(self, metric: str, value: float) -> float:
        """Normalizar métrica 0-100"""
        metric_lower = metric.lower()
        
        if '%' in metric_lower or 'percentage' in metric_lower:
            return min(100, max(0, value))
        elif '/90' in metric:
            if 'goal' in metric_lower:
                return min(100, max(0, (value / 2.0) * 100))
            elif 'assist' in metric_lower or 'xa' in metric_lower:
                return min(100, max(0, (value / 1.5) * 100))
            elif 'shot' in metric_lower:
                return min(100, max(0, (value / 8.0) * 100))
            elif 'pass' in metric_lower:
                return min(100, max(0, (value / 100) * 100))
            elif 'tackle' in metric_lower:
                return min(100, max(0, (value / 8.0) * 100))
            elif 'interception' in metric_lower:
                return min(100, max(0, (value / 5.0) * 100))
            elif 'save' in metric_lower or 'opa' in metric_lower:
                return min(100, max(0, (value / 8.0) * 100))
            else:
                return min(100, max(0, (value / 5.0) * 100))
        else:
            return min(100, max(0, (value / 10.0) * 100))
    
    def _apply_modifiers(self, base_rating: float, player_data: Dict) -> float:
        """Aplicar modificadores"""
        rating = base_rating
        
        # Liga
        league = player_data.get('Liga', player_data.get('League', ''))
        multiplier = self.league_multipliers.get(league, 1.0)
        if multiplier > 1.0:
            rating += (multiplier - 1.0) * 5
        
        # Minutos
        minutes = player_data.get('Minutes', player_data.get('Min', 2700))
        if minutes < 900:
            rating -= (900 - minutes) / 900 * 10
        
        return rating
    
    def _calculate_basic_rating(self, player_data: Dict) -> float:
        """Rating básico"""
        base = 65
        market_value = player_data.get('Market_Value', player_data.get('Market Value', 0))
        if market_value > 50: base += 5
        elif market_value > 20: base += 3
        elif market_value > 10: base += 1
        return max(40, min(99, base))
    
    def bulk_calculate_ratings(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """Calcular ratings masivamente"""
        ratings = []
        for idx, player in players_df.iterrows():
            try:
                position = player.get('Position', 'CM')
                profile = player.get('Profile', 'All Profiles')
                if profile == 'All Profiles' or pd.isna(profile):
                    profile = self._get_default_profile(position)
                rating = self.calculate_player_rating(player.to_dict(), position, profile)
                ratings.append(rating)
            except:
                ratings.append(65.0)
        
        players_df = players_df.copy()
        players_df['Calculated_Rating'] = ratings
        return players_df
    
    def _get_default_profile(self, position: str) -> str:
        """Perfil por defecto"""
        defaults = {
            'GK': 'Sweeper', 'CB': 'Ball Playing', 'RB': 'Progressive',
            'LB': 'Progressive', 'CDM': 'Deep Lying', 'CM': 'Box-to-Box',
            'CAM': 'Advanced Playmaker', 'RW': 'Wide Playmaker',
            'LW': 'Wide Playmaker', 'ST': 'Target Man'
        }
        return defaults.get(position, 'Box-to-Box')
