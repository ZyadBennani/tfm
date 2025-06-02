import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes."""
    # Calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):
        name = 'radar'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')

        def fill(self, *args, **kwargs):
            """Override fill so that line is closed by default"""
            closed = kwargs.pop('closed', True)
            return super().fill(*args, closed=closed, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            closed = kwargs.pop('closed', True)
            return super().plot(*args, closed=closed, **kwargs)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            x0, y0 = (0.5, 0.5)
            r = 0.5
            if frame == 'circle':
                return Circle((x0, y0), r)
            elif frame == 'polygon':
                return RegularPolygon((x0, y0), num_vars, radius=r, orientation=0)
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                spine_type = 'circle'
                verts = unit_poly_verts(num_vars)
                verts.append(verts[0])
                path = Path(verts)
                spine = Spine(self, spine_type, path)
                spine.set_transform(self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta

def unit_poly_verts(num_vars):
    """Return vertices of polygon for subplot axes."""
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
    verts = [(0.5 * np.cos(t) + 0.5, 0.5 * np.sin(t) + 0.5) for t in theta]
    return verts

def create_radar_chart(ax, angles, values, labels, color, alpha, title):
    """Plot the radar chart."""
    angles = np.concatenate((angles, [angles[0]]))  # complete the circle
    values = np.concatenate((values, [values[0]]))

    # Plot data
    ax.plot(angles, values, 'o-', linewidth=2.5, color=color, alpha=0.25)
    ax.fill(angles, values, color=color, alpha=alpha)

    # Fix axis to go in the right order and start at 12 o'clock
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Draw axis lines for each angle and label
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)

    # Go through labels and adjust alignment based on where it is in the circle
    for label, angle in zip(ax.get_xticklabels(), angles):
        if angle in (0, np.pi):
            label.set_horizontalalignment('center')
        elif 0 < angle < np.pi:
            label.set_horizontalalignment('left')
        else:
            label.set_horizontalalignment('right')

    # Set chart title with custom font
    ax.set_title(title, y=1.08, fontsize=14, fontweight='bold')

    # Add alternating background colors
    ax.set_facecolor('#f0f0f0')
    ax.grid(True, color='white', linestyle='-', linewidth=1.5)

    # Add radial labels
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"],
               color="grey", size=8)

def plot_player_comparison(player1, player2, data, output_dir='graficos_radar'):
    """Create a radar chart comparing two players."""
    # Ensure output directory exists
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get player data
    p1_data = data[data['Jugador'] == player1].iloc[0]
    p2_data = data[data['Jugador'] == player2].iloc[0]

    # Get metrics and values
    metrics = []
    p1_values = []
    p2_values = []

    for i in range(1, 10):  # Assuming maximum 9 metrics per player
        metric_col = f'Metrica {i}'
        value_col = f'Valor Normalizado {i}'
        
        if metric_col in data.columns and value_col in data.columns:
            metric = p1_data[metric_col]
            if pd.notna(metric):  # Only include non-null metrics
                metrics.append(metric)
                p1_values.append(float(p1_data[value_col]))
                p2_values.append(float(p2_data[value_col]))

    num_vars = len(metrics)
    if num_vars < 3:
        print(f"Not enough metrics for {player1} vs {player2}")
        return

    # Set up the figure with style
    plt.style.use('seaborn')
    fig = plt.figure(figsize=(12, 8))
    fig.patch.set_facecolor('white')

    # Create the radar chart
    angles = radar_factory(num_vars, frame='polygon')
    ax = fig.add_subplot(111, projection='radar')

    # Plot the two players
    create_radar_chart(ax, angles, p1_values, metrics, '#1f77b4', 0.25,
                      f'{player1} ({p1_data["Equipo"]}) vs\n{player2} ({p2_data["Equipo"]})')
    create_radar_chart(ax, angles, p2_values, metrics, '#ff7f0e', 0.25, '')

    # Add a legend
    plt.legend([player1, player2], loc='upper right',
               bbox_to_anchor=(0.1, 0.1))

    # Set chart limits
    ax.set_ylim(0, 100)

    # Save the figure
    filename = f"{output_dir}/{player1.replace(' ', '_')}_vs_{player2.replace(' ', '_')}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def main():
    # Read the normalized data
    data = pd.read_csv('Datos/radares_normalizados.csv', sep=';')

    # Define player comparisons by position
    comparisons = [
        ('Manuel Neuer', 'Wojciech Szczesny'),  # GK
        ('Benjamin Pavard', 'Jules Kounde'),    # RB
        ('Jerome Boateng', 'Pau Cubarsi'),      # CB
        ('David Alaba', 'Inigo Martinez'),      # CB
        ('Alphonso Davies', 'Alejandro Balde'), # LB
        ('Joshua Kimmich', 'Frenkie De Jong'),  # CM-CDM
        ('Leon Goretzka', 'Pedri'),            # CM-CDM
        ('Thomas Muller', 'Dani Olmo'),        # CAM
        ('Kingsley Coman', 'Raphinha'),        # W
        ('Serge Gnabry', 'Lamine Yamal')       # W
    ]

    # Generate all comparison charts
    for player1, player2 in comparisons:
        print(f"Generating comparison: {player1} vs {player2}")
        plot_player_comparison(player1, player2, data)

if __name__ == "__main__":
    main() 