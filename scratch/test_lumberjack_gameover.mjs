import { writeFileSync } from 'fs';

async function run() {
  const res = await fetch('http://127.0.0.1:9222/json/list');
  const tabs = await res.json();
  const tab = tabs.find(t => t.url.includes('5173'));

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

  // Trigger death / game over
  console.log('Triggering collision / game over...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_right');
      if (btn) {
        btn.click();
        btn.click();
      }
    `
  });

  await new Promise(r => setTimeout(r, 700));

  const screen = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/lumberjack_nima_result.png', Buffer.from(screen.data, 'base64'));
  console.log('Saved lumberjack_nima_result.png!');

  ws.close();
}

run().catch(console.error);
