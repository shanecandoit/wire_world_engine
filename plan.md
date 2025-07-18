# Plan: Wireworld Rule Logic via YAML

## Goal
Move the Wireworld rule logic out of Python and into a YAML file (`wire-world.yaml`). The engine will load these rules and apply them to the grid at each step. For verification, print each (x, y) cell and the rule name applied during each step.

## Steps

1. **Define Wireworld Rules in YAML**
   - Create `wire-world.yaml` with a structure similar to the example in the README.
   - Each rule should have:
     - Name
     - Description
     - Pattern (3x3 neighborhood)
     - Optional conditions (e.g., neighbor counts)
     - New state for the center cell

2. **YAML Loader**
   - Implement a loader in Python to parse `wire-world.yaml`.
   - Convert YAML rules into Python objects/classes for use in the engine.

3. **Rule Matching Engine**
   - For each cell, check all rules to find a match (pattern and conditions).
   - When a rule matches, record the rule name and apply the transformation.
   - If multiple rules match, use the first match (or define priority in YAML).

4. **Simulation Step**
   - For each cell (x, y):
     - Find and apply the matching rule.
     - Print (x, y) and the rule name for verification.
   - Update the grid synchronously after all rules are applied.

5. **Integration**
   - Replace the hardcoded logic in `Grid.step()` with the rule engine.
   - Ensure the UI still displays the grid as before.

6. **Testing/Verification**
   - Run the simulation and verify that for each cell, the correct rule name is printed.
   - Compare the output to expected Wireworld behavior.

## Deliverables
- `wire-world.yaml` with all Wireworld rules.
- Updated engine code to load and apply rules from YAML.
- Console output showing (x, y) and rule name for each cell at each step.
- Existing UI and animation remain functional.

# Progress Update (Step 1 Complete)

---

## Step 1 Complete
- Created `wire-world.yaml` with all Wireworld rules, following the structure in the README.
- Each rule includes name, description, pattern, optional conditions, and new state.

## Next Steps

2. **YAML Loader**
   - Implement a loader in Python to parse `wire-world.yaml`.
   - Convert YAML rules into Python objects/classes for use in the engine.

3. **Rule Matching Engine**
   - For each cell, check all rules to find a match (pattern and conditions).
   - When a rule matches, record the rule name and apply the transformation.
   - If multiple rules match, use the first match (or define priority in YAML).

4. **Simulation Step**
   - For each cell (x, y):
     - Find and apply the matching rule.
     - Print (x, y) and the rule name for verification.
   - Update the grid synchronously after all rules are applied.

5. **Integration**
   - Replace the hardcoded logic in `Grid.step()` with the rule engine.
   - Ensure the UI still displays the grid as before.

6. **Testing/Verification**
   - Run the simulation and verify that for each cell, the correct rule name is printed.
   - Compare the output to expected Wireworld behavior.

---

# Next: Implement YAML loader and rule objects in Python.

# Progress Update (Step 2 Complete)

---

## Step 2 Complete
- Implemented a YAML loader using PyYAML to parse `wire-world.yaml`.
- Created `Rule` and `RuleSet` classes in Python.
  - `Rule` holds the pattern, new state, and conditions, and can check if it matches a cell.
  - `RuleSet` loads all rules from YAML and provides access to the rules and state mappings.

## Next Steps

3. **Rule Matching Engine**
   - For each cell, check all rules to find a match (pattern and conditions).
   - When a rule matches, record the rule name and apply the transformation.
   - If multiple rules match, use the first match (or define priority in YAML).

4. **Simulation Step**
   - For each cell (x, y):
     - Find and apply the matching rule.
     - Print (x, y) and the rule name for verification.
   - Update the grid synchronously after all rules are applied.

5. **Integration**
   - Replace the hardcoded logic in `Grid.step()` with the rule engine.
   - Ensure the UI still displays the grid as before.

6. **Testing/Verification**
   - Run the simulation and verify that for each cell, the correct rule name is printed.
   - Compare the output to expected Wireworld behavior.

---

# Next: Implement rule matching and per-cell rule name printing in the simulation step.
