from PIL import Image

flame_idle = Image.open('public/images/fargol_body_flame.png') # 165 x 218
flame_chop = Image.open('scratch/chop_flame_extracted.png') # 941 x 818

scale = 0.265
flame_chop_s = flame_chop.resize((int(flame_chop.width * scale), int(flame_chop.height * scale)), Image.Resampling.LANCZOS)

canvas_w = 320
canvas_h = 230

# In flame_idle (165x218), her foot is at y=217 (height 218)
# Let's put flame_idle at x=50, y=canvas_h - flame_idle.height (y=12, feet at y=229)
idle_canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
idle_canvas.paste(flame_idle, (50, canvas_h - flame_idle.height), flame_idle)

for offset_x in [10, 20, 30]:
    c_test = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    paste_y = canvas_h - flame_chop_s.height
    c_test.paste(flame_chop_s, (offset_x, paste_y), flame_chop_s)
    
    overlay = Image.blend(idle_canvas.convert('RGBA'), c_test.convert('RGBA'), 0.5)
    overlay.save(f'scratch/flame_overlay_{offset_x}.png')
    print(f"Saved scratch/flame_overlay_{offset_x}.png")

