import logging
from pathlib import Path
import sys
from src.scrapers.fbref_scraper import FBrefScraper
from src.config import LOGS_DIR

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'main.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_single_player():
    """Prueba el scraper con un solo jugador para verificar que funciona."""
    try:
        # Inicializar el scraper
        scraper = FBrefScraper()
        
        # URL de prueba (Lewis Baker)
        test_url = "https://fbref.com/en/players/1b278bf5/Lewis-Baker"
        logger.info(f"Probando scraper con jugador: {test_url}")
        
        # Obtener estadísticas
        stats = scraper.get_player_stats(test_url)
        
        if stats:
            logger.info("Scraping exitoso!")
            logger.info(f"Tablas encontradas: {list(stats.keys())}")
            return True
        else:
            logger.error("No se pudieron obtener estadísticas")
            return False
            
    except Exception as e:
        logger.error(f"Error durante la prueba: {str(e)}")
        return False

if __name__ == "__main__":
    if test_single_player():
        logger.info("Prueba completada con éxito. Podemos proceder con el scraping completo.")
    else:
        logger.error("La prueba falló. Por favor revisa los errores antes de continuar.") 