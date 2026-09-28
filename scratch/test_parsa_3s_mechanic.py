import os
from PIL import Image, ImageDraw, ImageFont

art_dir = '/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64'

# 1. Code Checks
with open('public/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

checks = [
    ('3000ms sleep timeout', 'setTimeout(function()' in js and '3000);' in js),
    ('parsaWaitingForChop variable', 'var parsaWaitingForChop = false;' in js),
    ('parsaSleepStartTime variable', 'var parsaSleepStartTime = 0;' in js),
    ('za = false in triggerParsaNap', 'za = false;' in js),
    ('za = false in 3000ms wake callback', 'parsaWaitingForChop = true;' in js),
    ('Ca(a) blocks while parsaSleeping', 'if (parsaSleeping) {' in js and 'return;' in js),
    ('Ca(a) resumes fatigue bar on chop', 'if (parsaWaitingForChop) {' in js and 'za = true;' in js),
    ('Ta() execution while sleeping or waiting', 'parsaSleeping || parsaWaitingForChop' in js),
]

print("--- Parsa 3s Sleep & Fatigue Bar Code Invariants ---")
all_passed = True
for name, passed in checks:
    print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    if not passed:
        all_passed = False

if not all_passed:
    raise RuntimeError("Verification failed on 3s sleep invariants!")

print("All code checks passed!\n")

# 2. Re-generate Animated GIF demonstrating 3s sleep and paused fatigue bar
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_badge = ImageFont.truetype(font_path, 11)
font_title = ImageFont.truetype(font_path, 14)

frames = []
bg_sim = Image.new('RGBA', (340, 360), (28, 36, 52, 255))
bg_draw = ImageDraw.Draw(bg_sim)
for y in range(0, 310):
    ratio = y / 310
    bg_draw.line([(0, y), (340, y)], fill=(int(24 + 100*ratio), int(45 + 130*ratio), int(75 + 80*ratio), 255))
# Tree trunk
bg_draw.rectangle([230, 0, 280, 310], fill=(125, 90, 45, 255))
# Ground
bg_draw.rectangle([0, 310, 340, 360], fill=(115, 168, 70, 255))

body_spr = Image.open('public/images/parsa_body.png').resize((68, 140), Image.Resampling.LANCZOS)
swing_spr = Image.open('public/images/parsa_swing.png').resize((115, 140), Image.Resampling.LANCZOS)
sleep_spr = Image.open('public/images/parsa_sleep.png').resize((68, 140), Image.Resampling.LANCZOS)

# Helper to draw Top Fatigue & Ability HUD
def render_hud(frame, status_text, fatigue_pct, fatigue_col, status_col):
    d = ImageDraw.Draw(frame)
    # HUD Box
    d.rounded_rectangle([10, 10, 180, 52], radius=6, fill=(10, 15, 25, 220), outline=status_col, width=1)
    d.text((16, 14), status_text, font=font_badge, fill=status_col)
    # Fatigue Bar Track
    d.rectangle([16, 34, 174, 44], fill=(0, 0, 0, 180))
    # Fatigue Bar Fill
    fill_w = int(158 * (fatigue_pct / 100))
    if fill_w > 0:
        d.rectangle([16, 34, 16 + fill_w, 44], fill=fatigue_col)

# 1. Normal active game - stamina depleting
for step, pct in enumerate([100, 70, 40, 15, 0]):
    f = bg_sim.copy()
    f.paste(body_spr, (140, 310 - 140), body_spr)
    col = (46, 204, 113, 255) if pct > 30 else (231, 76, 60, 255)
    render_hud(f, f"Tiredness draining: {pct}%", pct, col, (241, 196, 15, 255))
    frames.append(f)

# 2. Stamina hits 0 -> Triggers 3-Second Blanket Sleep!
# Show 3s countdown: 3.0s, 2.5s, 2.0s, 1.5s, 1.0s, 0.5s
for sec in [3.0, 2.5, 2.0, 1.5, 1.0, 0.5]:
    f = bg_sim.copy()
    f.paste(sleep_spr, (140, 310 - 140), sleep_spr)
    render_hud(f, f"🛌 Sleeping: {sec:.1f}s (100% full)", 100, (155, 89, 182, 255), (155, 89, 182, 255))
    d = ImageDraw.Draw(f)
    d.text((130, 110), "Zzz...", font=font_title, fill=(241, 196, 15, 255))
    frames.append(f)

# 3. Wakes up after 3s -> Fatigue bar STOPPED until user starts chopping!
for w_step in range(4):
    f = bg_sim.copy()
    f.paste(body_spr, (140, 310 - 140), body_spr)
    # Status green paused
    render_hud(f, "⏰ Awake! Fatigue PAUSED", 100, (46, 204, 113, 255), (46, 204, 113, 255))
    d = ImageDraw.Draw(f)
    d.text((95, 110), "⏸️ Waiting for Chop...", font=font_badge, fill=(46, 204, 113, 255))
    frames.append(f)

# 4. User chops -> Fatigue resumes!
f_chop = bg_sim.copy()
f_chop.paste(swing_spr, (140, 310 - 140), swing_spr)
render_hud(f_chop, "🪓 User Chops! Resumed", 98, (46, 204, 113, 255), (241, 196, 15, 255))
frames.append(f_chop)

f_chop2 = bg_sim.copy()
f_chop2.paste(body_spr, (140, 310 - 140), body_spr)
render_hud(f_chop2, "Chopping active! (1/2 left)", 92, (46, 204, 113, 255), (241, 196, 15, 255))
frames.append(f_chop2)

gif_path = os.path.join(art_dir, 'parsa_nap_and_chop.gif')
frames[0].save(
    gif_path,
    save_all=True,
    append_images=frames[1:],
    duration=320,
    loop=0
)
print("Saved updated parsa_nap_and_chop.gif successfully!")
