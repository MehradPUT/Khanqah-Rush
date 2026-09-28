with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace bindMobileTouch logic
old_bind = """  function bindMobileTouch(el, action) {
    if (!el) return;
    var lastTrigger = 0;
    function handleTouchOrClick(e) {
      var now = +new Date;
      if (now - lastTrigger < 50) return;
      lastTrigger = now;
      if (e) {
        if (e.stopPropagation) e.stopPropagation();
        if (e.cancelable && e.preventDefault) e.preventDefault();
      }
      action();
    }
    el.ontouchstart = handleTouchOrClick;
    el.onclick = handleTouchOrClick;
    if (!el._touchBound) {
      el._touchBound = true;
      el.addEventListener('touchstart', handleTouchOrClick, { passive: false });
      el.addEventListener('click', handleTouchOrClick);
    }
  }"""

new_bind = """  function bindMobileTouch(el, action) {
    if (!el) return;
    var lastTouchTime = 0;
    var lastActionTime = 0;
    function handleEvent(e) {
      var now = +new Date;
      if (e && e.type === 'touchstart') {
        lastTouchTime = now;
      } else if (e && e.type === 'click') {
        // If click happens within 500ms of a touchstart, it's a ghost click. Ignore it.
        if (now - lastTouchTime < 500) return;
      }
      // Simple debounce to prevent rapid fire (PC mouse double clicks etc)
      if (now - lastActionTime < 50) return;
      lastActionTime = now;

      if (e) {
        if (e.stopPropagation) e.stopPropagation();
        if (e.cancelable && e.preventDefault) e.preventDefault();
      }
      action();
    }
    el.ontouchstart = handleEvent;
    el.onclick = handleEvent;
    if (!el._touchBound) {
      el._touchBound = true;
      el.addEventListener('touchstart', handleEvent, { passive: false });
      el.addEventListener('click', handleEvent);
    }
  }"""

code = code.replace(old_bind, new_bind)

# Replace triggerCardTap logic
old_tap = """    function triggerCardTap(e) {
      var now = +new Date;
      if (now - lastCardAction < 50) return;
      lastCardAction = now;
      if (e) {
        if (e.stopPropagation) e.stopPropagation();
        if (e.cancelable && e.preventDefault) e.preventDefault();
      }
      rotateCharacter(1);
    }"""

new_tap = """    var lastCardTouchTime = 0;
    function triggerCardTap(e) {
      var now = +new Date;
      if (e && (e.type === 'touchstart' || e.type === 'touchend')) {
        lastCardTouchTime = now;
      } else if (e && e.type === 'click') {
        if (now - lastCardTouchTime < 500) return;
      }
      
      if (now - lastCardAction < 50) return;
      lastCardAction = now;
      if (e) {
        if (e.stopPropagation) e.stopPropagation();
        if (e.cancelable && e.preventDefault) e.preventDefault();
      }
      rotateCharacter(1);
    }"""

code = code.replace(old_tap, new_tap)

# Also update the touchend listener for the card to use lastCardTouchTime
code = code.replace(
    'touchStartTime = +new Date;',
    'touchStartTime = +new Date; lastCardTouchTime = touchStartTime;'
)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated touch logic")
