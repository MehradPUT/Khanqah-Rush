import { writeFileSync } from 'fs';

async function run() {
  const res = await fetch('http://127.0.0.1:9222/json/list');
  const tabs = await res.json();
  const tab = tabs.find(t => t.url.includes('5173'));
  console.log('Target tab:', tab.title, tab.url);

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

  // Set device size
  await send('Emulation.setDeviceMetricsOverride', {width: 430, height: 860, deviceScaleFactor: 2, mobile: true});
  
  // Reload page
  console.log('Reloading page...');
  await send('Page.reload');
  await new Promise(r => setTimeout(r, 1200));

  // Click Play
  console.log('Clicking play...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_left');
      if (btn) btn.click();
    `
  });
  await new Promise(r => setTimeout(r, 800));

  // Capture Old Phase screenshot (charging 'جوانی' bar on top left)
  console.log('Chop once to trigger animation and sound...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_left');
      if (btn) btn.click();
    `
  });
  await new Promise(r => setTimeout(r, 600));

  const screenOld = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/javani_bar_old.png', Buffer.from(screenOld.data, 'base64'));
  console.log('Saved javani_bar_old.png!');

  // Now trigger Young Phase
  console.log('Activating Rejuvenation (Young Phase)...');
  await send('Runtime.evaluate', {
    expression: `
      if (window.nimaGame) {
        window.nimaGame.activateRejuvenation();
      }
    `
  });
  await new Promise(r => setTimeout(r, 500));

  // Chop during young phase
  console.log('Chop once in young phase...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_left');
      if (btn) btn.click();
    `
  });
  await new Promise(r => setTimeout(r, 400));

  const screenYoung = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/javani_bar_young.png', Buffer.from(screenYoung.data, 'base64'));
  console.log('Saved javani_bar_young.png!');

  // Trigger game over by hitting branch (repeated chops on wrong side)
  console.log('Triggering game over...');
  await send('Runtime.evaluate', {
    expression: `
      for (var i = 0; i < 30; i++) {
        var btn = document.getElementById('button_right');
        if (btn) btn.click();
      }
    `
  });
  await new Promise(r => setTimeout(r, 1200));

  const screenGameOver = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/result_screen_nima.png', Buffer.from(screenGameOver.data, 'base64'));
  console.log('Saved result_screen_nima.png!');

  ws.close();
}

run().catch(console.error);
