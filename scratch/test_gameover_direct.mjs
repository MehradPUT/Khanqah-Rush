import { writeFileSync } from 'fs';

async function run() {
  const res = await fetch('http://127.0.0.1:9222/json/list');
  const tabs = await res.json();
  let tab = tabs.find(t => t.type === 'page');

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

  console.log('Triggering death via Va()...');
  await send('Runtime.evaluate', {
    expression: `
      // Check if Va is accessible or trigger via timeout / error
      window.dispatchEvent(new KeyboardEvent('keydown', { keyCode: 37 })); // chop left
    `
  });
  await new Promise(r => setTimeout(r, 400));

  // Now trigger death by setting ba = 0 or calling Va
  await send('Runtime.evaluate', {
    expression: `
      // Trigger death by running out of time
      ba = -1000;
    `
  });

  await new Promise(r => setTimeout(r, 200));

  console.log('Capturing in-game death...');
  const s1 = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/gameover_actual_died.png', Buffer.from(s1.data, 'base64'));
  console.log('Saved gameover_actual_died.png');

  // Wait for result screen
  await new Promise(r => setTimeout(r, 1200));
  console.log('Capturing result screen...');
  const s2 = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/result_screen_actual.png', Buffer.from(s2.data, 'base64'));
  console.log('Saved result_screen_actual.png');

  ws.close();
}

run().catch(console.error);
