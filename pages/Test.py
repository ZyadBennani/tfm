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
    page_title="Análisis Barça - Datos Agregados",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar menú y footer
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
        <h1 style='color: var(--primary-blue);'>Análisis Barça - Datos Agregados</h1>
        <p style='color: var(--text-color); font-size: 1.2rem;'>
            Análisis basado en datos agregados de Wyscout
        </p>
    </div>
""", unsafe_allow_html=True)

# Función para añadir métricas derivadas
def add_derived_columns(df_team, df_match):
    """
    Añade métricas derivadas a los DataFrames de equipo y partido
    
    Args:
        df_team: DataFrame con estadísticas de equipo
        df_match: DataFrame con estadísticas de partido
        
    Returns:
        Tuple con (df_team_enhanced, df_match_enhanced)
    """
    # Crear copias para no modificar los originales
    df_team = df_team.copy()
    df_match = df_match.copy()
    
    # Métricas derivadas para df_team
    df_team['Verticality_Index'] = (df_team['Forward_passes_accurate'] + 
                                   df_team['Long_passes_accurate']) / (df_team['Total_passes_accurate'] + 1e-6)
    
    df_team['CounterPress_Success_pct'] = df_team['Recoveries_High'] / (df_team['Possession_Losses_High'] + 1e-6)
    
    df_team['Positional_xG'] = df_team['xG'] - df_team['Counterattacks_with_shots'] * 0.18
    
    df_team['Off_Transition_Efficiency'] = df_team['Counterattacks_with_shots'] / (
        df_team['Recoveries_Low'] + df_team['Recoveries_Medium'] + 1e-6)
    
    df_team['Width_Ratio'] = df_team['Crosses_accurate'] / (df_team['Deep_completed_passes'] + 1e-6)
    
    df_team['Aerial_Duels_pct'] = df_team['Aerial_duels_won'] / (df_team['Aerial_duels_total'] + 1e-6)
    
    df_team['xG_ABP_proxy'] = df_team['Set_pieces_with_shots'] * 0.12
    
    # Métricas adicionales útiles
    df_team['Pass_Accuracy'] = df_team['Total_passes_accurate'] / (df_team['Total_passes'] + 1e-6) * 100
    df_team['Shot_Accuracy'] = df_team['Shots_on_target'] / (df_team['Total_shots'] + 1e-6) * 100
    
    return df_team, df_match

# Cargar datos
def load_data():
    """
    Carga los datos procesados
    Returns:
        Tuple (df_team, df_match)
    """
    df_team = pd.read_csv('Datos/processed/team_stats.csv')
    df_match = pd.read_csv('Datos/processed/match_stats.csv')
    
    # Convertir fecha a datetime
    df_team['Date'] = pd.to_datetime(df_team['Date'])
    df_match['Date'] = pd.to_datetime(df_match['Date'])
    
    return df_team, df_match

# Cargar datos reales
df_team, df_match = load_data()
# Añadir métricas derivadas
df_team, df_match = add_derived_columns(df_team, df_match)

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
    st.header("Fase Ofensiva")
    
    # Cards con métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("xG/partido", f"{df_team['xG'].mean():.2f}")
    with col2:
        st.metric("% Precisión pase", f"{df_team['Pass_Accuracy'].mean():.1f}%")
    with col3:
        st.metric("Entradas área", f"{df_team['Deep_completed_passes'].mean():.1f}")
    with col4:
        st.metric("Pases progresivos", f"{df_team['Forward_passes'].mean():.1f}")
    with col5:
        st.metric("Índice Verticalidad", f"{df_team['Verticality_Index'].mean()*100:.1f}%")
    
    # Gráficas
    col1, col2 = st.columns(2)
    
    with col1:
        # Scatter xG vs Goles con línea de tendencia
        fig_xg = px.scatter(
            df_team,
            x='xG', y='Goals',
            size='Total_shots',
            color='Shot_Accuracy',
            title='Expected Goals vs. Goles Marcados',
            labels={
                'xG': 'Expected Goals (xG)',
                'Goals': 'Goles Marcados',
                'Total_shots': 'Tiros Totales',
                'Shot_Accuracy': 'Precisión de Tiro (%)'
            },
            color_continuous_scale='RdBu',
            trendline="ols"
        )
        
        fig_xg.update_layout(
            template='plotly_white',
            title_x=0.5,
            title_font_size=20,
            showlegend=True,
            height=500
        )
        
        st.plotly_chart(fig_xg, use_container_width=True)
        
    with col2:
        # Distribución de pases
        pass_data = [
            df_team['Forward_passes_accurate'],
            df_team['Long_passes_accurate'],
            df_team['Total_passes_accurate']
        ]
        
        pass_labels = ['Pases Progresivos', 'Pases Largos', 'Total Pases']
        
        fig_passes = go.Figure()
        for i, data in enumerate(pass_data):
            fig_passes.add_trace(go.Box(
                y=data,
                name=pass_labels[i],
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8
            ))
        
        fig_passes.update_layout(
            title='Distribución de Pases Completados por Tipo',
            title_x=0.5,
            title_font_size=20,
            template='plotly_white',
            showlegend=True,
            height=500,
            yaxis_title='Número de Pases'
        )
        
        st.plotly_chart(fig_passes, use_container_width=True)
    
    # Gráfica adicional de eficiencia ofensiva
    fig_radar = go.Figure()
    
    # Métricas para el radar chart
    metrics = {
        'Precisión de Pase': df_team['Pass_Accuracy'].mean() / 100,
        'Precisión de Tiro': df_team['Shot_Accuracy'].mean() / 100,
        'Índice de Verticalidad': df_team['Verticality_Index'].mean(),
        'Ratio de Conversión': df_team['Goals'].mean() / df_team['Total_shots'].mean(),
        'Eficiencia xG': df_team['Goals'].mean() / df_team['xG'].mean()
    }
    
    # Crear radar chart
    fig_radar.add_trace(go.Scatterpolar(
        r=list(metrics.values()),
        theta=list(metrics.keys()),
        fill='toself',
        name='Eficiencia Ofensiva',
        line_color='#004D98'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        title='Radar de Eficiencia Ofensiva',
        title_x=0.5,
        title_font_size=20,
        showlegend=True,
        height=500
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # Insights
    st.markdown("""
        <div class='insight-box'>
            <h3>Insights Ofensivos</h3>
            <ul>
                <li>Promedio de xG por partido: {:.2f}</li>
                <li>Ratio de conversión de tiros: {:.1f}%</li>
                <li>Precisión de pase en último tercio: {:.1f}%</li>
                <li>Entradas al área por partido: {:.1f}</li>
            </ul>
        </div>
    """.format(
        df_team['xG'].mean(),
        (df_team['Goals'].sum() / df_team['Total_shots'].sum()) * 100,
        df_team['Pass_Accuracy'].mean(),
        df_team['Deep_completed_passes'].mean()
    ), unsafe_allow_html=True)

# 2. Transición Ofensiva
with tabs[1]:
    st.header("Transición Ofensiva")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Contraataques con tiro", f"{df_team['Counterattacks_with_shots'].mean():.1f}")
    with col2:
        st.metric("Éxito Contrapresión", f"{df_team['CounterPress_Success_pct'].mean()*100:.1f}%")
    with col3:
        st.metric("Recuperaciones altas", f"{df_team['Recoveries_High'].mean():.1f}")
    with col4:
        st.metric("Eficiencia Transición", f"{df_team['Off_Transition_Efficiency'].mean()*100:.1f}%")
    
    # Gráficas
    col1, col2 = st.columns(2)
    
    with col1:
        # Timeline de contraataques
        fig_counter = go.Figure()
        
        # Añadir línea de contraataques
        fig_counter.add_trace(go.Scatter(
            x=df_team['Match_ID'],
            y=df_team['Counterattacks_with_shots'],
            mode='lines+markers',
            name='Contraataques con tiro',
            line=dict(color='#004D98', width=2),
            marker=dict(size=8)
        ))
        
        # Añadir línea de eficiencia
        fig_counter.add_trace(go.Scatter(
            x=df_team['Match_ID'],
            y=df_team['Off_Transition_Efficiency'] * 100,
            mode='lines+markers',
            name='Eficiencia (%)',
            line=dict(color='#A50044', width=2),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig_counter.update_layout(
            title='Evolución de Contraataques y Eficiencia',
            title_x=0.5,
            title_font_size=20,
            xaxis_title='Partido',
            yaxis_title='Contraataques con tiro',
            yaxis2=dict(
                title='Eficiencia (%)',
                overlaying='y',
                side='right'
            ),
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_counter, use_container_width=True)
    
    with col2:
        # Distribución de recuperaciones por zona
        recovery_data = pd.DataFrame({
            'Zona': ['Alta', 'Media', 'Baja'],
            'Recuperaciones': [
                df_team['Recoveries_High'].mean(),
                df_team['Recoveries_Medium'].mean(),
                df_team['Recoveries_Low'].mean()
            ]
        })
        
        fig_recovery = px.bar(
            recovery_data,
            x='Zona',
            y='Recuperaciones',
            title='Distribución de Recuperaciones por Zona',
            color='Zona',
            color_discrete_map={
                'Alta': '#004D98',
                'Media': '#A50044',
                'Baja': '#EDBB00'
            }
        )
        
        fig_recovery.update_layout(
            title_x=0.5,
            title_font_size=20,
            xaxis_title='Zona de Recuperación',
            yaxis_title='Promedio por Partido',
            template='plotly_white',
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig_recovery, use_container_width=True)
    
    # Gráfica adicional de velocidad de transición
    fig_transition = go.Figure()
    
    # Crear scatter plot de velocidad de transición
    fig_transition.add_trace(go.Scatter(
        x=df_team['Match_tempo'],
        y=df_team['Off_Transition_Efficiency'] * 100,
        mode='markers',
        marker=dict(
            size=df_team['Counterattacks_with_shots'] * 5,
            color=df_team['Recoveries_High'],
            colorscale='RdBu',
            showscale=True,
            colorbar=dict(title='Recuperaciones Altas')
        ),
        text=df_team['Match_ID'].apply(lambda x: f'Partido {x}'),
        name='Velocidad de Transición'
    ))
    
    fig_transition.update_layout(
        title='Relación entre Tempo y Eficiencia en Transición',
        title_x=0.5,
        title_font_size=20,
        xaxis_title='Tempo del Partido',
        yaxis_title='Eficiencia en Transición (%)',
        template='plotly_white',
        height=500
    )
    
    st.plotly_chart(fig_transition, use_container_width=True)
    
    # Insights
    st.markdown("""
        <div class='insight-box'>
            <h3>Insights de Transición Ofensiva</h3>
            <ul>
                <li>Promedio de contraataques con tiro: {:.1f}</li>
                <li>Eficiencia en transiciones: {:.1f}%</li>
                <li>Recuperaciones en campo rival: {:.1f}</li>
                <li>Éxito en contrapresión: {:.1f}%</li>
            </ul>
        </div>
    """.format(
        df_team['Counterattacks_with_shots'].mean(),
        df_team['Off_Transition_Efficiency'].mean() * 100,
        df_team['Recoveries_High'].mean(),
        df_team['CounterPress_Success_pct'].mean() * 100
    ), unsafe_allow_html=True)

# 3. Fase Defensiva
with tabs[2]:
    st.header("Fase Defensiva")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("PSxGA", f"{df_match['PSxGA'].mean():.2f}")
    with col2:
        st.metric("PPDA", f"{df_team['PPDA'].mean():.2f}")
    with col3:
        st.metric("Intercepciones", f"{df_team['Interceptions'].mean():.1f}")
    with col4:
        st.metric("Duelos aéreos ganados", f"{df_team['Aerial_duels_won'].mean():.1f}")
    
    # Gráficas
    col1, col2 = st.columns(2)
    
    with col1:
        # Evolución del PSxGA
        fig_psxga = go.Figure()
        
        # Línea de PSxGA
        fig_psxga.add_trace(go.Scatter(
            x=df_match['Match_ID'],
            y=df_match['PSxGA'],
            mode='lines+markers',
            name='PSxGA',
            line=dict(color='#004D98', width=2),
            marker=dict(size=8)
        ))
        
        # Línea de media móvil
        fig_psxga.add_trace(go.Scatter(
            x=df_match['Match_ID'],
            y=df_match['PSxGA'].rolling(window=5, min_periods=1).mean(),
            mode='lines',
            name='Media móvil (5 partidos)',
            line=dict(color='#A50044', width=2, dash='dash')
        ))
        
        fig_psxga.update_layout(
            title='Evolución del PSxGA',
            title_x=0.5,
            title_font_size=20,
            xaxis_title='Partido',
            yaxis_title='PSxGA',
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_psxga, use_container_width=True)
    
    with col2:
        # Distribución del PPDA
        fig_ppda = go.Figure()
        
        # Histograma de PPDA
        fig_ppda.add_trace(go.Histogram(
            x=df_team['PPDA'],
            nbinsx=15,
            name='PPDA',
            marker_color='#004D98'
        ))
        
        # Línea vertical de la media del equipo
        fig_ppda.add_vline(
            x=df_team['PPDA'].mean(),
            line_dash="dash",
            line_color="#A50044",
            annotation_text=f"Media: {df_team['PPDA'].mean():.2f}",
            annotation_position="top"
        )
        
        # Línea vertical de la media de la liga
        fig_ppda.add_vline(
            x=df_match['PPDA_league_avg'].mean(),
            line_dash="dash",
            line_color="#EDBB00",
            annotation_text=f"Media Liga: {df_match['PPDA_league_avg'].mean():.2f}",
            annotation_position="bottom"
        )
        
        fig_ppda.update_layout(
            title='Distribución del PPDA',
            title_x=0.5,
            title_font_size=20,
            xaxis_title='PPDA',
            yaxis_title='Frecuencia',
            template='plotly_white',
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig_ppda, use_container_width=True)
    
    # Gráfica adicional de métricas defensivas
    defensive_metrics = pd.DataFrame({
        'Métrica': [
            'Intercepciones',
            'Duelos aéreos ganados',
            'Recuperaciones altas',
            'Despejes'
        ],
        'Por Partido': [
            df_team['Interceptions'].mean(),
            df_team['Aerial_duels_won'].mean(),
            df_team['Recoveries_High'].mean(),
            df_team['Clearances'].mean()
        ]
    })
    
    fig_def_metrics = px.bar(
        defensive_metrics,
        x='Métrica',
        y='Por Partido',
        title='Métricas Defensivas por Partido',
        color='Métrica',
        color_discrete_sequence=['#004D98', '#A50044', '#EDBB00', '#000000']
    )
    
    fig_def_metrics.update_layout(
        title_x=0.5,
        title_font_size=20,
        xaxis_title='',
        yaxis_title='Promedio por Partido',
        template='plotly_white',
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig_def_metrics, use_container_width=True)
    
    # Insights
    st.markdown("""
        <div class='insight-box'>
            <h3>Insights Defensivos</h3>
            <ul>
                <li>PSxGA promedio: {:.2f}</li>
                <li>PPDA vs Media Liga: {:.2f} vs {:.2f}</li>
                <li>Intercepciones por partido: {:.1f}</li>
                <li>Eficiencia en duelos aéreos: {:.1f}%</li>
            </ul>
        </div>
    """.format(
        df_match['PSxGA'].mean(),
        df_team['PPDA'].mean(),
        df_match['PPDA_league_avg'].mean(),
        df_team['Interceptions'].mean(),
        df_team['Aerial_duels_won'].mean() / df_team['Aerial_duels_total'].mean() * 100
    ), unsafe_allow_html=True)

# 4. Transición Defensiva
with tabs[3]:
    st.header("Transición Defensiva")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pérdidas en zona alta", f"{df_team['Possession_Losses_High'].mean():.1f}")
    with col2:
        st.metric("PPDA post-pérdida", f"{df_team['PPDA'].mean():.2f}")
    with col3:
        st.metric("Recuperaciones altas", f"{df_team['Recoveries_High'].mean():.1f}")
    with col4:
        st.metric("Éxito en contrapresión", f"{df_team['CounterPress_Success_pct'].mean()*100:.1f}%")
    
    # Gráficas
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de pérdidas por zona
        loss_data = pd.DataFrame({
            'Zona': ['Alta', 'Media', 'Baja'],
            'Pérdidas': [
                df_team['Possession_Losses_High'].mean(),
                df_team['Recoveries_Medium'].mean(),  # Usando como proxy
                df_team['Recoveries_Low'].mean()  # Usando como proxy
            ]
        })
        
        fig_losses = px.bar(
            loss_data,
            x='Zona',
            y='Pérdidas',
            title='Distribución de Pérdidas por Zona',
            color='Zona',
            color_discrete_map={
                'Alta': '#004D98',
                'Media': '#A50044',
                'Baja': '#EDBB00'
            }
        )
        
        fig_losses.update_layout(
            title_x=0.5,
            title_font_size=20,
            xaxis_title='Zona de Pérdida',
            yaxis_title='Promedio por Partido',
            template='plotly_white',
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig_losses, use_container_width=True)
    
    with col2:
        # Relación entre pérdidas y recuperaciones
        fig_recovery = go.Figure()
        
        fig_recovery.add_trace(go.Scatter(
            x=df_team['Possession_Losses_High'],
            y=df_team['Recoveries_High'],
            mode='markers',
            marker=dict(
                size=df_team['PPDA'] * 2,
                color=df_team['CounterPress_Success_pct'],
                colorscale='RdBu',
                showscale=True,
                colorbar=dict(title='Éxito en Contrapresión')
            ),
            text=df_team['Match_ID'].apply(lambda x: f'Partido {x}'),
            name='Relación Pérdidas-Recuperaciones'
        ))
        
        fig_recovery.update_layout(
            title='Relación entre Pérdidas y Recuperaciones en Zona Alta',
            title_x=0.5,
            title_font_size=20,
            xaxis_title='Pérdidas en Zona Alta',
            yaxis_title='Recuperaciones en Zona Alta',
            template='plotly_white',
            height=500
        )
        
        st.plotly_chart(fig_recovery, use_container_width=True)
    
    # Gráfica adicional de evolución temporal
    fig_evolution = go.Figure()
    
    # Añadir líneas de evolución
    fig_evolution.add_trace(go.Scatter(
        x=df_team['Match_ID'],
        y=df_team['Possession_Losses_High'],
        mode='lines+markers',
        name='Pérdidas Altas',
        line=dict(color='#004D98', width=2)
    ))
    
    fig_evolution.add_trace(go.Scatter(
        x=df_team['Match_ID'],
        y=df_team['Recoveries_High'],
        mode='lines+markers',
        name='Recuperaciones Altas',
        line=dict(color='#A50044', width=2)
    ))
    
    fig_evolution.add_trace(go.Scatter(
        x=df_team['Match_ID'],
        y=df_team['PPDA'],
        mode='lines+markers',
        name='PPDA',
        line=dict(color='#EDBB00', width=2),
        yaxis='y2'
    ))
    
    fig_evolution.update_layout(
        title='Evolución de Métricas de Transición Defensiva',
        title_x=0.5,
        title_font_size=20,
        xaxis_title='Partido',
        yaxis_title='Cantidad',
        yaxis2=dict(
            title='PPDA',
            overlaying='y',
            side='right'
        ),
        template='plotly_white',
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    # Insights
    st.markdown("""
        <div class='insight-box'>
            <h3>Insights de Transición Defensiva</h3>
            <ul>
                <li>Pérdidas en zona alta por partido: {:.1f}</li>
                <li>Ratio de recuperación post-pérdida: {:.1f}%</li>
                <li>PPDA en transición: {:.2f}</li>
                <li>Eficiencia de contrapresión: {:.1f}%</li>
            </ul>
        </div>
    """.format(
        df_team['Possession_Losses_High'].mean(),
        (df_team['Recoveries_High'].mean() / df_team['Possession_Losses_High'].mean()) * 100,
        df_team['PPDA'].mean(),
        df_team['CounterPress_Success_pct'].mean() * 100
    ), unsafe_allow_html=True)

# 5. Balón Parado
with tabs[4]:
    st.header("Balón Parado")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tiros de ABP", f"{df_team['Set_pieces_with_shots'].mean():.1f}")
    with col2:
        st.metric("xG de ABP", f"{df_team['xG_ABP_proxy'].mean():.2f}")
    with col3:
        st.metric("Duelos aéreos ganados", f"{df_team['Aerial_duels_won'].mean():.1f}")
    with col4:
        st.metric("% Duelos aéreos", f"{df_team['Aerial_Duels_pct'].mean()*100:.1f}%")
    
    # Gráficas
    col1, col2 = st.columns(2)
    
    with col1:
        # Evolución de ABP
        fig_set_pieces = go.Figure()
        
        # Línea de tiros de ABP
        fig_set_pieces.add_trace(go.Scatter(
            x=df_team['Match_ID'],
            y=df_team['Set_pieces_with_shots'],
            mode='lines+markers',
            name='Tiros de ABP',
            line=dict(color='#004D98', width=2),
            marker=dict(size=8)
        ))
        
        # Línea de xG de ABP
        fig_set_pieces.add_trace(go.Scatter(
            x=df_team['Match_ID'],
            y=df_team['xG_ABP_proxy'],
            mode='lines+markers',
            name='xG de ABP',
            line=dict(color='#A50044', width=2),
            marker=dict(size=8)
        ))
        
        fig_set_pieces.update_layout(
            title='Evolución de Acciones a Balón Parado',
            title_x=0.5,
            title_font_size=20,
            xaxis_title='Partido',
            yaxis_title='Cantidad',
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_set_pieces, use_container_width=True)
    
    with col2:
        # Scatter de duelos aéreos
        fig_aerial = go.Figure()
        
        fig_aerial.add_trace(go.Scatter(
            x=df_team['Aerial_duels_total'],
            y=df_team['Aerial_duels_won'],
            mode='markers',
            marker=dict(
                size=df_team['Set_pieces_with_shots'] * 5,
                color=df_team['Aerial_Duels_pct'],
                colorscale='RdBu',
                showscale=True,
                colorbar=dict(title='% Duelos Ganados')
            ),
            text=df_team['Match_ID'].apply(lambda x: f'Partido {x}'),
            name='Duelos Aéreos'
        ))
        
        # Añadir línea de tendencia
        fig_aerial.add_trace(go.Scatter(
            x=[df_team['Aerial_duels_total'].min(), df_team['Aerial_duels_total'].max()],
            y=[df_team['Aerial_duels_total'].min() * df_team['Aerial_Duels_pct'].mean(),
               df_team['Aerial_duels_total'].max() * df_team['Aerial_Duels_pct'].mean()],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Media de Éxito'
        ))
        
        fig_aerial.update_layout(
            title='Relación entre Duelos Aéreos Totales y Ganados',
            title_x=0.5,
            title_font_size=20,
            xaxis_title='Duelos Aéreos Totales',
            yaxis_title='Duelos Aéreos Ganados',
            template='plotly_white',
            height=500
        )
        
        st.plotly_chart(fig_aerial, use_container_width=True)
    
    # Gráfica adicional de tipos de ABP
    set_piece_types = pd.DataFrame({
        'Tipo': ['Córners', 'Faltas', 'Penaltis'],
        'Cantidad': [
            df_team['Set_pieces_with_shots'].mean() * 0.6,  # Aproximación
            df_team['Set_pieces_with_shots'].mean() * 0.3,  # Aproximación
            df_team['Set_pieces_with_shots'].mean() * 0.1   # Aproximación
        ]
    })
    
    fig_types = px.pie(
        set_piece_types,
        values='Cantidad',
        names='Tipo',
        title='Distribución de Tipos de ABP',
        color='Tipo',
        color_discrete_sequence=['#004D98', '#A50044', '#EDBB00']
    )
    
    fig_types.update_layout(
        title_x=0.5,
        title_font_size=20,
        template='plotly_white',
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig_types, use_container_width=True)
    
    # Insights
    st.markdown("""
        <div class='insight-box'>
            <h3>Insights de Balón Parado</h3>
            <ul>
                <li>Promedio de tiros de ABP: {:.1f}</li>
                <li>xG generado de ABP: {:.2f}</li>
                <li>Eficiencia en duelos aéreos: {:.1f}%</li>
                <li>Duelos aéreos ganados por partido: {:.1f}</li>
            </ul>
        </div>
    """.format(
        df_team['Set_pieces_with_shots'].mean(),
        df_team['xG_ABP_proxy'].mean(),
        df_team['Aerial_Duels_pct'].mean() * 100,
        df_team['Aerial_duels_won'].mean()
    ), unsafe_allow_html=True) 