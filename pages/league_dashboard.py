import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import os

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
    ("Cádiz CF", "cadiz.png"),
    ("Granada CF", "granada.png"),
    ("Almería", "almeria.png"),
]

# 2. Datos ficticios reproducibles
def generate_fake_data():
    rng = np.random.default_rng(7)
    teams = [name for name, _ in LALIGA_TEAMS]
    n = len(teams)
    df = pd.DataFrame({
        "Team": teams,
        "PPDA": rng.uniform(5, 14, n),
        "CtrShots90": rng.uniform(0.2, 3.0, n),
        "LossHigh": rng.integers(25, 51, n),
        "RecovHigh": rng.integers(5, 31, n),
        "ShotsOT90": rng.uniform(1.5, 6.0, n),
        "DeepPass90": rng.uniform(6, 22, n),
        "PSxGA90": rng.uniform(0.6, 2.5, n),
        "ProgPass90": rng.uniform(15, 45, n),
        "xG90": rng.uniform(0.6, 2.2, n),
    })
    df["CP_succ"] = df["RecovHigh"] / df["LossHigh"]
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

# 4. Renderizado Streamlit
def main():
    st.set_page_config(page_title="Liga – Radar de Fases", layout="wide")
    st.title("⚽ Liga – Radar de Fases de Juego")
    df = generate_fake_data()

    colors = ["#1E88E5", "#43A047", "#FB8C00", "#8E24AA"]
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    phases = [
        ("PPDA", "CtrShots90", True,  "Transición ofensiva"),
        ("CP_succ", "ShotsOT90", False, "Transición defensiva"),
        ("DeepPass90", "PSxGA90", True,  "Fase defensiva"),
        ("ProgPass90", "xG90", False, "Fase ofensiva"),
    ]
    for ax, (x, y, inv, title), col in zip(axs.flatten(), phases, colors):
        plot_phase(ax, df, x, y, inv, title, col)

    plt.tight_layout()
    st.pyplot(fig)

if __name__ == "__main__":
    main() 