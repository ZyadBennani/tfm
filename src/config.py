from pathlib import Path

# Directorios base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

# Directorios de datos
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'

# Archivos de entrada/salida
INPUT_FILE = RAW_DATA_DIR / 'Jugadores.csv'
FBREF_OUTPUT = PROCESSED_DATA_DIR / 'fbref_stats.json'

# Crear directorios necesarios
for directory in [LOGS_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True) 