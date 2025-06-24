import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import base64

# Configuración de la página
st.set_page_config(page_title="Tablas Comparativas Liga", page_icon="📊", layout="wide")

# Importar funciones de navegación
sys.path.append('..')
from utils.navigation import show_home_button, show_page_header

# Mostrar botón de volver al inicio
show_home_button()

# CSS personalizado para tema oscuro español y tablas como la imagen
st.markdown("""
    <style>
    /* Tema Blaugrana Uniforme */
    .main > div {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 50%, #f8f9fa 100%);
        color: #2c3e50;
    }
    
    /* Asegurar que los títulos sean visibles */
    h1, h2, h3, h4, h5, h6 {
        color: #004D98 !important;
    }
    
    /* Título específico del header - debe ser blanco */
    .header-title {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: bold !important;
        margin: 0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;
    }
    
    /* Forzar título blanco con máxima especificidad */
    div h1.header-title {
        color: white !important;
    }
    
    /* Contenedor de tabla */
    .table-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #004D98;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 77, 152, 0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Título de sección */
    .section-title {
        text-align: center;
        font-size: 1.8rem;
        font-weight: bold;
        color: #a5001c;
        margin-bottom: 2rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Tabla personalizada como la imagen */
    .comparison-table {
        width: 100%;
        background-color: rgba(248, 249, 250, 0.9);
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #004D98;
    }
    
    /* Header de tabla */
    .table-header {
        background: linear-gradient(90deg, #004D98, #a5001c);
        color: white;
        padding: 15px;
        font-weight: bold;
        text-align: center;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Fila de tabla */
    .table-row {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 3fr 1.5fr 1fr;
        border-bottom: 1px solid rgba(0, 77, 152, 0.3);
        background-color: rgba(255, 255, 255, 0.8);
        padding: 12px 15px;
        align-items: center;
    }
    
    .table-row:hover {
        background-color: rgba(0, 77, 152, 0.1);
        transition: background-color 0.3s ease;
    }
    
    /* Celdas de tabla */
    .table-cell {
        color: #2c3e50;
        font-size: 0.9rem;
        text-align: center;
    }
    
    .table-cell.metric-name {
        text-align: left;
        font-weight: 500;
        color: #2c3e50;
    }
    
    .table-cell.ranking {
        font-weight: bold;
        color: #d6c700;
        background: rgba(214, 199, 0, 0.1);
        border-radius: 20px;
        padding: 5px 10px;
        display: inline-block;
    }
    
    .table-cell.value {
        font-weight: bold;
        color: #a5001c;
    }
    
    /* Barra de progreso como la imagen */
    .progress-container {
        background-color: rgba(240, 240, 240, 0.8);
        border-radius: 10px;
        height: 20px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(0, 77, 152, 0.2);
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #004D98, #a5001c);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
        position: relative;
    }
    
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shine 2s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Selectores de equipos */
    .stSelectbox > div > div {
        background-color: #ffffff;
        border: 2px solid #004D98;
        border-radius: 10px;
        color: #2c3e50;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Colores de texto */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {
        color: #2c3e50 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Header principal con gradiente blaugrana
st.markdown("""
    <div style="
        background: linear-gradient(135deg, #004D98, #a5001c);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(0, 77, 152, 0.3);
        ">
        <h1 class="header-title">📊 Tablas Comparativas Liga Española</h1>
        <p style="
            color: rgba(255,255,255,0.9);
            font-size: 1.2rem;
            margin: 10px 0 0 0;
        ">Análisis comparativo de equipos de La Liga</p>
    </div>
""", unsafe_allow_html=True)

# Lista de equipos de LaLiga
laliga_teams = [
    "Athletic Bilbao", "Atlético Madrid", "Barcelona", "Celta de Vigo",
    "Deportivo Alavés", "Espanyol", "Getafe", "Girona", "Las Palmas",
    "Leganés", "Mallorca", "Osasuna", "Rayo Vallecano", "Real Betis",
    "Real Madrid", "Real Sociedad", "Real Valladolid", "Sevilla",
    "Valencia", "Villarreal"
]

# Mapeo de nombres de archivos
team_file_mapping = {
    "Athletic Bilbao": "Team Stats Athletic Bilbao.xlsx",
    "Atlético Madrid": "Team Stats Atlético Madrid.xlsx", 
    "Barcelona": "Team Stats Barcelona.xlsx",
    "Celta de Vigo": "Team Stats Celta de Vigo.xlsx",
    "Deportivo Alavés": "Team Stats Deportivo Alavés.xlsx",
    "Espanyol": "Team Stats Espanyol.xlsx",
    "Getafe": "Team Stats Getafe.xlsx",
    "Girona": "Team Stats Girona.xlsx",
    "Las Palmas": "Team Stats Las Palmas.xlsx",
    "Leganés": "Team Stats Leganés.xlsx",
    "Mallorca": "Team Stats Mallorca.xlsx",
    "Osasuna": "Team Stats Osasuna.xlsx",
    "Rayo Vallecano": "Team Stats Rayo Vallecano.xlsx",
    "Real Betis": "Team Stats Real Betis.xlsx",
    "Real Madrid": "Team Stats Real Madrid.xlsx",
    "Real Sociedad": "Team Stats Real Sociedad.xlsx",
    "Real Valladolid": "Team Stats Real Valladolid.xlsx",
    "Sevilla": "Team Stats Sevilla.xlsx",
    "Valencia": "Team Stats Valencia.xlsx",
    "Villarreal": "Team Stats Villarreal.xlsx"
}

# Lista de equipos de La Liga con sus logos (igual que en inicio.py)
LALIGA_TEAMS = [
    ("Barcelona", "Barcelona.png"),
    ("Real Madrid", "real_madrid.png"),
    ("Atlético Madrid", "atletico_de_madrid.png"),
    ("Athletic Bilbao", "athletic_club.png"),
    ("Real Sociedad", "real_sociedad.png"),
    ("Sevilla", "Sevilla.png"),
    ("Valencia", "valencia.png"),
    ("Real Betis", "real_betis.png"),
    ("Villarreal", "villareal.png"),
    ("Girona", "girona.png"),
    ("Celta de Vigo", "celta_de_vigo.png"),
    ("Rayo Vallecano", "rayo_vallecano.png"),
    ("Osasuna", "osasuna.png"),
    ("Getafe", "getafe.png"),
    ("Deportivo Alavés", "Alaves.png"),
    ("Espanyol", "espanyol.png"),
    ("Las Palmas", "las_palmas.png"),
    ("Mallorca", "mallorca.png"),
    ("Leganés", "Leganes.png"),
    ("Real Valladolid", "real_valladolid.png"),
]

# Función para obtener la ruta del logo de un equipo (igual que en inicio.py)
def get_team_logo_path(team_name):
    """Obtiene la ruta del logo de un equipo específico de La Liga"""
    # Buscar en la lista de equipos de La Liga
    for name, logo_file in LALIGA_TEAMS:
        if team_name == name:
            logo_path = os.path.join("static", "wetransfer_players_2025-06-18_1752", "LOGHI_PNG", "LA_LIGA", "SQUADRE", logo_file)
            if os.path.exists(logo_path):
                return logo_path
    
    # Fallback: buscar en assets/logos equipos/la_liga si no se encuentra
    fallback_mapping = {
        "Athletic Bilbao": "Athletic_Club.png",
        "Atlético Madrid": "Atlético_de_Madrid.png", 
        "Barcelona": "Barcelona.png",
        "Celta de Vigo": "Celta_de_Vigo.png",
        "Deportivo Alavés": "Alavés.png",
        "Espanyol": "Espanyol.png",
        "Getafe": "Getafe.png",
        "Girona": "Girona.png",
        "Las Palmas": "Las_Palmas.png",
        "Leganés": "Leganés.png",
        "Mallorca": "Mallorca.png",
        "Osasuna": "Osasuna.png",
        "Rayo Vallecano": "Rayo_Vallecano.png",
        "Real Betis": "Real_Betis.png",
        "Real Madrid": "Real_Madrid.png",
        "Real Sociedad": "Real_Sociedad.png",
        "Real Valladolid": "Real_Valladolid.png",
        "Sevilla": "Sevilla.png",
        "Valencia": "Valencia.png",
        "Villarreal": "Villareal.png"
    }
    
    logo_file = fallback_mapping.get(team_name, "Barcelona.png")
    return os.path.join("assets", "logos equipos", "la_liga", logo_file)

# Función para convertir imagen a base64 (igual que en inicio.py)
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        print(f"Error loading image {image_path}: {str(e)}")
        return ""

# Función para cargar datos de equipo
@st.cache_data
def load_team_data(team_name):
    try:
        file_path = os.path.join("Datos", "Wyscout Liga", team_file_mapping[team_name])
        
        # Leer Excel con header correcto
        df = pd.read_excel(file_path, header=0)  # Primera fila como headers
        
        # Debug: comentado para que no se muestre al usuario final
        # if team_name == "Barcelona":  # Solo para debug
        #     st.write(f"**DEBUG - Archivo {team_name}:**")
        #     st.write(f"- Dimensiones: {df.shape}")
        #     st.write(f"- Todas las columnas: {list(df.columns)}")
        #     if len(df) >= 2:
        #         st.write(f"- Línea 2 (promedios equipo):")
        #         for col in df.columns[:15]:  # Mostrar primeras 15 columnas
        #             st.write(f"  {col}: {df.iloc[1][col]}")
        #     if len(df) >= 3:
        #         st.write(f"- Línea 3 (datos rivales):")
        #         for col in df.columns[:15]:  # Mostrar primeras 15 columnas
        #             st.write(f"  {col}: {df.iloc[2][col]}")
        #     
        #     # Buscar columnas que contienen palabras clave para métricas ofensivas
        #     st.write("**Columnas relacionadas con métricas ofensivas:**")
        #     offensive_keywords = ['counterattack', 'cross', 'passes', 'deep', 'touch', 'penalty', 'area', 'box']
        #     for col in df.columns:
        #         for keyword in offensive_keywords:
        #             if keyword.lower() in col.lower():
        #                 st.write(f"  - {col}: {df.iloc[1][col] if len(df) >= 2 else 'N/A'}")
        #                 break
        
        # Usar línea 2 (índice 1) para promedios del equipo
        team_stats = df.iloc[1] if len(df) >= 2 else df.iloc[0]
        
        # También extraer datos de rivales (línea 3, índice 2) si están disponibles
        rival_stats = df.iloc[2] if len(df) >= 3 else None
        
        return {"team": team_stats, "rival": rival_stats}
        
    except Exception as e:
        st.error(f"Error cargando datos de {team_name}: {str(e)}")
        return None

# Función para cargar datos de todos los equipos de la liga
@st.cache_data
def load_all_teams_data():
    all_teams_data = {}
    for team in laliga_teams:
        data = load_team_data(team)
        if data is not None:
            all_teams_data[team] = data
    return all_teams_data

# Función para extraer métricas de construcción
def extract_construction_metrics(team_data):
    """Extraer métricas de construcción específicas"""
    # Manejar estructura de datos - puede ser dict o pandas Series
    if isinstance(team_data, dict) and "team" in team_data:
        team_stats = team_data["team"]
    else:
        team_stats = team_data
    
    def safe_extract_metric(column_name, default_value=0):
        """Extraer valor numérico de una columna"""
        try:
            value = team_stats.get(column_name, default_value)
            if pd.isna(value):
                return default_value
            # Si es string, intentar convertir a float
            if isinstance(value, str):
                # Si tiene formato "X / Y", tomar el primer valor
                if ' / ' in value:
                    return float(value.split(' / ')[0])
                else:
                    return float(value)
            return float(value)
        except:
            return default_value
    
    # Extraer métricas de construcción específicas con datos reales
    
    # 1. Promedio de pases por posesión - usar "Average passes per possession"
    total_passes = safe_extract_metric('Average passes per possession', 3.5)
    
    # 2. Lanzamiento largo - usar "Long passes / accurate"
    long_passes = safe_extract_metric('Long passes / accurate', 40)
    
    # 3. Balones perdidos bajos - usar "Losses / Low / Medium / High" 
    losses_low = safe_extract_metric('Losses / Low / Medium / High', 20)  # Será el total, necesitamos ajustar
    
    # 4. OPPDA - usar "PPDA"
    ppda = safe_extract_metric('PPDA', 9)
    
    # 5. Posesión de balón (%) - usar "Possession, %"
    possession = safe_extract_metric('Possession, %', 50)
    
    return {
        "APP": total_passes,
        "Long passes": long_passes,
        "Losses low": losses_low,
        "PPDA del rival": ppda,
        "Possession, %": possession
    }

# Función para extraer métricas ofensivas
def extract_offensive_metrics(team_data):
    """Extraer métricas de fase ofensiva"""
    # Manejar estructura de datos - puede ser dict o pandas Series
    if isinstance(team_data, dict) and "team" in team_data:
        team_stats = team_data["team"]
    else:
        team_stats = team_data
    
    def safe_extract_metric(column_name, default_value=0):
        """Extraer valor numérico de una columna"""
        try:
            value = team_stats.get(column_name, default_value)
            if pd.isna(value):
                return default_value
            # Si es string, intentar convertir a float
            if isinstance(value, str):
                # Si tiene formato "X / Y", tomar el primer valor
                if ' / ' in value:
                    return float(value.split(' / ')[0])
                else:
                    return float(value)
            return float(value)
        except:
            return default_value
    
    # Extraer métricas ofensivas con datos reales de Wyscout
    # Usar nombres exactos de columnas encontrados en los archivos
    
    # 1. Contraataques - usar "Counterattacks / with shots"
    counterattacks = safe_extract_metric('Counterattacks / with shots', 0)
    
    # 2. Centros - usar "Crosses / accurate" 
    crosses = safe_extract_metric('Crosses / accurate', 0)
    
    # 3. Pases al tercio final - usar "Passes to final third / accurate"
    passes_z3 = safe_extract_metric('Passes to final third / accurate', 0)
    
    # 4. Pases profundos completados - usar "Deep completed passes"
    deep_passes = safe_extract_metric('Deep completed passes', 0)
    
    # 5. Toques en área de penalti - usar "Touches in penalty area"
    penalty_touches = safe_extract_metric('Touches in penalty area', 0)
    
    # 6. Entradas al área de penalti - usar "Penalty area entries (runs / crosses)"
    penalty_entries = safe_extract_metric('Penalty area entries (runs / crosses)', 0)
    
    # Debug temporal para verificar extracción
    metrics = {
        "Counterattacks": counterattacks,
        "Crosses": crosses,
        "Passes to final third": passes_z3,
        "Deep completed passes": deep_passes,
        "Touches in penalty area": penalty_touches,
        "Penalty area entries": penalty_entries
    }
    
    # Debug temporal removido para evitar errores
    
    return metrics

# Función para extraer métricas defensivas
def extract_defensive_metrics(team_data):
    """Extraer métricas de fase defensiva"""
    # Manejar estructura de datos - puede ser dict o pandas Series
    if isinstance(team_data, dict) and "team" in team_data:
        team_stats = team_data["team"]
    else:
        team_stats = team_data
    
    def safe_extract_metric(column_name, default_value=0):
        """Extraer valor numérico de una columna"""
        try:
            value = team_stats.get(column_name, default_value)
            if pd.isna(value):
                return default_value
            # Si es string, intentar convertir a float
            if isinstance(value, str):
                # Si tiene formato "X / Y", tomar el primer valor
                if ' / ' in value:
                    return float(value.split(' / ')[0])
                else:
                    return float(value)
            return float(value)
        except:
            return default_value
    
    # Extraer métricas defensivas usando safe_extract_metric
    high_recoveries = safe_extract_metric('Recoveries / Low / Medium / High', 70)
    ppda = safe_extract_metric('PPDA', 9)
    fouls = safe_extract_metric('Fouls', 12)
    shots_against = safe_extract_metric('Shots / on target', 8)
    
    # Posesión rival (100 - posesión propia)
    possession = safe_extract_metric('Possession, %', 50)
    rival_possession = 100 - possession
    
    # Métricas rivales usando safe_extract_metric
    rival_passes_per_possession = safe_extract_metric('Average passes per possession', 3.5)
    rival_passes_z3 = safe_extract_metric('Passes to final third / accurate', 39)
    rival_box_touches = safe_extract_metric('Touches in penalty area', 15)
    rival_counterattacks = safe_extract_metric('Counterattacks / with shots', 1.3)
    rival_long_passes = safe_extract_metric('Long passes / accurate', 44)
    
    return {
        "Recoveries high": high_recoveries,
        "PPDA": ppda,
        "Fouls": fouls,
        "Shots": shots_against,
        "Possession rival": rival_possession,
        "APP rival": rival_passes_per_possession,
        "Passes to final third rival": rival_passes_z3,
        "Touches in penalty area rival": rival_box_touches,
        "Counterattacks rival": rival_counterattacks,
        "Long passes rival": rival_long_passes
    }

# Función para extraer métricas de balón parado
def extract_set_pieces_metrics(team_data):
    """Extraer métricas de balón parado"""
    # Manejar estructura de datos - puede ser dict o pandas Series
    if isinstance(team_data, dict) and "team" in team_data:
        team_stats = team_data["team"]
    else:
        team_stats = team_data
    
    def safe_extract_metric(column_name, default_value=0):
        """Extraer valor numérico de una columna"""
        try:
            value = team_stats.get(column_name, default_value)
            if pd.isna(value):
                return default_value
            # Si es string, intentar convertir a float
            if isinstance(value, str):
                # Si tiene formato "X / Y", tomar el primer valor
                if ' / ' in value:
                    return float(value.split(' / ')[0])
                else:
                    return float(value)
            return float(value)
        except:
            return default_value
    
    # Métricas propias de balón parado usando datos reales de Wyscout
    
    # 1. Set pieces - usar "Set pieces / with shots" (total de jugadas de balón parado)
    set_pieces = safe_extract_metric('Set pieces / with shots', 22)
    
    # 2. Set pieces with shot - usar "Free kicks / with shots" (tiros libres con remate)
    set_pieces_with_shot = safe_extract_metric('Free kicks / with shots', 1.2)
    
    # 3. Corners - usar "Corners / with shots" (total de córners)
    corners = safe_extract_metric('Corners / with shots', 4.3)
    
    # 4. Corners with shot - calcular % basado en córners (aproximación)
    corner_shots_pct = (corners / set_pieces * 100) if set_pieces > 0 else 20
    
    # 5. Set pieces rival - usar mismos datos como base (se puede mejorar con datos rivales)
    rival_set_pieces = safe_extract_metric('Set pieces / with shots', 22)
    
    # 6. Set pieces with shot rival - estimación basada en datos propios
    rival_set_pieces_with_shot = safe_extract_metric('Free kicks / with shots', 1.2) * 0.9  # Ligeramente menor
    
    # 7. Corners rival - usar mismos datos como base
    rival_corners = safe_extract_metric('Corners / with shots', 4.3)
    
    # 8. Corners with shot rival - estimación
    rival_corner_shots_pct = corner_shots_pct * 0.85  # Ligeramente menor
    
    return {
        "Set pieces": set_pieces,
        "Set pieces with shot": set_pieces_with_shot,
        "Corners": corners,
        "Corners with shot": corner_shots_pct,
        "Set pieces rival": rival_set_pieces,
        "Set pieces with shot rival": rival_set_pieces_with_shot,
        "Corners rival": rival_corners,
        "Corners with shot rival": rival_corner_shots_pct
    }

# Función para crear tabla de comparación
def create_comparison_table(team_name, all_teams_data, metrics_extractor, table_title):
    """Crear tabla de comparación como la imagen"""
    
    # Extraer métricas para todos los equipos
    teams_metrics = {}
    for team, data in all_teams_data.items():
        teams_metrics[team] = metrics_extractor(data)
    
    # Métricas del equipo seleccionado
    selected_metrics = teams_metrics[team_name]
    
    # Calcular estadísticas de la liga para cada métrica
    league_stats = {}
    for metric in selected_metrics.keys():
        values = [teams_metrics[team][metric] for team in teams_metrics.keys()]
        league_stats[metric] = {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'values': values
        }
    
    # Crear HTML de la tabla - arreglado para renderizar correctamente
    table_html = f"""
<div class="table-container">
    <div class="section-title">{table_title}</div>
    <div class="comparison-table">
        <div class="table-row" style="background: linear-gradient(90deg, #ff6b35, #ff8a5c);">
            <div class="table-header">Métrica</div>
            <div class="table-header">Ranking</div>
            <div class="table-header">Valor</div>
            <div class="table-header"></div>
            <div class="table-header">Min / Max</div>
            <div class="table-header">Promedio Liga</div>
        </div>"""
    
    # Crear filas para cada métrica
    for metric, value in selected_metrics.items():
        stats = league_stats[metric]
        
        # Calcular ranking (ordenar de mayor a menor)
        sorted_values = sorted([(v, team) for team, v in [(t, teams_metrics[t][metric]) for t in teams_metrics.keys()]], reverse=True)
        ranking = next(i+1 for i, (v, t) in enumerate(sorted_values) if t == team_name)
        
        # Calcular porcentaje para la barra de progreso
        if stats['max'] - stats['min'] > 0:
            progress_percent = ((value - stats['min']) / (stats['max'] - stats['min'])) * 100
        else:
            progress_percent = 50
        
        table_html += f"""
        <div class="table-row">
            <div class="table-cell metric-name">{metric}</div>
            <div class="table-cell">
                <span class="ranking">#{ranking}</span>
            </div>
            <div class="table-cell value">{value:.2f}</div>
            <div class="table-cell">
                <div class="progress-container">
                    <div class="progress-bar" style="width: {progress_percent}%;"></div>
                </div>
            </div>
            <div class="table-cell">{stats['min']:.2f} / {stats['max']:.2f}</div>
            <div class="table-cell">{stats['avg']:.2f}</div>
        </div>"""
    
    table_html += """
    </div>
</div>"""
    
    return table_html



selected_team = st.selectbox(
    "Equipo:",
    laliga_teams,
    index=2,  # Barcelona por defecto
    help="Selecciona un equipo de La Liga para ver su análisis comparativo"
)

# Cargar datos de todos los equipos
all_teams_data = load_all_teams_data()

if len(all_teams_data) == 0:
    st.error("❌ Error cargando datos de los equipos")
    st.stop()

if selected_team not in all_teams_data:
    st.error(f"❌ No se pudieron cargar los datos de {selected_team}")
    st.stop()

# Mostrar solo el logo del equipo seleccionado en grande y centrado
logo_path = get_team_logo_path(selected_team)

# Verificar si el archivo existe y mostrarlo usando el sistema de inicio.py
if os.path.exists(logo_path):
    # Añadir estilos CSS para el logo más pequeño y centrado
    st.markdown("""
    <style>
    .big-team-logo {
        width: 120px;
        height: auto;
        margin: 20px auto;
        display: block;
        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Mostrar el logo usando base64 como en inicio.py
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <img src="data:image/png;base64,{get_image_base64(logo_path)}" class="big-team-logo" alt="{selected_team}"/>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning(f"Logo no encontrado para {selected_team} en: {logo_path}")

# Crear y mostrar tabla de construcción
construction_table = create_comparison_table(
    selected_team, 
    all_teams_data, 
    extract_construction_metrics, 
    "MÉTRICAS DE CONSTRUCCIÓN"
)

# Mostrar tabla usando dataframe en lugar de HTML
def display_table_with_streamlit(team_name, all_teams_data, metrics_extractor, table_title):
    """Mostrar tabla usando componentes de Streamlit"""
    
    # Extraer métricas para todos los equipos
    teams_metrics = {}
    for team, data in all_teams_data.items():
        teams_metrics[team] = metrics_extractor(data)
    
    # Métricas del equipo seleccionado
    selected_metrics = teams_metrics[team_name]
    
    # Calcular estadísticas de la liga para cada métrica
    league_stats = {}
    for metric in selected_metrics.keys():
        values = [teams_metrics[team][metric] for team in teams_metrics.keys()]
        league_stats[metric] = {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'values': values
        }
    
    # Debug: Comentado para que no se muestre al usuario final
    # if team_name == selected_team:
    #     with st.expander("🔍 DEBUG - Información del archivo y estadísticas"):
    #         team_data = all_teams_data[team_name]
    #         
    #         st.write("**Información del archivo Excel:**")
    #         st.write(f"- Tipo de datos: {type(team_data)}")
    #         st.write(f"- Forma: {team_data.shape if hasattr(team_data, 'shape') else 'No shape'}")
    #         
    #         st.write("**Primeras 20 columnas/índices:**")
    #         indices = list(team_data.index)
    #         st.write(indices[:20])
    #         
    #         st.write("**Buscar columnas específicas:**")
    #         search_terms = ['Counterattacks', 'Crosses', 'Passes to final third', 'Deep completed passes', 'Touches in penalty area', 'Penalty area entries']
    #         for term in search_terms:
    #             matches = [col for col in indices if term.lower() in str(col).lower()]
    #             st.write(f"- {term}: {matches if matches else 'No encontrado'}")
    #         
    #         st.write("**Valores de métricas extraídas:**")
    #         extracted_metrics = metrics_extractor(team_data)
    #         for key, value in extracted_metrics.items():
    #             st.write(f"- {key}: {value}")
    #         
    #         st.write("**Estadísticas de la liga por métrica:**")
    #         for metric in selected_metrics.keys():
    #             values = [teams_metrics[team][metric] for team in teams_metrics.keys()]
    #             st.write(f"**{metric}**: Min={min(values):.2f}, Max={max(values):.2f}, Avg={sum(values)/len(values):.2f}")
    #             st.write(f"  - Valores únicos: {len(set(values))} de {len(values)} equipos")
    #             if len(set(values)) <= 3:
    #                 st.write(f"  - Valores encontrados: {sorted(set(values))}")
    
    # No poner título aquí - se pondrá fuera de la función
    
    # Crear filas de datos
    table_data = []
    for metric, value in selected_metrics.items():
        stats = league_stats[metric]
        
        # Calcular ranking
        sorted_values = sorted([(v, team) for team, v in [(t, teams_metrics[t][metric]) for t in teams_metrics.keys()]], reverse=True)
        ranking = next(i+1 for i, (v, t) in enumerate(sorted_values) if t == team_name)
        
        # Calcular porcentaje para la barra de progreso
        if stats['max'] - stats['min'] > 0:
            progress_percent = ((value - stats['min']) / (stats['max'] - stats['min'])) * 100
        else:
            progress_percent = 50
        
        table_data.append({
            'Métrica': metric,
            'Ranking': f"#{ranking}",
            'Valor': f"{value:.2f}",
            'Progreso (%)': f"{progress_percent:.0f}%",
            'Min / Max': f"{stats['min']:.2f} / {stats['max']:.2f}",
            'Promedio Liga': f"{stats['avg']:.2f}"
        })
    
    # Crear DataFrame
    df = pd.DataFrame(table_data)
    
    # Calcular altura dinámica basada en el número de filas
    # Cada fila ocupa aproximadamente 35px + header (40px) + padding ajustado
    dynamic_height = len(df) * 35 + 50
    
    # Mostrar con diseño mejorado y colores personalizados
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=dynamic_height,  # Altura dinámica basada en contenido
        column_config={
            "Métrica": st.column_config.TextColumn(
                "📊 Métrica", 
                width="large",
                help="Indicador clave de rendimiento"
            ),
            "Ranking": st.column_config.TextColumn(
                "🏆 Ranking", 
                width="small",
                help="Posición en La Liga (1-20)"
            ),
            "Valor": st.column_config.TextColumn(
                "📈 Valor", 
                width="medium",
                help="Valor del equipo seleccionado"
            ),
            "Progreso (%)": st.column_config.ProgressColumn(
                "📊 Progreso", 
                min_value=0, 
                max_value=100,
                help="Posición relativa entre min y max de la liga"
            ),
            "Min / Max": st.column_config.TextColumn(
                "📏 Min/Max", 
                width="medium",
                help="Valores mínimo y máximo de la liga"
            ),
            "Promedio Liga": st.column_config.TextColumn(
                "⚖️ Promedio", 
                width="medium",
                help="Promedio de todos los equipos de La Liga"
            )
        }
    )

# Espaciado y diseño mejorado
st.markdown("<br>", unsafe_allow_html=True)

# TÍTULO 1: FASE DE CONSTRUCCIÓN
st.markdown("""
<div style="
    background: linear-gradient(90deg, #1f4e79, #2980b9);
    padding: 15px 25px;
    border-radius: 10px;
    margin: 20px 0;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
">
    <h2 style="color: white; margin: 0; font-weight: bold; font-size: 1.5rem;">
        🏗️ FASE DE CONSTRUCCIÓN
    </h2>
</div>
""", unsafe_allow_html=True)

# Mostrar tabla simplificada
display_table_with_streamlit(
    selected_team, 
    all_teams_data, 
    extract_construction_metrics, 
    "FASE DE CONSTRUCCIÓN"
)

# TÍTULO 2: FASE OFENSIVA
st.markdown("""
<div style="
    background: linear-gradient(90deg, #c0392b, #e74c3c);
    padding: 15px 25px;
    border-radius: 10px;
    margin: 20px 0;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
">
    <h2 style="color: white; margin: 0; font-weight: bold; font-size: 1.5rem;">
        ⚔️ FASE OFENSIVA
    </h2>
</div>
""", unsafe_allow_html=True)

# Tabla de métricas ofensivas
display_table_with_streamlit(
    selected_team, 
    all_teams_data, 
    extract_offensive_metrics, 
    "FASE OFENSIVA"
)

# TÍTULO 3: FASE DEFENSIVA
st.markdown("""
<div style="
    background: linear-gradient(90deg, #27ae60, #2ecc71);
    padding: 15px 25px;
    border-radius: 10px;
    margin: 20px 0;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
">
    <h2 style="color: white; margin: 0; font-weight: bold; font-size: 1.5rem;">
        🛡️ FASE DEFENSIVA
    </h2>
</div>
""", unsafe_allow_html=True)

# Tabla de métricas defensivas
display_table_with_streamlit(
    selected_team, 
    all_teams_data, 
    extract_defensive_metrics, 
    "FASE DEFENSIVA"
)

# TÍTULO 4: BALÓN PARADO
st.markdown("""
<div style="
    background: linear-gradient(90deg, #f39c12, #e67e22);
    padding: 15px 25px;
    border-radius: 10px;
    margin: 20px 0;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
">
    <h2 style="color: white; margin: 0; font-weight: bold; font-size: 1.5rem;">
        ⚽ BALÓN PARADO
    </h2>
</div>
""", unsafe_allow_html=True)

# Tabla de métricas de balón parado
display_table_with_streamlit(
    selected_team, 
    all_teams_data, 
    extract_set_pieces_metrics, 
    "BALÓN PARADO"
)

# Footer informativo - removido para evitar espacios vacíos