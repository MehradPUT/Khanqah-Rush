from PIL import Image, ImageDraw, ImageFont
import os

width = 640
height = 360

# Background sky with forest gradient
banner = Image.new("RGBA", (width, height), (199, 240, 249, 255))
draw = ImageDraw.Draw(banner)

# Ground
draw.rectangle([0, 260, width, height], fill=(145, 102, 74, 255))
draw.rectangle([0, 240, width, 260], fill=(174, 221, 127, 255))

# Tree in center
trunk_x = width // 2 - 35
draw.rectangle([trunk_x, 0, trunk_x + 70, 260], fill=(161, 116, 56, 255))
# Bark streaks
draw.rectangle([trunk_x + 15, 0, trunk_x + 28, 260], fill=(186, 140, 77, 255))
draw.rectangle([trunk_x + 45, 0, trunk_x + 55, 260], fill=(130, 95, 49, 255))

# Branches
draw.rectangle([trunk_x - 80, 80, trunk_x, 115], fill=(161, 116, 56, 255))
draw.rectangle([trunk_x + 70, 150, trunk_x + 150, 185], fill=(161, 116, 56, 255))
# Leaves on branches
draw.ellipse([trunk_x - 120, 60, trunk_x - 60, 135], fill=(126, 173, 79, 255))
draw.ellipse([trunk_x + 130, 130, trunk_x + 190, 205], fill=(126, 173, 79, 255))

# Paste heroes if available
def paste_sprite(img_path, pos, scale=1.0, flip=False):
    if os.path.exists(img_path):
        sp = Image.open(img_path).convert("RGBA")
        new_w = int(sp.width * scale)
        new_h = int(sp.height * scale)
        sp = sp.resize((new_w, new_h), Image.Resampling.LANCZOS)
        if flip:
            sp = sp.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        banner.paste(sp, pos, sp)

# Left hero: Nima swinging axe
paste_sprite("public/images/nima_swing_young.png", (trunk_x - 130, 120), scale=1.0, flip=False)

# Right hero: Fateme standing
paste_sprite("public/images/fateme_body.png", (trunk_x + 85, 120), scale=1.0, flip=False)

# Far left hero: Fargol Flame
paste_sprite("public/images/fargol_body_flame.png", (20, 120), scale=1.0, flip=False)

# Far right hero: Ali
paste_sprite("public/images/ali_body.png", (width - 90, 120), scale=1.0, flip=True)

# Title overlay banner
# Semi-transparent dark banner at top
overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
o_draw = ImageDraw.Draw(overlay)
o_draw.rectangle([0, 0, width, 55], fill=(22, 22, 24, 200))
banner = Image.alpha_composite(banner, overlay)
draw = ImageDraw.Draw(banner)

# Title text
try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
except:
    font_title = ImageFont.load_default()
    font_sub = ImageFont.load_default()

draw.text((20, 12), "KHANQAH RUSH", fill=(255, 215, 0, 255), font=font_title)
draw.text((width - 240, 20), "8 Heroes • Telegram Lumberjack", fill=(220, 220, 220, 255), font=font_sub)

out_path = "telegram_game_banner.png"
banner.convert("RGB").save(out_path, "PNG")
print(f"Successfully generated 640x360 Telegram Game Banner: {out_path}")
