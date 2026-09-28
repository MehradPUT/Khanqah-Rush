import os
from PIL import Image, ImageDraw, ImageFont

art_dir = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64'
os.makedirs(art_dir, exist_ok=True)

amir = Image.open('public/images/amirhossein_body.png')
nima = Image.open('public/images/nima_body_young.png')
fargol = Image.open('public/images/fargol_body.png')
ali = Image.open('public/images/ali_body.png')

font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_title = ImageFont.truetype(font_path, 16)
font_sub = ImageFont.truetype(font_path, 12)
font_lbl = ImageFont.truetype(font_path, 11)

# Canvas: 4 columns
w, h = 880, 500
img = Image.new('RGBA', (w, h), (18, 24, 38, 255))
draw = ImageDraw.Draw(img)

draw.rectangle([0, 0, w, 55], fill=(12, 16, 26, 255))
draw.text((20, 12), 'Character Size Comparison (بررسی سایز کاراکترها)', font=font_title, fill=(255, 255, 255, 255))
draw.text((20, 34), 'Current (107px) vs +25% (134px) vs +40% (150px) vs +50% (160px)', font=font_sub, fill=(180, 190, 205, 255))

scales = [
    ('Current (1.0x / 107px)', 107, 110),
    ('+25% (1.25x / 134px)', 134, 330),
    ('+40% (1.40x / 150px)', 150, 550),
    ('+50% (1.50x / 160px)', 160, 770)
]

ground_y = 420

for title, target_h, center_x in scales:
    col_x1 = center_x - 100
    col_x2 = center_x + 100
    draw.rounded_rectangle([col_x1, 65, col_x2, 475], radius=12, fill=(24, 32, 48, 220), outline=(50, 65, 95, 255), width=1)
    draw.text((col_x1 + 10, 75), title, font=font_lbl, fill=(245, 176, 65, 255))
    
    # Ground
    draw.line([(col_x1 + 8, ground_y), (col_x2 - 8, ground_y)], fill=(133, 184, 82, 255), width=3)
    
    # Tree trunk
    trunk_w = 45
    trunk_x = center_x + 25
    draw.rectangle([trunk_x, 95, trunk_x + trunk_w, ground_y], fill=(130, 95, 49, 255))
    
    # Branch at y = 180 (approaching)
    draw.rectangle([trunk_x - 65, 180, trunk_x, 225], fill=(120, 85, 40, 255))
    draw.ellipse([trunk_x - 75, 165, trunk_x - 20, 215], fill=(100, 150, 60, 255))

    # Scale Amirhossein
    scale_factor = target_h / 214.0
    scaled_w = int(amir.width * scale_factor)
    scaled_amir = amir.resize((scaled_w, target_h), Image.Resampling.LANCZOS)
    
    px = trunk_x - scaled_w - 5
    py = ground_y - target_h
    img.paste(scaled_amir, (px, py), scaled_amir)

out_path = os.path.join(art_dir, 'character_size_comparison.png')
img.save(out_path)
print(f'Saved comparison to {out_path}')
