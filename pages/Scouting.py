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
    
    # Posición
    st.markdown('<p class="filter-title">Puesto</p>', unsafe_allow_html=True)
    position = st.selectbox(
        label="Select Position",
        options=["All", "GK", "CB", "RB", "LB", "CM-CDM", "CAM", "RW", "LW", "ST"],
        index=0,
        key="position_select",
        label_visibility="collapsed"  # Ocultar el label ya que tenemos el título arriba
    )
    
    # Perfil/Rol
    st.markdown('<p class="filter-title">Perfiles</p>', unsafe_allow_html=True)
    available_profiles = position_profiles.get(position, ["All Profiles"])
    roles = st.selectbox(
        label="Select Profile",
        options=available_profiles,
        index=0,
        key="profile_select",
        label_visibility="collapsed"  # Ocultar el label ya que tenemos el título arriba
    )
    
    # Edad
    st.markdown('<p class="filter-title">Rango de Edad</p>', unsafe_allow_html=True)
    age_range = st.slider("", 15, 40, (18, 35))
    
    # Pie dominante
    st.markdown('<p class="filter-title">Pie Dominante</p>', unsafe_allow_html=True)
    foot = st.radio("", ["Both", "Left", "Right"])
    
    # País
    st.markdown('<p class="filter-title">Nacionalidad</p>', unsafe_allow_html=True)
    nationality = st.text_input("")
    
    # Contrato
    st.markdown('<p class="filter-title">Fin de Contrato</p>', unsafe_allow_html=True)
    contract_dates = st.date_input(
        "",
        (datetime.now(), datetime(2025, 12, 31))
    )
    
    # Valor de mercado
    st.markdown('<p class="filter-title">Valor de Mercado (M€)</p>', unsafe_allow_html=True)
    market_value = st.slider("", 0, 100, (0, 50))
    
    # Salario
    st.markdown('<p class="filter-title">Salario (K€/semana)</p>', unsafe_allow_html=True)
    salary = st.slider("", 0, 500, (0, 100))
    
    # Equipo
    st.markdown('<p class="filter-title">Equipo Actual</p>', unsafe_allow_html=True)
    team = st.text_input("", key="team_input")
    
    # Filtros avanzados
    with st.expander("Advanced Filters"):
        st.markdown('<p class="filter-title">Métricas por 90 min</p>', unsafe_allow_html=True)
        metrics_90 = st.multiselect(
            "",
            ["xG", "xA", "Passes Completed", "Tackles", "Interceptions", "Distance Covered"]
        )
        
        st.markdown('<p class="filter-title">Percentil</p>', unsafe_allow_html=True)
        percentile = st.checkbox("Mostrar solo ≥ 70th percentil")
        
        st.markdown('<p class="filter-title">Riesgo de Lesión</p>', unsafe_allow_html=True)
        injury_risk = st.slider("", 0, 100, 50)
        
        st.markdown('<p class="filter-title">Valor de Mercado Ajustado (M€)</p>', unsafe_allow_html=True)
        adjusted_value = st.number_input("", min_value=0.0)

    # Botones de acción
    col1, col2 = st.columns(2)
    with col1:
        st.button("Apply Filters", type="primary")
    with col2:
        st.button("Reset")

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
        'Name': ['Player 1', 'Player 2', 'Player 3'],
        'Age': [23, 25, 21],
        'Position': ['CM', 'ST', 'CB'],
        'Value (M€)': [15, 45, 8],
        'Rating': [7.8, 8.2, 7.5],
        'Nationality': ['🇪🇸 ESP', '🇫🇷 FRA', '🇩🇪 GER'],
        'Club': ['Barcelona', 'PSG', 'Bayern Munich']
    })
    
    st.dataframe(
        df,
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