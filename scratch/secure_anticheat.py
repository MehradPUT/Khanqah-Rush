with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re

# 1. Remove the dangerous dispatchTelegramCheaterAlert function entirely
# We'll replace it with a dummy function or remove it from the code string
old_dispatch = r'''function dispatchTelegramCheaterAlert\(calloutText, playerName, score\) \{.*?\n\}\n'''
code = re.sub(old_dispatch, '', code, flags=re.DOTALL)

# Also remove the specific config object containing the token if it's explicitly injected
# But looking at the regex, I'll just rewrite the `qb` function injection to not call it.

# 2. Update the `new_qb` string in the python script to remove the dispatch call
old_qb_block = '''  if (isCheat) {
    dispatchTelegramCheaterAlert(calloutText, playerName, ca);
  }
}'''

new_qb_block = '''  if (isCheat) {
    console.warn("Cheater detected. Payload flagged. Backend should dispatch message.");
  }
}'''

code = code.replace(old_qb_block, new_qb_block)

# Remove the function definition from the script explicitly
old_dispatch_def = """function dispatchTelegramCheaterAlert(calloutText, playerName, score) {
  // 1. If in Telegram Mini App and sendData is available:
  try {
    if (window.Telegram && window.Telegram.WebApp && typeof window.Telegram.WebApp.sendData === 'function') {
      window.Telegram.WebApp.sendData(JSON.stringify({
        type: "cheater_alert",
        user: playerName,
        text: calloutText,
        score: score
      }));
    }
  } catch(e) {}

  // 2. Direct Telegram Bot API if configured:
  try {
    var cfg = window.KHANQAH_CONFIG || {
    botToken: "8685486373:AAH4cI9lZ6i3-gBBzy8rqQXc5Jpq-pfgO68"
  };
    var botToken = cfg.botToken || window.TELEGRAM_BOT_TOKEN;
    var chatId = cfg.chatId || window.TELEGRAM_CHAT_ID;

    if (!chatId && R) {
      try {
        var rawR = decodeURIComponent(escape(atob(R)));
        var parsedR = JSON.parse(rawR.substr(0, rawR.length - 32));
        chatId = parsedR.ci || parsedR.chat_id || (parsedR.chat && parsedR.chat.id);
      } catch(e) {}
    }
    if (!chatId && window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.chat) {
      chatId = window.Telegram.WebApp.initDataUnsafe.chat.id;
    }

    if (botToken && chatId) {
      fetch("https://api.telegram.org/bot" + botToken + "/sendMessage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: chatId,
          text: calloutText
        })
      }).catch(function() {});
    }
  } catch(e) {}

  try {
    console.warn("%c🚨 [HONEYPOT ALERT] Cheater flagged! Telegram Message: " + calloutText, "color: #d32f2f; font-weight: bold; font-size: 14px;");
  } catch(e) {}
}"""

code = code.replace(old_dispatch_def, "")

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Removed client-side Telegram dispatch and secured bot token.")
