import os
import base64
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from unidecode import unidecode
from fuzzywuzzy import fuzz
import re

class PlayerPhotoManager:
    def __init__(self, photos_dir="static/players_photos"):
        self.photos_dir = photos_dir
        self.cache = {}
        self.available_photos = self._scan_available_photos()
        
        # Mapeos manuales para casos especiales
        self.manual_mappings = {
            'robert lewandowski': 'Robert Lewandowski.png',
            'lewandowski': 'Robert Lewandowski.png',
            'erling haaland': 'Erling Haaland.png',
            'haaland': 'Erling Haaland.png',
            'kylian mbappe': 'Kylian Mbappé.png',
            'mbappe': 'Kylian Mbappé.png',
            'pedri': 'Pedri.png',
            'pedri gonzalez': 'Pedri.png',
            'jude bellingham': 'Jude Bellingham.png',
            'bellingham': 'Jude Bellingham.png',
            'vinicius jr': 'Vinicius Jr.png',
            'vinicius junior': 'Vinicius Jr.png',
            'vini jr': 'Vinicius Jr.png',
            'luka modric': 'Luka Modrić.png',
            'modric': 'Luka Modrić.png',
            'karim benzema': 'Karim Benzema.png',
            'benzema': 'Karim Benzema.png',
            'toni kroos': 'Toni Kroos.png',
            'kroos': 'Toni Kroos.png',
            'casemiro': 'Casemiro.png',
            'sergio ramos': 'Sergio Ramos.png',
            'ramos': 'Sergio Ramos.png',
            'virgil van dijk': 'Virgil van Dijk.png',
            'van dijk': 'Virgil van Dijk.png',
            'mohamed salah': 'Mohamed Salah.png',
            'salah': 'Mohamed Salah.png',
            'sadio mane': 'Sadio Mané.png',
            'mane': 'Sadio Mané.png',
            'kevin de bruyne': 'Kevin De Bruyne.png',
            'de bruyne': 'Kevin De Bruyne.png',
            'raheem sterling': 'Raheem Sterling.png',
            'sterling': 'Raheem Sterling.png',
            'harry kane': 'Harry Kane.png',
            'kane': 'Harry Kane.png',
            'son heung-min': 'Son Heung-min.png',
            'son': 'Son Heung-min.png',
            'bruno fernandes': 'Bruno Fernandes.png',
            'fernandes': 'Bruno Fernandes.png',
            'marcus rashford': 'Marcus Rashford.png',
            'rashford': 'Marcus Rashford.png',
            'jadon sancho': 'Jadon Sancho.png',
            'sancho': 'Jadon Sancho.png',
            'phil foden': 'Phil Foden.png',
            'foden': 'Phil Foden.png',
            'jack grealish': 'Jack Grealish.png',
            'grealish': 'Jack Grealish.png',
            'declan rice': 'Declan Rice.png',
            'rice': 'Declan Rice.png',
            'mason mount': 'Mason Mount.png',
            'mount': 'Mason Mount.png',
            'bukayo saka': 'Bukayo Saka.png',
            'saka': 'Bukayo Saka.png'
        }
    
    def _scan_available_photos(self):
        """Escanea el directorio de fotos y devuelve lista de archivos disponibles"""
        if not os.path.exists(self.photos_dir):
            return []
        
        photos = []
        for file in os.listdir(self.photos_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                photos.append(file)
        return photos
    
    def normalize_name(self, name):
        """Normaliza nombres para hacer matching"""
        if not name:
            return ""
        
        # Convertir a minúsculas y quitar espacios extra
        normalized = str(name).lower().strip()
        
        # Quitar acentos usando unidecode
        normalized = unidecode(normalized)
        
        # Quitar caracteres especiales pero mantener espacios
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Quitar espacios múltiples
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def find_photo(self, player_name):
        """Encuentra la foto de un jugador usando múltiples estrategias"""
        if not player_name:
            return None
        
        # Normalizar nombre del jugador
        normalized_name = self.normalize_name(player_name)
        
        # Estrategia 1: Mapeo manual
        if normalized_name in self.manual_mappings:
            photo_file = self.manual_mappings[normalized_name]
            if photo_file in self.available_photos:
                return photo_file
        
        # Estrategia 2: Búsqueda exacta
        for photo in self.available_photos:
            photo_name = self.normalize_name(photo.replace('.png', '').replace('.jpg', '').replace('.jpeg', ''))
            if photo_name == normalized_name:
                return photo
        
        # Estrategia 3: Búsqueda por apellidos
        name_parts = normalized_name.split()
        if len(name_parts) > 1:
            for photo in self.available_photos:
                photo_name = self.normalize_name(photo.replace('.png', '').replace('.jpg', '').replace('.jpeg', ''))
                # Verificar si algún apellido coincide
                for part in name_parts[1:]:  # Omitir el primer nombre
                    if part in photo_name:
                        return photo
        
        # Estrategia 4: Búsqueda fuzzy
        best_match = None
        best_score = 0
        
        for photo in self.available_photos:
            photo_name = self.normalize_name(photo.replace('.png', '').replace('.jpg', '').replace('.jpeg', ''))
            score = fuzz.ratio(normalized_name, photo_name)
            
            if score > best_score and score > 80:  # Umbral de similitud
                best_score = score
                best_match = photo
        
        return best_match
    
    def create_placeholder(self, player_name, size=(80, 80)):
        """Crea un placeholder con las iniciales del jugador"""
        # Obtener iniciales
        name_parts = player_name.split()
        if len(name_parts) >= 2:
            initials = f"{name_parts[0][0]}{name_parts[-1][0]}".upper()
        elif len(name_parts) == 1:
            initials = name_parts[0][:2].upper()
        else:
            initials = "??"
        
        # Crear imagen
        img = Image.new('RGB', size, color='#004D98')
        draw = ImageDraw.Draw(img)
        
        # Intentar usar una fuente, si no usar la default
        try:
            font_size = max(size[0] // 3, 20)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Calcular posición del texto
        if font:
            bbox = draw.textbbox((0, 0), initials, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width = len(initials) * 10
            text_height = 15
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # Dibujar texto
        draw.text((x, y), initials, fill='white', font=font)
        
        return img
    
    def get_player_photo_base64(self, player_name, size=(80, 80)):
        """Obtiene la foto del jugador en formato base64"""
        cache_key = f"{player_name}_{size[0]}x{size[1]}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Buscar foto
        photo_file = self.find_photo(player_name)
        
        if photo_file:
            # Cargar foto real
            photo_path = os.path.join(self.photos_dir, photo_file)
            try:
                img = Image.open(photo_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
            except Exception:
                # Si hay error cargando la foto, crear placeholder
                img = self.create_placeholder(player_name, size)
        else:
            # Crear placeholder
            img = self.create_placeholder(player_name, size)
        
        # Convertir a base64
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Guardar en caché
        self.cache[cache_key] = img_base64
        
        return img_base64
    
    def get_stats(self):
        """Obtiene estadísticas del gestor de fotos"""
        return {
            'total_photos': len(self.available_photos),
            'manual_mappings': len(self.manual_mappings),
            'cache_size': len(self.cache)
        }

# Función para obtener el gestor de fotos (singleton)
@st.cache_resource
def get_photo_manager():
    return PlayerPhotoManager() 