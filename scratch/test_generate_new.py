from PIL import Image, ImageDraw

def draw_sparkle(draw, cx, cy, size, color=(255, 255, 255, 255)):
    # 4-point star sparkle
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
    # Bright center dot
    draw.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=(255, 255, 255, 255))

def draw_long_white_beard(draw):
    # Flowing majestic white beard from chin down onto chest
    # Chin/jaw is at y=42 to 46, width x=39 to 61
    points_outer = [
        (40, 42), (37, 50), (36, 62), (38, 76), (42, 88), (47, 98), 
        (50, 102), # tip of beard
        (53, 98), (58, 88), (62, 76), (64, 62), (63, 50), (60, 42)
    ]
    draw.polygon(points_outer, fill=(225, 230, 235, 255), outline=(175, 182, 190, 255))
    
    # Main white body
    points_inner = [
        (41, 43), (39, 51), (38, 62), (40, 75), (44, 87), 
        (50, 99), 
        (56, 87), (60, 75), (62, 62), (61, 51), (59, 43)
    ]
    draw.polygon(points_inner, fill=(255, 255, 255, 255))
    
    # Realistic strands & layering
    strands = [
        [(41, 48), (40, 60), (42, 74), (46, 86)],
        [(45, 45), (44, 58), (45, 72), (48, 90)],
        [(50, 45), (50, 62), (50, 78), (50, 97)],
        [(55, 45), (56, 58), (55, 72), (52, 90)],
        [(59, 48), (60, 60), (58, 74), (54, 86)]
    ]
    for s in strands:
        draw.line(s, fill=(195, 202, 210, 255), width=1)
        
    # Highlights
    highlights = [
        [(43, 50), (42, 65), (44, 80)],
        [(48, 48), (48, 68), (48, 88)],
        [(52, 48), (52, 68), (52, 88)],
        [(57, 50), (58, 65), (56, 80)]
    ]
    for h in highlights:
        draw.line(h, fill=(255, 255, 255, 255), width=1)

    # White mustache covering the dark mustache
    draw.rounded_rectangle([40, 36, 60, 42], radius=2, fill=(252, 252, 255, 255), outline=(195, 202, 210, 255))
    draw.line([(42, 38), (58, 38)], fill=(255, 255, 255, 255), width=1)

def create_nima_sprite(is_old=False):
    # BOTH phases start from the exact young face: scratch/face_young_clean.png
    face_img = Image.open('scratch/face_young_clean.png').convert('RGBA')
    fw, fh = face_img.size

    sprite = Image.new('RGBA', (100, 214), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound at bottom
    draw.rounded_rectangle([0, 174, 100, 214], radius=19, fill=(153, 204, 102, 255))

    # 2. Sneakers
    draw.rounded_rectangle([32, 186, 48, 198], radius=3, fill=(26, 26, 26, 255))
    draw.rectangle([32, 194, 48, 198], fill=(245, 245, 245, 255))
    draw.rounded_rectangle([52, 186, 68, 198], radius=3, fill=(26, 26, 26, 255))
    draw.rectangle([52, 194, 68, 198], fill=(245, 245, 245, 255))

    # 3. Skinny Blue Jeans
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

    # 4. Skinny T-shirt
    # Bottom half: Solid Gray (y from 89 to 126, height 37px)
    draw.rounded_rectangle([33, 89, 67, 126], radius=3, fill=(120, 120, 128, 255))
    draw.line([(33, 125), (67, 125)], fill=(85, 85, 92, 255), width=2)

    # Top half: y from 52 to 89 (height 37px)
    # Top 75% of top half: y from 52 to 80 (height 28px) -> BLACK
    draw.rounded_rectangle([33, 52, 67, 80], radius=3, fill=(22, 22, 24, 255))
    # Bottom 25% of top half: y from 80 to 89 (height 9px) -> WHITE
    draw.rectangle([33, 80, 67, 89], fill=(248, 248, 250, 255))
    draw.line([(33, 80), (67, 80)], fill=(180, 180, 185, 255), width=1)
    draw.line([(33, 89), (67, 89)], fill=(140, 140, 145, 255), width=1)

    # Slim short sleeves at top (black)
    draw.rounded_rectangle([27, 54, 33, 76], radius=2, fill=(22, 22, 24, 255))
    draw.rounded_rectangle([67, 54, 73, 76], radius=2, fill=(22, 22, 24, 255))

    # Slim skin peeking from sleeves
    draw.rounded_rectangle([28, 76, 32, 84], radius=2, fill=(223, 172, 155, 255))
    draw.rounded_rectangle([68, 76, 72, 84], radius=2, fill=(223, 172, 155, 255))

    # Neck
    draw.rectangle([46, 44, 54, 54], fill=(223, 172, 155, 255))
    draw.arc([44, 48, 56, 56], 0, 180, fill=(22, 22, 24, 255), width=2)

    # 5. Face (Exact young face with dark hair)
    target_fh = 55
    target_fw = int(fw * (target_fh / fh))
    face_scaled = face_img.resize((target_fw, target_fh), Image.Resampling.NEAREST)
    face_x = 50 - (target_fw // 2)
    face_y = 0
    sprite.paste(face_scaled, (face_x, face_y), face_scaled)

    # 6. If Old Phase: add the VERY LONG WHITE BEARD!
    if is_old:
        draw_long_white_beard(draw)

    # 7. If Young Phase: add SPARKLES around him!
    if not is_old:
        # Magical golden and cyan/white sparkles dancing around
        sparkles = [
            (16, 20, 5, (241, 196, 15, 255)),   # Gold star top left
            (84, 18, 6, (241, 196, 15, 255)),   # Gold star top right
            (50, 4, 4, (255, 255, 255, 255)),   # White star above head
            (12, 60, 6, (88, 214, 141, 255)),   # Emerald/cyan star left
            (88, 64, 5, (88, 214, 141, 255)),   # Emerald/cyan star right
            (16, 105, 5, (241, 196, 15, 255)),  # Gold star mid left
            (84, 110, 6, (241, 196, 15, 255)),  # Gold star mid right
            (20, 155, 4, (255, 255, 255, 255)), # White glint lower left
            (80, 158, 5, (88, 214, 141, 255)),  # Cyan glint lower right
        ]
        for sx, sy, sz, sc in sparkles:
            draw_sparkle(draw, sx, sy, sz, sc)

    return sprite

sp_old = create_nima_sprite(is_old=True)
sp_old.save('scratch/test_new_old.png')

sp_young = create_nima_sprite(is_old=False)
sp_young.save('scratch/test_new_young.png')

print('Generated test_new_old.png and test_new_young.png')
