import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
import io
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap

# Configuración de la página
st.set_page_config(
    page_title="Player Scouting",
    page_icon="🔍",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
        /* Estilos generales */
        .main {
            background-color: #f8f9fa;
            color: #1a1a1a;
            padding: 1rem;
        }
        
        /* Sidebar mejorada */
        .stSidebar {
            background-color: white;
            padding: 2rem 1rem;
        }
        
        /* Títulos y texto */
        h1, h2, h3 {
            color: #1a1a1a;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        /* Tabs mejorados */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            padding: 1rem;
            border-radius: 1rem;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 10px 25px;
            border-radius: 0.5rem;
            background-color: transparent;
            color: #1a1a1a;
            font-weight: 500;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #f0f0f0;
        }
        
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: #004D98;
            color: white;
            transform: scale(1.05);
        }
        
        /* Tarjetas de jugadores mejoradas */
        .player-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
            border: 1px solid #E5E7EB;
            transition: all 0.3s ease;
        }
        
        .player-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
        }
        
        .player-card h3 {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            color: #004D98;
        }
        
        .player-card p {
            font-size: 1.1rem;
            color: #4a5568;
            margin-bottom: 1rem;
        }
        
        /* Badges y métricas */
        .metric-badge {
            background-color: #A50044;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-size: 1rem;
            font-weight: 600;
            display: inline-block;
            margin-top: 0.5rem;
        }
        
        /* Navegación y breadcrumbs */
        .breadcrumb {
            padding: 1rem 0;
            color: #4a5568;
            font-size: 1rem;
            margin-bottom: 1rem;
        }
        
        .shortlist-counter {
            background-color: #A50044;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-size: 1rem;
            font-weight: 600;
        }
        
        /* Filtros y controles */
        .filter-title {
            margin: 1rem 0 0.5rem 0;
            font-weight: 600;
            color: #1a1a1a;
            font-size: 1.1rem;
        }
        
        /* Botones mejorados */
        .stButton button {
            width: 100%;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Tabla mejorada */
        .stDataFrame {
            font-size: 1rem;
        }
        
        .stDataFrame td, .stDataFrame th {
            padding: 1rem !important;
        }
        
        /* Selectores y inputs */
        .stSelectbox, .stMultiSelect {
            margin-bottom: 1rem;
        }
        
        .stSelectbox > div > div, .stMultiSelect > div > div {
            padding: 0.5rem;
            font-size: 1rem;
        }
        
        /* Sliders mejorados */
        .stSlider {
            padding: 1rem 0;
        }
        
        /* Expander mejorado */
        .streamlit-expanderHeader {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a1a1a;
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
        }
        
        /* Estilos mejorados para selectbox */
        .stSelectbox [data-baseweb="select"] {
            background-color: white;
            padding: 0.5rem;
            border-radius: 0.5rem;
            border: 1px solid #E5E7EB;
        }
        
        .stSelectbox [data-baseweb="select"] > div {
            font-size: 1rem;
            color: #1a1a1a;
            font-weight: 500;
        }
        
        /* Asegurar que el texto del selectbox sea visible */
        div[data-baseweb="select"] > div:first-child {
            color: #1a1a1a !important;
            opacity: 1 !important;
        }
        
        /* Forzar visibilidad del texto en selectbox */
        div[data-baseweb="select"] span {
            color: #000000 !important;
            opacity: 1 !important;
        }
        
        div[data-baseweb="select"] div[data-testid="stMarkdown"] {
            color: #000000 !important;
            opacity: 1 !important;
        }
        
        .stSelectbox div[role="listbox"] div {
            color: #000000 !important;
        }
        
        .stSelectbox div[data-baseweb="select"] div {
            color: #000000 !important;
        }
        
        /* Estilo específico para el texto seleccionado */
        div[data-baseweb="select"] [data-testid="stMarkdown"] p {
            color: #000000 !important;
            font-weight: 500 !important;
        }
        
        /* Asegurar contraste */
        .stSelectbox {
            background-color: #ffffff;
        }
        
        .stSelectbox > div > div {
            background-color: white !important;
            color: #000000 !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 0.5rem !important;
            padding: 0.5rem !important;
        }
        
        /* Estilo para el texto dentro del selectbox */
        .stSelectbox > div > div > div {
            color: #000000 !important;
            font-weight: 500 !important;
        }
        
        /* Estilo para las opciones del dropdown */
        div[data-baseweb="select"] ul {
            background-color: white !important;
        }
        
        div[data-baseweb="select"] ul li {
            color: #000000 !important;
        }
        
        /* Eliminar cualquier texto transparente */
        div[data-baseweb="select"] * {
            color: #000000 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Título principal y descripción
st.title("⚽ Player Scouting")
st.markdown("""
    <div style='background-color: white; padding: 1.5rem; border-radius: 1rem; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
        <h4 style='color: #1a1a1a; margin-bottom: 0.5rem;'>Búsqueda Avanzada de Jugadores</h4>
        <p style='color: #4a5568;'>Utiliza los filtros para encontrar jugadores que se ajusten a tus criterios de búsqueda. Puedes comparar jugadores y añadirlos a tu shortlist.</p>
    </div>
""", unsafe_allow_html=True)

# Breadcrumb y contador de shortlist con mejor diseño
col1, col2 = st.columns([6,1])
with col1:
    st.markdown("""
        <div class="breadcrumb" style='background-color: white; padding: 1rem; border-radius: 0.5rem;'>
            <span style='color: #004D98;'>Home</span> > 
            <span style='font-weight: 600;'>Player Search</span>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div style='text-align: right; background-color: white; padding: 1rem; border-radius: 0.5rem;'>
            <span style='font-size: 1.2rem;'>📋</span> 
            <span class="shortlist-counter">0</span>
        </div>
    """, unsafe_allow_html=True)

# Diccionario de perfiles por posición
position_profiles = {
    "GK": ["Sweeper", "Line Keeper", "Traditional"],
    "CB": ["Ball Playing", "Stopper", "Sweeper"],
    "RB": ["Defensive", "Progressive", "Offensive"],
    "LB": ["Defensive", "Progressive", "Offensive"],
    "CM-CDM": ["Deep Lying", "Box-to-Box", "Holding"],
    "CAM": ["Advanced Playmaker", "Shadow Striker", "Dribbling Creator"],
    "RW": ["Wide Playmaker", "Direct Winger", "Hybrid"],
    "LW": ["Wide Playmaker", "Direct Winger", "Hybrid"],
    "ST": ["Target Man", "Poacher", "Playmaker"],
    "All": ["All Profiles"]  # Opción por defecto
}

# Sidebar con filtros
with st.sidebar:
    st.markdown("### Quick Filters")
    
    # Valores por defecto
    default_filters = {
        "position_select": "All",
        "profile_select": "All Profiles",
        "age_range": (18, 35),
        "foot": "Both",
        "nationality": "",
        "contract_dates": (datetime.now(), datetime(2025, 12, 31)),
        "market_value": (0, 50),
        "salary_m": (0.0, 5.0),
        "metrics_90": [],
        "percentile": False,
        "height_range": (160, 200),
        "has_clause": "Ambos",
    }

    # --- SOLUCIÓN RESET ---
    if st.session_state.get("reset_filters", False):
        for k, v in default_filters.items():
            st.session_state[k] = v
        st.session_state["reset_filters"] = False
        st.rerun()

    # Inicializar filtros si no existen
    for k, v in default_filters.items():
        if k not in st.session_state:
            st.session_state[k] = v
    
    # Posición
    st.markdown('<p class="filter-title">Puesto</p>', unsafe_allow_html=True)
    position = st.selectbox(
        label="Select Position",
        options=["All", "GK", "CB", "RB", "LB", "CM-CDM", "CAM", "RW", "LW", "ST"],
        index=0,
        key="position_select",
        label_visibility="collapsed"
    )
    
    # Perfil/Rol
    st.markdown('<p class="filter-title">Perfiles</p>', unsafe_allow_html=True)
    available_profiles = position_profiles.get(position, ["All Profiles"])
    roles = st.selectbox(
        label="Select Profile",
        options=available_profiles,
        index=0,
        key="profile_select",
        label_visibility="collapsed"
    )
    
    # Edad
    st.markdown('<p class="filter-title">Edad</p>', unsafe_allow_html=True)
    age_range = st.slider("", 15, 40, st.session_state.age_range, key="age_range")
    
    # Altura
    st.markdown('<p class="filter-title">Altura (cm)</p>', unsafe_allow_html=True)
    height_range = st.slider("", 140, 210, st.session_state.height_range, key="height_range")
    
    # Pie dominante
    st.markdown('<p class="filter-title">Pie Dominante</p>', unsafe_allow_html=True)
    foot = st.radio("", ["Both", "Left", "Right"], index=["Both", "Left", "Right"].index(st.session_state.foot), key="foot")
    
    # País
    st.markdown('<p class="filter-title">Nacionalidad</p>', unsafe_allow_html=True)
    nationality = st.text_input("", value=st.session_state.nationality, key="nationality")
    
    # Contrato
    st.markdown('<p class="filter-title">Fin de Contrato</p>', unsafe_allow_html=True)
    contract_dates = st.date_input(
        "",
        st.session_state.contract_dates,
        key="contract_dates"
    )
    
    # Valor de mercado
    st.markdown('<p class="filter-title">Valor de Mercado (M€)</p>', unsafe_allow_html=True)
    market_value = st.slider("", 0, 200, st.session_state.market_value, key="market_value")
    
    # Salario
    st.markdown('<p class="filter-title">Salario bruto anual máximo</p>', unsafe_allow_html=True)
    def format_salary(val):
        if val < 1_000_000:
            return f"{val//1000}K€"
        else:
            if val % 1_000_000 == 0:
                return f"{val//1_000_000}M€"
            else:
                return f"{val/1_000_000:.1f}M€".replace('.0','')
    
    # Mostrar el valor formateado arriba del slider
    max_salary_k = st.slider(
        f"Salario máximo seleccionado: {format_salary(1000*st.session_state.get('max_salary_k', 5000))}",
        min_value=100,
        max_value=100_000,
        value=5_000,
        step=50,
        format="%dK€",
        key="max_salary_k",
        label_visibility="visible"
    )
    max_salary = max_salary_k * 1000

    # Filtro de cláusula
    st.markdown('<p class="filter-title">¿Tiene cláusula?</p>', unsafe_allow_html=True)
    has_clause = st.radio(
        "",
        ["Sí", "No"],
        index=0,
        key="has_clause"
    )
    
    # Filtros avanzados
    with st.expander("Advanced Filters"):
        st.markdown('<p class="filter-title">Métricas por 90 min</p>', unsafe_allow_html=True)
        metrics_90 = st.multiselect(
            "",
            ["xG", "xA", "Passes Completed", "Tackles", "Interceptions", "Distance Covered"],
            default=st.session_state.metrics_90,
            key="metrics_90"
        )
        st.markdown('<p class="filter-title">Percentil</p>', unsafe_allow_html=True)
        percentile = st.checkbox("Mostrar solo ≥ 70th percentil", value=st.session_state.percentile, key="percentile")

    # Botones de acción
    col1, col2 = st.columns(2)
    with col1:
        st.button("Apply Filters", type="primary")
    with col2:
        if st.button("Reset"):
            st.session_state["reset_filters"] = True
            st.rerun()

# Panel principal
tab1, tab2, tab3 = st.tabs(["Table View", "Card View", "Heatmap View"])

with tab1:
    st.markdown("""
        <div style='background-color: white; padding: 1.5rem; border-radius: 1rem; margin-bottom: 1rem;'>
            <h3 style='margin-bottom: 1rem;'>Resultados de la Búsqueda</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabla de resultados mejorada
    df = pd.DataFrame({
        'Name': ['Player 1', 'Player 2', 'Player 3', 'Player 4', 'Player 5', 'Player 6', 'Player 7', 'Player 8', 'Player 9', 'Player 10', 'Player 11', 'Player 12'],
        'Age': [23, 25, 21, 28, 24, 27, 22, 29, 26, 20, 30, 19],
        'Position': ['CM', 'ST', 'CB', 'RW', 'LW', 'GK', 'CB', 'CM', 'ST', 'LB', 'RB', 'CAM'],
        'Profile': ['Box-to-Box', 'Poacher', 'Stopper', 'Direct Winger', 'Wide Playmaker', 'Sweeper', 'Ball Playing', 'Deep Lying', 'Target Man', 'Defensive', 'Progressive', 'Advanced Playmaker'],
        'Value (M€)': [15, 45, 8, 22, 18, 5, 12, 30, 25, 10, 9, 16],
        'Rating': [7.8, 8.2, 7.5, 7.9, 8.0, 7.2, 7.7, 8.1, 7.6, 7.3, 7.4, 8.0],
        'xG': [0.25, 0.45, 0.10, 0.30, 0.28, 0.05, 0.12, 0.33, 0.40, 0.08, 0.09, 0.29],
        'xA': [0.18, 0.22, 0.05, 0.27, 0.19, 0.03, 0.07, 0.25, 0.21, 0.06, 0.08, 0.24],
        'Passes Completed': [65, 40, 55, 70, 68, 30, 60, 75, 50, 45, 48, 72],
        'Tackles': [2, 1, 4, 3, 2, 0, 5, 2, 1, 6, 7, 2],
        'Interceptions': [1, 0, 3, 2, 1, 0, 4, 1, 0, 5, 6, 1],
        'Distance Covered': [10.2, 9.8, 10.5, 11.0, 10.7, 9.0, 10.1, 11.2, 10.3, 9.5, 9.7, 11.1],
        'Nationality': ['🇪🇸 ESP', '🇫🇷 FRA', '🇩🇪 GER', '🇮🇹 ITA', '🇧🇷 BRA', '🇵🇹 POR', '🇳🇱 NED', '🇦🇷 ARG', '🇧🇪 BEL', '🇬🇧 ENG', '🇺🇾 URU', '🇭🇷 CRO'],
        'Club': ['Barcelona', 'PSG', 'Bayern Munich', 'Juventus', 'Real Madrid', 'Chelsea', 'Liverpool', 'Atletico', 'Sevilla', 'Valencia', 'Betis', 'Milan'],
        'Contract End': [2026, 2025, 2027, 2024, 2026, 2025, 2027, 2024, 2026, 2025, 2027, 2024],
        'Market Value': [15, 45, 8, 22, 18, 5, 12, 30, 25, 10, 9, 16],
        'Salary': [2_000_000, 8_000_000, 1_200_000, 3_500_000, 2_800_000, 900_000, 1_500_000, 4_000_000, 2_200_000, 1_000_000, 1_100_000, 2_600_000],
        'Height': [180, 185, 190, 175, 178, 192, 188, 181, 183, 177, 179, 176],
        'Foot': ['Right', 'Left', 'Right', 'Right', 'Left', 'Right', 'Left', 'Right', 'Right', 'Left', 'Right', 'Left'],
        'Has Clause': ['Sí', 'No', 'Sí', 'No', 'Sí', 'No', 'Sí', 'No', 'Sí', 'No', 'Sí', 'No'],
    })

    # --- FILTRADO POR TODOS LOS FILTROS ---
    filtered_df = df.copy()
    # Posición
    if position != "All":
        filtered_df = filtered_df[filtered_df["Position"] == position]
    # Perfil
    if roles != "All Profiles":
        filtered_df = filtered_df[filtered_df["Profile"] == roles]
    # Edad
    filtered_df = filtered_df[(filtered_df["Age"] >= age_range[0]) & (filtered_df["Age"] <= age_range[1])]
    # Altura
    filtered_df = filtered_df[(filtered_df["Height"] >= height_range[0]) & (filtered_df["Height"] <= height_range[1])]
    # Pie dominante
    if foot != "Both":
        filtered_df = filtered_df[filtered_df["Foot"] == foot]
    # Nacionalidad
    if nationality:
        filtered_df = filtered_df[filtered_df["Nationality"].str.contains(nationality, case=False)]
    # Contrato
    # (Ejemplo: solo filtra por año de fin de contrato)
    filtered_df = filtered_df[(filtered_df["Contract End"] >= contract_dates[0].year) & (filtered_df["Contract End"] <= contract_dates[1].year)]
    # Valor de mercado
    filtered_df = filtered_df[(filtered_df["Market Value"] >= market_value[0]) & (filtered_df["Market Value"] <= market_value[1])]
    # Salario
    filtered_df = filtered_df[filtered_df["Salary"] <= max_salary]
    # Cláusula
    if has_clause == "Sí":
        filtered_df = filtered_df[filtered_df["Has Clause"] == "Sí"]
    elif has_clause == "No":
        filtered_df = filtered_df[filtered_df["Has Clause"] == "No"]

    # --- LÓGICA DE FILTRO POR MÉTRICAS (mantener al final) ---
    if metrics_90:
        top_sets = []
        for metric in metrics_90:
            if metric in filtered_df.columns:
                top_players = filtered_df.nlargest(10, metric)["Name"].tolist()
                top_sets.append(set(top_players))
        if top_sets:
            top_intersection = set.intersection(*top_sets)
            if top_intersection:
                filtered_df = filtered_df[filtered_df["Name"].isin(top_intersection)]
                cols_to_show = ["Name", "Position", "Club", "Rating"] + metrics_90
                st.dataframe(
                    filtered_df[cols_to_show].sort_values(by="Rating", ascending=False),
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No hay jugadores que estén en el top 10 de todas las métricas seleccionadas. Prueba con otras combinaciones o menos métricas.")
        else:
            st.info("No hay métricas válidas seleccionadas.")
    else:
        st.dataframe(
            filtered_df,
            column_config={
                "Name": st.column_config.TextColumn(
                    "Player Name",
                    width="medium",
                    help="Full name of the player"
                ),
                "Rating": st.column_config.ProgressColumn(
                    "Rating",
                    format="%.1f",
                    min_value=0,
                    max_value=10,
                ),
                "Value (M€)": st.column_config.NumberColumn(
                    "Market Value",
                    format="€%.1fM",
                ),
            },
            hide_index=True,
            use_container_width=True
        )

with tab2:
    st.markdown("<h3 style='margin-bottom: 1.5rem;'>Player Cards</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="player-card">
                <img src="https://via.placeholder.com/150" style="width: 100%; border-radius: 0.5rem; margin-bottom: 1rem;">
                <h3>Player 1</h3>
                <p>🎯 CM | 👤 23 years</p>
                <p>🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | ⚽ Barcelona</p>
                <div class="metric-badge">Rating: 7.8</div>
                <div style="margin-top: 1rem;">
                    <button style="background-color: #004D98; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; width: 100%; cursor: pointer;">
                        View Profile
                    </button>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="player-card">
                <img src="https://via.placeholder.com/150" style="width: 100%; border-radius: 0.5rem; margin-bottom: 1rem;">
                <h3>Player 2</h3>
                <p>⚔️ ST | 👤 25 years</p>
                <p>🇫🇷 France | ⚽ PSG</p>
                <div class="metric-badge">Rating: 8.2</div>
                <div style="margin-top: 1rem;">
                    <button style="background-color: #004D98; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; width: 100%; cursor: pointer;">
                        View Profile
                    </button>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="player-card">
                <img src="https://via.placeholder.com/150" style="width: 100%; border-radius: 0.5rem; margin-bottom: 1rem;">
                <h3>Player 3</h3>
                <p>🛡️ CB | 👤 21 years</p>
                <p>🇩🇪 Germany | ⚽ Bayern Munich</p>
                <div class="metric-badge">Rating: 7.5</div>
                <div style="margin-top: 1rem;">
                    <button style="background-color: #004D98; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; width: 100%; cursor: pointer;">
                        View Profile
                    </button>
                </div>
            </div>
        """, unsafe_allow_html=True)

with tab3:
    # Vista de mapa de calor (placeholder)
    st.markdown("### Player Heatmap")
    st.info("Select a player to view their heatmap")

# Función helper para crear el campo de fútbol (se usará para heatmaps)
def create_football_pitch():
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Configuración del campo
    ax.set_facecolor('#1E293B')
    fig.patch.set_facecolor('#0F172A')
    
    # Dibujar las líneas del campo
    ax.plot([0, 0, 100, 100, 0], [0, 100, 100, 0, 0], color='white', lw=2)
    ax.plot([50, 50], [0, 100], color='white', lw=2)
    
    # Círculo central
    circle = plt.Circle((50, 50), 9.15, fill=False, color='white', lw=2)
    ax.add_patch(circle)
    
    # Áreas
    ax.plot([0, 16.5, 16.5, 0], [20, 20, 80, 80], color='white', lw=2)
    ax.plot([100, 83.5, 83.5, 100], [20, 20, 80, 80], color='white', lw=2)
    
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.axis('off')
    
    return fig, ax

# Placeholder para el comparador de jugadores
if st.button("Compare Selected Players"):
    st.markdown("### Player Comparison")
    col1, col2 = st.columns(2)
    
    with col1:
        # Radar chart placeholder
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[80, 70, 85, 75, 90],
            theta=['Pace', 'Shooting', 'Passing', 'Dribbling', 'Physical'],
            fill='toself',
            name='Player 1'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            paper_bgcolor='#1E293B',
            plot_bgcolor='#1E293B',
            font=dict(color='#E2E8F0')
        )
        st.plotly_chart(fig)
    
    with col2:
        # Tabla comparativa placeholder
        st.dataframe(pd.DataFrame({
            'Metric': ['Goals', 'Assists', 'Pass %', 'Tackles'],
            'Player 1': [15, 8, 87, 45],
            'Player 2': [12, 12, 92, 32]
        }))

# Botón de exportar informe
st.download_button(
    label="Export Report (PDF)",
    data=b"Placeholder PDF data",
    file_name="scouting_report.pdf",
    mime="application/pdf"
) 