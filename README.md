# OIL

_Overly introspective language, version 2.2_

## Usage

    oil.py hello_world.oil

## Reference

A OIL file consists of a number of lines, seperated by newline characters.
In general, any file is a valid OIL file, but most files won't do anything.
The file is read in line-by-line by the interpreter, and the content of each
line is put into a cell on the OIL tape. When the script starts execution, the
tape can be imagined as a continuous sequence of fields, each of which holds
the content of a line, but during execution, more fields can be added at any
integer position.

Lines are parsed by first checking if all characters in the line are digits, in
that case the value of the line is that integer. Otherwise, the value of the
line is a string. The only datatypes are strings and integers. Whenever a string
contains only digits, it becomes an integer.

The OIL tape is equipped with a directional (by default: positive) read-write
head that starts at position 0 (i.e. in the first line). Whenever this
reference talks about _moving to the right_ etc., this has to be replaced by
_moving left_ if the direction got negative (see `reverse`).

The computation is executed in steps. At the beginning of every step, the head
reads the command at its current position. Any values the head reads get
forcibly converted to integers (any non-numeric string becomes 0). The head
then executes the command the integer is linked to (see below). If a number
doesn't have a command assigned to it, it executes the command `nop`. The
commands may instruct the head to move to the right to read further arguments.
At the end of most commands (all except `jump`, `relative_jump`, and
`conditional_jump`, because they move the head manually) the head gets moved to
the right again to be ready to read the next command. This process continues
until either the command `quit` is executed, or the head tries to read a command
from an empty cell. This doesn't apply to the process of reading arguments, or
any other reads done within a command; in that case the value that is read will
be 0 (but the cell will remain empty).

### Commands

The list of commands follows. The labels are purely informative and can not be
used instead of the numbers (they merely denote the names of the corresponding
functions in the reference implementation). The final head movement is ommitted in this list.

- `nop` (0): Do nothing.
- `copy` (1): Advance the head, read argument A, advance the head , read
  argument B. Copy the value from the A<sup>th</sup> cell to the B<sup>th</sup>
  cell.
- `reverse` (2): Reverse the direction; from now on the head moves in the other
direction.
- `quit` (3): Immediately quit the interpreter.
- `output` (4): Advance the head, read argument A. Print the value of
the A<sup>th</sup> cell to stdout.
- `user_input` (5): Advance the head, read argument A. Read a line of user input
  into the A<sup>th</sup> cell.
- `jump` (6): Advance the head, jump to the cell under the head.
- `relative_jump` (7): Advance the head, read argument A, jump A blocks in the
  current direction.
- `increment` (8): Advance the head, read argument A, increment the value in cell
  A.
- `decrement` (9): Advance the head, read argument A, decrement the value in cell
  A.
- `conditional_jump` (10): Advance the head, read argument A. Advance the head,
  read argument B. If the A<sup>th</sup> cell's content is equal to that of
  cell B, advance the head once, otherwise advance the head twice. Now jump to
  the cell under the head.
- `newline` (11): Print a newline character if this is the main script.
  Otherwise behaves like a `nop`.
- `explode` (12): Explode a cell: Advance the head twice, reading the next two
  values (A, B). Convert the value from cell A into a string. Put its length in
  cell B, and each of its characters seperately into cells after B.
- `implode` (13): Implode a string: Advance the head thrice, reading the next
  three values (A, B, C), and put the cell sequence that starts at cell A and
  is B cells long into cell C.
- `call` (14): Call an external OIL script: Advance the head, read in the file
  name (relative to the working directory). Advance the head again, read in the
  starting location of that script to write to. Advance the head again, read in
  the starting location of that script to read from. Then, a subinterpreter is
  started with that script. Anytime it would print something, it instead writes
  it to the main interpreter's writing location (advancing automatically).
  Anytime it would expect user input, it instead reads it from the next cell in
  the reading location. Effectively, this acts as a way to define something
  like functions.
- `random` (15): Fill a given cell with a random value: First read the cell
  address, then an inclusive upper bound. Fill the cell with a pseudorandom
  number between 0 and that number. If the upper bound is negative, this is a
  nop instead.
- `ord` (16): Advance the head twice, reading the next two values (A, B).
  Convert the value from cell A into a string. Put its length in cell B, and
  each of the numeric values of the codepoints of its characters seperately
  into cells after B.
- `chr` (17): Advance the head thrice, reading the next three values (A, B, C),
  and put the codepoint sequence that starts at cell A and is B cells long into
  cell C, converted into the characters of that codepoint. An invalid codepoint
  maps to `U+FFFD`.

## See also

- [A blog post about OIL](https://gastrovec.github.io/esoteric-annoyances.html)
- [OIL on the esolangs wiki](http://esolangs.org/wiki/OIL)
- [oilrs, an OIL implementation in Rust](https://github.com/serprex/oilrs)
