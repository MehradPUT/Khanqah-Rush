import os
from PIL import Image, ImageDraw, ImageFont

art_dir = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64'

font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_title = ImageFont.truetype(font_path, 15)
font_body = ImageFont.truetype(font_path, 12)
font_badge = ImageFont.truetype(font_path, 11)
font_score = ImageFont.truetype(font_path, 22)
font_score_lbl = ImageFont.truetype(font_path, 10)

body = Image.open('public/images/amirhossein_body.png').convert('RGBA').resize((68, 140), Image.Resampling.LANCZOS)
swing = Image.open('public/images/amirhossein_swing.png').convert('RGBA').resize((115, 140), Image.Resampling.LANCZOS)

w, h = 420, 680
ground_y = 550
trunk_x = 175
trunk_w = 70

def draw_game_scene(char_on_left=False, is_swinging=False, branch_right_at_d0=True):
    scene = Image.new('RGBA', (w, h), (142, 197, 173, 255))
    draw = ImageDraw.Draw(scene)

    # Sky
    for y in range(ground_y):
        ratio = y / ground_y
        r = int(24 + (142 - 24) * ratio)
        g = int(40 + (197 - 40) * ratio)
        b = int(72 + (173 - 72) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Tree Trunk
    draw.rectangle([trunk_x, 0, trunk_x + trunk_w, ground_y], fill=(130, 95, 49, 255))
    for ty in range(20, ground_y, 45):
        draw.line([(trunk_x + 10, ty), (trunk_x + 55, ty)], fill=(100, 70, 30, 255), width=3)
        draw.line([(trunk_x + 25, ty + 20), (trunk_x + 45, ty + 20)], fill=(100, 70, 30, 255), width=2)

    # Ground
    draw.rectangle([0, ground_y, w, h], fill=(133, 184, 82, 255))
    draw.line([(0, ground_y), (w, ground_y)], fill=(110, 160, 65, 255), width=3)

    # Branches along trunk:
    # 1. Branch at da[0] on the right (clearance 155px with +40px fix):
    if branch_right_at_d0:
        bx = trunk_x + trunk_w
        by = ground_y - 140 - 15  # 155px above ground (15px clearance over 140px head)
        # Wood arm
        draw.line([(bx, by + 15), (bx + 40, by)], fill=(130, 95, 49, 255), width=18)
        draw.line([(bx + 30, by), (bx + 75, by)], fill=(130, 95, 49, 255), width=14)
        draw.line([(bx + 70, by), (bx + 75, by - 25)], fill=(130, 95, 49, 255), width=14)
        # Foliage
        draw.ellipse([bx + 35, by - 45, bx + 115, by - 5], fill=(126, 173, 79, 240))
        draw.ellipse([bx + 50, by - 58, bx + 105, by - 20], fill=(153, 204, 102, 240))
        draw.ellipse([bx + 60, by - 68, bx + 95, by - 35], fill=(175, 221, 127, 240))

    # 2. Branch higher up on left (at da[2], 100px higher):
    bx_l = trunk_x
    by_l = ground_y - 155 - 100
    draw.line([(bx_l, by_l + 15), (bx_l - 40, by_l)], fill=(130, 95, 49, 255), width=18)
    draw.line([(bx_l - 30, by_l), (bx_l - 75, by_l)], fill=(130, 95, 49, 255), width=14)
    draw.line([(bx_l - 70, by_l), (bx_l - 75, by_l - 25)], fill=(130, 95, 49, 255), width=14)
    draw.ellipse([bx_l - 115, by_l - 45, bx_l - 35, by_l - 5], fill=(126, 173, 79, 240))
    draw.ellipse([bx_l - 105, by_l - 58, bx_l - 50, by_l - 20], fill=(153, 204, 102, 240))

    # 3. Branch higher up on left (at da[4], 200px higher):
    by_l2 = by_l - 100
    draw.line([(bx_l, by_l2 + 15), (bx_l - 40, by_l2)], fill=(130, 95, 49, 255), width=18)
    draw.line([(bx_l - 30, by_l2), (bx_l - 75, by_l2)], fill=(130, 95, 49, 255), width=14)
    draw.ellipse([bx_l - 115, by_l2 - 45, bx_l - 35, by_l2 - 5], fill=(126, 173, 79, 240))

    # Character Sprite:
    if char_on_left:
        cx = trunk_x - 68 - 8
        cy = ground_y - 140
        spr = body.transpose(Image.FLIP_LEFT_RIGHT)
        scene.paste(spr, (cx, cy), spr)
    else:
        cx = trunk_x + trunk_w + 10
        cy = ground_y - 140
        if is_swinging:
            sx = trunk_x + trunk_w - 5
            scene.paste(swing, (sx, cy), swing)
        else:
            scene.paste(body, (cx, cy), body)

    # Top HUD
    draw.rounded_rectangle([16, 22, 205, 80], radius=14, fill=(13, 27, 42, 240), outline=(41, 128, 185, 255), width=2)
    draw.text((28, 30), 'amirhossein', font=font_title, fill=(255, 255, 255, 255))
    draw.text((28, 52), '⚡ ۲X امتیاز فعال (140px)', font=font_badge, fill=(255, 215, 0, 255))

    # Score
    draw.rounded_rectangle([w - 115, 22, w - 16, 78], radius=12, fill=(18, 28, 44, 220), outline=(245, 176, 65, 200), width=2)
    draw.text((w - 100, 28), 'SCORE', font=font_score_lbl, fill=(200, 200, 200, 255))
    draw.text((w - 100, 44), '4', font=font_score, fill=(255, 213, 79, 255))

    return scene, draw

# 1. In-game action preview image with annotations
scene_img, draw = draw_game_scene(char_on_left=False, is_swinging=False, branch_right_at_d0=True)

# Clearance Annotation Callout
bx = trunk_x + trunk_w
by = ground_y - 155
head_y = ground_y - 140

# Callout banner right next to head and branch
draw.line([(bx + 8, by), (bx + 80, by)], fill=(255, 215, 0, 255), width=2)
draw.line([(bx + 8, head_y), (bx + 80, head_y)], fill=(46, 204, 113, 255), width=2)
draw.line([(bx + 80, by), (bx + 95, (by + head_y) // 2)], fill=(255, 215, 0, 255), width=2)
draw.line([(bx + 80, head_y), (bx + 95, (by + head_y) // 2)], fill=(46, 204, 113, 255), width=2)

draw.rounded_rectangle([bx - 10, by - 65, bx + 160, by - 15], radius=8, fill=(13, 20, 32, 245), outline=(46, 204, 113, 255), width=2)
draw.text((bx - 2, by - 58), "✅ FIXED: Clean Clearance!", font=font_body, fill=(46, 204, 113, 255))
draw.text((bx - 2, by - 40), "+15px clearance above head", font=font_badge, fill=(255, 215, 0, 255))
draw.text((bx - 2, by - 26), "No collision at 140px height", font=font_badge, fill=(200, 200, 200, 255))

out_preview_path = os.path.join(art_dir, 'branch_clearance_ingame_fixed.png')
scene_img.save(out_preview_path)
print('Saved', out_preview_path)

# 2. Animated GIF
frames = []
for i in range(8):
    frame, _ = draw_game_scene(char_on_left=False, is_swinging=False, branch_right_at_d0=True)
    frames.append(frame)

# Then player switches to left to avoid branch and chops!
for i in range(4):
    frame, _ = draw_game_scene(char_on_left=True, is_swinging=True, branch_right_at_d0=True)
    frames.append(frame)

out_gif_path = os.path.join(art_dir, 'branch_clearance_gameplay.gif')
frames[0].save(out_gif_path, save_all=True, append_images=frames[1:], duration=150, loop=0)
print('Saved', out_gif_path)
