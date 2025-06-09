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
    
    def __init__(self):
        self.base_url = "https://fbref.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Tablas que necesitamos extraer
        self.required_tables = [
            'Standard',
            'Shooting',
            'Passing',
            'Passing Types',
            'GCA',
            'Defensive Actions',
            'Possession',
            'Playing Time',
            'Misc Stats',
            'Goalkeeping'
        ]
        
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """
        Realiza una petición HTTP con manejo de errores y rate limiting
        """
        try:
            time.sleep(3)  # Rate limiting para evitar bloqueos
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error al hacer la petición a {url}: {str(e)}")
            return None
            
    def scrape_player_stats(self, player_url: str) -> Dict:
        """
        Extrae todas las estadísticas requeridas de un jugador
        """
        stats = {}
        soup = self._make_request(player_url)
        
        if not soup:
            return stats
            
        try:
            # Extraer información básica del jugador
            player_info = self._extract_player_info(soup)
            stats.update(player_info)
            
            # Extraer todas las tablas de estadísticas
            for table_name in self.required_tables:
                table_stats = self._extract_table_stats(soup, table_name)
                stats[table_name] = table_stats
                
            return stats
        except Exception as e:
            logger.error(f"Error al extraer estadísticas del jugador {player_url}: {str(e)}")
            return stats
            
    def _extract_player_info(self, soup: BeautifulSoup) -> Dict:
        """
        Extrae la información básica del jugador de FBref
        """
        info = {}
        try:
            # Obtener el contenedor principal de información del jugador
            player_info_div = soup.find('div', {'itemtype': 'https://schema.org/Person'})
            
            if player_info_div:
                # Nombre completo
                name_tag = player_info_div.find('h1', {'itemprop': 'name'})
                if name_tag:
                    info['full_name'] = name_tag.text.strip()
                
                # Información adicional en formato p
                p_tags = player_info_div.find_all('p')
                for p in p_tags:
                    text = p.text.strip()
                    
                    # Posición
                    if 'Position:' in text:
                        info['position'] = text.split('Position:')[1].split('▪')[0].strip()
                    
                    # Pie dominante
                    if 'Footed:' in text:
                        info['footed'] = text.split('Footed:')[1].split('▪')[0].strip()
                    
                    # Altura
                    if 'cm' in text and ',' in text:
                        height_part = text.split(',')[0]
                        if 'cm' in height_part:
                            info['height'] = height_part.strip()
                    
                    # Peso
                    if 'kg' in text:
                        weight_parts = text.split(',')
                        for part in weight_parts:
                            if 'kg' in part:
                                info['weight'] = part.strip()
                
                # Nacionalidad
                nationality_div = player_info_div.find('div', {'class': 'birthplace'})
                if nationality_div:
                    info['nationality'] = [img['alt'] for img in nationality_div.find_all('img')]
            
            logger.info(f"Información básica extraída: {info}")
            return info
            
        except Exception as e:
            logger.error(f"Error al extraer información básica del jugador: {str(e)}")
            return info
        
    def _extract_table_stats(self, soup: BeautifulSoup, table_name: str) -> Dict:
        """
        Extrae las estadísticas de una tabla específica
        """
        stats = {}
        try:
            # Mapeo de nombres de tablas a IDs
            table_id_mapping = {
                'Standard': 'stats_standard_dom_lg',
                'Shooting': 'stats_shooting_dom_lg',
                'Passing': 'stats_passing_dom_lg',
                'Passing Types': 'stats_passing_types_dom_lg',
                'GCA': 'stats_gca_dom_lg',
                'Defensive Actions': 'stats_defense_dom_lg',
                'Possession': 'stats_possession_dom_lg',
                'Playing Time': 'stats_playing_time_dom_lg',
                'Misc Stats': 'stats_misc_dom_lg',
                'Goalkeeping': 'stats_keeper_dom_lg'
            }
            
            table_id = table_id_mapping.get(table_name)
            if not table_id:
                logger.warning(f"No se encontró mapeo para la tabla {table_name}")
                return stats
            
            # Buscar la tabla por ID
            table = soup.find('table', {'id': table_id})
            if not table:
                logger.warning(f"No se encontró la tabla {table_name}")
                return stats
            
            # Extraer encabezados
            headers = []
            header_row = table.find('thead').find_all('th')
            for header in header_row:
                header_text = header.text.strip()
                if header_text and not header_text.isspace():
                    headers.append(header_text)
            
            # Extraer datos
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                season = None
                season_cell = row.find('th')
                if season_cell:
                    season = season_cell.text.strip()
                
                if not season:
                    continue
                
                stats[season] = {}
                cells = row.find_all(['th', 'td'])
                
                for header, cell in zip(headers, cells):
                    value = cell.text.strip()
                    if value and not value.isspace():
                        stats[season][header] = value
            
            logger.info(f"Estadísticas extraídas para la tabla {table_name}")
            return stats
            
        except Exception as e:
            logger.error(f"Error al extraer tabla {table_name}: {str(e)}")
            return stats
        
    def process_player_list(self, player_urls: List[str]) -> List[Dict]:
        """
        Procesa una lista de URLs de jugadores en paralelo
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(self.scrape_player_stats, url): url 
                           for url in player_urls}
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    if data:
                        results.append(data)
                except Exception as e:
                    logger.error(f"Error procesando {url}: {str(e)}")
                    
        return results

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

            for table_id in self.required_tables:
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

    def read_csv_with_encodings(self, file_path):
        """Intenta leer un archivo CSV con diferentes codificaciones."""
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252', 'utf-8-sig']
        
        for encoding in encodings:
            try:
                logger.info(f"Intentando leer {file_path} con codificación {encoding}")
                df = pd.read_csv(file_path, sep=';', encoding=encoding)
                logger.info(f"Éxito leyendo el archivo con codificación {encoding}")
                logger.info(f"Columnas encontradas: {df.columns.tolist()}")
                logger.info(f"Primeras filas:\n{df.head()}")
                return df
            except UnicodeDecodeError as e:
                logger.warning(f"Error con codificación {encoding}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Error inesperado con codificación {encoding}: {str(e)}")
                continue
        
        raise Exception("No se pudo leer el archivo con ninguna codificación")

    def run(self, input_file=None):
        """Ejecuta el proceso completo de scraping."""
        try:
            # Usar el archivo de entrada predeterminado si no se proporciona uno
            input_file = input_file or INPUT_FILE
            logger.info(f"Usando archivo de entrada: {input_file}")
            
            # Leer archivo de jugadores
            players_df = self.read_csv_with_encodings(input_file)
            
            # Filtrar por ligas especificadas
            target_leagues = [9, 10, 13, 11, 12, 17, 20, 23, 32, 37]
            players_df = players_df[players_df['ID_Liga'].isin(target_leagues)]
            
            # Procesar jugadores
            results_df = self.process_players(players_df)
            
            # Guardar resultados
            results_df.to_parquet(FBREF_OUTPUT)
            
            logger.info(f"Datos guardados exitosamente en {FBREF_OUTPUT}")
            
        except Exception as e:
            logger.error(f"Error en el proceso de scraping: {str(e)}")
            raise

if __name__ == "__main__":
    scraper = FBrefScraper()
    scraper.run() 