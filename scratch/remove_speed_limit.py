with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Remove inhuman_cps check from ca_pre_injection
old_cps_check = """  var _elapsedSec = (_nowChop - _game_start_time) / 1000;
  if (_recent_chops.length > 14 || (_elapsedSec > 1.5 && (_chop_count / _elapsedSec) > 14)) {
    _honeypot_cheated = true;
    _honeypot_reason = 'inhuman_cps';
  }"""

new_cps_check = """  var _elapsedSec = (_nowChop - _game_start_time) / 1000;
  // Inhuman speed limit removed"""

code = code.replace(old_cps_check, new_cps_check)

# 2. Remove impossible_speed check from qb (Game Over)
old_impossible_speed = """  var curCps = Math.round((_chop_count || 1) / elapsedSec);
  if (ca > 40 && elapsedSec < 2.5) {
    isCheat = true;
    _honeypot_reason = _honeypot_reason || "impossible_speed";
  }"""

new_impossible_speed = """  var curCps = Math.round((_chop_count || 1) / elapsedSec);
  // Impossible speed check removed"""

code = code.replace(old_impossible_speed, new_impossible_speed)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Speed limits removed from script.")
