# Required for formatting text
import textwrap
import sys

#Fixme: FIXME: messy import structure, to be cleaned
import threading
import time
import tkinter

# Constants representing different cell types in the game
EMPTY = 0
FOOD = 1
SNAKE = 2
WALL = 3

import tkinter as _tk
import tkinter.dialog as _Dialog
import tkinter.filedialog as _tkFileDialog
import tkinter.messagebox as _tkMessageBox
import queue as _Queue
import threading as _threading
import time as _time
import os as _os
import random as _random
import sys as _sys
import datetime as _datetime
import pickle as _pickle
import urllib.request, urllib.error, urllib.parse, urllib.error
import json

from abc import ABC, abstractmethod

# Custom exception class

class _IPyException(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)
	    
# Input validation helper functions

def _verify_int(value_var, string_var, minimum=None, maximum=None):
     # Check if value is an int and within optional bounds	
    if not isinstance(value_var, int):
        value = "%s not an int for %s, got %s" % (value_var, string_var, str(type(value_var))[1:-1])
        raise _IPyException(value)
    _verify_input(value_var, string_var, minimum, maximum)


def _verify_float(value_var, string_var, minimum=None, maximum=None):
    # Check if value is a float (or int) and within bounds
    if not isinstance(value_var, float):
        if not isinstance(value_var, int):
            value = "%s is not a float or int for %s, got %s" % (value_var, string_var, str(type(value_var))[1:-1])
            raise _IPyException(value)
    _verify_input(value_var, string_var, minimum, maximum)


def _verify_str(value_var, string_var):
    # Check if value is a string
    if not isinstance(value_var, str):
        value = "%s is not a string for %s, got %s" % (value_var, string_var, str(type(value_var))[1:-1])
        raise _IPyException(value)


def _verify_bool(value_var, string_var):
    # Check if value is a boolean
    if not isinstance(value_var, bool):
        value = "%s is not a boolean for %s, got %s" % (value_var, string_var, str(type(value_var))[1:-1])
        raise _IPyException(value)


def _verify_input(value_var, string_var, minimum=None, maximum=None):
    # Check if value is within the specified bounds
    if minimum is None:
        minimum = float('-inf')
    if maximum is None:
        maximum = float('inf')
    if value_var >= minimum:
        if value_var <= maximum:
            return
    value = "%s is out of bounds, expected range: %s to %s, got: %s" % (string_var, minimum, maximum, value_var)
    raise _IPyException(value)

# A class to initialize the tkinter UI in hidden mode
class _Factory():
    def __init__(self):
        self.mainroot = _tk.Tk()    # Create main Tkinter root
        self.mainroot.withdraw()    # Hide the main window
        self.mainroot.update()      # Update the hidden root

# A file input dialog that sets stdin to the selected file
class _AskInput(object):
    def __init__(self, mainroot):
        root = _tk.Toplevel(mainroot)         # Create a new top-level window
        root.withdraw()                       # Hide it
        self.f = _tkFileDialog.askopenfilename(parent=root)  # Show open file dialog
        if self.f != '':    
            _sys.stdin = open(self.f)           # Redirect stdin to the selected file
        root.destroy()                          # Destroy dialog window

# A dialog box asking user a question with multiple options
class _AskUser(object):
    def __init__(self, mainroot, question, options):
        root = _tk.Toplevel(mainroot)
        root.withdraw()
        dg = _Dialog.Dialog(None,
                            title="",
                            text=question,
                            default=0,
                            bitmap=_tkMessageBox.QUESTION,
                            strings=options)
        self.answer = options[dg.num]      # Store user's answer
        root.destroy()

# Instantiate the hidden UI once for use across the app
_ui_factory = _Factory()

# Reads a full snake game run from a file and returns metadata and all frames
def read_snake_run(file_name):
    with open(file_name) as f:
        # ignore "Width" "Height"
        hint = f.readline()   # First line is a comment or hint

	# Second line: extract width and height of the board
        [_, width, _, height] = f.readline().split()
        width = int(width)
        height = int(height)

	# Third line: optional apple spot (or 0 if not defined)
	    
        line = f.readline()
        if line.startswith("apple"):
            [_, apple_spot] = line.split()
            apple_spot = int(apple_spot)
        else:
            apple_spot = 0
        has_more = True
        frames = []

	# Read all frames until EOF
        while has_more:
            frame = read_snake_frame(width, height, f)  # Read one frame
            frames.append(frame)
            # # Detect if more frames exist: 2 empty lines separate frames
            # readline gives '' for EOF
            c = f.readline()
            has_more = c.endswith("\n")
            if has_more:
                c = f.readline()
                has_more = c.endswith("\n")

    return hint, apple_spot, (width, height), frames

# Reads a single animation frame
def read_snake_frame(width, height, f):
    events = read_events(f)                # First, read the event section
    board = read_board(width, height, f)   # Then, read the board/grid state 
    return (events, board)

# Reads events from the file until "---" is found
def read_events(f):
    event_line = f.readline().strip()
    events = []
    while not (event_line == "---"):
        if event_line.startswith("apple_spot"):
            [_, apple_pick] = event_line.split()
            events.append(("apple_spot", int(apple_pick)))  # Add apple event
        else:
            [event_name, data] = event_line.split(':')
            events.append((event_name, data))               # Add other event types

        event_line = f.readline()
        event_line = event_line.strip()                 # Read next event line
    return events


# Reads a 2D board/grid of width x height
def read_board(width, height, f):
    board = []
    for y in range(height):
        line = f.readline().strip()
        if line == "GameOver":
            return "GameOver"          # Return game over signal
        grid_line = []
        for x in range(width):
            grid_line.append(ascii_to_cell_type(line[x]))      # Convert char to cell type
        board.append(grid_line)                 # Add row to board
    return board

# Function to convert an ASCII character to a cell type constant
def ascii_to_cell_type(c):
    if c == 'A':
        return FOOD         # 'A' represents FOOD
    elif c == 'X':
        return SNAKE        # 'X' represents part of the SNAKE
    elif c == '=':
        return WALL         # '=' represents a WALL
    else:
        return EMPTY        # Any other character is treated as EMPTY space

# Function to convert a cell type constant back to an ASCII character
def cell_type_to_ascii(cell_type):
    if cell_type == FOOD:
        return 'A'                 # FOOD is shown as 'A'
    elif cell_type == SNAKE:
        return 'X'                 # SNAKE is shown as 'X'
    else:
        return '.'                 # All others (WALL or EMPTY) are shown as '.'

# Abstract Base Class for Snake Interface
class SnakeInterface(ABC):

    def __init__(self):
	# Initialize constants from the _Snake class
        self.EMPTY = _Snake.EMPTY
        self.FOOD = _Snake.FOOD
        self.SNAKE = _Snake.SNAKE
        self.WALL = _Snake.WALL

    @abstractmethod
    def board_size(self):
        """Returns the board size as tuple (width,height)"""

    @abstractmethod
    def place(self, x, y, color):
        """Place a Snake piece (defined by 'color') on the given X and Y coordinates.
        """
        pass

    @abstractmethod
    def place_transparent(self, x, y, color):
        """Place a semi-transparent Snake piece (defined by 'color') on the given X and Y coordinates.
        """
        pass

    @abstractmethod
    def clear(self):
        """Clears the display.
        Note: this does not clear the text area!
        """
        pass

    @abstractmethod
    def show(self):
        """Show the changes made to the display (i.e. after calling place or clear)
        """
        pass

    @abstractmethod
    def get_event(self):
        """Returns an event generated from the display.
        The returned object has 2 properties:
        - name: holds the group which the event belongs to.
        - data: holds useful information for the user.
        """
        pass

    @abstractmethod
    def set_animation_speed(self, fps):
        """Set an event to repeat 'fps' times per second.
        If the value is set to 0 or less, the repeating will halt.
        In theory the maximum value is 1000, but this depends on activity of the system.

        The generated events (available by using get_event) have these properties:
        - name: 'alarm'.
        - data: 'refresh'.
        """
        pass

    @abstractmethod
    def print_(self, text):
        """Print text to the text area on the display.
        This function does not add a trailing newline by itself.
        """
        pass

    @abstractmethod
    def clear_text(self):
        """Clears the text area on the display.
        """
        pass

    @abstractmethod
    def wait(self, ms):
        """Let your program wait for an amount of milliseconds.

        This function only guarantees that it will wait at least this amount of time.
        If the system, i.e., is too busy, then this time might increase.
        - Python time module.
        """
        pass

    def random(self, maximum):
        """Picks a random integer ranging from 0 <= x < maximum
        Minimum for maximum is 1
        """
        return random.randrange(maximum)

    @abstractmethod
    def set_game_over(self):
        """Display the game over screen"""
        pass

    @abstractmethod
    def close(self):
        """Closes the display and stops your program.
        """
        pass

    @abstractmethod
    def stay_open(self):
        """Force the window to remain open.
        Only has effect on Mac OS to prevent the window from closing after the execution finishes.

        Make sure that this is the last statement you call when including it because the code does NOT continue after this.
        """
        pass


class SnakeTestInterface(SnakeInterface):
    def __init__(self, test_filename):
        super().__init__()
	# Read the test file and extract game parameters
        hint, self.next_random, (self.width, self.height), self.frames = read_snake_run(test_filename)

	# Initialize the current board with empty cells
        self.cur_board = [[EMPTY for x in range(self.width)] for y in range(self.height)]
        (self.events, self.want_board) = self.frames[0] # Get initial frame's events and expected board
        self.frames = self.frames[1:]                    # Remaining frames after the first


        self.error_msg = ""                              # Collects debugging messages for errors        
        if hint != "":                                   # Add hint (if any) to the error message
            wrapped_hint = textwrap.fill("Hint: " + hint, width=80)
            self.error_msg += wrapped_hint + "\n\n"

        self.error_msg += "apple_spot " + str(self.next_random) + "\n"      # Record the next expected random apple spot
        self.test_succeeded = False
        self.game_over = False
        width = self.width
        height = self.height
        scale = 3

	# Validate dimensions and scale
        _verify_int(width, "Width", 1)
        _verify_int(height, "Height", 1)
        _verify_float(scale, 'Scale', 0.25, 4.0)
        global _ui_factory                             # UI initialization
        self.fps = 1                                   # Frames per second for animation
        self.pause = False
        self.current_frame = 0
        self.snake_interface = _Snake(width * 2 + 2, height + 1, _ui_factory.mainroot, scale, "Student Snake")        # Initialize the snake UI for testing
	# Provide usage instructions
        self.snake_interface.print_("Please refrain from spamming any keys, only press one key per frame\n")
        self.snake_interface.print_("Press [SPACEBAR] to pause the simulation\n")
        self.snake_interface.print_("Press [ARROW LEFT] to go back one step\n")
        self.snake_interface.print_("Press [ARROW RIGHT] to go forward step(only works if you already went back)\n")
        self.snake_interface.print_("Press [ARROW UP] to speed up the animation\n")
        self.snake_interface.print_("Press [ARROW DOWN] to slow down the animation\n")


    def fill_boards(self):
	# Display the student and reference board labels
        text1 = tkinter.Label(self.snake_interface.root, text="Student Snake")
        text2 = tkinter.Label(self.snake_interface.root, text="Reference Snake")
        text1.place(x=0, y=0)
        text2.place(x=(self.width + 2) * self.snake_interface.size_per_coord, y=0)
	# Draw borders between the student and reference boards
        self.snake_interface.place(0 + self.width, 0, self.snake_interface.WALL)
        self.snake_interface.place(1 + self.width, 0, self.snake_interface.WALL)
        [self.snake_interface.place(a, 0, self.snake_interface.WALL) for a in range(self.width * 2 + 2)]

	# Draw the expected board (reference)
        for y in range(len(self.want_board)):
            self.snake_interface.place(0 + self.width, y + 1, self.snake_interface.WALL)
            self.snake_interface.place(1 + self.width, y + 1, self.snake_interface.WALL)
            for x in range(len(self.want_board[y])):
                self.print_(str((x, y)))
                self.snake_interface.place(x + 2 + self.width, y + 1, self.want_board[y][x])
	 # Draw the current student board
        for y in range(len(self.cur_board)):
            self.snake_interface.place(0 + self.width, y, self.snake_interface.WALL)
            self.snake_interface.place(1 + self.width, y, self.snake_interface.WALL)
            for x in range(len(self.cur_board[y])):
                self.print_(str((x, y)))
                self.snake_interface.place(x, y + 1, self.cur_board[y][x])

    def board_size(self):
        return self.width, self.height

    def place(self, x, y, color):
	# Place a cell in the student board and update the UI
        _verify_int(x, 'X', 0, self.snake_interface.width - 1)
        _verify_int(y, 'Y', 0, self.snake_interface.height - 1)
        # 0 = empty, 1 = food, 2 = snake, 3 = wall, 4 = food_t, 5 = snake_t, 6 = wall_t
        _verify_int(color, 'Color', 0, 6)
        self.snake_interface.place(x, y + 1, color)
        self.cur_board[y][x] = color

    def place_transparent(self, x, y, color):
	# Place a semi-transparent version of the object (for animations)
        _verify_int(x, 'X', 0, self.snake_interface.width - 1)
        _verify_int(y, 'Y', 0, self.snake_interface.height - 1)
        # 0 = empty, 1 = food_t, 2 = snake_t, 3 = wall_t (before next step in code)
        _verify_int(color, 'Color', 0, 6)
        if color == self.EMPTY:
            self.place(x, y, self.EMPTY)
        else:
            self.place(x, y, color + 3)
        self.snake_interface.clear()

    def clear(self):                         # Clear the board and reset to empty
        self.snake_interface.clear()
        self.cur_board = [[EMPTY for x in range(self.width)] for y in range(self.height)]

    def printerr(self, s, end='\n'):         # Append an error/debug message
        self.error_msg += s + end

    def raise_err(self, message):            # Raise an error with detailed message
        raise _IPyException(message + "\n\n" + self.error_msg)

    def show(self):                          # Compare the current board to the expected board and show UI
        self.fill_boards()
        self.snake_interface.show()
        if self.test_succeeded:
            return
        self.printerr("---")

        def print_line(line):                # Helper to print a board line
            for c in line:
                self.printerr(cell_type_to_ascii(c), end='')

        if self.game_over and self.want_board != "GameOver":                        # Compare expected vs actual board states with error handling
            self.printerr("Want".ljust(self.width) + " " + "Got".ljust(self.width))
            print_line(self.want_board[0])
            self.printerr(" ", end='')
            self.printerr("GameOver".ljust(self.width), end="")
            self.printerr("")
            for i in range(self.height - 1):
                print_line(self.want_board[i + 1])
                self.printerr("")
            raise _IPyException("You indicated game over, but the game was not over.\n\n" + self.error_msg)
        elif (not self.game_over) and self.want_board == "GameOver":
            width = max(self.width, len("GameOver"))
            self.printerr("Want".ljust(width) + " " + "Got".ljust(self.width))
            self.printerr("GameOver".ljust(width), end="")
            self.printerr(" ", end='')
            print_line(self.cur_board[0])
            self.printerr("")
            for i in range(self.height - 1):
                self.printerr(" ".ljust(width), end="")
                self.printerr(" ", end='')
                print_line(self.cur_board[i + 1])
                self.printerr("")
            raise _IPyException("The game was over, but you did not did not indicate so.\n\n" + self.error_msg)
        elif self.game_over and self.want_board == "GameOver":
            self.printerr("Want".ljust(self.width) + " " + "Got".ljust(self.width))
            self.printerr("GameOver".ljust(self.width) + " " + "GameOver".ljust(self.width), end="")
        else:
            self.printerr("Want".ljust(self.width) + " " + "Got".ljust(self.width))
            for i in range(self.height):
                print_line(self.want_board[i])
                self.printerr(" ", end='')
                print_line(self.cur_board[i])
                self.printerr("")

            if self.cur_board != self.want_board:
                raise _IPyException("Did not get the correct board!\n\n" + self.error_msg)
        self.printerr("")
	    
        # Advance to next frame if any
        if self.frames == []:
            self.test_succeeded = True
            return

        if self.events == []:
            (self.events, self.want_board) = self.frames[0]
            self.frame_history += [(self.cur_board, self.want_board)]
            self.frames = self.frames[1:]
        time.sleep(self.snake_interface.interval * 0.001)

    def get_event(self):
	    # Handle input and step logic
        keyboard_event = self.snake_interface.get_event()
        if keyboard_event.name.strip() == "arrow" and keyboard_event.data.strip() == "u":
            self.set_animation_speed(min(20, self.fps + 1))
        elif keyboard_event.name.strip() == "arrow" and keyboard_event.data.strip() == "d":
            self.set_animation_speed(max(1, self.fps - 1))
        elif keyboard_event.name.strip() == "arrow" and keyboard_event.data.strip() == "l":
            if len(self.frame_history) > 2 and len(self.frame_history) + self.current_frame > 2:
                self.current_frame -= 1
                self.cur_board = self.frame_history[self.current_frame - 1][0]
                self.want_board = self.frame_history[self.current_frame - 2][1]
        elif keyboard_event.name.strip() == "arrow" and keyboard_event.data.strip() == "r":
            if self.current_frame < 0:
                self.current_frame += 1
                self.cur_board = self.frame_history[self.current_frame - 1][0]
                self.want_board = self.frame_history[self.current_frame - 2][1]
        elif keyboard_event.name.strip() == "other" and keyboard_event.data.strip() == "space":
            self.pause = not self.pause
        if self.pause or self.current_frame < 0:
            self.want_board = self.frame_history[self.current_frame - 2][1]
            self.fill_boards()
            self.snake_interface.show()
            return Event("", "")           # Return a no-op event while paused
        if len(self.frame_history) > 0:
            self.want_board = self.frame_history[-1][1]
        if not self.events:
            if len(self.frames) == 0:
                return Event("quit", "")
            else:
                raise _IPyException("Forgot to call ui.show() before first get_event or forgot to call show after alarm : refresh\n\n" + self.error_msg)
        else:                 # Process next event
            event = self.events[0]
            if event[0].strip() == "apple_spot":
                self.next_random = event[1]
                self.events = self.events[1:]
                event = self.events[0]
                self.printerr("apple_spot " + str(self.next_random))
            self.events = self.events[1:]
            self.printerr(event[0] + " " + event[1])
            return Event(event[0].strip(), event[1].strip())
		
    # Utility methods used in the UI logic of the Snake game
    def set_game_over(self):   
	# Sets the game as over and updates the UI accordingly
        self.game_over = True
        self.snake_interface.set_game_over()

    def set_animation_speed(self, fps):
	 # Sets the frame rate (animation speed) for the game loop
        self.fps = fps
        _verify_float(fps, "Animation speed")
        self.snake_interface.set_animation_speed(fps)

    def print_(self, text):     # Override for printing messages (used in some interfaces)
        pass

    def clear_text(self):       # Override to clear text from a display area
        pass

    def wait(self, ms):         # Override for waiting a number of milliseconds
        pass

    def random(self, maximum):             # Deterministically returns a value using next_random (mocking randomness)
        return self.next_random % maximum

    def close(self):            # Override for closing the interface
        pass

    def stay_open(self):        # Override to keep the interface open         
        pass


class SnakeUserInterface(SnakeInterface):
    def __init__(self, width, height, scale=1.0):
        """This class starts the SnakeUserInterface.
		Constants:
		- EMPTY
		- FOOD
		- SNAKE
		- WALL

		Parameters for the class:
		- width: at least 1
		- height: at least 1

		Optional parameters:
		- scale: 0.25 to 1.0
		"""
        super().__init__()
        _verify_int(width, "Width", 1)
        _verify_int(height, "Height", 1)
        _verify_float(scale, 'Scale', 0.25, 1.0)
        global _ui_factory
        self.snake_interface = _Snake(width, height, _ui_factory.mainroot, scale)
	# Read test scenario data
        hint, self.next_random, (self.width, self.height), self.frames = read_snake_run(test_filename)           
        self.cur_board = [[EMPTY for x in range(self.width)] for y in range(self.height)]
        (self.events, self.want_board) = self.frames[0]
        self.frames = self.frames[1:]

	# Error hint and status flags
        self.error_msg = ""
        if hint != "":
            wrapped_hint = textwrap.fill("Hint: " + hint, width=80)
            self.error_msg += wrapped_hint + "\n\n"

        self.error_msg += "apple_spot " + str(self.next_random) + "\n"
        self.test_succeeded = False
        self.game_over = False

    def board_size(self):                                                  # Returns the width and height of the board
        return self.width, self.height

    def set_game_over(self):                                               # Marks the game as over
        self.game_over = True
        self.snake_interface.set_game_over()

    def place(self, x, y, color):
        """Place a Snake piece (defined by 'color') on the given X and Y coordinates.
		"""

        self.cur_board[y][x] = color
        _verify_int(x, 'X', 0, self.snake_interface.width - 1)
        _verify_int(y, 'Y', 0, self.snake_interface.height - 1)
        # 0 = empty, 1 = food, 2 = snake, 3 = wall, 4 = food_t, 5 = snake_t, 6 = wall_t
        _verify_int(color, 'Color', 0, 6)
        self.snake_interface.place(x, y, color)

    def place_transparent(self, x, y, color):
        """Place a semi-transparent Snake piece (defined by 'color') on the given X and Y coordinates.
		"""

        _verify_int(x, 'X', 0, self.snake_interface.width - 1)
        _verify_int(y, 'Y', 0, self.snake_interface.height - 1)
        # 0 = empty, 1 = food_t, 2 = snake_t, 3 = wall_t (before next step in code)
        _verify_int(color, 'Color', 0, 6)
        if color == self.EMPTY:
            self.place(x, y, self.EMPTY)
        else:
            self.place(x, y, color + 3)

    def clear(self):
        """Clears the display.
		Note: this does not clear the text area!
		"""
        self.cur_board = [[EMPTY for x in range(self.width)] for y in range(self.height)]
        self.snake_interface.clear()

    def show(self):
        """Show the changes made to the display (i.e. after calling place or clear)
		"""

        self.snake_interface.show()

    def get_event(self):
        """Returns an event generated from the display.
		The returned object has 2 properties:
		- name: holds the group which the event belongs to.
		- data: holds useful information for the user.
		"""
        if self.events == []:
            if len(self.frames) == 0:
                return Event("quit", "")
            else:
                raise _IPyException("Forgot to call ui.show() before first get_event or forgot to call show after alarm : refresh\n\n" + self.error_msg)
        else:
            event = self.events[0]
            if event[0].strip() == "apple_spot":
                self.next_random = event[1]
                self.events = self.events[1:]
                event = self.events[0]
                self.printerr("apple_spot " + str(self.next_random))
            self.events = self.events[1:]
            self.printerr(event[0] + " " + event[1])
            return Event(event[0].strip(), event[1].strip())
        #return self.snake_interface.get_event()

    def set_animation_speed(self, fps):
        """Set an event to repeat 'fps' times per second.
		If the value is set to 0 or less, the repeating will halt.
		In theory the maximum value is 1000, but this depends on activity of the system.

		The generated events (available by using get_event) have these properties:
		- name: 'alarm'.
		- data: 'refresh'.
		"""

        _verify_float(fps, "Animation speed")
        self.snake_interface.set_animation_speed(fps)

    def print_(self, text):
        """Print text to the text area on the display.
		This function does not add a trailing newline by itself.
		"""

        _verify_str(text, "Text")
        self.snake_interface.print_(text)

    def clear_text(self):
        """Clears the text area on the display.
		"""

        self.snake_interface.clear_text()

    def wait(self, ms):
        """Let your program wait for an amount of milliseconds.

		This function only guarantees that it will wait at least this amount of time.
		If the system, i.e., is too busy, then this time might increase.
		- Python time module.
		"""

        _verify_int(ms, "Waiting time", 0)
        self.snake_interface.wait(ms)

    def random(self, maximum):
        """Picks a random integer ranging from 0 <= x < maximum
		Minimum for maximum is 1
		"""

        return self.next_random % maximum

    def close(self):
        """Closes the display and stops your program.
		"""

        self.snake_interface.close()

    def stay_open(self):
        """Force the window to remain open.
		Only has effect on Mac OS to prevent the window from closing after the execution finishes.

		Make sure that this is the last statement you call when including it because the code does NOT continue after this.
		"""

        global _ui_factory
        _ui_factory.mainroot.mainloop()


class Event(object):
    def __init__(self, name, data):
        """This class holds the name and data for each event in their respective variables.
		Variables:
		- name
		- data

		Example to access with SnakeUserInterface:

		ui = SnakeUserInterface(5,5) # 5 by 5 grid for testing purposes
		your_variable = ui.get_event() # code will block untill an event comes
		# your_variable now points to an event
		print your_variable.name, your_variable.data

		List of events:
		- name: mouseover
		  data: x and y coordinates (as integers), separated by a space
			  generated when mouse goes over a coordinate on the window
		- name: mouseexit
		  data: x and y coordinates (as integers), separated by a space
			  generated when mouse exits a coordinate on the window
		- name: click
		  data: x and y coordinates (as integers), separated by a space
			  generated when the user clicks on a coordinate on the window
		- name: alarm
		  data: refresh
			  generated as often per second as the user set the animation speed to; note that the data is exactly as it says: "refresh"
		- name: letter
		  data: the letter that got pressed
			  generated when the user presses on a letter (A to Z; can be lowercase or uppercase depending on shift/caps lock)
		- name: number
		  data: the number (as a string) that got pressed
			  generated when the user presses on a number (0 to 9)
		- name: alt_number
		  data: the number (as a string) that got pressed
			  generated when the user presses on a number (0 to 9) while at the same time pressing the Alt key
		- name: arrow
		  data: the arrow key that got pressed, given by a single letter
			  generated when the user presses on an arrow key, data is then one of: l, r, u, d
		- name: other
		  data: data depends on key pressed
			  generated when the user pressed a different key than those described above
			  possible data:
			  - caps_lock
			  - num_lock
			  - alt
			  - control
			  - shift
			  more data can exist and are recorded (read: they generate events), but not documented
		"""
        self.name = name
        self.data = data

    # Return a user-friendly string representation of the object
    def __str__(self):
        return self.name + " : " + self.data

    # Return an unambiguous string representation of the object
    def __repr__(self):
        return self.name + " : " + self.data

# A simple holder class for snake body parts or visual elements, storing their coordinates and color
class _SnakeHolder(object):
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color


class _Snake(object):
    # one cannot prevent users from editing 'constants', as constants simply do not exist in Python
    EMPTY = 0
    FOOD = 1
    SNAKE = 2
    WALL = 3

    def __init__(self, width, height, mainroot, scale=1.0, title="SnakeUserInterface"):
        # create queue to store changes to placings
        self.to_show_queue = _Queue.Queue(maxsize=0)
        self.event_queue = _Queue.Queue(maxsize=0)

        # copy params  (# Game configuration)
        self.width = width
        self.height = height
        self.scale = scale
        self.game_over = False

        self.closing_window = False

        # start the main window
        self.root = _tk.Toplevel(mainroot)
        self.root.title(title)
        self.root.protocol("WM_DELETE_WINDOW", self.callback)    # Handle window close
        self.root.bind("<Escape>", self.callback)                # Handle Esc key to exit
        self.root.resizable(False, False)

        # calculate sizes
        self.size_per_coord = int(25 * scale)
        self.text_height = int(100 * scale)

        # create main frame
        self.frame = _tk.Frame(self.root, width=self.size_per_coord * self.width,
                               height=self.size_per_coord * self.height + self.text_height)
        self.frame.pack_propagate(0)
        self.frame.pack()

        # create board to hold references to snake-pieces
        self.food_board = []  # for storing references to create_image
        self.snake_board = []
        self.wall_board = []
        self.food_ghost_board = []
        self.snake_ghost_board = []
        self.wall_ghost_board = []
        self.img_refs = []  # for storing references to images - order: food, snake, wall, food_t, snake_t, wall_t
        self.canvas_width = self.size_per_coord * self.width
        self.canvas_height = self.size_per_coord * self.height
        # create and fill the canvas --> paintable area
        self.c = _tk.Canvas(self.frame, width=self.canvas_width,
                            height=self.canvas_height, bg="black", bd=0, highlightthickness=0)
        self.c.pack()
        self.last_x = -1  # used to generate mouseOver/Exit events
        self.last_y = -1  # used to generate mouseOver/Exit events
        self.fill_canvas()

        # create the textholder
        self.scrollbar = _tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=_tk.RIGHT, fill=_tk.Y)
        self.textarea = _tk.Text(self.frame, yscrollcommand=self.scrollbar.set)
        self.textarea.pack(side=_tk.LEFT, fill=_tk.BOTH)
        self.scrollbar.config(command=self.textarea.yview)
        self.textarea.config(state=_tk.DISABLED)

	# Initialize timer and animation settings
        self.interval = 0
        self.alarm_speed = 0
        self.timer = self.milliseconds()

	 # Update main Tk root window
        global _ui_factory
        _ui_factory.mainroot.update()

    # Sets the game over flag to True
    def set_game_over(self):
        self.game_over = True

    # Callback function to close the window and exit the application
    def callback(self, event=None):
        self.root.destroy()
        _os._exit(0)

    # Returns current time in milliseconds
    def milliseconds(self):
        return _time.time() * 1000

    # Places food, snake on the canvas at position (x, y)
    def place(self, x, y, color):
        element = _SnakeHolder(x, y, color)
        self.to_show_queue.put(element)

    # Clears the entire canvas by filling it with empty cells
    def clear(self):
        for x in range(self.width):
            for y in range(self.height):
                self.place(x, y, self.EMPTY)
		    
    # Displays queued elements on the canvas, respecting layering and visibility
    def show(self):
        try:
            if self.game_over:
                self.c.create_text(self.canvas_width / 2, self.canvas_height / 2, fill="red", text="Game over!")
                return
            while True:
                element = self.to_show_queue.get_nowait()
                position = []
                position.append(self.food_board[element.x][element.y])
                position.append(self.snake_board[element.x][element.y])
                position.append(self.wall_board[element.x][element.y])
                position.append(self.food_ghost_board[element.x][element.y])
                position.append(self.snake_ghost_board[element.x][element.y])
                position.append(self.wall_ghost_board[element.x][element.y])
                for i in range(len(position)):
                    # add 1 to i, because 0 is empty [same as doing color - 1]
                    # thus, if 0, then it doesn't match with 1 to 6
                    # therefore putting the whole position to hidden
                    if element.color == i + 1:                             # Show only the element matching the color index
                        for e in position[i]:
                            self.c.itemconfig(e, state=_tk.NORMAL)
                    else:
                        for e in position[i]:
                            self.c.itemconfig(e, state=_tk.HIDDEN)

        except _Queue.Empty:
            pass
        global _ui_factory
        _ui_factory.mainroot.update()

     # Waits for and returns the next input event from the queue
    def get_event(self):
        global _ui_factory
        _ui_factory.mainroot.update()
        while True:
            try:
                self.refresh_event()
                event = self.event_queue.get_nowait()
                return event
            except _Queue.Empty:
                wait_time = min(self.interval, 10)
                self.wait(wait_time)
                _ui_factory.mainroot.update()

    # Sets the animation speed by defining frame interval based on FPS
    def set_animation_speed(self, fps):
        current_time = self.milliseconds()
        if fps <= 0:
            self.interval = 0
            self.timer = current_time
            return
        if fps > 1000:
            fps = 1000
        self.interval = int(1000.0 / fps)
        self.refresh_event()

    # Prints text to the text area in the UI
    def print_(self, text):
        self.textarea.config(state=_tk.NORMAL)
        self.textarea.insert(_tk.END, text)
        self.textarea.see(_tk.END)
        self.textarea.config(state=_tk.DISABLED)
        global _ui_factory
        _ui_factory.mainroot.update()

    # Clears the text output area
    def clear_text(self):
        self.textarea.config(state=_tk.NORMAL)
        self.textarea.delete(1.0, _tk.END)
        self.textarea.see(_tk.END)
        self.textarea.config(state=_tk.DISABLED)
        global _ui_factory
        _ui_factory.mainroot.update()

     # Sleeps for a given number of milliseconds
    def wait(self, ms):
        try:
            _time.sleep(ms * 0.001)
        except:
            self.close()

    # Closes the GUI window and exits the program
    def close(self):
        self.root.destroy()
        _os._exit(0)

    # Returns a random integer less than the given maximum
    def random(self, maximum=1):
        return int(_random.random() * maximum)

    # Creates canvas elements representing game pieces based on type and position
    def create_piece(self, x0, y0, img, mix):
        result = []
        if img == self.FOOD:                            # Create food graphics with green top and red body
            r = int(255 / (1 + mix))
            g = int(64 / (1 + mix))
            b = int(64 / (1 + mix))
            scale = 0.8
            x1 = x0 + (1.0 - scale) / 2.0 * self.size_per_coord
            y1 = y0 + (1.0 - scale) * self.size_per_coord
            x2 = x0 + (1.0 - (1.0 - scale) / 2.0) * self.size_per_coord
            y2 = y0 + self.size_per_coord
            result.append(
                self.c.create_oval(x1, y1, x2, y2, state=_tk.HIDDEN, fill="#%02X%02X%02X" % (r, g, b), width=0))
            r = int(64 / (1 + mix))
            g = int(255 / (1 + mix))
            b = int(64 / (1 + mix))
            scale = 0.4
            x1 = x0 + self.size_per_coord / 2.0
            y1 = y0
            x2 = x1
            y2 = y0 + scale * self.size_per_coord
            result.append(
                self.c.create_line(x1, y1, x2, y2, state=_tk.HIDDEN, fill="#%02X%02X%02X" % (r, g, b), width=2))
        if img == self.SNAKE:                                                     # Create a snake body segment
            r = int(32 / (1 + mix))
            g = int(255 / (1 + mix))
            b = int(0 / (1 + mix))
            x1 = x0
            y1 = y0
            x2 = x0 + self.size_per_coord
            y2 = y0 + self.size_per_coord
            result.append(
                self.c.create_oval(x1, y1, x2, y2, state=_tk.HIDDEN, fill="#%02X%02X%02X" % (r, g, b), width=0))
        if img == self.WALL:                                  # Create a wall segment
            r = int(200 / (1 + mix))
            g = int(100 / (1 + mix))
            b = int(0 / (1 + mix))
            x1 = x0
            y1 = y0
            x2 = x0 + self.size_per_coord
            y2 = y0 + self.size_per_coord
            result.append(
                self.c.create_rectangle(x1, y1, x2, y2, state=_tk.HIDDEN, fill="#%02X%02X%02X" % (r, g, b), width=0))

        return result

    # Initializes visual representations of snake, food, and walls
    def create_snake_pieces(self):
        mixer = 0, 0, 0, 1, 1, 1
        imgtype = self.FOOD, self.SNAKE, self.WALL, self.FOOD, self.SNAKE, self.WALL
        boards = self.food_board, self.snake_board, self.wall_board, self.food_ghost_board, self.snake_ghost_board, self.wall_ghost_board
        for n in range(len(boards)):
            for i in range(self.width):
                boards[n].append([])
                for j in range(self.height):
                    x0 = self.size_per_coord * i
                    y0 = self.size_per_coord * j
                    img = self.create_piece(x0, y0, imgtype[n], mixer[n])
                    boards[n][i].append(img)

    # Prepares the canvas by binding events and creating game objects
    def fill_canvas(self):
        self.bind_events()
        self.create_snake_pieces()

    # Handles mouse movement and generates events when the mouse moves over different cells
    def motion_event(self, event):
        if not self.mouse_on_screen:
            return
        x_old = self.last_x
        y_old = self.last_y
        x_new = event.x / self.size_per_coord
        y_new = event.y / self.size_per_coord
        x_change = int(x_old) != int(x_new)
        y_change = int(y_old) != int(y_new)
        if x_change or y_change:
            self.generate_event("mouseexit", "%d %d" % (x_old, y_old))
            self.generate_event("mouseover", "%d %d" % (x_new, y_new))
            self.last_x = x_new
            self.last_y = y_new

    # Handles when the mouse enters the game canvas
    def enter_window_event(self, event):
        x_new = event.x / self.size_per_coord
        y_new = event.y / self.size_per_coord
        self.generate_event("mouseover", "%d %d" % (x_new, y_new))
        self.last_x = x_new
        self.last_y = y_new
        self.mouse_on_screen = True

    # Handles when the mouse leaves the canvas
    def leave_window_event(self, event):
        self.generate_event("mouseexit", "%d %d" % (self.last_x, self.last_y))
        self.mouse_on_screen = False

     # Handles Alt+number key events
    def alt_number_event(self, event):
        if event.char == event.keysym:
            if ord(event.char) >= ord('0') and ord(event.char) <= ord('9'):
                self.generate_event("alt_number", event.char)

    # Processes keyboard input and generates corresponding events
    def key_event(self, event):
        if event.char == event.keysym:
            if ord(event.char) >= ord('0') and ord(event.char) <= ord('9'):
                self.generate_event("number", event.char)
            elif ord(event.char) >= ord('a') and ord(event.char) <= ord('z'):
                self.generate_event("letter", event.char)
            elif ord(event.char) >= ord('A') and ord(event.char) <= ord('Z'):
                self.generate_event("letter", event.char)
            else:
                self.generate_event("other", event.char)
        elif event.keysym == 'Up':
            self.generate_event("arrow", "u")
        elif event.keysym == 'Down':
            self.generate_event("arrow", "d")
        elif event.keysym == 'Left':
            self.generate_event("arrow", "l")
        elif event.keysym == 'Right':
            self.generate_event("arrow", "r")
        elif event.keysym == 'Multi_Key':
            return
        elif event.keysym == 'Caps_Lock':
            self.generate_event("other", "caps lock")
        elif event.keysym == 'Num_Lock':
            self.generate_event("other", "num lock")
        elif event.keysym == 'Shift_L' or event.keysym == 'Shift_R':
            self.generate_event("other", "shift")
        elif event.keysym == 'Control_L' or event.keysym == 'Control_R':
            self.generate_event("other", "control")
        elif event.keysym == 'Alt_L' or event.keysym == 'Alt_R':
            self.generate_event("other", "alt")
        else:
            self.generate_event("other", event.keysym)

    # Handles mouse click events and translates them to cell coordinates
    def click_event(self, event):
        x = event.x / self.size_per_coord
        y = event.y / self.size_per_coord
        self.generate_event("click", "%d %d" % (x, y))

     # Generates an "alarm" event if it's time to refresh based on the animation interval
    def refresh_event(self):
        current_time = self.milliseconds()
        threshold = current_time - self.timer - self.interval
        if threshold >= 0 and self.interval > 0:
            self.generate_event("alarm", "refresh")
            self.timer = current_time

     # Adds an event to the event queue
    def generate_event(self, name, data):
        event = Event(name, data)
        self.event_queue.put(event)

    # Binds mouse and keyboard events to the canvas for user interaction
    def bind_events(self):
        self.c.focus_set()  # to redirect keyboard input to this widget
        self.c.bind("<Motion>", self.motion_event)
        self.c.bind("<Enter>", self.enter_window_event)
        self.c.bind("<Leave>", self.leave_window_event)
        self.c.bind("<Alt-Key>", self.alt_number_event)
        self.c.bind("<Key>", self.key_event)
        self.c.bind("<Button-1>", self.click_event)
