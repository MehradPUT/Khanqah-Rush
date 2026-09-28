from collections import deque
from PIL import Image

def clean_sprite_floodfill(img, bg_target, seeds, tol=26):
    w, h = img.size
    visited = bytearray(w * h)
    q = deque()
    
    for s in seeds:
        q.append(s)
            
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
            visited[idx] = 2

    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out_data = []
    for i in range(w * h):
        if visited[i] == 1:
            out_data.append((0, 0, 0, 0))
        else:
            out_data.append(pixels[i])
    out.putdata(out_data)
    return out

# 1. CLEAN FATEME STANDING BODY
print("Refining Fateme Standing Body...")
raw_body = Image.open('/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/.user_uploaded/media_1790494261913.png').convert('RGBA')
w, h = raw_body.size

# Seeds: outer border + between legs (x=500, y=850 in raw coordinates: let's check)
seeds_body = []
for x in range(w):
    seeds_body.append((x, 0))
    seeds_body.append((x, h - 1))
for y in range(h):
    seeds_body.append((0, y))
    seeds_body.append((w - 1, y))

# Between legs seed in raw 1024x1024: (around x=510, y=880)
seeds_body.append((510, 880))
seeds_body.append((500, 850))

body_cleaned = clean_sprite_floodfill(raw_body, (184, 183, 191), seeds_body, tol=28)

# Remove ground shadow ellipse under shoes (dull gray, y > 940)
body_px = list(body_cleaned.getdata())
for i in range(w * h):
    x = i % w
    y = i // w
    p = body_px[i]
    if p[3] > 0:
        # Ignore bottom right sparkle
        if x > 850 and y > 820:
            body_px[i] = (0, 0, 0, 0)
        # Ground shadow: dull gray under the shoes (y > 938)
        elif y > 938 and abs(p[0] - p[1]) < 8 and abs(p[1] - p[2]) < 10 and 100 < p[0] < 165:
            body_px[i] = (0, 0, 0, 0)

body_cleaned.putdata(body_px)
bbox_b = body_cleaned.getbbox()
print("Cleaned body bbox:", bbox_b)
crop_b = body_cleaned.crop(bbox_b)

# Canvas: (104, 214)
body_canvas = Image.new('RGBA', (104, 214), (0, 0, 0, 0))
target_h = 204
target_w = int(crop_b.width * (target_h / crop_b.height))
scaled_b = crop_b.resize((target_w, target_h), Image.Resampling.LANCZOS)
paste_x = (104 - target_w) // 2
paste_y = 214 - target_h
body_canvas.paste(scaled_b, (paste_x, paste_y), scaled_b)

body_canvas.save('public/images/fateme_body.png')
body_canvas.save('dist/images/fateme_body.png')
body_canvas.save('/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/fateme_body.png')
print("Saved fateme_body.png")

# 2. CLEAN FATEME SWING ACTION
print("\nRefining Fateme Swing Action...")
raw_swing = Image.open('/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/fateme_swing_action_1790494663343.jpg').convert('RGBA')
w, h = raw_swing.size

seeds_swing = []
for x in range(w):
    seeds_swing.append((x, 0))
    seeds_swing.append((x, h - 1))
for y in range(h):
    seeds_swing.append((0, y))
    seeds_swing.append((w - 1, y))

# Also add seeds between legs and between leg and log
seeds_swing.append((450, 800))
seeds_swing.append((480, 820))
seeds_swing.append((680, 700))
seeds_swing.append((700, 750))

swing_cleaned = clean_sprite_floodfill(raw_swing, (180, 179, 187), seeds_swing, tol=26)

# Clear the wood log stump and chips on the far right (x > 750 and y > 520)
swing_px = list(swing_cleaned.getdata())
for i in range(w * h):
    x = i % w
    y = i // w
    p = swing_px[i]
    if p[3] > 0:
        # Wood stump on right (below the axe blade)
        if x > 750 and y > 515:
            swing_px[i] = (0, 0, 0, 0)
        # Ground shadow
        elif y > 935 and abs(p[0] - p[1]) < 8 and abs(p[1] - p[2]) < 10 and 100 < p[0] < 165:
            swing_px[i] = (0, 0, 0, 0)

swing_cleaned.putdata(swing_px)
bbox_s = swing_cleaned.getbbox()
print("Cleaned swing bbox:", bbox_s)
crop_s = swing_cleaned.crop(bbox_s)

# Canvas: (176, 214)
swing_canvas = Image.new('RGBA', (176, 214), (0, 0, 0, 0))
target_sh = 196
target_sw = int(crop_s.width * (target_sh / crop_s.height))
if target_sw > 170:
    target_sw = 170
    target_sh = int(crop_s.height * (target_sw / crop_s.width))

scaled_s = crop_s.resize((target_sw, target_sh), Image.Resampling.LANCZOS)
paste_sx = 176 - target_sw - 4 # forward facing tree
paste_sy = 214 - target_sh
swing_canvas.paste(scaled_s, (paste_sx, paste_sy), scaled_s)

swing_canvas.save('public/images/fateme_swing.png')
swing_canvas.save('dist/images/fateme_swing.png')
swing_canvas.save('/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/fateme_swing.png')
print("Saved fateme_swing.png")

# 3. CLEAN FATEME DEFEAT POSE
print("\nRefining Fateme Defeat Pose...")
raw_died = Image.open('/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/fateme_died_pose_1790494685434.jpg').convert('RGBA')
w, h = raw_died.size

seeds_died = []
for x in range(w):
    seeds_died.append((x, 0))
    seeds_died.append((x, h - 1))
for y in range(h):
    seeds_died.append((0, y))
    seeds_died.append((w - 1, y))

# Add seeds between legs and above axe
seeds_died.append((250, 720))
seeds_died.append((500, 750))

died_cleaned = clean_sprite_floodfill(raw_died, (182, 181, 187), seeds_died, tol=26)

died_px = list(died_cleaned.getdata())
for i in range(w * h):
    x = i % w
    y = i // w
    p = died_px[i]
    if p[3] > 0:
        # Ground shadow: dull gray under the legs and body
        if (y > 780 or (x > 500 and y > 680)) and abs(p[0] - p[1]) < 8 and abs(p[1] - p[2]) < 10 and 110 < p[0] < 165:
            # But do not remove shoe sole (sole is white/light purple > 180)
            if not (p[0] > 180 and p[1] > 180):
                died_px[i] = (0, 0, 0, 0)

died_cleaned.putdata(died_px)
bbox_d = died_cleaned.getbbox()
print("Cleaned died bbox:", bbox_d)
crop_d = died_cleaned.crop(bbox_d)

# Canvas: (141, 170)
died_canvas = Image.new('RGBA', (141, 170), (0, 0, 0, 0))
target_dh = 156
target_dw = int(crop_d.width * (target_dh / crop_d.height))
if target_dw > 138:
    target_dw = 138
    target_dh = int(crop_d.height * (target_dw / crop_d.width))

scaled_d = crop_d.resize((target_dw, target_dh), Image.Resampling.LANCZOS)
paste_dx = (141 - target_dw) // 2
paste_dy = 170 - target_dh
died_canvas.paste(scaled_d, (paste_dx, paste_dy), scaled_d)

died_canvas.save('public/images/fateme_died.png')
died_canvas.save('dist/images/fateme_died.png')
died_canvas.save('/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/fateme_died.png')
print("Saved fateme_died.png")

# Composite preview sheet
sheet = Image.new('RGBA', (480, 240), (28, 36, 52, 255))
sheet.paste(body_canvas, (20, 240 - 214 - 10), body_canvas)
sheet.paste(swing_canvas, (150, 240 - 214 - 10), swing_canvas)
sheet.paste(died_canvas, (330, 240 - 170 - 10), died_canvas)

sheet.save('/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/fateme_suite_preview.png')
print("Saved fateme_suite_preview.png composite!")
