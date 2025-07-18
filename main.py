
import yaml
import rich
from rich.console import Console

import copy
import time
from typing import List, Optional


# --- Rule and Loader Classes ---
class Rule:
    def __init__(self, name, description, pattern, new_state, conditions=None):
        self.name = name
        self.description = description
        self.pattern = pattern  # 3x3 pattern, center cell is the target
        self.new_state = new_state
        self.conditions = conditions or []

    def matches(self, grid, x, y, states):
        # Check 3x3 pattern match (X is wildcard)
        h, w = len(grid), len(grid[0])
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                px, py = x + dx, y + dy
                pat_val = self.pattern[dx+1][dy+1]
                if pat_val == 'X':
                    continue
                if not (0 <= px < h and 0 <= py < w):
                    return False
                if grid[px][py] != pat_val:
                    return False
        # Check conditions (e.g., neighbor counts)
        for cond in self.conditions:
            if cond['type'] == 'neighbor_count':
                state_val = cond['state']
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        px, py = x + dx, y + dy
                        if 0 <= px < h and 0 <= py < w:
                            if grid[px][py] == state_val:
                                count += 1
                op = cond['operator']
                vals = cond['values']
                if op == 'in' and count not in vals:
                    return False
                if op == 'not in' and count in vals:
                    return False
        return True

class RuleSet:
    def __init__(self, rules, states):
        self.rules = rules
        self.states = states

    @staticmethod
    def from_yaml(path):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        states = {v: k for k, v in data['states'].items()}
        rules = []
        for rule in data['rules']:
            # Convert pattern: replace state names with ints, keep 'X' as is
            pat = []
            for row in rule['pattern']:
                pat.append([cell if cell == 'X' else int(cell) for cell in row])
            rules.append(Rule(
                name=rule['name'],
                description=rule.get('description', ''),
                pattern=pat,
                new_state=rule['new_state'],
                conditions=rule.get('conditions', [])
            ))
        return RuleSet(rules, states)

import copy
import time
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


class Grid:
    def __init__(self, width: int, height: int, initial: Optional[List[List[int]]] = None):
        self.width = width
        self.height = height
        if initial:
            self.grid = copy.deepcopy(initial)
        else:
            self.grid = [[0 for _ in range(width)] for _ in range(height)]

    def __getitem__(self, idx):
        return self.grid[idx]

    def __setitem__(self, idx, value):
        self.grid[idx] = value

    def step(self):
        new_grid = copy.deepcopy(self.grid)
        for x in range(self.height):
            for y in range(self.width):
                cell = self.grid[x][y]
                if cell == 0:  # Empty
                    new_grid[x][y] = 0
                elif cell == 1:  # Electron Head
                    new_grid[x][y] = 2
                elif cell == 2:  # Electron Tail
                    new_grid[x][y] = 3
                elif cell == 3:  # Conductor
                    heads = self.count_neighbors(x, y, 1)
                    if heads == 1 or heads == 2:
                        new_grid[x][y] = 1
                    else:
                        new_grid[x][y] = 3
        self.grid = new_grid

    def count_neighbors(self, x, y, state):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.height and 0 <= ny < self.width:
                    if self.grid[nx][ny] == state:
                        count += 1
        return count

    def as_list(self):
        return self.grid


class UI:
    def __init__(self, console=None):
        self.console = console or Console()
        self.state_repr = {
            0: '[grey].[/]',      # Empty
            1: '[bold red]*[/]',  # Electron head
            2: '[blue]_[/]',      # Electron tail
            3: '[yellow]+[/]'     # Conductor
        }

    def draw(self, grid: Grid, step: int):
        self.console.clear()
        self.console.print(Panel(f"[bold green]Wireworld Step {step}[/]", expand=False))
        table = Table(show_header=False, box=None, pad_edge=False)
        for _ in range(grid.width):
            table.add_column(justify="center", no_wrap=True)
        for row in grid.as_list():
            table.add_row(*[self.state_repr.get(cell, '?') for cell in row])
        self.console.print(table)
        self.console.print()


class App:
    def __init__(self):
        # 0: empty, 1: electron head, 2: electron tail, 3: conductor
        # Simple wire with an electron head
        # Empty grey "."
        # Head red "*"
        # Tail blue "_"
        # Conductor yellow "+"
        initial = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 3, 3, 3, 3, 3, 3, 3, 0],
            [0, 3, 0, 0, 0, 0, 0, 0, 3, 0],
            [0, 3, 0, 3, 3, 3, 3, 0, 3, 0],
            [0, 3, 0, 3, 0, 0, 3, 0, 3, 0],
            [0, 3, 0, 3, 0, 0, 3, 0, 3, 0],
            [0, 3, 0, 3, 3, 3, 3, 0, 3, 0],
            [0, 3, 0, 0, 0, 0, 0, 0, 3, 0],
            [0, 3, 3, 3, 3, 3, 3, 3, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        initial[1][1] = 1  # Electron head
        initial[1][2] = 2  # Electron tail
        self.grid = Grid(10, 10, initial)
        self.ui = UI()
        self.steps = 10

    def run(self):
        for i in range(self.steps):
            self.ui.draw(self.grid, i)
            self.grid.step()
            time.sleep(0.3)

def count_neighbors(grid, x, y, state):
    count = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                if grid[nx][ny] == state:
                    count += 1
    return count

def step_wireworld(grid):
    new_grid = copy.deepcopy(grid)
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            cell = grid[x][y]
            if cell == 0:  # Empty
                new_grid[x][y] = 0
            elif cell == 1:  # Electron Head
                new_grid[x][y] = 2
            elif cell == 2:  # Electron Tail
                new_grid[x][y] = 3
            elif cell == 3:  # Conductor
                heads = count_neighbors(grid, x, y, 1)
                if heads == 1 or heads == 2:
                    new_grid[x][y] = 1
                else:
                    new_grid[x][y] = 3
    return new_grid


def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
