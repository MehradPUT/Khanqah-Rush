import os
from collections import deque
from PIL import Image

normal_path = "/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/.user_uploaded/media_1790430172328.png"
flame_path = "/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/.user_uploaded/media_1790430178308.jpg"

def floodfill_bg(img, bg_target, tol=25):
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
        return (abs(c[0] - bg_target[0]) <= tol and 
                abs(c[1] - bg_target[1]) <= tol and 
                abs(c[2] - bg_target[2]) <= tol)

    pixels = list(img.getdata())
    
    while q:
        x, y = q.popleft()
        idx = y * w + x
        if visited[idx]:
            continue
            
        c = pixels[idx]
        if is_bg(c):
            visited[idx] = 1
            if x > 0: q.append((x - 1, y))
            if x < w - 1: q.append((x + 1, y))
            if y > 0: q.append((x, y - 1))
            if y < h - 1: q.append((x, y + 1))
        else:
            visited[idx] = 2 # marked as foreground edge

    out = Image.new('RGBA', (w, h), (0,0,0,0))
    out_data = []
    for i in range(w * h):
        if visited[i] == 1:
            out_data.append((0, 0, 0, 0))
        else:
            out_data.append(pixels[i])
    out.putdata(out_data)
    
    # find bbox
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
        
    return out

def process_sprite(path, bg_target, target_width, target_height):
    img = Image.open(path).convert('RGBA')
    out = floodfill_bg(img, bg_target)
    out = out.resize((target_width, target_height), Image.Resampling.LANCZOS)
    return out

print("Processing normal body...")
fargol_normal = process_sprite(normal_path, (183, 183, 187), 94, 140)
fargol_normal.save('public/images/fargol_body.png')

print("Processing flame body...")
fargol_flame = process_sprite(flame_path, (92, 92, 92), 94, 140)
fargol_flame.save('public/images/fargol_body_flame.png')

def create_swing(base_sprite):
    swing = Image.new('RGBA', (120, 140), (0,0,0,0))
    rotated = base_sprite.rotate(-15, expand=True, resample=Image.Resampling.BICUBIC)
    bbox = rotated.getbbox()
    if bbox:
        rotated = rotated.crop(bbox)
    
    ratio = 135 / rotated.height
    new_w = int(rotated.width * ratio)
    rotated = rotated.resize((new_w, 135), Image.Resampling.LANCZOS)
    
    paste_x = 120 - new_w - 5
    paste_y = 140 - 135
    swing.paste(rotated, (paste_x, paste_y), rotated)
    return swing

print("Creating swing frames...")
fargol_normal_swing = create_swing(fargol_normal)
fargol_normal_swing.save('public/images/fargol_swing.png')

fargol_flame_swing = create_swing(fargol_flame)
fargol_flame_swing.save('public/images/fargol_swing_flame.png')

def create_died(base_sprite):
    died = Image.new('RGBA', (95, 111), (0,0,0,0))
    slumped = base_sprite.resize((94, int(140 * 0.7)), Image.Resampling.LANCZOS)
    rotated = slumped.rotate(40, expand=True, resample=Image.Resampling.BICUBIC)
    
    bbox = rotated.getbbox()
    if bbox:
        rotated = rotated.crop(bbox)
        
    rotated = rotated.resize((95, 111), Image.Resampling.LANCZOS)
    died.paste(rotated, (0,0), rotated)
    return died

print("Creating died frames...")
fargol_died = create_died(fargol_normal)
fargol_died.save('public/images/fargol_died.png')

print("Done generating sprites.")
