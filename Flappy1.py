import pygame
from pygame.locals import *
import random

pygame.mixer.init(44100, -16, 1, 512)
pygame.init()

clock = pygame.time.Clock() 
fps = 40

screen_width = 864
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")
# Define fonts and font colors
font = pygame.font.SysFont('Bauhaus 93', 60)
white = (255, 255, 255)

# Game variables
ground_scroll = 0
ground_scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500 # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
high_score = 0
grace_duration = 800  # milliseconds
grace_start = None
show_start_screen = True

# Load images
bg =  pygame.image.load('images/bg.png')
ground = pygame.image.load('images/ground.png')
restart_img = pygame.image.load('images/restart.png')


# Load Sound Files
score_sound = pygame.mixer.Sound('Sounds/sfx_point.mp3')
collide_sound = pygame.mixer.Sound('Sounds/sfx_die.mp3')
game_music = pygame.mixer.music.load('Sounds/3-main-theme-101soundboards.mp3')
pygame.mixer.music.set_volume(0.7)

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

def reset_game():
    global score, grace_start
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = screen_height // 2
    flappy.reset(100, screen_height // 2)
    score = 0 
    grace_start = None
    return score
   


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load('images/bird1.png'),
                       pygame.image.load('images/bird2.png'),
                       pygame.image.load('images/bird3.png')]
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'images/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
    
    def update(self, current_time):
        if flying == True: 
            # Gravity
            if grace_start is not None and current_time - grace_start < grace_duration:
                self.rect.x += 2  # horizontal glide
            else:
                self.vel += 0.5
                if self.vel > 10:
                    self.vel = 10
                if self.rect.bottom < screen_height - ground.get_height(): 
                    self.rect.y += self.vel
        
        if game_over == False:
        # Jump
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            # Handle animation
            self.counter += 1
            flap_cooldown = 5
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                # Update the image
                self.image = self.images[self.index]


            # rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)  
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)
    # Jump method for mouse and keyboard input
    def jump(self):
        self.vel = -10
        self.clicked = True


    def reset(self, x, y):
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index] 

# pipes
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/pipe.png')
        self.rect = self.image.get_rect()
        # position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - pipe_gap // 2]
        if position == -1:
            self.rect.topleft = [x, y + pipe_gap // 2]

    def update(self):
        # Move the pipe to the left
        self.rect.x -= ground_scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        # get mouse position
        mouse_pos = pygame.mouse.get_pos()
        # Check if mouse is over the button
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #  Draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, screen_height // 2)       
bird_group.add(flappy)

#  Create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 -100, restart_img)

run  = True
while run:
    clock.tick(fps)
    # Draw background
    screen.blit(bg, (0,0))

    bird_group.draw(screen)
    current_time = pygame.time.get_ticks()
    bird_group.update(current_time)

    pipe_group.draw(screen)

    # Draw ground
    screen.blit(ground, (ground_scroll, screen_height - ground.get_height()))

    # Check score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                score_sound.play()
                # Update high score if current score is higher
                if score > high_score:
                    high_score = score
                pass_pipe = False
   
    draw_text(f'SCORE: {score}', font, white, 20, 20)    
    draw_text(f'HI: {high_score}', font, white, screen_width - 180, 20)
    #  Look for collisions
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        if not game_over:
            collide_sound.play()
            game_over = True

    # Check if bird has hit the ground
    if flappy.rect.bottom >= screen_height - ground.get_height():
        if not game_over:
            collide_sound.play()
            game_over = True
            flying = False
         
    if game_over == False and flying == True:

        # generate pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, screen_height // 2 + pipe_height, -1)
            top_pipe = Pipe(screen_width, screen_height // 2 + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

    # Draw and scroll the ground
        ground_scroll -= ground_scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0
        pipe_group.update()

    # Check for game over and reset
    if game_over == True:
       if button.draw() == True:
           game_over = False
           score = reset_game()

    #  Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # Mouse Input
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not flying and not game_over:
                flying = True
                pygame.mixer.music.play(loops =- 1)
            elif flying and not game_over:
                flappy.jump()
        # Keyboard Input
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not flying and not game_over:
                flying = True
                pygame.mixer.music.play(loops =- 1)
            elif flying and not game_over:
                flappy.jump()
            elif game_over:
                game_over = False
                score = reset_game()
        # Grace time while start
        if (event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)):
            if not flying and not game_over:
                flying = True
                grace_start = pygame.time.get_ticks()    
    pygame.display.update()

pygame.quit()

    


