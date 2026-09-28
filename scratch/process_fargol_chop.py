from PIL import Image, ImageOps
from collections import deque

def extract_character(img_path, out_path, bg_color=(144, 144, 144), color_thresh=25):
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    pixels = img.load()
    
    # We will identify background pixels using BFS flood fill from all 4 borders
    visited = [[False]*h for _ in range(w)]
    queue = deque()
    
    def is_bg(x, y):
        r, g, b, a = pixels[x, y]
        # Check if close to grey
        diff = max(abs(r - bg_color[0]), abs(g - bg_color[1]), abs(b - bg_color[2]))
        # Also check saturation / difference between channels
        chan_diff = max(abs(r - g), abs(g - b), abs(r - b))
        return diff < color_thresh and chan_diff < 15

    # Push all borders
    for x in range(w):
        if is_bg(x, 0):
            queue.append((x, 0))
            visited[x][0] = True
        if is_bg(x, h-1):
            queue.append((x, h-1))
            visited[x][h-1] = True
    for y in range(h):
        if is_bg(0, y):
            queue.append((0, y))
            visited[0][y] = True
        if is_bg(w-1, y):
            queue.append((w-1, y))
            visited[w-1][y] = True
            
    while queue:
        cx, cy = queue.popleft()
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[nx][ny]:
                if is_bg(nx, ny):
                    visited[nx][ny] = True
                    queue.append((nx, ny))
                    
    # Also find interior background pockets: any unvisited region matching is_bg
    # Let's check interior regions
    interior_queue = deque()
    for x in range(w):
        for y in range(h):
            if not visited[x][y] and is_bg(x, y):
                # Region of grey that is enclosed
                interior_visited = []
                q = deque([(x, y)])
                visited[x][y] = True
                interior_visited.append((x, y))
                while q:
                    ix, iy = q.popleft()
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        jx, jy = ix + dx, iy + dy
                        if 0 <= jx < w and 0 <= jy < h and not visited[jx][jy] and is_bg(jx, jy):
                            visited[jx][jy] = True
                            q.append((jx, jy))
                            interior_visited.append((jx, jy))
                # If this pocket is indeed background grey
                # we keep it visited (will become transparent)

    # Set transparent
    for x in range(w):
        for y in range(h):
            if visited[x][y]:
                pixels[x, y] = (0, 0, 0, 0)
                
    # Crop to non-transparent bbox
    bbox = img.getbbox()
    cropped = img.crop(bbox)
    cropped.save(out_path)
    print(f"Saved {out_path} with size {cropped.size}")
    return cropped

extract_character('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/fargol_chop_ai_1789651890428.jpg', 'scratch/chop_normal_extracted.png')
extract_character('/home/abdollahabadi/.gemini/antigravity-ide/brain/cb36b2c5-fa18-4c58-a56d-9b82392d1874/fargol_flame_chop_ai_1789651953765.jpg', 'scratch/chop_flame_extracted.png')
