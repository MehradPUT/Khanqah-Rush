from PIL import Image

idle = Image.open('public/images/fargol_body.png') # 132 x 214
chop = Image.open('scratch/chop_normal_extracted.png') # 921 x 696
flame_chop = Image.open('scratch/chop_flame_extracted.png') # 941 x 818

# Let's test scale
scale = 0.22 # slightly larger for dramatic punch
chop_s = chop.resize((int(chop.width * scale), int(chop.height * scale)), Image.Resampling.LANCZOS)
print("Chop scaled:", chop_s.size)

# Create an overlay canvas
# Let's make a canvas where idle is placed at a known position
canvas_w = 260
canvas_h = 220

# Place idle on canvas:
# In idle, feet are at y=213, body center around x=66
idle_canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
# Let's put idle at x=50, y=0 (feet at y=214)
idle_canvas.paste(idle, (50, canvas_h - idle.height), idle)

# Now place chop on canvas so her front/back foot and head make visual sense:
# In chop_s: foot bottom is at chop_s.height - 1
# We want foot bottom at canvas_h - 1!
chop_canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
# In chop, she lunges forward to the right into the tree
# Let's test various paste_x: 20, 30, 40
for offset_x in [20, 30, 40]:
    c_test = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    paste_y = canvas_h - chop_s.height
    c_test.paste(chop_s, (offset_x, paste_y), chop_s)
    
    # Create an overlay with idle at 50% alpha and chop at 50% alpha
    overlay = Image.blend(idle_canvas.convert('RGBA'), c_test.convert('RGBA'), 0.5)
    overlay.save(f'scratch/overlay_test_{offset_x}.png')
    print(f"Saved scratch/overlay_test_{offset_x}.png")

