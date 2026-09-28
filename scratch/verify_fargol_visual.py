import os
from PIL import Image, ImageDraw

art_dir = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64'

b_norm = Image.open('public/images/fargol_body.png')
s_norm = Image.open('public/images/fargol_swing.png')
b_flame = Image.open('public/images/fargol_body_flame.png')
s_flame = Image.open('public/images/fargol_swing_flame.png')
d_norm = Image.open('public/images/fargol_died.png')

comp = Image.new('RGBA', (600, 200), (40, 40, 60, 255))
d = ImageDraw.Draw(comp)

def paste_w_bg(img, x, y, cw, ch):
    d.rectangle([x, y, x + cw, y + ch], outline=(100,255,100,255))
    comp.paste(img, (x, y + ch - img.height), img)

paste_w_bg(b_norm, 10, 30, 94, 140)
paste_w_bg(s_norm, 120, 30, 120, 140)
paste_w_bg(b_flame, 260, 30, 94, 140)
paste_w_bg(s_flame, 370, 30, 120, 140)
paste_w_bg(d_norm, 500, 59, 95, 111)

d.text((30, 10), "Normal")
d.text((150, 10), "Swing")
d.text((280, 10), "Flame")
d.text((400, 10), "Flame Swing")
d.text((520, 30), "Died")

comp_path = os.path.join(art_dir, 'fargol_new_verify.png')
comp.save(comp_path)
print("Saved verification composite!")
