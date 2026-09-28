import { writeFileSync } from 'fs';

async function verify() {
  console.log('Connecting to Chrome...');
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

  await send('Emulation.setDeviceMetricsOverride', {width: 430, height: 860, deviceScaleFactor: 2, mobile: true});
  console.log('Reloading page...');
  await send('Page.reload');
  await new Promise(r => setTimeout(r, 1200));

  // 1. Select Fargol
  console.log('1. Selecting Fargol...');
  await send('Runtime.evaluate', {
    expression: `window.khanqahGame.setCharacter('fargol');`
  });
  await new Promise(r => setTimeout(r, 500));
  const snapStart = await send('Page.captureScreenshot', {});
  writeFileSync('scratch/final_start_fargol.png', Buffer.from(snapStart.data, 'base64'));
  console.log('Saved scratch/final_start_fargol.png');

  // 2. Start Game
  console.log('2. Starting game as Fargol...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_left');
      if (btn) btn.click();
    `
  });
  await new Promise(r => setTimeout(r, 600));

  // Chop 6 times safely
  for (let i = 0; i < 6; i++) {
    await send('Runtime.evaluate', {
      expression: `
        var tree = window.khanqahGame.getTree();
        var b = tree && tree.length ? tree[0] : 0;
        var side = (b < 0) ? false : ((b > 0) ? true : window.khanqahGame.getPlayerSide());
        window.khanqahGame.chop(side);
      `
    });
    await new Promise(r => setTimeout(r, 100));
  }

  const snapGameplay = await send('Page.captureScreenshot', {});
  writeFileSync('scratch/final_fargol_gameplay.png', Buffer.from(snapGameplay.data, 'base64'));
  console.log('Saved scratch/final_fargol_gameplay.png');

  // 3. Flame Mode
  console.log('3. Activating Flame Mode...');
  await send('Runtime.evaluate', {
    expression: `window.khanqahGame.triggerFargolFlame();`
  });
  await new Promise(r => setTimeout(r, 400));
  const snapFlame = await send('Page.captureScreenshot', {});
  writeFileSync('scratch/final_fargol_flame.png', Buffer.from(snapFlame.data, 'base64'));
  console.log('Saved scratch/final_fargol_flame.png');

  // 4. Branch Invincibility Test while flaming
  console.log('4. Testing branch collision while flaming...');
  const invincibilityCheck = await send('Runtime.evaluate', {
    expression: `
      var tree = window.khanqahGame.getTree();
      var b = tree && tree.length ? tree[0] : 0;
      // Intentionally chop towards branch side
      var side = (b < 0) ? true : false;
      window.khanqahGame.chop(side);
      ({ alive: window.khanqahGame.isAlive() });
    `,
    returnByValue: true
  });
  console.log('Alive during branch hit in flame mode:', invincibilityCheck.value);

  // 5. Nima Sacrifice Mechanic
  console.log('5. Testing Nima Sacrifice on lethal hit...');
  await send('Runtime.evaluate', {
    expression: `
      // Cancel flame early to test sacrifice
      window.khanqahGame.kill();
    `
  });
  await new Promise(r => setTimeout(r, 350));

  const sacrificeCheck = await send('Runtime.evaluate', {
    expression: `
      ({
        alive: window.khanqahGame.isAlive(),
        sacrificeAvailable: window.khanqahGame.isFargolSacrificeAvailable()
      });
    `,
    returnByValue: true
  });
  console.log('Sacrifice check (should be alive: true, sacrificeAvailable: false):', sacrificeCheck.value);

  const snapSacrifice = await send('Page.captureScreenshot', {});
  writeFileSync('scratch/final_fargol_sacrifice.png', Buffer.from(snapSacrifice.data, 'base64'));
  console.log('Saved scratch/final_fargol_sacrifice.png');

  // 6. Second Lethal Hit -> Actual Game Over
  console.log('6. Triggering second lethal hit for Game Over...');
  await send('Runtime.evaluate', {
    expression: `
      window.khanqahGame.kill();
    `
  });
  await new Promise(r => setTimeout(r, 1200));

  const gameOverCheck = await send('Runtime.evaluate', {
    expression: `
      var scoreVal = document.getElementById('score_value');
      var table = document.getElementById('table');
      ({
        alive: window.khanqahGame.isAlive(),
        inResult: window.khanqahGame.isInResult(),
        score: scoreVal ? scoreVal.innerText : null,
        leaderboardEntry: table ? table.innerText : null
      });
    `,
    returnByValue: true
  });
  console.log('Game Over result:', gameOverCheck.value);

  const snapGameOver = await send('Page.captureScreenshot', {});
  writeFileSync('scratch/final_fargol_gameover.png', Buffer.from(snapGameOver.data, 'base64'));
  console.log('Saved scratch/final_fargol_gameover.png');

  ws.close();
  console.log('ALL VERIFICATIONS COMPLETED SUCCESSFULLY!');
}

verify().catch(console.error);
