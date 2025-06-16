import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, List, Optional
import concurrent.futures
from playwright.sync_api import sync_playwright
from tqdm import tqdm
import sys
from src.config import LOGS_DIR, INPUT_FILE, FBREF_OUTPUT
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'fbref_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('fbref_scraper')

class FBrefScraper:
    """
    Scraper for FBref.com to extract player statistics
    """
    
    def __init__(self, output_dir: str = "Datos/fbref_data"):
        """
        Inicializa el scraper de FBref
        
        Args:
            output_dir: Directorio donde se guardarán los datos extraídos
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.setup_driver()
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def setup_driver(self):
        """Configura el driver de Selenium con opciones optimizadas"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ejecutar en modo headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.driver.set_page_load_timeout(30)

    def normalize_name(self, name: str) -> str:
        """
        Normaliza el nombre para usar en nombres de archivo
        
        Args:
            name: Nombre a normalizar
            
        Returns:
            Nombre normalizado
        """
        # Eliminar caracteres especiales y espacios
        normalized = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
        # Reemplazar espacios con guiones
        normalized = re.sub(r'\s+', '-', normalized.strip())
        return normalized

    def get_player_data(self, player_id: str, player_name: str) -> Optional[Dict]:
        """
        Obtiene los datos de un jugador de FBref
        
        Args:
            player_id: ID del jugador en FBref
            player_name: Nombre del jugador
            
        Returns:
            Diccionario con los datos del jugador o None si hay error
        """
        self.logger.info(f"Procesando jugador: {player_name} (https://fbref.com/en/players/{player_id})")
        
        try:
            url = f"https://fbref.com/en/players/{player_id}"
            self.driver.get(url)
            
            # Esperar a que la página cargue completamente
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Dar tiempo extra para que cargue el JavaScript
            time.sleep(5)
            
            # Obtener datos de cada tabla
            tables_data = {}
            table_ids = [
                "stats_standard", "stats_shooting", "stats_passing",
                "stats_passing_types", "stats_gca", "stats_defense",
                "stats_possession", "stats_misc", "stats_playing_time",
                "stats_keeper", "stats_keeper_adv"
            ]
            
            for table_id in table_ids:
                try:
                    table_data = self.extract_table(table_id, player_name)
                    if table_data is not None:
                        tables_data[table_id] = table_data
                except Exception as e:
                    self.logger.error(f"Error extrayendo tabla {table_id} para {player_name}: {str(e)}")
                    continue
            
            if not tables_data:
                self.logger.error(f"No se obtuvieron datos para {player_name}")
                return None
                
            return tables_data
            
        except Exception as e:
            self.logger.error(f"Error procesando jugador {player_name}: {str(e)}")
            # Reiniciar el driver si hay un error grave
            self.driver.quit()
            self.setup_driver()
            return None
            
    def extract_table(self, table_id: str, player_name: str) -> Optional[pd.DataFrame]:
        """
        Extrae una tabla específica de la página del jugador
        
        Args:
            table_id: ID de la tabla a extraer
            player_name: Nombre del jugador para logging
            
        Returns:
            DataFrame con los datos de la tabla o None si hay error
        """
        try:
            # Esperar a que la tabla esté presente
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, table_id))
            )
            
            # Extraer HTML de la tabla
            table_html = table.get_attribute('outerHTML')
            
            # Parsear tabla con pandas
            dfs = pd.read_html(table_html)
            
            if not dfs:
                self.logger.warning(f"Tabla {table_id} no encontrada para {player_name}")
                return None
                
            # Tomar la primera tabla encontrada
            df = dfs[0]
            
            # Filtrar solo la temporada 2024-25
            df = df[df['Season'].str.contains('2024-25|2024-2025', na=False)]
            
            if df.empty:
                self.logger.warning(f"No hay datos de 2024-25 en tabla {table_id} para {player_name}")
                return None
                
            return df
            
        except TimeoutException:
            self.logger.warning(f"Tabla {table_id} no encontrada para {player_name}")
            return None
        except Exception as e:
            self.logger.error(f"Error extrayendo tabla {table_id}: {str(e)}")
            return None

    def get_output_filename(self, player_name: str, table_type: str) -> str:
        """
        Genera el nombre de archivo para los datos extraídos
        
        Args:
            player_name: Nombre del jugador
            table_type: Tipo de tabla
            
        Returns:
            Ruta completa del archivo
        """
        normalized_name = self.normalize_name(player_name)
        filename = f"{normalized_name}_2024-25_{table_type}.csv"
        return os.path.join(self.output_dir, filename)

    def scrape_all_players(self, players_csv: str):
        """
        Extrae datos para todos los jugadores en el CSV
        
        Args:
            players_csv: Ruta al archivo CSV con los datos de los jugadores
        """
        # Leer CSV de jugadores
        df = pd.read_csv(players_csv, sep=';')
        
        for _, row in df.iterrows():
            # Extraer player_id de la URL de FBref
            fbref_url = row['Link_FBref']
            player_id = fbref_url.split('/')[-2]
            player_name = row['player_name']
            
            try:
                self.get_player_data(player_id, player_name)
                time.sleep(1.5)  # Esperar entre jugadores
                
            except Exception as e:
                self.logger.error(f"Error procesando {player_name}: {str(e)}")
                continue

    def __del__(self):
        """Cierra el driver al destruir la instancia"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    scraper = FBrefScraper()
    scraper.scrape_all_players(INPUT_FILE) 