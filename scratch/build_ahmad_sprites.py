import os
from collections import deque
from PIL import Image, ImageDraw

def floodfill_clean_stand(img_path):
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
        
    def is_bg(c):
        return (abs(c[0] - 191) <= 18 and 
                abs(c[1] - 191) <= 18 and 
                abs(c[2] - 191) <= 18)

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
                if not is_bg(c):
                    clean.putpixel((x, y), c)
                
    bbox = clean.getbbox()
    print(f'Extracted {os.path.basename(img_path)} bbox: {bbox}')
    return clean.crop(bbox)

def floodfill_clean_swing(img_path):
    img = Image.open(img_path).convert('RGBA')
    w, h = img.size
    visited = bytearray(w * h)
    q = deque()

    # Add background seeds (top, left, and bottom-left)
    for x in range(w):
        q.append((x, 0))
        if x < 700:
            q.append((x, h - 1))
    for y in range(h):
        q.append((0, y))

    def is_bg(c):
        return (abs(c[0] - 191) <= 18 and 
                abs(c[1] - 191) <= 18 and 
                abs(c[2] - 191) <= 18)

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

    # Also floodfill/remove the tree trunk starting from bottom-right (1023, 1023)
    tree_q = deque([(w - 1, h - 1)])
    tree_visited = bytearray(w * h)
    while tree_q:
        x, y = tree_q.popleft()
        idx = y * w + x
        if tree_visited[idx]:
            continue
        tree_visited[idx] = 1
        # Stop at axe blade boundary (x < 870 when y < 700)
        if x < 870 and y < 700:
            continue
        c = img.getpixel((x, y))
        if not visited[idx]:
            visited[idx] = 2  # Marked as tree
            if x > 0 and not tree_visited[idx - 1]: tree_q.append((x - 1, y))
            if x < w - 1 and not tree_visited[idx + 1]: tree_q.append((x + 1, y))
            if y > 0 and not tree_visited[idx - w]: tree_q.append((x, y - 1))
            if y < h - 1 and not tree_visited[idx + w]: tree_q.append((x, y + 1))

    clean = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            idx = y * w + x
            if visited[idx] == 0:
                c = img.getpixel((x, y))
                if not is_bg(c):
                    clean.putpixel((x, y), c)

    bbox = clean.getbbox()
    print(f'Extracted {os.path.basename(img_path)} bbox: {bbox}')
    return clean.crop(bbox)

def create_standing_sprite(char_img):
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

    # Subtle protective shield aura (steel cyan/gold)
    aura = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    aura_draw = ImageDraw.Draw(aura)
    aura_draw.ellipse([10, 12, 134, 192], fill=(41, 128, 185, 20), outline=(52, 152, 219, 70), width=1)
    sprite = Image.alpha_composite(sprite, aura)

    # Paste character
    sprite.paste(scaled_char, (paste_x, paste_y), scaled_char)
    return sprite

def create_swing_sprite(char_img):
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

    # 3. Slumped Dark Pants & Black Sneakers
    draw.rounded_rectangle([18, 114, 82, 148], radius=6, fill=(25, 28, 32, 255))
    draw.rounded_rectangle([16, 132, 44, 154], radius=4, fill=(25, 28, 32, 255))
    draw.rounded_rectangle([54, 132, 82, 154], radius=4, fill=(25, 28, 32, 255))
    # Black Nike-style sneakers with white swoosh
    draw.rounded_rectangle([12, 148, 44, 166], radius=4, fill=(35, 38, 42, 255), outline=(15, 18, 22, 255))
    draw.line([(20, 156), (36, 156)], fill=(240, 240, 240, 255), width=2)
    draw.rounded_rectangle([54, 148, 86, 166], radius=4, fill=(35, 38, 42, 255), outline=(15, 18, 22, 255))
    draw.line([(62, 156), (78, 156)], fill=(240, 240, 240, 255), width=2)

    # 4. Slumped Upper Body & Sweatshirt (cropped from stand_clean)
    upper_raw = stand_clean.crop((0, 0, stand_clean.width, int(stand_clean.height * 0.52)))
    scale = 82 / upper_raw.height
    uw = int(upper_raw.width * scale)
    uh = 82
    scaled_upper = upper_raw.resize((uw, uh), Image.Resampling.LANCZOS)
    
    # Red 'X' eyes squarely over his eyes
    u_draw = ImageDraw.Draw(scaled_upper)
    eye_col = (231, 76, 60, 255)
    # Left eye (37, 14) and Right eye (44, 15)
    for (ex, ey) in [(37, 14), (44, 15)]:
        u_draw.line([(ex - 2, ey - 2), (ex + 2, ey + 2)], fill=eye_col, width=2)
        u_draw.line([(ex - 2, ey + 2), (ex + 2, ey - 2)], fill=eye_col, width=2)

    paste_x = 50 - (uw // 2)
    paste_y = 42
    sprite.paste(scaled_upper, (paste_x, paste_y), scaled_upper)

    # 5. Broken steel shield fragment resting at waist
    shield_pts = [(16, 122), (32, 116), (46, 122), (40, 138), (32, 144), (20, 138)]
    draw.polygon(shield_pts, fill=(52, 152, 219, 230), outline=(41, 128, 185, 255))
    draw.line([(26, 118), (32, 130), (36, 142)], fill=(241, 196, 15, 255), width=2)

    # 6. Dizzy Stars & Shield Sparkles
    def draw_star(cx, cy, r, color):
        pts = [
            (cx, cy - r), (cx + r*0.3, cy - r*0.3),
            (cx + r, cy), (cx + r*0.3, cy + r*0.3),
            (cx, cy + r), (cx - r*0.3, cy + r*0.3),
            (cx - r, cy), (cx - r*0.3, cy - r*0.3)
        ]
        draw.polygon(pts, fill=color)

    draw_star(42, 22, 6, (241, 196, 15, 255))   # Gold star
    draw_star(57, 14, 5, (52, 152, 219, 255))   # Cyan spark
    draw_star(72, 24, 6, (241, 196, 15, 255))   # Gold star

    return sprite

def main():
    print('Processing Ahmad sprites with wide unclipped canvases...')
    os.makedirs('public/images', exist_ok=True)
    
    stand_raw = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/ahmad_standing_1790145019513.jpg'
    swing_raw = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/ahmad_swing_action_1790145050522.jpg'
    
    stand_clean = floodfill_clean_stand(stand_raw)
    swing_clean = floodfill_clean_swing(swing_raw)
    
    # 1. Standing Sprite (144 x 214)
    body = create_standing_sprite(stand_clean)
    body.save('public/images/ahmad_body.png')
    print('Saved public/images/ahmad_body.png:', body.size, 'bbox:', body.getbbox())
    
    # 2. Swinging Sprite (184 x 214)
    swing = create_swing_sprite(swing_clean)
    swing.save('public/images/ahmad_swing.png')
    print('Saved public/images/ahmad_swing.png:', swing.size, 'bbox:', swing.getbbox())
    
    # 3. Defeat Sprite (141 x 170)
    died = create_defeat_sprite(stand_clean)
    died.save('public/images/ahmad_died.png')
    print('Saved public/images/ahmad_died.png:', died.size, 'bbox:', died.getbbox())
    
    print('All 3 Ahmad sprites created successfully!')

if __name__ == '__main__':
    main()
