import pandas as pd
import numpy as np
import os
import glob
import streamlit as st
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class DataLoader:
    """Clase para cargar y consolidar datos de jugadores de múltiples fuentes"""
    
    def __init__(self, base_path: str = "Datos"):
        self.base_path = base_path
        self.fbref_path = os.path.join(base_path, "Datos Jugadores Fede", "wetransfer_tfm_2025-06-16_1449")
        self.normalization_files = {
            'equipos': os.path.join(base_path, "G_Equipos.csv"),
            'jugadores': os.path.join(base_path, "G_Jugadores.csv"),
            'ligas': os.path.join(base_path, "G_Ligas.csv")
        }
        
        # Sistema de caché persistente
        self.cache_dir = os.path.join(base_path, ".cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        self.cache_files = {
            'fbref': os.path.join(self.cache_dir, 'fbref_data.pkl'),
            'transfermarket': os.path.join(self.cache_dir, 'transfermarket_data.pkl'),
            'capology': os.path.join(self.cache_dir, 'capology_data.pkl'),
            'normalization': os.path.join(self.cache_dir, 'normalization_data.pkl'),
            'consolidated': os.path.join(self.cache_dir, 'consolidated_data.pkl')
        }
        
        # Tiempo de expiración del caché (7 días)
        self.cache_expiry_days = 7
    
    def _is_cache_valid(self, cache_file: str) -> bool:
        """Verifica si el archivo de caché es válido (existe y no ha expirado)"""
        if not os.path.exists(cache_file):
            return False
        
        # Verificar tiempo de modificación
        mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        expiry_time = datetime.now() - timedelta(days=self.cache_expiry_days)
        
        return mod_time > expiry_time
    
    def _save_to_cache(self, data: pd.DataFrame, cache_file: str):
        """Guarda datos en caché"""
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            st.warning(f"No se pudo guardar caché: {e}")
    
    def _load_from_cache(self, cache_file: str) -> Optional[pd.DataFrame]:
        """Carga datos desde caché"""
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            return None
    
    def load_normalization_data(self) -> Dict[str, pd.DataFrame]:
        """Carga los archivos de normalización con caché persistente"""
        
        # Verificar si hay caché válido
        if self._is_cache_valid(self.cache_files['normalization']):
            cached_data = self._load_from_cache(self.cache_files['normalization'])
            if cached_data is not None:
                return cached_data
        
        norm_data = {}
        
        try:
            # Cargar G_Equipos.csv - probar diferentes encodings
            try:
                norm_data['equipos'] = pd.read_csv(self.normalization_files['equipos'], sep=';', encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    norm_data['equipos'] = pd.read_csv(self.normalization_files['equipos'], sep=';', encoding='latin-1')
                except:
                    norm_data['equipos'] = pd.read_csv(self.normalization_files['equipos'], sep=';', encoding='cp1252')
            
            # Cargar G_Jugadores.csv - probar diferentes encodings
            try:
                norm_data['jugadores'] = pd.read_csv(self.normalization_files['jugadores'], sep=';', encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    norm_data['jugadores'] = pd.read_csv(self.normalization_files['jugadores'], sep=';', encoding='latin-1')
                except:
                    norm_data['jugadores'] = pd.read_csv(self.normalization_files['jugadores'], sep=';', encoding='cp1252')
            
            # Cargar G_Ligas.csv - probar diferentes encodings
            try:
                norm_data['ligas'] = pd.read_csv(self.normalization_files['ligas'], encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    norm_data['ligas'] = pd.read_csv(self.normalization_files['ligas'], encoding='latin-1')
                except:
                    norm_data['ligas'] = pd.read_csv(self.normalization_files['ligas'], encoding='cp1252')
            
            # Guardar en caché
            self._save_to_cache(norm_data, self.cache_files['normalization'])
            
            return norm_data
            
        except Exception as e:
            st.error(f"Error cargando archivos de normalización: {e}")
            return {}
    
    def load_fbref_data(self) -> pd.DataFrame:
        """Carga todos los datos de FBREF de las 8 ligas con caché persistente"""
        
        # Verificar si hay caché válido
        if self._is_cache_valid(self.cache_files['fbref']):
            cached_data = self._load_from_cache(self.cache_files['fbref'])
            if cached_data is not None:
                return cached_data
        
        # Si no hay caché válido, procesar datos
        st.info("🔄 Cargando datos de FBREF... (esto puede tardar unos minutos la primera vez)")
        
        all_players = []
        
        # Ligas disponibles en FBREF
        fbref_leagues = [
            "La_Liga_2024-2025 FBREF",
            "EPL_2024-2025 FBREF", 
            "Bundesliga_2024-2025 FBREF",
            "Serie_A_2024-2025 FBREF",
            "Ligue_1_2024-2025 FBREF",
            "Primeira_Liga_2024-2025 FBREF",
            "Eredivisie_2024-2025 FBREF",
            "Super_Lig_2024-2025 FBREF"
        ]
        
        for league in fbref_leagues:
            league_path = os.path.join(self.fbref_path, league)
            
            if not os.path.exists(league_path):
                continue
                
            # Obtener equipos de la liga
            teams = [d for d in os.listdir(league_path) 
                    if os.path.isdir(os.path.join(league_path, d))]
            
            for team in teams:
                team_path = os.path.join(league_path, team)
                
                # Buscar archivos CSV de jugadores
                player_files = glob.glob(os.path.join(team_path, "**", "*.csv"), recursive=True)
                
                for player_file in player_files:
                    try:
                        # Intentar diferentes encodings para los archivos
                        df_player = None
                        for encoding in ['utf-8', 'latin-1', 'cp1252']:
                            try:
                                df_player = pd.read_csv(player_file, encoding=encoding)
                                break
                            except UnicodeDecodeError:
                                continue
                        
                        if df_player is not None and not df_player.empty:
                            # Agregar metadatos
                            df_player['Liga'] = league.replace('_2024-2025 FBREF', '').replace('_', ' ')
                            df_player['Equipo'] = team
                            df_player['Archivo_Origen'] = player_file
                            
                            # DETECTAR TEMPORADA - Solo queremos 2024-2025
                            if '2024-2025' in league or '2024-25' in league:
                                df_player['Season'] = '2024-2025'
                            else:
                                # Saltar datos de temporadas anteriores
                                continue
                            
                            # Extraer nombre del jugador del archivo
                            player_name = os.path.basename(player_file).replace('.csv', '')
                            df_player['player_name'] = player_name
                            
                            all_players.append(df_player)
                            
                    except Exception as e:
                        continue  # Saltar archivos problemáticos
        
        # Consolidar datos
        if all_players:
            result_df = pd.concat(all_players, ignore_index=True)
        else:
            result_df = pd.DataFrame()
        
        # Guardar en caché
        self._save_to_cache(result_df, self.cache_files['fbref'])
        st.success("✅ Datos de FBREF cargados y guardados en caché")
        
        return result_df
    
    def load_transfermarket_data(self) -> pd.DataFrame:
        """Carga todos los datos de Transfermarket con caché persistente"""
        
        # Verificar si hay caché válido
        if self._is_cache_valid(self.cache_files['transfermarket']):
            cached_data = self._load_from_cache(self.cache_files['transfermarket'])
            if cached_data is not None:
                return cached_data
        
        all_tm_data = []
        
        # Ligas de Transfermarket
        tm_leagues = [
            "La_Liga Transfermarket",
            "EPL Transfermarket",
            "Bundesliga Transfermarket", 
            "Serie_A Transfermarket",
            "Ligue_1 Transfermarket",
            "Primeira_Liga Transfermarket",
            "Eredevise Transfermarket",
            "Super Lig Transfermarket"
        ]
        
        for league in tm_leagues:
            league_path = os.path.join(self.fbref_path, league)
            
            if not os.path.exists(league_path):
                continue
                
            # Buscar archivos CSV en la liga
            csv_files = glob.glob(os.path.join(league_path, "*.csv"))
            
            for csv_file in csv_files:
                try:
                    # Intentar diferentes encodings
                    df_team = None
                    for encoding in ['utf-8', 'latin-1', 'cp1252']:
                        try:
                            df_team = pd.read_csv(csv_file, encoding=encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if df_team is not None and not df_team.empty:
                        # Agregar metadatos
                        team_name = os.path.basename(csv_file).replace('.csv', '')
                        df_team['Liga_TM'] = league.replace(' Transfermarket', '')
                        df_team['Equipo_TM'] = team_name
                        df_team['Archivo_TM'] = csv_file
                        
                        all_tm_data.append(df_team)
                        
                except Exception as e:
                    continue
        
        # Consolidar datos
        if all_tm_data:
            result_df = pd.concat(all_tm_data, ignore_index=True)
        else:
            result_df = pd.DataFrame()
        
        # Guardar en caché
        self._save_to_cache(result_df, self.cache_files['transfermarket'])
        
        return result_df
    
    def load_capology_data(self) -> pd.DataFrame:
        """Carga todos los datos de Capology (salarios) con caché persistente"""
        
        # Verificar si hay caché válido
        if self._is_cache_valid(self.cache_files['capology']):
            cached_data = self._load_from_cache(self.cache_files['capology'])
            if cached_data is not None:
                return cached_data
        
        all_cap_data = []
        
        capology_path = os.path.join(self.fbref_path, "Capology")
        
        if not os.path.exists(capology_path):
            result_df = pd.DataFrame()
            self._save_to_cache(result_df, self.cache_files['capology'])
            return result_df
        
        # Recorrer todas las ligas en Capology
        for league_dir in os.listdir(capology_path):
            league_path = os.path.join(capology_path, league_dir)
            
            if not os.path.isdir(league_path):
                continue
            
            # Recorrer equipos en cada liga
            for team_dir in os.listdir(league_path):
                team_path = os.path.join(league_path, team_dir)
                
                if not os.path.isdir(team_path):
                    continue
                
                # Buscar archivos CSV (Tabla_Limpia_*.csv)
                csv_files = glob.glob(os.path.join(team_path, "Tabla_Limpia_*.csv"))
                
                for csv_file in csv_files:
                    try:
                        # Intentar diferentes encodings
                        df_salary = None
                        for encoding in ['utf-8', 'latin-1', 'cp1252']:
                            try:
                                df_salary = pd.read_csv(csv_file, encoding=encoding)
                                break
                            except UnicodeDecodeError:
                                continue
                        
                        if df_salary is not None and not df_salary.empty:
                            # Agregar metadatos
                            df_salary['Liga_Cap'] = league_dir
                            df_salary['Equipo_Cap'] = team_dir
                            df_salary['Archivo_Cap'] = csv_file
                            
                            all_cap_data.append(df_salary)
                            
                    except Exception as e:
                        continue
        
        if all_cap_data:
            result_df = pd.concat(all_cap_data, ignore_index=True)
        else:
            result_df = pd.DataFrame()
        
        # Guardar en caché
        self._save_to_cache(result_df, self.cache_files['capology'])
        
        return result_df
    
    def normalize_player_name(self, name: str) -> str:
        """Normaliza nombres de jugadores para hacer matching"""
        if pd.isna(name) or name == "":
            return ""
            
        # Convertir a lowercase y quitar espacios extra
        normalized = str(name).lower().strip()
        
        # Reemplazar caracteres especiales comunes
        replacements = {
            'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a', 'ã': 'a',
            'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e',
            'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i',
            'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o', 'õ': 'o',
            'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u',
            'ñ': 'n', 'ç': 'c',
            '-': '_', ' ': '_', '.': '', "'": ''
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Quitar múltiples underscores
        while '__' in normalized:
            normalized = normalized.replace('__', '_')
            
        return normalized.strip('_')
    
    def get_sample_data(self) -> pd.DataFrame:
        """Genera datos de muestra para testing mientras implementamos la carga real"""
        
        # Datos ficticios pero realistas para testing
        sample_players = []
        
        # Algunos jugadores conocidos para testing
        players_data = [
            {"Name": "Robert Lewandowski", "Age": 35, "Position": "ST", "Club": "Barcelona", "League": "La Liga", "Nationality": "Poland", "Height": 185, "Foot": "Right"},
            {"Name": "Erling Haaland", "Age": 24, "Position": "ST", "Club": "Manchester City", "League": "EPL", "Nationality": "Norway", "Height": 194, "Foot": "Left"},
            {"Name": "Kylian Mbappé", "Age": 25, "Position": "LW", "Club": "PSG", "League": "Ligue 1", "Nationality": "France", "Height": 178, "Foot": "Right"},
            {"Name": "Pedri", "Age": 21, "Position": "CM", "Club": "Barcelona", "League": "La Liga", "Nationality": "Spain", "Height": 174, "Foot": "Right"},
            {"Name": "Jude Bellingham", "Age": 21, "Position": "CM", "Club": "Real Madrid", "League": "La Liga", "Nationality": "England", "Height": 186, "Foot": "Right"},
        ]
        
        # Expandir con más jugadores ficticios
        positions = ["GK", "CB", "RB", "LB", "CM", "CDM", "CAM", "RW", "LW", "ST"]
        clubs = ["Barcelona", "Real Madrid", "Manchester City", "Arsenal", "Bayern Munich", "PSG", "Juventus", "AC Milan"]
        leagues = ["La Liga", "EPL", "Bundesliga", "Serie A", "Ligue 1"]
        nationalities = ["Spain", "England", "Germany", "France", "Brazil", "Argentina", "Portugal", "Italy"]
        
        np.random.seed(42)  # Para resultados reproducibles
        
        for i in range(50):  # 50 jugadores de muestra
            player = {
                "Name": f"Player {i+1}",
                "Age": np.random.randint(18, 35),
                "Position": np.random.choice(positions),
                "Club": np.random.choice(clubs),
                "League": np.random.choice(leagues),
                "Nationality": np.random.choice(nationalities),
                "Height": np.random.randint(165, 200),
                "Foot": np.random.choice(["Left", "Right"]),
                "Market_Value": np.random.randint(5, 100),
                "Salary_Annual": np.random.randint(500_000, 15_000_000),
                "Contract_End": np.random.choice([2024, 2025, 2026, 2027, 2028, 2029]),
                "Rating": np.random.randint(60, 95),  # Rating ficticio por ahora
                "xG_90": round(np.random.uniform(0.1, 0.8), 2),
                "xA_90": round(np.random.uniform(0.05, 0.5), 2),
                "Passes_Completed_90": np.random.randint(20, 90),
                "Tackles_90": round(np.random.uniform(0.5, 5.0), 1),
                "Interceptions_90": round(np.random.uniform(0.2, 3.0), 1),
                "Distance_Covered_90": round(np.random.uniform(9.0, 12.0), 1),
                "Has_Clause": np.random.choice(["Sí", "No"]),
                "Profile": "TBD"  # Por implementar
            }
            sample_players.append(player)
        
        # Agregar los jugadores conocidos
        for known_player in players_data:
            # Completar con datos ficticios
            known_player.update({
                "Market_Value": np.random.randint(20, 150),
                "Salary_Annual": np.random.randint(2_000_000, 25_000_000),
                "Contract_End": np.random.choice([2025, 2026, 2027, 2028]),
                "Rating": np.random.randint(80, 95),
                "xG_90": round(np.random.uniform(0.2, 0.9), 2),
                "xA_90": round(np.random.uniform(0.1, 0.6), 2),
                "Passes_Completed_90": np.random.randint(40, 95),
                "Tackles_90": round(np.random.uniform(0.5, 4.0), 1),
                "Interceptions_90": round(np.random.uniform(0.3, 2.5), 1),
                "Distance_Covered_90": round(np.random.uniform(9.5, 11.8), 1),
                "Has_Clause": np.random.choice(["Sí", "No"]),
                "Profile": "TBD"
            })
            sample_players.append(known_player)
        
        return pd.DataFrame(sample_players)
    
    def clear_cache(self, cache_type: str = 'all'):
        """Limpia el caché especificado"""
        if cache_type == 'all':
            # Limpiar todo el caché
            for cache_file in self.cache_files.values():
                if os.path.exists(cache_file):
                    try:
                        os.remove(cache_file)
                        st.success(f"✅ Caché limpiado: {os.path.basename(cache_file)}")
                    except Exception as e:
                        st.warning(f"⚠️ No se pudo limpiar: {os.path.basename(cache_file)}")
        elif cache_type in self.cache_files:
            # Limpiar caché específico
            cache_file = self.cache_files[cache_type]
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                    st.success(f"✅ Caché limpiado: {cache_type}")
                except Exception as e:
                    st.warning(f"⚠️ No se pudo limpiar caché: {cache_type}")
    
    def get_cache_info(self) -> dict:
        """Obtiene información sobre el estado del caché"""
        cache_info = {}
        
        for cache_type, cache_file in self.cache_files.items():
            if os.path.exists(cache_file):
                mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                file_size = os.path.getsize(cache_file) / (1024 * 1024)  # MB
                is_valid = self._is_cache_valid(cache_file)
                
                cache_info[cache_type] = {
                    'exists': True,
                    'last_modified': mod_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'size_mb': round(file_size, 2),
                    'is_valid': is_valid,
                    'expires_in_days': self.cache_expiry_days - (datetime.now() - mod_time).days
                }
            else:
                cache_info[cache_type] = {
                    'exists': False,
                    'last_modified': 'N/A',
                    'size_mb': 0,
                    'is_valid': False,
                    'expires_in_days': 0
                }
        
        return cache_info 