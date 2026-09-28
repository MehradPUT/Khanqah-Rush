import { writeFileSync } from 'fs';

async function run() {
  console.log('Connecting to Chrome...');
  const res = await fetch('http://127.0.0.1:9222/json/list');
  const tabs = await res.json();
  const tab = tabs.find(t => t.url.includes('5173')) || tabs.find(t => t.type === 'page');
  if (!tab) throw new Error('No page tab found in Chrome');

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

  // Set viewport
  await send('Emulation.setDeviceMetricsOverride', {
    width: 430,
    height: 860,
    deviceScaleFactor: 2,
    mobile: true
  });

  // Navigate to local game
  console.log('Navigating to http://localhost:5173/...');
  await send('Page.navigate', { url: 'http://localhost:5173/' });
  await new Promise(r => setTimeout(r, 2000));

  // Switch to Fargol
  console.log('Selecting Fargol...');
  await send('Runtime.evaluate', {
    expression: `
      (function() {
        const btn = document.getElementById('btn_select_fargol');
        if (btn) btn.click();
      })()
    `
  });
  await new Promise(r => setTimeout(r, 800));

  // Capture start screen
  let shot = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync('scratch/swing_test_start.png', Buffer.from(shot.data, 'base64'));
  console.log('Saved scratch/swing_test_start.png');

  // Start game by clicking play button / clicking canvas
  console.log('Starting game and chopping...');
  await send('Runtime.evaluate', {
    expression: `
      (function() {
        // Start game if on greet screen
        if (typeof pb === 'function' && !aa) {
          pb();
        }
      })()
    `
  });
  await new Promise(r => setTimeout(r, 800));

  // Perform a chop and immediately capture during the swing!
  console.log('Chopping and capturing normal swing...');
  await send('Runtime.evaluate', {
    expression: `
      (function() {
        if (typeof Ca === 'function') {
          Ca(0); // chop right side
        }
      })()
    `
  });
  
  // Capture immediately (around 30ms into the swing)
  await new Promise(r => setTimeout(r, 30));
  shot = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync('scratch/swing_test_normal_chop.png', Buffer.from(shot.data, 'base64'));
  console.log('Saved scratch/swing_test_normal_chop.png');

  // Wait 120ms for swing to revert to idle
  await new Promise(r => setTimeout(r, 120));
  shot = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync('scratch/swing_test_after_chop_idle.png', Buffer.from(shot.data, 'base64'));
  console.log('Saved scratch/swing_test_after_chop_idle.png');

  // Now trigger flame mode and capture flame swing
  console.log('Activating Flame Mode & capturing flame swing...');
  await send('Runtime.evaluate', {
    expression: `
      (function() {
        fargolChops = 99;
        Ca(0); // 100th chop triggers flame mode!
      })()
    `
  });
  await new Promise(r => setTimeout(r, 400));

  // Chop during flame mode and capture flame swing!
  await send('Runtime.evaluate', {
    expression: `
      (function() {
        Ca(0); // swing with flames!
      })()
    `
  });
  await new Promise(r => setTimeout(r, 30));
  shot = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync('scratch/swing_test_flame_chop.png', Buffer.from(shot.data, 'base64'));
  console.log('Saved scratch/swing_test_flame_chop.png');

  ws.close();
  console.log('All swing tests completed successfully!');
}

run().catch(console.error);
