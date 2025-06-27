import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import re

def scrape_fbref_player_all_metrics(url):
    """Extrae todas las métricas y valores de la página de FBREF de un jugador, incluyendo tablas en comentarios."""
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.text, 'html.parser')
    data = {}
    # Procesar tablas visibles
    for table in soup.find_all('table'):
        table_id = table.get('id', 'no_id')
        for row in table.find_all('tr'):
            cells = row.find_all(['th', 'td'])
            if len(cells) < 2:
                continue
            metric = cells[0].get_text(strip=True)
            value = cells[-1].get_text(strip=True)
            key = f"{table_id} | {metric}"
            data[key] = value
    # Procesar tablas dentro de comentarios HTML
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment_soup = BeautifulSoup(comment, 'html.parser')
        for table in comment_soup.find_all('table'):
            table_id = table.get('id', 'no_id')
            for row in table.find_all('tr'):
                cells = row.find_all(['th', 'td'])
                if len(cells) < 2:
                    continue
                metric = cells[0].get_text(strip=True)
                value = cells[-1].get_text(strip=True)
                key = f"{table_id} | {metric}"
                data[key] = value
    return data

if __name__ == '__main__':
    url = 'https://fbref.com/en/players/1b278bf5/Lewis-Baker'
    result = scrape_fbref_player_all_metrics(url)
    for k, v in result.items():
        print(f"{k}: {v}") 