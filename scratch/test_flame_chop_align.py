from PIL import Image

flame_idle = Image.open('public/images/fargol_body_flame.png') # 165 x 218
flame_chop = Image.open('scratch/chop_flame_extracted.png') # 941 x 818
norm_chop = Image.open('scratch/chop_normal_extracted.png') # 921 x 696

print("Flame idle size:", flame_idle.size)
print("Flame chop size:", flame_chop.size)

# In flame_chop, notice the crown fire reaches high up
# Let's scale flame_chop with the exact same scale as normal chop (0.265)
scale = 0.265
flame_chop_s = flame_chop.resize((int(flame_chop.width * scale), int(flame_chop.height * scale)), Image.Resampling.LANCZOS)
print("Flame chop scaled size:", flame_chop_s.size)

# Let's check foot bottom in flame_chop_s
foot_y = flame_chop_s.height - 1
for y in range(flame_chop_s.height - 1, -1, -1):
    if any(flame_chop_s.getpixel((x, y))[3] > 64 for x in range(flame_chop_s.width)):
        foot_y = y
        break
print(f"Foot Y in flame_chop_s: {foot_y} out of {flame_chop_s.height}")

