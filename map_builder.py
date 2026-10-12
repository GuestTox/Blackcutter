import pygame, json, sys, math

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Spatial Data Map Editor (Zoom, Rotation & Snapping)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 14, bold=True)

# Editor State
mode = "COLLIDER"

# World Data (Stored with dimensions, position, and rotation)
# colliders/areas format: [{"x": int, "y": int, "w": int, "h": int, "rot": float}]
colliders = []  
areas = []      
entities = []   # [{"x": int, "y": int, "entity_id": int}]

# Camera / Viewport State (Zoom & Pan)
camera_x, camera_y = 0.0, 0.0
zoom_level = 1.0
MIN_ZOOM = 0.1
MAX_ZOOM = 10.0

panning = False
pan_start_pos = (0, 0)
pan_start_cam = (0, 0)

# Tool Drawing & Rotation State
drawing = False
start_world_pos = (0, 0)
current_rect = None  # Will be handled as a dict during creation
active_entity_id = 1
current_rotation = 0.0  # in degrees
snap_increment = 15.0   # default angle snap increment in degrees

# Base Map Texture
try:
    texture = pygame.image.load("assets/levels/test01.png").convert_alpha()
except FileNotFoundError:
    texture = pygame.Surface((2000, 1500))
    texture.fill((30, 30, 40))

# Colors
COLOR_BG = (10, 10, 12)
COLOR_COLLIDER = (0, 255, 100)
COLOR_AREA = (50, 150, 255)
COLOR_ENTITY = (255, 150, 0)
COLOR_UI_BG = (20, 22, 28)
COLOR_TEXT = (220, 220, 220)

# Screen space to World space helper functions (accounting for zoom & camera translation)
def screen_to_world(pos):
    wx = (pos[0] / zoom_level) + camera_x
    wy = (pos[1] / zoom_level) + camera_y
    return (wx, wy)

def world_to_screen(pos):
    sx = (pos[0] - camera_x) * zoom_level
    sy = (pos[1] - camera_y) * zoom_level
    return (sx, sy)

def export_json():
    data = {
        "world_size": {"w": texture.get_width(), "h": texture.get_height()},
        "colliders": colliders,
        "areas": areas,
        "entities": entities
    }
    with open("arena_map.json", "w") as f:
        json.dump(data, f, indent=4)
    print("--- Spatial Data Exported ---")
    print(json.dumps(data, indent=4))

# Toolbar buttons
buttons = [
    {"mode": "COLLIDER", "rect": pygame.Rect(10, 10, 120, 30), "label": "[1] Collider"},
    {"mode": "AREA",     "rect": pygame.Rect(140, 10, 120, 30), "label": "[2] Area"},
    {"mode": "ENTITY",   "rect": pygame.Rect(270, 10, 120, 30), "label": "[3] Entity"},
    {"action": "EXPORT", "rect": pygame.Rect(410, 10, 130, 30), "label": "Export JSON"}
]

def draw_rotated_rect(surface, color, rect_data, width=0):
    """Draws a rotated rectangle given world or screen dimensions."""
    x, y, w, h = rect_data['x'], rect_data['y'], rect_data['w'], rect_data['h']
    rot = math.radians(rect_data.get('rot', 0.0))
    
    # Calculate local corners relative to the top-left origin (before rotation)
    cx, cy = w / 2.0, h / 2.0
    corners = [
        (-cx, -cy),
        (cx, -cy),
        (cx, cy),
        (-cx, cy)
    ]
    
    world_center_x = x + cx
    world_center_y = y + cy
    
    screen_center = world_to_screen((world_center_x, world_center_y))
    
    screen_corners = []
    for cx_local, cy_local in corners:
        # Rotate local point
        rx = cx_local * math.cos(rot) - cy_local * math.sin(rot)
        ry = cx_local * math.sin(rot) + cy_local * math.cos(rot)
        # Scale by zoom and translate to screen space center
        sc_x = screen_center[0] + rx * zoom_level
        sc_y = screen_center[1] + ry * zoom_level
        screen_corners.append((sc_x, sc_y))
        
    if width == 0:
        # pygame doesn't have a direct rotated polygon fill with alpha support easily without a surface,
        # but for outlines or simple fills we can draw a polygon:
        pygame.draw.polygon(surface, color, screen_corners)
    else:
        pygame.draw.polygon(surface, color, screen_corners, int(width * zoom_level) if width > 0 else 1)

running = True
while running:
    screen.fill(COLOR_BG)
    mouse_screen = pygame.mouse.get_pos()
    mouse_world = screen_to_world(mouse_screen)

    keys = pygame.key.get_pressed()
    shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
    ctrl_pressed = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- PANNING EVENTS (Middle Click [2] or Right Click [3]) ---
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (2, 3):
            panning = True
            pan_start_pos = event.pos
            pan_start_cam = (camera_x, camera_y)

        elif event.type == pygame.MOUSEBUTTONUP and event.button in (2, 3):
            panning = False

        # --- DRAWING / PLACEMENT EVENTS (Left Click [1]) ---
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            ui_clicked = False
            for btn in buttons:
                if btn["rect"].collidepoint(event.pos):
                    ui_clicked = True
                    if "mode" in btn: mode = btn["mode"]
                    elif btn.get("action") == "EXPORT": export_json()
                    break

            if not ui_clicked and event.pos[1] > 50:
                if mode in ("COLLIDER", "AREA"):
                    drawing = True
                    start_world_pos = mouse_world
                    current_rotation = 0.0
                elif mode == "ENTITY":
                    entities.append({"x": mouse_world[0], "y": mouse_world[1], "entity_id": active_entity_id})

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing and current_rect:
                rect_data = {
                    "x": current_rect["x"], 
                    "y": current_rect["y"], 
                    "w": current_rect["w"], 
                    "h": current_rect["h"],
                    "rot": current_rotation
                }
                if mode == "COLLIDER":
                    colliders.append(rect_data)
                elif mode == "AREA":
                    areas.append(rect_data)
                drawing = False
                current_rect = None

        # --- SCROLL WHEEL CONTROLS (Zoom, Rotate, Snap Increment) ---
        elif event.type == pygame.MOUSEWHEEL:
            if ctrl_pressed:
                # Ctrl + Scrollwheel: Modify Snapping Increment
                snap_increment = max(0, snap_increment + (event.y * 5.0))
            elif shift_pressed and drawing:
                # Shift + Scrollwheel: Rotate active drawing rectangle
                delta_rot = event.y * snap_increment
                current_rotation = (current_rotation + delta_rot) % 360
            else:
                # Normal Scrollwheel: Zoom into/out of mouse pointer position
                old_zoom = zoom_level
                if event.y > 0:
                    zoom_level *= 1.12
                else:
                    zoom_level /= 1.12
                zoom_level = max(MIN_ZOOM, min(MAX_ZOOM, zoom_level))
                
                # Adjust camera so zoom centers around the mouse cursor
                camera_x = mouse_screen[0] / zoom_level + camera_x - mouse_screen[0] / old_zoom
                camera_y = mouse_screen[1] / zoom_level + camera_y - mouse_screen[1] / old_zoom

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: mode = "COLLIDER"
            elif event.key == pygame.K_2: mode = "AREA"
            elif event.key == pygame.K_3: mode = "ENTITY"

            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                if mode == "ENTITY":
                    active_entity_id += 1
                else:
                    snap_increment = min(90.0, snap_increment + 5.0)
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                if mode == "ENTITY":
                    active_entity_id = max(0, active_entity_id - 1)
                else:
                    snap_increment = max(1.0, snap_increment - 5.0)

            elif event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
                export_json()
            elif event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL):
                if mode == "COLLIDER" and colliders: colliders.pop()
                elif mode == "AREA" and areas: areas.pop()
                elif mode == "ENTITY" and entities: entities.pop()

    # --- CAMERA PAN CONTROL LOGIC ---
    if panning:
        dx = mouse_screen[0] - pan_start_pos[0]
        dy = mouse_screen[1] - pan_start_pos[1]
        camera_x = pan_start_cam[0] - (dx / zoom_level)
        camera_y = pan_start_cam[1] - (dy / zoom_level)

    # WASD Camera Panning
    pan_speed = 8.0 / zoom_level
    if keys[pygame.K_a]: camera_x -= pan_speed
    if keys[pygame.K_d]: camera_x += pan_speed
    if keys[pygame.K_w]: camera_y -= pan_speed
    if keys[pygame.K_s] and not ctrl_pressed: camera_y += pan_speed

    # Update active dragging rectangle in WORLD coordinates
    if drawing:
        x = min(start_world_pos[0], mouse_world[0])
        y = min(start_world_pos[1], mouse_world[1])
        w = abs(start_world_pos[0] - mouse_world[0])
        h = abs(start_world_pos[1] - mouse_world[1])
        current_rect = {"x": x, "y": y, "w": w, "h": h}

    # --- RENDER LAYER ---
    
    # 1. Background Image scaled and translated
    scaled_texture_width = int(texture.get_width() * zoom_level)
    scaled_texture_height = int(texture.get_height() * zoom_level)
    # Optimization: only scale if needed, or blit zoomed surface
    if zoom_level == 1.0:
        scaled_texture = texture
    else:
        scaled_texture = pygame.transform.smoothscale(texture, (scaled_texture_width, scaled_texture_height))
    
    screen.blit(scaled_texture, world_to_screen((0, 0)))

    # 2. Area Zones
    for a in areas:
        draw_rotated_rect(screen, COLOR_AREA, a, width=2)

    # 3. Collider Boxes
    for c in colliders:
        draw_rotated_rect(screen, COLOR_COLLIDER, c, width=2)

    # 4. Preview Active Dragging Box
    if current_rect:
        preview_data = {**current_rect, "rot": current_rotation}
        preview_color = COLOR_COLLIDER if mode == "COLLIDER" else COLOR_AREA
        draw_rotated_rect(screen, preview_color, preview_data, width=1)

    # 5. Entity Spawn Points
    for ent in entities:
        epos = world_to_screen((ent['x'], ent['y']))
        pygame.draw.circle(screen, COLOR_ENTITY, (int(epos[0]), int(epos[1])), max(2, int(8 * zoom_level)), 2)
        pygame.draw.circle(screen, COLOR_ENTITY, (int(epos[0]), int(epos[1])), max(1, int(2 * zoom_level)))
        lbl = font.render(f"ID:{ent['entity_id']}", True, COLOR_TEXT)
        screen.blit(lbl, (epos[0] + 10, epos[1] - 10))

    # --- UI TOOLBAR LAYER (Fixed to Screen Coordinates) ---
    pygame.draw.rect(screen, COLOR_UI_BG, (0, 0, 1200, 50))
    pygame.draw.line(screen, (50, 50, 60), (0, 50), (1200, 50), 2)

    for btn in buttons:
        is_selected = btn.get("mode") == mode
        bg_col = (60, 60, 80) if is_selected else (35, 38, 48)
        border_col = COLOR_ENTITY if is_selected else (80, 80, 100)
        
        pygame.draw.rect(screen, bg_col, btn["rect"], border_radius=4)
        pygame.draw.rect(screen, border_col, btn["rect"], 2, border_radius=4)
        
        txt_surf = font.render(btn["label"], True, COLOR_TEXT)
        txt_rect = txt_surf.get_rect(center=btn["rect"].center)
        screen.blit(txt_surf, txt_rect)

    # Status Bar
    if mode == "ENTITY":
        status_msg = f"Active ID: {active_entity_id}"
    elif drawing:
        status_msg = f"Rot: {current_rotation:.1f}° | Snap: {snap_increment}°"
    else:
        status_msg = f"Snap: {snap_increment}° (Ctrl+Wheel to change)"
        
    info_surf = font.render(f"Mode: {mode} | Zoom: {zoom_level:.2f}x | {status_msg}", True, (180, 180, 180))
    screen.blit(info_surf, (550, 18))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()