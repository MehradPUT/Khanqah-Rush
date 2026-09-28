import os
from collections import deque
from PIL import Image, ImageDraw

def floodfill_clean(img_path, bg_target=(188, 188, 188), tol=20, extra_seeds=None):
    img = Image.open(img_path).convert('RGBA')
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
                c = img.getpixel((x, y))
                # Secondary cleanup of isolated bg pixels
                if is_bg(c):
                    continue
                clean.putpixel((x, y), c)
                
    bbox = clean.getbbox()
    print(f'Extracted {os.path.basename(img_path)} bbox: {bbox}')
    return clean.crop(bbox)

def create_standing_sprite(char_img):
    # Canvas enlarged to 144px to prevent any clipping of arms, shoulders, or axe handle
    canvas_w, canvas_h = 144, 214
    sprite = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound at bottom
    draw.rounded_rectangle([6, 174, 138, 214], radius=19, fill=(153, 204, 102, 255))

    # 2. Scale character to height 182px
    target_h = 182
    scale = target_h / char_img.height
    target_w = int(char_img.width * scale)
    scaled_char = char_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    paste_x = (canvas_w - target_w) // 2
    paste_y = 14

    # Subtle cozy lavender aura neatly contained
    aura = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    aura_draw = ImageDraw.Draw(aura)
    aura_draw.ellipse([8, 12, 136, 192], fill=(155, 89, 182, 25), outline=(142, 68, 173, 75), width=1)
    sprite = Image.alpha_composite(sprite, aura)

    # Paste character
    sprite.paste(scaled_char, (paste_x, paste_y), scaled_char)
    return sprite

def create_swing_sprite(char_img):
    # Canvas enlarged to 184px to prevent any clipping during chopping swing
    canvas_w, canvas_h = 184, 214
    sprite = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound across bottom
    draw.rounded_rectangle([2, 174, canvas_w - 2, 214], radius=19, fill=(153, 204, 102, 255))

    # 2. Scale character
    target_h = 176
    scale = target_h / char_img.height
    target_w = int(char_img.width * scale)
    scaled_char = char_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    paste_x = (canvas_w - target_w) // 2
    paste_y = 20

    sprite.paste(scaled_char, (paste_x, paste_y), scaled_char)
    return sprite

def create_sleep_sprite(char_img):
    # Canvas enlarged to 144px matching standing sprite
    canvas_w, canvas_h = 144, 214
    sprite = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound at bottom
    draw.rounded_rectangle([6, 174, 138, 214], radius=19, fill=(153, 204, 102, 255))

    # 2. Scale character in blanket
    target_h = 182
    scale = target_h / char_img.height
    target_w = int(char_img.width * scale)
    scaled_char = char_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    paste_x = (canvas_w - target_w) // 2
    paste_y = 14

    # Cozy dream aura (lavender glow)
    aura = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    aura_draw = ImageDraw.Draw(aura)
    aura_draw.ellipse([8, 12, 136, 192], fill=(142, 68, 173, 35), outline=(175, 122, 197, 100), width=1)
    sprite = Image.alpha_composite(sprite, aura)

    # Paste character
    sprite.paste(scaled_char, (paste_x, paste_y), scaled_char)

    # 3. Add glowing floating Zzz's
    zzz = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    z_draw = ImageDraw.Draw(zzz)
    # Z 1
    z_draw.line([(100, 32), (110, 32), (100, 42), (110, 42)], fill=(255, 235, 59, 255), width=2)
    # Z 2
    z_draw.line([(114, 20), (126, 20), (114, 30), (126, 30)], fill=(255, 235, 59, 230), width=2)
    # Z 3
    z_draw.line([(126, 8), (134, 8), (126, 16), (134, 16)], fill=(255, 235, 59, 180), width=1)
    sprite = Image.alpha_composite(sprite, zzz)

    return sprite

def create_defeat_sprite(stand_clean):
    canvas_w, canvas_h = 141, 170
    sprite = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound
    draw.rounded_rectangle([3, 130, 103, 170], radius=19, fill=(153, 204, 102, 255))

    # 2. Fallen Axe on right (keep x within 136 so it does not touch edge)
    draw.rounded_rectangle([38, 127, 126, 139], radius=6, fill=(130, 95, 49, 255))
    draw.rectangle([105, 127, 135, 157], fill=(45, 50, 60, 255))
    draw.rectangle([105, 157, 135, 169], fill=(240, 242, 245, 255), outline=(170, 175, 185, 255))

    # 3. Slumped Dark Jeans & Brown Boots
    draw.rounded_rectangle([18, 114, 82, 148], radius=6, fill=(35, 42, 52, 255))
    draw.rounded_rectangle([16, 132, 44, 154], radius=4, fill=(35, 42, 52, 255))
    draw.rounded_rectangle([54, 132, 82, 154], radius=4, fill=(35, 42, 52, 255))
    # Boots
    draw.rounded_rectangle([12, 148, 44, 166], radius=4, fill=(75, 50, 38, 255), outline=(45, 30, 22, 255))
    draw.rounded_rectangle([54, 148, 86, 166], radius=4, fill=(75, 50, 38, 255), outline=(45, 30, 22, 255))

    # 4. Slumped Upper Body & Plaid Jacket (cropped from unclipped stand_clean)
    upper_raw = stand_clean.crop((60, 0, 644, 600))
    scale = 82 / upper_raw.height
    uw = int(upper_raw.width * scale)
    uh = 82
    scaled_upper = upper_raw.resize((uw, uh), Image.Resampling.LANCZOS)
    
    # Red 'X' eyes on glasses
    u_draw = ImageDraw.Draw(scaled_upper)
    ex1, ey1 = int(uw * 0.44), int(uh * 0.22)
    ex2, ey2 = int(uw * 0.65), int(uh * 0.22)
    eye_col = (231, 76, 60, 255)
    for (ex, ey) in [(ex1, ey1), (ex2, ey2)]:
        u_draw.line([(ex - 3, ey - 3), (ex + 3, ey + 3)], fill=eye_col, width=2)
        u_draw.line([(ex - 3, ey + 3), (ex + 3, ey - 3)], fill=eye_col, width=2)

    paste_x = 50 - (uw // 2)
    paste_y = 42
    sprite.paste(scaled_upper, (paste_x, paste_y), scaled_upper)

    # 5. Draped blanket at waist / lap
    draw.rounded_rectangle([14, 122, 86, 140], radius=6, fill=(155, 89, 182, 240), outline=(120, 40, 140, 255), width=2)
    draw.line([(16, 128), (84, 128)], fill=(241, 196, 15, 240), width=2)
    draw.line([(16, 134), (84, 134)], fill=(41, 128, 185, 240), width=2)

    # 6. Dizzy Stars
    def draw_star(cx, cy, r, color):
        pts = [
            (cx, cy - r), (cx + r*0.3, cy - r*0.3),
            (cx + r, cy), (cx + r*0.3, cy + r*0.3),
            (cx, cy + r), (cx - r*0.3, cy + r*0.3),
            (cx - r, cy), (cx - r*0.3, cy - r*0.3)
        ]
        draw.polygon(pts, fill=color)

    draw_star(26, 22, 6, (241, 196, 15, 255))
    draw_star(50, 14, 5, (175, 122, 197, 255))
    draw_star(74, 24, 6, (241, 196, 15, 255))

    return sprite

def main():
    print('Processing Parsa sprites with wide unclipped canvases...')
    os.makedirs('public/images', exist_ok=True)
    
    stand_raw = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/parsa_full_standing_1789995975638.jpg'
    swing_raw = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/parsa_swing_action_1789996005231.jpg'
    sleep_raw = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/parsa_sleep_blanket_1789996028803.jpg'
    
    stand_clean = floodfill_clean(stand_raw)
    swing_clean = floodfill_clean(swing_raw, extra_seeds=[(585, 230), (608, 605), (602, 140)])
    sleep_clean = floodfill_clean(sleep_raw)
    
    # 1. Standing Sprite (144 x 214)
    body = create_standing_sprite(stand_clean)
    body.save('public/images/parsa_body.png')
    print('Saved public/images/parsa_body.png:', body.size, 'bbox:', body.getbbox())
    
    # 2. Swinging Sprite (184 x 214)
    swing = create_swing_sprite(swing_clean)
    swing.save('public/images/parsa_swing.png')
    print('Saved public/images/parsa_swing.png:', swing.size, 'bbox:', swing.getbbox())
    
    # 3. Sleep Sprite (144 x 214)
    sleep = create_sleep_sprite(sleep_clean)
    sleep.save('public/images/parsa_sleep.png')
    print('Saved public/images/parsa_sleep.png:', sleep.size, 'bbox:', sleep.getbbox())
    
    # 4. Defeat Sprite (141 x 170)
    died = create_defeat_sprite(stand_clean)
    died.save('public/images/parsa_died.png')
    print('Saved public/images/parsa_died.png:', died.size, 'bbox:', died.getbbox())
    
    print('All 4 Parsa sprites created successfully!')

if __name__ == '__main__':
    main()
