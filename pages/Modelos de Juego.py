import streamlit as st
st.set_page_config(
    page_title="Modelos de Juego",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)
import os
import pandas as pd
from utils.navigation import show_home_button, show_page_header
import plotly.graph_objects as go
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from PIL import Image

# Mostrar botón de volver al inicio
show_home_button()

# Mostrar header de la página
show_page_header("Modelos de Juego")

# Definición de métricas por modelo
MODELOS_JUEGO = {
    'K1': [
        'Passes to final third / accurate', 'Average passes per possession', 'Progressive passes / accurate',
        'Deep completed crosses', 'Penalty area entries (runs / crosses)', 'Recoveries / Low / Medium / High',
        'Touches in penalty area', 'Positional attacks / with shots', 'xG'
    ],
    'K2': [
        'PPDA', 'Recoveries / Low / Medium / High', 'Average passes per possession', 'Defensive duels / won',
        'Interceptions', 'Losses / Low / Medium / High', 'Counterattacks / with shots', 'xG', 'PSxGA',
        'Clearances', 'Shots / on target'
    ],
    'K3': [
        'PPDA', 'Recoveries / Low / Medium / High', 'Counterattacks / with shots', 'xG',
        'Forward passes / accurate', 'Progressive passes / accurate', 'Defensive duels / won',
        'Losses / Low / Medium / High', 'Penalty area entries (runs / crosses)', 'Aerial duels / won', 'Goals'
    ],
    'K4': [
        'Possession, %', 'Average passes per possession', 'xG', 'Counterattacks / with shots',
        'Positional attacks / with shots', 'Defensive duels / won', 'Recoveries / Low / Medium / High',
        'Progressive passes / accurate', 'Shots / on target', 'Losses / Low / Medium / High',
        'Crosses / accurate', 'Long passes / accurate', 'Passes / accurate', 'PPDA'
    ]
}

# Función para obtener el logo
EQUIPO_LOGO_MAP = {
    'Barcelona': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Barcelona.png',
    'Real Madrid': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Real_Madrid.png',
    'Atlético Madrid': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/atletico_madrid.png',
    'Athletic Bilbao': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Athletic_Club.png',
    'Real Sociedad': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Real_Sociedad.png',
    'Sevilla': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Sevilla.png',
    'Valencia': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Valencia.png',
    'Real Betis': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Real_Betis.png',
    'Villarreal': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Villareal.png',
    'Girona': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Girona.png',
    'Celta de Vigo': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Celta_Vigo.png',
    'Rayo Vallecano': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Rayo_Vallecano.png',
    'Osasuna': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Osasuna.png',
    'Getafe': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Getafe.png',
    'Deportivo Alavés': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Deportivo_Alaves.png',
    'Espanyol': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Espanyol.png',
    'Las Palmas': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Las_Palmas.png',
    'Mallorca': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Mallorca.png',
    'Leganés': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Leganés.png',
    'Real Valladolid': 'static/wetransfer_players_2025-06-18_1752/LOGHI_PNG/LA_LIGA/SQUADRE/Valladolid.png',
}

def get_logo_path(equipo):
    return EQUIPO_LOGO_MAP.get(equipo, None)

# Leer todos los excels de la carpeta
folder = "Datos/Wyscout Liga"
files = [f for f in os.listdir(folder) if f.endswith('.xlsx') and not f.startswith('~$')]
team_dfs = []
for file in files:
    path = os.path.join(folder, file)
    df = pd.read_excel(path)
    # Suponemos que el nombre del equipo está en el nombre del archivo
    team_name = file.replace('Team Stats ', '').replace('.xlsx', '').replace('_', ' ').strip()
    df['Team'] = team_name
    team_dfs.append(df)

# Unir todos los equipos en un solo DataFrame (asumimos que cada archivo tiene una fila resumen o la fila relevante es la primera)
teams_data = []
for df in team_dfs:
    row = df.iloc[0]  # Ajusta si la fila relevante no es la primera
    team = row['Team']
    team_metrics = {'Team': team}
    for modelo, metrics in MODELOS_JUEGO.items():
        values = []
        for m in metrics:
            if m in row:
                values.append(row[m])
            else:
                values.append(np.nan)
        team_metrics[modelo] = np.nanmean(values)
    teams_data.append(team_metrics)

df_teams = pd.DataFrame(teams_data)

# Normalizar los valores de cada modelo (MinMax)
scaler = MinMaxScaler()
modelos_cols = list(MODELOS_JUEGO.keys())
df_teams[modelos_cols] = scaler.fit_transform(df_teams[modelos_cols])

# Calcular la posición relativa de cada equipo en el gráfico (usamos K1 vs K2 para X, K3 vs K4 para Y)
df_teams['x'] = (df_teams['K2'] - df_teams['K1'])
df_teams['y'] = (df_teams['K4'] - df_teams['K3'])

def plot_modelos_juego(df):
    fig = go.Figure()
    x_min, x_max = df['x'].min()-0.1, df['x'].max()+0.1
    y_min, y_max = df['y'].min()-0.1, df['y'].max()+0.1
    x_med, y_med = 0, 0
    # Fondos de cuadrantes
    fig.add_shape(type="rect", x0=x_min, x1=x_med, y0=y_med, y1=y_max, fillcolor="rgba(255,255,200,0.32)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=x_med, x1=x_max, y0=y_med, y1=y_max, fillcolor="rgba(200,255,200,0.32)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=x_min, x1=x_med, y0=y_min, y1=y_med, fillcolor="rgba(200,220,255,0.32)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=x_med, x1=x_max, y0=y_min, y1=y_med, fillcolor="rgba(255,200,200,0.32)", line_width=0, layer="below")
    # Líneas de mediana
    fig.add_shape(type="line", x0=x_med, x1=x_med, y0=y_min, y1=y_max, line=dict(dash="dash", color="gray"))
    fig.add_shape(type="line", x0=x_min, x1=x_max, y0=y_med, y1=y_med, line=dict(dash="dash", color="gray"))
    # Etiquetas de cuadrantes
    cuadrantes = [
        (x_min + 0.2*(x_max-x_min), y_max - 0*(y_max-y_min), 'K1', 'Pressing & Positional Play'),
        (x_max - 0.15*(x_max-x_min), y_max - 0*(y_max-y_min), 'K2', 'Low Block & Counter'),
        (x_min + 0.2*(x_max-x_min), y_min + 0*(y_max-y_min), 'K3', 'High Press & Direct'),
        (x_max - 0.15*(x_max-x_min), y_min + 0*(y_max-y_min), 'K4', 'Structured & Balanced'),
    ]
    for cx, cy, k, label in cuadrantes:
        fig.add_annotation(
            x=cx, y=cy,
            text=f"<b>{k}</b><br><span style='font-size:1.1em'>{label}</span>",
            showarrow=False, font=dict(size=16, color="#222"),
            xanchor="left" if 'K1' in k or 'K3' in k else "right",
            yanchor="top" if 'K1' in k or 'K2' in k else "bottom",
            bgcolor="rgba(255,255,255,0.7)", bordercolor="#004D98", borderwidth=2
        )
    # Logos y puntos
    logo_sizex = (x_max - x_min) * 0.11
    logo_sizey = (y_max - y_min) * 0.11
    for _, row in df.iterrows():
        team = row['Team']
        is_barca = (team == 'Barcelona')
        # Efecto destacado igual que en la página de inicio
        if is_barca:
            # Dibuja un círculo grande detrás del logo (más grande)
            fig.add_trace(go.Scatter(
                x=[row['x']],
                y=[row['y']],
                mode="markers",
                marker=dict(size=95, color="rgba(165,0,68,0.25)", line=dict(width=7, color="#A50044")),
                hoverinfo="skip",
                showlegend=False
            ))
            sizex = logo_sizex
            sizey = logo_sizey
        else:
            sizex = logo_sizex
            sizey = logo_sizey
        # Marcador invisible para hover
        fig.add_trace(go.Scatter(
            x=[row['x']], y=[row['y']],
            mode="markers",
            marker=dict(size=1, color='rgba(0,0,0,0)', symbol="circle"),
            name=team,
            text=f"<b>{team}</b>",
            hoverinfo="text"
        ))
        logo_path = get_logo_path(team)
        if logo_path and os.path.exists(logo_path):
            fig.add_layout_image(
                dict(
                    source=Image.open(logo_path),
                    x=row['x'],
                    y=row['y'],
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
    fig.update_xaxes(range=[x_min, x_max], showticklabels=False, visible=False)
    fig.update_yaxes(range=[y_min, y_max], showticklabels=False, visible=False)
    fig.update_layout(
        plot_bgcolor="#F8F9FA",
        paper_bgcolor="#FFFFFF",
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(family="Arial", size=16),
        height=700,
        width=1100
    )
    return fig

fig = plot_modelos_juego(df_teams)
st.plotly_chart(fig, use_container_width=True)

# Tabla resumen de los modelos de juego
st.markdown("""
<style>
.tabla-modelos {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 0;
    margin-top: 24px;
    font-family: Arial, sans-serif;
}
.tabla-modelos th {
    background: linear-gradient(90deg, #004D98 60%, #b50a2e 100%);
    color: #fff;
    padding: 18px 8px 14px 8px;
    font-size: 1.25em;
    border-radius: 18px 18px 0 0;
    font-weight: bold;
}
.tabla-modelos td {
    background: #fff;
    color: #003366;
    padding: 16px 18px;
    vertical-align: top;
    font-size: 1.08em;
    border-bottom: 1px solid #e0e0e0;
}
.tabla-modelos tr:last-child td {
    border-radius: 0 0 18px 18px;
}
</style>
<table class='tabla-modelos'>
    <tr>
        <th>K1: Pressing & Positional Play</th>
        <th>K2: Low Block & Counter</th>
        <th>K3: High Press & Direct</th>
        <th>K4: Structured & Balanced</th>
    </tr>
    <tr>
        <td><b>Características:</b>
            <ul>
                <li>Recuperación alta y presión coordinada</li>
                <li>Pases progresivos y posesión alta</li>
                <li>Superioridad numérica en campo rival</li>
            </ul>
        </td>
        <td><b>Características:</b>
            <ul>
                <li>Defensa compacta y bloque bajo</li>
                <li>Contrataques rápidos y letales</li>
                <li>Seguridad defensiva como base</li>
            </ul>
        </td>
        <td><b>Características:</b>
            <ul>
                <li>Presión alta e intensidad defensiva</li>
                <li>Transiciones rápidas y verticalidad</li>
                <li>Duelo físico y ritmo elevado</li>
            </ul>
        </td>
        <td><b>Características:</b>
            <ul>
                <li>Equilibrio entre defensa y ataque</li>
                <li>Transiciones controladas y estructura táctica</li>
                <li>Flexibilidad y solidez defensiva</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><b>Definición:</b> Juego basado en el control del balón y la posesión posicional.</td>
        <td><b>Definición:</b> Bloque bajo y transiciones rápidas, explota espacios del rival.</td>
        <td><b>Definición:</b> Presión intensa y juego directo, superioridad física.</td>
        <td><b>Definición:</b> Modelo híbrido, combina solidez y flexibilidad.</td>
    </tr>
    <tr>
        <td><b>Tipo de plantilla:</b>
            <ul>
                <li>Guardiola, Flick</li>
                <li>Jugadores inteligentes, técnicos, asociativos</li>
                <li>Laterales que aportan amplitud</li>
                <li>Mediocentro posicional de élite</li>
                <li>Defensas con gran capacidad de pase</li>
                <li>Extremos que juegan por dentro y crean juego</li>
            </ul>
        </td>
        <td><b>Tipo de plantilla:</b>
            <ul>
                <li>Mourinho, Simeone</li>
                <li>Centrales contundentes y bien posicionados</li>
                <li>Lateral defensivo y lateral profundo</li>
                <li>Delantero físico para descarga</li>
                <li>Volantes intensos y veloces para transiciones</li>
                <li>Portero con buen juego largo</li>
            </ul>
        </td>
        <td><b>Tipo de plantilla:</b>
            <ul>
                <li>Klopp, Gasperini</li>
                <li>Jugadores atléticos, agresivos, directos</li>
                <li>Centrocampistas box-to-box</li>
                <li>Delanteros que atacan el espacio</li>
                <li>Centrales potentes en duelos</li>
                <li>Extremos verticales con gran zancada</li>
            </ul>
        </td>
        <td><b>Tipo de plantilla:</b>
            <ul>
                <li>Emery, Imanol Alguacil</li>
                <li>Jugadores tácticamente disciplinados</li>
                <li>Centrocampistas mixtos</li>
                <li>Delanteros que participan en la creación</li>
                <li>Líneas cortas entre líneas</li>
                <li>Laterales con lectura táctica</li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><b>Filosofía:</b><br>"Si tenemos el balón, el rival no lo tiene."</td>
        <td><b>Filosofía:</b><br>"Primero no encajar. Después, golpear."</td>
        <td><b>Filosofía:</b><br>"El orden es enemigo del ritmo."</td>
        <td><b>Filosofía:</b><br>"El equilibrio no es pasividad, es inteligencia colectiva."</td>
    </tr>
    <tr>
        <td><b>Métricas:</b>
            <ul>
                <li>Passes to final third / accurate</li>
                <li>Average passes per possession</li>
                <li>Progressive passes / accurate</li>
                <li>Deep completed crosses</li>
                <li>Penalty area entries (runs / crosses)</li>
                <li>Recoveries / Low / Medium / High</li>
                <li>Touches in penalty area</li>
                <li>Positional attacks / with shots</li>
                <li>xG</li>
            </ul>
        </td>
        <td><b>Métricas:</b>
            <ul>
                <li>PPDA</li>
                <li>Recoveries / Low / Medium / High</li>
                <li>Average passes per possession</li>
                <li>Defensive duels / won</li>
                <li>Interceptions</li>
                <li>Losses / Low / Medium / High</li>
                <li>Counterattacks / with shots</li>
                <li>xG</li>
                <li>PSxGA</li>
                <li>Clearances</li>
                <li>Shots / on target</li>
            </ul>
        </td>
        <td><b>Métricas:</b>
            <ul>
                <li>PPDA</li>
                <li>Recoveries / Low / Medium / High</li>
                <li>Counterattacks / with shots</li>
                <li>xG</li>
                <li>Forward passes / accurate</li>
                <li>Progressive passes / accurate</li>
                <li>Defensive duels / won</li>
                <li>Losses / Low / Medium / High</li>
                <li>Penalty area entries (runs / crosses)</li>
                <li>Aerial duels / won</li>
                <li>Goals</li>
            </ul>
        </td>
        <td><b>Métricas:</b>
            <ul>
                <li>Possession, %</li>
                <li>Average passes per possession</li>
                <li>xG</li>
                <li>Counterattacks / with shots</li>
                <li>Positional attacks / with shots</li>
                <li>Defensive duels / won</li>
                <li>Recoveries / Low / Medium / High</li>
                <li>Progressive passes / accurate</li>
                <li>Shots / on target</li>
                <li>Losses / Low / Medium / High</li>
                <li>Crosses / accurate</li>
                <li>Long passes / accurate</li>
                <li>Passes / accurate</li>
                <li>PPDA</li>
            </ul>
        </td>
    </tr>
</table>
""", unsafe_allow_html=True) 