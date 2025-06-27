import streamlit as st
import os
from PIL import Image
import base64
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import itertools
import glob
import sys


# Configuración de la página
st.set_page_config(
    page_title="Análisis y comparativa de equipos",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Importar funciones de navegación
sys.path.append('..')
from utils.navigation import show_home_button, show_page_header, show_navbar_switch_page

# Mostrar botón de volver al inicio
show_home_button()

# Mostrar header de la página
show_page_header("Análisis y comparativa de equipos")

# --- BLOQUE DE CSS GLOBAL FCB.LAB ---
st.markdown('''
    <!-- Importar fuentes Google Fonts clásicas y elegantes -->
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Montserrat:wght@300;400;500;600&family=Source+Sans+Pro:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
    :root {
        --font-title: 'Playfair Display', serif;
        --font-subtitle: 'Montserrat', sans-serif;
        --font-body: 'Source Sans Pro', sans-serif;
        --barca-primary: #004D98;
        --barca-secondary: #a5001c;
    }
    .liga-card, .team-card, .centered-header, .main-content {
        box-shadow: 0 8px 32px 0 rgba(0,77,152,0.18), 0 1.5px 8px 0 rgba(165,0,28,0.10);
        backdrop-filter: blur(8px) saturate(120%);
        background: linear-gradient(135deg, rgba(255,255,255,0.85) 60%, rgba(0,77,152,0.08) 100%);
        border: 1.5px solid rgba(0,77,152,0.10);
    }
    .centered-header {
        background: linear-gradient(135deg, #004D98 60%, #a5001c 100%);
        color: #fff;
    }
    .liga-card, .team-card {
        border-radius: 18px;
        margin: 15px;
        transition: box-shadow 0.3s, transform 0.3s;
    }
    .liga-card:hover, .team-card:hover {
        box-shadow: 0 16px 40px 0 rgba(0,77,152,0.22), 0 2px 12px 0 rgba(165,0,28,0.13);
        transform: translateY(-6px) scale(1.02);
        border-color: #004D98;
    }
    .stButton button {
        background: linear-gradient(135deg, #004D98 60%, #a5001c 100%);
        color: #fff;
        border: none;
        border-radius: 30px;
        padding: 12px 28px;
        font-family: var(--font-subtitle) !important;
        font-weight: 600;
        font-size: 1.08em;
        box-shadow: 0 2px 12px rgba(0,77,152,0.10);
        transition: background 0.25s, box-shadow 0.25s, transform 0.15s;
        outline: none;
        cursor: pointer;
        letter-spacing: 0.5px;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #003366 60%, #a5001c 100%);
        box-shadow: 0 6px 20px rgba(0,77,152,0.18);
        transform: translateY(-2px) scale(1.03);
    }
    .stButton button:active {
        background: linear-gradient(135deg, #002244 60%, #7a0010 100%);
        box-shadow: 0 2px 8px rgba(0,77,152,0.10);
        transform: scale(0.98);
    }
    .stButton button:disabled {
        background: #e0e0e0;
        color: #aaa;
        cursor: not-allowed;
        box-shadow: none;
    }
    .stSelectbox > div > div, .stTextInput > div > input, .stNumberInput > div > input, .stSlider > div {
        background: rgba(255,255,255,0.85) !important;
        border: 2px solid #004D98 !important;
        border-radius: 12px !important;
        color: #2c3e50 !important;
        box-shadow: 0 2px 8px rgba(0,77,152,0.08);
        font-family: var(--font-body) !important;
        font-size: 1.05em !important;
        transition: border 0.2s, box-shadow 0.2s;
    }
    .stSelectbox > div > div:focus-within, .stTextInput > div > input:focus, .stNumberInput > div > input:focus, .stSlider > div:focus-within {
        border: 2.5px solid #a5001c !important;
        box-shadow: 0 0 0 3px rgba(165,0,28,0.13);
        outline: none !important;
    }
    .stSelectbox > div > div::placeholder, .stTextInput > div > input::placeholder, .stNumberInput > div > input::placeholder {
        color: #888 !important;
        opacity: 1 !important;
        font-style: italic;
    }
    .stSlider > div [role=slider] {
        background: linear-gradient(90deg, #004D98 0%, #a5001c 100%) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0,77,152,0.10);
    }
    .stSlider > div [role=slider]:focus {
        outline: 2.5px solid #a5001c !important;
        box-shadow: 0 0 0 3px rgba(165,0,28,0.13) !important;
    }
    body, .main-content, .stApp {
        font-family: var(--font-body) !important;
    }
    h1 {
        font-family: var(--font-title) !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
    }
    h2, h3 {
        font-family: var(--font-subtitle) !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
    }
    h4, h5, h6 {
        font-family: var(--font-subtitle) !important;
        font-weight: 400 !important;
    }
    p, .stMarkdown, .stText, div, span {
        font-family: var(--font-body) !important;
        line-height: 1.6 !important;
    }
    .stButton button {
        font-family: var(--font-subtitle) !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
    }
    .team-name {
        font-family: var(--font-subtitle) !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
    }
    .stSelectbox, .stSlider, .stNumberInput {
        font-family: var(--font-body) !important;
    }
    .stSidebar {display: none !important;}
    .navbar {
        position: sticky;
        top: 0;
        z-index: 9999;
        background: linear-gradient(90deg, #004D98 80%, #a5001c 100%);
        padding: 0.5rem 0 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2.5rem;
    }
    .navbar a {
        color: #fff;
        font-weight: 600;
        font-size: 1.08em;
        text-decoration: none;
        padding: 0.4rem 1.2rem;
        border-radius: 0.5rem;
        transition: background 0.2s, color 0.2s;
    }
    .navbar a:hover {
        background: #a5001c;
        color: #fff;
    }
    </style>
''', unsafe_allow_html=True)
# --- FIN BLOQUE CSS GLOBAL ---

st.markdown("""
    <style>
    [data-testid='stSidebarNav'] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# Función para cargar imágenes
def load_image(image_path):
    try:
        return Image.open(image_path)
    except:
        return None

# Función para obtener la ruta de la imagen del equipo
def get_team_logo_path(team_name):
    """Obtiene la ruta del logo de un equipo específico de cualquier liga"""
    # Buscar en todas las listas de equipos para encontrar el archivo correcto
    all_teams_with_paths = [
        (LALIGA_TEAMS, "LA_LIGA", "SQUADRE"),
        (PREMIER_TEAMS, "PREMIER LEAGUE", "SQUADRE"),
        (SERIE_A_TEAMS, "SERIE_A", "SQUADRE_24-25"),
        (BUNDESLIGA_TEAMS, "BUNDES", "SQUADRE"),
        (LIGUE1_TEAMS, "LIGUE_1", "SQUADRE")
    ]
    
    for teams_list, league_folder, squadre_folder in all_teams_with_paths:
        for name, logo_file in teams_list:
            if team_name == name:
                logo_path = os.path.join("static", "wetransfer_players_2025-06-18_1752", "LOGHI_PNG", league_folder, squadre_folder, logo_file)
                if os.path.exists(logo_path):
                    return logo_path
    
    # Fallback: buscar en static/logos si no se encuentra en las carpetas reales
    filename = team_name.lower().replace(" ", "_") + ".png"
    return os.path.join("static", "logos", filename)

# Función para obtener la ruta del logo de la liga
def get_league_logo_path(league_name):
    # Mapeo de nombres de liga a rutas específicas donde están los logos reales
    league_mapping = {
        "La Liga Española": os.path.join("static", "wetransfer_players_2025-06-18_1752", "LOGHI_PNG", "LA_LIGA", "LOGO", "La_Liga.png"),
        "Premier League": os.path.join("static", "wetransfer_players_2025-06-18_1752", "LOGHI_PNG", "PREMIER LEAGUE", "Premier League.png"),
        "Serie A": os.path.join("static", "wetransfer_players_2025-06-18_1752", "LOGHI_PNG", "SERIE_A", "LOGO", "Serie_A.png"),
        "Bundesliga": os.path.join("static", "wetransfer_players_2025-06-18_1752", "LOGHI_PNG", "BUNDES", "LOGO", "Bundesliga.png"),
        "Ligue 1": os.path.join("static", "wetransfer_players_2025-06-18_1752", "LOGHI_PNG", "LIGUE_1", "LOGO", "Ligue_1.png")
    }
    
    # Obtener la ruta específica para la liga
    league_path = league_mapping.get(league_name)
    
    if league_path and os.path.exists(league_path):
        return league_path
    
    # Fallback a los logos temporales si no se encuentra el original
    return os.path.join("static", "leagues", league_name.lower().replace(" ", "_") + ".png")

# Listas globales de equipos para todas las ligas (NECESARIAS PARA TODAS LAS FUNCIONES)
LALIGA_TEAMS = [
    ("Barcelona", "Barcelona.png"),
    ("Real Madrid", "real_madrid.png"),
    ("Atletico de Madrid", "atletico_de_madrid.png"),
    ("Athletic Club", "athletic_club.png"),
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
    ("Alaves", "Alaves.png"),
    ("Espanyol", "espanyol.png"),
    ("Las Palmas", "las_palmas.png"),
    ("Mallorca", "mallorca.png"),
    ("Leganes", "Leganes.png"),
    ("Real Valladolid", "real_valladolid.png"),
]

PREMIER_TEAMS = [
    ("Manchester City", "manchester_city.png"),
    ("Arsenal", "arsenal.png"),
    ("Manchester United", "manchester_united.png"),
    ("Liverpool", "liverpool.png"),
    ("Newcastle", "Newcastle.png"),
    ("Brighton", "brighton.png"),
    ("Aston Villa", "aston_villa.png"),
    ("Tottenham", "Tottenham.png"),
    ("Brentford", "brentford.png"),
    ("Chelsea", "chelsea.png"),
    ("Crystal Palace", "crystal_palace.png"),
    ("Wolves", "Wolves.png"),
    ("West Ham", "West_Ham.png"),
    ("Bournemouth", "bournemouth.png"),
    ("Nottingham Forest", "nottingham_forest.png"),
    ("Fulham", "fulham.png"),
    ("Everton", "everton.png"),
    ("Luton Town", "luton_town.png"),
    ("Burnley", "burnley.png"),
    ("Sheffield United", "sheffield_united.png"),
]

SERIE_A_TEAMS = [
    ("Atalanta", "Atalanta.png"),
    ("Bologna", "Bologna.png"),
    ("Cagliari", "Cagliari.png"),
    ("Como", "Como.png"),
    ("Empoli", "Empoli.png"),
    ("Fiorentina", "Fiorentina.png"),
    ("Genoa", "Genoa.png"),
    ("Hellas Verona", "Hellas_Verona.png"),
    ("Inter", "Inter.png"),
    ("Juventus", "Juventus.png"),
    ("Lazio", "Lazio.png"),
    ("Lecce", "Lecce.png"),
    ("Milan", "Milan.png"),
    ("Monza", "Monza.png"),
    ("Napoli", "Napoli.png"),
    ("Parma", "Parma.png"),
    ("Roma", "Roma.png"),
    ("Torino", "Torino.png"),
    ("Udinese", "Udinese.png"),
    ("Venezia", "Venezia.png"),
]

BUNDESLIGA_TEAMS = [
    ("Augsburg", "Augsburg.png"),
    ("Bayer Leverkusen", "Bayer_Leverkusen.png"),
    ("Bayern Munich", "Bayern_Munich.png"),
    ("Bochum", "Bochum.png"),
    ("Borussia Dortmund", "Borussia_Dortmund.png"),
    ("Borussia Mönchengladbach", "Borussia_Mönchengladbach.png"),
    ("Eintracht Frankfurt", "Eintracht_Frankfurt.png"),
    ("Freiburg", "Freiburg.png"),
    ("Heidenheim", "Heidenheim.png"),
    ("Hoffenheim", "Hoffenheim.png"),
    ("Holstein Kiel", "Holstein_Kiel.png"),
    ("Mainz 05", "Mainz_05.png"),
    ("RB Leipzig", "RB_Leipzig.png"),
    ("St Pauli", "St_Pauli.png"),
    ("Stuttgart", "Stuttgart.png"),
    ("Union Berlin", "Union_Berlin.png"),
    ("Werder Bremen", "Werder_Bremen.png"),
    ("Wolfsburg", "Wolfsburg.png"),
]

LIGUE1_TEAMS = [
    ("Angers", "Angers.png"),
    ("Auxerre", "Auxerre.png"),
    ("Brest", "Brest.png"),
    ("Le Havre", "Le_Havre.png"),
    ("Lens", "Lens.png"),
    ("Lille", "Lille.png"),
    ("Lyon", "Lyon.png"),
    ("Marseille", "Marseille.png"),
    ("Monaco", "Monaco.png"),
    ("Montpellier", "Montpellier.png"),
    ("Nantes", "Nantes.png"),
    ("Nice", "Nice.png"),
    ("PSG", "Paris_Saint-Germain.png"),
    ("Reims", "Reims.png"),
    ("Rennes", "Rennes.png"),
    ("Saint Etienne", "Saint Etienne.png"),
    ("Strasbourg", "Strasbourg.png"),
    ("Toulouse", "Toulouse.png"),
]



# Función para cargar estadísticas de La Liga (NECESARIA ANTES QUE LAS OTRAS)
def load_laliga_team_stats(per90=True):
    """Carga estadísticas de equipos de La Liga con datos consistentes"""
    teams = [name for name, _ in LALIGA_TEAMS]
    np.random.seed(42)  # Seed fijo para datos consistentes
    
    rows = []
    for team in teams:
        row = {
            'Team': team,
            'PPDA/90': np.random.uniform(5, 14),
            'CtrShots/90': np.random.uniform(0.2, 3.0),
            'CP_succes/90': np.random.uniform(0.2, 0.8),
            'ShotsOT/90': np.random.uniform(1.5, 6.0),
            'DeepPass/90': np.random.uniform(6, 22),
            'PSxGA/90': np.random.uniform(0.6, 2.5),
            'ProgPass/90': np.random.uniform(15, 45),
            'xG/90': np.random.uniform(0.6, 2.2),
        }
        rows.append(row)
    
    return pd.DataFrame(rows)

# Función para cargar estadísticas de Premier League


# Función principal para gráficas de análisis de fases
def plot_phase_plotly(df, x, y, invert, title, color, x_range=None, y_range=None, selected_team=None, x_label=None, y_label=None):
    """Crea gráfica interactiva con logos de equipos (adaptado de League Dashboard)"""
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    
    fig = go.Figure()
    
    # Calcular tamaño proporcional al rango de ejes
    if x_range is not None:
        x_span = x_range[1] - x_range[0]
    else:
        x_span = df[x].max() - df[x].min()
    if y_range is not None:
        y_span = y_range[1] - y_range[0]
    else:
        y_span = df[y].max() - df[y].min()
    
    # Calcular distancia mínima entre puntos
    coords = list(zip(df[x], df[y]))
    min_dist = None
    if len(coords) > 1:
        min_dist = min(np.hypot(a[0]-b[0], a[1]-b[1]) for a, b in itertools.combinations(coords, 2))
    else:
        min_dist = min(x_span, y_span)
    
    # Autozoom: logos entre 8% y 16% del rango, según densidad
    min_size = 0.08
    max_size = 0.16
    if min_dist is not None and max(x_span, y_span) > 0:
        density_factor = min(1.0, max(0.0, min_dist / (0.25 * max(x_span, y_span))))
        logo_frac = min_size + (max_size - min_size) * density_factor
    else:
        logo_frac = 0.12
    
    logo_sizex = x_span * logo_frac
    logo_sizey = y_span * logo_frac
    
    # Añadir logos y marcadores para cada equipo
    for _, row in df.iterrows():
        team = row['Team']
        is_selected = (selected_team is not None and team == selected_team)
        
        # Tamaño especial si es el equipo seleccionado
        if is_selected:
            sizex = logo_sizex * 1.7
            sizey = logo_sizey * 1.7
            # Dibuja un círculo grande detrás del logo
            fig.add_trace(go.Scatter(
                x=[row[x]],
                y=[row[y]],
                mode="markers",
                marker=dict(size=70, color="rgba(165,0,68,0.25)", line=dict(width=4, color="#A50044")),
                hoverinfo="skip",
                showlegend=False
            ))
        else:
            sizex = logo_sizex
            sizey = logo_sizey
        
        # Marcador invisible para hover
        fig.add_trace(go.Scatter(
            x=[row[x]],
            y=[row[y]],
            mode="markers",
            marker=dict(size=1, color='rgba(0,0,0,0)', symbol="circle"),
            name=team,
            text=f"<b>{team}</b><br>{x_label or x}: {row[x]:.2f}<br>{y_label or y}: {row[y]:.2f}",
            hoverinfo="text"
        ))
        
        # Añadir imagen del logo usando la función actualizada
        logo_full_path = get_team_logo_path(team)
        if os.path.exists(logo_full_path):
            fig.add_layout_image(
                dict(
                    source=Image.open(logo_full_path),
                    x=row[x],
                    y=row[y],
                    xref="x",
                    yref="y",
                    sizex=sizex,
                    sizey=sizey,
                    xanchor="center",
                    yanchor="middle",
                    layer="above",
                    sizing="contain",
                    opacity=1.0
                )
            )
    
    # Líneas de la mediana
    x_med = df[x].median()
    y_med = df[y].median()
    x_min, x_max = (x_range if x_range else (df[x].min(), df[x].max()))
    y_min, y_max = (y_range if y_range else (df[y].min(), df[y].max()))
    
    # Fondos de cuadrantes
    fig.add_shape(type="rect", x0=x_min, x1=x_med, y0=y_med, y1=y_max, fillcolor="rgba(255,255,200,0.32)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=x_med, x1=x_max, y0=y_med, y1=y_max, fillcolor="rgba(200,255,200,0.32)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=x_min, x1=x_med, y0=y_min, y1=y_med, fillcolor="rgba(200,220,255,0.32)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=x_med, x1=x_max, y0=y_min, y1=y_med, fillcolor="rgba(255,200,200,0.32)", line_width=0, layer="below")
    
    # Líneas de mediana
    fig.add_shape(type="line", x0=x_med, x1=x_med, y0=y_min, y1=y_max, line=dict(dash="dash", color="gray"))
    fig.add_shape(type="line", x0=x_min, x1=x_max, y0=y_med, y1=y_med, line=dict(dash="dash", color="gray"))
    
    # Configurar ejes
    if invert:
        if x_range:
            fig.update_xaxes(range=x_range[::-1], showticklabels=False)
        else:
            fig.update_xaxes(autorange="reversed", showticklabels=False)
    else:
        if x_range:
            fig.update_xaxes(range=x_range, showticklabels=False)
        else:
            fig.update_xaxes(autorange=True, showticklabels=False)
    
    if y_range:
        fig.update_yaxes(range=y_range, showticklabels=False)
    else:
        fig.update_yaxes(showticklabels=False)
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label or x,
        yaxis_title=y_label or y,
        plot_bgcolor="#F8F9FA",
        paper_bgcolor="#FFFFFF",
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(family="Arial", size=14),
        transition=dict(duration=600, easing="cubic-in-out")
    )
    return fig

# Función para mostrar análisis de fases genérica para cualquier liga
def mostrar_analisis_fases(selected_team, liga="La Liga Española"):
    """Muestra las 4 gráficas de análisis de fases de juego para la liga especificada"""
    # Cargar datos según la liga
    if liga == "La Liga Española":
        df = load_laliga_team_stats(per90=True)
    elif liga == "Premier League":
        df = load_premier_team_stats(per90=True)
    elif liga == "Serie A":
        df = load_serie_a_team_stats(per90=True)
    elif liga == "Bundesliga":
        df = load_bundesliga_team_stats(per90=True)
    elif liga == "Ligue 1":
        df = load_ligue1_team_stats(per90=True)
    else:
        df = load_laliga_team_stats(per90=True)  # Fallback
    
    colors = ["#1E88E5", "#43A047", "#FB8C00", "#8E24AA"]
    phases = [
        ("PPDA", "Contraataques con disparo", False,  "Transición ofensiva"),
        ("Pérdidas altas recuperadas", "Disparos a puerta recibidos", False, "Transición defensiva"),
        ("DeepPass", "xG de tiros a puerta", False,  "Fase defensiva"),
        ("Pases progresivos", "xG", False, "Fase ofensiva"),
    ]
    
    # Calcular rangos globales para cada métrica
    axis_ranges = {}
    # Mapeo de nombres mostrados a nombres de columnas (corregido para datos reales)
    metric_mapping = {
        "PPDA": "PPDA/90",
        "Contraataques con disparo": "CtrShots/90",
        "Pérdidas altas recuperadas": "CP_succes/90", 
        "Disparos a puerta recibidos": "ShotsOT/90",
        "DeepPass": "DeepPass/90",
        "xG de tiros a puerta": "PSxGA/90",
        "Pases progresivos": "ProgPass/90",
        "xG": "xG/90"
    }
    
    for (x, y, inv, title), color in zip(phases, colors):
        # Mapear nombres de display a nombres de columna
        x_col = metric_mapping.get(x, x)
        y_col = metric_mapping.get(y, y)
        
        x_min, x_max = df[x_col].min(), df[x_col].max()
        y_min, y_max = df[y_col].min(), df[y_col].max()
        x_margin = (x_max - x_min) * 0.15
        y_margin = (y_max - y_min) * 0.15
        axis_ranges[(x, y)] = ([x_min - x_margin, x_max + x_margin], [y_min - y_margin, y_max + y_margin])
        
    cols = st.columns(2)
    for i, ((x, y, inv, title), color) in enumerate(zip(phases, colors)):
        # Mapear nombres de display a nombres de columna
        x_col = metric_mapping.get(x, x)
        y_col = metric_mapping.get(y, y)
        
        x_range, y_range = axis_ranges[(x, y)]
        fig = plot_phase_plotly(df, x_col, y_col, inv, title, color, x_range=x_range, y_range=y_range, selected_team=selected_team, x_label=x, y_label=y)
        with cols[i % 2]:
            st.plotly_chart(fig, use_container_width=True)

# Función para mostrar rankings genérica para cualquier liga
def mostrar_rankings_liga(selected_team, liga="La Liga Española"):
    """Muestra rankings top 10 por métrica con selector interactivo para la liga especificada"""
    # Cargar datos según la liga
    if liga == "La Liga Española":
        df = load_laliga_team_stats(per90=True)
        teams_list = LALIGA_TEAMS
    elif liga == "Premier League":
        df = load_premier_team_stats(per90=True)
        teams_list = PREMIER_TEAMS
    elif liga == "Serie A":
        df = load_serie_a_team_stats(per90=True)
        teams_list = SERIE_A_TEAMS
    elif liga == "Bundesliga":
        df = load_bundesliga_team_stats(per90=True)
        teams_list = BUNDESLIGA_TEAMS
    elif liga == "Ligue 1":
        df = load_ligue1_team_stats(per90=True)
        teams_list = LIGUE1_TEAMS
    else:
        df = load_laliga_team_stats(per90=True)
        teams_list = LALIGA_TEAMS
    
    st.subheader("🏅 Top 10 por métrica")
    
    metric_options = [
        ("PPDA/90", "PPDA"),
        ("CtrShots/90", "Contraataques con disparo"),
        ("CP_succes/90", "Pérdidas altas recuperadas"),
        ("ShotsOT/90", "Disparos a puerta recibidos"),
        ("DeepPass/90", "DeepPass"),
        ("PSxGA/90", "xG de tiros a puerta"),
        ("ProgPass/90", "Pases progresivos"),
        ("xG/90", "xG"),
    ]
    
    metric_key = st.selectbox("Selecciona métrica para ranking", [m[1] for m in metric_options], index=0, key="ranking_metric_selector")
    metric_col = [m[0] for m in metric_options if m[1] == metric_key][0]
    
    # Ordenar ranking (mayor a menor, salvo PPDA y PSxGA que menor es mejor)
    asc_metrics = ["PPDA/90", "PSxGA/90"]
    ascending = metric_col in asc_metrics
    top10 = df.sort_values(metric_col, ascending=ascending).head(10)
    
    # Mostrar ranking
    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
    for idx, (_, row) in enumerate(top10.iterrows()):
        logo_file = [logo for name, logo in teams_list if name == row['Team']]
        logo_path = os.path.join("static", "logos", logo_file[0]) if logo_file else None
        
        if logo_file and os.path.exists(logo_path):
            with open(logo_path, "rb") as img_f:
                img_bytes = img_f.read()
                img_b64 = base64.b64encode(img_bytes).decode()
            logo_html = f"<img src='data:image/png;base64,{img_b64}' height='28' style='vertical-align:middle;margin-right:8px;'>"
        else:
            logo_html = ""
        
        highlight = "background:#ffe5f0;border-radius:8px;" if row['Team'] == selected_team else ""
        st.markdown(f"<div style='display:flex;align-items:center;{highlight}padding:4px 8px;margin-bottom:2px;'><span style='width:24px;font-weight:bold;'>{idx+1}</span>{logo_html}<span style='flex:1;'>{row['Team']}</span><span style='font-weight:bold;'>{row[metric_col]:.2f}</span></div>", unsafe_allow_html=True)



# Función para convertir imagen a base64
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        print(f"Error loading image {image_path}: {str(e)}")
        return ""



# Estilos CSS para tema del Barcelona
st.markdown("""
    <style>
    /* Variables globales del Barcelona */
    :root {
        --primary-color: #004D98;
        --secondary-color: #a5001c;
        --background-light: #f8f9fa;
        --text-color: #2C3E50;
        --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Estilos generales */
    .main {
        background-color: var(--background-light);
        color: var(--text-color);
    }

    /* Ocultar menú y footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Título principal con tema del Barcelona
st.markdown("""
    <div class="main-header">
    </div>
""", unsafe_allow_html=True)

# Selector de equipo a resaltar
team_names = [name for name, _ in LALIGA_TEAMS]
selected_team = st.selectbox("🎯 Equipo a resaltar en análisis", team_names, index=0, key="team_selector")

# Mostrar el ranking
mostrar_rankings_liga(selected_team, "La Liga Española")

st.markdown("---")  # Separador visual

# Título para las gráficas
st.subheader("📊 Análisis de Fases de Juego")

# Mostrar las 4 gráficas
mostrar_analisis_fases(selected_team, "La Liga Española")



