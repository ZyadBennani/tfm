# Football Data Scraping Project

Este proyecto automatiza la recolección de datos de jugadores de fútbol de múltiples fuentes:
- FBref (estadísticas de rendimiento)
- Transfermarkt (valor de mercado y datos biográficos)
- Capology (información salarial)

## Estructura del Proyecto

```
.
├── data/
│   ├── raw/             # Datos de entrada (Jugadores.csv)
│   ├── processed/       # Datos procesados en formato parquet
│   └── interim/         # Datos intermedios si son necesarios
├── src/
│   ├── scrapers/        # Scripts de scraping para cada fuente
│   │   ├── fbref_scraper.py
│   │   ├── transfermarkt_scraper.py
│   │   └── capology_scraper.py
│   ├── utils/           # Utilidades comunes
│   │   └── data_merger.py
│   └── main.py          # Script principal
├── logs/                # Archivos de log
├── tests/               # Tests unitarios
├── requirements.txt     # Dependencias del proyecto
└── README.md           # Este archivo
```

## Requisitos

- Python ≥ 3.10
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-repositorio>
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Unix o MacOS:
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Instalar Playwright:
```bash
playwright install
```

## Uso

1. Asegúrate de tener el archivo `Jugadores.csv` en la carpeta `data/raw/` con el formato correcto:
   - Columnas requeridas: player_id, ID_Jugador, Loan_Transfered, ID_Liga, contestant_id, ID_Equipo, player_name, etc.
   - Separador: punto y coma (;)
   - Codificación: UTF-8

2. Ejecutar el script principal:
```bash
python src/main.py
```

El script:
1. Recopilará datos de FBref (estadísticas de juego)
2. Recopilará datos de Transfermarkt (valor de mercado)
3. Recopilará datos de Capology (salarios)
4. Combinará todos los datos en un único archivo

## Resultados

Los datos se guardarán en:
- `data/processed/fbref_stats.parquet`
- `data/processed/transfermarkt_data.parquet`
- `data/processed/capology_data.parquet`
- `data/processed/jugadores_full.parquet` (datos combinados)
- `data/processed/jugadores_full.csv` (formato para Excel España)

## Ligas Incluidas

- Premier League (ID: 9)
- Championship (ID: 10)
- Ligue 1 (ID: 13)
- Serie A (ID: 11)
- La Liga (ID: 12)
- La Liga 2 (ID: 17)
- Bundesliga (ID: 20)
- Eredivisie (ID: 23)
- Primeira Liga portuguesa (ID: 32)
- Jupiler League (ID: 37)

## Logs

Los logs se guardan en la carpeta `logs/` con un archivo separado para cada componente:
- `main.log`
- `fbref_scraper.log`
- `transfermarkt_scraper.log`
- `capology_scraper.log`
- `data_merger.log`

## Notas

- El scraping se realiza con delays entre requests para evitar bloqueos
- Se utiliza Playwright para manejar sitios con JavaScript
- Los datos se guardan en formato Parquet para optimizar el almacenamiento
- Se genera un CSV adicional con formato específico para Excel (España)

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request 