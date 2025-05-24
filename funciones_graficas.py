import plotly.graph_objects as go 
import streamlit as st


def crear_grafico_radar(jugador, datos):
    categorias = ['Velocidad', 'Regate', 'Pase', 'Tiro', 'Defensa', 'Físico']
    valores = [85, 92, 88, 78, 65, 75]

    # Crear el gráfico de radar
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=categorias,
        fill='toself',
        name=jugador,
        line_color='#CD2640',
        fillcolor='rgba(205, 38, 64, 0.3)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title="Características del Jugador",
        showlegend=True
    )

    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)


