import os
from collections import deque
from PIL import Image, ImageDraw

def floodfill_bg(img, bg_target=(200, 200, 200), tol=20, extra_seeds=None):
    w, h = img.size
    visited = bytearray(w * h)
    q = deque()
    
    # Border seeds
    for x in range(w):
        q.append((x, 0))
        q.append((x, h - 1))
    for y in range(h):
        q.append((0, y))
        q.append((w - 1, y))
        
    if extra_seeds:
        for seed in extra_seeds:
            q.append(seed)
            
    def is_bg(c):
        return (abs(c[0] - bg_target[0]) <= tol and 
                abs(c[1] - bg_target[1]) <= tol and 
                abs(c[2] - bg_target[2]) <= tol)

    while q:
        x, y = q.popleft()
        idx = y * w + x
        if visited[idx]:
            continue
        visited[idx] = 1
        c = img.getpixel((x, y))
        if is_bg(c):
            if x > 0 and not visited[idx - 1]: q.append((x - 1, y))
            if x < w - 1 and not visited[idx + 1]: q.append((x + 1, y))
            if y > 0 and not visited[idx - w]: q.append((x, y - 1))
            if y < h - 1 and not visited[idx + w]: q.append((x, y + 1))

    clean = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            idx = y * w + x
            if not visited[idx]:
                clean.putpixel((x, y), img.getpixel((x, y)))
    return clean

def extract_amirhossein_standing():
    art_path = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/amirhossein_ref_crop.jpg'
    stand_art = Image.open(art_path).convert('RGBA')
    
    clean = floodfill_bg(stand_art, bg_target=(200, 201, 200), tol=20, extra_seeds=[(130, 480)])
    bbox = clean.getbbox()
    print('Amirhossein standing bbox:', bbox)
    cropped = clean.crop(bbox)
    return cropped

def extract_amirhossein_swing():
    art_path = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/original_amirhossein_swing.jpg'
    swing_art = Image.open(art_path).convert('RGBA')
    
    # Extra seeds for gap between legs and above arms
    clean = floodfill_bg(swing_art, bg_target=(198, 198, 198), tol=20, extra_seeds=[(450, 680), (600, 300)])
    bbox = clean.getbbox()
    print('Amirhossein swing bbox:', bbox)
    cropped = clean.crop(bbox)
    return cropped

def create_amirhossein_standing_sprite(char_img):
    canvas_w, canvas_h = 104, 214
    sprite = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound at bottom
    draw.rounded_rectangle([2, 174, 102, 214], radius=19, fill=(153, 204, 102, 255))

    # 2. Scale character to height 184px (ground at y=196, head at y=12)
    target_h = 184
    scale = target_h / char_img.height
    target_w = int(char_img.width * scale)
    scaled_char = char_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    paste_x = (canvas_w - target_w) // 2 + 1
    paste_y = 12

    # Subtle royal-blue / gold 2X aura
    aura = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    aura_draw = ImageDraw.Draw(aura)
    aura_draw.ellipse([18, 10, 86, 196], fill=(41, 128, 185, 25), outline=(241, 196, 15, 85), width=1)
    sprite = Image.alpha_composite(sprite, aura)

    # Paste character
    sprite.paste(scaled_char, (paste_x, paste_y), scaled_char)
    return sprite

def create_amirhossein_swing_sprite(char_img):
    canvas_w, canvas_h = 176, 214
    sprite = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound across bottom
    draw.rounded_rectangle([2, 174, canvas_w - 2, 214], radius=19, fill=(153, 204, 102, 255))

    # 2. Scale character
    target_h = 176
    scale = target_h / char_img.height
    target_w = int(char_img.width * scale)
    scaled_char = char_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    paste_x = 0
    paste_y = 20

    # 3. Dynamic speed & 2X double impact arcs
    arcs = [
        [(145, 115), (175, 115)],
        [(150, 135), (174, 135)],
        [(155, 105), (155, 145)],
    ]
    for arc in arcs:
        draw.line(arc, fill=(241, 196, 15, 180), width=2)

    sprite.paste(scaled_char, (paste_x, paste_y), scaled_char)
    return sprite

def create_amirhossein_defeat_sprite(char_img):
    canvas_w, canvas_h = 141, 170
    sprite = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound
    draw.rounded_rectangle([3, 130, 103, 170], radius=19, fill=(153, 204, 102, 255))

    # 2. Fallen Axe on right
    draw.rounded_rectangle([38, 127, 132, 139], radius=6, fill=(130, 95, 49, 255))
    draw.rectangle([111, 127, 141, 157], fill=(45, 50, 60, 255))
    draw.rectangle([111, 157, 141, 169], fill=(240, 242, 245, 255), outline=(170, 175, 185, 255))

    # 3. Slumped Distressed Charcoal Jeans
    draw.rounded_rectangle([24, 116, 68, 142], radius=6, fill=(35, 40, 48, 255))
    draw.rounded_rectangle([20, 134, 42, 154], radius=4, fill=(35, 40, 48, 255))
    # Knee distress cuts
    draw.line([(25, 140), (33, 140)], fill=(65, 70, 80, 255), width=2)
    draw.rounded_rectangle([46, 134, 68, 154], radius=4, fill=(35, 40, 48, 255))
    draw.line([(51, 140), (59, 140)], fill=(65, 70, 80, 255), width=2)

    # 4. Clean White Low-Top Sneakers
    draw.rounded_rectangle([18, 148, 42, 164], radius=3, fill=(245, 245, 250, 255), outline=(180, 185, 195, 255))
    draw.rectangle([18, 160, 42, 164], fill=(70, 75, 85, 255))
    draw.rounded_rectangle([46, 148, 70, 164], radius=3, fill=(245, 245, 250, 255), outline=(180, 185, 195, 255))
    draw.rectangle([46, 160, 70, 164], fill=(70, 75, 85, 255))

    # 5. Slumped Royal Blue Oversized T-Shirt
    draw.rounded_rectangle([24, 60, 68, 122], radius=6, fill=(38, 75, 175, 255))
    # Sleeves
    draw.rounded_rectangle([18, 62, 26, 92], radius=3, fill=(38, 75, 175, 255))
    draw.rounded_rectangle([66, 62, 74, 92], radius=3, fill=(38, 75, 175, 255))
    # White cursive script text on chest
    draw.line([(34, 76), (58, 76)], fill=(245, 245, 255, 220), width=1)
    draw.line([(38, 80), (54, 80)], fill=(245, 245, 255, 180), width=1)
    # Silver chain necklace around neck collar
    draw.arc([38, 56, 54, 66], start=0, end=180, fill=(220, 225, 235, 255), width=2)

    # Bare forearms
    draw.rounded_rectangle([19, 92, 25, 120], radius=3, fill=(215, 160, 140, 255))
    draw.rounded_rectangle([67, 92, 73, 120], radius=3, fill=(215, 160, 140, 255))

    # 6. Knockout Head from authentic art
    # Crop head from char_img: x: 45..190, y: 0..170
    raw_head = char_img.crop((45, 0, 190, 170))
    target_h = 52
    target_w = int(raw_head.width * (target_h / raw_head.height))
    scaled_head = raw_head.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Draw knockout 'X' eyes
    h_draw = ImageDraw.Draw(scaled_head)
    ex1, ey1 = int(target_w * 0.40), int(target_h * 0.44)
    ex2, ey2 = int(target_w * 0.68), int(target_h * 0.44)
    eye_col = (231, 76, 60, 255)
    for (ex, ey) in [(ex1, ey1), (ex2, ey2)]:
        h_draw.line([(ex - 3, ey - 3), (ex + 3, ey + 3)], fill=eye_col, width=2)
        h_draw.line([(ex - 3, ey + 3), (ex + 3, ey - 3)], fill=eye_col, width=2)

    # Rotate head slightly
    head_box_w = target_w + 30
    head_box_h = target_h + 30
    head_canvas = Image.new('RGBA', (head_box_w, head_box_h), (0, 0, 0, 0))
    head_canvas.paste(scaled_head, (15, 15), scaled_head)
    head_tilted = head_canvas.rotate(-10, resample=Image.Resampling.BICUBIC, expand=True)

    head_x = 46 - (head_tilted.width // 2)
    head_y = 12
    sprite.paste(head_tilted, (head_x, head_y), head_tilted)

    # 7. Dizzy Stars & 2X Multiplier Symbol
    def draw_star(cx, cy, r, color):
        pts = [
            (cx, cy - r), (cx + r*0.3, cy - r*0.3),
            (cx + r, cy), (cx + r*0.3, cy + r*0.3),
            (cx, cy + r), (cx - r*0.3, cy + r*0.3),
            (cx - r, cy), (cx - r*0.3, cy - r*0.3)
        ]
        draw.polygon(pts, fill=color)

    draw_star(32, 16, 6, (241, 196, 15, 255))
    draw_star(62, 10, 5, (52, 152, 219, 255))
    draw_star(82, 18, 6, (241, 196, 15, 255))

    return sprite

def main():
    print('Extracting Amirhossein models...')
    stand_char = extract_amirhossein_standing()
    swing_char = extract_amirhossein_swing()
    print(f'Amirhossein stand: {stand_char.size}, Amirhossein swing: {swing_char.size}')

    os.makedirs('public/images', exist_ok=True)

    # 1. Standing sprite
    print('Generating amirhossein_body.png...')
    body = create_amirhossein_standing_sprite(stand_char)
    body.save('public/images/amirhossein_body.png')

    # 2. Swinging sprite
    print('Generating amirhossein_swing.png...')
    swing = create_amirhossein_swing_sprite(swing_char)
    swing.save('public/images/amirhossein_swing.png')

    # 3. Defeat sprite
    print('Generating amirhossein_died.png...')
    died = create_amirhossein_defeat_sprite(stand_char)
    died.save('public/images/amirhossein_died.png')

    print('All 3 Amirhossein sprites successfully created in public/images/!')

if __name__ == '__main__':
    main()
