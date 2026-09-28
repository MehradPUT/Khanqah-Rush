# Project Rules & Design Constraints: Khanqah Rush

## Sound Effects Policy (Strict Requirement)
- **NO Custom Sound Effects for Characters**: Do NOT create, generate, or integrate custom sound effects, speech synthesis, voice engines, or TTS audio for any playable character (Nima, Fargol, Ali, Amirhossein, or future characters).
- **Core Game Audio Only**: Only the original, native game audio (such as woodchopping hits `hit1`, `hit2`, `hit3`) should be played.
- **Visual Feedback Only**: Characters express abilities through visual elements only:
  - Arcade floating combat popups (`spawnCombatPopup`)
  - Dynamic top-left HUD ability gauges
  - Spritesheet frames (swinging, idle, defeated)
  - Haptic feedback pulses (`Telegram.WebApp.HapticFeedback`)
