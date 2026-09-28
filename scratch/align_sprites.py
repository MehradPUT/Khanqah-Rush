from PIL import Image

idle = Image.open('public/images/fargol_body.png') # 132 x 214
chop = Image.open('scratch/chop_normal_extracted.png') # 921 x 696

# Let's inspect the bounding box of idle and chop
print("Idle size:", idle.size)
print("Chop size:", chop.size)

# In idle (132x214):
# Character foot Y is at y=213.
# Character foot X is around x=32 to x=116.
# Let's find the head center in idle:
# Crown top is at y=0, band at y=26, chin around y=50.
# Head X bounds in idle:
head_rows = []
for y in range(10, 40):
    row = [x for x in range(idle.width) if idle.getpixel((x, y))[3] > 64]
    if row:
        head_rows.extend(row)
print("Idle head X center:", sum(head_rows)/len(head_rows))

# In chop:
# Let's find head X bounds in chop (crown is around y=10 to y=80):
chop_head_rows = []
for y in range(20, 80):
    # Head is between x=400 and x=700 (ignoring slash on right)
    row = [x for x in range(400, 700) if chop.getpixel((x, y))[3] > 64]
    if row:
        chop_head_rows.extend(row)
print("Chop head X center:", sum(chop_head_rows)/len(chop_head_rows))

