from PIL import Image, ImageDraw

def draw_refined_beard(draw):
    # Flowing natural white beard matching pixel art
    # Jawline connection: (36, 42) to (64, 42)
    
    # 1. Base shadow / contour
    points_outer = [
        (37, 42), (35, 50), (34, 62), (36, 76), (40, 88), (46, 98), 
        (50, 104), # tip of beard
        (54, 98), (60, 88), (64, 76), (66, 62), (65, 50), (63, 42)
    ]
    draw.polygon(points_outer, fill=(225, 230, 235, 255), outline=(170, 178, 185, 255))
    
    # 2. Main white body
    points_inner = [
        (38, 43), (36, 51), (35, 62), (37, 75), (41, 87), 
        (50, 101), 
        (59, 87), (63, 75), (65, 62), (64, 51), (62, 43)
    ]
    draw.polygon(points_inner, fill=(255, 255, 255, 255))
    
    # 3. Soft shading lines for strands
    shadow_lines = [
        [(38, 46), (37, 60), (39, 75), (44, 88)],
        [(42, 45), (41, 60), (43, 74), (47, 92)],
        [(47, 44), (46, 62), (47, 78), (49, 98)],
        [(53, 44), (54, 62), (53, 78), (51, 98)],
        [(58, 45), (59, 60), (57, 74), (53, 92)],
        [(62, 46), (63, 60), (61, 75), (56, 88)]
    ]
    for line in shadow_lines:
        draw.line(line, fill=(205, 212, 220, 255), width=1)

    # 4. Highlight lines (bright pure white)
    highlight_lines = [
        [(40, 48), (39, 64), (41, 78)],
        [(45, 46), (44, 66), (45, 84)],
        [(50, 46), (50, 68), (50, 92)],
        [(55, 46), (56, 66), (55, 84)],
        [(60, 48), (61, 64), (59, 78)]
    ]
    for line in highlight_lines:
        draw.line(line, fill=(255, 255, 255, 255), width=1)

    # 5. Natural pixel-curved white mustache
    # Dip in center (x=50, y=38), wings spread to (36, 40) and (64, 40)
    mustache_points = [
        (48, 38), (43, 37), (37, 39), (36, 42), (42, 42), (48, 40),
        (50, 41),
        (52, 40), (58, 42), (64, 42), (63, 39), (57, 37), (52, 38)
    ]
    draw.polygon(mustache_points, fill=(255, 255, 255, 255), outline=(195, 202, 210, 255))
    draw.line([(38, 40), (49, 39)], fill=(230, 235, 240, 255), width=1)
    draw.line([(51, 39), (62, 40)], fill=(230, 235, 240, 255), width=1)

