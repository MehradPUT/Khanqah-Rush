from PIL import Image, ImageDraw

def draw_long_white_beard(draw, chin_x, chin_y):
    # chin_x = 50 (center of sprite)
    # chin_y = 44 (where goatee starts)
    # Beard flows down to y = 92 (length ~48px)
    
    # Base shadow / shape
    points_outer = [
        (42, 44), (39, 52), (38, 64), (40, 78), (44, 90), (48, 96), 
        (50, 98), # tip of beard
        (52, 96), (56, 90), (60, 78), (62, 64), (61, 52), (58, 44)
    ]
    draw.polygon(points_outer, fill=(220, 225, 230, 255), outline=(180, 185, 190, 255))
    
    # Inner white volume
    points_inner = [
        (43, 45), (41, 53), (40, 64), (42, 76), (46, 88), 
        (50, 95), 
        (54, 88), (58, 76), (60, 64), (59, 53), (57, 45)
    ]
    draw.polygon(points_inner, fill=(255, 255, 255, 255))
    
    # Strands & texture for natural flowing hair
    # Subtle silver strand lines
    strands = [
        # Left side strands
        [(43, 48), (42, 60), (43, 74), (47, 86)],
        [(46, 46), (45, 58), (46, 72), (48, 88)],
        # Center strands
        [(50, 46), (50, 62), (50, 78), (50, 93)],
        # Right side strands
        [(54, 46), (55, 58), (54, 72), (52, 88)],
        [(57, 48), (58, 60), (57, 74), (53, 86)]
    ]
    for s in strands:
        draw.line(s, fill=(200, 205, 210, 255), width=1)
        
    # Highlights (pure white accents)
    highlights = [
        [(45, 50), (44, 65), (46, 80)],
        [(49, 48), (49, 68), (49, 85)],
        [(51, 48), (51, 68), (51, 85)],
        [(55, 50), (56, 65), (54, 80)]
    ]
    for h in highlights:
        draw.line(h, fill=(255, 255, 255, 255), width=1)

    # White mustache covering the dark mustache
    draw.rounded_rectangle([42, 38, 58, 43], radius=2, fill=(250, 250, 255, 255), outline=(210, 215, 220, 255))
    draw.line([(43, 40), (57, 40)], fill=(255, 255, 255, 255), width=1)

print('Beard drawing function defined')
