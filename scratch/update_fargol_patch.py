import re

with open('scratch/patch_lumberjack.py', 'r') as f:
    code = f.read()

# Add textures
code = code.replace(
    'var tex_fargol_normal = null;',
    'var tex_fargol_normal = null;\nvar tex_fargol_swing = null;\nvar tex_fargol_flame_swing = null;'
)

code = code.replace(
    '    if (tex_fargol_normal) ta.texture = tex_fargol_normal;',
    '''    if (tex_fargol_normal) ta.texture = tex_fargol_normal;
    if (tex_fargol_swing) x.texture = tex_fargol_swing; /* dummy load */
    if (tex_fargol_flame_swing) x.texture = tex_fargol_flame_swing;'''
)

code = code.replace(
    "  tex_fargol_normal = new b.Texture(new b.BaseTexture(a.fargol_normal));",
    "  tex_fargol_normal = new b.Texture(new b.BaseTexture(a.fargol_normal));\n  tex_fargol_swing = new b.Texture(new b.BaseTexture(a.fargol_swing));\n  tex_fargol_flame_swing = new b.Texture(new b.BaseTexture(a.fargol_swing_flame));"
)

# Update width 86 -> 94
code = code.replace(
    'sa.width=(selectedCharacter==="fargol"?86:((selectedCharacter==="parsa"||selectedCharacter==="ahmad")?94:68))',
    'sa.width=((selectedCharacter==="fargol"||selectedCharacter==="parsa"||selectedCharacter==="ahmad")?94:68)'
)
code = code.replace(
    'ta.width=(selectedCharacter==="fargol"?86:((selectedCharacter==="parsa"||selectedCharacter==="ahmad")?94:68))',
    'ta.width=((selectedCharacter==="fargol"||selectedCharacter==="parsa"||selectedCharacter==="ahmad")?94:68)'
)

# Update width 86 -> 94 in reset blocks
code = code.replace('sa.width = 86;', 'sa.width = 94;')
code = code.replace('ta.width = 86;', 'ta.width = 94;')

# Update Fargol flame width 107 -> 94
code = code.replace('sa.width = 107;', 'sa.width = 94;')
code = code.replace('ta.width = 107;', 'ta.width = 94;')

# Rewrite Fargol mb() logic
old_mb = """mb_replacement = '''function mb(a){
  if (selectedCharacter === 'fargol') {
    if (typeof sa !== 'undefined') {
      sa.rotation = 0.09;
      setTimeout(function(){ if (typeof sa !== 'undefined') sa.rotation = 0; }, 65);
    }"""
new_mb = """mb_replacement = '''function mb(a){
  if (selectedCharacter === 'fargol') {
    if (typeof sa !== 'undefined') {
      if (fargolFlameActive && tex_fargol_flame_swing) {
        sa.texture = tex_fargol_flame_swing;
      } else if (!fargolFlameActive && tex_fargol_swing) {
        sa.texture = tex_fargol_swing;
      }
      sa.width = 120;
      sa.height = 140;
      setTimeout(function(){ 
        if (typeof sa !== 'undefined') {
          if (fargolFlameActive && tex_fargol_flame) {
            sa.texture = tex_fargol_flame;
          } else if (!fargolFlameActive && tex_fargol_normal) {
            sa.texture = tex_fargol_normal;
          }
          sa.width = 94; 
          sa.height = 140;
        }
      }, 65);
    }"""
code = code.replace(old_mb, new_mb)

with open('scratch/patch_lumberjack.py', 'w') as f:
    f.write(code)

print("Updated scratch/patch_lumberjack.py")
