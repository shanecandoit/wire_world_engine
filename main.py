import yaml
import copy
import time
import numpy as np
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel


# --- Rule and Loader Classes ---
class Rule:
    def __init__(self, name, description, pattern, new_state, conditions=None):
        self.name = name
        self.description = description
        self.pattern = pattern
        self.new_state = new_state
        self.conditions = conditions or []

    def _count_neighbors(self, grid, x, y, state_to_count):
        """Helper method to count neighbors of a specific state."""
        count = 0
        h, w = grid.shape
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                
                px, py = x + dx, y + dy
                if 0 <= px < h and 0 <= py < w and grid[px, py] == state_to_count:
                    count += 1
        return count

    def matches(self, grid, x, y):
        """
        Checks if a rule applies by verifying both the 3x3 pattern
        and all additional conditions.
        """
        # --- 1. Check the full 3x3 pattern ---
        h, w = grid.shape
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                pattern_cell = self.pattern[dx + 1][dy + 1]
                if pattern_cell == 'X':  # Wildcard matches anything
                    continue

                px, py = x + dx, y + dy
                # If pattern requires a state but we are off-grid, it's not a match
                if not (0 <= px < h and 0 <= py < w):
                    return False
                
                # If the grid cell doesn't match the specific state in the pattern
                if grid[px, py] != pattern_cell:
                    return False

        # --- 2. If pattern matched, check all conditions ---
        for cond in self.conditions:
            if cond['type'] == 'neighbor_count':
                state_to_check = cond['state']
                required_counts = cond['values']
                
                neighbor_count = self._count_neighbors(grid, x, y, state_to_check)
                
                if neighbor_count not in required_counts:
                    return False  # A condition was not met

        # If both the pattern and all conditions pass, the rule is a match.
        return True

class RuleSet:
    def __init__(self, rules, states):
        self.rules = rules
        self.states = states
        self.state_alias_to_value = {alias: value for alias, value in states.items()}
        self.state_value_to_alias = {value: alias for alias, value in states.items()}

    @staticmethod
    def from_yaml(path):
        def parse_when(when_str):
            lines = [line.strip() for line in when_str.strip().splitlines() 
                     if line.strip()]
            pattern = []
            for line in lines:
                row = [cell for cell in line.split()]
                pattern.append(row)
            return pattern

        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        states = data['states']
        rules = []
        for rule_data in data['rules']:
            pat = parse_when(rule_data['when'])
            # Store the 'then' state and conditions directly as aliases
            rules.append(Rule(
                name=rule_data['name'],
                description=rule_data.get('description', ''),
                pattern=pat,
                new_state=rule_data['then'],  # Use the alias 'H', 'W', etc. directly
                conditions=rule_data.get('conditions', [])  # Use the conditions block as-is
            ))
        return RuleSet(rules, states)


class Grid:
    def __init__(self, width: int, height: int, initial: Optional[List[List[str]]] = None, log_file=None, enable_logging=False):
        self.width = width
        self.height = height
        self.enable_logging = enable_logging
        self.turn = 0
        if initial[0][0] and isinstance(initial[0][0], str) and len(initial[0][0]) == 1:
            self.grid = np.array(initial, dtype=str)
        else:
            self.grid = np.full((height, width), '_', dtype=str)  # Default to '_'

        # assert that the first cell is a char of len 1
        msg = "Initial grid must be a 2D list of single-character strings."
        print(f"Initial grid: {initial}")
        print("first cell", initial[0][0], len(initial[0][0]), type(initial[0][0]))
        assert initial[0][0] and isinstance(initial[0][0], str) and len(initial[0][0]) == 1, msg


        # Initialize log file if logging is enabled
        if self.enable_logging:
            self.log_file = open('game.log', 'w') if not log_file else log_file
        else:
            self.log_file = None

    def __getitem__(self, idx):
        return self.grid[idx]

    def __setitem__(self, idx, value):
        self.grid[idx] = value

    def step(self, rule_set: RuleSet):
        self.turn += 1
        if self.enable_logging:
            self.log_file.write(f"--- Step {self.turn} ---\n")
            self.log_file.write(f"--- Applying rules for next step ---\n")
        
        new_grid = self.grid.copy()
        for x in range(self.height):
            for y in range(self.width):
                new_state = self.calculate_next_cell_state(x, y, rule_set)
                new_grid[x, y] = new_state
                
                if self.enable_logging:
                    # Log the state change, if a rule was applied
                    current_state = self.grid[x, y]
                    if new_state != current_state:
                        log_entry = f"Cell ({x}, {y}): Changed from '{current_state}' to '{new_state}'.\n"
                        self.log_file.write(log_entry)

        self.grid = new_grid

    def calculate_next_cell_state(self, x: int, y: int, rule_set: RuleSet) -> str:
        """
        Calculates the next state of a single cell based on Wireworld rules.
        This function encapsulates the core logic for state transitions.
        """
        current_state = self.grid[x, y]
        
        # Iterate through rules to find the first match
        for rule in rule_set.rules:
            if rule.matches(self.grid, x, y):
                return rule.new_state
        
        # If no rule matches, the state remains unchanged (e.g., empty cells)
        return current_state

    def as_list(self):
        return self.grid.tolist()


class UI:
    def __init__(self, console=None):
        self.console = console or Console()
        # states:
        #   _: Empty
        #   H: Electron Head (red)
        #   T: Electron Tail (blue)
        #   W: Conductor Wire (yellow)
        self.state_alias_to_repr = {
            '_': '[grey].[/]',      # Empty
            'H': '[bold red]H[/]',  # Electron head
            'T': '[blue]T[/]',      # Electron tail
            'W': '[yellow]W[/]'     # Conductor
        }

    def draw(self, grid: Grid, step: int):
        self.console.clear()
        self.console.print(Panel(f"[bold green]Wireworld Step {step}[/]", expand=False))
        table = Table(show_header=False, box=None, pad_edge=False)
        for _ in range(grid.width):
            table.add_column(justify="center", no_wrap=True)
        for row in grid.as_list():
            visuals = [self.state_alias_to_repr.get(cell, '?') for cell in row]
            table.add_row(*visuals)
        self.console.print(table)
        self.console.print


class App:
    def __init__(self):
        # 0: empty, 1: electron head, 2: electron tail, 3: conductor
        # Simple wire with an electron head
        # Empty grey "."
        # Head red "*"
        # Tail blue "_"
        # Conductor yellow "+"
        initial_str = [
            "__________",  # 1
            "_WTHWWWWW_",  # 2
            "_W______W_",  # 3
            "_W_HWWW_W_",  # 4
            "_W_W__W_W_",  # 5
            "_W_W__W_W_",  # 6
            "_W_WWWW_W_",  # 7
            "_W______W_",  # 8
            "_WWWWWWWW_",  # 9
            "__________"   # 10
        ]

        initial = [list(row) for row in initial_str]
        initial = np.array(initial)
        # initial[1][1] = 'T'  # Electron tail
        # initial[1][2] = 'H'  # Electron head
        self.grid = Grid(10, 10, initial, enable_logging=True)
        self.ui = UI()
        self.rule_set = RuleSet.from_yaml('wire-world.yaml')
        self.steps = 15

        self.time_delay = 0.3

    def run(self):
        for i in range(self.steps):
            self.ui.draw(self.grid, i)
            self.grid.step(self.rule_set)
            time.sleep(self.time_delay)


def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
