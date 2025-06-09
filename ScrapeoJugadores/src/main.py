import logging
from pathlib import Path
import sys
from scrapers.fbref_scraper import FBrefScraper
from scrapers.transfermarkt_scraper import TransfermarktScraper
from scrapers.capology_scraper import CapologyScraper
from utils.data_merger import DataMerger

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('main')

def main():
    """Ejecuta el proceso completo de scraping y combinación de datos."""
    try:
        logger.info("Iniciando proceso de scraping...")
        
        # Crear directorios necesarios si no existen
        Path('data/processed').mkdir(parents=True, exist_ok=True)
        Path('logs').mkdir(exist_ok=True)
        
        # 1. Scraping de FBref
        logger.info("Iniciando scraping de FBref...")
        fbref_scraper = FBrefScraper()
        fbref_scraper.run('data/raw/Jugadores.csv')
        logger.info("Scraping de FBref completado")
        
        # 2. Scraping de Transfermarkt
        logger.info("Iniciando scraping de Transfermarkt...")
        transfermarkt_scraper = TransfermarktScraper()
        transfermarkt_scraper.run('data/raw/Jugadores.csv')
        logger.info("Scraping de Transfermarkt completado")
        
        # 3. Scraping de Capology
        logger.info("Iniciando scraping de Capology...")
        capology_scraper = CapologyScraper()
        capology_scraper.run('data/raw/Jugadores.csv')
        logger.info("Scraping de Capology completado")
        
        # 4. Combinar datos
        logger.info("Iniciando combinación de datos...")
        merger = DataMerger()
        merger.run()
        logger.info("Combinación de datos completada")
        
        logger.info("Proceso completo finalizado exitosamente")
        
    except Exception as e:
        logger.error(f"Error en el proceso: {str(e)}")
        raise

if __name__ == "__main__":
    main() 