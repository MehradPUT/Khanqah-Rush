from PIL import Image, ImageDraw

def draw_sultan_crown(draw, cx, cy, width=30, height=14, is_flaming=False):
    band_y = cy + height - 4
    # Golden base band
    draw.rounded_rectangle([cx - width//2, band_y, cx + width//2, band_y + 4], radius=2, fill=(255, 215, 0, 255), outline=(180, 140, 0, 255))
    
    # Jewels on band (ruby, emerald, ruby)
    draw.rectangle([cx - width//2 + 4, band_y + 1, cx - width//2 + 6, band_y + 3], fill=(220, 20, 60, 255)) # Ruby
    draw.rectangle([cx - 2, band_y + 1, cx + 1, band_y + 3], fill=(0, 200, 100, 255)) # Emerald
    draw.rectangle([cx + width//2 - 6, band_y + 1, cx + width//2 - 4, band_y + 3], fill=(220, 20, 60, 255)) # Ruby
    
    # 5 Crown peaks (center is royal sultan peak)
    peaks = [
        [(cx - width//2, band_y), (cx - width//2 + 2, cy + 3), (cx - width//2 + 5, band_y)],
        [(cx - width//2 + 4, band_y), (cx - width//4, cy + 1), (cx - width//4 + 4, band_y)],
        [(cx - 6, band_y), (cx, cy - 4), (cx + 6, band_y)], # Center tallest
        [(cx + width//4 - 4, band_y), (cx + width//4, cy + 1), (cx + width//2 - 4, band_y)],
        [(cx + width//2 - 5, band_y), (cx + width//2 - 2, cy + 3), (cx + width//2, band_y)],
    ]
    for p in peaks:
        draw.polygon(p, fill=(255, 223, 0, 255), outline=(190, 150, 0, 255))
        # Tip jewel / pearl
        tip_x, tip_y = p[1]
        draw.rectangle([tip_x - 1, tip_y - 2, tip_x + 1, tip_y], fill=(255, 255, 255, 255))
    
    # Big center ruby on royal peak
    draw.polygon([(cx, cy - 1), (cx + 2, cy + 2), (cx, cy + 5), (cx - 2, cy + 2)], fill=(220, 20, 60, 255))

    if is_flaming:
        # Fire licking upwards from peaks
        fire_spikes = [
            [(cx - width//2 + 2, cy + 2), (cx - width//2 + 1, cy - 8), (cx - width//2 + 4, cy - 1)],
            [(cx - width//4, cy), (cx - width//4, cy - 11), (cx - width//4 + 4, cy - 2)],
            [(cx - 1, cy - 4), (cx - 2, cy - 16), (cx + 3, cy - 5)],
            [(cx, cy - 4), (cx + 3, cy - 14), (cx + 4, cy - 3)],
            [(cx + width//4, cy), (cx + width//4, cy - 11), (cx + width//4 + 4, cy - 2)],
            [(cx + width//2 - 2, cy + 2), (cx + width//2 - 1, cy - 8), (cx + width//2 - 3, cy - 1)],
        ]
        for fp in fire_spikes:
            draw.polygon(fp, fill=(255, 60, 0, 240))
            inner = [(fp[0][0], fp[0][1]), ((fp[1][0]*2 + fp[0][0])//3, (fp[1][1]*2 + fp[0][1])//3), (fp[2][0], fp[2][1])]
            draw.polygon(inner, fill=(255, 235, 50, 255))

def draw_flame_aura_behind(draw, cx, cy):
    # Roaring flame aura licking around body and sides (behind torso and head)
    flame_jets = [
        # Left side flames
        [(cx - 18, cy + 60), (cx - 38, cy + 40), (cx - 16, cy + 30)],
        [(cx - 17, cy + 35), (cx - 44, cy + 10), (cx - 16, cy - 5)],
        [(cx - 16, cy), (cx - 40, cy - 30), (cx - 14, cy - 45)],
        [(cx - 15, cy - 40), (cx - 32, cy - 70), (cx - 8, cy - 55)],
        # Right side flames
        [(cx + 18, cy + 60), (cx + 38, cy + 40), (cx + 16, cy + 30)],
        [(cx + 17, cy + 35), (cx + 44, cy + 10), (cx + 16, cy - 5)],
        [(cx + 16, cy), (cx + 40, cy - 30), (cx + 14, cy - 45)],
        [(cx + 15, cy - 40), (cx + 32, cy - 70), (cx + 8, cy - 55)],
        # Top aura above crown
        [(cx - 10, cy - 65), (cx - 6, cy - 90), (cx - 1, cy - 70)],
        [(cx - 2, cy - 70), (cx + 3, cy - 94), (cx + 8, cy - 70)],
        [(cx + 7, cy - 70), (cx + 12, cy - 88), (cx + 16, cy - 65)],
        # Lower body embers
        [(cx - 18, cy + 85), (cx - 30, cy + 70), (cx - 15, cy + 65)],
        [(cx + 18, cy + 85), (cx + 30, cy + 70), (cx + 15, cy + 65)],
    ]
    for fj in flame_jets:
        # Outer red-orange fire
        draw.polygon(fj, fill=(255, 30, 0, 220))
        # Mid orange flame
        mid = [((fj[0][0]*2 + cx)//3, (fj[0][1]*2 + cy)//3), (fj[1][0], fj[1][1] + 5), ((fj[2][0]*2 + cx)//3, (fj[2][1]*2 + cy)//3)]
        draw.polygon(mid, fill=(255, 140, 0, 240))
        # Inner golden spark
        inner = [((fj[0][0] + cx)//2, (fj[0][1] + cy)//2), (fj[1][0], fj[1][1] + 12), ((fj[2][0] + cx)//2, (fj[2][1] + cy)//2)]
        draw.polygon(inner, fill=(255, 240, 60, 255))

    # Floating ember sparks
    embers = [(cx - 32, cy - 10), (cx + 35, cy - 18), (cx - 25, cy - 55), (cx + 28, cy - 50), (cx - 18, cy - 85), (cx + 22, cy - 82)]
    for ex, ey in embers:
        draw.rectangle([ex - 1, ey - 1, ex + 1, ey + 1], fill=(255, 235, 80, 255))

def create_fargol_standing(is_flame=False):
    sprite = Image.new('RGBA', (100, 214), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 0. If Flame mode: Draw flame aura BEHIND the character first
    if is_flame:
        draw_flame_aura_behind(draw, 50, 100)

    # 1. Grass mound
    draw.rounded_rectangle([0, 174, 100, 214], radius=19, fill=(153, 204, 102, 255))

    # 2. Sneakers (dark with clean white sole)
    draw.rounded_rectangle([32, 186, 48, 198], radius=3, fill=(30, 34, 42, 255))
    draw.rectangle([32, 194, 48, 198], fill=(245, 245, 245, 255))
    draw.rounded_rectangle([52, 186, 68, 198], radius=3, fill=(30, 34, 42, 255))
    draw.rectangle([52, 194, 68, 198], fill=(245, 245, 245, 255))

    # 3. Tailored Dark Trousers (Charcoal Navy)
    draw.rounded_rectangle([33, 124, 67, 148], radius=3, fill=(36, 44, 56, 255))
    draw.rounded_rectangle([34, 140, 47, 188], radius=2, fill=(36, 44, 56, 255))
    draw.line([(37, 144), (37, 184)], fill=(50, 62, 78, 255), width=2)
    draw.line([(46, 140), (46, 187)], fill=(24, 30, 38, 255), width=1)
    draw.rounded_rectangle([53, 140, 66, 188], radius=2, fill=(36, 44, 56, 255))
    draw.line([(56, 144), (56, 184)], fill=(50, 62, 78, 255), width=2)
    draw.line([(53, 140), (53, 187)], fill=(24, 30, 38, 255), width=1)
    draw.line([(50, 124), (50, 140)], fill=(22, 28, 36, 255), width=1)

    # 4. Soft Sage / Mint Green Tunic (matching photo)
    # Tunic covers from y=80 down to y=128
    draw.rounded_rectangle([32, 80, 68, 128], radius=4, fill=(142, 197, 173, 255)) # mint sage
    # Belt / waist cinch at y=114
    draw.line([(32, 114), (68, 114)], fill=(110, 168, 144, 255), width=2)
    draw.line([(33, 127), (67, 127)], fill=(110, 168, 144, 255), width=2) # hem shadow
    # Subtle vertical pleats
    draw.line([(42, 95), (41, 126)], fill=(125, 182, 158, 255), width=1)
    draw.line([(58, 95), (59, 126)], fill=(125, 182, 158, 255), width=1)
    # V-Neck / Collar
    draw.polygon([(45, 80), (50, 88), (55, 80)], fill=(115, 172, 148, 255))

    # Sleeves (arms alongside body)
    draw.rounded_rectangle([26, 82, 32, 116], radius=2, fill=(142, 197, 173, 255))
    draw.rounded_rectangle([68, 82, 74, 116], radius=2, fill=(142, 197, 173, 255))
    # Delicate hands
    draw.rounded_rectangle([26, 116, 32, 126], radius=3, fill=(235, 185, 170, 255))
    draw.rounded_rectangle([68, 116, 74, 126], radius=3, fill=(235, 185, 170, 255))

    # 5. Face & Headscarf
    face_raw = Image.open('scratch/fargol_clean_face.png').convert('RGBA')
    # Resize head neatly
    target_h = 50
    target_w = int(face_raw.width * (target_h / face_raw.height)) # ~46
    face_scaled = face_raw.resize((target_w, target_h), Image.Resampling.NEAREST)

    head_x = 50 - target_w // 2
    head_y = 34
    sprite.paste(face_scaled, (head_x, head_y), face_scaled)

    # 6. Royal Sultan Crown
    crown_x = 50
    crown_y = head_y - 8
    draw_sultan_crown(draw, crown_x, crown_y, width=30, height=13, is_flaming=is_flame)

    return sprite

def create_fargol_died():
    sprite = Image.new('RGBA', (141, 170), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound
    draw.rounded_rectangle([3, 130, 103, 170], radius=19, fill=(153, 204, 102, 255))

    # 2. Fallen Axe
    draw.rounded_rectangle([38, 127, 132, 139], radius=6, fill=(130, 95, 49, 255))
    draw.rectangle([111, 127, 141, 157], fill=(206, 69, 58, 255))
    draw.rectangle([111, 157, 141, 169], fill=(255, 255, 255, 255), outline=(190, 190, 190, 255))

    # 3. Slumped Dark Trousers
    draw.rounded_rectangle([24, 116, 68, 142], radius=5, fill=(36, 44, 56, 255))
    draw.rounded_rectangle([20, 134, 42, 154], radius=4, fill=(36, 44, 56, 255))
    draw.line([(24, 136), (24, 150)], fill=(50, 62, 78, 255), width=2)
    draw.rounded_rectangle([46, 134, 68, 154], radius=4, fill=(36, 44, 56, 255))
    draw.line([(50, 136), (50, 150)], fill=(50, 62, 78, 255), width=2)

    # Sneakers
    draw.rounded_rectangle([18, 148, 42, 164], radius=3, fill=(30, 34, 42, 255))
    draw.rectangle([18, 158, 42, 164], fill=(245, 245, 245, 255))
    draw.rounded_rectangle([46, 148, 70, 164], radius=3, fill=(30, 34, 42, 255))
    draw.rectangle([46, 158, 70, 164], fill=(245, 245, 245, 255))

    # 4. Slumped Sage Tunic
    draw.rounded_rectangle([28, 72, 64, 120], radius=4, fill=(142, 197, 173, 255))
    draw.line([(28, 119), (64, 119)], fill=(110, 168, 144, 255), width=2)
    # Sleeves & hands slumped
    draw.rounded_rectangle([21, 74, 28, 110], radius=2, fill=(142, 197, 173, 255))
    draw.rounded_rectangle([64, 74, 71, 110], radius=2, fill=(142, 197, 173, 255))
    draw.rounded_rectangle([19, 108, 27, 120], radius=3, fill=(235, 185, 170, 255))
    draw.rounded_rectangle([65, 108, 73, 120], radius=3, fill=(235, 185, 170, 255))

    # 5. Head on dedicated canvas for tilt
    face_raw = Image.open('scratch/fargol_clean_face.png').convert('RGBA')
    target_h = 50
    target_w = int(face_raw.width * (target_h / face_raw.height))
    face_scaled = face_raw.resize((target_w, target_h), Image.Resampling.NEAREST)

    # Dizzy cross eyes on face
    f_draw = ImageDraw.Draw(face_scaled)
    # Eyes in face coordinates
    ex1, ey1 = int(target_w * 0.38), int(target_h * 0.44)
    ex2, ey2 = int(target_w * 0.65), int(target_h * 0.44)
    f_draw.line([(ex1-3, ey1-3), (ex1+3, ey1+3)], fill=(200, 50, 40, 255), width=2)
    f_draw.line([(ex1-3, ey1+3), (ex1+3, ey1-3)], fill=(200, 50, 40, 255), width=2)
    f_draw.line([(ex2-3, ey2-3), (ex2+3, ey2+3)], fill=(200, 50, 40, 255), width=2)
    f_draw.line([(ex2-3, ey2+3), (ex2+3, ey2-3)], fill=(200, 50, 40, 255), width=2)

    head_canvas = Image.new('RGBA', (target_w + 30, target_h + 30), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(head_canvas)
    head_canvas.paste(face_scaled, (15, 18), face_scaled)

    # Crown on head canvas
    draw_sultan_crown(h_draw, 15 + target_w//2, 10, width=28, height=13, is_flaming=False)

    # Tilt head -12 degrees
    head_tilted = head_canvas.rotate(-12, resample=Image.Resampling.BICUBIC, expand=True)
    sprite.paste(head_tilted, (46 - head_tilted.width//2, 12), head_tilted)

    # Dizzy stars
    def draw_star(cx, cy, r, color):
        pts = [
            (cx, cy - r), (cx + r*0.3, cy - r*0.3),
            (cx + r, cy), (cx + r*0.3, cy + r*0.3),
            (cx, cy + r), (cx - r*0.3, cy + r*0.3),
            (cx - r, cy), (cx - r*0.3, cy - r*0.3)
        ]
        draw.polygon(pts, fill=color)

    draw_star(32, 16, 6, (241, 196, 15, 255))
    draw_star(58, 8, 7, (243, 156, 18, 255))
    draw_star(80, 16, 5, (241, 196, 15, 255))

    return sprite

if __name__ == '__main__':
    normal = create_fargol_standing(is_flame=False)
    normal.save('public/images/fargol_body.png')
    normal.save('scratch/fargol_body.png')

    flame = create_fargol_standing(is_flame=True)
    flame.save('public/images/fargol_body_flame.png')
    flame.save('scratch/fargol_body_flame.png')

    died = create_fargol_died()
    died.save('public/images/fargol_died.png')
    died.save('scratch/fargol_died.png')

    print('Fargol sprites created with high detail!')
