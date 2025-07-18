import pytest
import numpy as np
from main import RuleSet, Grid, Rule
import yaml
from typing import List, Optional

def load_yaml_rules(file_path: str) -> RuleSet:
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    states = {k: v for k, v in data['states'].items()}
    return RuleSet.from_yaml(file_path)

"""
states:
  _: Empty
  H: Electron Head (red)
  T: Electron Tail (blue)
  W: Conductor Wire (yellow)
"""

@pytest.fixture
def rule_set():
    return load_yaml_rules('wire-world.yaml')

def grid_from_string(grid_str: str, rule_set: RuleSet) -> List[List[str]]:
    """Convert a string representation of a grid to a 2D list of single-character strings."""
    rows = grid_str.strip().split(',')
    grid = []
    for row in rows:
        grid.append([rule_set.state_value_to_alias[rule_set.state_alias_to_value[cell]] for cell in row])
    return grid

def test_calculate_next_cell_state_empty_remains_empty(rule_set):
    grid_data = [
        ['.', '.', '.'],
        ['.', '.', '.'],
        ['.', '.', '.']
    ]
    grid_obj = Grid(3, 3, initial=grid_data)
    next_state = grid_obj.calculate_next_cell_state(1, 1, rule_set)
    assert next_state == '.', f"Expected '.' but got {next_state}"

def test_calculate_next_cell_state_head_to_tail(rule_set):
    grid_data = [
        ['.', '.', '.'],
        ['.', 'H', '.'],
        ['.', '.', '.']
    ]
    grid_obj = Grid(3, 3, initial=grid_data)
    next_state = grid_obj.calculate_next_cell_state(1, 1, rule_set)
    assert next_state == 'T', f"Expected 'T' but got {next_state}"

def test_calculate_next_cell_state_tail_to_conductor(rule_set):
    grid_data = [
        ['.', '.', '.'],
        ['.', 'T', '.'],
        ['.', '.', '.']
    ]
    grid_obj = Grid(3, 3, initial=grid_data)
    next_state = grid_obj.calculate_next_cell_state(1, 1, rule_set)
    assert next_state == 'W', f"Expected 'W' but got {next_state}"

def test_calculate_next_cell_state_conductor_one_head_neighbor(rule_set):
    grid_data = [
        ['.', '.', '.'],
        ['H', 'W', '.'],
        ['.', '.', '.']
    ]
    grid_obj = Grid(3, 3, initial=grid_data)
    next_state = grid_obj.calculate_next_cell_state(1, 1, rule_set)
    assert next_state == 'H', f"Expected 'H' but got {next_state}"

def test_calculate_next_cell_state_conductor_two_head_neighbors(rule_set):
    grid_data = [
        ['H', '.', '.'],
        ['.', 'W', '.'],
        ['H', '.', '.']
    ]
    grid_obj = Grid(3, 3, initial=grid_data)
    next_state = grid_obj.calculate_next_cell_state(1, 1, rule_set)
    assert next_state == 'H', f"Expected 'H' but got {next_state}"

def test_calculate_next_cell_state_conductor_zero_head_neighbors(rule_set):
    grid_data = [
        ['.', '.', '.'],
        ['.', 'W', '.'],
        ['.', '.', '.']
    ]
    grid_obj = Grid(3, 3, initial=grid_data)
    next_state = grid_obj.calculate_next_cell_state(1, 1, rule_set)
    assert next_state == 'W', f"Expected 'W' but got {next_state}"

def test_calculate_next_cell_state_conductor_three_head_neighbors(rule_set):
    grid_data = [
        ['H', 'H', 'H'],
        ['.', 'W', '.'],
        ['.', '.', '.']
    ]
    grid_obj = Grid(3, 3, initial=grid_data)
    next_state = grid_obj.calculate_next_cell_state(1, 1, rule_set)
    assert next_state == 'W', f"Expected 'W' but got {next_state}"
