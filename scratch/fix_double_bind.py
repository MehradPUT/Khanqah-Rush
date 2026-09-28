import re

with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the top of bindMobileTouch
old_func = """  function bindMobileTouch(el, action) {
    if (!el) return;
    var lastTouchTime = 0;"""

new_func = """  function bindMobileTouch(el, action) {
    if (!el || el._touchBound) return; // Prevent double-binding
    el._touchBound = true;
    var lastTouchTime = 0;"""

code = code.replace(old_func, new_func)

# Remove the inner `if (!el._touchBound)` since we moved it to the top
old_inner = """    el.ontouchstart = handleEvent;
    el.onclick = handleEvent;
    if (!el._touchBound) {
      el._touchBound = true;
      el.addEventListener('touchstart', handleEvent, { passive: false });
      el.addEventListener('click', handleEvent);
    }"""

new_inner = """    el.ontouchstart = handleEvent;
    el.onclick = handleEvent;
    el.addEventListener('touchstart', handleEvent, { passive: false });
    el.addEventListener('click', handleEvent);"""

code = code.replace(old_inner, new_inner)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Double binding fixed.")
