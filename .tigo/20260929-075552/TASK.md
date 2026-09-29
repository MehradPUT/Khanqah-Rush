# Migrate index.html entry to Vite src/main.ts

- STATUS: OPEN
- PRIORITY: 90
- TAGS: migration, frontend

index.html still loads the frozen 496KB legacy bundle public/js/main.js (script src=js/main.js), while src/main.ts expects a <canvas id=gameCanvas> element that does not exist in index.html. Point the Vite entry at /src/main.ts, add the missing canvas element, and drop public/js/main.js once the Vite build covers it. This also retires the frozen honeypot code paths inside the legacy bundle. Acceptance: npm run dev serves the TS game, npm run build outputs a working dist/.
