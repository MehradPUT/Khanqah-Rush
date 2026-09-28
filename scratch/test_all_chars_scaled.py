import os
from PIL import Image, ImageDraw, ImageFont

art_dir = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64'
nima = Image.open('public/images/nima_body_young.png')
fargol = Image.open('public/images/fargol_body.png')
ali = Image.open('public/images/ali_body.png')
amir = Image.open('public/images/amirhossein_body.png')

font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_title = ImageFont.truetype(font_path, 16)
font_sub = ImageFont.truetype(font_path, 12)
font_lbl = ImageFont.truetype(font_path, 11)

w, h = 880, 420
img = Image.new('RGBA', (w, h), (18, 24, 38, 255))
draw = ImageDraw.Draw(img)

draw.rectangle([0, 0, w, 50], fill=(12, 16, 26, 255))
draw.text((20, 10), 'All 4 Characters at +30% Scale (139px Height)', font=font_title, fill=(255, 255, 255, 255))
draw.text((20, 30), 'Crisp pixel details, grounded stance, and balanced tree proportions', font=font_sub, fill=(180, 190, 205, 255))

chars = [
    ('Nima (Young)', nima, 110, (0, 229, 255, 255)),
    ('Fargol (Sultan)', fargol, 330, (255, 61, 0, 255)),
    ('Ali (Architect)', ali, 550, (255, 152, 0, 255)),
    ('Amirhossein (2X)', amir, 770, (41, 128, 185, 255))
]

ground_y = 350
target_h = 139

for name, sprite, cx, border_col in chars:
    bx1 = cx - 100
    bx2 = cx + 100
    draw.rounded_rectangle([bx1, 60, bx2, 395], radius=12, fill=(24, 32, 48, 220), outline=border_col, width=2)
    draw.text((bx1 + 12, 70), name, font=font_lbl, fill=border_col)
    
    # Ground
    draw.line([(bx1 + 8, ground_y), (bx2 - 8, ground_y)], fill=(133, 184, 82, 255), width=3)
    
    scale_factor = target_h / 214.0
    sw = int(sprite.width * scale_factor)
    scaled_sp = sprite.resize((sw, target_h), Image.Resampling.LANCZOS)
    
    px = cx - sw // 2
    py = ground_y - target_h
    img.paste(scaled_sp, (px, py), scaled_sp)

out_path = os.path.join(art_dir, 'all_characters_scaled_preview.png')
img.save(out_path)
print(f'Saved preview to {out_path}')
