import re

with open('scratch/patch_lumberjack.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix NodeList.forEach
old_dots_loop = """  var dots = document.querySelectorAll('.char-carousel-dot');
  dots.forEach(function(dot) {
    if (dot.getAttribute('data-char') === charId) {
      dot.classList.add('active');
      dot.style.background = charData.color;
      dot.style.boxShadow = '0 0 8px ' + charData.color;
    } else {
      dot.classList.remove('active');
      dot.style.background = 'rgba(255,255,255,0.4)';
      dot.style.boxShadow = 'none';
    }
  });"""

new_dots_loop = """  var dots = document.querySelectorAll('.char-carousel-dot');
  for (var i = 0; i < dots.length; i++) {
    var dot = dots[i];
    if (dot.getAttribute('data-char') === charId) {
      dot.classList.add('active');
      dot.style.background = charData.color;
      dot.style.boxShadow = '0 0 8px ' + charData.color;
    } else {
      dot.classList.remove('active');
      dot.style.background = 'rgba(255,255,255,0.4)';
      dot.style.boxShadow = 'none';
    }
  }"""

code = code.replace(old_dots_loop, new_dots_loop)

# Fix Array.findIndex
old_rotate = """function rotateCharacter(direction) {
  var curIdx = ALL_CHARACTERS.findIndex(function(c) { return c.id === selectedCharacter; });
  if (curIdx < 0) curIdx = 0;
  var nextIdx = (curIdx + direction + ALL_CHARACTERS.length) % ALL_CHARACTERS.length;
  selectCharacter(ALL_CHARACTERS[nextIdx].id);
}"""

new_rotate = """function rotateCharacter(direction) {
  var curIdx = -1;
  for (var i = 0; i < ALL_CHARACTERS.length; i++) {
    if (ALL_CHARACTERS[i].id === selectedCharacter) {
      curIdx = i;
      break;
    }
  }
  if (curIdx < 0) curIdx = 0;
  var nextIdx = (curIdx + direction + ALL_CHARACTERS.length) % ALL_CHARACTERS.length;
  selectCharacter(ALL_CHARACTERS[nextIdx].id);
}"""

code = code.replace(old_rotate, new_rotate)

with open('scratch/patch_lumberjack.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Browser compatibility fixed.")
