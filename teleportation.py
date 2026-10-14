
import pygame
portal_1 = pygame.image.load('assets/portal1.png').convert_alpha()
portal_2 = pygame.image.load('assets/portal2.png').convert_alpha()
x = 0
y = 0
def get_solved():
    global is_solved
    return is_solved
def set_x(xer):
    global x
    x = xer
    return x
def set_y(yer):
    global y
    y = yer
    return y
def get_x():
    global x
    return x
def get_y():
    global y
    return y
def render(surface, hitbox, event, tile_size):
    global portal_2
    global portal_1
    portal_1 = pygame.transform.scale(portal_1, (tile_size, tile_size))
    portal_2 = pygame.transform.scale(portal_2, (tile_size, tile_size))
    portals = [
        {"id": "bG1", "rect": pygame.Rect(tile_size , tile_size , tile_size, tile_size), "pressed": False},
        {"id": "bG2", "rect": pygame.Rect(tile_size * 3, tile_size * 3, tile_size, tile_size), "pressed": False},

        {"id": "bA", "rect": pygame.Rect(tile_size * 2, tile_size * 5, tile_size, tile_size), "pressed": False},

        {"id": "bH2", "rect": pygame.Rect(tile_size * 3, tile_size * 8, tile_size, tile_size), "pressed": False},
        {"id": "bH1", "rect": pygame.Rect(tile_size , tile_size * 10, tile_size, tile_size), "pressed": False},

        {"id": "bI1", "rect": pygame.Rect(tile_size * 5, tile_size * 3, tile_size, tile_size), "pressed": False},
        {"id": "bI3", "rect": pygame.Rect(tile_size * 4, tile_size * 6, tile_size, tile_size), "pressed": False},
        {"id": "bI2", "rect": pygame.Rect(tile_size * 5, tile_size * 8, tile_size, tile_size), "pressed": False},

        {"id": "bB", "rect": pygame.Rect(tile_size * 8, tile_size * 2, tile_size, tile_size), "pressed": False},

        {"id": "bK1", "rect": pygame.Rect(tile_size * 7, tile_size * 4, tile_size, tile_size), "pressed": False},
        {"id": "bK2", "rect": pygame.Rect(tile_size * 8, tile_size * 7, tile_size, tile_size), "pressed": False},

        {"id": "bD", "rect": pygame.Rect(tile_size * 8, tile_size * 9, tile_size, tile_size), "pressed": False},

        {"id": "bJ1", "rect": pygame.Rect(tile_size * 10, tile_size * 3, tile_size, tile_size), "pressed": False},
        {"id": "bJ3", "rect": pygame.Rect(tile_size * 11, tile_size * 6, tile_size, tile_size), "pressed": False},
        {"id": "bJ2", "rect": pygame.Rect(tile_size * 10, tile_size * 8, tile_size, tile_size), "pressed": False},

        {"id": "bE1", "rect": pygame.Rect(tile_size * 14, tile_size , tile_size, tile_size), "pressed": False},
        {"id": "bE2", "rect": pygame.Rect(tile_size * 12, tile_size * 3, tile_size, tile_size), "pressed": False},

        {"id": "bC", "rect": pygame.Rect(tile_size * 13, tile_size * 5, tile_size, tile_size), "pressed": False},

        {"id": "bF2", "rect": pygame.Rect(tile_size * 12, tile_size * 8, tile_size, tile_size), "pressed": False},
        {"id": "bF1", "rect": pygame.Rect(tile_size * 14, tile_size * 10, tile_size, tile_size), "pressed": False},
        ]
    teleport_map = {
        "bA": (tile_size * 14, tile_size),
        "bE1": (tile_size * 2, tile_size * 5),

        "bE2": (tile_size * 5, tile_size * 3),
        "bI1": (tile_size * 14, tile_size ),

        "bB": (tile_size * 14, tile_size * 10),
        "bF1": (tile_size * 8, tile_size * 2),

        "bF2": (tile_size * 5, tile_size * 8),
        "bI2": (tile_size * 12, tile_size * 8),

        "bI3": (tile_size * 7, tile_size * 4),
        "bK1": (tile_size * 4, tile_size * 6),

        "bK2": (tile_size * 11, tile_size * 6),
        "bJ3": (tile_size * 8, tile_size * 7),

        "bJ1": (tile_size * 3, tile_size * 3),
        "bG2": (tile_size * 10, tile_size * 3),

        "bG1": (tile_size * 13, tile_size * 5),
        "bC": (tile_size , tile_size ),

        "bD": (tile_size , tile_size * 10),
        "bH1": (tile_size * 8, tile_size * 9),

        "bH2": (tile_size * 10, tile_size * 8),
        "bJ2": (tile_size * 3, tile_size * 8),
    }
    player_on_any_button = False
    for prtl in portals:
        if hitbox.colliderect(prtl["rect"]):
            player_on_any_button = True
            if not prtl["pressed"]:
                prtl["pressed"] = True
                if prtl["id"] in teleport_map:
                    new_x, new_y = teleport_map[prtl["id"]]
                    gus_x, gus_y = new_x, new_y
                    target_y = new_y
                    target_x = new_x
                    hitbox.x = gus_x
                    hitbox.y = gus_y
                    for dest_btn in portals:
                        if dest_btn["rect"].collidepoint(new_x + tile_size // 2, new_y + tile_size // 2):
                            dest_btn["pressed"] = True
        else:
            prtl["pressed"] = False
    # Draw portals based on their state
    for prtl in portals:
        if prtl["pressed"]:
            surface.blit(portal_1, (prtl["rect"].x, prtl["rect"].y))
        else:
            surface.blit(portal_2, (prtl["rect"].x, prtl["rect"].y))
def set_solved(solved):
    global is_solved
    is_solved = solved
    return True
