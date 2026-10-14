import pygame


# ---- module-level state ----
is_solved  = False
activation = False

# ---- assets loaded at import time, matching teleportation.py's pattern ----
rock_sprite        = pygame.image.load('./assets/Rock.png').convert_alpha()
switch_on_sprite   = pygame.image.load('./assets/MountedLeverBottomOn.png').convert_alpha()
switch_off_sprite  = pygame.image.load('./assets/MountedLeverBottomOff.png').convert_alpha()

sfx_lever = pygame.mixer.Sound('assets/InteractSound.wav')

def get_solved():
    global is_solved
    return is_solved

def set_solved(solved):
    global is_solved
    is_solved = solved
    return True

def render(surface, hitbox, event, tile_size):
    global rock_sprite
    global switch_on_sprite
    global switch_off_sprite
    global is_solved
    global activation

    # Scale sprites to current tile size (mirrors how teleportation.py scales portal images)
    rock_sprite       = pygame.transform.scale(rock_sprite,       (tile_size, tile_size))
    switch_on_sprite  = pygame.transform.scale(switch_on_sprite,  (tile_size, tile_size))
    switch_off_sprite = pygame.transform.scale(switch_off_sprite, (tile_size, tile_size))

    # The switch tile — player stands here and presses SPACE to solve the room
    switch = pygame.Rect(tile_size * 6, tile_size * 6, tile_size, tile_size)

    # Rock positions that act as bumpers on the ice floor
    ROCKS = [
        (tile_size,       tile_size * 2),  (tile_size * 3,  tile_size * 8),
        (tile_size * 5,   tile_size * 6),  (tile_size * 6,  tile_size * 5),
        (tile_size * 6,   tile_size * 7),  (tile_size * 7,  tile_size * 2),
        (tile_size * 8,   tile_size * 8),  (tile_size * 10, tile_size * 4),
        (tile_size * 11,  tile_size * 5),  (tile_size * 12, tile_size * 3),
        (tile_size * 12,  tile_size * 9),  (tile_size * 13, tile_size * 6),
    ]

    # Toggle the switch when the player stands on it and presses SPACE
    if hitbox.colliderect(switch) and event:
        activation = not activation
        sfx_lever.play()
    if activation:
        is_solved = True

    # Draw switch in its current state
    if activation:
        surface.blit(switch_on_sprite,  (switch.x, switch.y))
    else:
        surface.blit(switch_off_sprite, (switch.x, switch.y))

    # Draw all rocks
    for rock in ROCKS:
        surface.blit(rock_sprite, rock)