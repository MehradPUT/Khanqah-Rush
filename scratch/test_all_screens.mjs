import { writeFileSync } from 'fs';

async function run() {
  const res = await fetch('http://127.0.0.1:9222/json/list');
  const tabs = await res.json();
  let tab = tabs.find(t => t.type === 'page');

  if (!tab) {
    throw new Error('No page tab found!');
  }
  console.log('Target tab:', tab.title, tab.url);

  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  let id = 1;
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const msgId = id++;
    const handler = (e) => {
      const d = JSON.parse(e.data);
      if (d.id === msgId) {
        ws.removeEventListener('message', handler);
        if (d.error) reject(d.error);
        else resolve(d.result);
      }
    };
    ws.addEventListener('message', handler);
    ws.send(JSON.stringify({id: msgId, method, params}));
  });

  await new Promise(r => ws.onopen = r);

  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', {width: 430, height: 860, deviceScaleFactor: 2, mobile: true});
  
  // Navigate to fresh page
  console.log('Navigating to http://localhost:5173/ ...');
  await send('Page.navigate', { url: 'http://localhost:5173/' });
  await new Promise(r => setTimeout(r, 2000));

  // 1. Capture Start Screen
  console.log('Capturing start screen...');
  const s1 = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/start_screen_skinny.png', Buffer.from(s1.data, 'base64'));
  console.log('Saved start_screen_skinny.png');

  // 2. Click Play to start
  console.log('Clicking Play...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_left');
      if (btn) btn.click();
    `
  });
  await new Promise(r => setTimeout(r, 600));

  // Chop left once
  console.log('Chop once...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_left');
      if (btn) btn.click();
    `
  });
  await new Promise(r => setTimeout(r, 400));

  const s2 = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/gameplay_skinny_old.png', Buffer.from(s2.data, 'base64'));
  console.log('Saved gameplay_skinny_old.png');

  // 3. Rejuvenate to Young Nima
  console.log('Activating Young Nima Rejuvenation...');
  await send('Runtime.evaluate', {
    expression: `
      if (window.nimaGame) window.nimaGame.activateRejuvenation();
    `
  });
  await new Promise(r => setTimeout(r, 500));

  const s3 = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/gameplay_skinny_young.png', Buffer.from(s3.data, 'base64'));
  console.log('Saved gameplay_skinny_young.png');

  // 4. Trigger death / collision by hitting into branch
  console.log('Hitting into branch for Game Over...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_right');
      if (btn) {
        btn.click();
        btn.click();
        btn.click();
      }
    `
  });
  await new Promise(r => setTimeout(r, 300));

  const s4 = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/gameover_nima_died.png', Buffer.from(s4.data, 'base64'));
  console.log('Saved gameover_nima_died.png');

  // Wait for result screen animation to settle
  await new Promise(r => setTimeout(r, 1200));
  const s5 = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/result_screen_nima_died.png', Buffer.from(s5.data, 'base64'));
  console.log('Saved result_screen_nima_died.png');

  ws.close();
}

run().catch(console.error);
