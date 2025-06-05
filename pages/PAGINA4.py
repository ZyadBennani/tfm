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
        .main {
            background-color: #0F172A;
            color: #E2E8F0;
        }
        .stSidebar {
            background-color: #1E293B;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            padding: 0.5rem;
            border-radius: 1rem;
            background-color: #1E293B;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 10px 20px;
            border-radius: 0.5rem;
            background-color: transparent;
            color: #E2E8F0;
            font-weight: 500;
        }
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: #3B82F6;
            color: white;
        }
        .player-card {
            background-color: #1E293B;
            padding: 1rem;
            border-radius: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin: 0.5rem;
        }
        .metric-badge {
            background-color: #3B82F6;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        .breadcrumb {
            padding: 0.5rem 0;
            color: #94A3B8;
            font-size: 0.875rem;
        }
        .shortlist-counter {
            background-color: #EF4444;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# Breadcrumb y contador de shortlist
col1, col2 = st.columns([6,1])
with col1:
    st.markdown('<div class="breadcrumb">Home > Player Search</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div style="text-align: right">📋 <span class="shortlist-counter">0</span></div>', unsafe_allow_html=True)

# Sidebar con filtros
with st.sidebar:
    st.markdown("### Quick Filters")
    
    # Posición
    position = st.selectbox(
        "Position",
        ["All", "GK", "CB", "FB", "DM", "CM", "AM", "WG", "ST"],
        index=0
    )
    
    # Perfil/Rol
    roles = st.multiselect(
        "Player Role",
        ["Ball Playing CB", "Box-to-Box", "Deep-Lying Playmaker", "Target Man", "Inverted Winger", "Sweeper Keeper"]
    )
    
    # Edad
    age_range = st.slider("Age Range", 15, 40, (18, 35))
    
    # Pie dominante
    foot = st.radio("Preferred Foot", ["Both", "Left", "Right"])
    
    # País
    nationality = st.text_input("Nationality")
    
    # Contrato
    contract_dates = st.date_input(
        "Contract End Date Range",
        (datetime.now(), datetime(2025, 12, 31))
    )
    
    # Valor de mercado
    market_value = st.slider("Market Value (M€)", 0, 100, (0, 50))
    
    # Salario
    salary = st.slider("Salary (K€/week)", 0, 500, (0, 100))
    
    # Equipo
    team = st.text_input("Current Team")
    
    # Filtros avanzados
    with st.expander("Advanced Filters"):
        metrics_90 = st.multiselect(
            "Metrics per 90",
            ["xG", "xA", "Passes Completed", "Tackles", "Interceptions", "Distance Covered"]
        )
        
        percentile = st.checkbox("Show only ≥ 70th percentile")
        
        injury_risk = st.slider("Injury Risk", 0, 100, 50)
        
        adjusted_value = st.number_input("Adjusted Market Value (M€)", min_value=0.0)
    
    # Botones de acción
    col1, col2 = st.columns(2)
    with col1:
        st.button("Apply Filters", type="primary")
    with col2:
        st.button("Reset")

# Panel principal
tab1, tab2, tab3 = st.tabs(["Table View", "Card View", "Heatmap View"])

with tab1:
    # Tabla de resultados (placeholder)
    st.dataframe(pd.DataFrame({
        'Name': ['Player 1', 'Player 2', 'Player 3'],
        'Age': [23, 25, 21],
        'Position': ['CM', 'ST', 'CB'],
        'Value (M€)': [15, 45, 8],
        'Rating': [7.8, 8.2, 7.5]
    }))

with tab2:
    # Vista de tarjetas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="player-card">
                <h3>Player 1</h3>
                <p>CM | 23 years</p>
                <div class="metric-badge">Rating: 7.8</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="player-card">
                <h3>Player 2</h3>
                <p>ST | 25 years</p>
                <div class="metric-badge">Rating: 8.2</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="player-card">
                <h3>Player 3</h3>
                <p>CB | 21 years</p>
                <div class="metric-badge">Rating: 7.5</div>
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