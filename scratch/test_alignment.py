from PIL import Image

im_idle = Image.open('public/images/fargol_body.png') # 132 x 214
print("Idle size:", im_idle.size)

im_chop = Image.open('scratch/chop_normal_extracted.png') # 921 x 696
print("Chop size:", im_chop.size)

im_flame_chop = Image.open('scratch/chop_flame_extracted.png') # 941 x 818
print("Flame chop size:", im_flame_chop.size)

