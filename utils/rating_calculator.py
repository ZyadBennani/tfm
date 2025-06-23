import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
import logging

try:
    import scipy.stats as stats
except ImportError:
    print("⚠️ scipy no disponible - usando distribución simplificada")
    stats = None

class RatingCalculator:
    """Sistema completo de cálculo de rating para jugadores de fútbol"""
    
    def __init__(self, profiles_file_path: str = "rating_profiles.xlsx"):
        self.profiles_file_path = profiles_file_path
        self.profiles_data = {}
        # MULTIPLICADORES EQUILIBRADOS
        self.league_multipliers = {
            'Premier League': 1.5, 'La Liga': 1.5, 'Serie A': 1.5, 
            'Bundesliga': 1.5, 'Ligue 1': 1.5,  # Equilibrado: 1.5 para top 5
            'Liga Portugal': 1.3, 'Eredivisie': 1.3, 'Süper Lig': 1.3,  # 1.3 para segundo tier
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
        
        # TODOS LOS PERFILES (3 por posición) - Datos completos del Excel
        hardcoded_profiles = {
            # PORTEROS (3 perfiles)
            'Sweeper': {
                'sin_balon': {'#OPA /90': 20, 'Crosses Stopped %': 13, 'PSxG +/-': 17, 'Clean‑Sheet %': 16.66, 'Pen Save %': 16.67},
                'con_balon': {'Long pass completion %': 16.66, 'Touches outside box /90': 16.67, 'Progressive passes /90': 16.67}
            },
            'Line Keeper': {
                'sin_balon': {'Save %': 20, 'PSxG +/-': 17, 'Shots‑on‑Target Against': 13, 'Clean‑Sheet %': 16.66, 'Pen Save %': 16.67},
                'con_balon': {'Launch %': 16.67}
            },
            'Traditional': {
                'sin_balon': {'Save %': 20, 'Clean‑Sheet %': 13, 'Crosses Stopped %': 17, 'GA /90': 16.66},
                'con_balon': {'Launch %': 16.67, 'Goal Kicks Avg Length': 16.67}
            },
            
            # DEFENSAS CENTRALES (3 perfiles)
            'Ball Playing': {
                'sin_balon': {'Blocks /90': 16.66, 'Clearances /90': 16.67, 'Aerial Win %': 16.67, 'Tackles /90': 20, 'Interceptions /90': 20},
                'con_balon': {'Progressive passes /90': 20, 'Pass Completion %': 16.67, 'Long Pass Cmp %': 13, 'Passes into Final 3rd /90': 17}
            },
            'Stopper': {
                'sin_balon': {'Tackles /90': 20, 'Aerial Duels Contested': 17, 'Aerial Win %': 13, 'Blocks /90': 16.67, 'Fouls Committed /90': 16.66},
                'con_balon': {}
            },
            'Sweeper': {
                'sin_balon': {'Interceptions /90': 20, 'Clearances /90': 17, 'Blocks /90': 13, 'Ball Recoveries /90': 16.66},
                'con_balon': {'Progressive passes /90': 16.67, 'Pass Completion %': 16.67, 'Carries into Final 3rd /90': 16.66}
            },
            
            # LATERALES (3 perfiles)
            'Defensive': {
                'sin_balon': {'Tackles Def 3rd /90': 20, 'Interceptions /90': 17, 'Blocks /90': 16.66, 'Ball Recoveries /90': 16.67, 'Clearances /90': 16.67},
                'con_balon': {'Pass Completion %': 16.67, 'Progressive passes /90': 20, 'Passes into Final 3rd /90': 13}
            },
            'Progressive': {
                'sin_balon': {'Tackles Mid 3rd /90': 16.66, 'Interceptions /90': 16.67, 'Ball Recoveries /90': 16.67},
                'con_balon': {'Progressive carries /90': 20, 'Progressive passes /90': 17, 'Pass Completion %': 16.67, 'Touches in Final 3rd /90': 13}
            },
            'Offensive': {
                'sin_balon': {'Tackles Att 3rd /90': 16.67, 'Ball Recoveries /90': 16.67},
                'con_balon': {'Crossing accuracy %': 20, 'Dribbles completed /90': 17, 'Touches in Final 3rd /90': 13, 'Carries into Final 3rd /90': 16.66}
            },
            
            # MEDIOCENTROS DEFENSIVOS (3 perfiles)
            'Deep Lying': {
                'sin_balon': {'Tackles+Interceptions /90': 20, 'Ball Recoveries /90': 16.67, 'Fouls Committed /90': 16.67, 'Blocks Shots /90': 17, 'Clearances /90': 16.66},
                'con_balon': {'Progressive Carries /90': 13, 'Passes Under Pressure /90': 16.67, 'Pass Completion %': 16.67}
            },
            'Holding': {
                'sin_balon': {'Tackles Def 3rd /90': 20, 'Blocks Shots /90': 17, 'Interceptions /90': 13, 'Clearances /90': 16.66},
                'con_balon': {'Passes Under Pressure /90': 16.67, 'Pass Completion %': 16.67}
            },
            'Box-to-Box Destroyer': {
                'sin_balon': {'Tackles+Interceptions /90': 20, 'Duels Won %': 17, 'Ball Recoveries /90': 16.66, 'Fouls Committed /90': 16.66, 'Interceptions /90': 17, 'Clearances /90': 13},
                'con_balon': {'Progressive Carries /90': 13, 'Pass Completion %': 16.67}
            },
            
            # MEDIOCENTROS (3 perfiles)
            'Box-to-Box': {
                'sin_balon': {'Tackles+Interceptions /90': 20, 'Ball Recoveries /90': 16.67, 'Fouls Committed /90': 16.67},
                'con_balon': {'Progressive passes /90': 17, 'Pass Completion %': 16.67, 'Key passes /90': 20}
            },
            'Playmaker': {
                'sin_balon': {'Interceptions /90': 16.66, 'Ball Recoveries /90': 16.67, 'Yellow Cards': 16.67},
                'con_balon': {'Pass Completion %': 16.67, 'Passes into Final 3rd /90': 13, 'Progressive passes /90': 17}
            },
            'Defensive': {
                'sin_balon': {'Tackles /90': 20, 'Interceptions /90': 17, 'Blocks Passes /90': 16.67, 'Ball Recoveries /90': 16.67, 'Aerial Duels Won %': 13},
                'con_balon': {'Pass Completion %': 16.67}
            },
            
            # MEDIAPUNTAS (3 perfiles)
            'Advanced Playmaker': {
                'sin_balon': {'Interceptions Att 3rd /90': 16.67, 'Ball Recoveries /90': 16.67, 'Fouls Committed /90': 16.66},
                'con_balon': {'Touches in box /90': 16.66, 'Key passes /90': 20, 'Progressive passes /90': 13, 'Pass Completion %': 16.67}
            },
            'Shadow Striker': {
                'sin_balon': {'Interceptions /90': 17, 'Ball Recoveries /90': 16.66, 'Aerial Duels Won %': 13},
                'con_balon': {'Key passes /90': 20, 'Passes into Final 3rd /90': 13, 'Progressive carries /90': 17}
            },
            'Dribbling Creator': {
                'sin_balon': {'Fouls Drawn /90': 16.67, 'Ball Recoveries /90': 16.67},
                'con_balon': {'Dribbles completed /90': 20, 'Progressive carries /90': 17, 'Key passes /90': 16.66}
            },
            
            # EXTREMOS (3 perfiles)
            'Wide Playmaker': {
                'sin_balon': {'Ball Recoveries /90': 16.67, 'Fouls Drawn /90': 16.67},
                'con_balon': {'xA /90': 17, 'Key passes /90': 20, 'Progressive passes /90': 13}
            },
            'Direct Winger': {
                'sin_balon': {'Ball Recoveries /90': 16.67, 'Aerial Duels Won %': 13},
                'con_balon': {'Shots on target %': 13, 'xA /90': 13, 'Key passes /90': 16.66, 'Progressive carries /90': 20}
            },
            'Hybrid': {
                'sin_balon': {'Ball Recoveries /90': 16.67, 'Progressive passes receive...': 16.67},
                'con_balon': {'xA /90': 17, 'Progressive passes /90': 13, 'Dribbles completed %': 16.67, 'Progressive passes receive...': 16.67}
            },
            
            # DELANTEROS (3 perfiles)
            'Target Man': {
                'sin_balon': {'Aerial Duels Contested /90': 20, 'Offsides /90': 16.67},
                'con_balon': {'Headed shots /90': 13, 'Shots /90': 16.66, 'Goals /90': 20, 'npxG /90': 16.67, 'Shots inside box /90': 17, 'npxG / Shot': 13}
            },
            'Poacher': {
                'sin_balon': {'Offsides': 16.67, 'Offsides /90': 16.67},
                'con_balon': {'Shots inside box /90': 17, 'npxG / Shot': 13, 'Goals /90': 20, 'Shot on target %': 16.67, 'Dribbles attempted /90': 17}
            },
            'Playmaker': {
                'sin_balon': {'Ball Recoveries /90': 16.67},
                'con_balon': {'Key passes /90': 20, 'xA /90': 17, 'Progressive passes /90': 13, 'Shots /90': 16.66, 'Goals /90': 20, 'Touches in midfield /90': 16.67}
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
        """Calcular rating de jugador - VERSIÓN CON GAUSSIANA"""
        try:
            # PASO 1: Calcular rating base (como antes)
            profile_key = self._find_profile_key(position, profile)
            
            if profile_key and profile_key in self.profiles_data:
                # Rating con métricas específicas
                base_rating = self._calculate_weighted_rating(player_data, self.profiles_data[profile_key])
            else:
                # Rating básico
                base_rating = self._calculate_basic_rating(player_data)
            
            # PASO 2: Aplicar modificadores tradicionales
            base_rating = self._apply_modifiers(base_rating, player_data)
            
            # PASO 3: 🎯 TRANSFORMACIÓN GAUSSIANA + ELITE FACTORS
            final_rating = self._apply_gaussian_transformation(base_rating, player_data)
            
            return final_rating
            
        except Exception as e:
            print(f"❌ Error calculando rating para {player_data.get('Name', 'Unknown')}: {e}")
            return 65.0
    
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
        """Calcular rating con pesos - VERSIÓN EQUILIBRADA"""
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
            # SISTEMA EQUILIBRADO: distribución más realista
            base_score = total_score / total_weight  # 0-100
            
            # Mapeo equilibrado: permitir buenos ratings pero sin inflación
            if base_score >= 90:  # Solo jugadores excepcionales
                rating = 80 + (base_score - 90) * 1.0  # 80-90
            elif base_score >= 75:  # Muy buenos jugadores  
                rating = 70 + (base_score - 75) * 0.67  # 70-80
            elif base_score >= 60:  # Buenos jugadores
                rating = 60 + (base_score - 60) * 0.67  # 60-70
            elif base_score >= 40:  # Promedio
                rating = 50 + (base_score - 40) * 0.5   # 50-60
            else:  # Por debajo del promedio
                rating = 40 + (base_score * 0.25)  # 40-50
                
            return min(90, max(40, rating))  # Hard cap en 90
        else:
            return 60  # Base más equilibrada
    
    def _get_metric_value(self, player_data: Dict, metric: str) -> Optional[float]:
        """Obtener valor de métrica con mapeo EXPANDIDO"""
        # Mapeo más completo de métricas
        mapping = {
            # Porteros
            '#OPA /90': ['Saves', 'OPA_90', 'Saves_90', 'SoTA'],
            'PSxG +/-': ['PSxG', 'Post_Shot_xG', 'PSxG_90'],
            'Save %': ['Save_Percentage', 'Save_Pct', 'Save%'],
            'Crosses Stopped %': ['Cross_Stop_Pct', 'Crosses_Stopped'],
            'Clean‑Sheet %': ['Clean_Sheet_Pct', 'CS%'],
            
            # Defensivos
            'Tackles /90': ['Tackles_90', 'Tackles', 'Tkl'],
            'Interceptions /90': ['Interceptions_90', 'Interceptions', 'Int'],
            'Blocks /90': ['Blocks_90', 'Blocks', 'Blk'],
            'Clearances /90': ['Clearances_90', 'Clearances', 'Clr'],
            'Aerial Win %': ['Aerial_Win_Pct', 'Aerial_Wins_Pct'],
            
            # Pases
            'Pass Completion %': ['Pass_Completion_Percentage', 'Pass_Pct', 'Pass%'],
            'Progressive passes /90': ['Progressive_Passes_90', 'Prog_Passes'],
            'Key passes /90': ['Key_Passes_90', 'Key_Passes', 'KP'],
            'Long Pass Cmp %': ['Long_Pass_Completion', 'Long_Pass_Pct'],
            
            # Ofensivos
            'Goals /90': ['Goals_90', 'Goals', 'Gls'],
            'npxG /90': ['npxG_90', 'npxG', 'Non_Penalty_xG'],
            'xA /90': ['xA_90', 'xA', 'Expected_Assists'],
            'Shots /90': ['Shots_90', 'Shots', 'Sh'],
            'Headed shots /90': ['Headed_Shots_90', 'Header_Shots'],
            'Shots inside box /90': ['Shots_Inside_Box_90', 'SiB'],
            
            # Físicos
            'Aerial Duels Contested /90': ['Aerial_Duels_90', 'Aerial_Contested'],
            'Ball Recoveries /90': ['Ball_Recoveries_90', 'Recoveries'],
            'Fouls Drawn /90': ['Fouls_Drawn_90', 'Fouls_Drawn'],
            'Dribbles completed /90': ['Dribbles_90', 'Successful_Dribbles']
        }
        
        # Buscar directo
        if metric in player_data:
            return float(player_data[metric]) if pd.notna(player_data[metric]) else None
        
        # Buscar en mapeo
        alternatives = mapping.get(metric, [])
        for alt in alternatives:
            if alt in player_data:
                return float(player_data[alt]) if pd.notna(player_data[alt]) else None
        
        # Búsqueda flexible (más agresiva)
        clean_metric = metric.lower().replace(' ', '_').replace('/', '_').replace('-', '_').replace('%', 'pct')
        for key in player_data.keys():
            clean_key = key.lower().replace(' ', '_').replace('/', '_').replace('-', '_').replace('%', 'pct')
            if clean_metric in clean_key or clean_key in clean_metric:
                return float(player_data[key]) if pd.notna(player_data[key]) else None
        
        return None
    
    def _normalize_metric(self, metric: str, value: float) -> float:
        """Normalizar métrica 0-100 - VERSIÓN EQUILIBRADA"""
        metric_lower = metric.lower()
        
        if '%' in metric_lower or 'percentage' in metric_lower:
            # Porcentajes: más generoso pero controlado
            return min(95, max(0, value * 0.9))  # Era 0.8, ahora 0.9
            
        elif '/90' in metric:
            if 'goal' in metric_lower:
                # Goles: permitir mejores ratings para goleadores
                return min(95, max(0, (value / 1.2) * 100))  # Era 1.5, ahora 1.2
            elif 'assist' in metric_lower or 'xa' in metric_lower:
                # Asistencias: más generoso
                return min(95, max(0, (value / 1.2) * 100))  # Era 1.0, ahora 1.2
            elif 'shot' in metric_lower:
                # Disparos: más equilibrado
                return min(95, max(0, (value / 7.0) * 100))  # Era 6.0, ahora 7.0
            elif 'pass' in metric_lower:
                # Pases: más equilibrado
                return min(100, max(0, (value / 75) * 100))  # MÁS GENEROSO: era 90, ahora 75
            elif 'tackle' in metric_lower:
                # Entradas: más equilibrado
                return min(95, max(0, (value / 7.0) * 100))  # Era 6.0, ahora 7.0
            elif 'interception' in metric_lower:
                # Intercepciones: más equilibrado
                return min(95, max(0, (value / 4.5) * 100))  # Era 4.0, ahora 4.5
            elif 'save' in metric_lower or 'opa' in metric_lower:
                # Paradas: más equilibrado
                return min(95, max(0, (value / 7.0) * 100))  # Era 6.0, ahora 7.0
            else:
                # Otras métricas: más equilibrado
                return min(95, max(0, (value / 4.5) * 100))  # Era 4.0, ahora 4.5
        else:
            # Métricas generales: más equilibrado
            return min(95, max(0, (value / 9.0) * 100))  # Era 8.0, ahora 9.0
    
    def _apply_modifiers(self, base_rating: float, player_data: Dict) -> float:
        """Aplicar modificadores - VERSIÓN CORREGIDA Y CONSERVADORA"""
        rating = base_rating
        
        # Liga: reducir impacto
        league = player_data.get('Liga', player_data.get('League', ''))
        multiplier = self.league_multipliers.get(league, 1.0)
        if multiplier > 1.0:
            # Reducir de 5 a 2 puntos máximo
            rating += (multiplier - 1.0) * 2  # Era 5, ahora 2
        
        # Minutos: penalización más suave
        minutes = player_data.get('Minutes', player_data.get('Min', 2700))
        if minutes < 900:
            # Reducir penalización máxima de 10 a 5
            rating -= (900 - minutes) / 900 * 5  # Era 10, ahora 5
        
        return rating
    
    def _calculate_basic_rating(self, player_data: Dict) -> float:
        """Rating básico EQUILIBRADO para cuando no hay métricas específicas"""
        base = 60  # Más equilibrado: era 55, ahora 60
        
        # Bonus por valor de mercado (EQUILIBRADO)
        market_value = player_data.get('Market_Value', player_data.get('Market Value', 0))
        if market_value > 150: base += 15   # Era 12, ahora 15 - Súper estrellas
        elif market_value > 100: base += 12 # Era 8, ahora 12
        elif market_value > 80: base += 9   # Era 6, ahora 9
        elif market_value > 50: base += 6   # Era 4, ahora 6
        elif market_value > 30: base += 4   # Era 2, ahora 4
        elif market_value > 15: base += 2   # Era 1, ahora 2
        elif market_value > 5: base += 1    # Nuevo nivel
        
        # Bonus por rating original (EQUILIBRADO)
        original_rating = player_data.get('Rating', 0)
        if original_rating > 65:
            # Escala más equilibrada
            bonus = (original_rating - 65) * 0.7  # Era 0.4, ahora 0.7
            base += min(bonus, 12)  # Cap aumentado de 8 a 12 puntos
        
        # Bonus por liga (EQUILIBRADO)
        league = player_data.get('Liga', player_data.get('League', ''))
        if league in ['La Liga', 'Premier League', 'Bundesliga', 'Serie A', 'Ligue 1']:
            base += 3  # Era 2, ahora 3
        elif league in ['Liga Portugal', 'Eredivisie', 'Süper Lig']:
            base += 1  # Nuevo: bonus menor para ligas secundarias
        
        # Bonus por edad (EQUILIBRADO)
        age = player_data.get('Age', 25)
        if 24 <= age <= 29:  # Prime age
            base += 2  # Vuelto a 2 desde 1
        elif 22 <= age <= 32:  # Edad buena
            base += 1  # Nuevo nivel
        
        return max(40, min(95, base))  # ELIMINADO EL LÍMITE 85 - ahora 95
    
    def bulk_calculate_ratings(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """Calcular ratings masivamente con reescalado gaussiano automático"""
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
        
        # 🎯 APLICAR REESCALADO GAUSSIANO AUTOMÁTICO MÁS AGRESIVO
        print("🔄 Aplicando reescalado gaussiano...")
        players_df = self.gauss_scale(
            players_df, 
            col='Calculated_Rating',
            pos_col='Position',
            by_position=False,  # Global para mejor distribución
            mu=78,              # Media MÁS alta (era 72, ahora 78)
            sigma=18            # MÁS dispersión (era 15, ahora 18)
        )
        
        # Usar el rating reescalado como el rating final a mostrar
        if 'rating_40_99' in players_df.columns:
            players_df['Display_Rating'] = players_df['rating_40_99']
        
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

    def _apply_gaussian_transformation(self, base_rating: float, player_data: Dict) -> float:
        """🎯 TRANSFORMACIÓN GAUSSIANA + FACTORES ELITE"""
        # PASO 1: Normalizar rating base a percentil (0-1)
        # Asumir que ratings base están en rango 40-85 (actual)
        normalized = (base_rating - 40) / 45  # 0-1
        normalized = max(0, min(1, normalized))  # Clamp
        
        # PASO 2: Aplicar distribución gaussiana inversa
        # Media=72, Desviación=15 → Distribución MÁS GENEROSA
        target_mean = 72  # Era 70, ahora 72 - sube la media
        target_std = 15   # Era 12, ahora 15 - más dispersión
        
        # Convertir percentil a valor gaussiano
        if normalized == 0:
            gaussian_rating = 40
        elif normalized == 1:
            gaussian_rating = 99
        else:
            if stats is not None:
                # Usar función inversa de distribución normal (IDEAL)
                z_score = stats.norm.ppf(normalized)
                gaussian_rating = target_mean + (z_score * target_std)
            else:
                # Aproximación sin scipy (FALLBACK)
                # Transformación sigmoidea que simula gaussiana
                import math
                # Convertir [0,1] a aproximación gaussiana
                if normalized < 0.5:
                    # Lado izquierdo de la gaussiana
                    scaled = normalized * 2  # 0->1
                    gaussian_rating = target_mean - (target_std * 2 * (1 - scaled))
                else:
                    # Lado derecho de la gaussiana
                    scaled = (normalized - 0.5) * 2  # 0->1
                    gaussian_rating = target_mean + (target_std * 2 * scaled)
        
        # PASO 3: Aplicar factores ELITE para casos especiales
        elite_bonus = self._calculate_elite_factors(player_data, base_rating)
        final_rating = gaussian_rating + elite_bonus
        
        # PASO 4: Clamp final en rango 40-99
        return max(40, min(99, final_rating))
    
    def _calculate_elite_factors(self, player_data: Dict, base_rating: float) -> float:
        """🌟 FACTORES ELITE AGRESIVOS - Para que Lamine Yamal, Mbappe lleguen a 95-99"""
        bonus = 0
        
        # 💎 SÚPER ELITE - Valor de mercado excepcional (MÁS AGRESIVO)
        market_value = player_data.get('Market_Value', player_data.get('Market Value', 0))
        if market_value > 180:  # Mbappe, Haaland nivel
            bonus += 15  # Era 8, ahora 15
        elif market_value > 150:  # Elite mundial
            bonus += 12  # Era 6, ahora 12
        elif market_value > 120:  # Muy top
            bonus += 8   # Era 4, ahora 8
        elif market_value > 100:  # Top
            bonus += 5   # Era 2, ahora 5
        elif market_value > 80:   # Buenos
            bonus += 3   # Nuevo nivel
        elif market_value > 60:   # Prometedores
            bonus += 1   # Nuevo nivel
        
        # 🔥 RATING ORIGINAL EXCEPCIONAL (MÁS AGRESIVO)
        original_rating = player_data.get('Rating', 0)
        if original_rating >= 90:  # FIFA/datos originales ya lo consideran elite
            bonus += 12  # Era 6, ahora 12
        elif original_rating >= 85:
            bonus += 8   # Era 4, ahora 8
        elif original_rating >= 80:
            bonus += 5   # Era 2, ahora 5
        elif original_rating >= 75:
            bonus += 2   # Nuevo nivel
        
        # ⭐ JÓVENES TALENTOS EN LIGAS TOP (Lamine Yamal factor) - MÁS AGRESIVO
        age = player_data.get('Age', 25)
        league = player_data.get('Liga', player_data.get('League', ''))
        if age <= 22 and league in ['La Liga', 'Premier League', 'Bundesliga', 'Serie A', 'Ligue 1']:
            if market_value > 80:  # Joven + caro + liga top = futuro crack
                bonus += 10  # Era 5, ahora 10 - LAMINE YAMAL BOOST
            elif market_value > 50:
                bonus += 6   # Era 3, ahora 6
            elif market_value > 30:
                bonus += 4   # Era 2, ahora 4
            elif market_value > 15:  # Jóvenes prometedores
                bonus += 2   # Nuevo
        
        # 🏆 MÉTRICAS EXCEPCIONALES (Top 1% mundial)
        metrics_bonus = self._check_exceptional_metrics(player_data)
        bonus += metrics_bonus
        
        # 🌍 BONUS POR LIGA TOP5 (más generoso)
        if league in ['La Liga', 'Premier League', 'Bundesliga', 'Serie A', 'Ligue 1']:
            bonus += 2  # Era 1, ahora 2
        elif league in ['Liga Portugal', 'Eredivisie', 'Süper Lig']:
            bonus += 1  # Nuevo
        
        # 🎯 EDAD PRIME (pico de rendimiento) - MÁS GENEROSO
        if 24 <= age <= 29:
            bonus += 3   # Era 1.5, ahora 3
        elif 22 <= age <= 32:
            bonus += 1.5 # Era 0.5, ahora 1.5
        elif age <= 21:  # Jóvenes talentos
            bonus += 2   # Nuevo - boost para jóvenes
        
        # 🚀 BOOST ESPECIAL para casos extremos
        # Si ya tiene rating alto + valor alto + joven = SÚPER BOOST
        if original_rating >= 85 and market_value > 100 and age <= 23:
            bonus += 8  # LAMINE YAMAL / PEDRI / GAVI boost especial
        elif original_rating >= 80 and market_value > 80 and age <= 25:
            bonus += 5  # Estrellas jóvenes
        
        return bonus
    
    def _check_exceptional_metrics(self, player_data: Dict) -> float:
        """🔥 Detectar métricas excepcionales que justifican rating elite - MÁS GENEROSO"""
        bonus = 0
        
        # Mapeo de métricas excepcionales por posición (UMBRALES MÁS BAJOS)
        exceptional_thresholds = {
            # Delanteros - más generoso
            'Goals_90': 0.6,    # Era 1.0, ahora 0.6
            'npxG_90': 0.5,     # Era 0.8, ahora 0.5
            'Goals': 15,        # Era 25, ahora 15
            'Shots_on_target_percentage': 45, # 45%+ precisión
            
            # Creativos - más generoso
            'xA_90': 0.3,       # Era 0.5, ahora 0.3
            'Key_Passes_90': 2.5, # Era 3.5, ahora 2.5
            'Assists': 8,       # Era 15, ahora 8
            'Progressive_passes_90': 8, # 8+ pases progresivos
            
            # Defensivos - más generoso
            'Tackles_90': 2.5,  # Era 4.0, ahora 2.5
            'Interceptions_90': 2.0, # Era 3.0, ahora 2.0
            'Aerial_win_percentage': 65, # 65%+ duelos aéreos
            'Pass_completion_percentage': 88, # 88%+ pases completados
            
            # Porteros - más generoso
            'Save_Percentage': 70, # Era 80, ahora 70
            'Clean_Sheet_Percentage': 35, # Era 50, ahora 35
            'PSxG': 5,          # 5+ PSxG en temporada
            
            # Métricas universales
            'Market_Value': 50, # 50M+ = excepcional por definición
            'Minutes': 2500,    # 2500+ minutos = titular absoluto
        }
        
        # Comprobar cada métrica con BONUS AUMENTADO
        for metric, threshold in exceptional_thresholds.items():
            value = self._get_metric_value(player_data, metric)
            if value is not None and value >= threshold:
                # BONUS DINÁMICO según el nivel de la métrica
                if metric == 'Market_Value':
                    if value > 150: bonus += 4   # Súper elite
                    elif value > 100: bonus += 3 # Elite
                    elif value > 80: bonus += 2  # Muy bueno
                    else: bonus += 1             # Bueno
                elif 'percentage' in metric.lower() or '%' in metric:
                    # Para porcentajes, bonus proporcional
                    excess = (value - threshold) / threshold
                    bonus += min(3, 1 + excess)  # 1-3 puntos según exceso
                else:
                    # Para otras métricas, bonus estándar aumentado
                    bonus += 2.5  # Era 1.5, ahora 2.5
        
        # Cap máximo por métricas AUMENTADO
        return min(bonus, 12)  # Era 4, ahora 12 - mucho más generoso

    def gauss_scale(
        self, 
        df: pd.DataFrame,
        col: str = 'raw_rating',
        pos_col: str = 'Position',
        by_position: bool = False,
        mu: float = 78,  # Media más alta (era 70, ahora 78)
        sigma: float = 20,  # Mayor dispersión (era 12, ahora 20)
    ) -> pd.DataFrame:
        """
        🔥 SISTEMA AVANZADO DE REESCALADO CON SIGMA ADAPTATIVO
        
        Combina las mejores opciones de ChatGPT:
        - Opción 1: Sigma adaptativo (stretch dinámico)
        - Opción 4: Diagnóstico asistido completo
        
        GARANTIZA matemáticamente que algunos jugadores alcancen 90+
        """
        df = df.copy()
        
        # Detectar columna de rating
        if col not in df.columns:
            if 'Display_Rating' in df.columns:
                col = 'Display_Rating'
            elif 'Calculated_Rating' in df.columns:
                col = 'Calculated_Rating'
            elif 'Rating' in df.columns:
                col = 'Rating'
            else:
                print("⚠️ No se encontró columna de rating válida")
                df['rating_40_99'] = 70
                return df
        
        raw_ratings = df[col].copy()
        
        # 🔍 PASO 1: DIAGNÓSTICO COMPLETO (Opción 4 de ChatGPT)
        print(f"\n🔍 === DIAGNÓSTICO COMPLETO DE {col} ===")
        print(f"📊 Estadísticas básicas:")
        print(f"  • Min: {raw_ratings.min():.2f}")
        print(f"  • Max: {raw_ratings.max():.2f}")
        print(f"  • Mean: {raw_ratings.mean():.2f}")
        print(f"  • Std: {raw_ratings.std():.3f}")
        print(f"  • Rango: {raw_ratings.max() - raw_ratings.min():.2f}")
        
        print(f"📈 Percentiles:")
        print(f"  • P5: {raw_ratings.quantile(0.05):.2f}")
        print(f"  • P50 (mediana): {raw_ratings.quantile(0.50):.2f}")
        print(f"  • P95: {raw_ratings.quantile(0.95):.2f}")
        print(f"  • P99: {raw_ratings.quantile(0.99):.2f}")
        
        # Análisis de distribución
        count_80_plus = (raw_ratings >= 80).sum()
        count_75_plus = (raw_ratings >= 75).sum()
        count_70_plus = (raw_ratings >= 70).sum()
        print(f"🎯 Distribución actual:")
        print(f"  • ≥80: {count_80_plus} jugadores")
        print(f"  • ≥75: {count_75_plus} jugadores") 
        print(f"  • ≥70: {count_70_plus} jugadores")
        
        # 🛠️ PASO 2: DETECCIÓN Y CORRECCIÓN DE PROBLEMAS
        
        # Problema: NaNs
        if raw_ratings.isnull().any():
            nan_count = raw_ratings.isnull().sum()
            raw_ratings = raw_ratings.fillna(raw_ratings.mean())
            print(f"⚠️ CORREGIDO: {nan_count} NaNs imputados con la media")
        
        # Problema: Varianza muy baja (Opción 4 de ChatGPT)
        std_threshold = 0.15
        if raw_ratings.std() <= std_threshold:
            print(f"🚨 PROBLEMA DETECTADO: Std muy baja ({raw_ratings.std():.3f} ≤ {std_threshold})")
            print(f"   Esto impide que el escalado gaussiano funcione correctamente")
            
            # SOLUCIÓN: Mapping por percentil puro (Opción 2 de ChatGPT)
            print(f"🔧 APLICANDO SOLUCIÓN: Mapping por percentil puro")
            percentiles = raw_ratings.rank(method='average') / (len(raw_ratings) + 1)
            df['rating_40_99'] = (50 + percentiles * 49).round().astype(int)
            df['rating_40_99'] = df['rating_40_99'].clip(50, 99)
            
            # Aplicar boost élite forzado
            self._apply_elite_boost(df)
            self._print_final_results(df, col, "Mapping Percentil")
            return df
        
        # Problema: Rango muy pequeño  
        rating_range = raw_ratings.max() - raw_ratings.min()
        if rating_range < 1.0:
            print(f"🚨 PROBLEMA DETECTADO: Rango muy pequeño ({rating_range:.3f})")
            
            # SOLUCIÓN: Min-max scaling agresivo
            print(f"🔧 APLICANDO SOLUCIÓN: Min-max scaling agresivo")
            normalized = (raw_ratings - raw_ratings.min()) / (rating_range + 1e-6)
            df['rating_40_99'] = (50 + normalized * 49).round().astype(int)
            df['rating_40_99'] = df['rating_40_99'].clip(50, 99)
            
            # Aplicar boost élite forzado
            self._apply_elite_boost(df)
            self._print_final_results(df, col, "Min-Max Scaling")
            return df
        
        # 🎯 PASO 3: SIGMA ADAPTATIVO (Opción 1 de ChatGPT) 
        print(f"\n🚀 === APLICANDO SIGMA ADAPTATIVO ===")
        
        # Normalizar a percentiles [0,1]
        percentiles = raw_ratings.rank(method='average') / (len(raw_ratings) + 1)
        percentiles = percentiles.clip(0.001, 0.999)
        
        # BÚSQUEDA ITERATIVA de sigma óptimo
        target_max = 98  # Queremos que el máximo sea 98+
        best_sigma = sigma
        
        for attempt_sigma in [sigma, sigma * 1.5, sigma * 2.0, sigma * 2.5, sigma * 3.0]:
            try:
                # Aplicar transformación gaussiana
                if stats is not None:
                    z_scores = percentiles.apply(lambda p: stats.norm.ppf(p))
                    gaussian_ratings = mu + attempt_sigma * z_scores
                else:
                    # Método aproximado sin scipy
                    import math
                    def approx_norm_ppf(p):
                        if p <= 0.5:
                            t = math.sqrt(-2 * math.log(p))
                            return -(t - (2.30753 + t * 0.27061) / (1 + t * (0.99229 + t * 0.04481)))
                        else:
                            t = math.sqrt(-2 * math.log(1 - p))
                            return t - (2.30753 + t * 0.27061) / (1 + t * (0.99229 + t * 0.04481))
                    
                    z_scores = percentiles.apply(approx_norm_ppf)
                    gaussian_ratings = mu + attempt_sigma * z_scores
                
                # Clamp temporal
                clamped = gaussian_ratings.clip(50, 99)
                max_achieved = clamped.max()
                
                print(f"  • Sigma {attempt_sigma:.1f} → Máximo: {max_achieved:.1f}")
                
                if max_achieved >= target_max:
                    best_sigma = attempt_sigma
                    print(f"✅ ENCONTRADO: Sigma {best_sigma:.1f} logra máximo {max_achieved:.1f}")
                    break
                    
            except Exception as e:
                print(f"  ⚠️ Error con sigma {attempt_sigma}: {e}")
                continue
        
        # Aplicar mejor sigma encontrado
        if stats is not None:
            z_scores = percentiles.apply(lambda p: stats.norm.ppf(p))
            gaussian_ratings = mu + best_sigma * z_scores
        else:
            import math
            def approx_norm_ppf(p):
                if p <= 0.5:
                    t = math.sqrt(-2 * math.log(p))
                    return -(t - (2.30753 + t * 0.27061) / (1 + t * (0.99229 + t * 0.04481)))
                else:
                    t = math.sqrt(-2 * math.log(1 - p))
                    return t - (2.30753 + t * 0.27061) / (1 + t * (0.99229 + t * 0.04481))
            
            z_scores = percentiles.apply(approx_norm_ppf)
            gaussian_ratings = mu + best_sigma * z_scores
        
        # Clamp final
        df['rating_40_99'] = gaussian_ratings.clip(50, 99).round().astype(int)
        
        # 🌟 PASO 4: BOOST ÉLITE GARANTIZADO
        self._apply_elite_boost(df)
        
        # 📊 PASO 5: RESULTADOS Y VALIDACIÓN
        self._print_final_results(df, col, f"Sigma Adaptativo ({best_sigma:.1f})")
        
        return df
    
    def _apply_elite_boost(self, df: pd.DataFrame):
        """Aplicar boost élite forzado para garantizar ratings altos"""
        
        # Boost por valor de mercado
        if 'Market_Value' in df.columns or 'Market Value' in df.columns:
            market_col = 'Market_Value' if 'Market_Value' in df.columns else 'Market Value'
            
            # Top 1% → mínimo 92
            top_1_percent = df[market_col].quantile(0.99)
            super_elite_mask = df[market_col] >= top_1_percent
            df.loc[super_elite_mask, 'rating_40_99'] = df.loc[super_elite_mask, 'rating_40_99'].clip(lower=92)
            
            # Top 5% → mínimo 87  
            top_5_percent = df[market_col].quantile(0.95)
            elite_mask = df[market_col] >= top_5_percent
            df.loc[elite_mask, 'rating_40_99'] = df.loc[elite_mask, 'rating_40_99'].clip(lower=87)
            
            # Top 10% → mínimo 82
            top_10_percent = df[market_col].quantile(0.90)
            good_mask = df[market_col] >= top_10_percent
            df.loc[good_mask, 'rating_40_99'] = df.loc[good_mask, 'rating_40_99'].clip(lower=82)
        
        # Boost por rating original alto
        if 'Rating' in df.columns:
            original_elite = df['Rating'] >= 85
            df.loc[original_elite, 'rating_40_99'] = df.loc[original_elite, 'rating_40_99'].clip(lower=90)
            
            original_very_good = df['Rating'] >= 80
            df.loc[original_very_good, 'rating_40_99'] = df.loc[original_very_good, 'rating_40_99'].clip(lower=85)
    
    def _print_final_results(self, df: pd.DataFrame, original_col: str, method: str):
        """Imprimir resultados finales con estadísticas completas"""
        final_ratings = df['rating_40_99']
        
        print(f"\n🎯 === RESULTADOS FINALES ({method}) ===")
        print(f"📊 Nuevas estadísticas:")
        print(f"  • Rango: {final_ratings.min()}-{final_ratings.max()}")
        print(f"  • Media: {final_ratings.mean():.1f}")
        print(f"  • Std: {final_ratings.std():.1f}")
        
        # Distribución por rangos
        over_95 = (final_ratings >= 95).sum()
        over_90 = (final_ratings >= 90).sum()
        over_87 = (final_ratings >= 87).sum()
        over_85 = (final_ratings >= 85).sum()
        over_80 = (final_ratings >= 80).sum()
        
        print(f"🎯 Nueva distribución:")
        print(f"  • ≥95 (ÉLITE): {over_95} jugadores")
        print(f"  • ≥90 (MUY ALTO): {over_90} jugadores")
        print(f"  • ≥87 (ALTO): {over_87} jugadores ← ¡PROBLEMA SOLUCIONADO!")
        print(f"  • ≥85 (BUENO): {over_85} jugadores")
        print(f"  • ≥80 (DECENTE): {over_80} jugadores")
        
        # Top 10 jugadores
        if 'Name' in df.columns:
            top_10 = df.nlargest(10, 'rating_40_99')[['Name', 'rating_40_99', original_col]]
            print(f"\n🌟 TOP 10 JUGADORES:")
            for idx, row in top_10.iterrows():
                original = row[original_col] if not pd.isna(row[original_col]) else 0
                new_rating = row['rating_40_99']
                change = f"(+{new_rating - original:.0f})" if new_rating > original else f"({new_rating - original:.0f})"
                print(f"  {idx+1:2d}. {row['Name']:<25} {new_rating:2d} {change}")
        
        # Validación crítica
        if over_87 == 0:
            print(f"❌ FALLO CRÍTICO: Ningún jugador tiene rating ≥87")
        else:
            print(f"✅ ÉXITO: {over_87} jugadores con rating ≥87")
        
        print(f"=" * 50)
