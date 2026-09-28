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

  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', {width: 430, height: 860, deviceScaleFactor: 2, mobile: true});
  
  console.log('Navigating to http://localhost:5173/ ...');
  await send('Page.navigate', { url: 'http://localhost:5173/' });
  await new Promise(r => setTimeout(r, 1500));

  // Click Play to start
  console.log('Starting game...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_left');
      if (btn) btn.click();
    `
  });
  await new Promise(r => setTimeout(r, 500));

  // Chop left and trigger a combat shout
  console.log('Chopping and spawning combat callout...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_left');
      if (btn) {
        btn.click();
        // Ensure callout triggers
        if (typeof nimaVoiceEngine !== 'undefined') {
          nimaVoiceEngine.lastChopTime = 0;
          nimaVoiceEngine.speak('old', 'chop');
        }
      }
    `
  });
  await new Promise(r => setTimeout(r, 150));

  const s1 = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/combat_popup_chop_old.png', Buffer.from(s1.data, 'base64'));
  console.log('Saved combat_popup_chop_old.png');

  // Trigger Young Frenzy
  console.log('Activating Young Frenzy...');
  await send('Runtime.evaluate', {
    expression: `
      if (window.nimaGame) window.nimaGame.activateRejuvenation();
    `
  });
  await new Promise(r => setTimeout(r, 200));

  const s2 = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/combat_popup_young_frenzy.png', Buffer.from(s2.data, 'base64'));
  console.log('Saved combat_popup_young_frenzy.png');

  // Trigger Young Chop
  console.log('Chopping in Young Frenzy...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_left');
      if (btn) {
        btn.click();
        if (typeof nimaVoiceEngine !== 'undefined') {
          nimaVoiceEngine.lastChopTime = 0;
          nimaVoiceEngine.speak('young', 'chop');
        }
      }
    `
  });
  await new Promise(r => setTimeout(r, 150));

  const s3 = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/combat_popup_young_chop.png', Buffer.from(s3.data, 'base64'));
  console.log('Saved combat_popup_young_chop.png');

  ws.close();
}

run().catch(console.error);
