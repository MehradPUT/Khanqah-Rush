from PIL import Image

# 1. NORMAL CHOP
chop_norm = Image.open('scratch/chop_normal_extracted.png') # 921 x 696
scale_norm = 0.265
chop_norm_scaled = chop_norm.resize((int(chop_norm.width * scale_norm), int(chop_norm.height * scale_norm)), Image.Resampling.LANCZOS)
print("Normal chop scaled:", chop_norm_scaled.size) # (244, 184)

# In overlay2_test_25:
# idle was placed at x = 50.
# chop was placed at x = 25.
# That means chop starts 25 pixels to the left of idle's left edge (x=0).
# And chop ends at 25 + 244 = 269.
# Since idle's left edge is at 50, chop's right edge is at 269 - 50 = 219 pixels to the right of idle's left edge!
# If we define the canvas for chop to have the EXACT same left origin as idle:
# Wait! Can a canvas have content to the left of x=0?
# A PNG image always has positive pixel coordinates [0 .. W-1].
# If we place chop on a canvas of width W = 25 + 244 = 269:
# Then x = 25 is where idle's x=0 would be!
# If x = 25 is idle's x=0, then in game:
# When idle renders at width 66 (from texture width 132):
# The ratio is 0.5 (66 / 132).
# So in game coordinates:
# The 25px offset to the left is 25 * 0.5 = 12.5px (or 13px)!
# Total render width of chop in game = 269 * 0.5 = 134.5px (or 135px)!
# And sa.x during chop = -12.5px (or -13px)!
# Anchor stays (0, 1)!
# Feet Y stays at y = 1!
# Sa.height stays 107px!

# Let's test this in Python!
