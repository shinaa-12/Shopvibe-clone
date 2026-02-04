"""
Generate placeholder product images
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create images directory
images_dir = os.path.join('app1', 'static', 'images')
os.makedirs(images_dir, exist_ok=True)

# Product list with colors
products = [
    {'name': 'Laptop', 'color': (52, 73, 94)},      # Dark blue
    {'name': 'Phone', 'color': (155, 89, 182)},     # Purple
    {'name': 'Headphones', 'color': (231, 76, 60)}, # Red
    {'name': 'Tablet', 'color': (46, 204, 113)},    # Green
    {'name': 'Camera', 'color': (241, 196, 15)},    # Yellow
    {'name': 'Watch', 'color': (52, 152, 219)},     # Blue
]

# Generate images
for product in products:
    # Create image
    img = Image.new('RGB', (300, 300), color=product['color'])
    draw = ImageDraw.Draw(img)
    
    # Add text (product name)
    try:
        # Try to use a larger font
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        # Fall back to default font
        font = ImageFont.load_default()
    
    # Get text bounding box to center it
    text = product['name']
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (300 - text_width) // 2
    y = (300 - text_height) // 2
    
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Save image
    filename = product['name'].lower().replace(' ', '_') + '.png'
    filepath = os.path.join(images_dir, filename)
    img.save(filepath)
    print(f"Created: {filepath}")

print(f"\nAll images created in {images_dir}/")
