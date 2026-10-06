# Khanqah Rush

[![Vite](https://img.shields.io/badge/Vite-5.2-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![PixiJS](https://img.shields.io/badge/PixiJS-v4.0.2-E72264?logo=pixijs&logoColor=white)](https://pixijs.com/)
[![Telegram Mini App](https://img.shields.io/badge/Telegram-Mini_App-26A5E4?logo=telegram&logoColor=white)](https://core.telegram.org/bots/webapps)
[![License: Private](https://img.shields.io/badge/License-Proprietary-yellow.svg)](#)

> **Khanqah Rush** is an arcade woodchopping game built for the **Telegram Mini Apps (TMA)** ecosystem and modern mobile/desktop web browsers. Inspired by classic arcade mechanics, it combines Persian Khanqah aesthetics, an 8-hero roster with unique abilities, arcade combat popups, Telegram haptic feedback, and anti-cheat protection.

---

## 🎮 Gameplay Overview

Chop the sacred tree as fast as possible while dodging incoming branches from the left and right. Stamina continuously drains—keep up the chopping rhythm to survive, trigger character-specific abilities, climb the leaderboard, and unlock high scores!

### Controls
* **Mobile / Touch**: Tap the left or right half of the screen to chop from that side.
* **Keyboard**: Use `Arrow Left (◀)` and `Arrow Right (▶)`, `A` / `D`, or vim-style `H` / `L` — in game and in the character menu.
* **Mouse**: Click on-screen directional buttons or canvas zones.

---

## 🛡️ Playable Hero Roster

Every character in Khanqah Rush features visual states (idle, swinging, defeated, ability triggers) and mechanics:

| Character | Title / Specialization | Unique Mechanics & Abilities |
| :--- | :--- | :--- |
| **Nima (نیما)** | Master Woodcutter *(پیر و جوان)* | **Awakened Youth (جوانی)**: Chaining rapid cuts fills his focus gauge, temporarily transforming him into Young Nima with unlimited stamina and blazing cut speed. |
| **Fargol (فرگل)** | Pyro Woodchopper *(شعله‌ور)* | **Flame Stance & Phoenix Rebirth**: Channels fiery swings and possesses a one-time self-sacrifice / phoenix resurrection ability upon fatal hits. |
| **Ahmad (احمد)** | Iron Shield *(سپر پولادین)* | **Stacking Steel Shield**: Every 100 successful chops grants a stacking protective shield that absorbs lethal branch collisions or fatigue exhaustion. |
| **Erfan (عرفان)** | Critical Striker *(ضربه مهلک)* | **Precision Crits**: High-multiplier critical chops with arcade floating text popups (`erfan-crit`). |
| **Ali (علی)** | Agile Lumberjack *(دفاع و فرار)* | **Dodge & Parry**: Rapid defensive positioning and branch clearance reflexes. |
| **Amirhossein (امیرحسین)** | Swift Chopper *(ریتم سریع)* | **Cadence Multiplier**: High combo multipliers when maintaining a consistent, rapid chopping tempo. |
| **Parsa (پارسا)** | Sloth Lumberjack *(خواب و جهش)* | **Sleep Recovery & Leap**: Enters a 3-second power nap to recover full stamina, combined with high-risk branch leaps. |
| **Fateme (فاطمه)** | Precision Artisan *(تبر طلایی)* | **Streak Mastery**: Precision bonus multiplier that scales exponentially with uninterrupted clean cuts. |

---

## 📐 Project Rules & Audio Policy

As defined in [`PROJECT_RULES.md`](PROJECT_RULES.md):

* **Strict Sound Effects Policy**: Only native, core woodchopping sound effects (`hit1`, `hit2`, `hit3`) are permitted.
* **No Character Voice Synthesizers**: Speech synthesis, TTS, and custom voice audio engines for playable characters are strictly prohibited.
* **100% Visual & Haptic Feedback**: Character states and abilities are expressed exclusively through:
  * Floating arcade combat popups (`spawnCombatPopup`)
  * Top-left HUD ability gauges & indicators
  * Multi-frame character sprites (swinging, idle, defeated, jump, sleep)
  * Native Telegram haptic feedback pulses (`Telegram.WebApp.HapticFeedback`)

---

## 🔒 Built-in Anti-Cheat System

Khanqah Rush includes client-side honeypot traps and behavioral validation:

1. **Honeypot Bait**: Global console bait variables (`window.score`, `window.setScore`, `window.Lumberjack.setScore`) that trap unauthorized console manipulation.
2. **CPS & Duration Verification**: Validates clicks-per-second (CPS) against human physical limits and verifies elapsed game duration.
3. **Cryptographic Score Tokens**: Scores submitted to backend endpoints require validation tokens generated from in-game chopping timestamps.
4. **Cheater Callout System**: Automatically detects illicit score tampering and dispatches alert payloads (`"<Player>" یه متقلبه!`).

---

## 📁 Repository Structure

```
Khanqah-Rush/
├── index.html              # Main HTML5 entry point with Telegram Mini App viewport
├── package.json            # Project scripts and dependencies
├── vite.config.js          # Vite dev server and build configuration
├── PROJECT_RULES.md        # Architectural constraints and audio policy
├── .gitignore              # Git ignore rules (node_modules, caches, env, OS files)
│
├── public/                 # Static assets served at root
│   ├── css/
│   │   └── main.min.css    # Minified game styling & responsive layouts
│   ├── fonts/
│   │   ├── CharterBT.ttf
│   │   └── CharterBT-Bold.ttf
│   ├── images/             # Active gameplay, hero spritesheets & UI icons
│   │   ├── ahmad_*.png
│   │   ├── ali_*.png
│   │   ├── amirhossein_*.png
│   │   ├── erfan_*.png
│   │   ├── fargol_*.png
│   │   ├── fateme_*.png
│   │   ├── nima_*.png
│   │   ├── parsa_*.png
│   │   └── [play|refresh|left|right].png
│   ├── js/
│   │   └── main.js         # PixiJS WebGL engine, game logic, anti-cheat & HUD
│   └── sounds/
│       ├── hit1.mp3        # Core chopping audio
│       ├── hit2.mp3
│       └── hit3.mp3
│
└── dist/                   # Production-ready static distribution bundle
    ├── index.html
    ├── css/
    ├── fonts/
    ├── images/
    ├── js/
    └── sounds/
```

---

## 🚀 Getting Started

### Prerequisites
* [Node.js](https://nodejs.org/) (v18.0.0 or higher recommended)
* npm (v9.0.0 or higher)

### Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/awmiram/Khanqah-Rush.git
cd Khanqah-Rush
npm install
```

### Development Server
Run the local Vite development server:
```bash
npm run dev
```
Open your browser at `http://localhost:5173`.

### Production Build
To create an optimized production build:
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

---

## 📱 Telegram Mini App Deployment

1. **Host Static Assets**: Deploy the repository root or the [`dist/`](dist/) folder to any static hosting provider (e.g., Cloudflare Pages, Vercel, GitHub Pages, or AWS S3).
2. **Register with BotFather**:
   * Open [@BotFather](https://t.me/BotFather) on Telegram.
   * Send `/newapp` or `/newgame`.
   * Link your bot and provide the deployed HTTPS URL.
3. **Launch**: Open the Mini App link inside Telegram on mobile or desktop to enjoy full haptic feedback and Telegram user integration.
