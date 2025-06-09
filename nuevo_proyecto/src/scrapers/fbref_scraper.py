from playwright.sync_api import sync_playwright
import pandas as pd
import time
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FBrefScraper:
    def __init__(self):
        self.base_url = "https://fbref.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def get_player_stats(self, url):
        """Obtiene las estadísticas de un jugador de FBref."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                logger.info(f"Accediendo a {url}")
                page.goto(url)
                time.sleep(2)  # Esperar a que cargue el contenido dinámico
                
                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, 'lxml')
            stats = self._extract_all_stats(soup)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
            
    def _extract_all_stats(self, soup):
        """Extrae todas las estadísticas de la página."""
        stats = {
            'info': self._extract_player_info(soup),
            'stats': self._extract_stats_tables(soup)
        }
        return stats
        
    def _extract_player_info(self, soup):
        """Extrae la información básica del jugador."""
        info = {}
        try:
            info_div = soup.find('div', {'itemtype': 'https://schema.org/Person'})
            if info_div:
                # Nombre
                name_tag = info_div.find('h1', {'itemprop': 'name'})
                if name_tag:
                    info['name'] = name_tag.text.strip()
                
                # Posición y otros datos
                for p in info_div.find_all('p'):
                    text = p.text.strip()
                    if 'Position:' in text:
                        info['position'] = text.split('Position:')[1].split('▪')[0].strip()
                    if 'Footed:' in text:
                        info['footed'] = text.split('Footed:')[1].split('▪')[0].strip()
                
                # Nacionalidad
                nationality_div = info_div.find('div', {'class': 'birthplace'})
                if nationality_div:
                    info['nationality'] = [img['alt'] for img in nationality_div.find_all('img')]
                    
            return info
            
        except Exception as e:
            logger.error(f"Error extrayendo información básica: {str(e)}")
            return info
            
    def _extract_stats_tables(self, soup):
        """Extrae las tablas de estadísticas."""
        tables = {}
        try:
            # IDs de las tablas que queremos extraer
            table_ids = [
                'stats_standard_dom_lg',
                'stats_shooting_dom_lg',
                'stats_passing_dom_lg',
                'stats_passing_types_dom_lg',
                'stats_gca_dom_lg',
                'stats_defense_dom_lg',
                'stats_possession_dom_lg',
                'stats_playing_time_dom_lg',
                'stats_misc_dom_lg',
                'stats_keeper_dom_lg'
            ]
            
            for table_id in table_ids:
                table = soup.find('table', {'id': table_id})
                if table:
                    try:
                        df = pd.read_html(str(table))[0]
                        tables[table_id] = df.to_dict('records')
                    except Exception as e:
                        logger.warning(f"Error procesando tabla {table_id}: {str(e)}")
                        
            return tables
            
        except Exception as e:
            logger.error(f"Error extrayendo tablas: {str(e)}")
            return tables 