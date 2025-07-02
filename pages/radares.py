import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def load_player_data():
    return pd.read_csv(r'C:/Users/zyadb/Desktop/LINKEDIN/DatosLinkedin/radares_nico_williams.csv', sep=';')

def get_player_metrics(df, player_name, team):
    try:
        player_data = df[(df['Jugador'].str.strip() == player_name) & \
                        (df['Equipo'] == team)]
        if len(player_data) == 0:
            st.error(f"No se encontraron datos para {player_name} en {team}")
            return None
        player_data = player_data.iloc[0]
        metrics = {}
        for i in range(1, 10):  # 9 métricas posibles
            metric_name = player_data[f'Metrica {i}']
            metric_value = player_data[f'Valor Normalizado {i}']
            if pd.notna(metric_name) and pd.notna(metric_value):
                try:
                    value = float(str(metric_value).replace(',', '.'))
                    value = max(0, min(100, value))
                    metrics[metric_name] = value
                except:
                    continue
        return metrics
    except Exception as e:
        st.error(f"Error al obtener métricas para {player_name}: {str(e)}")
        return None

def create_radar_chart(barca_player: str, bayern_player: str, position: str, chart_id: str = None):
    df = load_player_data()
    try:
        metrics_barca = get_player_metrics(df, barca_player, 'Barcelona')
        metrics_bayern = get_player_metrics(df, bayern_player, 'Bayern')
        if not metrics_barca or not metrics_bayern:
            st.error(f"No se pudieron obtener métricas para la comparación {barca_player} vs {bayern_player}")
            st.write("Datos disponibles en el CSV:")
            st.write(df[['Jugador', 'Equipo']].to_dict('records'))
            return None
        all_categories = set(metrics_barca.keys()) | set(metrics_bayern.keys())
        categories = sorted(list(all_categories))
        barca_values = [metrics_barca.get(cat, 0) for cat in categories]
        bayern_values = [metrics_bayern.get(cat, 0) for cat in categories]
        barca_values.append(barca_values[0])
        bayern_values.append(bayern_values[0])
        categories_closed = categories + [categories[0]]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=barca_values,
            theta=categories_closed,
            fill='toself',
            name=barca_player,
            line_color='#004D98',
            fillcolor='rgba(0, 77, 152, 0.3)',
            connectgaps=True,
            line=dict(color='#004D98', width=2)
        ))
        fig.add_trace(go.Scatterpolar(
            r=bayern_values,
            theta=categories_closed,
            fill='toself',
            name=bayern_player,
            line_color='#DC052D',
            fillcolor='rgba(220, 5, 45, 0.3)',
            connectgaps=True,
            line=dict(color='#DC052D', width=2)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(128, 128, 128, 0.3)',
                    gridwidth=1
                ),
                angularaxis=dict(
                    direction='clockwise',
                    rotation=90,
                    gridcolor='rgba(128, 128, 128, 0.3)',
                    gridwidth=1,
                    linecolor='rgba(128, 128, 128, 0.6)',
                    linewidth=1
                ),
                bgcolor='rgba(255, 255, 255, 0.9)'
            ),
            showlegend=True,
            height=350,
            margin=dict(t=20, b=20, l=20, r=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    except Exception as e:
        st.error(f"Error al crear el gráfico para {barca_player} vs {bayern_player}: {str(e)}")
        return None

# --- INTERFAZ PRINCIPAL ---
st.title("Comparativa de Radares Barça vs Bayern")
df = load_player_data()

# Selección de jugadores
barca_players = ['Nico Williams']
bayern_players = ['Luis Díaz']

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    barca_player = st.selectbox("Jugador 1", barca_players)
with col2:
    bayern_player = st.selectbox("Jugador 2", bayern_players)
with col3:
    position = st.text_input("Posición (opcional)", "")

if st.button("Mostrar Radar"):
    fig = create_radar_chart(barca_player, bayern_player, position)
    if fig:
        st.plotly_chart(fig, use_container_width=True) 