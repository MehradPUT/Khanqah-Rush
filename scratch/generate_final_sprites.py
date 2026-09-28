from PIL import Image, ImageDraw

def draw_sparkle(draw, cx, cy, size, color=(255, 255, 255, 255)):
    r = size
    inner = max(1, size // 4)
    points = [
        (cx, cy - r),
        (cx + inner, cy - inner),
        (cx + r, cy),
        (cx + inner, cy + inner),
        (cx, cy + r),
        (cx - inner, cy + inner),
        (cx - r, cy),
        (cx - inner, cy - inner)
    ]
    draw.polygon(points, fill=color)
    draw.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=(255, 255, 255, 255))

def draw_refined_beard(draw):
    # Base shadow / contour
    points_outer = [
        (37, 42), (35, 50), (34, 62), (36, 76), (40, 88), (46, 98), 
        (50, 104), # tip of beard
        (54, 98), (60, 88), (64, 76), (66, 62), (65, 50), (63, 42)
    ]
    draw.polygon(points_outer, fill=(225, 230, 235, 255), outline=(170, 178, 185, 255))
    
    # Main white body
    points_inner = [
        (38, 43), (36, 51), (35, 62), (37, 75), (41, 87), 
        (50, 101), 
        (59, 87), (63, 75), (65, 62), (64, 51), (62, 43)
    ]
    draw.polygon(points_inner, fill=(255, 255, 255, 255))
    
    # Shading lines
    shadow_lines = [
        [(38, 46), (37, 60), (39, 75), (44, 88)],
        [(42, 45), (41, 60), (43, 74), (47, 92)],
        [(47, 44), (46, 62), (47, 78), (49, 98)],
        [(53, 44), (54, 62), (53, 78), (51, 98)],
        [(58, 45), (59, 60), (57, 74), (53, 92)],
        [(62, 46), (63, 60), (61, 75), (56, 88)]
    ]
    for line in shadow_lines:
        draw.line(line, fill=(205, 212, 220, 255), width=1)

    # Highlights
    highlight_lines = [
        [(40, 48), (39, 64), (41, 78)],
        [(45, 46), (44, 66), (45, 84)],
        [(50, 46), (50, 68), (50, 92)],
        [(55, 46), (56, 66), (55, 84)],
        [(60, 48), (61, 64), (59, 78)]
    ]
    for line in highlight_lines:
        draw.line(line, fill=(255, 255, 255, 255), width=1)

    # Natural pixel-curved white mustache
    mustache_points = [
        (48, 38), (43, 37), (37, 39), (36, 42), (42, 42), (48, 40),
        (50, 41),
        (52, 40), (58, 42), (64, 42), (63, 39), (57, 37), (52, 38)
    ]
    draw.polygon(mustache_points, fill=(255, 255, 255, 255), outline=(195, 202, 210, 255))
    draw.line([(38, 40), (49, 39)], fill=(230, 235, 240, 255), width=1)
    draw.line([(51, 39), (62, 40)], fill=(230, 235, 240, 255), width=1)

def create_standing(is_old=False):
    face_img = Image.open('scratch/face_young_clean.png').convert('RGBA')
    fw, fh = face_img.size

    sprite = Image.new('RGBA', (100, 214), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # Grass mound
    draw.rounded_rectangle([0, 174, 100, 214], radius=19, fill=(153, 204, 102, 255))

    # Sneakers
    draw.rounded_rectangle([32, 186, 48, 198], radius=3, fill=(26, 26, 26, 255))
    draw.rectangle([32, 194, 48, 198], fill=(245, 245, 245, 255))
    draw.rounded_rectangle([52, 186, 68, 198], radius=3, fill=(26, 26, 26, 255))
    draw.rectangle([52, 194, 68, 198], fill=(245, 245, 245, 255))

    # Skinny Blue Jeans
    draw.rounded_rectangle([33, 124, 67, 148], radius=4, fill=(43, 96, 138, 255))
    draw.rounded_rectangle([34, 140, 47, 188], radius=3, fill=(43, 96, 138, 255))
    draw.line([(37, 144), (37, 184)], fill=(59, 130, 182, 255), width=2)
    draw.line([(46, 140), (46, 187)], fill=(27, 68, 104, 255), width=1)
    draw.rounded_rectangle([53, 140, 66, 188], radius=3, fill=(43, 96, 138, 255))
    draw.line([(56, 144), (56, 184)], fill=(59, 130, 182, 255), width=2)
    draw.line([(53, 140), (53, 187)], fill=(27, 68, 104, 255), width=1)
    draw.line([(50, 124), (50, 140)], fill=(20, 50, 80, 255), width=2)
    draw.line([(36, 128), (43, 133)], fill=(20, 50, 80, 255), width=1)
    draw.line([(64, 128), (57, 133)], fill=(20, 50, 80, 255), width=1)

    # Skinny T-shirt
    # Bottom half: Gray (y from 89 to 126)
    draw.rounded_rectangle([33, 89, 67, 126], radius=3, fill=(120, 120, 128, 255))
    draw.line([(33, 125), (67, 125)], fill=(85, 85, 92, 255), width=2)

    # Top half: y from 52 to 89
    # Top 75% black (y 52 to 80)
    draw.rounded_rectangle([33, 52, 67, 80], radius=3, fill=(22, 22, 24, 255))
    # Bottom 25% white (y 80 to 89)
    draw.rectangle([33, 80, 67, 89], fill=(248, 248, 250, 255))
    draw.line([(33, 80), (67, 80)], fill=(180, 180, 185, 255), width=1)
    draw.line([(33, 89), (67, 89)], fill=(140, 140, 145, 255), width=1)

    # Sleeves
    draw.rounded_rectangle([27, 54, 33, 76], radius=2, fill=(22, 22, 24, 255))
    draw.rounded_rectangle([67, 54, 73, 76], radius=2, fill=(22, 22, 24, 255))

    # Skin on arms
    draw.rounded_rectangle([28, 76, 32, 84], radius=2, fill=(223, 172, 155, 255))
    draw.rounded_rectangle([68, 76, 72, 84], radius=2, fill=(223, 172, 155, 255))

    # Neck
    draw.rectangle([46, 44, 54, 54], fill=(223, 172, 155, 255))
    draw.arc([44, 48, 56, 56], 0, 180, fill=(22, 22, 24, 255), width=2)

    # Young face on BOTH phases
    target_fh = 55
    target_fw = int(fw * (target_fh / fh))
    face_scaled = face_img.resize((target_fw, target_fh), Image.Resampling.NEAREST)
    face_x = 50 - (target_fw // 2)
    face_y = 0
    sprite.paste(face_scaled, (face_x, face_y), face_scaled)

    if is_old:
        # Long white beard for old phase
        draw_refined_beard(draw)
    else:
        # Sparkles for young phase
        sparkles = [
            (16, 20, 5, (241, 196, 15, 255)),
            (84, 18, 6, (241, 196, 15, 255)),
            (50, 4, 4, (255, 255, 255, 255)),
            (12, 60, 6, (88, 214, 141, 255)),
            (88, 64, 5, (88, 214, 141, 255)),
            (16, 105, 5, (241, 196, 15, 255)),
            (84, 110, 6, (241, 196, 15, 255)),
            (20, 155, 4, (255, 255, 255, 255)),
            (80, 158, 5, (88, 214, 141, 255)),
        ]
        for sx, sy, sz, sc in sparkles:
            draw_sparkle(draw, sx, sy, sz, sc)

    return sprite

def create_died(is_old=False):
    face_img = Image.open('scratch/face_young_clean.png').convert('RGBA')
    fw, fh = face_img.size
    sprite = Image.new('RGBA', (141, 170), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # Grass mound
    draw.rounded_rectangle([3, 130, 103, 170], radius=19, fill=(153, 204, 102, 255))

    # Fallen Axe
    draw.rounded_rectangle([38, 127, 132, 139], radius=6, fill=(130, 95, 49, 255))
    draw.rectangle([111, 127, 141, 157], fill=(206, 69, 58, 255))
    draw.rectangle([111, 157, 141, 169], fill=(255, 255, 255, 255), outline=(190, 190, 190, 255))

    # Slumped Blue Jeans
    draw.rounded_rectangle([24, 116, 68, 142], radius=6, fill=(43, 96, 138, 255))
    draw.rounded_rectangle([20, 134, 42, 154], radius=4, fill=(43, 96, 138, 255))
    draw.line([(24, 136), (24, 150)], fill=(59, 130, 182, 255), width=2)
    draw.rounded_rectangle([46, 134, 68, 154], radius=4, fill=(43, 96, 138, 255))
    draw.line([(50, 136), (50, 150)], fill=(59, 130, 182, 255), width=2)

    # Sneakers
    draw.rounded_rectangle([18, 148, 42, 164], radius=3, fill=(26, 26, 26, 255))
    draw.rectangle([18, 158, 42, 164], fill=(245, 245, 245, 255))
    draw.rounded_rectangle([46, 148, 70, 164], radius=3, fill=(26, 26, 26, 255))
    draw.rectangle([46, 158, 70, 164], fill=(245, 245, 245, 255))

    # Skinny T-shirt
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

    # Head on dedicated canvas for tilting
    target_fh = 55
    target_fw = int(fw * (target_fh / fh))
    head_canvas = Image.new('RGBA', (target_fw + 20, target_fh + 60), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(head_canvas)

    face_scaled = face_img.copy().resize((target_fw, target_fh), Image.Resampling.NEAREST)
    f_draw = ImageDraw.Draw(face_scaled)
    ex1, ey1 = int(target_fw * 0.38), int(target_fh * 0.40)
    ex2, ey2 = int(target_fw * 0.68), int(target_fh * 0.40)
    eye_col = (200, 50, 40, 255)
    f_draw.line([(ex1 - 4, ey1 - 4), (ex1 + 4, ey1 + 4)], fill=eye_col, width=2)
    f_draw.line([(ex1 - 4, ey1 + 4), (ex1 + 4, ey1 - 4)], fill=eye_col, width=2)
    f_draw.line([(ex2 - 4, ey2 - 4), (ex2 + 4, ey2 + 4)], fill=eye_col, width=2)
    f_draw.line([(ex2 - 4, ey2 + 4), (ex2 + 4, ey2 - 4)], fill=eye_col, width=2)

    head_canvas.paste(face_scaled, (10, 0), face_scaled)

    if is_old:
        cx = 10 + target_fw // 2
        b_outer = [
            (cx - 13, 42), (cx - 15, 50), (cx - 16, 62), (cx - 14, 76), (cx - 10, 88), (cx - 4, 98),
            (cx, 104),
            (cx + 4, 98), (cx + 10, 88), (cx + 14, 76), (cx + 16, 62), (cx + 15, 50), (cx + 13, 42)
        ]
        h_draw.polygon(b_outer, fill=(225, 230, 235, 255), outline=(170, 178, 185, 255))
        b_inner = [
            (cx - 12, 43), (cx - 14, 51), (cx - 15, 62), (cx - 13, 75), (cx - 9, 87),
            (cx, 101),
            (cx + 9, 87), (cx + 13, 75), (cx + 15, 62), (cx + 14, 51), (cx + 12, 43)
        ]
        h_draw.polygon(b_inner, fill=(255, 255, 255, 255))
        for line in [[(cx - 12, 46), (cx - 11, 60), (cx - 6, 88)], [(cx, 44), (cx, 75), (cx, 98)], [(cx + 12, 46), (cx + 11, 60), (cx + 6, 88)]]:
            h_draw.line(line, fill=(205, 212, 220, 255), width=1)
        m_points = [
            (cx - 2, 38), (cx - 7, 37), (cx - 13, 39), (cx - 14, 42), (cx - 8, 42), (cx - 2, 40),
            (cx, 41),
            (cx + 2, 40), (cx + 8, 42), (cx + 14, 42), (cx + 13, 39), (cx + 7, 37), (cx + 2, 38)
        ]
        h_draw.polygon(m_points, fill=(255, 255, 255, 255), outline=(195, 202, 210, 255))

    head_tilted = head_canvas.rotate(-10, resample=Image.Resampling.BICUBIC, expand=True)
    sprite.paste(head_tilted, (46 - (head_tilted.width // 2), 6), head_tilted)

    # Dizzy Stars
    def draw_star(cx, cy, r, color):
        points = [
            (cx, cy - r), (cx + r*0.3, cy - r*0.3),
            (cx + r, cy), (cx + r*0.3, cy + r*0.3),
            (cx, cy + r), (cx - r*0.3, cy + r*0.3),
            (cx - r, cy), (cx - r*0.3, cy - r*0.3)
        ]
        draw.polygon(points, fill=color)

    draw_star(32, 14, 6, (241, 196, 15, 255))
    draw_star(58, 8, 7, (243, 156, 18, 255))
    draw_star(78, 16, 5, (241, 196, 15, 255))

    return sprite

# 1. Standing sprites
sp_old = create_standing(is_old=True)
sp_old.save('public/images/nima_body_old.png')

sp_young = create_standing(is_old=False)
sp_young.save('public/images/nima_body_young.png')

# 2. Died sprites
died_old = create_died(is_old=True)
died_old.save('public/images/nima_died_old.png')

died_young = create_died(is_old=False)
died_young.save('public/images/nima_died_young.png')

print('Generated all 4 updated sprites successfully!')
