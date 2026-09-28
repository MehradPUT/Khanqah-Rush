with open('scratch/patch_lumberjack.py', 'r') as f:
    content = f.read()

new_ba_assignment = 'Ba = (function(){ try { var u = window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user; return u ? (u.first_name || u.username || "شما") : "شما"; } catch(e) { return "شما"; } })();'

content = content.replace(
    'Ba = selectedCharacter;',
    new_ba_assignment
)

with open('scratch/patch_lumberjack.py', 'w') as f:
    f.write(content)
print("Updated leaderboard name logic.")
