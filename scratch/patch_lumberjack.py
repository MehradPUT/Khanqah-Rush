import re
import base64

with open('scratch/orig_main.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix unencoded '#' in SVG data URLs
def encode_svg(match):
    prefix = match.group(1)
    svg_body = match.group(2)
    return prefix + svg_body.replace('#', '%23')

code = re.sub(r'(data:image/svg\+xml,)(<.*?</svg>)', encode_svg, code)
code = code.replace('<!!!!svg', '<svg')

# 1. Base64 data URLs for Nima Old Body and Nima Old Died
with open('public/images/nima_body_old.png', 'rb') as f:
    b64_body = base64.b64encode(f.read()).decode('ascii')
data_body = f"data:image/png;base64,{b64_body}"

with open('public/images/nima_died_old.png', 'rb') as f:
    b64_died = base64.b64encode(f.read()).decode('ascii')
data_died = f"data:image/png;base64,{b64_died}"

# Replace lumber_body and lumber_died data URLs completely for fallbacks
code = re.sub(r"lumber_body:'[^']*'", f"lumber_body:'{data_body}'", code)
code = re.sub(r"lumber_died:'[^']*'", f"lumber_died:'{data_died}'", code)

# 2. Replace hand_up with skinny arm & hand SVG
skinny_hand_up = (
    '<svg width="94px" height="104px" viewBox="0 0 94 104" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
    '<g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">'
    '<rect fill="%23825F31" x="52" y="9" width="12" height="94" rx="6"></rect>'
    '<rect fill="%23CE453A" x="52" y="0" width="30" height="30"></rect>'
    '<rect fill="%23FFFFFF" x="82" y="0" width="12" height="30"></rect>'
    '<rect fill="%23DFAC9B" x="3" y="79" width="60" height="10" rx="5"></rect>'
    '<rect fill="%23161618" x="1" y="76" width="10" height="16" rx="3"></rect>'
    '<rect fill="%23DFAC9B" x="49" y="41" width="16" height="15" rx="5"></rect>'
    '<rect fill="%23C49080" x="49" y="46" width="16" height="1"></rect>'
    '<rect fill="%23C49080" x="49" y="51" width="16" height="1"></rect>'
    '<rect fill="%23DFAC9B" x="49" y="76" width="16" height="15" rx="5"></rect>'
    '<rect fill="%23C49080" x="49" y="81" width="16" height="1"></rect>'
    '<rect fill="%23C49080" x="49" y="86" width="16" height="1"></rect>'
    '</g></svg>'
)
code = re.sub(r"hand_up:'[^']*'", f"hand_up:'data:image/svg+xml,{skinny_hand_up}'", code)

# 3. Replace hand_down with skinny arm & hand SVG
skinny_hand_down = (
    '<svg width="118px" height="18px" viewBox="0 0 118 18" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
    '<g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">'
    '<rect fill="%23825F31" x="24" y="3" width="94" height="12" rx="6"></rect>'
    '<rect fill="%23161618" x="1" y="4" width="15" height="10" rx="3"></rect>'
    '<rect fill="%23DFAC9B" x="14" y="5" width="36" height="8" rx="4"></rect>'
    '<rect fill="%23DFAC9B" x="49" y="2" width="16" height="14" rx="5"></rect>'
    '<rect fill="%23C49080" x="54" y="2" width="1" height="14"></rect>'
    '<rect fill="%23C49080" x="59" y="2" width="1" height="14"></rect>'
    '<rect fill="%23DFAC9B" x="86" y="2" width="16" height="14" rx="5"></rect>'
    '<rect fill="%23C49080" x="91" y="2" width="1" height="14"></rect>'
    '<rect fill="%23C49080" x="96" y="2" width="1" height="14"></rect>'
    '</g></svg>'
)
code = re.sub(r"hand_down:'[^']*'", f"hand_down:'data:image/svg+xml,{skinny_hand_down}'", code)

# 4. Multi-Character Engine (Nima, Fargol, Ali & Amirhossein) - Visual HUD, Abilities, and NO custom sound effects
multi_char_engine_code = r'''
// --- MULTI-CHARACTER (NIMA, FARGOL, ALI, AMIRHOSSEIN & PARSA) GAME ENGINE ---
// NOTE: All custom sound effects and speech synthesis for characters are permanently removed.
var selectedCharacter = localStorage.getItem('khanqah_character') || 'nima';
var nimaPhase = 'old';
var gameStartTime = 0;
var isRejuvenated = false;

// Fargol state
var fargolChops = 0;
var fargolFlameActive = false;
var fargolFlameStartTime = 0;
var fargolSacrificeAvailable = true;

// Ali state (10-Log Flurry after 50 chops)
var aliChops = 0;
var aliFlurryActive = false;
var isFlurryChop = false;
var aliFlurryRemaining = 0;
var aliFlurryTimer = null;

// Parsa state (Cozy Blanket Nap on tiredness exhaustion - 2 times max)
var parsaSleepCount = 0;
var parsaSleeping = false;
var parsaWaitingForChop = false;
var parsaSleepStartTime = 0;
var parsaSleepTimer = null;

// Ahmad state (Stacking Steel Shield every 100 chops)
var ahmadChops = 0;
var ahmadShieldCount = 0;
var ahmadShieldActive = false;

// Texture pointers
var tex_nima_old = null;
var tex_nima_young = null;
var tex_nima_swing_old = null;
var tex_nima_swing_young = null;
var tex_nima_died_old = null;
var tex_nima_died_young = null;
var tex_fargol_normal = null;
var tex_fargol_swing = null;
var tex_fargol_flame_swing = null;
var tex_fargol_flame = null;
var tex_fargol_died = null;
var tex_ali_body = null;
var tex_ali_swing = null;
var tex_ali_died = null;
var tex_amirhossein_body = null;
var tex_amirhossein_swing = null;
var tex_amirhossein_died = null;
var tex_parsa_body = null;
var tex_parsa_swing = null;
var tex_parsa_sleep = null;
var tex_parsa_died = null;
var tex_ahmad_body = null;
var tex_ahmad_swing = null;
var tex_ahmad_died = null;
var tex_erfan_body = null;
var tex_erfan_swing = null;
var tex_erfan_died = null;
var tex_fateme_body = null;
var tex_fateme_swing = null;
var tex_fateme_died = null;
var tex_parsa_jump = null;
var fargolSacrificeInProgress = false;

// Inject Arcade Styles (Visual Combat Popups, Character Selector, HUD)
(function initArcadeStyles() {
  if (document.getElementById('khanqah_arcade_styles')) return;
  var style = document.createElement('style');
  style.id = 'khanqah_arcade_styles';
  style.innerHTML = `
    @keyframes arcadeFloat {
      0% {
        opacity: 0;
        transform: translate(-50%, -50%) scale(0.3) rotate(var(--rot, -4deg));
      }
      15% {
        opacity: 1;
        transform: translate(-50%, -50%) scale(1.25) rotate(var(--rot, -4deg));
      }
      30% {
        transform: translate(-50%, -50%) scale(1.0) rotate(var(--rot, -4deg));
      }
      75% {
        opacity: 1;
        transform: translate(-50%, calc(-50% - 35px)) scale(1.05) rotate(var(--rot, -4deg));
      }
      100% {
        opacity: 0;
        transform: translate(-50%, calc(-50% - 65px)) scale(0.9) rotate(var(--rot, -4deg));
      }
    }

    .arcade-combat-text {
      position: fixed;
      pointer-events: none;
      z-index: 9999;
      font-family: 'Vazirmatn', Impact, 'Arial Black', -apple-system, sans-serif;
      font-size: 32px;
      font-weight: 900;
      text-align: center;
      white-space: nowrap;
      direction: rtl;
      animation: arcadeFloat 0.95s cubic-bezier(0.15, 0.9, 0.25, 1.2) forwards;
      letter-spacing: 0.8px;
      color: #FFD54F;
      text-shadow: 
        -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 2px 2px 0 #000,
        -3px 0 0 #000, 3px 0 0 #000, 0 -3px 0 #000, 0 3px 0 #000,
        0 4px 10px rgba(0,0,0,0.8);
    }

    .arcade-combat-text.erfan-crit { color: #f39c12; text-shadow: 0 0 10px #f1c40f, 0 0 20px #e74c3c, 2px 2px 0px #000; font-size: 32px; font-weight: 900; }
    .arcade-combat-text.crit {
      color: #FFF176;
      font-size: 36px;
      text-shadow: 
        -2px -2px 0 #E65100, 2px -2px 0 #E65100, -2px 2px 0 #E65100, 2px 2px 0 #E65100,
        -3px 0 0 #E65100, 3px 0 0 #E65100, 0 -3px 0 #E65100, 0 3px 0 #E65100,
        0 4px 12px rgba(0,0,0,0.9), 0 0 25px rgba(255, 152, 0, 0.9);
    }

    .arcade-combat-text.young {
      color: #00E5FF;
      font-size: 38px;
      text-shadow: 
        -2px -2px 0 #006064, 2px -2px 0 #006064, -2px 2px 0 #006064, 2px 2px 0 #006064,
        -3px 0 0 #006064, 3px 0 0 #006064, 0 -3px 0 #006064, 0 3px 0 #006064,
        0 5px 15px rgba(0,0,0,0.9), 0 0 30px rgba(0, 229, 255, 1);
    }

    .arcade-combat-text.flame {
      color: #FF1744;
      font-size: 38px;
      text-shadow: 
        -2px -2px 0 #D50000, 2px -2px 0 #D50000, -2px 2px 0 #D50000, 2px 2px 0 #D50000,
        -3px 0 0 #D50000, 3px 0 0 #D50000, 0 -3px 0 #D50000, 0 3px 0 #D50000,
        0 5px 15px rgba(0,0,0,0.9), 0 0 30px rgba(255, 23, 68, 1);
    }

    .arcade-combat-text.death {
      font-size: 32px;
      color: #FF5252;
      text-shadow: 
        -2px -2px 0 #212121, 2px -2px 0 #212121, -2px 2px 0 #212121, 2px 2px 0 #212121,
        0 4px 12px rgba(0,0,0,0.9);
    }

    .arcade-combat-text.small-popup { font-size: 20px !important; }

    /* CAROUSEL CHARACTER SELECTOR WITH ROTATING ARROWS */
    .char-carousel-wrap {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      margin: 10px auto 6px auto;
      max-width: 360px;
      width: 95%;
      position: relative;
      z-index: 9999;
      pointer-events: auto;
      touch-action: manipulation;
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
      -webkit-user-select: none;
      pointer-events: auto;
      touch-action: manipulation;
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
      -webkit-user-select: none;
      -webkit-tap-highlight-color: transparent;
      pointer-events: auto;
      touch-action: manipulation;
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
      justify-content: center;
      width: 100%;
      gap: 8px;
    }

    .char-card-avatar {
      display: none !important;
      font-size: 24px;
      line-height: 1;
      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
    }

    .char-card-titles {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      gap: 6px;
      flex-wrap: wrap;
    }

    .char-card-name {
      font-family: 'Arial Black', Impact, sans-serif;
      font-size: 17px;
      text-align: center;
      font-weight: 900;
      letter-spacing: 0.5px;
      color: #ffffff;
      display: block;
      width: 100%;
      margin: 0 auto;
      direction: ltr;
    }

    .char-card-badge { display: none !important;
      font-family: 'Vazirmatn', sans-serif;
      font-size: 11px;
      font-weight: 800;
      color: #e4b072;
      background: rgba(228, 176, 114, 0.18);
      padding: 2px 7px;
      border-radius: 8px;
      border: 1px solid rgba(228, 176, 114, 0.35);
    }

    .char-card-desc { display: none !important;
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
      z-index: 9999;
      position: relative;
      pointer-events: auto;
      touch-action: manipulation;
    }

    .char-carousel-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.25);
      cursor: pointer;
      transition: all 0.25s ease;
      pointer-events: auto;
      touch-action: manipulation;
      padding: 6px;
      margin: -6px 0;
      background-clip: content-box;
    }

    .char-carousel-dot.active {
      width: 18px;
      border-radius: 6px;
      background: #e4b072;
      box-shadow: 0 0 8px #e4b072;
    }

    /* TOP-LEFT DYNAMIC ABILITY BAR */
    #page_wrap {
      position: relative !important;
    }

    .char-ability-bar-wrap {
      position: absolute;
      top: 14px;
      left: 14px;
      width: 122px;
      padding: 5px 9px 6px 9px;
      border-radius: 12px;
      box-sizing: border-box;
      z-index: 1000;
      pointer-events: none;
      display: none;
      transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .char-ability-bar-wrap.nima.old {
      background: rgba(14, 20, 32, 0.84);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(255, 179, 0, 0.55);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), inset 0 1px 1px rgba(255, 255, 255, 0.15);
    }

    .char-ability-bar-wrap.fargol.normal {
      background: rgba(14, 28, 24, 0.86);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(142, 197, 173, 0.65);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), 0 0 10px rgba(142, 197, 173, 0.25);
    }

    .char-ability-bar-wrap.ali.normal {
      background: rgba(18, 24, 38, 0.88);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(255, 152, 0, 0.65);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), 0 0 12px rgba(255, 152, 0, 0.25);
    }

    .char-ability-bar-wrap.amirhossein.normal {
      background: rgba(13, 27, 42, 0.88);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(41, 128, 185, 0.65);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), 0 0 12px rgba(41, 128, 185, 0.3);
    }

    .char-ability-bar-wrap.parsa.normal {
      background: rgba(26, 18, 38, 0.88);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(155, 89, 182, 0.65);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), 0 0 12px rgba(155, 89, 182, 0.3);
    }

    .char-ability-bar-wrap.parsa.sleep {
      background: rgba(45, 20, 60, 0.92);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(241, 196, 15, 0.8);
      box-shadow: 0 0 18px rgba(155, 89, 182, 0.8), 0 0 8px rgba(241, 196, 15, 0.5);
    }

    .char-ability-bar-wrap.parsa.waiting {
      background: rgba(18, 38, 26, 0.9);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(46, 204, 113, 0.8);
      box-shadow: 0 0 14px rgba(46, 204, 113, 0.4);
    }

    .char-ability-bar-wrap.parsa.waiting .char-hud-title {
      color: #2ecc71;
      text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }

    .char-ability-bar-wrap.parsa.waiting .char-hud-timer {
      color: #2ecc71;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.parsa.waiting .char-hud-fill {
      background: #2ecc71;
      box-shadow: 0 0 8px rgba(46, 204, 113, 0.8);
    }

    .char-ability-bar-wrap.ahmad.normal {
      background: rgba(18, 28, 38, 0.88);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(52, 152, 219, 0.65);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), 0 0 12px rgba(52, 152, 219, 0.3);
    }

    .char-ability-bar-wrap.ahmad.shield {
      background: rgba(20, 35, 55, 0.94);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid #f1c40f;
      box-shadow: 0 0 18px rgba(52, 152, 219, 0.85), 0 0 10px rgba(241, 196, 15, 0.6);
    }

    .char-ability-bar-wrap.ahmad.shield .char-hud-title {
      color: #f1c40f;
      text-shadow: 0 0 6px rgba(241, 196, 15, 0.8);
    }

    .char-ability-bar-wrap.ahmad.shield .char-hud-timer {
      color: #f1c40f;
      text-shadow: 0 0 6px rgba(241, 196, 15, 0.8);
    }

    .char-ability-bar-wrap.ahmad.shield .char-hud-fill {
      background: linear-gradient(90deg, #3498db 0%, #2ecc71 50%, #f1c40f 100%);
      box-shadow: 0 0 10px rgba(241, 196, 15, 0.9);
    }

    .char-hud-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 2px;
      line-height: 1;
    }

    .char-hud-name {
      font-family: 'Arial Black', Impact, -apple-system, sans-serif;
      font-size: 11.5px;
      font-weight: 900;
      letter-spacing: 0.8px;
      text-transform: lowercase;
      color: #FFFFFF;
      text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9);
      transition: color 0.3s;
    }

    .char-hud-shield {
      font-family: 'Vazirmatn', sans-serif;
      font-size: 9px;
      font-weight: 800;
      padding: 1px 4px;
      border-radius: 4px;
      line-height: 1.2;
    }

    .char-hud-shield.active {
      color: #8ec5ad;
      background: rgba(142, 197, 173, 0.2);
      border: 1px solid rgba(142, 197, 173, 0.5);
      box-shadow: 0 0 6px rgba(142, 197, 173, 0.4);
    }

    .char-hud-shield.used {
      color: #888888;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      text-decoration: line-through;
    }

    .char-hud-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
      line-height: 1.1;
    }

    .char-hud-title {
      font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, Tahoma, sans-serif;
      font-size: 12.5px;
      font-weight: 800;
      letter-spacing: 0.2px;
      transition: color 0.3s;
    }

    .char-ability-bar-wrap.nima.old .char-hud-title {
      color: #FFE082;
      text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }

    .char-ability-bar-wrap.fargol.normal .char-hud-title {
      color: #8ec5ad;
      text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }

    .char-ability-bar-wrap.ali.normal .char-hud-title {
      color: #ffb74d;
      text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }

    .char-ability-bar-wrap.amirhossein.normal .char-hud-title {
      color: #70a1ff;
      text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }

    .char-ability-bar-wrap.parsa.normal .char-hud-title,
    .char-ability-bar-wrap.parsa.sleep .char-hud-title {
      color: #d7bde2;
      text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }

    .char-hud-timer {
      font-family: 'Arial Black', Impact, -apple-system, sans-serif;
      font-size: 11px;
      font-weight: 900;
      letter-spacing: 0.5px;
    }

    .char-ability-bar-wrap.nima.old .char-hud-timer {
      color: #FFB300;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.fargol.normal .char-hud-timer {
      color: #FFD54F;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.ali.normal .char-hud-timer {
      color: #ff9800;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.amirhossein.normal .char-hud-timer {
      color: #70a1ff;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.parsa.normal .char-hud-timer,
    .char-ability-bar-wrap.parsa.sleep .char-hud-timer {
      color: #f5b041;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.parsa .char-hud-fill {
      background: linear-gradient(90deg, #8e44ad 0%, #9b59b6 50%, #f1c40f 100%);
      box-shadow: 0 0 8px rgba(155, 89, 182, 0.7);
    }

    .char-ability-bar-wrap.ahmad.normal .char-hud-timer {
      color: #5dade2;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.ahmad .char-hud-fill {
      background: linear-gradient(90deg, #2980b9 0%, #3498db 70%, #5dade2 100%);
      box-shadow: 0 0 8px rgba(52, 152, 219, 0.7);
    }

    .char-ability-bar-wrap.erfan.normal {
      background: rgba(18, 28, 42, 0.88);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(43, 92, 143, 0.65);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), 0 0 12px rgba(43, 92, 143, 0.3);
    }

    .char-ability-bar-wrap.erfan.active {
      background: rgba(45, 25, 10, 0.94);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid #f39c12;
      box-shadow: 0 0 18px rgba(243, 156, 18, 0.85), 0 0 10px rgba(231, 76, 60, 0.6);
      animation: fargolFlamePulse 0.6s infinite ease-in-out;
    }

    .char-ability-bar-wrap.erfan.active .char-hud-title {
      color: #f39c12;
      text-shadow: 0 0 6px rgba(243, 156, 18, 0.9);
    }

    .char-ability-bar-wrap.erfan.active .char-hud-timer {
      color: #f1c40f;
      text-shadow: 0 0 6px rgba(241, 196, 15, 0.9);
    }

    .char-ability-bar-wrap.erfan.active .char-hud-fill {
      background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #f1c40f 100%);
      box-shadow: 0 0 10px rgba(243, 156, 18, 0.9);
    }

    .char-ability-bar-wrap.erfan.normal .char-hud-timer {
      color: #5dade2;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.erfan .char-hud-fill {
      background: linear-gradient(90deg, #2b5c8f 0%, #3498db 70%, #5dade2 100%);
      box-shadow: 0 0 8px rgba(43, 92, 143, 0.7);
    }

    .char-ability-bar-wrap.fateme.normal {
      background: rgba(16, 36, 36, 0.88);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      border: 1.5px solid rgba(38, 166, 154, 0.65);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), 0 0 12px rgba(38, 166, 154, 0.3);
    }

    .char-ability-bar-wrap.fateme.normal .char-hud-title {
      color: #80cbc4;
      text-shadow: 0 1px 3px rgba(0,0,0,0.9);
    }

    .char-ability-bar-wrap.fateme.normal .char-hud-timer {
      color: #80cbc4;
      text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    .char-ability-bar-wrap.fateme .char-hud-fill {
      background: linear-gradient(90deg, #00897b 0%, #26a69a 50%, #80cbc4 100%);
      box-shadow: 0 0 8px rgba(38, 166, 154, 0.7);
    }

    .char-hud-track {
      position: relative;
      width: 100%;
      height: 7px;
      background: rgba(0, 0, 0, 0.65);
      border-radius: 5px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: inset 0 1px 2px rgba(0,0,0,0.7);
    }

    .char-hud-fill {
      height: 100%;
      border-radius: 5px;
      transition: width 0.08s linear;
      width: 0%;
    }

    .char-ability-bar-wrap.nima.old .char-hud-fill {
      background: linear-gradient(90deg, #FF6F00 0%, #FFB300 50%, #FFE082 100%);
      box-shadow: 0 0 8px rgba(255, 179, 0, 0.8);
    }

    .char-ability-bar-wrap.fargol.normal .char-hud-fill {
      background: linear-gradient(90deg, #529471 0%, #8ec5ad 50%, #FFE082 100%);
      box-shadow: 0 0 8px rgba(142, 197, 173, 0.8);
    }

    .char-ability-bar-wrap.ali.normal .char-hud-fill {
      background: linear-gradient(90deg, #f57c00 0%, #ff9800 50%, #ffd54f 100%);
      box-shadow: 0 0 8px rgba(255, 152, 0, 0.8);
    }

    .char-ability-bar-wrap.amirhossein.normal .char-hud-fill {
      background: linear-gradient(90deg, #1e3799 0%, #2980b9 50%, #70a1ff 100%);
      box-shadow: 0 0 8px rgba(41, 128, 185, 0.8);
    }

    /* ALI FLURRY COMBO PHASE */
    @keyframes aliFlurryPulse {
      0%, 100% {
        transform: scale(1);
        box-shadow: 0 0 16px rgba(255, 152, 0, 0.9), inset 0 0 8px rgba(255, 193, 7, 0.4);
        border-color: #ff9800;
      }
      50% {
        transform: scale(1.04);
        box-shadow: 0 0 28px rgba(255, 193, 7, 1), inset 0 0 14px rgba(255, 87, 34, 0.7);
        border-color: #ffc107;
      }
    }

    .char-ability-bar-wrap.ali.flurry {
      background: rgba(35, 18, 8, 0.94);
      border: 1.5px solid #ff9800;
      animation: aliFlurryPulse 0.55s infinite ease-in-out;
    }

    .char-ability-bar-wrap.ali.flurry .char-hud-name {
      color: #ffc107;
      text-shadow: 0 0 8px rgba(255, 193, 7, 0.9);
    }

    .char-ability-bar-wrap.ali.flurry .char-hud-title {
      color: #ff9800;
      text-shadow: 0 0 8px rgba(255, 152, 0, 0.9);
    }

    .char-ability-bar-wrap.ali.flurry .char-hud-timer {
      color: #ffffff;
      text-shadow: 0 0 10px rgba(255, 193, 7, 1);
    }

    .char-ability-bar-wrap.ali.flurry .char-hud-fill {
      background: linear-gradient(90deg, #ff9800 0%, #ffc107 50%, #ffffff 100%);
      box-shadow: 0 0 14px rgba(255, 152, 0, 1);
    }

    /* NIMA YOUNG PHASE (ACTIVE JAVANI FRENZY) */
    @keyframes javaniPulse {
      0%, 100% {
        transform: scale(1);
        box-shadow: 0 0 14px rgba(0, 229, 255, 0.85), inset 0 0 8px rgba(0, 229, 255, 0.35);
        border-color: #00E5FF;
      }
      50% {
        transform: scale(1.04);
        box-shadow: 0 0 24px rgba(0, 229, 255, 1), inset 0 0 14px rgba(0, 229, 255, 0.6);
        border-color: #E0F7FA;
      }
    }

    .char-ability-bar-wrap.nima.young {
      background: rgba(0, 30, 45, 0.92);
      border: 1.5px solid #00E5FF;
      animation: javaniPulse 0.7s infinite ease-in-out;
    }

    .char-ability-bar-wrap.nima.young .char-hud-name {
      color: #00E5FF;
      text-shadow: 0 0 8px rgba(0, 229, 255, 0.9);
    }

    .char-ability-bar-wrap.nima.young .char-hud-title {
      color: #80DEEA;
      text-shadow: 0 0 8px rgba(0, 229, 255, 0.9);
    }

    .char-ability-bar-wrap.nima.young .char-hud-timer {
      color: #FFFFFF;
      text-shadow: 0 0 10px rgba(0, 229, 255, 1);
    }

    .char-ability-bar-wrap.nima.young .char-hud-fill {
      background: linear-gradient(90deg, #00B0FF 0%, #00E5FF 50%, #FFFFFF 100%);
      box-shadow: 0 0 14px rgba(0, 229, 255, 1);
    }

    /* FARGOL FLAME PHASE (ACTIVE INVINCIBLE FLAME) */
    @keyframes fargolFlamePulse {
      0%, 100% {
        transform: scale(1);
        box-shadow: 0 0 16px rgba(255, 23, 68, 0.9), inset 0 0 8px rgba(255, 61, 0, 0.4);
        border-color: #FF1744;
      }
      50% {
        transform: scale(1.04);
        box-shadow: 0 0 26px rgba(255, 61, 0, 1), inset 0 0 14px rgba(255, 23, 68, 0.7);
        border-color: #FFD600;
      }
    }

    .char-ability-bar-wrap.fargol.flame {
      background: rgba(45, 10, 5, 0.94);
      border: 1.5px solid #FF1744;
      animation: fargolFlamePulse 0.7s infinite ease-in-out;
    }

    .char-ability-bar-wrap.fargol.flame .char-hud-name {
      color: #FFD600;
      text-shadow: 0 0 8px rgba(255, 61, 0, 0.9);
    }

    .char-ability-bar-wrap.fargol.flame .char-hud-title {
      color: #FF6E40;
      text-shadow: 0 0 8px rgba(255, 23, 68, 0.9);
    }

    .char-ability-bar-wrap.fargol.flame .char-hud-timer {
      color: #FFFFFF;
      text-shadow: 0 0 10px rgba(255, 61, 0, 1);
    }

    .char-ability-bar-wrap.fargol.flame .char-hud-fill {
      background: linear-gradient(90deg, #D50000 0%, #FF3D00 50%, #FFD600 100%);
      box-shadow: 0 0 14px rgba(255, 61, 0, 1);
    }
  `;
  document.head.appendChild(style);
})();

function spawnCombatPopup(text, type) {
  var el = document.createElement('div');
  el.className = 'arcade-combat-text ' + (type || 'normal');
  el.innerText = text;
  var rot = (Math.random() * 12 - 6).toFixed(1) + 'deg';
  el.style.setProperty('--rot', rot);
  if (type === 'erfan-crit') {
    var x = window.innerWidth - 60 + (Math.random() * 20 - 10);
    var y = 60 + (Math.random() * 30 - 15);
    el.style.left = x + 'px';
    el.style.top = y + 'px';
  } else {
    var x = window.innerWidth / 2 + (Math.random() * 40 - 20);
    var y = window.innerHeight * 0.42 + (Math.random() * 30 - 15);
    el.style.left = x + 'px';
    el.style.top = y + 'px';
  }
  document.body.appendChild(el);
  setTimeout(function() {
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }, 950);
}

function getAliSafeSide() {
  if (typeof da === 'undefined' || !da || da.length === 0) return (typeof m !== 'undefined' ? m : true);
  // da[i] < 0: branch on LEFT -> safe side is RIGHT (false)
  // da[i] > 0: branch on RIGHT -> safe side is LEFT (true)
  if (da[0] !== 0) {
    return da[0] > 0;
  }
  if (da.length > 1 && da[1] !== 0) {
    return da[1] > 0;
  }
  if (da.length > 2 && da[2] !== 0) {
    return da[2] > 0;
  }
  return (typeof m !== 'undefined' ? m : true);
}

function triggerAliFlurry() {
  if (aliFlurryTimer) {
    clearInterval(aliFlurryTimer);
    aliFlurryTimer = null;
  }
  aliFlurryActive = true;
  aliFlurryRemaining = 10;
  ba = +new Date + qa; // Top up stamina to maximum!

  spawnCombatPopup('🪓⚡ رگبار ۱۰ کنده! +10 💥', 'crit');
  triggerTelegramHaptic('heavy');

  updateCharacterHUD('ali', 'flurry', 100, '10 کنده', false);

  // Before starting flurry, immediately move to the side without a branch!
  var initialSafe = getAliSafeSide();
  if (typeof wa === 'function') {
    wa(initialSafe, false);
  }

  aliFlurryTimer = setInterval(function() {
    if (typeof aa === 'undefined' || !aa) {
      clearInterval(aliFlurryTimer);
      aliFlurryTimer = null;
      aliFlurryActive = false;
      return;
    }

    if (aliFlurryRemaining > 0) {
      // 1. Determine the side that does not have a branch
      var safeSide = getAliSafeSide();

      // 2. Perform chop on safe side!
      isFlurryChop = true;
      try {
        if (typeof Ca === 'function') {
          Ca(safeSide);
        }
      } finally {
        isFlurryChop = false;
      }

      // 3. AFTER each chop: tree has descended.
      // Move to the side that doesn't have a branch so he never lands on/under a branch!
      var postSafeSide = getAliSafeSide();
      if (typeof wa === 'function' && typeof m !== 'undefined' && m !== postSafeSide) {
        wa(postSafeSide, false);
      }

      // 4. Keep stamina full during flurry
      ba = +new Date + qa;

      // 5. Telegram haptic feedback
      triggerTelegramHaptic('medium');

      aliFlurryRemaining--;
      var pct = Math.min(100, Math.max(0, (aliFlurryRemaining / 10) * 100));
      updateCharacterHUD('ali', 'flurry', pct, aliFlurryRemaining + ' کنده', false);
    }

    if (aliFlurryRemaining <= 0) {
      clearInterval(aliFlurryTimer);
      aliFlurryTimer = null;
      aliFlurryActive = false;

      // Ensure Ali is safely on the side without a branch after all 10 chops complete!
      var finalSafe = getAliSafeSide();
      if (typeof wa === 'function' && typeof m !== 'undefined' && m !== finalSafe) {
        wa(finalSafe, false);
      }

      if (typeof sa !== 'undefined' && aa && tex_ali_body) {
        sa.texture = tex_ali_body;
        sa.width = 68;
        sa.height = 140;
      }
      updateCharacterHUD('ali', 'normal', 0, '0/50', false);
    }
  }, 95);
}

function triggerParsaNap() {
  if (typeof aa === 'undefined' || !aa) return;
  if (parsaSleeping) return;
  parsaSleeping = true;
  parsaWaitingForChop = false;
  parsaSleepCount++;
  parsaSleepStartTime = +new Date;
  za = false; // Stop game fatigue timer immediately!
  ba = +new Date + qa; // Full stamina restored!
  if (typeof Ua === 'function') Ua(); // Lock fatigue bar at 100% full

  spawnCombatPopup('🛌 خواب ۳ ثانیه‌ای! تجدید قوا (' + parsaSleepCount + '/2) 💤', 'crit small-popup');
  triggerTelegramHaptic('heavy');

  if (typeof sa !== 'undefined' && tex_parsa_sleep) {
    sa.texture = tex_parsa_sleep;
    sa.width = 94;
    sa.height = 140;
  }
  if (typeof ta !== 'undefined' && tex_parsa_sleep) {
    ta.texture = tex_parsa_sleep;
    ta.width = 94;
    ta.height = 140;
  }

  var remB = Math.max(0, 2 - parsaSleepCount);
  updateCharacterHUD('parsa', 'sleep', 100, '3.0s خواب', false);

  if (parsaSleepTimer) clearTimeout(parsaSleepTimer);
  parsaSleepTimer = setTimeout(function() {
    // WAKE UP AFTER 3 SECONDS!
    parsaSleeping = false;
    parsaWaitingForChop = true; // Stop fatigue bar until user starts chopping!
    za = false; // Keep fatigue bar stopped!
    ba = +new Date + qa;
    if (typeof Ua === 'function') Ua();

    if (typeof sa !== 'undefined' && aa && tex_parsa_body) {
      sa.texture = tex_parsa_body;
      sa.width = 94;
      sa.height = 140;
    }
    if (typeof ta !== 'undefined' && tex_parsa_body) {
      ta.texture = tex_parsa_body;
      ta.width = 94;
      ta.height = 140;
    }

    spawnCombatPopup('⏰ بیدار شد! آماده برای تبر زدن! 🪓', 'young small-popup');
    triggerTelegramHaptic('medium');
    updateCharacterHUD('parsa', 'waiting', 100, 'آماده تبر (' + remB + '/2)', false);
  }, 3000);
}

function updateCharacterHUD(charId, phase, percent, timeText, shieldActive) {
  var barWrap = document.getElementById('char_ability_bar_wrap');
  if (!barWrap) {
    barWrap = document.createElement('div');
    barWrap.id = 'char_ability_bar_wrap';
    barWrap.className = 'char-ability-bar-wrap';
    barWrap.innerHTML = `
      <div class="char-hud-header" style="justify-content: flex-end; margin-bottom: 4px;">
        <span class="char-hud-timer" id="char_hud_timer">15s</span>
      </div>
      <div class="char-hud-track">
        <div class="char-hud-fill" id="char_hud_fill"></div>
      </div>
    `;
    var pageWrap = document.getElementById('page_wrap') || document.body;
    pageWrap.appendChild(barWrap);
  }

  // Remove old nima element if present
  var oldBanner = document.getElementById('nima_javani_bar_wrap');
  if (oldBanner && oldBanner.parentNode) oldBanner.parentNode.removeChild(oldBanner);

  if (phase === 'hide' || charId === 'fateme') {
    barWrap.style.display = 'none';
    return;
  }
  barWrap.style.display = 'block';
  barWrap.className = 'char-ability-bar-wrap ' + charId + ' ' + phase;

  var nameEl = document.getElementById('char_hud_name');
  var shieldEl = document.getElementById('char_hud_shield');
  var titleEl = document.getElementById('char_hud_title');
  var timerEl = document.getElementById('char_hud_timer');
  var fillEl = document.getElementById('char_hud_fill');

  if (charId === 'fargol') {
    if (shieldEl) {
      shieldEl.style.display = 'inline-block';
      shieldEl.innerText = shieldActive ? '🛡️ جان دوم' : '💔 مصرف شد';
      shieldEl.className = 'char-hud-shield ' + (shieldActive ? 'active' : 'used');
    }
    if (nameEl) {
      nameEl.innerText = (phase === 'flame' ? '🔥 Sultan' : '👑 Sultan');
    }
    if (titleEl) {
      titleEl.innerText = (phase === 'flame' ? 'Flame Active' : 'Sultan Flame');
    }
  } else if (charId === 'ali') {
    if (shieldEl) {
      shieldEl.style.display = 'none';
    }
    if (nameEl) {
      nameEl.innerText = (phase === 'flurry' ? '⚡ Ali (Flurry)' : '👓 Ali');
    }
    if (titleEl) {
      titleEl.innerText = (phase === 'flurry' ? '🔥 Auto Flurry!' : 'Log Flurry');
    }
  } else if (charId === 'amirhossein') {
    if (shieldEl) {
      shieldEl.style.display = 'none';
    }
    if (nameEl) {
      nameEl.innerText = '🧢 Amirhossein';
    }
    if (titleEl) {
      titleEl.innerText = '2X Score Multiplier';
    }
  } else if (charId === 'parsa') {
    if (shieldEl) {
      shieldEl.style.display = 'inline-block';
      var remB = Math.max(0, 2 - parsaSleepCount);
      shieldEl.innerText = remB > 0 ? '🛌 ' + remB + ' Blankets' : '💤 No Blankets';
      shieldEl.className = 'char-hud-shield ' + (remB > 0 ? 'active' : 'used');
    }
    if (nameEl) {
      nameEl.innerText = (phase === 'sleep' ? '💤 Parsa (Sleep 3s)' : (phase === 'waiting' ? '🪓 Parsa (Ready)' : '🛌 Parsa'));
    }
    if (titleEl) {
      titleEl.innerText = (phase === 'sleep' ? '🛌 3s Nap Invincible!' : (phase === 'waiting' ? 'Timer Paused! Chop now' : 'Blanket Rest'));
    }
  } else if (charId === 'ahmad') {
    if (shieldEl) {
      shieldEl.style.display = 'inline-block';
      shieldEl.innerText = ahmadShieldCount > 0 ? ('🛡️ ' + ahmadShieldCount + ' Shields') : '🛡️ Shield 100';
      shieldEl.className = 'char-hud-shield ' + (ahmadShieldCount > 0 ? 'active' : 'used');
    }
    if (nameEl) {
      nameEl.innerText = ahmadShieldCount > 0 ? ('🛡️ Ahmad (Shield: ' + ahmadShieldCount + ')') : '🛡️ Ahmad';
    }
    if (titleEl) {
      titleEl.innerText = ahmadShieldCount > 0 ? ('Shield Active (' + ahmadShieldCount + ')') : 'Charge Shield (100 Chops)';
    }
  } else if (charId === 'erfan') {
    if (shieldEl) {
      shieldEl.style.display = 'inline-block';
      shieldEl.innerText = phase === 'active' ? '⚡ 3X Active' : '⚡ 3X Ready';
      shieldEl.className = 'char-hud-shield ' + (phase === 'active' ? 'active' : 'used');
    }
    if (nameEl) {
      nameEl.innerText = phase === 'active' ? '⚡ Erfan (3X Score)' : '⚡ Erfan';
    }
    if (titleEl) {
      titleEl.innerText = phase === 'active' ? '3X Critical Score! 🔥' : 'Fatigue <50% = 3X Score';
    }
  } else {
    if (shieldEl) {
      shieldEl.style.display = 'none';
    }
    if (nameEl) {
      nameEl.innerText = (phase === 'young' ? '⚡ Nima' : 'Nima');
    }
    if (titleEl) {
      titleEl.innerText = (phase === 'young' ? '⚡ Youth Active' : 'Youth Cycle');
    }
  }

  if (timerEl && typeof timeText !== 'undefined') timerEl.innerText = timeText;
  if (fillEl && typeof percent !== 'undefined') fillEl.style.width = Math.min(100, Math.max(0, percent)) + '%';
}

function triggerTelegramHaptic(style) {
  try {
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.HapticFeedback) {
      if (style === 'selection') {
        window.Telegram.WebApp.HapticFeedback.selectionChanged();
      } else {
        window.Telegram.WebApp.HapticFeedback.impactOccurred(style);
      }
    }
  } catch(e) {}
}

// Telegram Mini App Auto-Init (Expand & Ready)
try {
  if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
    if (typeof window.Telegram.WebApp.enableClosingConfirmation === 'function') {
      window.Telegram.WebApp.enableClosingConfirmation();
    }
  }
} catch(e) {}

var ALL_CHARACTERS = [
  {
    id: 'nima',
    name: 'Nima',
    enName: 'Nima',
    avatar: '🧔',
    badge: '⚡ Youth Cycle',
    desc: 'Rejuvenates every 15s (100% stamina & speed)',
    color: '#3498db'
  },
  {
    id: 'fargol',
    name: 'Sultan (سلطان)',
    enName: 'Sultan',
    avatar: '👑',
    badge: '🔥 Flame & Sacrifice',
    desc: '100 Chops = 5s Invincible Flame + Parsa Sacrifice',
    color: '#e74c3c'
  },
  {
    id: 'ali',
    name: 'Ali',
    enName: 'Ali',
    avatar: '👓',
    badge: '🪓 10-Log Flurry',
    desc: '50 Chops = 10 Auto-Cleave Logs without branch hit',
    color: '#e67e22'
  },
  {
    id: 'amirhossein',
    name: 'Amirhossein',
    enName: 'Amirhossein',
    avatar: '🧢',
    badge: '⚡ 2X Score',
    desc: 'Permanent 2X points multiplier on every chop',
    color: '#2980b9'
  },
  {
    id: 'parsa',
    name: 'Parsa',
    enName: 'Parsa',
    avatar: '🛌',
    badge: '💤 2 Blankets',
    desc: 'Sleeps through exhaustion up to 2 times',
    color: '#9b59b6'
  },
  {
    id: 'ahmad',
    name: 'Ahmad',
    enName: 'Ahmad',
    avatar: '🛡️',
    badge: '🛡️ Shield 100',
    desc: 'Every 100 chops = 1 Stacking Branch Shield',
    color: '#2ecc71'
  },
  {
    id: 'erfan',
    name: 'Erfan',
    enName: 'Erfan',
    avatar: '⚡',
    badge: '⚡ 3X Clutch',
    desc: 'Fatigue below 50% = 3X Critical Points!',
    color: '#f39c12'
  },
  {
    id: 'fateme',
    name: 'Fateme',
    enName: 'Fateme',
    avatar: '🪓',
    badge: '🪵 Classic Lumberjack',
    desc: 'Classic mode without abilities (pure skill & speed)',
    color: '#26a69a'
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
  if (nameEl) nameEl.innerText = charData.enName;
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

function selectCharacter(charId) {
  selectedCharacter = charId;
  localStorage.setItem('khanqah_character', charId);
  updateCarouselCard(charId);
  if (charId === 'fateme' && typeof updateCharacterHUD === 'function') {
    updateCharacterHUD('fateme', 'hide');
  }

  // Update standing & death sprite preview on canvas
  if (typeof ta !== 'undefined') {
    if (charId === 'fargol') {
      if (tex_fargol_normal) ta.texture = tex_fargol_normal;
    if (tex_fargol_swing) x.texture = tex_fargol_swing; /* dummy load */
    if (tex_fargol_flame_swing) x.texture = tex_fargol_flame_swing;
      ta.width = 94;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_fargol_died) x.texture = tex_fargol_died;
        x.width = 95;
        x.height = 111;
      }
    } else if (charId === 'ali') {
      if (tex_ali_body) ta.texture = tex_ali_body;
      ta.width = 68;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_ali_died) x.texture = tex_ali_died;
        x.width = 95;
        x.height = 111;
      }
    } else if (charId === 'amirhossein') {
      if (tex_amirhossein_body) ta.texture = tex_amirhossein_body;
      ta.width = 68;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_amirhossein_died) x.texture = tex_amirhossein_died;
        x.width = 95;
        x.height = 111;
      }
    } else if (charId === 'parsa') {
      if (tex_parsa_body) ta.texture = tex_parsa_body;
      ta.width = 94;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_parsa_died) x.texture = tex_parsa_died;
        x.width = 95;
        x.height = 111;
      }
    } else if (charId === 'ahmad') {
      if (tex_ahmad_body) ta.texture = tex_ahmad_body;
      ta.width = 94;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_ahmad_died) x.texture = tex_ahmad_died;
        x.width = 95;
        x.height = 111;
      }
    } else if (charId === 'erfan') {
      if (tex_erfan_body) ta.texture = tex_erfan_body;
      ta.width = 68;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_erfan_died) x.texture = tex_erfan_died;
        x.width = 95;
        x.height = 111;
      }
    } else if (charId === 'fateme') {
      if (tex_fateme_body) ta.texture = tex_fateme_body;
      ta.width = 68;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_fateme_died) x.texture = tex_fateme_died;
        x.width = 95;
        x.height = 111;
      }
    } else {
      if (tex_nima_old) ta.texture = tex_nima_old;
      ta.width = 68;
      ta.height = 140;
      if (typeof S !== 'undefined') S.visible = false;
      if (typeof x !== 'undefined') {
        if (tex_nima_died_old) x.texture = tex_nima_died_old;
        x.width = 95;
        x.height = 111;
      }
    }
    if (typeof V !== 'undefined' && typeof C !== 'undefined') V.render(C);
  }

  if (typeof sa !== 'undefined') {
    if (charId === 'fargol') {
      if (tex_fargol_normal) sa.texture = tex_fargol_normal;
      sa.width = 94;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_fargol_died) w.texture = tex_fargol_died;
        w.width = 95;
        w.height = 111;
      }
    } else if (charId === 'ali') {
      if (tex_ali_body) sa.texture = tex_ali_body;
      sa.width = 68;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_ali_died) w.texture = tex_ali_died;
        w.width = 95;
        w.height = 111;
      }
    } else if (charId === 'amirhossein') {
      if (tex_amirhossein_body) sa.texture = tex_amirhossein_body;
      sa.width = 68;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_amirhossein_died) w.texture = tex_amirhossein_died;
        w.width = 95;
        w.height = 111;
      }
    } else if (charId === 'parsa') {
      if (tex_parsa_body) sa.texture = tex_parsa_body;
      sa.width = 94;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_parsa_died) w.texture = tex_parsa_died;
        w.width = 95;
        w.height = 111;
      }
    } else if (charId === 'ahmad') {
      if (tex_ahmad_body) sa.texture = tex_ahmad_body;
      sa.width = 94;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_ahmad_died) w.texture = tex_ahmad_died;
        w.width = 95;
        w.height = 111;
      }
    } else if (charId === 'erfan') {
      if (tex_erfan_body) sa.texture = tex_erfan_body;
      sa.width = 68;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_erfan_died) w.texture = tex_erfan_died;
        w.width = 95;
        w.height = 111;
      }
    } else if (charId === 'fateme') {
      if (tex_fateme_body) sa.texture = tex_fateme_body;
      sa.width = 68;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_fateme_died) w.texture = tex_fateme_died;
        w.width = 95;
        w.height = 111;
      }
    } else {
      if (tex_nima_old) sa.texture = tex_nima_old;
      sa.width = 68;
      sa.height = 140;
      if (typeof I !== 'undefined') I.visible = false;
      if (typeof H !== 'undefined') H.visible = false;
      if (typeof w !== 'undefined') {
        if (tex_nima_died_old) w.texture = tex_nima_died_old;
        w.width = 95;
        w.height = 111;
      }
    }
    if (typeof V !== 'undefined' && typeof C !== 'undefined') V.render(C);
    if (typeof U !== 'undefined' && typeof k !== 'undefined') U.render(k);
  }

  triggerTelegramHaptic('selection');
}

function rotateCharacter(direction) {
  var curIdx = -1;
  for (var i = 0; i < ALL_CHARACTERS.length; i++) {
    if (ALL_CHARACTERS[i].id === selectedCharacter) {
      curIdx = i;
      break;
    }
  }
  if (curIdx < 0) curIdx = 0;
  var nextIdx = (curIdx + direction + ALL_CHARACTERS.length) % ALL_CHARACTERS.length;
  selectCharacter(ALL_CHARACTERS[nextIdx].id);
}

function initCharacterSelector() {
  var prevBtn = document.getElementById('btn_char_prev');
  var nextBtn = document.getElementById('btn_char_next');
  var card = document.getElementById('char_carousel_card');
  var dotsContainer = document.getElementById('char_carousel_dots');

  function bindMobileTouch(el, action) {
    if (!el || el._touchBound) return; // Prevent double-binding
    el._touchBound = true;
    var lastTouchTime = 0;
    var lastActionTime = 0;
    function handleEvent(e) {
      var now = +new Date;
      if (e && e.type === 'touchstart') {
        lastTouchTime = now;
      } else if (e && e.type === 'click') {
        // If click happens within 500ms of a touchstart, it's a ghost click. Ignore it.
        if (now - lastTouchTime < 500) return;
      }
      // Simple debounce to prevent rapid fire (PC mouse double clicks etc)
      if (now - lastActionTime < 50) return;
      lastActionTime = now;

      if (e) {
        if (e.stopPropagation) e.stopPropagation();
        if (e.cancelable && e.preventDefault) e.preventDefault();
      }
      action();
    }
    el.ontouchstart = handleEvent;
    el.onclick = handleEvent;
    el.addEventListener('touchstart', handleEvent, { passive: false });
    el.addEventListener('click', handleEvent);
  }

  // Build dots
  if (dotsContainer && !dotsContainer.hasChildNodes()) {
    dotsContainer.innerHTML = '';
    ALL_CHARACTERS.forEach(function(c, idx) {
      var dot = document.createElement('div');
      dot.className = 'char-carousel-dot' + (c.id === selectedCharacter ? ' active' : '');
      dot.setAttribute('data-char', c.id);
      dot.setAttribute('data-index', idx);
      dot.setAttribute('title', c.enName + ' (' + c.name + ')');
      bindMobileTouch(dot, function() {
        selectCharacter(c.id);
      });
      dotsContainer.appendChild(dot);
    });
  }

  if (prevBtn) {
    bindMobileTouch(prevBtn, function() {
      rotateCharacter(-1);
    });
  }

  if (nextBtn) {
    bindMobileTouch(nextBtn, function() {
      rotateCharacter(1);
    });
  }

  if (card && !card._touchBound) {
    card._touchBound = true;
    var touchStartX = 0;
    var touchStartY = 0;
    var touchStartTime = 0;
    var lastCardAction = 0;

    var lastCardTouchTime = 0;
    function triggerCardTap(e) {
      var now = +new Date;
      if (e && (e.type === 'touchstart' || e.type === 'touchend')) {
        lastCardTouchTime = now;
      } else if (e && e.type === 'click') {
        if (now - lastCardTouchTime < 500) return;
      }
      
      if (now - lastCardAction < 50) return;
      lastCardAction = now;
      if (e) {
        if (e.stopPropagation) e.stopPropagation();
        if (e.cancelable && e.preventDefault) e.preventDefault();
      }
      rotateCharacter(1);
    }

    card.addEventListener('touchstart', function(e) {
      if (e.touches && e.touches.length > 0) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        touchStartTime = +new Date; lastCardTouchTime = touchStartTime;
      }
      if (e.stopPropagation) e.stopPropagation();
    }, { passive: false });

    card.addEventListener('touchend', function(e) {
      if (e.stopPropagation) e.stopPropagation();
      if (e.cancelable && e.preventDefault) e.preventDefault();

      var now = +new Date;
      if (now - lastCardAction < 50) return;

      var touchEndX = (e.changedTouches && e.changedTouches.length > 0) ? e.changedTouches[0].clientX : touchStartX;
      var touchEndY = (e.changedTouches && e.changedTouches.length > 0) ? e.changedTouches[0].clientY : touchStartY;
      var diffX = touchEndX - touchStartX;
      var diffY = touchEndY - touchStartY;
      var duration = now - touchStartTime;

      if (Math.abs(diffX) > 25 && Math.abs(diffX) > Math.abs(diffY)) {
        // Horizontal swipe!
        lastCardAction = now;
        rotateCharacter(diffX < 0 ? 1 : -1);
      } else if (Math.abs(diffX) < 20 && Math.abs(diffY) < 20 && duration < 600) {
        // Tap on card!
        triggerCardTap(e);
      }
    }, { passive: false });

    card.addEventListener('click', triggerCardTap);
    card.onclick = triggerCardTap;
  }

  updateCarouselCard(selectedCharacter);
}

window.khanqahGame = {
  getCharacter: function() { return selectedCharacter; },
  setCharacter: selectCharacter,
  getNimaPhase: function() { return nimaPhase; },
  getFargolChops: function() { return fargolChops; },
  isFargolFlaming: function() { return fargolFlameActive; },
  isFargolSacrificeAvailable: function() { return fargolSacrificeAvailable; },
  getAliChops: function() { return aliChops; },
  isAliFlurryActive: function() { return aliFlurryActive; },
  getAliFlurryRemaining: function() { return aliFlurryRemaining; },
  triggerAliFlurry: triggerAliFlurry,
  getParsaSleepCount: function() { return parsaSleepCount; },
  isParsaSleeping: function() { return parsaSleeping; },
  isParsaWaitingForChop: function() { return parsaWaitingForChop; },
  triggerParsaNap: triggerParsaNap,
  getAhmadChops: function() { return ahmadChops; },
  getAhmadShieldCount: function() { return ahmadShieldCount; },
  isAhmadShieldActive: function() { return ahmadShieldCount > 0; },
  setAhmadChops: function(n) { ahmadChops = n; },
  setAhmadShieldCount: function(c) { ahmadShieldCount = c; ahmadShieldActive = c > 0; },
  setAhmadShield: function(b) { ahmadShieldCount = b ? 1 : 0; ahmadShieldActive = b; },
  isErfanClutch: function() { return selectedCharacter === "erfan" && ((ba - +new Date) / qa < 0.5); },
  isAlive: function() { return typeof aa !== 'undefined' ? aa : false; },
  isInResult: function() { return typeof h !== 'undefined' ? h : false; },
  isInGreet: function() { return typeof Z !== 'undefined' ? !Z : true; },
  resetToCharacterSelection: function() { if (typeof rb === 'function') rb(); },
  getTree: function() { return typeof da !== 'undefined' && da ? da.slice(0, 5) : []; },
  getPlayerSide: function() { return typeof m !== 'undefined' ? m : true; },
  chop: function(left) { if (typeof Ca === 'function') Ca(left); },
  kill: function() { if (typeof Va === 'function') Va(); },
  triggerFargolFlame: function() {
    fargolFlameActive = true;
    fargolFlameStartTime = +new Date;
    if (typeof sa !== 'undefined' && tex_fargol_flame) {
      sa.texture = tex_fargol_flame;
      sa.width = 94;
      sa.height = 142;
    }
    if (typeof ta !== 'undefined' && tex_fargol_flame) {
      ta.texture = tex_fargol_flame;
      ta.width = 94;
      ta.height = 142;
    }
    // spawnCombatPopup removed
  }
};

// ==========================================
// ANTI-CHEAT HONEYPOT SENSORS & CONSOLE BAIT
// ==========================================
var _honeypot_cheated = false;
var _honeypot_reason = "";
var _shadow_score = 0 ^ 0x5F3759DF;
var _chop_count = 0;
var _game_start_time = 0;
var _recent_chops = [];

function _syncShadowScore() {
  _shadow_score = ca ^ 0x5F3759DF;
}

function _onCheatScoreInput(val, source) {
  var num = 0;
  if (typeof val === 'object' && val !== null) {
    num = val.score !== undefined ? val.score : (val.s !== undefined ? val.s : 0);
  } else {
    num = parseInt(val, 10);
  }
  if (isNaN(num)) num = 0;
  
  ca = num;
  _syncShadowScore();
  _honeypot_cheated = true;
  _honeypot_reason = source || "console_score_tampering";
  
  // Immediately update UI score so cheater sees their entered score on screen:
  Fa();
  
  try {
    console.log("%c✓ Score set to " + num + " (Honeypot Active)", "color: #2e7d32; font-weight: bold; font-size: 13px;");
    console.log("%cGame status: Score updated successfully.", "color: #555;");
  } catch(e) {}
  
  return { success: true, score: ca };
}

try {
  Object.defineProperty(window, "score", {
    get: function() { return ca; },
    set: function(val) { _onCheatScoreInput(val, "console_score_assignment"); },
    configurable: true
  });
} catch(e) {}

window.setScore = function(val) { return _onCheatScoreInput(val, "window_setScore"); };

window.game = window.game || {};
try {
  Object.defineProperty(window.game, "score", {
    get: function() { return ca; },
    set: function(val) { _onCheatScoreInput(val, "game_score_assignment"); },
    configurable: true
  });
} catch(e) {}
window.game.setScore = function(val) { return _onCheatScoreInput(val, "game_setScore"); };

window.Lumberjack = window.Lumberjack || {};
window.Lumberjack.setScore = function(val) { return _onCheatScoreInput(val, "lumberjack_setScore"); };
window.Lumberjack.getScore = function() { return ca; };

function getPlayerDisplayName() {
  if (typeof Ba === 'string' && Ba.length > 0) return Ba;
  try {
    var tgUser = window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user;
    if (tgUser) {
      if (tgUser.first_name) return tgUser.first_name;
      if (tgUser.username) return "@" + tgUser.username;
    }
  } catch(e) {}
  return "کاربر";
}

function generateScoreToken(score, startTime, chopCount) {
  var seed = (score * 31 + chopCount * 17 + Math.floor(startTime / 1000)) ^ 0x5A5A5A5A;
  return "OK_" + Math.abs(seed).toString(16);
}


window.KhanqahAntiCheat = {
  isCheater: function() { return _honeypot_cheated; },
  getReason: function() { return _honeypot_reason; },
  getShadowScore: function() { return _shadow_score; },
  triggerTrap: function(reason) { _honeypot_cheated = true; _honeypot_reason = reason || 'manual_test'; }
};

// ----------------------------------------------------
'''

closure_pattern = r'\(function\s*\(\s*ua\s*,\s*M\s*,\s*Da\s*,\s*b\s*,\s*kb\s*\)\s*\{'
match = re.search(closure_pattern, code)
code = code[:match.end()] + multi_char_engine_code + code[match.end():]

# 5. Load textures in the second Xa call (Nima + Fargol + Ali + Amirhossein + Parsa + Ahmad + Erfan + Fateme)
code = code.replace(
    'Xa({bg_trees:',
    'Xa({nima_old:"images/nima_body_old.png?v=2",nima_young:"images/nima_body_young.png?v=2",nima_swing_old:"images/nima_swing_old.png?v=2",nima_swing_young:"images/nima_swing_young.png?v=2",nima_died_old:"images/nima_died_old.png?v=2",nima_died_young:"images/nima_died_young.png?v=2",fargol_normal:"images/fargol_body.png?v=2",fargol_swing:"images/fargol_swing.png?v=2",fargol_flame:"images/fargol_body_flame.png?v=2",fargol_swing_flame:"images/fargol_swing_flame.png?v=2",fargol_died:"images/fargol_died.png?v=2",ali_body:"images/ali_body.png?v=2",ali_swing:"images/ali_swing.png?v=2",ali_died:"images/ali_died.png?v=2",amirhossein_body:"images/amirhossein_body.png?v=2",amirhossein_swing:"images/amirhossein_swing.png?v=2",amirhossein_died:"images/amirhossein_died.png?v=2",parsa_body:"images/parsa_body.png?v=2",parsa_swing:"images/parsa_swing.png?v=2",parsa_sleep:"images/parsa_sleep.png?v=2",parsa_died:"images/parsa_died.png?v=2",parsa_jump:"images/parsa_jump.png?v=2",ahmad_body:"images/ahmad_body.png?v=2",ahmad_swing:"images/ahmad_swing.png?v=2",ahmad_died:"images/ahmad_died.png?v=2",erfan_body:"images/erfan_body.png?v=2",erfan_swing:"images/erfan_swing.png?v=2",erfan_died:"images/erfan_died.png?v=2",fateme_body:"images/fateme_body.png?v=2",fateme_swing:"images/fateme_swing.png?v=2",fateme_died:"images/fateme_died.png?v=2",bg_trees:'
)

# 6. Setup textures & initial sprites
texture_setup = '''
// Setup Character Textures from loaded images
try {
  tex_nima_old = new b.Texture(new b.BaseTexture(a.nima_old));
  tex_nima_young = new b.Texture(new b.BaseTexture(a.nima_young));
  tex_nima_swing_old = new b.Texture(new b.BaseTexture(a.nima_swing_old));
  tex_nima_swing_young = new b.Texture(new b.BaseTexture(a.nima_swing_young));
  tex_nima_died_old = new b.Texture(new b.BaseTexture(a.nima_died_old));
  tex_nima_died_young = new b.Texture(new b.BaseTexture(a.nima_died_young));
  tex_fargol_normal = new b.Texture(new b.BaseTexture(a.fargol_normal));
  tex_fargol_swing = new b.Texture(new b.BaseTexture(a.fargol_swing));
  tex_fargol_flame_swing = new b.Texture(new b.BaseTexture(a.fargol_swing_flame));
  tex_fargol_flame = new b.Texture(new b.BaseTexture(a.fargol_flame));
  tex_fargol_died = new b.Texture(new b.BaseTexture(a.fargol_died));
  tex_ali_body = new b.Texture(new b.BaseTexture(a.ali_body));
  tex_ali_swing = new b.Texture(new b.BaseTexture(a.ali_swing));
  tex_ali_died = new b.Texture(new b.BaseTexture(a.ali_died));
  tex_amirhossein_body = new b.Texture(new b.BaseTexture(a.amirhossein_body));
  tex_amirhossein_swing = new b.Texture(new b.BaseTexture(a.amirhossein_swing));
  tex_amirhossein_died = new b.Texture(new b.BaseTexture(a.amirhossein_died));
  tex_parsa_body = new b.Texture(new b.BaseTexture(a.parsa_body));
  tex_parsa_swing = new b.Texture(new b.BaseTexture(a.parsa_swing));
  tex_parsa_sleep = new b.Texture(new b.BaseTexture(a.parsa_sleep));
  tex_parsa_died = new b.Texture(new b.BaseTexture(a.parsa_died));
  tex_parsa_jump = new b.Texture(new b.BaseTexture(a.parsa_jump));
  tex_ahmad_body = new b.Texture(new b.BaseTexture(a.ahmad_body));
  tex_ahmad_swing = new b.Texture(new b.BaseTexture(a.ahmad_swing));
  tex_ahmad_died = new b.Texture(new b.BaseTexture(a.ahmad_died));
  tex_erfan_body = new b.Texture(new b.BaseTexture(a.erfan_body));
  tex_erfan_swing = new b.Texture(new b.BaseTexture(a.erfan_swing));
  tex_erfan_died = new b.Texture(new b.BaseTexture(a.erfan_died));
  tex_fateme_body = new b.Texture(new b.BaseTexture(a.fateme_body));
  tex_fateme_swing = new b.Texture(new b.BaseTexture(a.fateme_swing));
  tex_fateme_died = new b.Texture(new b.BaseTexture(a.fateme_died));
} catch(e) {
  console.error('Character texture loading error:', e);
}
initCharacterSelector();
'''

sa_pattern = r'sa=new b\.Sprite\(g\(a\.lumber_body\)\);'
match_sa = re.search(sa_pattern, code)
if match_sa:
    code = code[:match_sa.start()] + texture_setup + code[match_sa.start():]
    code = code.replace(
        'sa=new b.Sprite(g(a.lumber_body));sa.width=50;sa.height=107;',
        'sa=new b.Sprite((selectedCharacter==="fateme"?tex_fateme_body:(selectedCharacter==="fargol"?tex_fargol_normal:(selectedCharacter==="ali"?tex_ali_body:(selectedCharacter==="amirhossein"?tex_amirhossein_body:(selectedCharacter==="parsa"?tex_parsa_body:(selectedCharacter==="ahmad"?tex_ahmad_body:(selectedCharacter==="erfan"?tex_erfan_body:tex_nima_old)))))))||g(a.lumber_body));sa.width=((selectedCharacter==="fargol"||selectedCharacter==="parsa"||selectedCharacter==="ahmad")?94:68);sa.height=140;if(typeof S!=="undefined")S.visible=false;if(typeof I!=="undefined")I.visible=false;if(typeof H!=="undefined")H.visible=false;'
    )
    code = code.replace(
        'ta=new b.Sprite(g(a.lumber_body));ta.width=50;ta.height=107;',
        'ta=new b.Sprite((selectedCharacter==="fateme"?tex_fateme_body:(selectedCharacter==="fargol"?tex_fargol_normal:(selectedCharacter==="ali"?tex_ali_body:(selectedCharacter==="amirhossein"?tex_amirhossein_body:(selectedCharacter==="parsa"?tex_parsa_body:(selectedCharacter==="ahmad"?tex_ahmad_body:(selectedCharacter==="erfan"?tex_erfan_body:tex_nima_old)))))))||g(a.lumber_body));ta.width=((selectedCharacter==="fargol"||selectedCharacter==="parsa"||selectedCharacter==="ahmad")?94:68);ta.height=140;if(typeof S!=="undefined")S.visible=false;if(typeof I!=="undefined")I.visible=false;if(typeof H!=="undefined")H.visible=false;'
    )
    code = code.replace(
        'w=new b.Sprite(g(a.lumber_died));w.width=73;w.height=85;',
        'w=new b.Sprite((selectedCharacter==="fateme"?tex_fateme_died:(selectedCharacter==="fargol"?tex_fargol_died:(selectedCharacter==="ali"?tex_ali_died:(selectedCharacter==="amirhossein"?tex_amirhossein_died:(selectedCharacter==="parsa"?tex_parsa_died:(selectedCharacter==="ahmad"?tex_ahmad_died:(selectedCharacter==="erfan"?tex_erfan_died:tex_nima_died_old)))))))||g(a.lumber_died));w.width=95;w.height=111;'
    )
    code = code.replace(
        'x=new b.Sprite(g(a.lumber_died));x.width=73;x.height=85;',
        'x=new b.Sprite((selectedCharacter==="fateme"?tex_fateme_died:(selectedCharacter==="fargol"?tex_fargol_died:(selectedCharacter==="ali"?tex_ali_died:(selectedCharacter==="amirhossein"?tex_amirhossein_died:(selectedCharacter==="parsa"?tex_parsa_died:(selectedCharacter==="ahmad"?tex_ahmad_died:(selectedCharacter==="erfan"?tex_erfan_died:tex_nima_died_old)))))))||g(a.lumber_died));x.width=95;x.height=111;'
    )

# 7. In pb() (start game):
pb_pattern = r'function pb\(\)\s*\{'
match_pb = re.search(pb_pattern, code)
if match_pb:
    pb_injection = '''
  gameStartTime = +new Date;
  nimaPhase = 'old';
  isRejuvenated = false;
  fargolChops = 0;
  fargolFlameActive = false;
  fargolFlameStartTime = 0;
  fargolSacrificeAvailable = true;
  fargolSacrificeInProgress = false;
  if (typeof aliFlurryTimer !== 'undefined' && aliFlurryTimer) {
    clearInterval(aliFlurryTimer);
    aliFlurryTimer = null;
  }
  aliChops = 0;
  aliFlurryActive = false;
  aliFlurryRemaining = 0;
  parsaSleeping = false;
  parsaWaitingForChop = false;
  if (typeof parsaSleepTimer !== 'undefined' && parsaSleepTimer) {
    clearTimeout(parsaSleepTimer);
    parsaSleepTimer = null;
  }
  parsaSleepCount = 0;
  parsaSleeping = false;
  parsaWaitingForChop = false;
  parsaSleepStartTime = 0;
  if (typeof parsaSleepTimer !== 'undefined' && parsaSleepTimer) {
    clearTimeout(parsaSleepTimer);
    parsaSleepTimer = null;
  }
  ahmadChops = 0;
  ahmadShieldCount = 0;
  ahmadShieldActive = false;
  if (typeof sa !== 'undefined') sa.x = 0;

  if (selectedCharacter === 'fargol') {
    if (typeof sa !== 'undefined') {
      if (tex_fargol_normal) sa.texture = tex_fargol_normal;
      sa.width = 94;
      sa.height = 140;
      sa.rotation = 0;
    }
    if (typeof ta !== 'undefined') {
      if (tex_fargol_normal) ta.texture = tex_fargol_normal;
    if (tex_fargol_swing) x.texture = tex_fargol_swing; /* dummy load */
    if (tex_fargol_flame_swing) x.texture = tex_fargol_flame_swing;
      ta.width = 94;
      ta.height = 140;
    }
    if (typeof I !== 'undefined') I.visible = false;
    if (typeof H !== 'undefined') H.visible = false;
    if (typeof S !== 'undefined') S.visible = false;
    if (typeof w !== 'undefined') {
      if (tex_fargol_died) w.texture = tex_fargol_died;
      w.width = 95;
      w.height = 111;
    }
    if (typeof x !== 'undefined') {
      if (tex_fargol_died) x.texture = tex_fargol_died;
      x.width = 95;
      x.height = 111;
    }
    updateCharacterHUD('fargol', 'normal', 0, '0/100', true);
  } else if (selectedCharacter === 'ali') {
    if (typeof sa !== 'undefined') {
      if (tex_ali_body) sa.texture = tex_ali_body;
      sa.width = 68;
      sa.height = 140;
      sa.rotation = 0;
    }
    if (typeof ta !== 'undefined') {
      if (tex_ali_body) ta.texture = tex_ali_body;
      ta.width = 68;
      ta.height = 140;
    }
    if (typeof I !== 'undefined') I.visible = false;
    if (typeof H !== 'undefined') H.visible = false;
    if (typeof S !== 'undefined') S.visible = false;
    if (typeof w !== 'undefined') {
      if (tex_ali_died) w.texture = tex_ali_died;
      w.width = 95;
      w.height = 111;
    }
    if (typeof x !== 'undefined') {
      if (tex_ali_died) x.texture = tex_ali_died;
      x.width = 95;
      x.height = 111;
    }
    updateCharacterHUD('ali', 'normal', 0, '0/50', false);
  } else if (selectedCharacter === 'amirhossein') {
    if (typeof sa !== 'undefined') {
      if (tex_amirhossein_body) sa.texture = tex_amirhossein_body;
      sa.width = 68;
      sa.height = 140;
      sa.rotation = 0;
    }
    if (typeof ta !== 'undefined') {
      if (tex_amirhossein_body) ta.texture = tex_amirhossein_body;
      ta.width = 68;
      ta.height = 140;
    }
    if (typeof I !== 'undefined') I.visible = false;
    if (typeof H !== 'undefined') H.visible = false;
    if (typeof S !== 'undefined') S.visible = false;
    if (typeof w !== 'undefined') {
      if (tex_amirhossein_died) w.texture = tex_amirhossein_died;
      w.width = 95;
      w.height = 111;
    }
    if (typeof x !== 'undefined') {
      if (tex_amirhossein_died) x.texture = tex_amirhossein_died;
      x.width = 95;
      x.height = 111;
    }
    updateCharacterHUD('amirhossein', 'normal', 100, '۲X فعال', false);
  } else if (selectedCharacter === 'parsa') {
    if (typeof sa !== 'undefined') {
      if (tex_parsa_body) sa.texture = tex_parsa_body;
      sa.width = 94;
      sa.height = 140;
      sa.rotation = 0;
    }
    if (typeof ta !== 'undefined') {
      if (tex_parsa_body) ta.texture = tex_parsa_body;
      ta.width = 94;
      ta.height = 140;
    }
    if (typeof I !== 'undefined') I.visible = false;
    if (typeof H !== 'undefined') H.visible = false;
    if (typeof S !== 'undefined') S.visible = false;
    if (typeof w !== 'undefined') {
      if (tex_parsa_died) w.texture = tex_parsa_died;
      w.width = 95;
      w.height = 111;
    }
    if (typeof x !== 'undefined') {
      if (tex_parsa_died) x.texture = tex_parsa_died;
      x.width = 95;
      x.height = 111;
    }
    updateCharacterHUD('parsa', 'normal', 100, '۲/۲ پتو', true);
  } else if (selectedCharacter === 'ahmad') {
    if (typeof sa !== 'undefined') {
      if (tex_ahmad_body) sa.texture = tex_ahmad_body;
      sa.width = 94;
      sa.height = 140;
      sa.rotation = 0;
    }
    if (typeof ta !== 'undefined') {
      if (tex_ahmad_body) ta.texture = tex_ahmad_body;
      ta.width = 94;
      ta.height = 140;
    }
    if (typeof I !== 'undefined') I.visible = false;
    if (typeof H !== 'undefined') H.visible = false;
    if (typeof S !== 'undefined') S.visible = false;
    if (typeof w !== 'undefined') {
      if (tex_ahmad_died) w.texture = tex_ahmad_died;
      w.width = 95;
      w.height = 111;
    }
    if (typeof x !== 'undefined') {
      if (tex_ahmad_died) x.texture = tex_ahmad_died;
      x.width = 95;
      x.height = 111;
    }
    updateCharacterHUD('ahmad', 'normal', 0, '0/100', false);
  } else if (selectedCharacter === 'erfan') {
    if (typeof sa !== 'undefined') {
      if (tex_erfan_body) sa.texture = tex_erfan_body;
      sa.width = 68;
      sa.height = 140;
      sa.rotation = 0;
    }
    if (typeof ta !== 'undefined') {
      if (tex_erfan_body) ta.texture = tex_erfan_body;
      ta.width = 68;
      ta.height = 140;
    }
    if (typeof I !== 'undefined') I.visible = false;
    if (typeof H !== 'undefined') H.visible = false;
    if (typeof S !== 'undefined') S.visible = false;
    if (typeof w !== 'undefined') {
      if (tex_erfan_died) w.texture = tex_erfan_died;
      w.width = 95;
      w.height = 111;
    }
    if (typeof x !== 'undefined') {
      if (tex_erfan_died) x.texture = tex_erfan_died;
      x.width = 95;
      x.height = 111;
    }
    updateCharacterHUD('erfan', 'normal', 100, '۱۰۰%', false);
  } else if (selectedCharacter === 'fateme') {
    if (typeof sa !== 'undefined') {
      if (tex_fateme_body) sa.texture = tex_fateme_body;
      sa.width = 68;
      sa.height = 140;
      sa.rotation = 0;
    }
    if (typeof ta !== 'undefined') {
      if (tex_fateme_body) ta.texture = tex_fateme_body;
      ta.width = 68;
      ta.height = 140;
    }
    if (typeof I !== 'undefined') I.visible = false;
    if (typeof H !== 'undefined') H.visible = false;
    if (typeof S !== 'undefined') S.visible = false;
    if (typeof w !== 'undefined') {
      if (tex_fateme_died) w.texture = tex_fateme_died;
      w.width = 95;
      w.height = 111;
    }
    if (typeof x !== 'undefined') {
      if (tex_fateme_died) x.texture = tex_fateme_died;
      x.width = 95;
      x.height = 111;
    }
    updateCharacterHUD('fateme', 'hide');
  } else {
    if (typeof sa !== 'undefined') {
      if (tex_nima_old) sa.texture = tex_nima_old;
      sa.width = 68;
      sa.height = 140;
    }
    if (typeof ta !== 'undefined') {
      if (tex_nima_old) ta.texture = tex_nima_old;
      ta.width = 68;
      ta.height = 140;
    }
    if (typeof I !== 'undefined') I.visible = false;
    if (typeof H !== 'undefined') H.visible = false;
    if (typeof S !== 'undefined') S.visible = false;
    if (typeof w !== 'undefined') {
      if (tex_nima_died_old) w.texture = tex_nima_died_old;
      w.width = 95;
      w.height = 111;
    }
    if (typeof x !== 'undefined') {
      if (tex_nima_died_old) x.texture = tex_nima_died_old;
      x.width = 95;
      x.height = 111;
    }
    updateCharacterHUD('nima', 'old', 0, '15s', false);
  }
'''
    code = code[:match_pb.end()] + pb_injection + code[match_pb.end():]

# 8. In Ta() (frame tick):
ta_pattern = r'function Ta\(\)\s*\{'
match_ta = re.search(ta_pattern, code)
if match_ta:
    ta_injection = '''
  if (fargolSacrificeInProgress) {
    ba = +new Date + qa;
    if (typeof Ua === 'function') Ua();
  }
  if (aa && (za || (selectedCharacter === 'parsa' && (parsaSleeping || parsaWaitingForChop)))) {
    if (selectedCharacter === 'fargol') {
      if (fargolFlameActive) {
        var flameElapsed = +new Date - fargolFlameStartTime;
        if (flameElapsed < 5000) {
          ba = +new Date + qa; // Stamina locked at max during flame
          var remFlame = ((5000 - flameElapsed) / 1000).toFixed(1);
          var flamePercent = Math.min(100, Math.max(0, ((5000 - flameElapsed) / 5000) * 100));
          updateCharacterHUD('fargol', 'flame', flamePercent, remFlame + 's', fargolSacrificeAvailable);
        } else {
          fargolFlameActive = false;
          if (typeof sa !== 'undefined') {
            if (tex_fargol_normal) sa.texture = tex_fargol_normal;
            sa.width = 94;
            sa.height = 140;
          }
          if (typeof ta !== 'undefined') {
            if (tex_fargol_normal) ta.texture = tex_fargol_normal;
    if (tex_fargol_swing) x.texture = tex_fargol_swing; /* dummy load */
    if (tex_fargol_flame_swing) x.texture = tex_fargol_flame_swing;
            ta.width = 94;
            ta.height = 140;
          }
        }
      } else {
        var currentProg = fargolChops % 100;
        updateCharacterHUD('fargol', 'normal', currentProg, currentProg + '/100', fargolSacrificeAvailable);
      }
    } else if (selectedCharacter === 'ali') {
      if (aliFlurryActive) {
        ba = +new Date + qa; // Stamina locked at max during flurry
        var remFlurryPct = Math.min(100, Math.max(0, (aliFlurryRemaining / 10) * 100));
        updateCharacterHUD('ali', 'flurry', remFlurryPct, aliFlurryRemaining + ' کنده', false);
      } else {
        var aliProg = ((aliChops % 50) / 50) * 100;
        updateCharacterHUD('ali', 'normal', aliProg, (aliChops % 50) + '/50', false);
      }
    } else if (selectedCharacter === 'amirhossein') {
      updateCharacterHUD('amirhossein', 'normal', 100, '۲X فعال', false);
    } else if (selectedCharacter === 'parsa') {
      var remB = Math.max(0, 2 - parsaSleepCount);
      if (parsaSleeping) {
        var sleepElapsed = +new Date - parsaSleepStartTime;
        var remSleep = Math.max(0, (3000 - sleepElapsed) / 1000).toFixed(1);
        ba = +new Date + qa; // Stamina held full
        if (typeof Ua === 'function') Ua(); // Keep fatigue bar full
        updateCharacterHUD('parsa', 'sleep', Math.max(0, ((3000 - sleepElapsed) / 3000) * 100), remSleep + 's خواب', false);
      } else if (parsaWaitingForChop) {
        ba = +new Date + qa; // Fatigue bar stopped until user starts chopping!
        if (typeof Ua === 'function') Ua(); // Keep fatigue bar full at 100%
        updateCharacterHUD('parsa', 'waiting', 100, 'آماده تبر (' + remB + '/2)', false);
      } else {
        updateCharacterHUD('parsa', 'normal', (remB / 2) * 100, remB + '/2 پتو', false);
      }
    } else if (selectedCharacter === 'ahmad') {
      var ahmProg = ahmadChops % 100;
      updateCharacterHUD('ahmad', ahmadShieldCount > 0 ? 'shield' : 'normal', ahmProg, ahmProg + '/100', ahmadShieldCount > 0);
    } else if (selectedCharacter === 'erfan') {
      var curStaminaRatio = Math.max(0, Math.min(1, (ba - +new Date) / qa));
      var isClutch = curStaminaRatio < 0.5;
      updateCharacterHUD('erfan', isClutch ? 'active' : 'normal', curStaminaRatio * 100, isClutch ? '۳X فعال! 🔥' : Math.round(curStaminaRatio * 100) + '%', isClutch);
    } else if (selectedCharacter === 'fateme') {
      updateCharacterHUD('fateme', 'hide');
    } else {
      var elapsed = +new Date - gameStartTime;
      var cycleTime = elapsed % 20000;
      if (cycleTime >= 15000) {
        var remainingRejuv = ((20000 - cycleTime) / 1000).toFixed(1);
        var youngPercent = Math.min(100, Math.max(0, ((20000 - cycleTime) / 5000) * 100));
        if (!isRejuvenated) {
          isRejuvenated = true;
          nimaPhase = 'young';
          if (typeof sa !== 'undefined' && tex_nima_young) { sa.texture = tex_nima_young; sa.width = 68; sa.height = 140; }
          if (typeof ta !== 'undefined' && tex_nima_young) { ta.texture = tex_nima_young; ta.width = 68; ta.height = 140; }
          spawnCombatPopup('⚡ طوفان جوانی! ⚡', 'young');
          triggerTelegramHaptic('heavy');
        }
        ba = +new Date + qa;
        updateCharacterHUD('nima', 'young', youngPercent, remainingRejuv + 's', false);
      } else {
        if (isRejuvenated) {
          isRejuvenated = false;
          nimaPhase = 'old';
          if (typeof sa !== 'undefined' && tex_nima_old) { sa.texture = tex_nima_old; sa.width = 68; sa.height = 140; }
          if (typeof ta !== 'undefined' && tex_nima_old) { ta.texture = tex_nima_old; ta.width = 68; ta.height = 140; }
        }
        var toRejuv = Math.max(0, Math.ceil((15000 - cycleTime) / 1000));
        var oldPercent = Math.min(100, Math.max(0, (cycleTime / 15000) * 100));
        updateCharacterHUD('nima', 'old', oldPercent, toRejuv + 's', false);
      }
    }
  }
'''
    code = code[:match_ta.end()] + ta_injection + code[match_ta.end():]

# 9. In Ca(a) (chop):
code = re.sub(r'function Ca\(a\)\s*\{', 'function Ca(a, e) {', code, count=1)
ca_pattern = r'function Ca\(a, e\)\s*\{'
match_ca = re.search(ca_pattern, code)
if match_ca:
    ca_pre_injection = '''
  if (e && e.isTrusted === false) {
    _honeypot_cheated = true;
    _honeypot_reason = 'untrusted_event';
  }
  var _nowChop = +new Date;
  if (!_game_start_time) _game_start_time = _nowChop;
  _chop_count++;
  _recent_chops.push(_nowChop);
  while (_recent_chops.length > 0 && _recent_chops[0] < _nowChop - 1000) {
    _recent_chops.shift();
  }
  var _elapsedSec = (_nowChop - _game_start_time) / 1000;
  // Inhuman speed limit removed

  if (fargolSacrificeInProgress) return;
  if (aa && selectedCharacter === 'fargol' && fargolFlameActive) {
    za || (za = !0, ba = +new Date + 4250);
    var b_chk = da[0];
    if (b_chk && a === (0 > b_chk)) {
      // BRANCH INVINCIBILITY: Shatter obstacle without dying!
      1 == Math.abs(b_chk) && $a(a, !0);
      ba = +new Date + qa;
      ca++;
      _syncShadowScore();
      ca % 20 || (Ha++, nb());
      Fa();
      $a(a);
      wa(a, !0, 2 == Math.abs(b_chk));
      // spawnCombatPopup removed
      triggerTelegramHaptic('heavy');
      return;
    }
  }
  if (aa && selectedCharacter === 'ali' && aliFlurryActive) {
    if (!isFlurryChop) {
      // Auto-flurry is active: ignore manual user button taps so combo is uninterrupted
      return;
    }
    za || (za = !0, ba = +new Date + 4250);
    var b_ali = da[0];
    if (b_ali && a === (0 > b_ali)) {
      // Emergency branch cleave: shatter branch safely without dying!
      1 == Math.abs(b_ali) && $a(a, !0);
    }
  }
  if (aa && selectedCharacter === 'parsa') {
    if (parsaSleeping) {
      // Still asleep during 3 seconds: ignore chop inputs!
      return;
    }
    if (parsaWaitingForChop) {
      parsaWaitingForChop = false;
      za = true; // User started chopping, resume fatigue bar!
      ba = +new Date + qa;
    }
  }
  if (aa && selectedCharacter === 'ahmad' && ahmadShieldCount > 0) {
    var b_ahm = da[0];
    if (b_ahm && a === (0 > b_ahm)) {
      // BRANCH SHIELD ABSORPTION: Shatter obstacle without dying!
      1 == Math.abs(b_ahm) && $a(a, !0);
      ahmadShieldCount--;
      ahmadShieldActive = ahmadShieldCount > 0;
      ba = +new Date + qa; // Full stamina refill
      ca++;
      ca % 20 || (Ha++, nb());
      Fa();
      $a(a);
      wa(a, !0, 2 == Math.abs(b_ahm));
      if (ahmadShieldCount > 0) {
        spawnCombatPopup('🛡️ سپر شکست و جان سالم به در برد! (' + ahmadShieldCount + ' باقی‌مانده) 💥', 'crit');
      } else {
        spawnCombatPopup('🛡️ آخرین سپر احمد را نجات داد! 💥', 'crit');
      }
      triggerTelegramHaptic('heavy');
      var ahmProg = ahmadChops % 100;
      updateCharacterHUD('ahmad', ahmadShieldCount > 0 ? 'shield' : 'normal', ahmProg, ahmProg + '/100', ahmadShieldCount > 0);
      return;
    }
  }
'''
    code = code[:match_ca.end()] + ca_pre_injection + code[match_ca.end():]

# In Ca(a), when a successful cut occurs:
code = code.replace(
    'Fa(),$a(a));wa(a,!0,2==Math.abs(b))',
    '''Fa(),$a(a));
    if (selectedCharacter === 'fargol') {
      if (!fargolFlameActive) {
        fargolChops++;
      }
      if (!fargolFlameActive && fargolChops > 0 && fargolChops % 100 === 0) {
        fargolFlameActive = true;
        fargolFlameStartTime = +new Date;
        if (typeof sa !== 'undefined' && tex_fargol_flame) {
          sa.texture = tex_fargol_flame;
          sa.width = 94;
          sa.height = 142;
        }
        if (typeof ta !== 'undefined' && tex_fargol_flame) {
          ta.texture = tex_fargol_flame;
          ta.width = 94;
          ta.height = 142;
        }
        // spawnCombatPopup removed
        triggerTelegramHaptic('heavy');
      } else {
        triggerTelegramHaptic(fargolFlameActive ? 'heavy' : 'light');
      }
    } else if (selectedCharacter === 'ali') {
      if (!aliFlurryActive) {
        aliChops++;
        if (aliChops > 0 && aliChops % 50 === 0) {
          triggerAliFlurry();
        } else {
          triggerTelegramHaptic('light');
          updateCharacterHUD('ali', 'normal', ((aliChops % 50) / 50) * 100, (aliChops % 50) + '/50', false);
        }
      }
    } else if (selectedCharacter === 'amirhossein') {
      ca++;
      ca % 20 || (Ha++, nb());
      Fa();
      //
      triggerTelegramHaptic('medium');
    } else if (selectedCharacter === 'parsa') {
      triggerTelegramHaptic('light');
    } else if (selectedCharacter === 'ahmad') {
      ahmadChops++;
      if (ahmadChops > 0 && ahmadChops % 100 === 0) {
        ahmadShieldCount++;
        ahmadShieldActive = true;
        if (ahmadShieldCount > 1) {
          spawnCombatPopup('🛡️ سپر جدید اضافه شد! (' + ahmadShieldCount + ' سپر) 🛡️', 'crit');
        } else {
          spawnCombatPopup('🛡️ سپر احمد فعال شد! 🛡️', 'crit');
        }
        triggerTelegramHaptic('heavy');
        updateCharacterHUD('ahmad', 'shield', 0, '0/100', true);
      } else {
        triggerTelegramHaptic('light');
        var ahmProg = ahmadChops % 100;
        updateCharacterHUD('ahmad', ahmadShieldCount > 0 ? 'shield' : 'normal', ahmProg, ahmProg + '/100', ahmadShieldCount > 0);
      }
    } else if (selectedCharacter === 'erfan') {
      var curStaminaRatio = (ba - +new Date) / qa;
      if (curStaminaRatio < 0.5) {
        ca += 2;
        ca % 20 || (Ha++, nb());
        Fa();
        spawnCombatPopup('3X', 'erfan-crit');
        triggerTelegramHaptic('heavy');
      } else {
        triggerTelegramHaptic('light');
      }
    } else if (selectedCharacter === 'fateme') {
      triggerTelegramHaptic('light');
    } else {
      triggerTelegramHaptic(isRejuvenated ? 'medium' : 'light');
    }
    _syncShadowScore();
    wa(a,!0,2==Math.abs(b))'''
)

# 10. In Va() (death / lethal hit):
parsa_sacrifice_func = '''function playParsaSacrificeAnimation(playerSide, onComplete) {
  fargolSacrificeInProgress = true;
  ba = +new Date + qa;
  if (typeof Ua === 'function') Ua();

  var parsaLeap = new b.Sprite(tex_parsa_jump || tex_parsa_body);
  parsaLeap.anchor.set(0.5, 0.5);
  parsaLeap.width = 135;
  parsaLeap.height = 140;
  parsaLeap.visible = true;

  // If Fargol is on left (playerSide === true): Parsa leaps from right offscreen to left
  // If Fargol is on right (playerSide === false): Parsa leaps from left offscreen to right
  var startX = playerSide ? (d + 75) : -75;
  var targetX = d / 2 + (playerSide ? -28 : 28);
  var startY = f - 45;
  var targetY = f - 135; // intercept point at branch height

  parsaLeap.x = startX;
  parsaLeap.y = startY;

  // parsa_jump points right, so if leaping to left (playerSide === true), flip horizontally:
  parsaLeap.scale.x = playerSide ? -Math.abs(parsaLeap.scale.x) : Math.abs(parsaLeap.scale.x);

  k.addChild(parsaLeap);

  // Golden heroic motion aura
  var auraGlow = new b.Graphics();
  auraGlow.beginFill(0xF39C12, 0.4);
  auraGlow.drawCircle(0, 0, 48);
  auraGlow.endFill();
  k.addChild(auraGlow);

  var startTime = +new Date();
  var leapDuration = 420;
  var totalDuration = 880;
  var hasImpacted = false;

  function stepAnim() {
    var elapsed = +new Date() - startTime;
    ba = +new Date + qa;
    if (typeof Ua === 'function') Ua();

    if (elapsed < leapDuration) {
      var t = elapsed / leapDuration;
      var curX = startX + (targetX - startX) * t;
      var arcY = -125 * Math.sin(t * Math.PI);
      var curY = startY + (targetY - startY) * t + arcY;

      parsaLeap.x = curX;
      parsaLeap.y = curY;
      auraGlow.x = curX;
      auraGlow.y = curY;
      parsaLeap.rotation = (playerSide ? -1 : 1) * (0.35 - t * 0.45);

      requestAnimationFrame(stepAnim);
    } else if (elapsed < totalDuration) {
      if (!hasImpacted) {
        hasImpacted = true;
        // INTERCEPT: Shatter lethal branch!
        if (da && da.length > 0) {
          var b_hit = da[0];
          if (b_hit && playerSide === (0 > b_hit)) {
            if (Math.abs(b_hit) === 1) {
              $a(playerSide, !0);
            }
            if (da.length > 0 && Math.abs(da[0]) === 2 && playerSide === (0 > da[0])) {
              $a(playerSide);
              ca++;
              ca % 20 || (Ha++, nb());
              Fa();
            } else if (da.length > 0 && playerSide === (0 > da[0])) {
              $a(playerSide);
              ca++;
              ca % 20 || (Ha++, nb());
              Fa();
            }
          }
        }
        // Extra fail-safe cleanup: remove any branch sprite in container u that is at or below player height on playerSide
        if (typeof u !== 'undefined' && u && u.children && u.children.length > 0) {
          for (var i = u.children.length - 1; i >= 0; i--) {
            var br = u.children[i];
            var brY = u.y + br.y;
            if (brY >= (f - 145) && ((br.scale.x < 0) === playerSide)) {
              u.removeChild(br);
            }
          }
        }
        Ea("hit2");
        triggerTelegramHaptic('heavy');
        if (auraGlow.parent) k.removeChild(auraGlow);

        // Flash shockwave
        var flash = new b.Graphics();
        flash.beginFill(0xFFFFFF, 0.85);
        flash.drawCircle(targetX, targetY, 65);
        flash.endFill();
        k.addChild(flash);
        setTimeout(function() {
          if (flash.parent) k.removeChild(flash);
        }, 90);

        // Switch Parsa to defeat pose with dizzy stars and X eyes as he absorbs the blow
        if (tex_parsa_died) parsaLeap.texture = tex_parsa_died;
        parsaLeap.width = 95;
        parsaLeap.height = 111;
      }

      var t2 = (elapsed - leapDuration) / (totalDuration - leapDuration);
      parsaLeap.x = targetX + (playerSide ? 45 : -45) * t2;
      parsaLeap.y = targetY + (f - targetY + 60) * (t2 * t2);
      parsaLeap.rotation += (playerSide ? 0.08 : -0.08);
      parsaLeap.alpha = Math.max(0, 1 - t2 * 1.25);

      requestAnimationFrame(stepAnim);
    } else {
      if (parsaLeap.parent) k.removeChild(parsaLeap);
      if (auraGlow.parent) k.removeChild(auraGlow);
      fargolSacrificeInProgress = false;
      ba = +new Date + qa;
      spawnCombatPopup('🛡️ فداکاری پارسا! جان دوباره سلطان! 🛡️', 'crit small-popup');
      if (typeof onComplete === 'function') onComplete();
    }
  }

  requestAnimationFrame(stepAnim);
}
'''
va_pattern = r'function Va\(\)\s*\{'
match_va = re.search(va_pattern, code)
if match_va:
    code = code[:match_va.start()] + parsa_sacrifice_func + code[match_va.start():]
    match_va = re.search(va_pattern, code)
    va_injection = '''
  if (typeof aliFlurryTimer !== 'undefined' && aliFlurryTimer) {
    clearInterval(aliFlurryTimer);
    aliFlurryTimer = null;
  }
  aliFlurryActive = false;
  aliFlurryRemaining = 0;
  parsaSleeping = false;
  parsaWaitingForChop = false;
  if (typeof parsaSleepTimer !== 'undefined' && parsaSleepTimer) {
    clearTimeout(parsaSleepTimer);
    parsaSleepTimer = null;
  }
  if (typeof sa !== 'undefined') sa.x = 0;

  if (selectedCharacter === 'fargol' && fargolSacrificeAvailable) {
    // SACRIFICE: Parsa leaps in to save Fargol!
    fargolSacrificeAvailable = false;
    ba = +new Date + qa; // Restore full stamina
    aa = true;
    za = true;
    updateCharacterHUD('fargol', fargolFlameActive ? 'flame' : 'normal', fargolChops % 100, (fargolChops % 100) + '/100', false);
    playParsaSacrificeAnimation(m);
    return; // Death avoided!
  }

  if (selectedCharacter === 'ahmad' && ahmadShieldCount > 0) {
    ahmadShieldCount--;
    ahmadShieldActive = ahmadShieldCount > 0;
    ba = +new Date + qa; // Restore full stamina
    aa = true;
    za = true;
    // Shatter lethal branch if currently colliding
    if (da && da.length > 0) {
      var b_hit = da[0];
      if (b_hit && m === (0 > b_hit)) {
        if (Math.abs(b_hit) === 1) {
          $a(m, !0);
        }
        if (da.length > 0 && Math.abs(da[0]) === 2 && m === (0 > da[0])) {
          $a(m);
          ca++;
          ca % 20 || (Ha++, nb());
          Fa();
        } else if (da.length > 0 && m === (0 > da[0])) {
          $a(m);
          ca++;
          ca % 20 || (Ha++, nb());
          Fa();
        }
      }
    }
    // Fail-safe branch cleanup for Ahmad
    if (typeof u !== 'undefined' && u && u.children && u.children.length > 0) {
      for (var i = u.children.length - 1; i >= 0; i--) {
        var br = u.children[i];
        var brY = u.y + br.y;
        if (brY >= (f - 145) && ((br.scale.x < 0) === m)) {
          u.removeChild(br);
        }
      }
    }
    Ea("hit2");
    if (ahmadShieldCount > 0) {
      spawnCombatPopup('🛡️ سپر از احمد محافظت کرد! (' + ahmadShieldCount + ' باقی‌مانده) 🛡️', 'crit');
    } else {
      spawnCombatPopup('🛡️ آخرین سپر از احمد محافظت کرد! 🛡️', 'crit');
    }
    triggerTelegramHaptic('heavy');
    var curChops = ahmadChops % 100;
    updateCharacterHUD('ahmad', ahmadShieldCount > 0 ? 'shield' : 'normal', curChops, curChops + '/100', ahmadShieldCount > 0);
    return; // Death avoided!
  }

  var curDeathTex = (selectedCharacter === 'fateme' ? tex_fateme_died : (selectedCharacter === 'fargol' ? tex_fargol_died : (selectedCharacter === 'ali' ? tex_ali_died : (selectedCharacter === 'amirhossein' ? tex_amirhossein_died : (selectedCharacter === 'parsa' ? tex_parsa_died : (selectedCharacter === 'ahmad' ? tex_ahmad_died : (selectedCharacter === 'erfan' ? tex_erfan_died : (nimaPhase === 'young' ? tex_nima_died_young : tex_nima_died_old))))))));
  if (typeof w !== 'undefined' && curDeathTex) w.texture = curDeathTex;
  if (typeof x !== 'undefined' && curDeathTex) x.texture = curDeathTex;
  updateCharacterHUD(selectedCharacter, 'hide');
  triggerTelegramHaptic('heavy');
'''
    code = code[:match_va.end()] + va_injection + code[match_va.end():]

# 11. In wa() (positioning & sprite switching):
code = code.replace(
    'w.visible=!0,y.visible=!1,x.visible=!0,B.visible=!1',
    'w.visible=!0,y.visible=!1,x.visible=!0,B.visible=!1,w.texture=((selectedCharacter==="fateme"?tex_fateme_died:(selectedCharacter==="fargol"?tex_fargol_died:(selectedCharacter==="ali"?tex_ali_died:(selectedCharacter==="amirhossein"?tex_amirhossein_died:(selectedCharacter==="parsa"?tex_parsa_died:(selectedCharacter==="ahmad"?tex_ahmad_died:(selectedCharacter==="erfan"?tex_erfan_died:(nimaPhase==="young"?tex_nima_died_young:tex_nima_died_old))))))))||w.texture),x.texture=((selectedCharacter==="fateme"?tex_fateme_died:(selectedCharacter==="fargol"?tex_fargol_died:(selectedCharacter==="ali"?tex_ali_died:(selectedCharacter==="amirhossein"?tex_amirhossein_died:(selectedCharacter==="parsa"?tex_parsa_died:(selectedCharacter==="ahmad"?tex_ahmad_died:(selectedCharacter==="erfan"?tex_erfan_died:(nimaPhase==="young"?tex_nima_died_young:tex_nima_died_old))))))))||x.texture),w.width=95,w.height=111,x.width=95,x.height=111'
)
code = code.replace(
    'w.visible=!1,y.visible=!0,x.visible=!1,B.visible=!0',
    'w.visible=!1,y.visible=!0,x.visible=!1,B.visible=!0,typeof I!=="undefined"&&(I.visible=!1),typeof H!=="undefined"&&(H.visible=!1),typeof S!=="undefined"&&(S.visible=!1),typeof sa!=="undefined"&&(sa.x=0)'
)

# 11b. In mb(a) (chopping swing & strike):
mb_pattern = r'function mb\(a\)\{H\.visible=!0;I\.visible=!1;setTimeout\(function\(\)\{H\.visible=\s*!1;I\.visible=!0\},50\);a\?Ea\("hit2"\):Ea\("hit1"\)\}'
mb_replacement = '''function mb(a){
  if (selectedCharacter === 'fargol') {
    if (typeof sa !== 'undefined') {
      if (fargolFlameActive && tex_fargol_flame_swing) {
        sa.texture = tex_fargol_flame_swing;
      } else if (!fargolFlameActive && tex_fargol_swing) {
        sa.texture = tex_fargol_swing;
      }
      sa.x = -14;
      sa.width = 120;
      sa.height = 140;
      setTimeout(function(){ 
        if (typeof sa !== 'undefined') {
          sa.x = 0;
          if (fargolFlameActive && tex_fargol_flame) {
            sa.texture = tex_fargol_flame;
          } else if (!fargolFlameActive && tex_fargol_normal) {
            sa.texture = tex_fargol_normal;
          }
          sa.width = 94; 
          sa.height = 140;
        }
      }, 65);
    }
  } else if (selectedCharacter === 'ali') {
    if (typeof sa !== 'undefined') {
      if (tex_ali_swing) {
        sa.texture = tex_ali_swing;
        sa.x = -34;
        sa.width = 115;
        sa.height = 140;
      }
      setTimeout(function(){
        if (typeof sa !== 'undefined' && aa) {
          sa.x = 0;
          if (tex_ali_body) sa.texture = tex_ali_body;
          sa.width = 68;
          sa.height = 140;
        }
      }, 75);
    }
  } else if (selectedCharacter === 'amirhossein') {
    if (typeof sa !== 'undefined') {
      if (tex_amirhossein_swing) {
        sa.texture = tex_amirhossein_swing;
        sa.x = -34;
        sa.width = 115;
        sa.height = 140;
      }
      setTimeout(function(){
        if (typeof sa !== 'undefined' && aa) {
          sa.x = 0;
          if (tex_amirhossein_body) sa.texture = tex_amirhossein_body;
          sa.width = 68;
          sa.height = 140;
        }
      }, 75);
    }
  } else if (selectedCharacter === 'parsa') {
    if (typeof sa !== 'undefined') {
      if (tex_parsa_swing) {
        sa.texture = tex_parsa_swing;
        sa.x = -14;
        sa.width = 120;
        sa.height = 140;
      }
      setTimeout(function(){
        if (typeof sa !== 'undefined' && aa) {
          sa.x = 0;
          if (tex_parsa_body) sa.texture = (parsaSleeping && tex_parsa_sleep ? tex_parsa_sleep : tex_parsa_body);
          sa.width = 94;
          sa.height = 140;
        }
      }, 75);
    }
  } else if (selectedCharacter === 'ahmad') {
    if (typeof sa !== 'undefined') {
      if (tex_ahmad_swing) {
        sa.texture = tex_ahmad_swing;
        sa.x = -14;
        sa.width = 120;
        sa.height = 140;
      }
      setTimeout(function(){
        if (typeof sa !== 'undefined' && aa) {
          sa.x = 0;
          if (tex_ahmad_body) sa.texture = tex_ahmad_body;
          sa.width = 94;
          sa.height = 140;
        }
      }, 75);
    }
  } else if (selectedCharacter === 'erfan') {
    if (typeof sa !== 'undefined') {
      if (tex_erfan_swing) {
        sa.texture = tex_erfan_swing;
        sa.x = -34;
        sa.width = 115;
        sa.height = 140;
      }
      setTimeout(function(){
        if (typeof sa !== 'undefined' && aa) {
          sa.x = 0;
          if (tex_erfan_body) sa.texture = tex_erfan_body;
          sa.width = 68;
          sa.height = 140;
        }
      }, 75);
    }
  } else if (selectedCharacter === 'fateme') {
    if (typeof sa !== 'undefined') {
      if (tex_fateme_swing) {
        sa.texture = tex_fateme_swing;
        sa.x = -34;
        sa.width = 115;
        sa.height = 140;
      }
      setTimeout(function(){
        if (typeof sa !== 'undefined' && aa) {
          sa.x = 0;
          if (tex_fateme_body) sa.texture = tex_fateme_body;
          sa.width = 68;
          sa.height = 140;
        }
      }, 75);
    }
  } else {
    if (typeof sa !== 'undefined') {
      var swingTex = (nimaPhase === 'young' ? tex_nima_swing_young : tex_nima_swing_old);
      if (swingTex) {
        sa.texture = swingTex;
        sa.x = -34;
        sa.width = 115;
        sa.height = 140;
      }
      setTimeout(function(){
        if (typeof sa !== 'undefined' && aa) {
          sa.x = 0;
          var idleTex = (nimaPhase === 'young' ? tex_nima_young : tex_nima_old);
          if (idleTex) sa.texture = idleTex;
          sa.width = 68;
          sa.height = 140;
        }
      }, 75);
    }
  }
  a ? Ea("hit2") : Ea("hit1");
}'''
code = re.sub(mb_pattern, mb_replacement, code)

# 12. In rb() (reset to character selection page on game over):
code = code.replace(
    'function rb(){if(!h){h=!0;V.render(C);',
    'function rb(){if(!h){h=!0;Z=!1;Ba = (function(){ try { var u = window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user; return u ? (u.first_name || u.username || "شما") : "شما"; } catch(e) { return "شما"; } })();'
)
code = code.replace(
    'ca>cb?qb():hb();Ia()}}',
    'ca>cb?qb():hb();if(typeof B!=="undefined")B.visible=!0;if(typeof x!=="undefined")x.visible=!1;if(typeof w!=="undefined")w.visible=!1;if(typeof y!=="undefined")y.visible=!1;if(typeof S!=="undefined")S.visible=!1;if(typeof I!=="undefined")I.visible=!1;if(typeof H!=="undefined")H.visible=!1;if(typeof sa!=="undefined")sa.x=0;updateCharacterHUD(selectedCharacter,"hide");selectCharacter(selectedCharacter);Ia()}}'
)

# 13. Update greet screen Ia() to refresh character selector state
code = code.replace(
    'function Ia(){',
    '''function Ia(){
  initCharacterSelector();
  if (typeof ta !== 'undefined') {
    ta.texture = (selectedCharacter === 'fateme' ? tex_fateme_body : (selectedCharacter === 'fargol' ? tex_fargol_normal : (selectedCharacter === 'ali' ? tex_ali_body : (selectedCharacter === 'amirhossein' ? tex_amirhossein_body : (selectedCharacter === 'parsa' ? tex_parsa_body : (selectedCharacter === 'ahmad' ? tex_ahmad_body : (selectedCharacter === 'erfan' ? tex_erfan_body : tex_nima_old))))))) || ta.texture;
    ta.width = ((selectedCharacter === 'fargol' || selectedCharacter === 'parsa' || selectedCharacter === 'ahmad') ? 94 : 68);
    ta.height = 140;
    if (typeof x !== 'undefined') {
      x.texture = (selectedCharacter === 'fateme' ? tex_fateme_died : (selectedCharacter === 'fargol' ? tex_fargol_died : (selectedCharacter === 'ali' ? tex_ali_died : (selectedCharacter === 'amirhossein' ? tex_amirhossein_died : (selectedCharacter === 'parsa' ? tex_parsa_died : (selectedCharacter === 'ahmad' ? tex_ahmad_died : (selectedCharacter === 'erfan' ? tex_erfan_died : tex_nima_died_old))))))) || x.texture;
      x.width = 95;
      x.height = 111;
    }
    if (typeof S !== "undefined") S.visible = false;
    if (typeof I !== "undefined") I.visible = false;
    if (typeof H !== "undefined") H.visible = false;
    V.render(C);
  }'''
)

# 14. Adjust branch height to clear 140px characters (+40px clearance):
# In pb(): initial branch generation
code = code.replace(
    'c.x=a?-10:10;c.y=-pa;',
    'c.x=a?-10:10;c.y=-pa-40;'
)
# In $a(a, c): dynamic branch generation as tree is chopped
code = code.replace(
    'e.x=d?-10:10;e.y=-pa;',
    'e.x=d?-10:10;e.y=-pa-40;'
)
# In Pa(): flying container K.y adjustment to match branch removed height
code = code.replace(
    'K.x=d/2;K.y=f-105;',
    'K.x=d/2;K.y=f-145;'
)
# In $a(a, c): keep log block ab flying from original height f-105
code = code.replace(
    'e=new b.Sprite(ab),e.x=a?25:-25,e.width=50,e.height=50,e.anchor.set(a?1:0,1),p.slide(e,e.x+(a?100:-100),-10,24)',
    'e=new b.Sprite(ab),e.x=a?25:-25,e.y=40,e.width=50,e.height=50,e.anchor.set(a?1:0,1),p.slide(e,e.x+(a?100:-100),30,24)'
)


# Intercept stamina exhaustion for Parsa's Blanket Sleep
code = code.replace(
    '0<ba-+new Date?Ua():Va()',
    '0<ba-+new Date?Ua():(selectedCharacter==="parsa"&&parsaSleepCount<2?triggerParsaNap():Va())'
)

# Rotate characters with left/right arrow keys on start / result screens:
old_keydown = 'aa?(37==a&&(Ka(La),Ca(!0)),39==a&&(Ka(jb),Ca(!1))):Z&&!h||32!=a||(Ka(La),fb())'
new_keydown = 'aa?(37==a&&(Ka(La),Ca(!0)),39==a&&(Ka(jb),Ca(!1))):(37==a?rotateCharacter(-1):(39==a?rotateCharacter(1):(Z&&!h||32!=a||(Ka(La),fb()))))'
code = code.replace(old_keydown, new_keydown)

# Anti-cheat state reset on new game:
code = code.replace(
    'ca=0;Ha=1;ra=za=!1;',
    'ca=0;_honeypot_cheated=!1;_honeypot_reason="";_syncShadowScore();_chop_count=0;_game_start_time=+new Date;_recent_chops=[];Ha=1;ra=za=!1;'
)

# Anti-cheat score submission in qb() and game-over check in rb():
old_qb = 'function qb(){R&&gb("/api/setScore",{data:R,score:ca||0},function(a){l=a.scores;bb();ya();a["new"]&&h&&(ra=!0,ma(Ja,"shown",ra))})}'
new_qb = '''function qb() {
  var isCheat = _honeypot_cheated || ((ca ^ 0x5F3759DF) !== _shadow_score);
  var elapsedSec = Math.max(1, Math.round((+new Date - (_game_start_time || +new Date)) / 1000));
  var curCps = Math.round((_chop_count || 1) / elapsedSec);
  // Impossible speed check removed

  var playerName = getPlayerDisplayName();
  var calloutText = '"' + playerName + '" یه متقلبه!';
  var tokenVal = isCheat ? ("FLAGGED_" + (_honeypot_reason || "honeypot")) : generateScoreToken(ca, _game_start_time, _chop_count);

  var payload = {
    data: R || "",
    score: ca || 0,
    token: tokenVal,
    cheater: isCheat ? 1 : 0,
    reason: isCheat ? _honeypot_reason : "",
    cps: curCps,
    duration: elapsedSec,
    message: calloutText
  };

  if (R || (window.KHANQAH_CONFIG && window.KHANQAH_CONFIG.reportUrl)) {
    var targetUrl = (window.KHANQAH_CONFIG && window.KHANQAH_CONFIG.reportUrl) || "/api/setScore";
    gb(targetUrl, payload, function(a) {
      if (a && a.scores) {
        l = a.scores;
        bb();
        ya();
        a["new"] && h && (ra = !0, ma(Ja, "shown", ra));
      }
    });
  }

  if (isCheat) {
    console.warn("Cheater detected. Payload flagged. Backend should dispatch message.");
  }
}'''
code = code.replace(old_qb, new_qb)

code = code.replace('ca>cb?qb():hb()', '(_honeypot_cheated||ca>cb)?qb():hb()')

old_listeners = 'N(La,Ma,function(){Z||Da.sound.play("hit1",{volume:0});!Z||h?fb():Ca(!0)});N(jb,\nMa,function(){aa&&Ca(!1)});'
new_listeners = 'N(La,Ma,function(e){Z||Da.sound.play("hit1",{volume:0});!Z||h?fb():Ca(!0,e)});N(jb,\nMa,function(e){aa&&Ca(!1,e)});'
code = code.replace(old_listeners, new_listeners)


with open('public/js/main.js', 'w', encoding='utf-8') as f:
    f.write(code)

print('Successfully patched public/js/main.js - Option B character scaling and branch clearance applied!')
