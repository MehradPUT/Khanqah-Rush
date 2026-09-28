import { writeFileSync } from 'fs';

async function run() {
  console.log('--- Connecting to Headless Chrome ---');
  const res = await fetch('http://127.0.0.1:9222/json/list');
  const tabs = await res.json();
  const tab = tabs.find(t => t.url.includes('5173'));
  if (!tab) {
    console.error('No tab found on 5173');
    process.exit(1);
  }
  console.log('Found tab:', tab.title, tab.url);

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
  
  // Reload page fresh
  console.log('1. Reloading page...');
  await send('Page.reload');
  await new Promise(r => setTimeout(r, 1200));

  // Screenshot initial start screen (Nima)
  const snap1 = await send('Page.captureScreenshot', {});
  writeFileSync('scratch/start_nima.png', Buffer.from(snap1.data, 'base64'));
  console.log('Saved scratch/start_nima.png');

  // 2. Select Fargol
  console.log('2. Selecting Fargol...');
  const selectResult = await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('btn_select_fargol');
      if (btn) btn.click();
      ({
        selected: window.khanqahGame.getCharacter(),
        btnActive: btn ? btn.classList.contains('active') : false
      });
    `,
    returnByValue: true
  });
  console.log('Character Selection Result:', selectResult.value);
  await new Promise(r => setTimeout(r, 600));

  // Screenshot start screen with Fargol selected
  const snap2 = await send('Page.captureScreenshot', {});
  writeFileSync('scratch/start_fargol.png', Buffer.from(snap2.data, 'base64'));
  console.log('Saved scratch/start_fargol.png');

  // 3. Start Game as Fargol
  console.log('3. Starting Game as Fargol...');
  await send('Runtime.evaluate', {
    expression: `
      var btn = document.getElementById('button_left');
      if (btn) btn.click();
    `
  });
  await new Promise(r => setTimeout(r, 800));

  // Check HUD
  const hudCheck1 = await send('Runtime.evaluate', {
    expression: `
      var wrap = document.getElementById('char_ability_bar_wrap');
      var name = document.getElementById('char_hud_name');
      var title = document.getElementById('char_hud_title');
      var timer = document.getElementById('char_hud_timer');
      var shield = document.getElementById('char_hud_shield');
      ({
        visible: wrap ? wrap.style.display : null,
        className: wrap ? wrap.className : null,
        name: name ? name.innerText : null,
        title: title ? title.innerText : null,
        timer: timer ? timer.innerText : null,
        shield: shield ? shield.innerText : null
      });
    `,
    returnByValue: true
  });
  console.log('In-Game Fargol HUD:', hudCheck1.value);

  // 4. Chop some logs
  console.log('4. Chopping logs...');
  for (let i = 0; i < 6; i++) {
    await send('Runtime.evaluate', {
      expression: `
        // Safe chop: determine safe side based on da[0]
        var side = true; // default left
        if (typeof da !== 'undefined' && da.length > 0) {
          var b = da[0];
          // If branch is on left (b < 0), chop from right (false).
          // If branch is on right (b > 0), chop from left (true).
          if (b < 0) side = false;
          else if (b > 0) side = true;
          else side = (typeof m !== 'undefined' ? m : true);
        }
        var btn = side ? document.getElementById('button_left') : document.getElementById('button_right');
        if (btn) btn.click();
      `
    });
    await new Promise(r => setTimeout(r, 120));
  }

  const snap3 = await send('Page.captureScreenshot', {});
  writeFileSync('scratch/fargol_gameplay_normal.png', Buffer.from(snap3.data, 'base64'));
  console.log('Saved scratch/fargol_gameplay_normal.png');

  // 5. Test Invincible Flame Mode
  console.log('5. Triggering Invincible Flame Mode...');
  await send('Runtime.evaluate', {
    expression: `
      window.khanqahGame.triggerFargolFlame();
    `
  });
  await new Promise(r => setTimeout(r, 300));

  const flameHUD = await send('Runtime.evaluate', {
    expression: `
      var wrap = document.getElementById('char_ability_bar_wrap');
      var name = document.getElementById('char_hud_name');
      var title = document.getElementById('char_hud_title');
      var timer = document.getElementById('char_hud_timer');
      ({
        isFlaming: window.khanqahGame.isFargolFlaming(),
        className: wrap ? wrap.className : null,
        name: name ? name.innerText : null,
        title: title ? title.innerText : null,
        timer: timer ? timer.innerText : null
      });
    `,
    returnByValue: true
  });
  console.log('Flame Mode HUD:', flameHUD.value);

  const snap4 = await send('Page.captureScreenshot', {});
  writeFileSync('scratch/fargol_flame_active.png', Buffer.from(snap4.data, 'base64'));
  console.log('Saved scratch/fargol_flame_active.png');

  // Test Branch Invincibility during flame: chop directly into obstacle side
  console.log('6. Testing branch invincibility during flame mode...');
  const invincibilityTest = await send('Runtime.evaluate', {
    expression: `
      // Intentionally chop into branch side if branch exists
      if (typeof da !== 'undefined' && da.length > 0) {
        var b = da[0];
        // Chop directly into branch side!
        var hazardSide = (b < 0);
        var btn = hazardSide ? document.getElementById('button_left') : document.getElementById('button_right');
        if (btn) btn.click();
      }
      ({ alive: typeof aa !== 'undefined' ? aa : null });
    `,
    returnByValue: true
  });
  console.log('Invincibility Branch Hit Result (should be alive: true):', invincibilityTest.value);

  await new Promise(r => setTimeout(r, 5200)); // wait for flame mode to expire

  // 7. Test Nima's Sacrifice / Protection Mechanic
  console.log('7. Testing Nima Sacrifice Mechanic on lethal hit...');
  const sacrificeCheckBefore = await send('Runtime.evaluate', {
    expression: `
      ({ sacrificeAvailable: window.khanqahGame.isFargolSacrificeAvailable() });
    `,
    returnByValue: true
  });
  console.log('Before hit:', sacrificeCheckBefore.value);

  // Trigger lethal hit (e.g. chop into branch or call Va())
  await send('Runtime.evaluate', {
    expression: `
      // Intentionally trigger lethal hit
      if (typeof da !== 'undefined' && da.length > 0) {
        var b = da[0];
        var hazardSide = (b < 0);
        var btn = hazardSide ? document.getElementById('button_left') : document.getElementById('button_right');
        if (btn) btn.click();
      }
    `
  });
  await new Promise(r => setTimeout(r, 400));

  const sacrificeCheckAfter = await send('Runtime.evaluate', {
    expression: `
      var shield = document.getElementById('char_hud_shield');
      ({
        alive: typeof aa !== 'undefined' ? aa : null,
        sacrificeAvailable: window.khanqahGame.isFargolSacrificeAvailable(),
        shieldText: shield ? shield.innerText : null,
        shieldClass: shield ? shield.className : null
      });
    `,
    returnByValue: true
  });
  console.log('After lethal hit (Sacrifice triggered!):', sacrificeCheckAfter.value);

  const snap5 = await send('Page.captureScreenshot', {});
  writeFileSync('scratch/fargol_sacrificed_saved.png', Buffer.from(snap5.data, 'base64'));
  console.log('Saved scratch/fargol_sacrificed_saved.png');

  // 8. Second lethal hit -> Game Over
  console.log('8. Triggering second lethal hit for Game Over...');
  await send('Runtime.evaluate', {
    expression: `
      // Chop into branch again to die
      if (typeof da !== 'undefined' && da.length > 0) {
        var b = da[0];
        var hazardSide = (b < 0);
        var btn = hazardSide ? document.getElementById('button_left') : document.getElementById('button_right');
        if (btn) btn.click();
      }
    `
  });
  await new Promise(r => setTimeout(r, 1000));

  const gameOverCheck = await send('Runtime.evaluate', {
    expression: `
      var pageWrap = document.getElementById('page_wrap');
      var scoreVal = document.getElementById('score_value');
      var table = document.getElementById('table');
      ({
        inResult: pageWrap ? pageWrap.classList.contains('in_result') : false,
        score: scoreVal ? scoreVal.innerText : null,
        leaderboard: table ? table.innerHTML.slice(0, 150) : null
      });
    `,
    returnByValue: true
  });
  console.log('Game Over Screen Check:', gameOverCheck.value);

  const snap6 = await send('Page.captureScreenshot', {});
  writeFileSync('scratch/fargol_gameover_result.png', Buffer.from(snap6.data, 'base64'));
  console.log('Saved scratch/fargol_gameover_result.png');

  ws.close();
  console.log('--- TEST FINISHED SUCCESSFULLY ---');
}

run().catch(console.error);
