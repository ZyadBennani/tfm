import pandas as pd
from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright
import time
from tqdm import tqdm
import logging
import sys
from src.config import LOGS_DIR, INPUT_FILE, TRANSFERMARKT_OUTPUT
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'transfermarkt_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('transfermarkt_scraper')

class TransfermarktScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_player_info(self, url):
        """Obtiene la información de un jugador de Transfermarkt."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url)
                time.sleep(2)
                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, 'lxml')
            
            # Información básica
            info = {
                'valor_mercado_actual': self._extract_market_value(soup),
                'valor_mercado_maximo': self._extract_max_market_value(soup),
                'fin_contrato': self._extract_contract_end(soup),
                'clausula_rescision': self._extract_release_clause(soup),
                'club_actual': self._extract_current_club(soup),
                'posicion_principal': self._extract_position(soup),
                'altura': self._extract_height(soup),
                'pie_dominante': self._extract_foot(soup),
                'nacionalidades': self._extract_nationalities(soup),
                'agente': self._extract_agent(soup),
                'historial_valor_mercado': self._extract_market_value_history(soup)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None

    def _extract_market_value(self, soup):
        try:
            value_div = soup.find('div', {'class': 'market-value'})
            if value_div:
                value = value_div.find('div', {'class': 'value'}).text.strip()
                return self._convert_value_to_euros(value)
            return None
        except:
            return None

    def _extract_max_market_value(self, soup):
        try:
            max_value_div = soup.find('div', {'class': 'max-market-value'})
            if max_value_div:
                value = max_value_div.find('div', {'class': 'value'}).text.strip()
                return self._convert_value_to_euros(value)
            return None
        except:
            return None

    def _extract_contract_end(self, soup):
        try:
            contract_div = soup.find('span', text='Contract expires:')
            if contract_div:
                date_str = contract_div.find_next('span').text.strip()
                return datetime.strptime(date_str, '%b %d, %Y').strftime('%Y-%m-%d')
            return None
        except:
            return None

    def _extract_release_clause(self, soup):
        try:
            clause_div = soup.find('span', text='Release clause:')
            if clause_div:
                value = clause_div.find_next('span').text.strip()
                return self._convert_value_to_euros(value)
            return None
        except:
            return None

    def _extract_current_club(self, soup):
        try:
            club_div = soup.find('span', {'class': 'club'})
            return club_div.text.strip() if club_div else None
        except:
            return None

    def _extract_position(self, soup):
        try:
            pos_div = soup.find('span', text='Position:')
            return pos_div.find_next('span').text.strip() if pos_div else None
        except:
            return None

    def _extract_height(self, soup):
        try:
            height_div = soup.find('span', text='Height:')
            if height_div:
                height_str = height_div.find_next('span').text.strip()
                return int(height_str.replace('cm', '').strip())
            return None
        except:
            return None

    def _extract_foot(self, soup):
        try:
            foot_div = soup.find('span', text='Foot:')
            return foot_div.find_next('span').text.strip() if foot_div else None
        except:
            return None

    def _extract_nationalities(self, soup):
        try:
            nat_div = soup.find('span', text='Citizenship:')
            if nat_div:
                return [n.strip() for n in nat_div.find_next('span').text.split(',')]
            return []
        except:
            return []

    def _extract_agent(self, soup):
        try:
            agent_div = soup.find('span', text='Player agent:')
            return agent_div.find_next('span').text.strip() if agent_div else None
        except:
            return None

    def _extract_market_value_history(self, soup):
        try:
            history_table = soup.find('table', {'class': 'market-value-history'})
            if history_table:
                history = []
                rows = history_table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        history.append({
                            'fecha': datetime.strptime(cols[0].text.strip(), '%b %d, %Y').strftime('%Y-%m-%d'),
                            'valor': self._convert_value_to_euros(cols[2].text.strip())
                        })
                return history
            return []
        except:
            return []

    def _convert_value_to_euros(self, value_str):
        """Convierte string de valor a euros (float)."""
        try:
            value_str = value_str.lower()
            multiplier = 1
            if 'm' in value_str:
                multiplier = 1000000
            elif 'k' in value_str:
                multiplier = 1000
                
            value = float(value_str.replace('€', '').replace('m', '').replace('k', '').strip())
            return value * multiplier
        except:
            return None

    def process_players(self, players_df):
        """Procesa la lista de jugadores y obtiene su información."""
        results = []
        
        for _, player in tqdm(players_df.iterrows(), total=len(players_df)):
            if pd.isna(player['Link_Transfermarkt']):
                continue
                
            logger.info(f"Procesando jugador: {player['player_name']}")
            info = self.get_player_info(player['Link_Transfermarkt'])
            
            if info:
                player_info = {
                    'player_id': player['player_id'],
                    'player_name': player['player_name'],
                    **info
                }
                results.append(player_info)
            
            time.sleep(3)  # Delay entre requests
            
        return pd.DataFrame(results)

    def run(self, input_file=None):
        """Ejecuta el proceso completo de scraping."""
        try:
            # Usar el archivo de entrada predeterminado si no se proporciona uno
            input_file = input_file or INPUT_FILE
            
            # Intentar diferentes codificaciones
            encodings = ['latin1', 'iso-8859-1', 'cp1252', 'utf-8-sig']
            for encoding in encodings:
                try:
                    logger.info(f"Intentando leer el archivo con codificación {encoding}")
                    players_df = pd.read_csv(input_file, sep=';', encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise Exception("No se pudo leer el archivo con ninguna codificación")
            
            # Filtrar por ligas especificadas
            target_leagues = [9, 10, 13, 11, 12, 17, 20, 23, 32, 37]
            players_df = players_df[players_df['ID_Liga'].isin(target_leagues)]
            
            # Procesar jugadores
            results_df = self.process_players(players_df)
            
            # Guardar resultados
            results_df.to_parquet(TRANSFERMARKT_OUTPUT)
            
            logger.info(f"Datos guardados exitosamente en {TRANSFERMARKT_OUTPUT}")
            
        except Exception as e:
            logger.error(f"Error en el proceso de scraping: {str(e)}")
            raise

if __name__ == "__main__":
    scraper = TransfermarktScraper()
    scraper.run() 