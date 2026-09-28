import { writeFileSync } from 'fs';

async function run() {
  const res = await fetch('http://127.0.0.1:9222/json/list');
  const tabs = await res.json();
  const tab = tabs.find(t => t.url.includes('5173'));
  console.log('Target tab:', tab.title);

  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  let id = 1;
  const send = (method, params = {}) => new Promise(r => {
    const msgId = id++;
    const handler = (e) => {
      const d = JSON.parse(e.data);
      if (d.id === msgId) {
        ws.removeEventListener('message', handler);
        r(d.result);
      }
    };
    ws.addEventListener('message', handler);
    ws.send(JSON.stringify({id: msgId, method, params}));
  });

  await new Promise(r => ws.onopen = r);

  await send('Emulation.setDeviceMetricsOverride', {width: 430, height: 860, deviceScaleFactor: 2, mobile: true});
  await new Promise(r => setTimeout(r, 600));

  console.log('Starting game by clicking Play button (#button_left)...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_left');
      if (btn) btn.click();
    `
  });

  await new Promise(r => setTimeout(r, 800));

  // Capture Old Nima
  console.log('Chop left once...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_left');
      if (btn) btn.click();
    `
  });
  await new Promise(r => setTimeout(r, 400));
  const screen1 = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/lumberjack_nima_old.png', Buffer.from(screen1.data, 'base64'));
  console.log('Saved lumberjack_nima_old.png!');

  // Now call activateRejuvenation() directly
  console.log('Calling window.nimaGame.activateRejuvenation()...');
  await send('Runtime.evaluate', {
    expression: `
      if (window.nimaGame) {
        window.nimaGame.activateRejuvenation();
      }
    `
  });

  await new Promise(r => setTimeout(r, 500));

  const screen2 = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/lumberjack_nima_young.png', Buffer.from(screen2.data, 'base64'));
  console.log('Saved lumberjack_nima_young.png!');

  ws.close();
}

run().catch(console.error);
