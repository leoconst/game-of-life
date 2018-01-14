import collections
import functools
import itertools
import os
import sys
import time

import attr


BLINKER = {(-1, 0), (0, 0), (1, 0)}
# · · ·
# ■ ■ ■
# · · ·

BLOCK = {(0, 0), (0, 1), (1, 0), (1, 1)}
# ■ ■
# ■ ■

DIEHARD = {(-3, 0), (-2, 0), (-2, -1),
           (2, -1), (3, -1), (4, -1), (3, 1)}
# · · · · · · ■ ·
# ■ ■ · · · · · ·
# · ■ · · · ■ ■ ■

R_PENTOMINO = {(0, 0), (0, -1), (-1, 0), (0, 1), (1, 1)}
# · ■ ■
# ■ ■ ·
# · ■ ·

PENTADECATHLON = [(-4, 0), (-3, 0), (-2, -1), (-2, 1), (-1, 0), (0, 0),
                  (1, 0), (2, 0), (3, -1), (3, 1), (4, 0), (5, 0)]
# · · ■ · · · · ■ · ·
# ■ ■ · ■ ■ ■ ■ · ■ ■
# · · ■ · · · · ■ · ·


DISPLAY_CHAR = '·■'


CLEAR_COMMAND = 'cls' if sys.platform == 'win32' else 'clear'


def clear_console():
    os.system(CLEAR_COMMAND)


def neighbours(cell):
    x, y = cell

    yield x + 1, y
    yield x - 1, y
    yield x, y + 1
    yield x, y - 1

    yield x + 1, y + 1
    yield x + 1, y - 1
    yield x - 1, y + 1
    yield x - 1, y - 1


def advanced(cells):
    """ Return an iterable of the new state of a given set of cells.

    Thanks to Jack Diederich (from his talk 'Stop Writing Classes').
    """
    checked = cells.union(*map(neighbours, cells))

    for cell in checked:
        count = len(cells.intersection(neighbours(cell)))
        if count == 3 or (count == 2 and cell in cells):
            yield cell


@attr.s
class Grid(object):
    
    x = attr.ib()
    y = attr.ib()

    def __attrs_post_init__(self):
        self.cells = set()

    def add_cell(self, x, y):
        """ Add a single cell at (x, y).
        """
        cell = (x, y)
        self.cells.add(cell)

    def _add_template(self, template, x=None, y=None, *, vertical=False):
        if vertical:
            template = {(y, x) for x, y in template}

        if x is None:
            x = self.x // 2
        if y is None:
            y = self.y // 2

        for template_x, template_y in template:
            self.add_cell(x + template_x, y + template_y)

    add_blinker = functools.partialmethod(_add_template, BLINKER)

    add_block = functools.partialmethod(_add_template, BLOCK)

    add_diehard = functools.partialmethod(_add_template, DIEHARD)

    add_pentadecathlon = functools.partialmethod(_add_template, PENTADECATHLON)

    add_r_pentomino = functools.partialmethod(_add_template, R_PENTOMINO)

    def display(self):
        """ Print the grid to the console.
        """
        for y in reversed(range(self.y)):
            cells = ((x, y) in self.cells for x in range(self.x))
            # Print a row of dots (dead) or squares (alive).
            print(' '.join(DISPLAY_CHAR[cell_exists] for cell_exists in cells))

    def advance(self):
        """ Advance the cells forward a step.
        """
        self.cells = set(advanced(self.cells))

    def _info_dump(self):
        if len(self.cells):
            min_x = min(x for x, _ in self.cells)
            max_x = max(x for x, _ in self.cells)
            min_y = min(y for _, y in self.cells)
            max_y = max(y for _, y in self.cells)
            print((min_x, min_y), (max_x, max_y))

        print(', '.join(f'{x} {y}' for x, y in self.cells))

    def start_loop(self, loop_count=0, delay=0.1, auto_break=25, output=True):
        """ Begin the simulation loop.
        """
        loops = range(1, loop_count + 1) if loop_count else itertools.count(1)
        recent_counts = collections.deque(range(2), auto_break)

        for loop in loops:
            count = len(self.cells)
            recent_counts.append(count)

            if not loop_count:
                if len(set(recent_counts)) == 1:
                    print(f'Auto exiting at loop {loop} (cell count remained '
                          f'at {count} for {auto_break} iterations)')
                    break
                elif not self.cells:
                    print(f'Auto exiting at loop {loop} (cell count hit 0)')
                    break

            if output:
                clear_console()
                print(f'loop: {loop} | count: {count}')
                self.display()

            self.advance()

            time.sleep(delay)

        self._info_dump()


# 1:
# grid.add_blinker(3, 5)
# grid.add_cell(3, 3)
# grid.add_cell(5, 6)
# grid.add_cell(5, 7)
# grid.add_cell(6, 6)

# 2:
# grid.add_blinker(3, 5)
# grid.add_cell(3, 3)
# grid.add_block(5, 6)


def main():
    grid = Grid(40, 30)
    grid.add_diehard()

    # grid.add_blinker(3, 5)
    # grid.add_cell(3, 3)
    # grid.add_block(7, 8)

    # grid.add_cell(5, 6)
    # grid.add_cell(5, 7)
    # grid.add_cell(6, 6)

    grid.start_loop(delay=0, auto_break=100, output=False)

if __name__ == '__main__':
    main()
