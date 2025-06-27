import os
import pandas as pd
import glob

# --- MÉTRICAS OBLIGATORIAS ---
REQUIRED_METRICS = [
    '% Cmp (largos)', 'PrgP', 'Lanz.', 'Bloqueos', 'Desp.', '% de ganados', '3.º ataq.', 'Tkl (Desafíos)',
    'Att', 'Fls', 'Int.', 'Recup.', '% Cmp', '3.º def.', 'Tkld', '3.º cent.', 'PrgC', 'CrAP', 'Succ',
    'Tkl+Int', 'TA', 'FR', '1/3', 'npxG/90', 'Gls/90', '% de TT', 'Exitosa %', 'PA', 'T/90', 'PrgR',
    'npxG/Sh', 'xAG/90'
]

# --- RUTAS DE LIGAS FBREF ---
FBREF_LEAGUE_PATHS = [
    r'C:/Users/zyadb/Documents/tfm/Datos/Datos Jugadores Fede/wetransfer_tfm_2025-06-16_1449/Bundesliga_2024-2025 FBREF',
    r'C:/Users/zyadb/Documents/tfm/Datos/Datos Jugadores Fede/wetransfer_tfm_2025-06-16_1449/Super_Lig_2024-2025 FBREF',
    r'C:/Users/zyadb/Documents/tfm/Datos/Datos Jugadores Fede/wetransfer_tfm_2025-06-16_1449/Serie_A_2024-2025 FBREF',
    r'C:/Users/zyadb/Documents/tfm/Datos/Datos Jugadores Fede/wetransfer_tfm_2025-06-16_1449/Primeira_Liga_2024-2025 FBREF',
    r'C:/Users/zyadb/Documents/tfm/Datos/Datos Jugadores Fede/wetransfer_tfm_2025-06-16_1449/Ligue_1_2024-2025 FBREF',
    r'C:/Users/zyadb/Documents/tfm/Datos/Datos Jugadores Fede/wetransfer_tfm_2025-06-16_1449/La_Liga_2024-2025 FBREF',
    r'C:/Users/zyadb/Documents/tfm/Datos/Datos Jugadores Fede/wetransfer_tfm_2025-06-16_1449/Eredivisie_2024-2025 FBREF',
    r'C:/Users/zyadb/Documents/tfm/Datos/Datos Jugadores Fede/wetransfer_tfm_2025-06-16_1449/EPL_2024-2025 FBREF',
]

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'Datos', 'processed', 'jugadores_fbref_metrics_completo.csv')

all_players = []

for league_path in FBREF_LEAGUE_PATHS:
    if not os.path.exists(league_path):
        continue
    teams = [d for d in os.listdir(league_path) if os.path.isdir(os.path.join(league_path, d))]
    for team in teams:
        team_path = os.path.join(league_path, team)
        player_files = glob.glob(os.path.join(team_path, '**', '*.csv'), recursive=True)
        for player_file in player_files:
            try:
                df_player = None
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df_player = pd.read_csv(player_file, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                if df_player is not None and not df_player.empty:
                    # Añadir metadatos
                    df_player['Liga'] = os.path.basename(league_path).replace('_2024-2025 FBREF', '').replace('_', ' ')
                    df_player['Equipo'] = team
                    df_player['Archivo_Origen'] = player_file
                    # Extraer nombre del jugador del archivo
                    player_name = os.path.basename(player_file).replace('.csv', '')
                    df_player['player_name'] = player_name
                    # Asegurar todas las métricas obligatorias
                    for col in REQUIRED_METRICS:
                        if col not in df_player.columns:
                            df_player[col] = pd.NA
                    # Reordenar columnas: primero metadatos, luego métricas
                    meta_cols = ['player_name', 'Liga', 'Equipo', 'Archivo_Origen']
                    ordered_cols = meta_cols + [c for c in REQUIRED_METRICS if c in df_player.columns]
                    # Añadir el resto de columnas del CSV (si hay más)
                    for c in df_player.columns:
                        if c not in ordered_cols:
                            ordered_cols.append(c)
                    df_player = df_player[ordered_cols]
                    all_players.append(df_player)
            except Exception as e:
                print(f'Error con {player_file}: {e}')
                continue

if all_players:
    result_df = pd.concat(all_players, ignore_index=True)
else:
    result_df = pd.DataFrame(columns=['player_name', 'Liga', 'Equipo', 'Archivo_Origen'] + REQUIRED_METRICS)

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
result_df.to_csv(OUTPUT_PATH, index=False)
print(f'✅ DataFrame consolidado guardado en {OUTPUT_PATH} con {len(result_df)} registros y {len(result_df.columns)} columnas.') 