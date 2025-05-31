import os
import pygame
import random
import math
from os import listdir
from os.path import isfile, join 
pygame.init()


BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_VEL = 5

PROFESSIONS = ["teacher", "lawyer", "healthcare", "engineer", "artist"]
collected_professions = 0
show_profession = False
current_profession_img = None
current_profession_alpha = 255



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
    path = join("assets", "terrain", "terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1 
    
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        super().__init__()
        self.SPRITES = {}
        self.SPRITES.update(load_sprite_sheet("player", "run.png", 32, 32, True))
        self.SPRITES.update(load_sprite_sheet("player", "idle.png", 32, 32, True))   
        self.SPRITES.update(load_sprite_sheet("player", "jump.png", 32, 32, True))      
        self.SPRITES.update(load_sprite_sheet("player", "fall.png", 32, 32, True))      
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
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
        self.update_sprite()
    
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        if self.y_vel < 0:
            sprite_sheet_name = "jump_" + self.direction
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet_name = "fall_" + self.direction
        elif self.x_vel != 0:
            sprite_sheet_name = "run_" + self.direction
        else:
            sprite_sheet_name = "idle_" + self.direction
        
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))



class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Orb(Object):
    ANIMATION_DELAY = 8

    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)

        self.SPRITES = load_sprite_sheet("orbs", "orb.png", size, size, False)
        self.animation_count = 0
        self.sprites = self.SPRITES["orb"]
        self.sprite = self.sprites[0]
        self.mask = pygame.mask.from_surface(self.sprite)
        self.fading = False
        self.alpha = 255  # Fully opaque

    def update_sprite(self):
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.sprites)
        self.sprite = self.sprites[sprite_index]
        self.animation_count += 1
        self.mask = pygame.mask.from_surface(self.sprite)

    def fade(self):
        if self.alpha > 0:
            self.alpha -= 15  # Fade speed
            if self.alpha < 0:
                self.alpha = 0
            self.sprite.set_alpha(self.alpha)
            self.mask = pygame.mask.from_surface(self.sprite) 

    def draw(self, win, offset_x):
        self.update_sprite()
        if self.fading:
            self.fade()
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


def draw(window, player, objects, bg_image, offset_x):
    window.blit(bg_image, (0, 0))
    for obj in objects:
        obj.draw(window, offset_x)    
    player.draw(window, offset_x)
    
    if show_profession and current_profession_img:
        img = current_profession_img.copy()
        img.set_alpha(current_profession_alpha)
        rect = img.get_rect(center=(WIDTH//2, HEIGHT//2))
        window.blit(img, rect)
    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

        collided_objects.append(obj)
    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    
    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 3)
    collide_right = collide(player, objects, PLAYER_VEL * 3)
    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    elif keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)
    
    handle_vertical_collision(player, objects, player.y_vel)


def main():
    global show_profession, collected_professions, current_profession_img, current_profession_alpha
    clock = pygame.time.Clock()
    win_width, win_height = WIDTH, HEIGHT
    window = pygame.display.set_mode((win_width, win_height), pygame.RESIZABLE)
    pygame.display.set_caption("Exploration - A Short Platformer Game")
    
    BG_IMAGE_ORIG = pygame.image.load(os.path.join("assets", "Background.png")).convert_alpha()
    BG_IMAGE = pygame.transform.scale(BG_IMAGE_ORIG, (WIDTH, HEIGHT))

    FINAL_IMAGES = []
    FINAL_ANIMATION_DELAY = 20  
    final_animation_index = 0
    final_animation_timer = 0

    final_folder = os.path.join("assets", "FINAL")
    if os.path.exists(final_folder):
        for fname in sorted(os.listdir(final_folder)):
            if fname.endswith(".png"):
                img = pygame.image.load(os.path.join(final_folder, fname)).convert_alpha()
                FINAL_IMAGES.append(img)

    block_size = 64
    orb_size = 70

    player = Player(100, 100, 50, 50)
    floor = [Block(i*block_size, HEIGHT - block_size, block_size) 
             for i in range(-WIDTH // block_size, WIDTH * 100 // block_size)]
    
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), 
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), 
               Block(block_size * 4, HEIGHT - block_size * 4, block_size), 
               Block(block_size * 10, HEIGHT - block_size * 4, block_size),
               Block(block_size * 11, HEIGHT - block_size * 4, block_size),
               Block(block_size * 14, HEIGHT - block_size * 6, block_size),
               Block(block_size * 15, HEIGHT - block_size * 6, block_size),               
               Block(block_size * 16, HEIGHT - block_size * 6, block_size),
               Block(block_size * 17, HEIGHT - block_size * 6, block_size),
               Block(block_size * 18, HEIGHT - block_size * 6, block_size),
               Block(block_size * 19, HEIGHT - block_size * 6, block_size),
               Block(block_size * 20, HEIGHT - block_size * 6, block_size),
               Block(block_size * 24, HEIGHT - block_size * 3, block_size),
               Block(block_size * 25, HEIGHT - block_size * 4, block_size),
               Block(block_size * 26, HEIGHT - block_size * 5, block_size),
               Block(block_size * 27, HEIGHT - block_size * 5, block_size),
               Block(block_size * 28, HEIGHT - block_size * 5, block_size),
               Block(block_size * 29, HEIGHT - block_size * 5, block_size),
               ]

    
    
    
    
    teacherOrb = Orb(300, HEIGHT - orb_size * 3, 70)  
    objects.append(teacherOrb)

    lawyerOrb = Orb(1344, HEIGHT - orb_size * 3, 70)  
    objects.append(lawyerOrb)
    
    healthcareOrb = Orb(2000, HEIGHT - orb_size * 3, 70)  
    objects.append(healthcareOrb)

    engineerOrb = Orb(3000, HEIGHT - orb_size * 3, 70)
    objects.append(engineerOrb)

    artistOrb = Orb(4000, HEIGHT - orb_size * 3, 70)
    objects.append(artistOrb)

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        current_fps = 40
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
            
            if show_profession and event.type == pygame.MOUSEBUTTONDOWN:
                show_profession = False
                collected_professions += 1
                if collected_professions == 5:
                    final_animation_index = 0
                    final_animation_timer = 0

        # --- FINAL ANIMATION ---
        if collected_professions >= 5:
            window.fill(BG_COLOR)
            if FINAL_IMAGES:
                final_animation_timer += 1
                if final_animation_timer >= FINAL_ANIMATION_DELAY:
                    final_animation_timer = 0
                    final_animation_index = (final_animation_index + 1) % len(FINAL_IMAGES)
                img = FINAL_IMAGES[final_animation_index]
                rect = img.get_rect(center=(win_width//2, win_height//2))
                window.blit(img, rect)
            pygame.display.update()
            continue  # Skip the rest of the game logic

        # --- NORMAL GAME LOGIC ---
        player.loop(FPS)

        for obj in objects[:]:
            if isinstance(obj, Orb) and not obj.fading:
                if player.mask is not None and obj.mask is not None:
                    if pygame.sprite.collide_mask(player, obj):
                        obj.fading = True
            if isinstance(obj, Orb) and obj.fading and obj.alpha == 0:
                objects.remove(obj)
                if collected_professions < len(PROFESSIONS):
                    show_profession = True
                    img_path = os.path.join("assets", "orbs", "professions", f"{PROFESSIONS[collected_professions]}.png")
                    current_profession_img = pygame.image.load(img_path).convert_alpha()
                    current_profession_alpha = 255
        handle_move(player, objects)
        draw(window, player, objects, BG_IMAGE, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0): 
            offset_x += player.x_vel
    pygame.quit()
    quit()


if __name__ == "__main__":
    main()


