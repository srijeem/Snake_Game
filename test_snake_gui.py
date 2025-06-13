import time

import snakelib_second as snakelib # Import custom snake testing library with alias snakelib
import snake                       # Import the student's snake game module to be tested
from unittest import TestCase      # Import TestCase class for creating unit tests
import importlib                   # Import importlib to reload modules during tests (reset state)

class TestSnake(TestCase):         # Define a test class inheriting from unittest.TestCase

    def run_test_from_file(self, test_name):
        test_ok = True                          # Flag to track if the test passed or failed
        msg = ""                                # Message to store error details if test fails
        ui = False                              # Variable to hold the user interface object, initially False
        try:
            importlib.reload(snake)    # Reload the snake module to reset its global variables before each test
            ui = snakelib.SnakeTestInterface(test_name)         # Initialize snake test UI with the test file
            ui.set_animation_speed(1)                           # Set animation speed for the test (slow = 1)
            snake.play_snake(ui)                                # Run the snake game with the test interface
            test_ok = ui.test_succeeded                         # Check if the test succeeded via the interface flag
            if not test_ok:                                     
                ui.raise_err("You quit before the test was over")     # Raise an error if user quit early
        except snakelib._IPyException  as err:
            msg = err.parameter                                    # Capture error message from custom exception
            test_ok = False                                        # Mark test as failed
        if ui:
            ui.snake_interface.root.destroy()                      # Close the UI window to clean up after the test


        self.assertTrue(test_ok,msg)                               # Assert that the test passed; if not, show the error message


    def test_start_correctly(self):
        self.run_test_from_file("tests/start_correctly.txt")        # Run test with initial start conditions

    def test_apple_pos5(self):
        self.run_test_from_file("tests/apple_pos5.txt")             # Test apple spawning at position 5

    def test_apple_pos8(self):
        self.run_test_from_file("tests/apple_pos8.txt")              # Test apple spawning at position 8

    def test_apple_pos10(self):
        self.run_test_from_file("tests/apple_pos10.txt")             # Test apple spawning at position 10

    def test_movesimple(self):
        self.run_test_from_file("tests/movesimple.txt")              # Test simple movement mechanics

    def test_change_dir(self):
        self.run_test_from_file("tests/change_dir.txt")              # Test changing direction logic

    def test_wrap_around(self):
        self.run_test_from_file("tests/wrap_around.txt")             # Test wrap-around movement at edges

    def test_grow(self):
        self.run_test_from_file("tests/grow.txt")                    # Test snake growth after eating apple           

    def test_grow_move(self):
        self.run_test_from_file("tests/grow_move.txt")               # Test growth combined with movement

    def test_game_over(self):
        self.run_test_from_file("tests/game_over.txt")               # Test game over condition detection

    def test_game_over2(self):
        self.run_test_from_file("tests/game_over2.txt")               # Another scenario testing game over

    def test_precisely_does_not_die(self):
        self.run_test_from_file("tests/precisely_does_not_die.txt")    # Test that snake doesn’t die in a tricky case

    def test_long(self):
        self.run_test_from_file("tests/long.txt")                      # Run a longer, more comprehensive test

    def test_very_long(self):
        self.run_test_from_file("tests/very_long.txt")                 # Run a very long and complex test
