# -*- coding: utf-8 -*-
import logging
from src.scrapers.fbref_scraper import FBrefScraper
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scraper():
    try:
        scraper = FBrefScraper()
        test_url = "https://fbref.com/en/players/1b278bf5/Lewis-Baker"
        logger.info(f"Probando scraper con: {test_url}")
        player_data = scraper.get_player_stats(test_url)
        
        if player_data:
            output_dir = Path("data/processed")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "test_player_stats.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(player_data, f, ensure_ascii=False, indent=4)
            logger.info(f"Datos guardados en: {output_file}")
            return True
        else:
            logger.error("No se pudieron obtener datos del jugador")
            return False
    except Exception as e:
        logger.error(f"Error durante la prueba: {str(e)}")
        return False

if __name__ == "__main__":
    test_scraper() 