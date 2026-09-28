with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

old_card = r'<div class="char-carousel-card" id="char_carousel_card" title="کلیک برای تغییر قهرمان">.*?</div>\s*</div>\s*<div class="char-card-desc" id="char_card_desc" style="display: none;"></div>\s*</div>'
new_card = """<div class="char-carousel-card" id="char_carousel_card" title="کلیک برای تغییر قهرمان" style="display:flex; justify-content:center; align-items:center;">
                <span class="char-card-name" id="char_card_name" style="display:block; width:100%; text-align:center; direction:ltr; margin:0; padding:0; font-family:'Arial Black', Impact, sans-serif; font-size:17px; font-weight:900; color:#fff;">Nima (نیما)</span>
              </div>"""

html = re.sub(old_card, new_card, html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html card simplified")
