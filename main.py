import os
import pygame
import random
import math
from os import listdir
from os.path import isfile, join 
pygame.init()


BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheet(dir1, file_name, width, height, direction=False):
    path = os.path.join("assets", dir1, file_name)
    sprite_sheet = pygame.image.load(path).convert_alpha()
    base_name = file_name.replace(".png", "")
    all_sprites = {}
    sprites = []
    for i in range(sprite_sheet.get_width() // width):
        surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        rect = pygame.Rect(i * width, 0, width, height)
        surface.blit(sprite_sheet, (0, 0), rect)
        sprites.append(pygame.transform.scale2x(surface))

    base_name = file_name.replace(".png", "")
    if direction:
        all_sprites[base_name + "_right"] = sprites
        all_sprites[base_name + "_left"] = flip(sprites)
    else:
        all_sprites[base_name] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        super().__init__()
        self.SPRITES = {}
        self.SPRITES.update(load_sprite_sheet("player", "run.png", 32, 32, True))
        self.SPRITES.update(load_sprite_sheet("player", "idle.png", 32, 32, True))        
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
<<<<<<< HEAD
        self.jump_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
=======
        
        

>>>>>>> aa11f93fc02078157f7541294f48b68983f832c3


    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
    
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0


    def loop(self, fps):
        #self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        
        self.fall_count += 1
        self.update_sprite()
    
    def update_sprite(self):
        if self.x_vel == 0:
            sprite_sheet_name = "idle_" + self.direction
        else:
            sprite_sheet_name = "run_" + self.direction
        
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, window):
        window.blit(self.sprite, (self.rect.x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def draw(window, player):
    player.draw(window)
    pygame.display.update()


def handle_move(player):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    if keys[pygame.K_a]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d]:
        player.move_right(PLAYER_VEL)
    

def main():
    clock = pygame.time.Clock()
    win_width, win_height = WIDTH, HEIGHT
    window = pygame.display.set_mode((win_width, win_height), pygame.RESIZABLE)
    pygame.display.set_caption("Platformer")
    
    BG_IMAGE_ORIG = pygame.image.load(os.path.join("assets", "Background.png")).convert_alpha()
    BG_IMAGE = pygame.transform.scale(BG_IMAGE_ORIG, (WIDTH, HEIGHT))

    player = Player(100, 100, 50, 50)

    run = True
    while run:
        if player.x_vel == 0:
            current_fps = 15
        if player.y_vel != 0: 
            current_fps = 60
        else:
            current_fps = 60
        
        clock.tick(current_fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            elif event.type == pygame.VIDEORESIZE:
                win_width, win_height = event.w, event.h
                window = pygame.display.set_mode((win_width, win_height), pygame.RESIZABLE)
                BG_IMAGE = pygame.transform.scale(BG_IMAGE_ORIG, (win_width, win_height))
            
            elif event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_w and player.jump_count < 2:
                    player.jump()
        window.blit(BG_IMAGE, (0, 0))

        player.loop(FPS)
        handle_move(player)
        draw(window, player)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()


