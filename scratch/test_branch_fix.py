import os
from PIL import Image, ImageDraw, ImageFont

art_dir = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64'
body = Image.open('public/images/amirhossein_body.png').convert('RGBA').resize((68, 140), Image.Resampling.LANCZOS)

# Create two comparison panels:
# Left: Before (branch at -pa, overlapping head by 25px)
# Right: After (branch at -pa - 40, clearing head by 15px)

w, h = 640, 520
img = Image.new('RGBA', (w, h), (18, 26, 42, 255))
draw = ImageDraw.Draw(img)

font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_title = ImageFont.truetype(font_path, 15)
font_lbl = ImageFont.truetype(font_path, 12)
font_badge = ImageFont.truetype(font_path, 11)

draw.rectangle([0, 0, w, 50], fill=(13, 20, 32, 255))
draw.text((20, 16), "Branch Clearance Fix Comparison (Amirhossein 140px Height)", font=font_title, fill=(255, 215, 0, 255))

ground_y = 440

for panel_idx, (title, shift, color) in enumerate([("BEFORE: Branch Collides (-pa / Clearance 115px)", 0, (231, 76, 60, 255)),
                                                   ("AFTER: Branch Clears (-pa - 40px / Clearance 155px)", 40, (46, 204, 113, 255))]):
    ox = panel_idx * 320

    # Sky
    for y in range(51, ground_y):
        ratio = (y - 51) / (ground_y - 51)
        r = int(24 + (130 - 24) * ratio)
        g = int(45 + (185 - 45) * ratio)
        b = int(75 + (165 - 75) * ratio)
        draw.line([(ox, y), (ox + 320, y)], fill=(r, g, b, 255))

    # Ground
    draw.rectangle([ox, ground_y, ox + 320, h], fill=(115, 168, 70, 255))
    draw.line([(ox, ground_y), (ox + 320, ground_y)], fill=(90, 140, 50, 255), width=3)

    # Trunk
    tx1, tx2 = ox + 110, ox + 160
    draw.rectangle([tx1, 51, tx2, ground_y], fill=(125, 90, 45, 255))

    # Character (feet at ground_y, height 140)
    char_x = tx2 + 10
    char_y = ground_y - 140
    img.paste(body, (char_x, char_y), body)

    # Branch at da[0]:
    # In Pixi: bottom of sprite is at (ground_y - 100 - shift)
    # The wood arm is 15px above bottom of sprite -> wood_arm_y = (ground_y - 115 - shift)
    # The branch wood arm goes from tx2 to tx2 + 75
    br_base_y = ground_y - 100 - shift
    wood_arm_y = br_base_y - 15

    # Draw branch wood
    draw.line([(tx2, br_base_y), (tx2 + 45, wood_arm_y)], fill=(138, 99, 50, 255), width=18)
    draw.line([(tx2 + 35, wood_arm_y), (tx2 + 80, wood_arm_y)], fill=(138, 99, 50, 255), width=14)
    draw.line([(tx2 + 70, wood_arm_y), (tx2 + 80, wood_arm_y - 25)], fill=(138, 99, 50, 255), width=14)

    # Foliage puffs
    draw.ellipse([tx2 + 40, wood_arm_y - 45, tx2 + 115, wood_arm_y - 5], fill=(126, 173, 79, 240))
    draw.ellipse([tx2 + 55, wood_arm_y - 58, tx2 + 105, wood_arm_y - 20], fill=(153, 204, 102, 240))
    draw.ellipse([tx2 + 65, wood_arm_y - 68, tx2 + 95, wood_arm_y - 35], fill=(175, 221, 127, 240))

    # Panel header & badge
    draw.rectangle([ox + 10, 60, ox + 310, 88], fill=(13, 20, 32, 230))
    draw.text((ox + 15, 66), title, font=font_lbl, fill=color)

    # Clearance annotation line
    head_y = ground_y - 140
    if shift == 0:
        # Show collision overlap
        draw.line([(char_x - 8, head_y), (char_x + 75, head_y)], fill=(255, 50, 50, 255), width=2)
        draw.text((ox + 20, ground_y + 15), "COLLISION: Head penetrates branch by 25px!", font=font_badge, fill=(255, 100, 100, 255))
        draw.text((ox + 20, ground_y + 35), "Head: 140px | Clearance: 115px", font=font_badge, fill=(200, 200, 200, 255))
    else:
        # Show clean clearance
        draw.line([(char_x - 8, head_y), (char_x + 75, head_y)], fill=(46, 204, 113, 255), width=1)
        draw.line([(char_x - 8, wood_arm_y), (char_x + 75, wood_arm_y)], fill=(255, 215, 0, 255), width=1)
        draw.text((ox + 20, ground_y + 15), "FIXED: Clean +15px clearance above head!", font=font_badge, fill=(46, 204, 113, 255))
        draw.text((ox + 20, ground_y + 35), "Head: 140px | Clearance: 155px (+40px shift)", font=font_badge, fill=(255, 215, 0, 255))

    # Divider
    if panel_idx > 0:
        draw.line([(ox, 50), (ox, h)], fill=(41, 128, 185, 150), width=2)

out_path = os.path.join(art_dir, 'branch_clearance_fix_comparison.png')
img.save(out_path)
print('Saved to', out_path)
