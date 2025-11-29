"""
Script pour créer un favicon avec les lettres "Ben"
"""
from PIL import Image, ImageDraw, ImageFont
import os

output_favicon = "static/favicon.ico"

# Créer une image de base (256x256 pour haute qualité)
size = 256
img = Image.new('RGB', (size, size), color='#6366f1')  # Fond violet/bleu

# Créer un objet de dessin
draw = ImageDraw.Draw(img)

# Essayer de charger une police système, sinon utiliser la police par défaut
try:
    # Taille de police adaptée
    font = ImageFont.truetype("arial.ttf", 140)
except:
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 140)
    except:
        # Si aucune police trouvée, utiliser la police par défaut
        font = ImageFont.load_default()

# Texte à afficher
text = "Ben"

# Obtenir les dimensions du texte pour le centrer
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Calculer la position pour centrer le texte
x = (size - text_width) // 2 - bbox[0]
y = (size - text_height) // 2 - bbox[1]

# Dessiner le texte en blanc
draw.text((x, y), text, fill='white', font=font)

# Créer les différentes tailles pour le favicon
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save(
    output_favicon,
    format='ICO',
    sizes=sizes
)

print(f"✅ Favicon créé: {output_favicon}")
print(f"   Texte: 'Ben' en blanc sur fond violet")
print(f"   Tailles incluses: {sizes}")
