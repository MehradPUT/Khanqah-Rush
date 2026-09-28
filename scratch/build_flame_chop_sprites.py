from PIL import Image

flame_idle = Image.open('public/images/fargol_body_flame.png') # 165 x 218
flame_chop = Image.open('scratch/chop_flame_extracted.png') # 941 x 818
scale = 0.265
flame_chop_s = flame_chop.resize((int(flame_chop.width * scale), int(flame_chop.height * scale)), Image.Resampling.LANCZOS)
print("Flame chop scaled:", flame_chop_s.size) # (249, 216)

# In test_flame_overlay, offset_x=20 looked fantastic!
# When flame_idle is at x=50, and flame_chop_s is at x=20:
# That means flame_chop starts (50 - 20) = 30 pixels to the left of flame_idle's left edge!
# And flame_chop ends at 20 + 249 = 269.
# Since flame_idle's left edge is at 50, flame_chop ends at 269 - 50 = 219 pixels to the right of flame_idle's left edge!
# Total width = 30 + 249 = 279!
# At 0.5 render scale:
# Width in game = 279 * 0.5 = 139.5 (or 140px)!
# Shift to left = 30 * 0.5 = 15px (sa.x = -15)!
# Height in game = 109px (218 * 0.5)!
