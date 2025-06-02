import os
from PIL import Image
import shutil

def convert_to_png(input_path, output_path):
    """Convert an image to PNG format and save it with the correct name"""
    try:
        if input_path.lower().endswith('.png'):
            # If it's already a PNG, just copy it
            shutil.copy2(input_path, output_path)
        else:
            # Convert to PNG
            with Image.open(input_path) as img:
                # Convert RGBA if necessary
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                img.save(output_path, 'PNG')
        print(f"Converted: {output_path}")
        return True
    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")
        return False

def normalize_filename(filename):
    """Convert filename to lowercase and replace spaces with underscores"""
    return filename.lower().replace(' ', '_')

def process_images():
    # Define directories
    base_dir = r'C:\Users\zyadb\MASTER\REORGANIZACION\assets'
    team_logos_dir = os.path.join(base_dir, 'logos equipos')
    league_logos_dir = os.path.join(base_dir, 'logos ligas')
    barca_players_dir = os.path.join(base_dir, 'Imaganes Jugadores Barça')
    bayern_players_dir = os.path.join(base_dir, 'Imagenes Jugadores Bayern')
    
    # Output directories
    static_dir = 'static'
    logos_dir = os.path.join(static_dir, 'logos')
    leagues_dir = os.path.join(static_dir, 'leagues')
    players_dir = os.path.join(static_dir, 'players')

    # Create output directories if they don't exist
    os.makedirs(logos_dir, exist_ok=True)
    os.makedirs(leagues_dir, exist_ok=True)
    os.makedirs(players_dir, exist_ok=True)

    print("\nDirectorios de origen:")
    print(f"Logos de equipos: {team_logos_dir}")
    print(f"Logos de ligas: {league_logos_dir}")
    print(f"Jugadores Barça: {barca_players_dir}")
    print(f"Jugadores Bayern: {bayern_players_dir}")
    
    # Process team logos
    if os.path.exists(team_logos_dir):
        print("\nProcessing team logos...")
        for root, dirs, files in os.walk(team_logos_dir):
            for filename in files:
                if '.ipynb_checkpoints' in root:
                    continue
                if any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
                    input_path = os.path.join(root, filename)
                    base_name = os.path.splitext(filename)[0]
                    normalized_name = normalize_filename(base_name) + '.png'
                    output_path = os.path.join(logos_dir, normalized_name)
                    convert_to_png(input_path, output_path)

    # Process league logos
    if os.path.exists(league_logos_dir):
        print("\nProcessing league logos...")
        for filename in os.listdir(league_logos_dir):
            if any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
                input_path = os.path.join(league_logos_dir, filename)
                base_name = os.path.splitext(filename)[0]
                normalized_name = normalize_filename(base_name) + '.png'
                output_path = os.path.join(leagues_dir, normalized_name)
                convert_to_png(input_path, output_path)

    # Process Barça player images
    if os.path.exists(barca_players_dir):
        print("\nProcessing Barça player images...")
        for filename in os.listdir(barca_players_dir):
            if any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
                input_path = os.path.join(barca_players_dir, filename)
                base_name = os.path.splitext(filename)[0]
                normalized_name = normalize_filename(base_name) + '.png'
                output_path = os.path.join(players_dir, normalized_name)
                convert_to_png(input_path, output_path)
    else:
        print(f"\nBarça players directory not found at: {barca_players_dir}")

    # Process Bayern player images
    if os.path.exists(bayern_players_dir):
        print("\nProcessing Bayern player images...")
        for filename in os.listdir(bayern_players_dir):
            if any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
                input_path = os.path.join(bayern_players_dir, filename)
                base_name = os.path.splitext(filename)[0]
                normalized_name = normalize_filename(base_name) + '.png'
                output_path = os.path.join(players_dir, normalized_name)
                convert_to_png(input_path, output_path)
                print(f"Processed Bayern player: {filename} -> {normalized_name}")
    else:
        print(f"\nBayern players directory not found at: {bayern_players_dir}")

if __name__ == '__main__':
    print("Starting image conversion process...")
    process_images()
    print("\nConversion process completed!") 