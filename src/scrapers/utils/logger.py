import logging
import os
from datetime import datetime

def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """
    Configura un logger con formato personalizado y salida a archivo
    
    Args:
        name: Nombre del logger
        log_dir: Directorio donde se guardarán los logs
        
    Returns:
        Logger configurado
    """
    # Crear directorio de logs si no existe
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Crear manejador de archivo
    log_file = os.path.join(log_dir, f"fbref_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    
    # Crear manejador de consola
    console_handler = logging.StreamHandler()
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Agregar manejadores al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 