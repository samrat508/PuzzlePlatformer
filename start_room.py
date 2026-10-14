import pygame

#==========================
# Sprites
#==========================
lever_sprite_on = pygame.image.load("./assets/MountedLeverBottomOn.png").convert_alpha()
lever_sprite_off = pygame.image.load("./assets/MountedLeverBottomOff.png").convert_alpha()
#==========================
# Game State
#==========================
is_solved = False
def render(surface, hitbox, event, tile_size):
    global is_solved
    global lever_sprite_on
    global lever_sprite_off
    # ============================
    # Creating objects
    # ============================
    lever_sprite_on = pygame.transform.scale(lever_sprite_on, (tile_size, tile_size))
    lever_sprite_off = pygame.transform.scale(lever_sprite_off, (tile_size, tile_size))
    lever_rect = pygame.Rect(tile_size * 6, tile_size * 7, tile_size, tile_size)
    #==============================
    # Game Logic
    #==============================
    if hitbox.colliderect(lever_rect) and event:
        is_solved = not is_solved
    if is_solved:
        surface.blit(lever_sprite_on, (lever_rect.x, lever_rect.y))
    else:
        surface.blit(lever_sprite_off, (lever_rect.x, lever_rect.y))
        get_solved()
def set_solved(solved):
    global is_solved
    is_solved = solved
    return is_solved
def get_solved():
    global is_solved
    return is_solved