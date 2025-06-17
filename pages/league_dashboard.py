import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import os
import glob
import plotly.graph_objects as go
import itertools
import base64

# Lista de los 20 equipos de LaLiga y sus nombres de archivo de logo
LALIGA_TEAMS = [
    ("FC Barcelona", "barcelona.png"),
    ("Real Madrid", "real_madrid.png"),
    ("Atlético de Madrid", "atletico_de_madrid.png"),
    ("Athletic Club", "athletic_club.png"),
    ("Real Sociedad", "real_sociedad.png"),
    ("Sevilla FC", "sevilla.png"),
    ("Valencia CF", "valencia.png"),
    ("Real Betis", "real_betis.png"),
    ("Villarreal CF", "villarreal.png"),
    ("Girona FC", "girona.png"),
    ("RC Celta", "celta_de_vigo.png"),
    ("Rayo Vallecano", "rayo_vallecano.png"),
    ("CA Osasuna", "osasuna.png"),
    ("Getafe CF", "getafe.png"),
    ("Deportivo Alavés", "alaves.png"),
    ("RCD Espanyol", "espanyol.png"),
    ("UD Las Palmas", "las_palmas.png"),
    ("RCD Mallorca", "mallorca.png"),
    ("CD Leganés", "leganes.png"),
    ("Real Valladolid", "real_valladolid.png"),
]

# 2. Datos ficticios reproducibles
def generate_fake_data(per90=True):
    rng = np.random.default_rng(7)
    teams = [name for name, _ in LALIGA_TEAMS]
    n = len(teams)
    if per90:
        df = pd.DataFrame({
            "Team": teams,
            "PPDA/90": rng.uniform(5, 14, n),
            "CtrShots/90": rng.uniform(0.2, 3.0, n),
            "LossHigh": rng.integers(25, 51, n),
            "RecovHigh": rng.integers(5, 31, n),
            "ShotsOT/90": rng.uniform(1.5, 6.0, n),
            "DeepPass/90": rng.uniform(6, 22, n),
            "PSxGA/90": rng.uniform(0.6, 2.5, n),
            "ProgPass/90": rng.uniform(15, 45, n),
            "xG/90": rng.uniform(0.6, 2.2, n),
            "CP_succes/90": rng.uniform(0.1, 0.8, n),
        })
    else:
        # Simular medias por partido (no por 90')
        df = pd.DataFrame({
            "Team": teams,
            "PPDA": rng.uniform(5, 14, n),
            "CtrShots": rng.uniform(0.2, 3.0, n),
            "LossHigh": rng.integers(25, 51, n),
            "RecovHigh": rng.integers(5, 31, n),
            "ShotsOT": rng.uniform(1.5, 6.0, n),
            "DeepPass": rng.uniform(6, 22, n),
            "PSxGA": rng.uniform(0.6, 2.5, n),
            "ProgPass": rng.uniform(15, 45, n),
            "xG": rng.uniform(0.6, 2.2, n),
            "CP_succ": rng.uniform(0.1, 0.8, n),
        })
    return df

LOGOS_PATH = os.path.join(os.path.dirname(__file__), "..", "static", "logos")

def get_logo_for_team(team_name):
    for name, logo_file in LALIGA_TEAMS:
        if team_name == name:
            logo_path = os.path.join(LOGOS_PATH, logo_file)
            if os.path.exists(logo_path):
                return Image.open(logo_path)
    return None

# 3. Función auxiliar para scatter-plot
def plot_phase(ax, df, x, y, invert, title, color):
    ax.scatter(df[x], df[y], s=0)
    for _, row in df.iterrows():
        logo_img = get_logo_for_team(row["Team"])
        if logo_img is not None:
            if row["Team"] == "FC Barcelona":
                # Borde especial para el Barça
                imagebox = OffsetImage(logo_img, zoom=0.13)
                ab = AnnotationBbox(
                    imagebox, (row[x], row[y]), frameon=True, pad=0.15,
                    bboxprops=dict(edgecolor="#A50044", linewidth=3, boxstyle="circle,pad=0.2", alpha=0.95)
                )
            else:
                imagebox = OffsetImage(logo_img, zoom=0.12)
                ab = AnnotationBbox(imagebox, (row[x], row[y]), frameon=False, pad=0.1)
            ax.add_artist(ab)
    ax.axvline(df[x].median(), ls='--', color='gray')
    ax.axhline(df[y].median(), ls='--', color='gray')
    if invert:
        ax.invert_xaxis()
    ax.set_title(title, fontsize=12)
    ax.set_xlabel(x)
    ax.set_ylabel(y)

def plot_phase_plotly(df, x, y, invert, title, color, x_range=None, y_range=None, selected_team=None):
    logos_path = os.path.join(os.path.dirname(__file__), "..", "static", "logos")
    logo_files = {name: os.path.join(logos_path, logo) for name, logo in LALIGA_TEAMS}
    fig = go.Figure()
    # Calcular tamaño proporcional al rango de ejes (autozoom)
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
    # Si los puntos están muy juntos, logos pequeños; si dispersos, logos grandes
    if min_dist is not None and max(x_span, y_span) > 0:
        density_factor = min(1.0, max(0.0, min_dist / (0.25 * max(x_span, y_span))))
        logo_frac = min_size + (max_size - min_size) * density_factor
    else:
        logo_frac = 0.12
    logo_sizex = x_span * logo_frac
    logo_sizey = y_span * logo_frac
    for _, row in df.iterrows():
        team = row['Team']
        logo_path = logo_files.get(team, None)
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
        invisible_marker = dict(size=1, color='rgba(0,0,0,0)', symbol="circle")
        if logo_path and os.path.exists(logo_path):
            fig.add_layout_image(
                dict(
                    source=Image.open(logo_path),
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
        fig.add_trace(go.Scatter(
            x=[row[x]],
            y=[row[y]],
            mode="markers",
            marker=invisible_marker,
            name=team,
            text=f"<b>{team}</b><br>{x}: {row[x]:.2f}<br>{y}: {row[y]:.2f}",
            hoverinfo="text"
        ))
    # Líneas de la mediana
    x_med = df[x].median()
    y_med = df[y].median()
    x_min, x_max = (x_range if x_range else (df[x].min(), df[x].max()))
    y_min, y_max = (y_range if y_range else (df[y].min(), df[y].max()))
    # Fondos de cuadrantes (colores suaves, opacidad más alta)
    fig.add_shape(type="rect", x0=x_min, x1=x_med, y0=y_med, y1=y_max, fillcolor="rgba(255,255,200,0.32)", line_width=0, layer="below")  # Amarillo
    fig.add_shape(type="rect", x0=x_med, x1=x_max, y0=y_med, y1=y_max, fillcolor="rgba(200,255,200,0.32)", line_width=0, layer="below")  # Verde
    fig.add_shape(type="rect", x0=x_min, x1=x_med, y0=y_min, y1=y_med, fillcolor="rgba(200,220,255,0.32)", line_width=0, layer="below")  # Azul
    fig.add_shape(type="rect", x0=x_med, x1=x_max, y0=y_min, y1=y_med, fillcolor="rgba(255,200,200,0.32)", line_width=0, layer="below")  # Rojo
    fig.add_shape(type="line", x0=x_med, x1=x_med, y0=y_min, y1=y_max, line=dict(dash="dash", color="gray"))
    fig.add_shape(type="line", x0=x_min, x1=x_max, y0=y_med, y1=y_med, line=dict(dash="dash", color="gray"))
    # Eje X: forzar explícitamente el rango de menor a mayor en Fase ofensiva
    if title == "Fase ofensiva":
        if x_range:
            fig.update_xaxes(range=x_range)
        else:
            fig.update_xaxes(autorange=True)
    elif invert:
        if x_range:
            fig.update_xaxes(range=x_range[::-1])
        else:
            fig.update_xaxes(autorange="reversed")
    else:
        if x_range:
            fig.update_xaxes(range=x_range)
        else:
            fig.update_xaxes(autorange=True)
    if y_range:
        fig.update_yaxes(range=y_range)
    fig.update_layout(
        title=title,
        xaxis_title=x,
        yaxis_title=y,
        plot_bgcolor="#F8F9FA",
        paper_bgcolor="#FFFFFF",
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(family="Arial", size=14),
        transition=dict(duration=600, easing="cubic-in-out")
    )
    return fig

def load_laliga_team_stats(per90=True):
    data_dir = os.path.join(os.path.dirname(__file__), "..", "Datos", "Wyscout Liga")
    files = glob.glob(os.path.join(data_dir, "Team Stats *.xlsx"))
    # Diccionario de normalización para equipos con nombre diferente en el Excel
    excel_name_map = {
        'Mallorca': 'RCD Mallorca',
        'Celta de Vigo': 'RC Celta',
        'Villareal': 'Villarreal CF',
        'Espanyol': 'RCD Espanyol',
    }
    team_map = {name.lower().replace('cf','').replace('fc','').replace('cd','').replace('ud','').replace('ca','').replace('rcd','').replace('athletic club','athletic bilbao').replace('atlético de madrid','atlético madrid').replace('deportivo alavés','alavés').replace('real sociedad','real sociedad').replace('real betis','real betis').replace('real madrid','real madrid').replace('real valladolid','real valladolid').replace('rayo vallecano','rayo vallecano').replace('girona fc','girona').replace('getafe cf','getafe').replace('osasuna','osasuna').replace('sevilla fc','sevilla').replace('valencia cf','valencia').replace('villarreal cf','villarreal').replace('espanyol','espanyol').replace('las palmas','las palmas').replace('mallorca','mallorca').replace('leganés','leganés').replace('cádiz cf','cadiz').replace('granada cf','granada').replace('almería','almeria').strip(): name for name, _ in LALIGA_TEAMS}
    rows = []
    for file in files:
        df = pd.read_excel(file)
        team_name = os.path.basename(file).replace('Team Stats ','').replace('.xlsx','').strip()
        team_key = team_name.lower().replace('cf','').replace('fc','').replace('cd','').replace('ud','').replace('ca','').replace('rcd','').replace('athletic club','athletic bilbao').replace('atlético de madrid','atlético madrid').replace('deportivo alavés','alavés').replace('real sociedad','real sociedad').replace('real betis','real betis').replace('real madrid','real madrid').replace('real valladolid','real valladolid').replace('rayo vallecano','rayo vallecano').replace('girona fc','girona').replace('getafe cf','getafe').replace('osasuna','osasuna').replace('sevilla fc','sevilla').replace('valencia cf','valencia').replace('villarreal cf','villarreal').replace('espanyol','espanyol').replace('las palmas','las palmas').replace('mallorca','mallorca').replace('leganés','leganés').replace('cádiz cf','cadiz').replace('granada cf','granada').replace('almería','almeria').strip()
        display_name = team_map.get(team_key, team_name)
        # Leer solo la segunda fila (índice 0) que contiene los valores del equipo
        row_data = df.iloc[0]
        # Normalizar nombre si es uno de los casos especiales
        excel_row_team = str(row_data['Date']).strip()
        if excel_row_team in excel_name_map:
            display_name = excel_name_map[excel_row_team]
        # CP_succes/90: Recoveries high / Losses high
        losses_high = None
        recov_high = None
        if 'Losses / Low / Medium / High' in df.columns:
            try:
                losses_high = float(str(row_data['Losses / Low / Medium / High']).split('/')[0].replace(',','.'))
            except:
                losses_high = None
        if 'Recoveries / Low / Medium / High' in df.columns:
            try:
                recov_high = float(str(row_data['Recoveries / Low / Medium / High']).split('/')[0].replace(',','.'))
            except:
                recov_high = None
        cp_succes = recov_high / losses_high if losses_high and losses_high > 0 else None
        def get_first(col):
            if col in df.columns:
                try:
                    return float(str(row_data[col]).split('/')[0].replace(',','.'))
                except:
                    return None
            return None
        def get_val(col):
            if col in df.columns:
                try:
                    return float(str(row_data[col]).replace(',','.'))
                except:
                    return None
            return None
        row = {
            'Team': display_name,
            'PPDA/90': get_val('PPDA'),
            'CtrShots/90': get_val('Counterattacks / with shots'),
            'CP_succes/90': cp_succes,
            'ShotsOT/90': get_val('Shots / on target'),
            'DeepPass/90': get_first('Passes to final third / accurate'),
            'PSxGA/90': get_val('PSxGA'),
            'ProgPass/90': get_first('Progressive passes / accurate'),
            'xG/90': get_val('xG'),
        }
        if not per90:
            row = {
                'Team': display_name,
                'PPDA': row['PPDA/90'],
                'CtrShots': row['CtrShots/90'],
                'CP_succ': row['CP_succes/90'],
                'ShotsOT': row['ShotsOT/90'],
                'DeepPass': row['DeepPass/90'],
                'PSxGA': row['PSxGA/90'],
                'ProgPass': row['ProgPass/90'],
                'xG': row['xG/90'],
            }
        rows.append(row)
    return pd.DataFrame(rows)

# 4. Renderizado Streamlit
def main():
    st.set_page_config(page_title="Liga – Radar de Fases", layout="wide")
    st.title("⚽ Liga – Radar de Fases de Juego")
    
    # Selector de equipo
    team_names = [name for name, _ in LALIGA_TEAMS]
    selected_team = st.selectbox("Equipo a resaltar", team_names, index=0)

    # Selector de tipo de métrica
    tipo = st.radio(
        "Tipo de métrica",
        ["Por 90 minutos", "Media del año"],
        horizontal=True,
        index=0
    )
    per90 = tipo == "Por 90 minutos"
    df = load_laliga_team_stats(per90=per90)

    # Mini ranking interactivo
    st.subheader("Ranking Top 10 por métrica")
    if per90:
        metric_options = [
            ("PPDA/90", "PPDA/90"),
            ("CtrShots/90", "CtrShots/90"),
            ("CP_succes/90", "CP_succes/90"),
            ("ShotsOT/90", "ShotsOT/90"),
            ("DeepPass/90", "DeepPass/90"),
            ("PSxGA/90", "PSxGA/90"),
            ("ProgPass/90", "ProgPass/90"),
            ("xG/90", "xG/90"),
        ]
    else:
        metric_options = [
            ("PPDA", "PPDA"),
            ("CtrShots", "CtrShots"),
            ("CP_succ", "CP_succ"),
            ("ShotsOT", "ShotsOT"),
            ("DeepPass", "DeepPass"),
            ("PSxGA", "PSxGA"),
            ("ProgPass", "ProgPass"),
            ("xG", "xG"),
        ]
    metric_key = st.selectbox("Selecciona métrica para ranking", [m[1] for m in metric_options], index=0)
    metric_col = [m[0] for m in metric_options if m[1] == metric_key][0]
    # Ordenar ranking (mayor a menor, salvo PPDA y PSxGA que menor es mejor)
    asc_metrics = ["PPDA/90", "PPDA", "PSxGA/90", "PSxGA"]
    ascending = metric_col in asc_metrics
    top10 = df.sort_values(metric_col, ascending=ascending).head(10)
    # Mostrar ranking
    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
    for idx, (_, row) in enumerate(top10.iterrows()):
        logo_file = [logo for name, logo in LALIGA_TEAMS if name == row['Team']]
        logo_path = os.path.join(os.path.dirname(__file__), "..", "static", "logos", logo_file[0]) if logo_file else None
        if logo_file and os.path.exists(logo_path):
            with open(logo_path, "rb") as img_f:
                img_bytes = img_f.read()
                img_b64 = base64.b64encode(img_bytes).decode()
            logo_html = f"<img src='data:image/png;base64,{img_b64}' height='28' style='vertical-align:middle;margin-right:8px;'>"
        else:
            logo_html = ""
        highlight = "background:#ffe5f0;border-radius:8px;" if row['Team'] == selected_team else ""
        st.markdown(f"<div style='display:flex;align-items:center;{highlight}padding:4px 8px;margin-bottom:2px;'><span style='width:24px;font-weight:bold;'>{idx+1}</span>{logo_html}<span style='flex:1;'>{row['Team']}</span><span style='font-weight:bold;'>{row[metric_col]:.2f}</span></div>", unsafe_allow_html=True)

    colors = ["#1E88E5", "#43A047", "#FB8C00", "#8E24AA"]
    if per90:
        phases = [
            ("PPDA/90", "CtrShots/90", False,  "Transición ofensiva",
             "<b>Cuadrantes:</b><br>↖️ Presión baja, pocos contraataques<br>↗️ Presión baja, muchos contraataques<br>↙️ Presión alta, pocos contraataques<br>↘️ Presión alta, muchos contraataques"),
            ("CP_succes/90", "ShotsOT/90", False, "Transición defensiva",
             "<b>Cuadrantes:</b><br>↖️ Baja eficacia CP, pocos tiros recibidos<br>↗️ Alta eficacia CP, pocos tiros recibidos<br>↙️ Baja eficacia CP, muchos tiros recibidos<br>↘️ Alta eficacia CP, muchos tiros recibidos"),
            ("DeepPass/90", "PSxGA/90", False,  "Fase defensiva",
             "<b>Cuadrantes:</b><br>↖️ Pocos pases profundos, bajo PSxGA<br>↗️ Muchos pases profundos, bajo PSxGA<br>↙️ Pocos pases profundos, alto PSxGA<br>↘️ Muchos pases profundos, alto PSxGA"),
            ("ProgPass/90", "xG/90", False, "Fase ofensiva",
             "<b>Cuadrantes:</b><br>↖️ Pocos pases progresivos, bajo xG<br>↗️ Muchos pases progresivos, bajo xG<br>↙️ Pocos pases progresivos, alto xG<br>↘️ Muchos pases progresivos, alto xG"),
        ]
    else:
        phases = [
            ("PPDA", "CtrShots", False,  "Transición ofensiva",
             "<b>Cuadrantes:</b><br>↖️ Presión baja, pocos contraataques<br>↗️ Presión baja, muchos contraataques<br>↙️ Presión alta, pocos contraataques<br>↘️ Presión alta, muchos contraataques"),
            ("CP_succ", "ShotsOT", False, "Transición defensiva",
             "<b>Cuadrantes:</b><br>↖️ Baja eficacia CP, pocos tiros recibidos<br>↗️ Alta eficacia CP, pocos tiros recibidos<br>↙️ Baja eficacia CP, muchos tiros recibidos<br>↘️ Alta eficacia CP, muchos tiros recibidos"),
            ("DeepPass", "PSxGA", False,  "Fase defensiva",
             "<b>Cuadrantes:</b><br>↖️ Pocos pases profundos, bajo PSxGA<br>↗️ Muchos pases profundos, bajo PSxGA<br>↙️ Pocos pases profundos, alto PSxGA<br>↘️ Muchos pases profundos, alto PSxGA"),
            ("ProgPass", "xG", False, "Fase ofensiva",
             "<b>Cuadrantes:</b><br>↖️ Pocos pases progresivos, bajo xG<br>↗️ Muchos pases progresivos, bajo xG<br>↙️ Pocos pases progresivos, alto xG<br>↘️ Muchos pases progresivos, alto xG"),
        ]
    # Calcular rangos globales para cada métrica
    axis_ranges = {}
    for (x, y, inv, title, quad_legend), color in zip(phases, colors):
        x_min, x_max = df[x].min(), df[x].max()
        y_min, y_max = df[y].min(), df[y].max()
        x_margin = (x_max - x_min) * 0.1
        y_margin = (y_max - y_min) * 0.1
        axis_ranges[(x, y)] = ([x_min - x_margin, x_max + x_margin], [y_min - y_margin, y_max + y_margin])
    cols = st.columns(2)
    for i, ((x, y, inv, title, quad_legend), color) in enumerate(zip(phases, colors)):
        x_range, y_range = axis_ranges[(x, y)]
        fig = plot_phase_plotly(df, x, y, inv, title, color, x_range=x_range, y_range=y_range, selected_team=selected_team)
        with cols[i % 2]:
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main() 