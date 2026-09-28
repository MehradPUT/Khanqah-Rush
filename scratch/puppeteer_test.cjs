const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.toString()));

  await page.goto('file://' + __dirname + '/../public/index.html', { waitUntil: 'networkidle0' });
  
  console.log("Page loaded. Clicking 'Next' 10 times...");
  for (let i = 0; i < 10; i++) {
    await page.click('#btn_char_next');
    await page.waitForTimeout(100);
    const selectedName = await page.evaluate(() => {
      const el = document.getElementById('char_card_name');
      return el ? el.innerText : 'Unknown';
    });
    console.log(`Click ${i+1}: Selected -> ${selectedName}`);
  }

  await browser.close();
})();
