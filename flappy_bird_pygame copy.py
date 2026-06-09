import pygame
import neat
import time
import os
import random
pygame.font.init()

# Set the width and height of the game window
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Variables to keep track of the generation and the number of birds in the generation
GEN = 0
NUM_BIRDS = 0

# Load the bird, pipe, background, and base images
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))

# Load the font for displaying text
STAT_FONT = pygame.font.SysFont("comicsans", 50)

# Define the Bird class
class Bird:
    # Load the images, set the maximum rotation and rotation velocity, and set the animation time
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    # Initialize the Bird object with its x and y position, and other variables
    def __init__(self, x, y):

        self.x = x  # x position of the bird
        self.y = y  # y position of the bird
        self.tilt = 0  # current tilt/angle of the bird
        self.tick_count =  0  # number of frames since the last jump
        self.vel = 0  # current velocity of the bird
        self.height = self.y  # height of the bird from the ground
        self.img_count = 0  # current animation frame
        self.img = self.IMGS[0]  # current image of the bird

    # Make the bird jump by changing its velocity and tick count
    def jump(self):
        self.vel = -10.5  # velocity of the bird after the jump (negative due to vertically flipped coordinate system)
        self.tick_count = 0  # reset the tick count
        self.height = self.y  # record the current height of the bird before the jump

    # Move the bird by changing its tick count and y position
    def move(self):
        self.tick_count += 1  # increment the tick count

        # Calculate the distance to move the bird up or down
        d = self.vel*self.tick_count+1.5*self.tick_count**2

        # Limit the maximum downward movement to 16 pixels per frame
        if d >= 16:
            d = d/abs(d)*16

        # Add 2 pixels of additional upward movement
        if d < 0:
            d -= 2
        
        # Move the bird by the calculated distance
        self.y = self.y + d

        # Set the bird's tilt based on its movement
        if d <0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else: 
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    # Draw the bird on the game window
    def draw(self, win):
        # Update the bird's image count
        self.img_count += 1

        # Set the bird's image based on the animation time
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4+1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        # Change the bird's image to a "diving" image if its tilt is too low
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
        
        # Rotate the bird's image by its current tilt angle
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        
        # Create a new rectangle object for the rotated image and center it on the bird's current position
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        
        # Draw the rotated image onto the game window at the new rectangle's top-left position
        win.blit(rotated_image, new_rect.topleft)

    
    def get_mask(self):
        # Returns a mask object for collision detection based on the bird's current image
        return pygame.mask.from_surface(self.img)

# Define  the Pipe class
class Pipe:
    # Set the gap between pipes and the velocity of the pipes
    GAP = 180
    VEL = 5
    def __init__(self, x):
        # Initialize the Pipe with its position and height
        self.x = x
        self.height = 0

        # Set the positions of the top and bottom pipes
        self.top = 0
        self.bottom = 0

        # Load the images for the top and bottom pipes
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        # Set whether the bird has passed the pipe
        self.passed = False

        # Set the initial height of the pipes
        self.set_height()

    def set_height(self):
        # Set the height of the pipes randomly
        self.height = random.randrange(50, 450)

        # Calculate the position of the top and bottom pipes based on the gap
        self.top = self.height - self.PIPE_TOP.get_height()    
        self.bottom = self.height + self.GAP

    def move(self):
        # Move the pipes to the left based on their velocity
        self.x -= self.VEL
        
    def draw(self, win):
        # Draw the top and bottom pipes on the game window
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        # Get the masks for the bird and the top and bottom pipes
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # Calculate the offset between the bird and the pipes
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x-bird.x, self.bottom - round(bird.y))

        # Check if the bird collides with the top or bottom pipe
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        # Return True if the bird collides with either pipe, False otherwise
        if t_point or b_point:
            return True
        
        return False

# Define the Base class    
class Base:
    # Set class variables
    VEL = 5 # Velocity of the base
    WIDTH = BASE_IMG.get_width() # Width of the base image
    IMG = BASE_IMG # Base image

    # Initialize the Base object
    def __init__(self, y):
        self.y = y  # Set the y-coordinate of the base
        self.x1 = 0  # Set the initial x-coordinate of the first base image
        self.x2 = self.WIDTH  # Set the initial x-coordinate of the second base image to the width of the base image

    # Move the base to the left
    def move(self):
        self.x1 -= self.VEL  # Update the x-coordinate of the first base image
        self.x2 -= self.VEL  # Update the x-coordinate of the second base image

        # If the first base image goes off the screen, move it to the right of the second image
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        # If the second base image goes off the screen, move it to the right of the first image
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    # Draw the base on the game window
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))  # Draw the first base image
        win.blit(self.IMG, (self.x2, self.y))  # Draw the second base image

# Define a function to draw the game window
def draw_window(win, birds, pipes, base, score, gen, num_birds):
    # Fill the background of the window with the background image
    win.blit(BG_IMG, ( 0,0))

    # Draw all the pipes in the pipe list
    for pipe in pipes:
        pipe.draw(win)

    # Create a text surface with the current score and draw it on the window
    text = STAT_FONT.render("Score: " +  str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(),10))

    # Create a text surface with the current generation and draw it on the window
    text = STAT_FONT.render("Gen: " +  str(gen), 1, (255,255,255))
    win.blit(text, (10,10))

    # Create a text surface with the current number of birds and draw it on the window
    text = STAT_FONT.render("Birds: " +  str(num_birds), 1, (255,255,255))
    win.blit(text, (10,90))

    # Draw the base on the window
    base.draw(win)

    # Draw each bird on the window
    for bird in birds:
        bird.draw(win)

    # Update the display to show the changes
    pygame.display.update()

# This is the main function that runs the game using the NEAT algorithm.
def main(genomes, config):
    # Global variable GEN keeps track of the generation number.
    global GEN
    GEN += 1
    # Initialize lists to store neural networks, genomes, and birds.
    nets = []
    ge = []
    birds = []

        # Loop through each genome provided in the population.
    for _, g in genomes:
        # Create a new neural network for each genome using the NEAT configuration.
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        # Create a new bird object and add it to the birds list.
        birds.append(Bird(230, 350))
        # Set the fitness of the genome to 0 initially.
        g.fitness = 0
        # Add the genome to the list of genomes.
        ge.append(g)


    # Create the base and initial pipe objects.
    base = Base(730)
    pipes = [Pipe(600)]
    # Set up the game window and clock.
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    # Set the initial score to 0.
    score = 0

    # Start the main game loop.
    run = True
    while run:
        # Handle any pygame events (such as closing the window).
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # Determine which pipe the birds should be focused on.
        pipe_ind = 0
        NUM_BIRDS = len(birds)

        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        # Loop through each bird and determine its movement and fitness.
        for x, bird in enumerate(birds):
            bird.move()
            # Increase the fitness of the genome for each frame the bird is alive.
            ge[x].fitness += 0.1
            # Activate the neural network for the current bird using the input values.
            output = nets[x].activate((bird.y, abs(bird.y-pipes[pipe_ind].height), abs(bird.y-pipes[pipe_ind].bottom)))
            # If the output value of the neural network is greater than 0.5, make the bird jump.
            if output[0] > 0.5:
                bird.jump()

        # Determine if a new pipe should be added to the game.
        add_pipe = False
        # Create a list of pipes to remove.
        rem = []

        # Loop through all pipes in the game
        for pipe in pipes:
            # Loop through all birds in the game
            for x, bird in enumerate(birds):
                # If the bird collides with the pipe, decrease its fitness score and remove it from the game
                if pipe.collide(bird):
                    ge[x].fitness -=1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                    # If the pipe hasn't been passed and the bird has flown past it, mark the pipe as passed and set the flag to add a new pipe
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            # If the pipe has moved off the screen, add it to the removal list
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            # Move the pipe in preparation for the next frame
            pipe.move()

        # If the flag 'add_pipe' is True, a pipe has been passed and the score should be updated along with the fitness of each bird.
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        # Remove pipes that have moved off the screen
        for r in rem:
            pipes.remove(r)

        # Check if any bird has hit the ceiling or the floor. If a bird hits the ceiling or the floor, remove the bird and its associated genome and neural net.
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        # Move the base
        base.move()
        #Update the game window with the new position of birds, pipes, and the base
        draw_window(win, birds, pipes, base, score, GEN, NUM_BIRDS)  


# Importing necessary modules
import os
import neat

# Define the function 'run' with the parameter 'config_path' which will run the NEAT algorithm on the main function
def run(config_path):
    
    # Load the NEAT configuration file from the specified path
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create a NEAT population object using the loaded configuration
    p = neat.Population(config)

    # Add a standard output reporter to print progress on every generation
    p.add_reporter(neat.StdOutReporter(True))

    # Add a statistics reporter to print statistics on the current population
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run the NEAT algorithm for up to 50 generations and return the winning genome
    winner = p.run(main, 50)

# If this script is run directly, not imported as a module, run the algorithm using the specified configuration file
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
