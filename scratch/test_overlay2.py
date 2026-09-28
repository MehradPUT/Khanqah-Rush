from PIL import Image

idle = Image.open('public/images/fargol_body.png') # 132 x 214
chop = Image.open('scratch/chop_normal_extracted.png') # 921 x 696
flame_chop = Image.open('scratch/chop_flame_extracted.png') # 941 x 818

scale = 0.265
chop_s = chop.resize((int(chop.width * scale), int(chop.height * scale)), Image.Resampling.LANCZOS)
print("Chop scaled:", chop_s.size)

canvas_w = 300
canvas_h = 220

# Place idle on canvas:
# In idle, feet are at y=213, body center around x=66
idle_canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
# Let's put idle at x=50, y=canvas_h - idle.height (y=6, feet at y=219)
idle_canvas.paste(idle, (50, canvas_h - idle.height), idle)

# Now test placing chop_s:
# Feet in chop_s are at chop_s.height - 1. We want feet at canvas_h - 1 (y=219)!
paste_y = canvas_h - chop_s.height

for offset_x in [15, 25, 35]:
    c_test = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    c_test.paste(chop_s, (offset_x, paste_y), chop_s)
    
    overlay = Image.blend(idle_canvas.convert('RGBA'), c_test.convert('RGBA'), 0.5)
    overlay.save(f'scratch/overlay2_test_{offset_x}.png')
    print(f"Saved scratch/overlay2_test_{offset_x}.png")

