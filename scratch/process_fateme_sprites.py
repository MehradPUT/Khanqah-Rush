import os
from collections import deque
from PIL import Image

def floodfill_bg(img, bg_target, tol=28, border_seeds=True):
    w, h = img.size
    visited = bytearray(w * h)
    q = deque()
    
    if border_seeds:
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

# 1. PROCESS STANDING BODY
print("Processing Fateme Standing Body...")
orig_img = Image.open('scratch/fateme_no_shadow.png')
# Target body canvas: (104, 214) (Option B Heroic scale, matches Erfan, Nima, Ali)
body_canvas = Image.new('RGBA', (104, 214), (0, 0, 0, 0))
target_h = 204
target_w = int(orig_img.width * (target_h / orig_img.height))
scaled_body = orig_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
paste_x = (104 - target_w) // 2
paste_y = 214 - target_h
body_canvas.paste(scaled_body, (paste_x, paste_y), scaled_body)

body_canvas.save('public/images/fateme_body.png')
body_canvas.save('dist/images/fateme_body.png')
body_canvas.save('/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/fateme_body.png')
print(f"Saved fateme_body.png ({body_canvas.size})")

# 2. PROCESS SWING ACTION
print("\nProcessing Fateme Swing Action...")
swing_raw = Image.open('/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/fateme_swing_action_1790494663343.jpg').convert('RGBA')
swing_clean = floodfill_bg(swing_raw, (180, 179, 187), tol=25)

# Remove the tree stump/log on the right and ground shadow
w, h = swing_clean.size
pixels = list(swing_clean.getdata())
clean_pixels = []

for i in range(w * h):
    x = i % w
    y = i // w
    p = pixels[i]
    if p[3] > 0:
        # Ground shadow at bottom (y > 930)
        if y > 930 and abs(p[0] - p[1]) < 10 and abs(p[1] - p[2]) < 12 and 100 < p[0] < 165:
            clean_pixels.append((0, 0, 0, 0))
        # Stump log wood: brown colors on far right below the axe blade (x > 750 and y > 530)
        elif x > 755 and y > 530 and (p[0] > p[2] + 25): # Brown wood has R significantly > B
            clean_pixels.append((0, 0, 0, 0))
        # Flying woodchips at bottom right (x > 750 and y > 540)
        elif x > 750 and y > 540:
            clean_pixels.append((0, 0, 0, 0))
        else:
            clean_pixels.append(p)
    else:
        clean_pixels.append((0, 0, 0, 0))

swing_clean.putdata(clean_pixels)
bbox_swing = swing_clean.getbbox()
print("Swing bbox:", bbox_swing)
swing_cropped = swing_clean.crop(bbox_swing)

# Target swing canvas: (176, 214) (Option B Heroic scale)
swing_canvas = Image.new('RGBA', (176, 214), (0, 0, 0, 0))
target_swing_h = 196
target_swing_w = int(swing_cropped.width * (target_swing_h / swing_cropped.height))
scaled_swing = swing_cropped.resize((target_swing_w, target_swing_h), Image.Resampling.LANCZOS)
# Position swing forward towards the tree
paste_swing_x = max(0, min(176 - target_swing_w, 10))
paste_swing_y = 214 - target_swing_h
swing_canvas.paste(scaled_swing, (paste_swing_x, paste_swing_y), scaled_swing)

swing_canvas.save('public/images/fateme_swing.png')
swing_canvas.save('dist/images/fateme_swing.png')
swing_canvas.save('/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/fateme_swing.png')
print(f"Saved fateme_swing.png ({swing_canvas.size})")

# 3. PROCESS DEFEAT POSE
print("\nProcessing Fateme Defeat Pose...")
died_raw = Image.open('/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/fateme_died_pose_1790494685434.jpg').convert('RGBA')
died_clean = floodfill_bg(died_raw, (182, 181, 187), tol=26)

# Remove ground shadow beneath slumped body/axe (y > 700, flat gray)
w, h = died_clean.size
pixels_died = list(died_clean.getdata())
clean_pixels_died = []

for i in range(w * h):
    x = i % w
    y = i // w
    p = pixels_died[i]
    if p[3] > 0:
        # Ground shadow: dull gray under the body (y > 680)
        if y > 680 and abs(p[0] - p[1]) < 8 and abs(p[1] - p[2]) < 10 and 110 < p[0] < 165:
            clean_pixels_died.append((0, 0, 0, 0))
        else:
            clean_pixels_died.append(p)
    else:
        clean_pixels_died.append((0, 0, 0, 0))

died_clean.putdata(clean_pixels_died)
bbox_died = died_clean.getbbox()
print("Died bbox:", bbox_died)
died_cropped = died_clean.crop(bbox_died)

# Target died canvas: (141, 170) (Option B Heroic scale, matches all characters)
died_canvas = Image.new('RGBA', (141, 170), (0, 0, 0, 0))
target_died_h = 158
target_died_w = int(died_cropped.width * (target_died_h / died_cropped.height))
if target_died_w > 138:
    target_died_w = 138
    target_died_h = int(died_cropped.height * (target_died_w / died_cropped.width))

scaled_died = died_cropped.resize((target_died_w, target_died_h), Image.Resampling.LANCZOS)
paste_died_x = (141 - target_died_w) // 2
paste_died_y = 170 - target_died_h
died_canvas.paste(scaled_died, (paste_died_x, paste_died_y), scaled_died)

died_canvas.save('public/images/fateme_died.png')
died_canvas.save('dist/images/fateme_died.png')
died_canvas.save('/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/fateme_died.png')
print(f"Saved fateme_died.png ({died_canvas.size})")

print("\nALL 3 FATEME SPRITES PROCESSED & SAVED SUCCESSFULLY!")
