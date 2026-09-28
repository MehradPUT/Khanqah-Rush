with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_logic = """  if (type === 'erfan-crit') {
    var x = window.innerWidth - 60 + (Math.random() * 20 - 10);
    var y = 60 + (Math.random() * 30 - 15);
    el.style.left = x + 'px';
    el.style.top = y + 'px';"""

new_logic = """  if (type === 'erfan-crit') {
    var rightEdge = window.innerWidth;
    var canvasEl = document.querySelector('canvas');
    if (canvasEl) {
      var rect = canvasEl.getBoundingClientRect();
      rightEdge = rect.right;
    }
    var x = rightEdge - 60 + (Math.random() * 20 - 10);
    var y = 60 + (Math.random() * 30 - 15);
    el.style.left = x + 'px';
    el.style.top = y + 'px';"""

code = code.replace(old_logic, new_logic)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Position logic fixed.")
