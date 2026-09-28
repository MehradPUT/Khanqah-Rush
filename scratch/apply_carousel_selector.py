import re

with open('public/js/main.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update CSS
old_css_start = '    /* CHARACTER SELECTOR BAR ON START & RESULT SCREENS */'
old_css_end = """    .char-tab-btn.active[data-char="erfan"] .char-tab-badge {
      color: #f39c12;
    }"""

new_carousel_css = """    /* CAROUSEL CHARACTER SELECTOR WITH ROTATING ARROWS */
    .char-carousel-wrap {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      margin: 10px auto 6px auto;
      max-width: 360px;
      width: 95%;
      position: relative;
      z-index: 10;
    }

    .char-arrow-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 44px;
      height: 52px;
      background: rgba(20, 26, 40, 0.88);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      border: 1.5px solid rgba(228, 176, 114, 0.45);
      border-radius: 14px;
      cursor: pointer;
      color: #e4b072;
      font-size: 20px;
      transition: all 0.2s cubic-bezier(0.25, 1, 0.5, 1);
      -webkit-tap-highlight-color: transparent;
      outline: none;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
      user-select: none;
    }

    .char-arrow-btn:hover {
      background: rgba(35, 48, 75, 0.95);
      border-color: #f1c40f;
      color: #ffffff;
      box-shadow: 0 0 14px rgba(241, 196, 15, 0.55);
      transform: translateY(-1px);
    }

    .char-arrow-btn:active {
      transform: scale(0.92);
      border-color: #f39c12;
    }

    .char-carousel-card {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 7px 12px;
      background: rgba(16, 22, 34, 0.92);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border-radius: 14px;
      border: 2px solid rgba(228, 176, 114, 0.6);
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4), 0 0 14px rgba(228, 176, 114, 0.25);
      cursor: pointer;
      transition: all 0.25s ease;
      min-width: 0;
      user-select: none;
      -webkit-tap-highlight-color: transparent;
    }

    .char-carousel-card:hover {
      background: rgba(22, 30, 48, 0.98);
      transform: translateY(-1px);
    }

    .char-carousel-card:active {
      transform: scale(0.98);
    }

    .char-card-header {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .char-card-avatar {
      font-size: 24px;
      line-height: 1;
      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
    }

    .char-card-titles {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }

    .char-card-name {
      font-family: 'Arial Black', Impact, sans-serif;
      font-size: 15px;
      font-weight: 900;
      letter-spacing: 0.5px;
      color: #ffffff;
    }

    .char-card-badge {
      font-family: 'Vazirmatn', sans-serif;
      font-size: 11px;
      font-weight: 800;
      color: #e4b072;
      background: rgba(228, 176, 114, 0.18);
      padding: 2px 7px;
      border-radius: 8px;
      border: 1px solid rgba(228, 176, 114, 0.35);
    }

    .char-card-desc {
      font-family: 'Vazirmatn', sans-serif;
      font-size: 11px;
      font-weight: 600;
      color: #b0bec5;
      margin-top: 3px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      text-align: right;
      direction: rtl;
    }

    /* 7 Carousel Indicator Dots */
    .char-carousel-dots {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      margin-bottom: 12px;
      z-index: 10;
      position: relative;
    }

    .char-carousel-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.25);
      cursor: pointer;
      transition: all 0.25s ease;
    }

    .char-carousel-dot.active {
      width: 18px;
      border-radius: 6px;
      background: #e4b072;
      box-shadow: 0 0 8px #e4b072;
    }"""

# Locate old css chunk
if old_css_start in code and old_css_end in code:
    idx1 = code.find(old_css_start)
    idx2 = code.find(old_css_end) + len(old_css_end)
    code = code[:idx1] + new_carousel_css + code[idx2:]
    print("Replaced CSS.")

# 2. Add ALL_CHARACTERS array before selectCharacter
characters_def = """var ALL_CHARACTERS = [
  {
    id: 'nima',
    name: 'نیما',
    enName: 'Nima',
    avatar: '🧔',
    badge: '⚡ جوانی',
    desc: 'شارژ جوانی هر ۱۵ ثانیه (انرژی ۱۰۰٪ و سرعت)',
    color: '#3498db'
  },
  {
    id: 'fargol',
    name: 'فرگل',
    enName: 'Fargol',
    avatar: '👑',
    badge: '🔥 شعله سلطان',
    desc: '۱۰۰ ضربه = ۵ ثانیه شعله‌ور و شکست‌ناپذیر',
    color: '#e74c3c'
  },
  {
    id: 'ali',
    name: 'علی',
    enName: 'Ali',
    avatar: '👓',
    badge: '🪓 رگبار ۱۰',
    desc: '۵۰ ضربه = رگبار ۱۰ کنده بدون برخورد به شاخه',
    color: '#e67e22'
  },
  {
    id: 'amirhossein',
    name: 'امیرحسین',
    enName: 'Amirhossein',
    avatar: '🧢',
    badge: '⚡ ۲X امتیاز',
    desc: 'امتیاز دوبل (۲ برابر) مداوم برای تمام ضربات',
    color: '#2980b9'
  },
  {
    id: 'parsa',
    name: 'پارسا',
    enName: 'Parsa',
    avatar: '🛌',
    badge: '💤 ۲ پتو',
    desc: 'خوابیدن و نجات از خستگی تا ۲ بار',
    color: '#9b59b6'
  },
  {
    id: 'ahmad',
    name: 'احمد',
    enName: 'Ahmad',
    avatar: '🛡️',
    badge: '🛡️ سپر ۱۰۰',
    desc: 'هر ۱۰۰ ضربه = ۱ سپر محافظ پشته‌ای',
    color: '#2ecc71'
  },
  {
    id: 'erfan',
    name: 'عرفان',
    enName: 'Erfan',
    avatar: '⚡',
    badge: '⚡ ۳X امتیاز',
    desc: 'خستگی زیر ۵۰٪ = امتیاز ۳ برابر بحرانی!',
    color: '#f39c12'
  }
];

function updateCarouselCard(charId) {
  var charData = ALL_CHARACTERS.find(function(c) { return c.id === charId; }) || ALL_CHARACTERS[0];
  var card = document.getElementById('char_carousel_card');
  var avatarEl = document.getElementById('char_card_avatar');
  var nameEl = document.getElementById('char_card_name');
  var badgeEl = document.getElementById('char_card_badge');
  var descEl = document.getElementById('char_card_desc');

  if (avatarEl) avatarEl.innerText = charData.avatar;
  if (nameEl) nameEl.innerText = charData.enName + ' (' + charData.name + ')';
  if (badgeEl) {
    badgeEl.innerText = charData.badge;
    badgeEl.style.color = charData.color;
    badgeEl.style.borderColor = charData.color + '55';
    badgeEl.style.background = charData.color + '22';
  }
  if (descEl) descEl.innerText = charData.desc;

  if (card) {
    card.style.borderColor = charData.color;
    card.style.boxShadow = '0 6px 18px rgba(0, 0, 0, 0.4), 0 0 16px ' + charData.color + '45';
  }

  // Update dots
  var dots = document.querySelectorAll('.char-carousel-dot');
  dots.forEach(function(dot) {
    if (dot.getAttribute('data-char') === charId) {
      dot.className = 'char-carousel-dot active';
      dot.style.background = charData.color;
      dot.style.boxShadow = '0 0 8px ' + charData.color;
    } else {
      dot.className = 'char-carousel-dot';
      dot.style.background = 'rgba(255, 255, 255, 0.25)';
      dot.style.boxShadow = 'none';
    }
  });
}
"""

if 'var ALL_CHARACTERS = [' not in code:
    code = code.replace('function selectCharacter(charId) {', characters_def + '\nfunction selectCharacter(charId) {')
    print("Added ALL_CHARACTERS and updateCarouselCard.")

# 3. In selectCharacter(charId):
# Replace the old button tab toggles with updateCarouselCard(charId)
old_tab_toggles = """  var btnNima = document.getElementById('btn_select_nima');
  var btnFargol = document.getElementById('btn_select_fargol');
  var btnAli = document.getElementById('btn_select_ali');
  var btnAmirhossein = document.getElementById('btn_select_amirhossein');
  var btnParsa = document.getElementById('btn_select_parsa');
  var btnAhmad = document.getElementById('btn_select_ahmad');
  var btnErfan = document.getElementById('btn_select_erfan');
  if (btnNima) btnNima.classList.remove('active');
  if (btnFargol) btnFargol.classList.remove('active');
  if (btnAli) btnAli.classList.remove('active');
  if (btnAmirhossein) btnAmirhossein.classList.remove('active');
  if (btnParsa) btnParsa.classList.remove('active');
  if (btnAhmad) btnAhmad.classList.remove('active');
  if (btnErfan) btnErfan.classList.remove('active');

  if (charId === 'fargol') {
    if (btnFargol) btnFargol.classList.add('active');
  } else if (charId === 'ali') {
    if (btnAli) btnAli.classList.add('active');
  } else if (charId === 'amirhossein') {
    if (btnAmirhossein) btnAmirhossein.classList.add('active');
  } else if (charId === 'parsa') {
    if (btnParsa) btnParsa.classList.add('active');
  } else if (charId === 'ahmad') {
    if (btnAhmad) btnAhmad.classList.add('active');
  } else if (charId === 'erfan') {
    if (btnErfan) btnErfan.classList.add('active');
  } else {
    if (btnNima) btnNima.classList.add('active');
  }"""

if old_tab_toggles in code:
    code = code.replace(old_tab_toggles, '  updateCarouselCard(charId);')
    print("Replaced old tab toggles in selectCharacter.")

# 4. Rewrite initCharacterSelector()
old_init_selector_pattern = re.compile(r'function initCharacterSelector\(\) \{.*?\n\}', re.DOTALL)
new_init_selector = """function rotateCharacter(direction) {
  var curIdx = ALL_CHARACTERS.findIndex(function(c) { return c.id === selectedCharacter; });
  if (curIdx < 0) curIdx = 0;
  var nextIdx = (curIdx + direction + ALL_CHARACTERS.length) % ALL_CHARACTERS.length;
  selectCharacter(ALL_CHARACTERS[nextIdx].id);
}

function initCharacterSelector() {
  var prevBtn = document.getElementById('btn_char_prev');
  var nextBtn = document.getElementById('btn_char_next');
  var card = document.getElementById('char_carousel_card');
  var dotsContainer = document.getElementById('char_carousel_dots');

  // Build dots
  if (dotsContainer && !dotsContainer.hasChildNodes()) {
    dotsContainer.innerHTML = '';
    ALL_CHARACTERS.forEach(function(c, idx) {
      var dot = document.createElement('div');
      dot.className = 'char-carousel-dot' + (c.id === selectedCharacter ? ' active' : '');
      dot.setAttribute('data-char', c.id);
      dot.setAttribute('data-index', idx);
      dot.setAttribute('title', c.enName + ' (' + c.name + ')');
      dot.addEventListener('click', function(e) {
        e.stopPropagation();
        selectCharacter(c.id);
      });
      dotsContainer.appendChild(dot);
    });
  }

  if (prevBtn) {
    prevBtn.onclick = function(e) {
      e.stopPropagation();
      e.preventDefault();
      rotateCharacter(-1);
    };
  }

  if (nextBtn) {
    nextBtn.onclick = function(e) {
      e.stopPropagation();
      e.preventDefault();
      rotateCharacter(1);
    };
  }

  if (card) {
    card.onclick = function(e) {
      e.stopPropagation();
      e.preventDefault();
      rotateCharacter(1);
    };

    // Touch swipe support
    var touchStartX = 0;
    card.addEventListener('touchstart', function(e) {
      touchStartX = e.touches[0].clientX;
    }, { passive: true });
    card.addEventListener('touchend', function(e) {
      var touchEndX = e.changedTouches[0].clientX;
      var diff = touchEndX - touchStartX;
      if (Math.abs(diff) > 35) {
        rotateCharacter(diff < 0 ? 1 : -1);
      }
    }, { passive: true });
  }

  updateCarouselCard(selectedCharacter);
}"""

# Replace initCharacterSelector
code = old_init_selector_pattern.sub(new_init_selector, code, count=1)
print("Replaced initCharacterSelector.")

# 5. Add Left/Right arrow key rotation when on start/result screen
# In keydown listener:
old_keydown = 'aa?(37==a&&(Ka(La),Ca(!0)),39==a&&(Ka(jb),Ca(!1))):Z&&!h||32!=a||(Ka(La),fb())'
new_keydown = 'aa?(37==a&&(Ka(La),Ca(!0)),39==a&&(Ka(jb),Ca(!1))):(37==a?rotateCharacter(-1):(39==a?rotateCharacter(1):(Z&&!h||32!=a||(Ka(La),fb()))))'

if old_keydown in code:
    code = code.replace(old_keydown, new_keydown)
    print("Added Left/Right arrow keys for character rotation.")

with open('public/js/main.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("public/js/main.js updated with Carousel Character Selector successfully!")
