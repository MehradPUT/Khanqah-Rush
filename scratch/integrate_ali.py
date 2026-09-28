import os
from collections import deque
from PIL import Image, ImageDraw

def floodfill_bg(img, bg_target=(178, 177, 182), tol=18, extra_seeds=None):
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

def extract_ali_standing():
    art_path = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/original_ali_art.jpg'
    stand_art = Image.open(art_path).convert('RGBA')
    
    # Floor shadow cutoff at y=975 so feet are clean
    # Crop to y <= 975
    clean = floodfill_bg(stand_art, bg_target=(178, 177, 182), tol=18, extra_seeds=[(380, 480), (600, 480)])
    
    # Remove floor shadow below shoes: y > 975
    for y in range(976, clean.height):
        for x in range(clean.width):
            clean.putpixel((x, y), (0, 0, 0, 0))

    bbox = clean.getbbox()
    print('Ali standing bbox:', bbox)
    cropped = clean.crop(bbox)
    return cropped

def extract_ali_swing():
    art_path = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/ali_swing_1789653215837.jpg'
    swing_art = Image.open(art_path).convert('RGBA')
    
    # Extra seeds for gap between legs and above arms
    clean = floodfill_bg(swing_art, bg_target=(177, 176, 181), tol=18, extra_seeds=[(350, 750), (650, 450)])
    bbox = clean.getbbox()
    print('Ali swing bbox:', bbox)
    cropped = clean.crop(bbox)
    return cropped

def create_ali_standing_sprite(char_img):
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

    # Subtle cyan / gold architectural focus aura
    aura = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    aura_draw = ImageDraw.Draw(aura)
    aura_draw.ellipse([20, 10, 84, 196], fill=(52, 152, 219, 25), outline=(245, 176, 65, 90), width=1)
    sprite = Image.alpha_composite(sprite, aura)

    # Paste character
    sprite.paste(scaled_char, (paste_x, paste_y), scaled_char)
    return sprite

def create_ali_swing_sprite(char_img):
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

    # 3. Precision blueprint grid lines flying from axe strike
    # Geometric cyan architectural lines
    grid_lines = [
        [(150, 120), (175, 120)],
        [(155, 140), (174, 140)],
        [(160, 110), (160, 150)],
        [(170, 115), (170, 145)],
    ]
    for gl in grid_lines:
        draw.line(gl, fill=(52, 152, 219, 160), width=1)

    sprite.paste(scaled_char, (paste_x, paste_y), scaled_char)
    return sprite

def create_ali_defeat_sprite(char_img):
    canvas_w, canvas_h = 141, 170
    sprite = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound
    draw.rounded_rectangle([3, 130, 103, 170], radius=19, fill=(153, 204, 102, 255))

    # 2. Fallen Axe on right
    draw.rounded_rectangle([38, 127, 132, 139], radius=6, fill=(130, 95, 49, 255))
    draw.rectangle([111, 127, 141, 157], fill=(45, 50, 60, 255))
    draw.rectangle([111, 157, 141, 169], fill=(240, 242, 245, 255), outline=(170, 175, 185, 255))

    # 3. Slumped Black Dress Trousers
    draw.rounded_rectangle([24, 116, 68, 142], radius=6, fill=(30, 32, 42, 255))
    draw.rounded_rectangle([20, 134, 42, 154], radius=4, fill=(30, 32, 42, 255))
    draw.line([(24, 136), (24, 150)], fill=(45, 48, 60, 255), width=2)
    draw.rounded_rectangle([46, 134, 68, 154], radius=4, fill=(30, 32, 42, 255))
    draw.line([(50, 136), (50, 150)], fill=(45, 48, 60, 255), width=2)

    # 4. Brown Leather Dress Shoes
    draw.rounded_rectangle([18, 148, 42, 164], radius=3, fill=(55, 38, 38, 255))
    draw.rectangle([18, 158, 42, 164], fill=(35, 22, 22, 255))
    draw.rounded_rectangle([46, 148, 70, 164], radius=3, fill=(55, 38, 38, 255))
    draw.rectangle([46, 158, 70, 164], fill=(35, 22, 22, 255))

    # 5. Slumped Beige Blazer & Black Shirt
    # Black button-up center
    draw.rounded_rectangle([34, 60, 58, 120], radius=3, fill=(20, 20, 24, 255))
    # Belt with silver buckle
    draw.line([(32, 118), (60, 118)], fill=(15, 15, 18, 255), width=3)
    draw.rectangle([43, 116, 49, 120], fill=(220, 225, 230, 255))

    # Beige Blazer jacket sides and collar
    draw.rounded_rectangle([24, 58, 38, 120], radius=3, fill=(215, 185, 145, 255))
    draw.rounded_rectangle([54, 58, 68, 120], radius=3, fill=(215, 185, 145, 255))
    draw.polygon([(30, 58), (38, 88), (34, 100), (28, 58)], fill=(195, 165, 125, 255))
    draw.polygon([(62, 58), (54, 88), (58, 100), (64, 58)], fill=(195, 165, 125, 255))

    # Beige sleeves
    draw.rounded_rectangle([20, 60, 26, 82], radius=2, fill=(215, 185, 145, 255))
    draw.rounded_rectangle([66, 60, 72, 82], radius=2, fill=(215, 185, 145, 255))

    # Limp arms with wristwatch on right wrist
    draw.rounded_rectangle([19, 82, 25, 118], radius=3, fill=(223, 172, 155, 255))
    # Silver wristwatch on right wrist:
    draw.rectangle([18, 112, 26, 116], fill=(190, 195, 205, 255))
    draw.rounded_rectangle([67, 82, 73, 118], radius=3, fill=(223, 172, 155, 255))

    # 6. Knockout Head from authentic pixel-art model
    # Crop head: x: 140..340, y: 0..240 in char_img
    raw_head = char_img.crop((140, 0, 340, 240))
    target_h = 50
    target_w = int(raw_head.width * (target_h / raw_head.height))
    scaled_head = raw_head.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Draw knockout 'X' eyes on eyeglasses
    h_draw = ImageDraw.Draw(scaled_head)
    ex1, ey1 = int(target_w * 0.42), int(target_h * 0.42)
    ex2, ey2 = int(target_w * 0.70), int(target_h * 0.42)
    eye_col = (210, 45, 35, 255)
    for (ex, ey) in [(ex1, ey1), (ex2, ey2)]:
        h_draw.line([(ex - 3, ey - 3), (ex + 3, ey + 3)], fill=eye_col, width=2)
        h_draw.line([(ex - 3, ey + 3), (ex + 3, ey - 3)], fill=eye_col, width=2)

    # Dedicated canvas for rotation
    head_box_w = target_w + 30
    head_box_h = target_h + 30
    head_canvas = Image.new('RGBA', (head_box_w, head_box_h), (0, 0, 0, 0))
    head_canvas.paste(scaled_head, (15, 15), scaled_head)
    head_tilted = head_canvas.rotate(-10, resample=Image.Resampling.BICUBIC, expand=True)

    head_x = 46 - (head_tilted.width // 2)
    head_y = 12
    sprite.paste(head_tilted, (head_x, head_y), head_tilted)

    # 7. Dizzy Math & Architecture Symbols (📐, 📏, ✨)
    def draw_triangle_ruler(cx, cy, size):
        draw.polygon([(cx, cy - size), (cx + size, cy + size), (cx - size, cy + size)], outline=(52, 152, 219, 255), width=2)
        draw.polygon([(cx, cy - size//2), (cx + size//2, cy + size//2), (cx - size//2, cy + size//2)], fill=(22, 27, 34, 255))

    draw_triangle_ruler(32, 16, 7)
    
    # Golden dizzy stars
    def draw_star(cx, cy, r, color):
        pts = [
            (cx, cy - r), (cx + r*0.3, cy - r*0.3),
            (cx + r, cy), (cx + r*0.3, cy + r*0.3),
            (cx, cy + r), (cx - r*0.3, cy + r*0.3),
            (cx - r, cy), (cx - r*0.3, cy - r*0.3)
        ]
        draw.polygon(pts, fill=color)

    draw_star(58, 8, 6, (241, 196, 15, 255))
    draw_star(80, 16, 5, (52, 152, 219, 255))

    return sprite

def main():
    print('Extracting Ali standing and swing models...')
    stand_char = extract_ali_standing()
    swing_char = extract_ali_swing()
    print(f'Ali stand: {stand_char.size}, Ali swing: {swing_char.size}')

    os.makedirs('public/images', exist_ok=True)

    # 1. Standing sprite
    print('Generating ali_body.png...')
    body = create_ali_standing_sprite(stand_char)
    body.save('public/images/ali_body.png')

    # 2. Swinging sprite
    print('Generating ali_swing.png...')
    swing = create_ali_swing_sprite(swing_char)
    swing.save('public/images/ali_swing.png')

    # 3. Defeat sprite
    print('Generating ali_died.png...')
    died = create_ali_defeat_sprite(stand_char)
    died.save('public/images/ali_died.png')

    print('All 3 Ali sprites successfully created in public/images/!')

if __name__ == '__main__':
    main()
