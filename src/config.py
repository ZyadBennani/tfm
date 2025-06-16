import os
from pathlib import Path

# Obtener el directorio raíz del proyecto
ROOT_DIR = Path(__file__).parent.parent

# Directorios principales
DATA_DIR = ROOT_DIR / "Datos"
LOGS_DIR = ROOT_DIR / "logs"
OUTPUT_DIR = DATA_DIR / "fbref_data"

# Archivos de entrada/salida
INPUT_FILE = DATA_DIR / "Jugadores.csv"
FBREF_OUTPUT = DATA_DIR / "fbref_stats.parquet"

# Crear directorios si no existen
for directory in [DATA_DIR, LOGS_DIR, OUTPUT_DIR]:
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True) 