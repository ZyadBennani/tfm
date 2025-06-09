# -*- coding: utf-8 -*-
import logging
from src.scrapers.fbref_scraper import FBrefScraper
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scraper():
    """Prueba el scraper con un jugador de ejemplo."""
    try:
        # Inicializar scraper
        scraper = FBrefScraper()
        
        # URL de prueba (Lewis Baker)
        test_url = "https://fbref.com/en/players/1b278bf5/Lewis-Baker"
        logger.info(f"Probando scraper con: {test_url}")
        
        # Obtener datos
        player_data = scraper.get_player_stats(test_url)
        
        if player_data:
            # Crear directorio para resultados si no existe
            output_dir = Path("data/processed")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Guardar resultados
            output_file = output_dir / "test_player_stats.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(player_data, f, ensure_ascii=False, indent=4)
                
            logger.info(f"Datos guardados en: {output_file}")
            logger.info(f"Información básica del jugador: {player_data['info']}")
            logger.info(f"Tablas de estadísticas encontradas: {list(player_data['stats'].keys())}")
            return True
        else:
            logger.error("No se pudieron obtener datos del jugador")
            return False
            
    except Exception as e:
        logger.error(f"Error durante la prueba: {str(e)}")
        return False

if __name__ == "__main__":
    test_scraper() 