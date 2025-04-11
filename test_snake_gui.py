import time

import snakelib_second as snakelib
import snake
from unittest import TestCase
import importlib

class TestSnake(TestCase):

    def run_test_from_file(self, test_name):
        test_ok = True
        msg = ""
        ui = False
        try:
            importlib.reload(snake) # reset global variables in student file
            ui = snakelib.SnakeTestInterface(test_name)
            ui.set_animation_speed(1)
            snake.play_snake(ui)
            test_ok = ui.test_succeeded
            if not test_ok:
                ui.raise_err("You quit before the test was over")
        except snakelib._IPyException  as err:
            msg = err.parameter
            test_ok = False
        if ui:
            ui.snake_interface.root.destroy()

        self.assertTrue(test_ok,msg)


    def test_start_correctly(self):
        self.run_test_from_file("tests/start_correctly.txt")

    def test_apple_pos5(self):
        self.run_test_from_file("tests/apple_pos5.txt")

    def test_apple_pos8(self):
        self.run_test_from_file("tests/apple_pos8.txt")

    def test_apple_pos10(self):
        self.run_test_from_file("tests/apple_pos10.txt")

    def test_movesimple(self):
        self.run_test_from_file("tests/movesimple.txt")

    def test_change_dir(self):
        self.run_test_from_file("tests/change_dir.txt")

    def test_wrap_around(self):
        self.run_test_from_file("tests/wrap_around.txt")

    def test_grow(self):
        self.run_test_from_file("tests/grow.txt")

    def test_grow_move(self):
        self.run_test_from_file("tests/grow_move.txt")

    def test_game_over(self):
        self.run_test_from_file("tests/game_over.txt")

    def test_game_over2(self):
        self.run_test_from_file("tests/game_over2.txt")

    def test_precisely_does_not_die(self):
        self.run_test_from_file("tests/precisely_does_not_die.txt")

    def test_long(self):
        self.run_test_from_file("tests/long.txt")

    def test_very_long(self):
        self.run_test_from_file("tests/very_long.txt")