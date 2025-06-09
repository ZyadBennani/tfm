import pandas as pd
import logging
from pathlib import Path
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/data_merger.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('data_merger')

class DataMerger:
    def __init__(self):
        self.processed_dir = Path('../data/processed')
        
    def load_data(self):
        """Carga los datos de los tres archivos parquet."""
        try:
            fbref_data = pd.read_parquet(self.processed_dir / 'fbref_stats.parquet')
            transfermarkt_data = pd.read_parquet(self.processed_dir / 'transfermarkt_data.parquet')
            capology_data = pd.read_parquet(self.processed_dir / 'capology_data.parquet')
            
            return fbref_data, transfermarkt_data, capology_data
        except Exception as e:
            logger.error(f"Error cargando datos: {str(e)}")
            raise

    def merge_data(self, fbref_data, transfermarkt_data, capology_data):
        """Combina los datos de las tres fuentes."""
        try:
            # Merge FBref con Transfermarkt
            merged_df = pd.merge(
                fbref_data,
                transfermarkt_data,
                on=['player_id', 'player_name'],
                how='outer'
            )
            
            # Merge con Capology
            final_df = pd.merge(
                merged_df,
                capology_data,
                on=['player_id', 'player_name'],
                how='outer'
            )
            
            return final_df
        except Exception as e:
            logger.error(f"Error combinando datos: {str(e)}")
            raise

    def save_data(self, df, save_csv=True):
        """Guarda los datos en formato parquet y opcionalmente en CSV."""
        try:
            # Guardar en Parquet
            parquet_path = self.processed_dir / 'jugadores_full.parquet'
            df.to_parquet(parquet_path)
            logger.info(f"Datos guardados en {parquet_path}")
            
            if save_csv:
                # Guardar en CSV con formato específico para Excel (España)
                csv_path = self.processed_dir / 'jugadores_full.csv'
                df.to_csv(
                    csv_path,
                    index=False,
                    sep=';',
                    decimal=',',
                    float_format='%.3f'
                )
                logger.info(f"Datos guardados en {csv_path}")
                
        except Exception as e:
            logger.error(f"Error guardando datos: {str(e)}")
            raise

    def run(self, save_csv=True):
        """Ejecuta el proceso completo de combinación de datos."""
        try:
            logger.info("Iniciando proceso de combinación de datos...")
            
            # Cargar datos
            fbref_data, transfermarkt_data, capology_data = self.load_data()
            logger.info("Datos cargados exitosamente")
            
            # Combinar datos
            final_df = self.merge_data(fbref_data, transfermarkt_data, capology_data)
            logger.info("Datos combinados exitosamente")
            
            # Guardar resultados
            self.save_data(final_df, save_csv)
            logger.info("Proceso completado exitosamente")
            
        except Exception as e:
            logger.error(f"Error en el proceso de combinación: {str(e)}")
            raise

if __name__ == "__main__":
    merger = DataMerger()
    merger.run() 