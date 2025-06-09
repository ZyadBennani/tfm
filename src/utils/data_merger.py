import pandas as pd
import logging
import sys
from src.config import LOGS_DIR, FBREF_OUTPUT, TRANSFERMARKT_OUTPUT, CAPOLOGY_OUTPUT, MERGED_OUTPUT

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'data_merger.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('data_merger')

class DataMerger:
    def __init__(self):
        self.fbref_data = None
        self.transfermarkt_data = None
        self.capology_data = None
        
    def load_data(self):
        """Carga los datos de los diferentes archivos parquet."""
        try:
            self.fbref_data = pd.read_parquet(FBREF_OUTPUT)
            self.transfermarkt_data = pd.read_parquet(TRANSFERMARKT_OUTPUT)
            self.capology_data = pd.read_parquet(CAPOLOGY_OUTPUT)
            logger.info("Datos cargados exitosamente")
        except Exception as e:
            logger.error(f"Error cargando los datos: {str(e)}")
            raise
            
    def merge_data(self):
        """Combina los datos de las diferentes fuentes."""
        try:
            # Combinar datos de FBref y Transfermarkt
            merged_df = pd.merge(
                self.fbref_data,
                self.transfermarkt_data,
                on=['player_id', 'player_name'],
                how='outer'
            )
            
            # Combinar con datos de Capology
            merged_df = pd.merge(
                merged_df,
                self.capology_data,
                on=['player_id', 'player_name'],
                how='outer'
            )
            
            logger.info("Datos combinados exitosamente")
            return merged_df
            
        except Exception as e:
            logger.error(f"Error combinando los datos: {str(e)}")
            raise
            
    def run(self):
        """Ejecuta el proceso completo de combinación de datos."""
        try:
            # Cargar datos
            self.load_data()
            
            # Combinar datos
            merged_df = self.merge_data()
            
            # Guardar resultados
            merged_df.to_parquet(MERGED_OUTPUT)
            
            # Guardar también en formato Excel para compatibilidad
            excel_output = MERGED_OUTPUT.with_suffix('.xlsx')
            merged_df.to_excel(excel_output, index=False)
            
            logger.info(f"Datos guardados exitosamente en {MERGED_OUTPUT} y {excel_output}")
            
        except Exception as e:
            logger.error(f"Error en el proceso de combinación: {str(e)}")
            raise

if __name__ == "__main__":
    merger = DataMerger()
    merger.run() 