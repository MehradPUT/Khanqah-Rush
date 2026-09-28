from PIL import Image

idle = Image.open('public/images/fargol_body.png') # 132 x 214
chop = Image.open('scratch/chop_normal_extracted.png') # 921 x 696

# In idle:
# Crown top is at y=0.
# Let's find chin in idle:
# In idle, chin is around y=48.
# Crown top to chin = ~48 pixels!

# In chop:
# Crown top is at y=0.
# Where is chin in chop?
# Let's inspect rows around x=530 in chop:
for y in range(0, 300, 10):
    # check color at (530, y)
    print(f"y={y}: {chop.getpixel((530, y))}")

