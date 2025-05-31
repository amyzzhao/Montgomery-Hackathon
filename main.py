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
BG_IMAGE_ORIG = pygame.image.load(os.path.join("assets", "Background.png"))



def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheet(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png", "")+"_right"] = sprites
            all_sprites[image.replace(".png", "")+"_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    
    return all_sprites

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1 
    SPRITES = load_sprite_sheet("player", "walkingAnimation.png", 32, 32, True)

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0

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
    
    def draw(self, win):
        self.sprite = self.SPRITES["walkingAnimation_" + self.direction][0]
        win.blit(self.sprite, (self.rect.x, self.rect.y))

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


def main(window):
    clock = pygame.time.Clock()
    win_width, win_height = WIDTH, HEIGHT
    window = pygame.display.set_mode((win_width, win_height), pygame.RESIZABLE)
    pygame.display.set_caption("Platformer")
    BG_IMAGE = pygame.transform.scale(BG_IMAGE_ORIG, (WIDTH, HEIGHT))

    player = Player(100, 100, 50, 50)

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            elif event.type == pygame.VIDEORESIZE:
                win_width, win_height = event.w, event.h
                window = pygame.display.set_mode((win_width, win_height), pygame.RESIZABLE)
                BG_IMAGE = pygame.transform.scale(BG_IMAGE_ORIG, (win_width, win_height))
        window.blit(BG_IMAGE, (0, 0))

        player.loop(FPS)
        handle_move(player)
        draw(window, player)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)


