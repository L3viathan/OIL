#!/usr/bin/env python3
"""OIL Reference implementation."""
import sys
import re
from os.path import dirname, abspath, join
from collections import defaultdict
from random import randint


class Quit(Exception):
    """Exception used for exiting."""

    pass


class Interpreter(object):
    """OIL interpreter object holding a tape and a head."""
    number = re.compile('^(0|-?[1-9]\d*)$')

    def __init__(self, debug=False):
        """
        Initialize interpreter.

        Set the debug variable, and map numbers to functions, using
        function annotations.
        """
        self.debug = debug
        self.parent = None
        self.codes = {}
        d = type(self).__dict__
        for key in d:
            try:
                num = d[key].__annotations__['return']
                self.codes[num] = d[key]
            except KeyError:
                pass
            except AttributeError:
                pass

    @staticmethod
    def intify(value):
        """Forcibly convert a value to an integer."""
        if type(value) == str:
            if Interpreter.number.match(value):
                return int(value)
            else:
                return 0
        else:
            return value

    def _move_head(self):
        """Advance the head."""
        self.pointer += self.direction

    def _get(self):
        """Get the value currently under the pointer."""
        return self.memory[self.pointer]

    def read_source(self, filename):
        """Read a file into the tape."""
        self.memory = defaultdict(int)
        with open(filename, newline="\n") as f:
            for index, line in enumerate(f):
                if self.debug and "#" in line:
                    line = line.split("#")[0]
                line = line.rstrip("\n")
                if Interpreter.number.match(line):
                    self.memory[index] = int(line)
                else:
                    self.memory[index] = line
        self.path = dirname(filename)

    def nop(self) -> 0:
        """Do nothing."""
        if self.debug:
            print("Nopping")
        self._move_head()

    def copy(self) -> 1:
        """Copy a value from one cell to another."""
        if self.debug:
            print("Copying")
        self._move_head()
        source = self.intify(self._get())
        self._move_head()
        target = self.intify(self._get())
        self.memory[target] = self.memory[source]
        self._move_head()

    def reverse(self) -> 2:
        """Invert the direction of the head movement."""
        if self.debug:
            print("Reversing")
        self.direction *= -1
        self._move_head()

    def quit(self) -> 3:
        """Stop the execution."""
        raise Quit()

    def output(self) -> 4:
        """Print a cell value."""
        if self.debug:
            print("Printing")
        self._move_head()
        cell = self.intify(self._get())
        if self.parent is None:
            print(self.memory[cell], end="", flush=True)
        else:
            self.parent.remote_write(self.memory[cell])
        self._move_head()

    def user_input(self) -> 5:
        """Read a line of input into a cell."""
        if self.debug:
            print("Reading user input")
        self._move_head()
        cell = self.intify(self._get())
        if self.parent is None:
            i = input()
        else:
            i = str(self.parent.remote_read())
        if Interpreter.number.match(i):
            self.memory[cell] = int(i)
        else:
            self.memory[cell] = i
        self._move_head()

    def jump(self) -> 6:
        """Jump to a cell."""
        self._move_head()
        self.pointer = self.intify(self._get())
        if self.debug:
            print("Jumping to", self.pointer)

    def relative_jump(self) -> 7:
        """Jump some number of cells ahead."""
        if self.debug:
            print("Relative jump")
        self._move_head()
        self.pointer = self.direction * self.intify(self._get()) + self.pointer

    def increment(self) -> 8:
        """Increment a given cell."""
        if self.debug:
            print("Incrementing")
        self._move_head()
        cell = self.intify(self._get())
        self.memory[cell] = self.intify(self.memory[cell]) + 1
        self._move_head()

    def decrement(self) -> 9:
        """Decrement a given cell."""
        if self.debug:
            print("Decrementing")
        self._move_head()
        cell = self.intify(self._get())
        self.memory[cell] = self.intify(self.memory[cell]) - 1
        self._move_head()

    def eq_jump(self) -> 10:
        """Check if two cells are equal, then jump accordingly."""
        self._move_head()
        cell1 = self.intify(self._get())
        self._move_head()
        cell2 = self.intify(self._get())
        if self.debug:
            print("Checking equality {} == {} ?".format(self.memory[cell1], self.memory[cell2]))
        if self.memory[cell1] != self.memory[cell2]:
            self._move_head()
        self.jump()

    def newline(self) -> 11:
        """Print a newline character."""
        if self.parent is None:
            print("")
        self._move_head()

    def explode(self) -> 12:
        """
        Break a cell's value into characters.

        Put their length and then the characters in cells starting from a
        given position.
        """
        if self.debug:
            print("Exploding")
        self._move_head()
        source = self.intify(self._get())
        self._move_head()
        target = self.intify(self._get())
        string = str(self.memory[source])
        self.memory[target] = len(string)
        for index, char in enumerate(string):
            if char.isnumeric():
                char = int(char)
            self.memory[target+(index+1)*self.direction] = char
        self._move_head()

    def implode(self) -> 13:
        """
        Join cells into a single one.

        Starting from a given cell and with a given length, join the values
        together in another cell.
        """
        if self.debug:
            print("Imploding")
        self._move_head()
        start = self.intify(self._get())
        self._move_head()
        length = self.intify(self._get())
        self._move_head()
        target = self.intify(self._get())
        if self.debug:
            print("Imploding from {} to {} (length {})".format(start, target, length))
        string = []
        counter = 0
        for pos in range(length):
            string.append(str(self.memory[start+(pos*self.direction)]))
        string = "".join(string)
        if Interpreter.number.match(string):
            string = int(string)
        else:
            pass
        self.memory[target] = string
        self._move_head()

    def call(self) -> 14:
        """Call a different file."""
        self._move_head()
        filename = abspath(join(self.path, str(self._get())))
        if self.debug:
            print("Calling", filename)
        self._move_head()
        self.write_to = self.intify(self._get())
        self._move_head()
        self.read_from = self.intify(self._get())
        try:
            inter = Interpreter()
            inter.remote_setup(self)
            inter.run(filename)
        except:
            pass
        self._move_head()

    def random(self) -> 15:
        """Set a cell to a random value."""
        self._move_head()
        cell = self.intify(self._get())
        self._move_head()
        top = self.intify(self._get())
        if top >= 0:
            self.memory[cell] = randint(0, top)
        self._move_head()

    def ord(self) -> 16:
        """
        Turn a cell's string value into a "list" of unicode codepoints.

        Put their length and then the codepoints in cells starting from a
        given position.
        """
        self._move_head()
        source = self.intify(self._get())
        self._move_head()
        target = self.intify(self._get())
        string = str(self.memory[source])
        self.memory[target] = len(string)
        for index, char in enumerate(string):
            self.memory[target+(index+1)*self.direction] = ord(char)
        self._move_head()

    def chr(self) -> 17:
        """
        Put a list of codepoints into a string

        Starting from a given cell and with a given length, join the values
        together in another cell.
        """
        if self.debug:
            print("Imploding")
        self._move_head()
        start = self.intify(self._get())
        self._move_head()
        length = self.intify(self._get())
        self._move_head()
        target = self.intify(self._get())
        string = []
        counter = 0
        for pos in range(length):
            cp = self.intify(self.memory[start+(pos*self.direction)])
            try:
                string.append(chr(cp))
            except:
                string.append('\ufffd')
        string = "".join(string)
        if Interpreter.number.match(string):
            string = int(string)
        else:
            pass
        self.memory[target] = string
        self._move_head()

    def remote_write(self, value):
        self.memory[self.write_to] = value
        self.write_to += self.direction

    def remote_read(self):
        value = self.memory[self.read_from]
        self.read_from += self.direction
        return value

    def remote_setup(self, parent):
        self.parent = parent

    def step(self):
        """Execute a single step."""
        if self.pointer not in self.memory:
            raise Quit()
        action = self.codes.get(self._get(), Interpreter.nop)
        if self.debug:
            print(self.memory)
            # print([self.memory[i] for i in range(70)])
            print("pointer:", self.pointer)
            #print(action)
        action(self)

    def run(self, filename):
        """Run a script, given its file name."""
        self.pointer = 0
        self.direction = 1
        self.read_source(filename)
        try:
            while True:
                self.step()
        except Quit:
            pass


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if len(sys.argv) > 2:
            debug = True
        else:
            debug = False
        Interpreter(debug=debug).run(filename)
    else:
        print(Interpreter().codes)
