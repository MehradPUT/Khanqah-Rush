from PIL import Image, ImageOps

idle = Image.open('public/images/fargol_body.png') # 132 x 214
chop = Image.open('scratch/chop_normal_extracted.png') # 921 x 696
flame_chop = Image.open('scratch/chop_flame_extracted.png') # 941 x 818

# Let's scale chop so crown/head matches idle
scale = 0.202
scaled_w = int(chop.width * scale)
scaled_h = int(chop.height * scale)
chop_scaled = chop.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
print("Chop scaled size:", chop_scaled.size)

# Let's find foot bottom in chop_scaled
foot_y_chop = chop_scaled.height - 1
for y in range(chop_scaled.height - 1, -1, -1):
    if any(chop_scaled.getpixel((x, y))[3] > 64 for x in range(chop_scaled.width)):
        foot_y_chop = y
        break

# In idle: foot bottom is at y = 213 (height is 214)
# We want the foot bottom in chop to land at y = 213 as well!
# So canvas height = 214!
# Where does chop_scaled need to be pasted vertically?
paste_y = 213 - foot_y_chop
print(f"foot_y_chop: {foot_y_chop}, paste_y: {paste_y}")

# Now where should it be placed horizontally?
# In idle, head center is at x = 61.
# In chop_scaled, let's find head center:
head_pts = []
for y in range(max(0, 20 - paste_y), min(chop_scaled.height, 80 - paste_y)):
    for x in range(int(chop_scaled.width * 0.4), int(chop_scaled.width * 0.7)):
        if chop_scaled.getpixel((x, y))[3] > 64:
            head_pts.append(x)
chop_head_x = sum(head_pts) / len(head_pts) if head_pts else chop_scaled.width // 2
print(f"chop_head_x: {chop_head_x}")

# In a forward swing, she leans forward slightly towards the tree (+8 to +12px)
target_head_x = 61 + 10 # 71
paste_x = int(target_head_x - chop_head_x)
print(f"paste_x: {paste_x}")

# If paste_x < 0, her cape would stick out to the left!
# Let's check how far left the cape goes:
# If paste_x is negative, say -20, that means her cape extends 20px to the left of x=0.
# If we keep x=0 aligned, we can either:
# Option A: Allow paste_x >= 0 by shifting the canvas and setting sa.x = -shift in game during chop
# Option B: Make canvas wide enough, and test paste_x.
