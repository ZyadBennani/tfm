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
        logging.FileHandler('../logs/capology_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('capology_scraper')

class CapologyScraper:
    def __init__(self):
        self.base_url = "https://www.capology.com/player/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_player_salary(self, player_slug):
        """Obtiene la información salarial de un jugador de Capology."""
        try:
            url = f"{self.base_url}{player_slug}"
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url)
                time.sleep(2)
                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, 'lxml')
            
            salary_info = {
                'salario_bruto': self._extract_gross_salary(soup),
                'bonificaciones': self._extract_bonuses(soup),
                'duracion_contrato': self._extract_contract_duration(soup),
                'ranking_salarial_club': self._extract_club_salary_rank(soup),
                'ranking_salarial_liga': self._extract_league_salary_rank(soup)
            }
            
            return salary_info
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None

    def _extract_gross_salary(self, soup):
        try:
            salary_div = soup.find('div', {'class': 'gross-salary'})
            if salary_div:
                salary_str = salary_div.text.strip()
                return self._convert_salary_to_euros(salary_str)
            return None
        except:
            return None

    def _extract_bonuses(self, soup):
        try:
            bonus_div = soup.find('div', {'class': 'bonuses'})
            if bonus_div:
                bonuses = []
                for bonus in bonus_div.find_all('div', {'class': 'bonus-item'}):
                    bonus_type = bonus.find('span', {'class': 'type'}).text.strip()
                    bonus_value = bonus.find('span', {'class': 'value'}).text.strip()
                    bonuses.append({
                        'tipo': bonus_type,
                        'valor': self._convert_salary_to_euros(bonus_value)
                    })
                return bonuses
            return []
        except:
            return []

    def _extract_contract_duration(self, soup):
        try:
            duration_div = soup.find('div', {'class': 'contract-duration'})
            if duration_div:
                start_date = duration_div.find('span', {'class': 'start-date'}).text.strip()
                end_date = duration_div.find('span', {'class': 'end-date'}).text.strip()
                return {
                    'inicio': start_date,
                    'fin': end_date
                }
            return None
        except:
            return None

    def _extract_club_salary_rank(self, soup):
        try:
            rank_div = soup.find('div', {'class': 'club-salary-rank'})
            if rank_div:
                return int(rank_div.text.strip().split('/')[0])
            return None
        except:
            return None

    def _extract_league_salary_rank(self, soup):
        try:
            rank_div = soup.find('div', {'class': 'league-salary-rank'})
            if rank_div:
                return int(rank_div.text.strip().split('/')[0])
            return None
        except:
            return None

    def _convert_salary_to_euros(self, salary_str):
        """Convierte string de salario a euros (float)."""
        try:
            salary_str = salary_str.lower()
            multiplier = 1
            if 'm' in salary_str:
                multiplier = 1000000
            elif 'k' in salary_str:
                multiplier = 1000
                
            value = float(salary_str.replace('€', '').replace('m', '').replace('k', '').strip())
            return value * multiplier
        except:
            return None

    def process_players(self, players_df):
        """Procesa la lista de jugadores y obtiene su información salarial."""
        results = []
        
        for _, player in tqdm(players_df.iterrows(), total=len(players_df)):
            if pd.isna(player['Nombre_Normalizado_Capology']):
                continue
                
            logger.info(f"Procesando jugador: {player['player_name']}")
            salary_info = self.get_player_salary(player['Nombre_Normalizado_Capology'])
            
            if salary_info:
                player_info = {
                    'player_id': player['player_id'],
                    'player_name': player['player_name'],
                    **salary_info
                }
                results.append(player_info)
            
            time.sleep(3)  # Delay entre requests
            
        return pd.DataFrame(results)

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
            output_path = Path('../data/processed/capology_data.parquet')
            results_df.to_parquet(output_path)
            
            logger.info(f"Datos guardados exitosamente en {output_path}")
            
        except Exception as e:
            logger.error(f"Error en el proceso de scraping: {str(e)}")
            raise

if __name__ == "__main__":
    scraper = CapologyScraper()
    scraper.run('../data/raw/Jugadores.csv') 