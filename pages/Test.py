import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="Test - Análisis Avanzado",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS
st.markdown("""
    <style>
        /* Variables globales */
        :root {
            --primary-blue: #004D98;
            --primary-red: #A50044;
            --background-light: #f8f9fa;
            --text-color: #2C3E50;
            --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Contenedores principales */
        .phase-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: var(--card-shadow);
            margin: 1rem 0;
        }

        /* Métricas */
        .metric-container {
            background: var(--background-light);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            transition: transform 0.2s;
        }
        
        .metric-container:hover {
            transform: translateY(-5px);
        }

        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-blue);
        }

        .metric-label {
            font-size: 1rem;
            color: var(--text-color);
        }

        /* Insights */
        .insight-box {
            background: linear-gradient(135deg, var(--primary-blue), var(--primary-red));
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
            margin-bottom: 2rem;
        }

        .stTabs [data-baseweb="tab"] {
            height: 60px;
            padding: 15px 30px;
            background-color: var(--background-light);
            border: none;
            color: var(--text-color);
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            border-radius: 8px;
        }

        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: var(--primary-blue);
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Título
st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h1 style='color: var(--primary-blue);'>Análisis Avanzado FC Barcelona</h1>
        <p style='color: var(--text-color); font-size: 1.2rem;'>
            Análisis detallado por fases del juego con métricas avanzadas
        </p>
    </div>
""", unsafe_allow_html=True)

# Generar datos de ejemplo
@st.cache_data
def generate_sample_data():
    # Datos para fase ofensiva
    offensive_data = pd.DataFrame({
        'match_id': range(1, 39),
        'xG': np.random.normal(2.1, 0.5, 38),
        'goals': np.random.poisson(2, 38),
        'positional_attacks': np.random.poisson(45, 38),
        'shots': np.random.poisson(15, 38),
        'area_entries': np.random.poisson(30, 38),
        'final_third_passes': np.random.poisson(100, 38),
        'progressive_passes': np.random.poisson(50, 38),
        'deep_completed_passes': np.random.poisson(25, 38),
        'avg_passes_possession': np.random.normal(8, 2, 38)
    })
    
    return offensive_data

offensive_data = generate_sample_data()

# Crear pestañas para cada fase
tabs = st.tabs([
    "⚔️ Fase Ofensiva",
    "⚡ Transición Ofensiva",
    "🛡️ Fase Defensiva",
    "🔄 Transición Defensiva",
    "⚽ Balón Parado"
])

# 1. Fase Ofensiva
with tabs[0]:
    st.markdown("""
        <div class="phase-container">
            <h2>Fase Ofensiva</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Métricas clave - Añadidas más métricas relevantes
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">2.1</div>
                <div class="metric-label">xG por partido</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">85%</div>
                <div class="metric-label">Precisión de pases</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">28.5</div>
                <div class="metric-label">Entradas al área</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">8.2</div>
                <div class="metric-label">Pases progresivos</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">65%</div>
                <div class="metric-label">Duelos ofensivos ganados</div>
            </div>
        """, unsafe_allow_html=True)

    # Visualizaciones
    st.markdown("### Análisis Detallado")
    
    # Filtros en la parte superior
    col1, col2 = st.columns(2)
    with col1:
        pass_type = st.selectbox(
            "Tipo de Pase",
            ["Todos", "Forward", "Back", "Lateral", "Long", "Progressive", "Smart"]
        )
    with col2:
        possession_filter = st.slider(
            "Filtrar por % posesión mínimo",
            0, 100, 30
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Scatter plot mejorado de xG vs Goles con tamaño por tiros
        fig_xg = px.scatter(
            offensive_data,
            x='xG',
            y='goals',
            size='shots',  # Tamaño basado en número de tiros
            color='positional_attacks',  # Color basado en ataques posicionales
            title='Expected Goals vs. Goles Marcados',
            labels={'xG': 'Expected Goals', 'goals': 'Goles', 'shots': 'Tiros', 'positional_attacks': 'Ataques Posicionales'},
            hover_data=['shots', 'positional_attacks', 'area_entries']
        )
        fig_xg.add_shape(
            type='line',
            x0=0, y0=0,
            x1=4, y1=4,
            line=dict(dash='dash', color='gray')
        )
        st.plotly_chart(fig_xg, use_container_width=True)
        
        # Nuevo gráfico: Distribución de tipos de pase
        pass_data = pd.DataFrame({
            'Tipo': ['Forward', 'Back', 'Lateral', 'Long', 'Progressive', 'Smart'],
            'Total': np.random.poisson(50, 6),
            'Precisión': np.random.uniform(60, 90, 6)
        })
        
        fig_passes = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_passes.add_trace(
            go.Bar(
                x=pass_data['Tipo'],
                y=pass_data['Total'],
                name="Cantidad",
                marker_color='#004D98'
            ),
            secondary_y=False
        )
        
        fig_passes.add_trace(
            go.Scatter(
                x=pass_data['Tipo'],
                y=pass_data['Precisión'],
                name="Precisión",
                marker_color='#A50044',
                mode='lines+markers'
            ),
            secondary_y=True
        )
        
        fig_passes.update_layout(
            title='Distribución y Precisión por Tipo de Pase',
            xaxis_title='Tipo de Pase',
            barmode='group'
        )
        
        fig_passes.update_yaxes(title_text="Cantidad", secondary_y=False)
        fig_passes.update_yaxes(title_text="Precisión (%)", secondary_y=True)
        
        st.plotly_chart(fig_passes, use_container_width=True)
    
    with col2:
        # Mapa de calor mejorado con filtro por tipo de pase
        fig_heatmap = go.Figure()
        
        # Generar datos de ejemplo más detallados para el heatmap
        x = np.random.normal(50, 15, 1000)
        y = np.random.normal(50, 15, 1000)
        
        fig_heatmap.add_trace(go.Histogram2d(
            x=x, y=y,
            colorscale='RdBu',
            nbinsx=20,
            nbinsy=20,
            name='Entradas al Área'
        ))
        
        fig_heatmap.update_layout(
            title=f'Mapa de Calor de {pass_type if pass_type != "Todos" else "Entradas"} al Área',
            xaxis_title='Ancho del Campo',
            yaxis_title='Largo del Campo'
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Nuevo gráfico: Radar de eficiencia ofensiva
        categories = ['Duelos Ganados', 'Precisión Pases', 'Conversión xG', 
                    'Ataques Exitosos', 'Entradas Área', 'Pases Progresivos']
        
        values = np.random.uniform(60, 90, 6)
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Eficiencia Ofensiva'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False,
            title='Radar de Eficiencia Ofensiva'
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)

    # Insight mejorado con más métricas
    st.markdown("""
        <div class="insight-box">
            <h4>Insight para el Staff Técnico</h4>
            <p>El equipo muestra una eficiencia superior a la media en la conversión de xG (115%), 
            con una tendencia positiva en las últimas 5 jornadas. Las entradas al área se concentran 
            principalmente en el carril izquierdo (65% de precisión en pases progresivos). 
            Destaca especialmente la eficiencia en duelos ofensivos (65% ganados) y la precisión 
            en pases inteligentes (Smart passes: 72% de precisión).</p>
        </div>
    """, unsafe_allow_html=True)

# 2. Transición Ofensiva
with tabs[1]:
    st.markdown("""
        <div class="phase-container">
            <h2>Transición Ofensiva</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Métricas clave mejoradas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">8.5</div>
                <div class="metric-label">Contraataques con tiro</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">75%</div>
                <div class="metric-label">Recuperaciones exitosas</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">12.8</div>
                <div class="metric-label">Pases progresivos</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">25.4m</div>
                <div class="metric-label">Distancia media de pase</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">3.2s</div>
                <div class="metric-label">Tiempo medio a tiro</div>
            </div>
        """, unsafe_allow_html=True)

    # Filtros superiores
    col1, col2 = st.columns(2)
    with col1:
        recovery_zone = st.selectbox(
            "Zona de Recuperación",
            ["Todas", "Alta", "Media", "Baja"]
        )
    with col2:
        counter_type = st.selectbox(
            "Tipo de Contraataque",
            ["Todos", "Directo", "Posicional", "Presión Alta"]
        )

    # Visualizaciones mejoradas
    col1, col2 = st.columns(2)
    
    with col1:
        # Timeline mejorado de contraataques
        fig_timeline = go.Figure()
        
        # Datos de ejemplo mejorados
        dates = pd.date_range(start='2024-01-01', periods=38, freq='W')
        counters = np.random.poisson(8, 38)
        success_rate = np.random.uniform(0.4, 0.8, 38)
        
        fig_timeline.add_trace(go.Scatter(
            x=dates, 
            y=counters,
            mode='lines+markers',
            name='Contraataques',
            line=dict(color='#004D98', width=2),
            marker=dict(
                size=10,
                color=success_rate,
                colorscale='RdYlBu',
                showscale=True,
                colorbar=dict(title='Tasa de Éxito')
            )
        ))
        
        fig_timeline.update_layout(
            title='Evolución de Contraataques y Tasa de Éxito',
            xaxis_title='Fecha',
            yaxis_title='Número de Contraataques'
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Nuevo gráfico: Distribución de recuperaciones por zona
        recovery_data = pd.DataFrame({
            'Zona': ['Alta', 'Media', 'Baja'],
            'Total': np.random.poisson(15, 3),
            'Convertidas': np.random.poisson(8, 3)
        })
        
        fig_recoveries = go.Figure()
        
        fig_recoveries.add_trace(go.Bar(
            name='Total',
            x=recovery_data['Zona'],
            y=recovery_data['Total'],
            marker_color='#004D98'
        ))
        
        fig_recoveries.add_trace(go.Bar(
            name='Convertidas en Ataque',
            x=recovery_data['Zona'],
            y=recovery_data['Convertidas'],
            marker_color='#A50044'
        ))
        
        fig_recoveries.update_layout(
            title='Recuperaciones por Zona y Conversión',
            barmode='group',
            xaxis_title='Zona de Recuperación',
            yaxis_title='Cantidad'
        )
        
        st.plotly_chart(fig_recoveries, use_container_width=True)
    
    with col2:
        # Scatter mejorado de velocidad de transición
        fig_transition = go.Figure()
        
        # Datos de ejemplo para velocidad de transición
        time_to_shot = np.random.uniform(2, 15, 50)
        distance = np.random.uniform(20, 80, 50)
        success = np.random.choice([0, 1], size=50, p=[0.7, 0.3])
        
        fig_transition.add_trace(go.Scatter(
            x=time_to_shot,
            y=distance,
            mode='markers',
            marker=dict(
                size=12,
                color=success,
                colorscale=[[0, '#A50044'], [1, '#004D98']],
                showscale=True,
                colorbar=dict(
                    title='Éxito',
                    ticktext=['No', 'Sí'],
                    tickvals=[0, 1]
                )
            ),
            text=['Éxito' if s == 1 else 'No éxito' for s in success],
            name='Transiciones'
        ))
        
        fig_transition.update_layout(
            title='Velocidad de Transición vs Distancia Recorrida',
            xaxis_title='Tiempo hasta el tiro (s)',
            yaxis_title='Distancia recorrida (m)'
        )
        
        st.plotly_chart(fig_transition, use_container_width=True)
        
        # Nuevo gráfico: Radar de eficiencia en transición
        categories = ['Velocidad', 'Precisión', 'Finalización', 
                    'Jugadores Involucrados', 'Distancia', 'Éxito']
        
        values = np.random.uniform(60, 90, 6)
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Eficiencia en Transición'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False,
            title='Radar de Eficiencia en Transición'
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)

    # Insight mejorado
    st.markdown("""
        <div class="insight-box">
            <h4>Insight para el Staff Técnico</h4>
            <p>La efectividad en transiciones ofensivas muestra una correlación directa con la altura 
            de recuperación (75% de éxito en zona alta). El equipo es especialmente efectivo en los 
            primeros 8 segundos tras la recuperación (65% de conversión), con una media de 3.2 segundos 
            hasta el tiro. Las transiciones más exitosas involucran 3-4 jugadores y una distancia 
            media de pase de 25.4m.</p>
        </div>
    """, unsafe_allow_html=True)

# 3. Fase Defensiva
with tabs[2]:
    st.markdown("""
        <div class="phase-container">
            <h2>Fase Defensiva</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Métricas clave
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">0.8</div>
                <div class="metric-label">PSxGA por partido</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">3.2</div>
                <div class="metric-label">Tiros a puerta en contra</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">22.5</div>
                <div class="metric-label">Intercepciones + Despejes</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">8.2</div>
                <div class="metric-label">PPDA</div>
            </div>
        """, unsafe_allow_html=True)

    # Visualizaciones
    col1, col2 = st.columns(2)
    
    with col1:
        # Shot-map burbuja
        fig_shotmap = go.Figure()
        
        # Datos de ejemplo para el shot-map
        shots_x = np.random.uniform(30, 90, 50)
        shots_y = np.random.uniform(20, 60, 50)
        psxg = np.random.exponential(0.1, 50)
        
        fig_shotmap.add_trace(go.Scatter(
            x=shots_x,
            y=shots_y,
            mode='markers',
            marker=dict(
                size=psxg*100,
                color=psxg,
                colorscale='RdBu',
                showscale=True
            ),
            name='Tiros Recibidos'
        ))
        
        fig_shotmap.update_layout(
            title='Mapa de Tiros Recibidos (tamaño = PSxG)',
            xaxis_title='Distancia',
            yaxis_title='Ancho del Campo'
        )
        
        st.plotly_chart(fig_shotmap, use_container_width=True)
        
        # Histogramas PPDA
        fig_ppda = go.Figure()
        
        # Datos de ejemplo para PPDA
        barca_ppda = np.random.normal(8, 1, 1000)
        liga_ppda = np.random.normal(10, 2, 1000)
        
        fig_ppda.add_trace(go.Histogram(
            x=barca_ppda,
            name='Barcelona',
            opacity=0.75
        ))
        
        fig_ppda.add_trace(go.Histogram(
            x=liga_ppda,
            name='Media Liga',
            opacity=0.75
        ))
        
        fig_ppda.update_layout(
            title='Comparativa PPDA: Barcelona vs Liga',
            xaxis_title='PPDA',
            yaxis_title='Frecuencia',
            barmode='overlay'
        )
        
        st.plotly_chart(fig_ppda, use_container_width=True)
    
    with col2:
        # Heat map de intercepciones/despejes
        fig_interceptions = go.Figure()
        
        # Datos de ejemplo para el heatmap
        interceptions_data = np.random.poisson(3, (10, 6))
        
        fig_interceptions.add_trace(go.Heatmap(
            z=interceptions_data,
            colorscale='RdBu',
            showscale=True
        ))
        
        fig_interceptions.update_layout(
            title='Mapa de Calor de Intercepciones y Despejes',
            xaxis_title='Ancho del Campo',
            yaxis_title='Largo del Campo'
        )
        
        st.plotly_chart(fig_interceptions, use_container_width=True)
        
        # Area chart PSxGA acumulado
        fig_psxga = go.Figure()
        
        # Datos de ejemplo para PSxGA acumulado
        x = list(range(1, 39))  # Convert range to list
        y = np.cumsum(np.random.normal(0.8, 0.2, 38))
        
        fig_psxga.add_trace(go.Scatter(
            x=x,
            y=y,
            fill='tozeroy',
            name='PSxGA Acumulado'
        ))
        
        fig_psxga.update_layout(
            title='PSxGA Acumulado por Jornada',
            xaxis_title='Jornada',
            yaxis_title='PSxGA Acumulado'
        )
        
        st.plotly_chart(fig_psxga, use_container_width=True)

    # Insight
    st.markdown("""
        <div class="insight-box">
            <h4>Insight para el Staff Técnico</h4>
            <p>El equipo mantiene un PSxGA significativamente inferior a la media de la liga (0.8 vs 1.2), 
            con especial efectividad en la presión alta (PPDA de 8.2). Los tiros concedidos se concentran 
            en zonas de bajo xG, indicando una defensa posicional efectiva.</p>
        </div>
    """, unsafe_allow_html=True)

# 4. Transición Defensiva
with tabs[3]:
    st.markdown("""
        <div class="phase-container">
            <h2>Transición Defensiva</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Métricas clave
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">12.3</div>
                <div class="metric-label">Pérdidas en ⅓ alto</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">6.8</div>
                <div class="metric-label">PPDA tras pérdida</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">1.2</div>
                <div class="metric-label">Tiros contra en contra</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">72%</div>
                <div class="metric-label">Duelos defensivos ganados</div>
            </div>
        """, unsafe_allow_html=True)

    # Visualizaciones
    col1, col2 = st.columns(2)
    
    with col1:
        # Mapa secuencial
        fig_sequential = go.Figure()
        
        # Datos de ejemplo para el mapa secuencial
        losses_x = np.random.uniform(60, 90, 30)
        losses_y = np.random.uniform(20, 60, 30)
        duels_x = losses_x + np.random.normal(0, 5, 30)
        duels_y = losses_y + np.random.normal(0, 5, 30)
        
        # Crear líneas de conexión
        for i in range(len(losses_x)):
            fig_sequential.add_trace(go.Scatter(
                x=[losses_x[i], duels_x[i]],
                y=[losses_y[i], duels_y[i]],
                mode='lines+markers',
                line=dict(color='rgba(0,77,152,0.3)'),
                showlegend=False if i > 0 else True,
                name='Secuencias' if i == 0 else None
            ))
        
        fig_sequential.update_layout(
            title='Mapa Secuencial: Pérdidas → Duelos',
            xaxis_title='Distancia',
            yaxis_title='Ancho del Campo'
        )
        
        st.plotly_chart(fig_sequential, use_container_width=True)
        
        # Bar chart apilado de pérdidas
        fig_losses = go.Figure()
        
        # Datos de ejemplo para pérdidas por zona
        zonas = ['Tercio Alto', 'Tercio Medio', 'Tercio Bajo']
        perdidas = np.random.poisson(10, 3)
        recuperadas = np.random.binomial(n=perdidas, p=0.7)
        
        fig_losses.add_trace(go.Bar(
            name='No Recuperadas',
            x=zonas,
            y=perdidas - recuperadas,
            marker_color='#A50044'
        ))
        
        fig_losses.add_trace(go.Bar(
            name='Recuperadas < 30s',
            x=zonas,
            y=recuperadas,
            marker_color='#004D98'
        ))
        
        fig_losses.update_layout(
            title='Pérdidas por Zona y % Recuperación',
            barmode='stack',
            xaxis_title='Zona del Campo',
            yaxis_title='Número de Pérdidas'
        )
        
        st.plotly_chart(fig_losses, use_container_width=True)
    
    with col2:
        # Scatter PPDA vs tiros concedidos
        fig_ppda_shots = go.Figure()
        
        # Datos de ejemplo
        ppda_values = np.random.normal(8, 1, 38)
        shots_conceded = np.random.poisson(2, 38)
        
        fig_ppda_shots.add_trace(go.Scatter(
            x=ppda_values,
            y=shots_conceded,
            mode='markers',
            marker=dict(
                size=10,
                color=shots_conceded,
                colorscale='RdBu_r',
                showscale=True
            )
        ))
        
        fig_ppda_shots.update_layout(
            title='PPDA vs. Tiros Concedidos en Contraataque',
            xaxis_title='PPDA en Transición',
            yaxis_title='Tiros Concedidos'
        )
        
        st.plotly_chart(fig_ppda_shots, use_container_width=True)
        
        # Mapa de presión post-pérdida
        fig_pressure = go.Figure()
        
        # Datos de ejemplo para el mapa de presión
        pressure_data = np.random.poisson(3, (10, 6))
        
        fig_pressure.add_trace(go.Heatmap(
            z=pressure_data,
            colorscale='RdBu',
            showscale=True
        ))
        
        fig_pressure.update_layout(
            title='Mapa de Presión Post-Pérdida',
            xaxis_title='Ancho del Campo',
            yaxis_title='Largo del Campo'
        )
        
        st.plotly_chart(fig_pressure, use_container_width=True)

    # Insight
    st.markdown("""
        <div class="insight-box">
            <h4>Insight para el Staff Técnico</h4>
            <p>La reacción a la pérdida es especialmente efectiva en el tercio alto (72% de recuperaciones en <30s). 
            El PPDA en transición (6.8) indica una presión inmediata efectiva, reduciendo significativamente 
            la probabilidad de tiros en contra durante contraataques.</p>
        </div>
    """, unsafe_allow_html=True)

# 5. Balón Parado
with tabs[4]:
    st.markdown("""
        <div class="phase-container">
            <h2>Balón Parado</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Métricas clave
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">5.8</div>
                <div class="metric-label">Set pieces con tiro</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">68%</div>
                <div class="metric-label">Duelos aéreos ganados</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">0.45</div>
                <div class="metric-label">xG por ABP</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">15.3</div>
                <div class="metric-label">Despejes en ABP def.</div>
            </div>
        """, unsafe_allow_html=True)

    # Visualizaciones
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar-Line dual axis
        fig_set_pieces = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Datos de ejemplo
        x = list(range(1, 39))  # Convert range to list
        xg_abp = np.random.normal(0.45, 0.1, 38)
        goles_abp = np.random.poisson(0.4, 38)
        
        fig_set_pieces.add_trace(
            go.Bar(
                x=x,
                y=xg_abp,
                name="xG ABP",
                marker_color='#004D98'
            ),
            secondary_y=False
        )
        
        fig_set_pieces.add_trace(
            go.Scatter(
                x=x,
                y=goles_abp,
                name="Goles ABP",
                marker_color='#A50044',
                mode='lines+markers'
            ),
            secondary_y=True
        )
        
        fig_set_pieces.update_layout(
            title='xG vs. Goles en ABP por Partido',
            xaxis_title='Jornada'
        )
        
        fig_set_pieces.update_yaxes(title_text="xG ABP", secondary_y=False)
        fig_set_pieces.update_yaxes(title_text="Goles ABP", secondary_y=True)
        
        st.plotly_chart(fig_set_pieces, use_container_width=True)
        
        # Scatter duelos aéreos
        fig_aerial = go.Figure()
        
        # Datos de ejemplo para duelos aéreos
        n_players = 15
        duelos_totales = np.random.poisson(20, n_players)
        duelos_ganados = np.random.uniform(50, 85, n_players)
        
        fig_aerial.add_trace(go.Scatter(
            x=duelos_totales,
            y=duelos_ganados,
            mode='markers+text',
            text=[f'Jugador {i+1}' for i in range(n_players)],
            textposition='top center',
            marker=dict(
                size=duelos_totales,
                color=duelos_ganados,
                colorscale='RdBu',
                showscale=True
            ),
            name='Duelos Aéreos'
        ))
        
        fig_aerial.update_layout(
            title='Duelos Aéreos por Jugador',
            xaxis_title='Duelos Totales',
            yaxis_title='% Duelos Ganados'
        )
        
        st.plotly_chart(fig_aerial, use_container_width=True)
    
    with col2:
        # Heat map circular de corners
        fig_corners = go.Figure()
        
        # Datos de ejemplo para el mapa circular
        theta = np.linspace(0, 2*np.pi, 36)
        r = np.linspace(0.3, 1, 10)
        theta_grid, r_grid = np.meshgrid(theta, r)
        
        # Generar datos de ejemplo para la visualización
        values = np.random.poisson(3, 36)  # Un valor por cada sector angular
        
        fig_corners.add_trace(go.Barpolar(
            r=values,  # Usar los valores directamente como longitud de las barras
            theta=np.degrees(theta),  # Convertir radianes a grados
            marker_color=values,  # Color basado en los valores
            marker=dict(
                colorscale='RdBu',
                showscale=True
            ),
            name='Corners'
        ))
        
        fig_corners.update_layout(
            title='Dirección y Éxito de Corners',
            polar=dict(
                radialaxis=dict(range=[0, max(values) * 1.2])  # Ajustar el rango radial basado en los datos
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig_corners, use_container_width=True)
        
        # Sankey ABP
        fig_set_pieces_flow = go.Figure(data=[go.Sankey(
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = ["Corner", "Falta", "Segundo Balón", "Tiro", "Gol"],
                color = "#004D98"
            ),
            link = dict(
                source = [0, 0, 1, 1, 2, 2, 3],
                target = [2, 3, 2, 3, 3, 4, 4],
                value = [8, 4, 6, 3, 7, 3, 4]
            )
        )])
        
        fig_set_pieces_flow.update_layout(title_text="Flujo de Acciones en ABP")
        st.plotly_chart(fig_set_pieces_flow, use_container_width=True)

    # Insight
    st.markdown("""
        <div class="insight-box">
            <h4>Insight para el Staff Técnico</h4>
            <p>La efectividad en ABP ofensivos muestra una conversión de xG del 89%, destacando especialmente 
            en corners al primer palo (35% de éxito). En defensa, el equipo muestra una solidez notable con 
            un 68% de duelos aéreos ganados y una organización efectiva en segundas jugadas.</p>
        </div>
    """, unsafe_allow_html=True) 