from PIL import Image

# 1. Normal Chop Sprite
chop_norm = Image.open('scratch/chop_normal_extracted.png') # 921 x 696
scale_norm = 0.265
scaled_norm = chop_norm.resize((int(chop_norm.width * scale_norm), int(chop_norm.height * scale_norm)), Image.Resampling.LANCZOS)
print("Normal chop scaled size:", scaled_norm.size) # (244, 184)

# Create canvas of height 214 so vertical scale (107/214 = 0.5) exactly matches idle
canvas_norm = Image.new('RGBA', (scaled_norm.width, 214), (0, 0, 0, 0))
# Paste so foot touches the bottom (y = 214 - scaled_norm.height)
paste_y_norm = 214 - scaled_norm.height
canvas_norm.paste(scaled_norm, (0, paste_y_norm), scaled_norm)
canvas_norm.save('public/images/fargol_body_chop.png')
canvas_norm.save('scratch/fargol_body_chop.png')
print("Saved public/images/fargol_body_chop.png with size", canvas_norm.size)

# 2. Flame Chop Sprite
chop_flame = Image.open('scratch/chop_flame_extracted.png') # 941 x 818
scale_flame = 0.265
scaled_flame = chop_flame.resize((int(chop_flame.width * scale_flame), int(chop_flame.height * scale_flame)), Image.Resampling.LANCZOS)
print("Flame chop scaled size:", scaled_flame.size) # (249, 216)

# Create canvas of height 218 so vertical scale (109/218 = 0.5) matches flame idle
canvas_flame = Image.new('RGBA', (scaled_flame.width, 218), (0, 0, 0, 0))
paste_y_flame = 218 - scaled_flame.height
canvas_flame.paste(scaled_flame, (0, paste_y_flame), scaled_flame)
canvas_flame.save('public/images/fargol_body_flame_chop.png')
canvas_flame.save('scratch/fargol_body_flame_chop.png')
print("Saved public/images/fargol_body_flame_chop.png with size", canvas_flame.size)

