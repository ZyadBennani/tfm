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
        
        # Sistema de caché persistente PERMANENTE
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
        
        # ⭐ CACHE PERMANENTE - No expira nunca (datos estáticos)
        self.cache_expiry_days = None  # Sin expiración
    
    def _is_cache_valid(self, cache_file: str) -> bool:
        """Verifica si el archivo de caché es válido - SIEMPRE válido si existe"""
        return os.path.exists(cache_file) and os.path.getsize(cache_file) > 0
    
    def _save_to_cache(self, data: pd.DataFrame, cache_file: str):
        """Guarda datos en caché con compresión optimizada"""
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            
            # Guardar con compresión para mayor eficiencia
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Log del cache guardado
            print(f"✅ Cache guardado: {cache_file} ({len(data)} registros)")
        except Exception as e:
            st.warning(f"No se pudo guardar caché: {e}")
    
    def _load_from_cache(self, cache_file: str) -> Optional[pd.DataFrame]:
        """Carga datos desde caché con manejo optimizado de errores"""
        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            print(f"✅ Cache cargado: {cache_file} ({len(data)} registros)")
            return data
        except Exception as e:
            print(f"❌ Error cargando cache {cache_file}: {e}")
            return None
    
    def load_normalization_data(self) -> Dict[str, pd.DataFrame]:
        """Carga los archivos de normalización con caché persistente PERMANENTE"""
        
        # ⭐ CACHE PERMANENTE - Si existe, lo usa siempre
        if self._is_cache_valid(self.cache_files['normalization']):
            cached_data = self._load_from_cache(self.cache_files['normalization'])
            if cached_data is not None:
                return cached_data
        
        # Solo procesa si no hay cache
        st.info("🔄 Procesando archivos de normalización... (solo la primera vez)")
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
            
            # ⭐ GUARDAR CACHE PERMANENTE
            self._save_to_cache(norm_data, self.cache_files['normalization'])
            st.success("✅ Archivos de normalización procesados y guardados permanentemente")
            
            return norm_data
            
        except Exception as e:
            st.error(f"Error cargando archivos de normalización: {e}")
            return {}
    
    def load_fbref_data(self) -> pd.DataFrame:
        """Carga todos los datos de FBREF de las 8 ligas con caché PERMANENTE"""
        
        # ⭐ CACHE PERMANENTE - Si existe, lo usa siempre
        if self._is_cache_valid(self.cache_files['fbref']):
            cached_data = self._load_from_cache(self.cache_files['fbref'])
            if cached_data is not None:
                return cached_data
        
        # Solo procesa si no hay cache
        st.info("🔄 Procesando datos de FBREF... (solo la primera vez, puede tardar 10 minutos)")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
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
        
        total_leagues = len(fbref_leagues)
        
        for i, league in enumerate(fbref_leagues):
            progress = (i + 1) / total_leagues
            progress_bar.progress(progress)
            status_text.text(f"Procesando {league}... ({i+1}/{total_leagues})")
            
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
        
        # ⭐ GUARDAR CACHE PERMANENTE
        self._save_to_cache(result_df, self.cache_files['fbref'])
        
        # Limpiar elementos de progreso
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"✅ Datos de FBREF procesados y guardados permanentemente ({len(result_df)} registros)")
        
        return result_df
    
    def load_transfermarket_data(self) -> pd.DataFrame:
        """Carga todos los datos de Transfermarket con caché PERMANENTE"""
        
        # ⭐ CACHE PERMANENTE - Si existe, lo usa siempre
        if self._is_cache_valid(self.cache_files['transfermarket']):
            cached_data = self._load_from_cache(self.cache_files['transfermarket'])
            if cached_data is not None:
                return cached_data
        
        # Solo procesa si no hay cache
        st.info("🔄 Procesando datos de Transfermarket... (solo la primera vez)")
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
        
        # ⭐ GUARDAR CACHE PERMANENTE
        self._save_to_cache(result_df, self.cache_files['transfermarket'])
        st.success(f"✅ Datos de Transfermarket procesados y guardados permanentemente ({len(result_df)} registros)")
        
        return result_df
    
    def load_capology_data(self) -> pd.DataFrame:
        """Carga todos los datos de Capology (salarios) con caché PERMANENTE"""
        
        # ⭐ CACHE PERMANENTE - Si existe, lo usa siempre
        if self._is_cache_valid(self.cache_files['capology']):
            cached_data = self._load_from_cache(self.cache_files['capology'])
            if cached_data is not None:
                return cached_data
        
        # Solo procesa si no hay cache
        st.info("🔄 Procesando datos de Capology... (solo la primera vez)")
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
        
        # ⭐ GUARDAR CACHE PERMANENTE
        self._save_to_cache(result_df, self.cache_files['capology'])
        st.success(f"✅ Datos de Capology procesados y guardados permanentemente ({len(result_df)} registros)")
        
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
        """Limpia archivos de caché - ⚠️ USAR SOLO SI HAY PROBLEMAS"""
        try:
            if cache_type == 'all':
                for cache_file in self.cache_files.values():
                    if os.path.exists(cache_file):
                        os.remove(cache_file)
                st.success("✅ Todos los archivos de caché han sido eliminados")
                st.warning("⚠️ La próxima carga tardará ~10 minutos en regenerar los datos")
            else:
                cache_file = self.cache_files.get(cache_type)
                if cache_file and os.path.exists(cache_file):
                    os.remove(cache_file)
                    st.success(f"✅ Caché de {cache_type} eliminado")
                    st.warning(f"⚠️ Los datos de {cache_type} se regenerarán en la próxima carga")
                else:
                    st.warning(f"⚠️ No se encontró caché para {cache_type}")
        except Exception as e:
            st.error(f"❌ Error eliminando caché: {e}")
    
    def get_cache_info(self) -> dict:
        """Obtiene información detallada sobre los archivos de caché"""
        cache_info = {}
        total_size = 0
        
        for cache_type, cache_file in self.cache_files.items():
            if os.path.exists(cache_file):
                stat = os.stat(cache_file)
                size_mb = round(stat.st_size / (1024 * 1024), 2)
                total_size += size_mb
                
                cache_info[cache_type] = {
                    'exists': True,
                    'size_mb': size_mb,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'status': '✅ Listo (carga instantánea)'
                }
            else:
                cache_info[cache_type] = {
                    'exists': False,
                    'size_mb': 0,
                    'modified': 'N/A',
                    'status': '⏳ Pendiente (tardará en procesarse)'
                }
        
        cache_info['total_size_mb'] = round(total_size, 2)
        cache_info['cache_status'] = '🚀 OPTIMIZADO' if all(info.get('exists', False) for info in cache_info.values() if isinstance(info, dict) and 'exists' in info) else '⏳ PROCESANDO'
        
        return cache_info
    
    def force_rebuild_cache(self):
        """Fuerza la regeneración completa del caché"""
        st.warning("🔄 Regenerando caché completo...")
        self.clear_cache('all')
        
        # Recargar datos
        self.load_normalization_data()
        self.load_fbref_data()
        self.load_transfermarket_data()
        self.load_capology_data()
        
        st.success("✅ Caché regenerado completamente") 