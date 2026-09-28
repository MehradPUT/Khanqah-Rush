with open('scratch/patch_lumberjack.py', 'r') as f:
    code = f.read()

old_list = 'fargol_normal:"images/fargol_body.png",fargol_flame:"images/fargol_body_flame.png",fargol_died:"images/fargol_died.png"'
new_list = 'fargol_normal:"images/fargol_body.png",fargol_swing:"images/fargol_swing.png",fargol_flame:"images/fargol_body_flame.png",fargol_swing_flame:"images/fargol_swing_flame.png",fargol_died:"images/fargol_died.png"'

code = code.replace(old_list, new_list)

with open('scratch/patch_lumberjack.py', 'w') as f:
    f.write(code)

print("Asset loading updated.")
