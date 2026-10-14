#Jordan Pope
#room that player enters when they win the game
#4.20.26
import pygame
clicked = False
is_solved = False
treasure_sprite = pygame.image.load("./assets/Treasure1.png").convert_alpha()
print("win room")
def render(surface, hitbox, event, tile_size):
    global clicked
    global treasure_sprite
    global is_solved
    treasure_rect = pygame.Rect(tile_size * 5, tile_size * 7, tile_size, tile_size)
    treasure_sprite = pygame.transform.scale(treasure_sprite, (tile_size, tile_size))
    surface.blit(treasure_sprite, (treasure_rect.x, treasure_rect.y))
    if hitbox.colliderect(treasure_rect) and event:
        clicked = True
    if clicked:
        is_solved = True
        print(is_solved)
def set_solved(solved):
    global is_solved
    is_solved = solved
    return is_solved
def get_solved():
    global is_solved
    return is_solved
