// Reference Telegram Bot Server (Node.js) for Khanqah Rush Anti-Cheat Honeypot
// Works with telegraf, node-telegram-bot-api, or direct Express webhook

const express = require('express');
const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || "YOUR_BOT_TOKEN";
const TELEGRAM_API = `https://api.telegram.org/bot${BOT_TOKEN}`;

// Helper: send message to Telegram Chat
async function sendTelegramMessage(chatId, text) {
  try {
    const res = await fetch(`${TELEGRAM_API}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: text
      })
    });
    return await res.json();
  } catch (err) {
    console.error("Telegram API Error:", err);
  }
}

// 1. Endpoint: /api/setScore (called by game client on game over)
app.post('/api/setScore', async (req, res) => {
  const { data, score, token, cheater, message, cps, duration } = req.body;

  let userName = "کاربر";
  let chatId = null;

  // Extract Telegram Game data hash if present
  if (data) {
    try {
      const raw = Buffer.from(data, 'base64').toString('utf8');
      const gameSession = JSON.parse(raw.substr(0, raw.length - 32));
      userName = gameSession.n || userName;
      chatId = gameSession.ci || gameSession.chat_id;
    } catch (e) {}
  }

  // 1. ALWAYS return 200 OK so the cheater thinks they succeeded!
  res.json({
    scores: [{ pos: 1, score: Number(score) || 0, name: userName, current: true }],
    "new": true
  });

  // 2. If flagged as cheater (from honeypot bait or invalid token):
  const isCheater = (cheater === "1" || cheater === 1 || String(token).startsWith("FLAGGED_"));

  if (isCheater && chatId) {
    // Send the exact message requested:
    const alertText = `"${userName}" یه متقلبه!`;
    console.warn(`🚨 BUSTED: Broadcasting to chat ${chatId}: ${alertText}`);
    await sendTelegramMessage(chatId, alertText);
  }
});

// 2. Telegram Webhook handler for Telegram.WebApp.sendData
app.post('/telegram-webhook', async (req, res) => {
  const update = req.body;
  if (update?.message?.web_app_data) {
    try {
      const appData = JSON.parse(update.message.web_app_data.data);
      if (appData.type === 'cheater_alert') {
        const chatId = update.message.chat.id;
        const calloutText = appData.text || `"${appData.user || 'کاربر'}" یه متقلبه!`;
        await sendTelegramMessage(chatId, calloutText);
      }
    } catch (e) {}
  }
  res.sendStatus(200);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Khanqah Rush Score & Anti-Cheat server running on port ${PORT}`);
});
