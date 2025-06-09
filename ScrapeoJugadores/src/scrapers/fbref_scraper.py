import pandas as pd
from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright
import time
from tqdm import tqdm
import logging
from pathlib import Path
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/fbref_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('fbref_scraper')

class FBrefScraper:
    def __init__(self):
        self.tables_to_scrape = [
            'stats_standard',
            'stats_shooting',
            'stats_passing',
            'stats_passing_types',
            'stats_gca',
            'stats_defense',
            'stats_possession',
            'stats_playing_time',
            'stats_misc',
            'stats_keeper'
        ]
        
    def get_player_stats(self, url):
        """Obtiene las estadísticas de un jugador de FBref."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url)
                time.sleep(2)  # Esperar a que cargue el contenido dinámico
                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, 'lxml')
            stats = {}

            for table_id in self.tables_to_scrape:
                table = soup.find('table', {'id': table_id})
                if table:
                    df = pd.read_html(str(table))[0]
                    stats[table_id] = df

            return stats
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None

    def process_players(self, players_df):
        """Procesa la lista de jugadores y obtiene sus estadísticas."""
        results = []
        
        for _, player in tqdm(players_df.iterrows(), total=len(players_df)):
            if pd.isna(player['Link_FBref']):
                continue
                
            logger.info(f"Procesando jugador: {player['player_name']}")
            stats = self.get_player_stats(player['Link_FBref'])
            
            if stats:
                # Combinar todas las estadísticas en un solo registro
                player_stats = {
                    'player_id': player['player_id'],
                    'player_name': player['player_name'],
                    **self._flatten_stats(stats)
                }
                results.append(player_stats)
            
            time.sleep(3)  # Delay entre requests
            
        return pd.DataFrame(results)

    def _flatten_stats(self, stats_dict):
        """Aplana el diccionario de estadísticas para crear un solo registro."""
        flattened = {}
        for table_name, df in stats_dict.items():
            if not df.empty:
                for col in df.columns:
                    if col != 'Season':  # Excluir columna de temporada
                        flattened[f"{table_name}_{col}"] = df.iloc[0][col]
        return flattened

    def run(self, input_file):
        """Ejecuta el proceso completo de scraping."""
        try:
            # Leer archivo de jugadores
            players_df = pd.read_csv(input_file, sep=';')
            
            # Filtrar por ligas especificadas
            target_leagues = [9, 10, 13, 11, 12, 17, 20, 23, 32, 37]
            players_df = players_df[players_df['ID_Liga'].isin(target_leagues)]
            
            # Procesar jugadores
            results_df = self.process_players(players_df)
            
            # Guardar resultados
            output_path = Path('../data/processed/fbref_stats.parquet')
            results_df.to_parquet(output_path)
            
            logger.info(f"Datos guardados exitosamente en {output_path}")
            
        except Exception as e:
            logger.error(f"Error en el proceso de scraping: {str(e)}")
            raise

if __name__ == "__main__":
    scraper = FBrefScraper()
    scraper.run('../data/raw/Jugadores.csv') 