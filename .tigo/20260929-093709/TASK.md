# Adopt Vazirmatn as the UI and Persian font

- STATUS: OPEN
- PRIORITY: 65
- TAGS: ui, frontend

The Vite shell currently loads Cinzel/Amiri/Outfit (see index.html font links and src/styles/game.css --font-display/--font-persian/--font-ui), while the legacy game used Vazirmatn, which renders Persian text (menus, defeat lines like عجب شاخه‌ای بود, HUD) much nicer. Switch the font stacks and index.html links to Vazirmatn (keep a sensible Latin fallback), then visually review all Persian strings in the start menu, HUD gauge, and game-over card at mobile widths.
