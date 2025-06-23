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

# Configuración de la página
st.set_page_config(
    page_title="ScoutVision",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Placeholder - se definirá después de las listas globales
ligas_y_equipos = {}

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

# Diccionario con nombres de ligas y sus equipos (definido después de las listas globales)
ligas_y_equipos = {
    "La Liga Española": [name for name, _ in LALIGA_TEAMS],
    "Premier League": [name for name, _ in PREMIER_TEAMS],
    "Serie A": [name for name, _ in SERIE_A_TEAMS],
    "Bundesliga": [name for name, _ in BUNDESLIGA_TEAMS],
    "Ligue 1": [name for name, _ in LIGUE1_TEAMS]
}

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
def load_premier_team_stats(per90=True):
    """Carga estadísticas de equipos de Premier League con datos consistentes"""
    teams = [name for name, _ in PREMIER_TEAMS]
    np.random.seed(43)  # Seed diferente para variabilidad entre ligas
    
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

# Función para cargar estadísticas de Serie A
def load_serie_a_team_stats(per90=True):
    """Carga estadísticas de equipos de Serie A con datos consistentes"""
    teams = [name for name, _ in SERIE_A_TEAMS]
    np.random.seed(44)  # Seed diferente para variabilidad entre ligas
    
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

# Función para cargar estadísticas de Bundesliga
def load_bundesliga_team_stats(per90=True):
    """Carga estadísticas de equipos de Bundesliga con datos consistentes"""
    teams = [name for name, _ in BUNDESLIGA_TEAMS]
    np.random.seed(45)  # Seed diferente para variabilidad entre ligas
    
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

# Función para cargar estadísticas de Ligue 1
def load_ligue1_team_stats(per90=True):
    """Carga estadísticas de equipos de Ligue 1 con datos consistentes"""
    teams = [name for name, _ in LIGUE1_TEAMS]
    np.random.seed(46)  # Seed diferente para variabilidad entre ligas
    
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

# Función para obtener logo de un equipo específico  
def get_logo_for_team(team_name):
    """Obtiene el logo de un equipo específico de cualquier liga"""
    # Buscar en todas las listas de equipos usando la nueva función
    logo_path = get_team_logo_path(team_name)
    if os.path.exists(logo_path):
        return Image.open(logo_path)
    return None

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

# Función para mostrar equipos de una liga
def mostrar_equipos(liga):
    st.markdown(f"<h2 style='text-align: center; color: #1e3c72;'>{liga}</h2>", unsafe_allow_html=True)
    
    # Mostrar el grid de equipos para todas las ligas
    mostrar_grid_equipos(liga)
    
    # Mostrar análisis completo debajo de los equipos para todas las ligas
    st.markdown("---")  # Separador visual
    
    # Obtener lista de equipos según la liga
    if liga == "La Liga":
        team_names = [name for name, _ in LALIGA_TEAMS]
        liga_key = "laliga"
    elif liga == "Premier League":
        team_names = [name for name, _ in PREMIER_TEAMS]
        liga_key = "premier"
    elif liga == "Serie A":
        team_names = [name for name, _ in SERIE_A_TEAMS]
        liga_key = "serie_a"
    elif liga == "Bundesliga":
        team_names = [name for name, _ in BUNDESLIGA_TEAMS]
        liga_key = "bundesliga"
    elif liga == "Ligue 1":
        team_names = [name for name, _ in LIGUE1_TEAMS]
        liga_key = "ligue1"
    else:
        team_names = [name for name, _ in LALIGA_TEAMS]
        liga_key = "laliga"
    
    # Selector de equipo global
    selected_team = st.selectbox("🎯 Equipo a resaltar en análisis", team_names, index=0, key=f"{liga_key}_team_selector")
    
    # Mostrar el ranking
    mostrar_rankings_liga(selected_team, liga)
    
    st.markdown("---")  # Separador visual
    
    # Título para las gráficas
    st.subheader("📊 Análisis de Fases de Juego")
    
    # Mostrar las 4 gráficas
    mostrar_analisis_fases(selected_team, liga)

# Función para mostrar el grid de equipos (extraída del código original)
def mostrar_grid_equipos(liga):
    """Muestra el grid de equipos para cualquier liga"""
    # Crear filas de 5 equipos cada una
    equipos = ligas_y_equipos[liga]
    for i in range(0, len(equipos), 5):
        cols = st.columns(5)
        for j, col in enumerate(cols):
            if i + j < len(equipos):
                equipo = equipos[i + j]
                with col:
                    st.markdown('<div class="team-card">', unsafe_allow_html=True)
                    logo_path = get_team_logo_path(equipo)
                    if os.path.exists(logo_path):
                        st.markdown(f'<img src="data:image/png;base64,{get_image_base64(logo_path)}" class="team-logo" alt="{equipo}"/>', unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="placeholder-image">Logo {equipo}</div>
                        """, unsafe_allow_html=True)
                    st.markdown(f'<div class="team-name">{equipo}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    if st.button(f"Ver {equipo}", key=f"btn_{equipo}"):
                        st.session_state.equipo_seleccionado = equipo
                        st.rerun()

# Función para convertir imagen a base64
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        print(f"Error loading image {image_path}: {str(e)}")
        return ""

# Estilos CSS personalizados
st.markdown("""
    <style>
    /* Variables de color para tema consistente */
    :root {
        --background-dark: #1E1E1E;
        --text-light: #FFFFFF;
        --text-dark: #333333;
        --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        --transition-speed: 0.3s;
        --barca-primary: #004D98;
        --barca-secondary: #A50044;
    }

    /* Estilos generales y animaciones */
    * {
        transition: all var(--transition-speed) ease;
    }

    .main-content {
        margin-top: 10px;
        padding: 15px;
        animation: fadeIn 0.5s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Tarjetas mejoradas */
    .liga-card {
        border: none;
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        background: white;
        margin: 10px 5px;
        cursor: pointer;
        transition: all var(--transition-speed) ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #f8f9fa;
    }

    .liga-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15);
        border-color: #e3f2fd;
    }

    .team-card {
        border: none;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        background: white;
        margin: 15px;
        transition: all var(--transition-speed) ease;
        box-shadow: var(--card-shadow);
    }

    .team-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
    }

    .team-logo {
        width: 120px;
        height: auto;
        margin-bottom: 10px;
    }

    .league-logo {
        max-width: 140px;
        max-height: 120px;
        width: auto;
        height: auto;
        object-fit: contain;
        filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.1));
        transition: all var(--transition-speed) ease;
    }

    .league-logo-premier {
        max-width: 168px; /* 20% más grande que 140px */
        max-height: 144px; /* 20% más grande que 120px */
        width: auto;
        height: auto;
        object-fit: contain;
        filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.1));
        transition: all var(--transition-speed) ease;
    }

    .liga-card:hover .league-logo {
        transform: scale(1.05);
        filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.15));
    }

    .liga-card:hover .league-logo-premier {
        transform: scale(1.05);
        filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.15));
    }

    .team-name {
        font-size: 1.2em;
        font-weight: bold;
        color: var(--text-dark);
        margin-top: 10px;
    }

    .centered-header {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, var(--barca-primary), var(--barca-secondary));
        color: var(--text-light);
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: var(--card-shadow);
    }

    .centered-header h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }

    .centered-header p {
        font-size: 1.2em;
        opacity: 0.9;
    }

    /* Botones mejorados */
    .stButton button {
        background: linear-gradient(135deg, var(--barca-primary), var(--barca-secondary));
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all var(--transition-speed) ease;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Navbar mejorada */
    .navbar {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    .nav-link {
        position: relative;
        overflow: hidden;
    }

    .nav-link::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background-color: white;
        transform: translateX(-100%);
        transition: transform var(--transition-speed) ease;
    }

    .nav-link:hover::after {
        transform: translateX(0);
    }
    </style>
""", unsafe_allow_html=True)

# Contenedor principal
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Inicializar variables de estado
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 'inicio'
if 'liga_seleccionada' not in st.session_state:
    st.session_state.liga_seleccionada = None
if 'equipo_seleccionado' not in st.session_state:
    st.session_state.equipo_seleccionado = None

# Sección principal con título FCBLAB
st.markdown("""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        margin-bottom: 15px;
        max-width: 600px;
    ">
        <div style="
            width: 100%;
            margin: 0;
            background: linear-gradient(135deg, #004D98, #A50044);
            border-radius: 20px;
            box-shadow: 0 8px 25px rgba(0, 77, 152, 0.3);
            padding: 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: pulse 4s ease-in-out infinite;
            "></div>
                         <h1 style="
                 font-size: 1.8em;
                 font-weight: 900;
                 color: white;
                 margin: 0;
                 letter-spacing: 2px;
                 text-shadow: 2px 4px 8px rgba(0,0,0,0.3);
                 font-family: 'Arial Black', Arial, sans-serif;
                 position: relative;
                 z-index: 2;
             ">FCBLAB</h1>
             <p style="
                 font-size: 0.9em;
                 color: rgba(255,255,255,0.9);
                 margin: 10px 0 15px 0;
                 font-weight: 300;
                 letter-spacing: 1px;
                 position: relative;
                 z-index: 2;
                          ">Laboratorio de Análisis del FC Barcelona</p>
         </div>
     </div>
""", unsafe_allow_html=True)

# Logo del Barça centrado debajo del título
st.markdown("""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        margin: -10px auto 20px auto;
        max-width: 400px;
    ">
        <div style="
            background: white;
            border-radius: 50%;
            padding: 18px;
            box-shadow: 0 8px 25px rgba(0, 77, 152, 0.2);
            border: 3px solid rgba(255,255,255,0.9);
        ">
""", unsafe_allow_html=True)

barca_logo = get_team_logo_path("Barcelona")
if os.path.exists(barca_logo):
    st.markdown(f"""
        <img 
            src="data:image/png;base64,{get_image_base64(barca_logo)}" 
            alt="FC Barcelona"
            style="
                width: 120px;
                height: auto;
                display: block;
                margin: 0 auto;
            "
        />
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="
            width: 120px;
            height: 120px;
            background: #f0f0f0;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-weight: bold;
        ">Logo FC Barcelona</div>
    """, unsafe_allow_html=True)

st.markdown("""
        </div>
     </div>
    
    <style>
    @keyframes pulse {
        0% { transform: rotate(0deg) scale(1); opacity: 0.3; }
        50% { transform: rotate(180deg) scale(1.1); opacity: 0.1; }
        100% { transform: rotate(360deg) scale(1); opacity: 0.3; }
    }
    </style>
""", unsafe_allow_html=True)

# Botones principales con espaciado reducido
st.markdown('<div style="margin-top: 10px; margin-bottom: 10px;">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1,2,2,1])
with col2:
    if st.button("Analisis Propio", key="barca_analysis", use_container_width=True):
        st.switch_page("pages/Analisis Propio.py")
with col3:
    if st.button("Barça VS Bayern", key="barca_bayern", use_container_width=True):
        st.switch_page("pages/Barça VS Bayern.py")
st.markdown('</div>', unsafe_allow_html=True)

# Separador visual
st.markdown("<hr style='margin: 20px 0; opacity: 0.2;'>", unsafe_allow_html=True)

# Si estamos en la página de inicio, mostrar el contenido normal
if st.session_state.pagina_actual == 'inicio':
    st.markdown("""
        <div style="text-align: center; margin: 20px 0 15px 0;">
            <h2 style="
                font-size: 2.2em;
                font-weight: 700;
                color: #2c3e50;
                margin-bottom: 5px;
                letter-spacing: 1px;
            ">🌍 Selecciona una Liga</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Mostrar las ligas en una cuadrícula con mejor espaciado
    ligas_lista = list(ligas_y_equipos.keys())
    cols = st.columns(len(ligas_lista), gap="medium")
    
    for i, liga_nombre in enumerate(ligas_lista):
        with cols[i]:
            logo_path = get_league_logo_path(liga_nombre)
            if os.path.exists(logo_path):
                # Tamaño especial para Premier League (20% más grande)
                if liga_nombre == "Premier League":
                    logo_class = "league-logo-premier"
                else:
                    logo_class = "league-logo"
                
                # Estructura HTML mejorada para que el logo aparezca DENTRO de la tarjeta
                st.markdown(f'''
                    <div class="liga-card">
                        <img src="data:image/png;base64,{get_image_base64(logo_path)}" class="{logo_class}" alt="{liga_nombre}"/>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                    <div class="liga-card">
                        <div class="placeholder-image">Logo {liga_nombre}</div>
                    </div>
                ''', unsafe_allow_html=True)
            
            if st.button(f"Ver {liga_nombre}", key=f"btn_{liga_nombre}"):
                st.session_state.liga_seleccionada = liga_nombre
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar el div de la cuadrícula

    # Si hay una liga seleccionada, mostrar sus equipos
    if st.session_state.liga_seleccionada:
        mostrar_equipos(st.session_state.liga_seleccionada)

   
# Cerrar el contenedor principal
st.markdown('</div>', unsafe_allow_html=True)



