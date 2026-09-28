from PIL import Image

normal_path = "/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/.user_uploaded/media_1790430172328.png"
flame_path = "/home/abdollahabadi/.gemini/antigravity/brain/cf64f2d7-5fbf-4ac1-a7a9-d9133b6c6a64/.user_uploaded/media_1790430178308.jpg"

norm = Image.open(normal_path).convert('RGB')
flame = Image.open(flame_path).convert('RGB')

print("Normal bg:", norm.getpixel((5,5)), norm.getpixel((norm.width-5, 5)))
print("Flame bg:", flame.getpixel((5,5)), flame.getpixel((flame.width-5, 5)))
