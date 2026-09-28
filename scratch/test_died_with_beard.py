from PIL import Image, ImageDraw

def create_died_sprite(is_old=False):
    face_img = Image.open('scratch/face_young_clean.png').convert('RGBA')
    fw, fh = face_img.size
    sprite = Image.new('RGBA', (141, 170), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound
    draw.rounded_rectangle([3, 130, 103, 170], radius=19, fill=(153, 204, 102, 255))

    # 2. Fallen Axe on right
    draw.rounded_rectangle([38, 127, 132, 139], radius=6, fill=(130, 95, 49, 255))
    draw.rectangle([111, 127, 141, 157], fill=(206, 69, 58, 255))
    draw.rectangle([111, 157, 141, 169], fill=(255, 255, 255, 255), outline=(190, 190, 190, 255))

    # 3. Slumped Skinny Blue Jeans
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

    # 4. Skinny T-shirt
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

    # 5. Knocked out Head
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
        # Draw long white beard on head_canvas (centered at x = 10 + target_fw//2)
        cx = 10 + target_fw // 2
        # Beard outer
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

    # Tilt head slightly
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

create_died_sprite(is_old=True).save('scratch/test_died_with_beard.png')
print('Saved scratch/test_died_with_beard.png')
