import pygame
import random
from pygame import mixer
import sys

pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode((905, 703))

# Background
background = pygame.image.load("bg001.png")

# Title and Icon
pygame.display.set_caption("Pixel Clash!")
icon = pygame.image.load("001-swordsman.png")
pygame.display.set_icon(icon)

# Sound
mixer.music.load("SuperHero_original.ogg")
mixer.music.play(-1)
slash_sound = mixer.Sound("sword-unsheathe.wav")

GRAVITY = 1


# Load Spritesheets
def load_spritesheet(spritesheet_name, sprite_width, sprite_height, scale_factor):
    
    spritesheet = pygame.image.load(spritesheet_name)

    # List to store rect objects for each sprite
    sprite_rects = []

    # Loop to create rects for each sprite
    for y in range(0, spritesheet.get_height(), sprite_height):
        for x in range(0, spritesheet.get_width(), sprite_width):
            sprite_rect = pygame.Rect(x, y, sprite_width, sprite_height)
            sprite_rects.append(sprite_rect)

    # Create a list to store individual sprite surfaces
    sprites = []

    # Extract each sprite using the rects
    for rect in sprite_rects:
        sprite = spritesheet.subsurface(rect)
        scaled_sprite = pygame.transform.scale(sprite, (sprite_width * scale_factor, sprite_height * scale_factor))
        sprites.append(scaled_sprite)

    # Sprites are stored in a list of sprites, goes from 0 to 99
    # 0 to 9 => idle
    # 10 to 19 => gesture
    # 20 to 29 => walk
    # 30 to 39 => attack
    # 40 to 49 => death
    return sprites


class Character:
    def __init__(self, x, y, x_speed, y_speed, ground, spritesheet_file, sprite_width, sprite_height, scale_factor, anim_rate):
        self.x = x
        self.y = y
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.sprites = load_spritesheet(spritesheet_file, sprite_width, sprite_height, scale_factor)
        self.image = self.sprites[0]
        self.direction = "right"
        self.state = "idle"
        self.anim_count = 0.0
        self.jumping = False
        self.jump = -20
        self.attacking = False
        self.strike = False
        self.health = 100
        self.anim_rate = anim_rate
        self.ground = ground

    def update_sprite(self):
        if self.state == "idle":
            if round(self.anim_count) not in range(0, 10):
                self.anim_count = 0.0
            self.image = self.sprites[round(self.anim_count)]
            self.anim_count += self.anim_rate

        if self.state == "walk":
            if round(self.anim_count) not in range(20, 30):
                self.anim_count = 20.0
            self.image = self.sprites[round(self.anim_count)]
            self.anim_count += self.anim_rate

        if self.state == "jump":
            if round(self.anim_count) not in range(10, 20):
                self.anim_count = 10.0
            self.image = self.sprites[round(self.anim_count)]
            self.anim_count += self.anim_rate

        if self.state == "attack":
            if round(self.anim_count) not in range(30, 40):
                self.anim_count = 33.0
            self.image = self.sprites[round(self.anim_count)]
            self.anim_count += self.anim_rate
            if round(self.anim_count) in range(36, 40):
                self.strike = True

        if self.state == "death":
            if round(self.anim_count) not in range(40, 50):
                self.anim_count = 40.0
            self.image = self.sprites[round(self.anim_count)]
            self.anim_count += self.anim_rate
            if round(self.anim_count) == 49:
                self.anim_rate = 0.0

    def animate(self):
        self.update_sprite()
        if self.direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)
        screen.blit(self.image, (self.x, self.y))

    
class Player(Character):
    def __init__(self):
        super().__init__(440, 400, 5, 0, 565, "warrior spritesheet calciumtrice.png", 32, 32, 2.5, 0.4)
        self.score = 0

    def update(self, keys):
        
        if not any (keys) and player.state != "death":
            if self.y == self.ground:
                self.state = "idle"

        # Walking left
        if keys[pygame.K_LEFT]:
            if self.y == self.ground:
                self.state = "walk"
            self.direction = "left"
            self.x -= self.x_speed
            if self.x <= 0:
                self.x = 0

        # Walking right
        if keys[pygame.K_RIGHT]:
            if self.y == self.ground:
                self.state = "walk"
            self.direction = "right"
            self.x += self.x_speed
            if self.x >= 841:
                self.x = 841

        # Jumping
        if keys[pygame.K_SPACE]:
            self.state = "jump"

        # Attacking (you have to stand still)
        if keys[pygame.K_RSHIFT] and not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_SPACE]):
            self.state = "attack"

        # Handle player jump and vertical boundaries
        self.y_speed += GRAVITY
        self.y += self.y_speed
        if self.y >= self.ground:
            self.y = self.ground
            self.jumping = False


player = Player()


class Enemy(Character):
    def __init__(self, x_speed, ground, spritesheet_file, damage, sprite_width, sprite_height, scale_factor, anim_rate):
        super().__init__(random.randint(100, 800), random.randint(200, 300), x_speed, 0, ground, spritesheet_file, sprite_width, sprite_height, scale_factor, anim_rate)
        self.damage = damage

    def update(self):
        self.y_speed += GRAVITY
        self.y += self.y_speed
        if self.y >= self.ground:
            self.y = self.ground
            self.state = "walk"
            distance = player.x - self.x

            # Enemy chase
            if abs(distance) > 25:

                if distance > 0:
                    self.direction = "right"
                    self.x += self.x_speed
                if distance < 0:
                    self.direction = "left"
                    self.x -= self.x_speed

            # Enemy attack
            if abs(distance) <= 25 and player.jumping == False:
                self.state = "attack"
                if self.strike:
                    player.health -= self.damage
                    self.strike = False

            # Enemy hit
            if abs(distance) <= 25 and player.state == "attack" and player.direction != self.direction and self.y == self.ground:
                slash_sound.play()
                player.score += 1
                self.x = player.x + random.randint(-300, 300)
                self.y = random.randint(200, 300)
                self.y_speed = 0
                self.state = "idle"


# Spawned Enemies
orc = Enemy(4, 565, "HunterOrc.png", 1, 32, 32, 2.5, 0.4)
goblin = Enemy(4, 550, "goblin spritesheet calciumtrice.png", 1, 32, 32, 3.0, 0.4)
ghost = Enemy(4, 565, "Ghost.png", 1, 32, 32, 2.5, 0.4)
skeleton = Enemy(4, 565, "skeleton spritesheet calciumtrice.png", 1, 32, 32, 2.5, 0.4)
wizard = Enemy(4, 565, "CrazyWizard.png", 1, 32, 32, 2.5, 0.4)

Enemies = [orc, goblin, ghost, skeleton, wizard]


class Cloud:
    def __init__(self, x, y, x_speed , spritesheet_file, sprite_width, sprite_height, scale_factor):
        self.x = x
        self.y = y
        self.x_speed = x_speed
        self.sprites = load_spritesheet(spritesheet_file, sprite_width, sprite_height, scale_factor)
        self.image = self.sprites[0]

    def update(self):
        self.x += self.x_speed

        if self.x > 1000 or self.x < -100:
            self.x_speed *= -1
            self.y = random.randint(100, 200)

    def animate(self):
        screen.blit(self.image, (self.x, self.y))

Clouds = []

for n in range(0, 3):
    cloud = Cloud(random.randint(0, 400), random.randint(100, 200), random.randint(6, 8), "nuvem.png", 32, 32, 3.5)
    Clouds.append(cloud)

for n in range(0, 3):
    cloud = Cloud(random.randint(400, 900), random.randint(100, 200), -random.randint(6, 8), "nuvem.png", 32, 32, 3.5)
    Clouds.append(cloud)


def show_stats():
    stats_font = pygame.font.Font("Enchanted Land.otf", 64)
    health = stats_font.render("Health: " + str(player.health), True, (32, 32, 32))
    score = stats_font.render("Score: " + str(player.score), True, (32, 32, 32))
    screen.blit(health, (10, 10))
    screen.blit(score, (720, 10))

                                   

# Initialize the game state
GAME_STATE = "MENU"


# Game Loop
RUNNING = True
while RUNNING:

    # Background Image
    screen.blit(background, (0, 0))

    clock.tick(30)


    # Main Menu
    if GAME_STATE == "MENU":

        # Title Screen
        title_font = pygame.font.Font("Early GameBoy.ttf", 60)
        title_text = title_font.render("Pixel Clash!", True, (32, 32, 32))
        screen.blit(title_text, (120, 200))

        start_button_font = pygame.font.Font("Enchanted Land.otf", 100)
        start_button = pygame.Rect(302, 301, 300, 100)
        start_text = start_button_font.render("Start", True, (255, 255, 255))
        start_text_rect = start_text.get_rect(center=start_button.center)
        pygame.draw.rect(screen, (32, 32, 32), start_button)
        screen.blit(start_text, start_text_rect)



        for event in pygame.event.get():

            # Quiting the game
            if event.type == pygame.QUIT:
                RUNNING = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    GAME_STATE = "GAME"


    # Game Play
    elif GAME_STATE == "GAME":

        keys = pygame.key.get_pressed()

        player.update(keys)

        for enemy in Enemies:
            enemy.update()

        for cloud in Clouds:
            cloud.update()

        for event in pygame.event.get():

            # Quiting the game
            if event.type == pygame.QUIT:
                RUNNING = False
                pygame.quit()
                sys.exit()

            # Jump Mechanic
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not player.jumping:
                    player.jumping = True
                    player.y_speed = player.jump

        # Check for game over condition
        if player.health <= 0:
            GAME_STATE = "DEAD"
            
        # Execute animations
        player.animate()

        for enemy in Enemies:
            enemy.animate() 

        for cloud in Clouds:
            cloud.animate()

        show_stats()

    
    # Game Over
    elif GAME_STATE == "DEAD":

        player.health = 0

        # Send the enemies away
        for enemy in Enemies:
            enemy.x = 2000
            enemy.x_speed = 0

        player.state = "death"
        player.animate()


        # Game over screen
        game_over_font = pygame.font.Font("Enchanted Land.otf", 128)
        final_score_font = pygame.font.Font("Enchanted Land.otf", 80)
        game_over_text = game_over_font.render("Game Over", True, (32, 32, 32))
        game_over_score = final_score_font.render("You slayed " + str(player.score) + " monsters", True, (32, 32, 32))
        screen.blit(game_over_text, (249, 100))
        screen.blit(game_over_score, (220, 250))

        restart_button_font = pygame.font.Font("Enchanted Land.otf", 80)
        restart_button = pygame.Rect(302, 390, 300, 100)
        restart_text = restart_button_font.render("Try Again", True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center=restart_button.center)
        pygame.draw.rect(screen, (32, 32, 32), restart_button)
        screen.blit(restart_text, restart_text_rect)
        

        for event in pygame.event.get():

            # Quiting the game
            if event.type == pygame.QUIT:
                RUNNING = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):

                    # Reset the game state
                    GAME_STATE = "GAME"

                    # Reset the player attributes
                    player.health = 100
                    player.state = "idle"
                    player.score = 0
                    player.anim_rate = 0.4

                    # Reset the enemies
                    for enemy in Enemies:
                        enemy.x = random.randint(100, 800)
                        enemy.y = random.randint(200, 300)
                        enemy.x_speed = 4
                        enemy.y_speed = 0
                        enemy.state = "idle"
        
                

    pygame.display.update()