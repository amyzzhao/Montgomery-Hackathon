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


window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Platformer")


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1 

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
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        
        self.fall_count += 1
    
    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, self.rect)


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
    BG_IMAGE = pygame.transform.scale(BG_IMAGE_ORIG, (WIDTH, HEIGHT))
    win_width, win_height = WIDTH, HEIGHT

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


