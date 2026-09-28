import os
from collections import deque
from PIL import Image, ImageDraw

def floodfill_bg(img, bg_target=(182, 181, 186), tol=18, extra_seeds=None):
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

def extract_nima_models():
    art_old_path = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/.user_uploaded/media_1789650408937.jpg'
    art_young_path = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/.user_uploaded/media_1789650408964.jpg'

    old_art = Image.open(art_old_path).convert('RGBA')
    young_art = Image.open(art_young_path).convert('RGBA')

    # 1. Clean Old Character
    old_clean = floodfill_bg(old_art, bg_target=(182, 181, 186), tol=18, extra_seeds=[(400, 500)])
    bbox_old = (263, 33, 819, 1023)
    old_char = old_clean.crop(bbox_old)

    # 2. Clean Young Upper Body (head, goatee, necklace, unobstructed tricolor chest)
    # Background in young_art around upper body is (183, 184, 189)
    young_clean = floodfill_bg(young_art, bg_target=(183, 184, 189), tol=18, extra_seeds=[(400, 500)])
    young_upper = young_clean.crop((263, 33, 819, 640))

    # 3. Composite Young Full Character (young upper over clean lower body)
    young_char = old_char.copy()
    young_char.paste(young_upper, (0, 0), young_upper)

    return old_char, young_char

def draw_sparkle(draw, cx, cy, size, color=(255, 255, 255, 255)):
    r = size
    inner = max(1, size // 4)
    points = [
        (cx, cy - r), (cx + inner, cy - inner),
        (cx + r, cy), (cx + inner, cy + inner),
        (cx, cy + r), (cx - inner, cy + inner),
        (cx - r, cy), (cx - inner, cy - inner)
    ]
    draw.polygon(points, fill=color)
    draw.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=(255, 255, 255, 255))

def create_standing_sprite(char_img, is_young=False):
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

    # Placement
    paste_x = 2
    paste_y = 12

    # 3. If Young Nima: draw fiery / golden Youth Rejuvenation aura behind
    if is_young:
        aura = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
        aura_draw = ImageDraw.Draw(aura)
        aura_draw.ellipse([14, 8, 90, 196], fill=(231, 76, 60, 45), outline=(243, 156, 18, 120), width=2)
        aura_draw.ellipse([22, 16, 82, 180], fill=(241, 196, 15, 35))
        sprite = Image.alpha_composite(sprite, aura)
        draw = ImageDraw.Draw(sprite)

    # 4. Paste character
    sprite.paste(scaled_char, (paste_x, paste_y), scaled_char)

    # 5. If Young Nima: add radiant golden & emerald sparkles
    if is_young:
        sparkles = [
            (14, 22, 5, (241, 196, 15, 255)),
            (90, 18, 6, (241, 196, 15, 255)),
            (52, 6, 4, (255, 255, 255, 255)),
            (10, 68, 5, (46, 204, 113, 255)),
            (94, 72, 5, (243, 156, 18, 255)),
            (12, 115, 5, (241, 196, 15, 255)),
            (92, 120, 6, (241, 196, 15, 255)),
            (16, 162, 4, (255, 255, 255, 255)),
            (88, 165, 5, (46, 204, 113, 255)),
        ]
        for sx, sy, sz, sc in sparkles:
            draw_sparkle(draw, sx, sy, sz, sc)

    return sprite

def create_defeat_sprite(char_img, is_old=False):
    canvas_w, canvas_h = 141, 170
    sprite = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound
    draw.rounded_rectangle([3, 130, 103, 170], radius=19, fill=(153, 204, 102, 255))

    # 2. Fallen Axe on right
    draw.rounded_rectangle([38, 127, 132, 139], radius=6, fill=(130, 95, 49, 255))
    draw.rectangle([111, 127, 141, 157], fill=(45, 50, 60, 255))
    draw.rectangle([111, 157, 141, 169], fill=(240, 242, 245, 255), outline=(170, 175, 185, 255))

    # 3. Slumped Blue Jeans
    draw.rounded_rectangle([24, 116, 68, 142], radius=6, fill=(43, 96, 138, 255))
    draw.rounded_rectangle([20, 134, 42, 154], radius=4, fill=(43, 96, 138, 255))
    draw.line([(24, 136), (24, 150)], fill=(59, 130, 182, 255), width=2)
    draw.rounded_rectangle([46, 134, 68, 154], radius=4, fill=(43, 96, 138, 255))
    draw.line([(50, 136), (50, 150)], fill=(59, 130, 182, 255), width=2)

    # 4. Dark Sneakers with White Soles
    draw.rounded_rectangle([18, 148, 42, 164], radius=3, fill=(26, 26, 26, 255))
    draw.rectangle([18, 158, 42, 164], fill=(245, 245, 245, 255))
    draw.rounded_rectangle([46, 148, 70, 164], radius=3, fill=(26, 26, 26, 255))
    draw.rectangle([46, 158, 70, 164], fill=(245, 245, 245, 255))

    # 5. Tricolor T-shirt (slumped torso)
    draw.rounded_rectangle([28, 89, 64, 120], radius=3, fill=(120, 120, 128, 255))
    draw.line([(28, 119), (64, 119)], fill=(85, 85, 92, 255), width=2)
    draw.rounded_rectangle([28, 58, 64, 81], radius=3, fill=(22, 22, 24, 255))
    draw.rectangle([28, 81, 64, 89], fill=(248, 248, 250, 255))
    draw.line([(28, 81), (64, 81)], fill=(180, 180, 185, 255), width=1)
    draw.line([(28, 89), (64, 89)], fill=(140, 140, 145, 255), width=1)

    draw.rounded_rectangle([22, 60, 28, 80], radius=2, fill=(22, 22, 24, 255))
    draw.rounded_rectangle([64, 60, 70, 80], radius=2, fill=(22, 22, 24, 255))

    draw.rounded_rectangle([21, 80, 27, 118], radius=3, fill=(223, 172, 155, 255))
    draw.rounded_rectangle([65, 80, 71, 118], radius=3, fill=(223, 172, 155, 255))
    draw.rounded_rectangle([19, 115, 27, 128], radius=4, fill=(223, 172, 155, 255))
    draw.rounded_rectangle([65, 115, 73, 128], radius=4, fill=(223, 172, 155, 255))

    # 6. Knockout Head from authentic pixel-art model
    if is_old:
        raw_head = char_img.crop((140, 0, 390, 490))
        target_h = 76
        target_w = int(raw_head.width * (target_h / raw_head.height))
        scaled_head = raw_head.resize((target_w, target_h), Image.Resampling.LANCZOS)
    else:
        raw_head = char_img.crop((140, 0, 390, 270))
        target_h = 48
        target_w = int(raw_head.width * (target_h / raw_head.height))
        scaled_head = raw_head.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Draw knockout 'X' eyes on the scaled head
    h_draw = ImageDraw.Draw(scaled_head)
    ex1, ey1 = int(target_w * 0.40), int(target_h * 0.28) if is_old else int(target_h * 0.42)
    ex2, ey2 = int(target_w * 0.70), int(target_h * 0.28) if is_old else int(target_h * 0.42)
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
    head_y = 4 if is_old else 16
    sprite.paste(head_tilted, (head_x, head_y), head_tilted)

    # 7. Dizzy Stars circling above
    def draw_star(cx, cy, r, color):
        pts = [
            (cx, cy - r), (cx + r*0.3, cy - r*0.3),
            (cx + r, cy), (cx + r*0.3, cy + r*0.3),
            (cx, cy + r), (cx - r*0.3, cy + r*0.3),
            (cx - r, cy), (cx - r*0.3, cy - r*0.3)
        ]
        draw.polygon(pts, fill=color)

    draw_star(32, 14, 6, (241, 196, 15, 255))
    draw_star(58, 8, 7, (243, 156, 18, 255))
    draw_star(78, 16, 5, (241, 196, 15, 255))

    return sprite

def main():
    print('Extracting Nima pixel art models...')
    old_char, young_char = extract_nima_models()
    print(f'Old char model: {old_char.size}, Young char model: {young_char.size}')

    os.makedirs('public/images', exist_ok=True)

    # 1. Standing sprites
    print('Generating nima_body_old.png...')
    body_old = create_standing_sprite(old_char, is_young=False)
    body_old.save('public/images/nima_body_old.png')

    print('Generating nima_body_young.png...')
    body_young = create_standing_sprite(young_char, is_young=True)
    body_young.save('public/images/nima_body_young.png')

    # 2. Defeat sprites
    print('Generating nima_died_old.png...')
    died_old = create_defeat_sprite(old_char, is_old=True)
    died_old.save('public/images/nima_died_old.png')

    print('Generating nima_died_young.png...')
    died_young = create_defeat_sprite(young_char, is_old=False)
    died_young.save('public/images/nima_died_young.png')

    print('All 4 Nima sprites successfully created in public/images/!')

if __name__ == '__main__':
    main()
