# Snake_Game

Snake Game Animation and Logic Implementation

This repository contains two projects: a basic animation of a circle moving across a grid and a classic implementation of the Snake game.

Animation:
Circle Movement: The animation starts with a circle at position (0, 0), moving right one square at a time. Once the circle reaches the end of a row, 
it moves to the first square of the next row. When it reaches the last row, it wraps around back to (0, 0).

Circle to Apple Toggle: Pressing the spacebar changes the circle into an apple. Pressing the spacebar again switches it back to the circle.

Snake Game:
Basic Mechanics: The snake starts with a length of 2 at the top left of the grid. The player controls the snake with arrow keys, 
guiding it towards apples to grow longer.

Apple Eating: Each time the snake eats an apple, it grows by one block.

Wrap-Around: If the snake reaches the edge of the screen, it re-emerges from the opposite side.

Game Over: The game ends if the snake collides with itself, at which point the "Game Over" screen is displayed.

Testing:
The code includes a testing framework that ensures the animation and game logic work as intended. It uses unit tests to validate the correct behavior of the circle's movement, 
apple placement, snake growth, direction changes, and game-over conditions.
