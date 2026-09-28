from PIL import Image, ImageDraw

def clean_head(img_path):
    im = Image.open(img_path).convert('RGBA')
    w, h = im.size
    # Crop off old wide shirt shoulders (chin/neck ends around y=134)
    return im.crop((0, 0, w, 134))

def create_nima_standing(face_img, is_young=False):
    fw, fh = face_img.size
    sprite = Image.new('RGBA', (100, 214), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound at bottom
    draw.rounded_rectangle([0, 174, 100, 214], radius=19, fill=(153, 204, 102, 255))

    # 2. Sneakers
    # Left sneaker
    draw.rounded_rectangle([32, 186, 48, 198], radius=3, fill=(26, 26, 26, 255))
    draw.rectangle([32, 194, 48, 198], fill=(245, 245, 245, 255))
    # Right sneaker
    draw.rounded_rectangle([52, 186, 68, 198], radius=3, fill=(26, 26, 26, 255))
    draw.rectangle([52, 194, 68, 198], fill=(245, 245, 245, 255))

    # 3. Skinny Blue Jeans
    # Pelvis: x from 33 to 67, y from 124 to 148
    draw.rounded_rectangle([33, 124, 67, 148], radius=4, fill=(43, 96, 138, 255))
    # Left leg
    draw.rounded_rectangle([34, 140, 47, 188], radius=3, fill=(43, 96, 138, 255))
    draw.line([(37, 144), (37, 184)], fill=(59, 130, 182, 255), width=2)
    draw.line([(46, 140), (46, 187)], fill=(27, 68, 104, 255), width=1)
    # Right leg
    draw.rounded_rectangle([53, 140, 66, 188], radius=3, fill=(43, 96, 138, 255))
    draw.line([(56, 144), (56, 184)], fill=(59, 130, 182, 255), width=2)
    draw.line([(53, 140), (53, 187)], fill=(27, 68, 104, 255), width=1)
    # Fly & pocket lines
    draw.line([(50, 124), (50, 140)], fill=(20, 50, 80, 255), width=2)
    draw.line([(36, 128), (43, 133)], fill=(20, 50, 80, 255), width=1)
    draw.line([(64, 128), (57, 133)], fill=(20, 50, 80, 255), width=1)

    # 4. Skinny T-shirt
    # Total torso y: 52 to 126 (height 74px)
    # Torso width: 34px (x from 33 to 67)
    
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

    # 5. Face
    target_fh = 55
    target_fw = int(fw * (target_fh / fh))
    face_scaled = face_img.resize((target_fw, target_fh), Image.Resampling.NEAREST)
    face_x = 50 - (target_fw // 2)
    face_y = 0
    sprite.paste(face_scaled, (face_x, face_y), face_scaled)

    # In Young phase, add flame aura
    if is_young:
        aura = Image.new('RGBA', (100, 214), (0, 0, 0, 0))
        aura_draw = ImageDraw.Draw(aura)
        aura_draw.ellipse([18, 12, 82, 168], fill=(231, 76, 60, 40), outline=(243, 156, 18, 110), width=2)
        sprite = Image.alpha_composite(aura, sprite)

    return sprite

def create_nima_died(face_img, is_young=False):
    fw, fh = face_img.size
    sprite = Image.new('RGBA', (141, 170), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    # 1. Grass mound
    draw.rounded_rectangle([3, 130, 103, 170], radius=19, fill=(153, 204, 102, 255))

    # 2. Fallen Axe on right
    # Handle
    draw.rounded_rectangle([38, 127, 132, 139], radius=6, fill=(130, 95, 49, 255))
    # Head
    draw.rectangle([111, 127, 141, 157], fill=(206, 69, 58, 255))
    # Blade
    draw.rectangle([111, 157, 141, 169], fill=(255, 255, 255, 255))

    # 3. Slumped Skinny Blue Jeans
    # Pelvis
    draw.rounded_rectangle([24, 116, 68, 142], radius=6, fill=(43, 96, 138, 255))
    # Left leg forward
    draw.rounded_rectangle([20, 134, 42, 154], radius=4, fill=(43, 96, 138, 255))
    draw.line([(24, 136), (24, 150)], fill=(59, 130, 182, 255), width=2)
    # Right leg forward
    draw.rounded_rectangle([46, 134, 68, 154], radius=4, fill=(43, 96, 138, 255))
    draw.line([(50, 136), (50, 150)], fill=(59, 130, 182, 255), width=2)

    # Sneakers
    # Left sneaker
    draw.rounded_rectangle([18, 148, 42, 164], radius=3, fill=(26, 26, 26, 255))
    draw.rectangle([18, 158, 42, 164], fill=(245, 245, 245, 255))
    # Right sneaker
    draw.rounded_rectangle([46, 148, 70, 164], radius=3, fill=(26, 26, 26, 255))
    draw.rectangle([46, 158, 70, 164], fill=(245, 245, 245, 255))

    # 4. Skinny T-shirt (slumped torso)
    # Width 36px (x from 28 to 64), y from 58 to 120 (height 62px)
    # Bottom half: Gray (y from 89 to 120, height 31px)
    draw.rounded_rectangle([28, 89, 64, 120], radius=3, fill=(120, 120, 128, 255))
    draw.line([(28, 119), (64, 119)], fill=(85, 85, 92, 255), width=2)

    # Top half: y from 58 to 89 (height 31px)
    # Top 75% of top half: y from 58 to 81 -> BLACK
    draw.rounded_rectangle([28, 58, 64, 81], radius=3, fill=(22, 22, 24, 255))
    # Bottom 25% of top half: y from 81 to 89 -> WHITE
    draw.rectangle([28, 81, 64, 89], fill=(248, 248, 250, 255))
    draw.line([(28, 81), (64, 81)], fill=(180, 180, 185, 255), width=1)
    draw.line([(28, 89), (64, 89)], fill=(140, 140, 145, 255), width=1)

    # Sleeves (black)
    draw.rounded_rectangle([22, 60, 28, 80], radius=2, fill=(22, 22, 24, 255))
    draw.rounded_rectangle([64, 60, 70, 80], radius=2, fill=(22, 22, 24, 255))

    # Limp skinny arms (skin tone #DFAC9B, NO TATTOOS)
    draw.rounded_rectangle([21, 80, 27, 118], radius=3, fill=(223, 172, 155, 255))
    draw.rounded_rectangle([65, 80, 71, 118], radius=3, fill=(223, 172, 155, 255))
    # Hands resting limp on grass
    draw.rounded_rectangle([19, 115, 27, 128], radius=4, fill=(223, 172, 155, 255))
    draw.rounded_rectangle([65, 115, 73, 128], radius=4, fill=(223, 172, 155, 255))

    # 5. Knocked out Head
    target_fh = 55
    target_fw = int(fw * (target_fh / fh))
    face_scaled = face_img.copy().resize((target_fw, target_fh), Image.Resampling.NEAREST)

    f_draw = ImageDraw.Draw(face_scaled)
    ex1, ey1 = int(target_fw * 0.38), int(target_fh * 0.40)
    ex2, ey2 = int(target_fw * 0.68), int(target_fh * 0.40)
    eye_col = (180, 50, 40, 255) if not is_young else (220, 60, 50, 255)
    f_draw.line([(ex1 - 4, ey1 - 4), (ex1 + 4, ey1 + 4)], fill=eye_col, width=2)
    f_draw.line([(ex1 - 4, ey1 + 4), (ex1 + 4, ey1 - 4)], fill=eye_col, width=2)
    f_draw.line([(ex2 - 4, ey2 - 4), (ex2 + 4, ey2 + 4)], fill=eye_col, width=2)
    f_draw.line([(ex2 - 4, ey2 + 4), (ex2 + 4, ey2 - 4)], fill=eye_col, width=2)

    face_tilted = face_scaled.rotate(-10, resample=Image.Resampling.BICUBIC, expand=True)
    sprite.paste(face_tilted, (46 - (face_tilted.width // 2), 6), face_tilted)

    # 6. Dizzy Stars / Sparkles
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

face_young = clean_head('scratch/face_cropped.png')
face_old = clean_head('scratch/face_old.png')

# 1. Standing sprites
standing_old = create_nima_standing(face_old, is_young=False)
standing_old.save('public/images/nima_body_old.png')

standing_young = create_nima_standing(face_young, is_young=True)
standing_young.save('public/images/nima_body_young.png')

# 2. Died sprites
died_old = create_nima_died(face_old, is_young=False)
died_old.save('public/images/nima_died_old.png')

died_young = create_nima_died(face_young, is_young=True)
died_young.save('public/images/nima_died_young.png')

print('Successfully generated all 4 Nima sprites!')
