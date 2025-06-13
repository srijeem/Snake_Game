# Snake_Game

 ## Snake Game Animation and Logic Implementation

This repository contains two projects: a basic animation of a circle moving across a grid and a classic implementation of the Snake game.

### Animation:
#### Circle Movement: The animation starts with a circle positioned at (0, 0) - the top-left corner of the grid.

- The circle moves one square to the right on each step.

- When the circle reaches the end of a row, it:

- Moves to the first square of the next row (i.e., wraps to the start of the next line).

- This continues row by row until the circle reaches the last square of the last row.

- Once the circle reaches the end of the grid, it wraps around back to (0, 0) and the animation repeats.


## Circle to Apple Toggle: 

- By default, the circle is displayed on the grid.

- When the user presses the spacebar:

- The circle changes into an apple.

- Pressing the spacebar again:

- The apple switches back to a circle.

- This toggle can be repeated any number of times during the animation.

## Snake Game:
### Basic Mechanics: 

- The snake starts with a length of 2 at the top-left corner of the grid.

- The player controls the snake using the arrow keys.
  
- The objective is to guide the snake toward apples that appear on the grid.
  
    -Each time the snake eats an apple:
  
-The snake grows longer by one segment.

- The game continues as the snake moves and grows, becoming more challenging to navigate without collision.

### Apple Eating: 
-Each time the snake eats an apple, it grows by one block.

### Wrap-Around: 

-If the snake reaches the edge of the screen, it re-emerges from the opposite side.

### Game Over: The game ends if the snake collides with itself, at which point the "Game Over" screen is displayed.

## Testing:

The code includes a testing framework to ensure the animation and game logic function correctly.

It uses unit tests to validate key components of the game:

- Circle movement - verifies the correct step-by-step progression across the grid.

- Apple placement — ensures apples appear in valid, unoccupied positions.

- Snake growth — checks that the snake increases in length when eating an apple.

- Direction changes — confirms the snake responds accurately to arrow key inputs.

- Game-over conditions — validates that the game ends correctly upon collision with walls or the snake itself.




### Snake Game Automated Test Suite

- This Python script runs automated tests on the Snake game implementation.

- It verifies the game's core functionality through multiple test scenarios.

- Tests include checking:

   - Game start behavior

   - Snake movement

   - Apple consumption and snake growth

   - Screen wrap-around mechanics

   - Game over conditions
