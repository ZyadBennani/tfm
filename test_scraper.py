import logging
import sys
import os
from src.scrapers.fbref_scraper import FBrefScraper
import pandas as pd
import time
from datetime import datetime

# Configurar logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"test_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_single_player(scraper: FBrefScraper, player_id: str, player_name: str) -> bool:
    """
    Prueba el scraper con un solo jugador
    
    Args:
        scraper: Instancia del scraper
        player_id: ID del jugador
        player_name: Nombre del jugador
        
    Returns:
        True si se obtuvieron datos correctamente, False en caso contrario
    """
    try:
        logger.info(f"\nProcesando jugador: {player_name}")
        data = scraper.get_player_data(player_id, player_name)
        
        if data:
            logger.info(f"Tablas extraídas para {player_name}: {list(data.keys())}")
            
            # Guardar cada tabla en un archivo CSV
            output_dir = os.path.join("Datos/fbref_test", player_name.lower().replace(" ", "_"))
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            for table_name, df in data.items():
                output_file = os.path.join(output_dir, f"{table_name}.csv")
                df.to_csv(output_file, index=False, encoding='utf-8')
                logger.info(f"Guardada tabla {table_name} en {output_file}")
                
            return True
        else:
            logger.error(f"No se obtuvieron datos para {player_name}")
            return False
            
    except Exception as e:
        logger.error(f"Error procesando jugador {player_name}: {str(e)}")
        return False

def test_scraper():
    """Prueba el scraper con varios jugadores"""
    try:
        # Crear instancia del scraper
        output_dir = "Datos/fbref_test"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        logger.info("Inicializando scraper...")
        scraper = FBrefScraper(output_dir=output_dir)
        
        # Lista de prueba con 3 jugadores diferentes
        test_players = [
            ("1b278bf5", "Lewis Baker"),  # Mediocampista
            ("dfa084b2", "Aynsley Pears"),  # Portero
            ("2c44a35d", "Emmanuel Dennis")  # Delantero
        ]
        
        # Probar cada jugador
        results = []
        for player_id, player_name in test_players:
            success = test_single_player(scraper, player_id, player_name)
            results.append((player_name, success))
            time.sleep(2)  # Esperar entre jugadores
            
        # Mostrar resumen
        logger.info("\nResumen de resultados:")
        for player_name, success in results:
            status = "✓ Éxito" if success else "✗ Error"
            logger.info(f"{status} - {player_name}")
            
    except Exception as e:
        logger.error(f"Error general en el test: {str(e)}")
    finally:
        if 'scraper' in locals():
            logger.info("Cerrando el scraper...")
            del scraper

if __name__ == "__main__":
    test_scraper() 