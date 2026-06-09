# Pygame Flappy Bird

A Flappy Bird clone built with Python and Pygame, featuring an AI that learns to play using the NEAT (NeuroEvolution of Augmenting Topologies) algorithm.

## How It Works

The game uses NEAT to evolve a population of 200 birds over up to 50 generations. Each bird is controlled by a small neural network with 3 inputs:

- Bird's current Y position
- Distance from the bird to the top pipe gap
- Distance from the bird to the bottom pipe gap

The network outputs a single value — if it exceeds 0.5, the bird jumps. Birds are rewarded for staying alive and penalized for hitting pipes. Over successive generations, the population learns to navigate the pipes.

## Requirements

- Python 3.x
- [Pygame](https://www.pygame.org/) (`pip install pygame`)
- [neat-python](https://neat-python.readthedocs.io/) (`pip install neat-python`)

## Running

```bash
python3 flappy_bird_pygame.py
```

The simulation will run automatically — no input needed. Generation number, score, and live bird count are displayed on screen.

## Project Structure

```
Pygame_Flappy_Bird/
├── flappy_bird_pygame.py   # Main game and NEAT training loop
├── config-feedforward.txt  # NEAT hyperparameter configuration
└── imgs/                   # Game sprites (bird, pipe, background, base)
```
