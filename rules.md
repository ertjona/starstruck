Below is the rules of the puzzle game Starstruck, followed by a practical development blueprint (logic, data model, solver, generator, UI, and progression system).

---

# 1. Core Game Rules (decoded)

### Objective

Place stars on the grid so that:

1. **Each row contains exactly one star**
2. **Each column contains exactly one star**
3. **Each colored region contains exactly one star**
4. **Stars cannot touch**

   * not horizontally
   * not vertically
   * not diagonally

### Player actions

* Tap once → mark cell with **X** (cannot contain a star)
* Tap twice → place **★**
* When a star is placed:

  * adjacent cells are automatically filled with X
  * (because touching is forbidden)

### Win condition

Puzzle solved when all constraints above are satisfied.

---

# 2. Data Model for Implementation

### Grid representation

Use a 2-layer model:

```text
Cell {
    row: int
    col: int
    regionId: int
    state: EMPTY | STAR | BLOCKED
}
```

Board:

```text
Board {
    size: N
    cells[N][N]
    regions: Map<regionId, list<Cell>>
}
```

Indexes to maintain:

```text
rowStars[row]
colStars[col]
regionStars[regionId]
```

These allow O(1) validity checks.

---

# 3. Validation Logic

### Star placement rule check

When placing a star:

```pseudo
function canPlaceStar(cell):
    if rowStars[cell.row] == 1 → false
    if colStars[cell.col] == 1 → false
    if regionStars[cell.region] == 1 → false
    if any adjacent cell contains STAR → false
    return true
```

### Auto-blocking neighbors

```pseudo
for each neighbor in 8 directions:
    if neighbor.state == EMPTY:
        neighbor.state = BLOCKED
```

---

# 4. Solver Engine (needed for hints & generation)

Use constraint propagation + backtracking.

### Deterministic rules

Implement first:

1. If row has only one empty spot → must be star
2. If region has one valid spot → must be star
3. If placing star would violate another region’s only option → block it
4. If a row already has a star → rest are X

These rules solve most puzzles without guessing.

### Backtracking fallback

```pseudo
solve(board):
    apply deterministic rules
    if solved → return true
    pick cell with fewest possibilities
    try STAR branch
    try BLOCKED branch
```

---

# 5. Puzzle Generator

Generation is the hardest part.

### Recommended approach

1. Generate a solved grid first

   * place one star per row/col
   * enforce non-touch rule
2. Partition board into regions afterward
3. Verify uniqueness by running solver

If multiple solutions → regenerate regions.

This approach is far easier than generating regions first.

---

# 6. UI/UX Design Suggestions

### Interaction model

* Tap cycle: EMPTY → X → STAR → EMPTY
* Auto-fill X around star
* Highlight invalid placements in red
* Show region boundaries clearly

### Helpful UX features

* Mistake detection toggle
* Undo history stack
* Hint button using solver
* “Show conflicts” overlay

---

# 7. Difficulty Scaling

Difficulty can be tuned by:

| Parameter                  | Effect                  |
| -------------------------- | ----------------------- |
| Grid size                  | biggest factor          |
| Region shape irregularity  | harder deduction        |
| Symmetry                   | easier puzzles          |
| Solver step depth required | real difficulty measure |

A good scale:

```text
Easy   : 6x6
Medium : 8x8
Hard   : 10x10
Expert : 12x12+
```

---

# 8. Suggested Architecture

```text
Game Layer
 ├── Board Model
 ├── Rule Engine
 ├── Solver Engine
 ├── Generator Engine
 └── Hint System

UI Layer
 ├── Grid Renderer
 ├── Input Handler
 ├── Animation Layer
 └── Tutorial Overlay
```

Keep logic separate from UI — this allows:

* web version
* mobile version
* AI hint system later

---

# 9. If expanding into a full product

Possible features:

* Daily puzzles
* Leaderboard by solve time
* Procedural infinite puzzles
* Theme packs / skins
* Progressive tutorial mode
* Accessibility (color-blind region patterns)

---

If helpful, the next step can be:

* a **working solver pseudocode**
* a **grid generator algorithm**
* or a **React / Flutter implementation skeleton**

Which direction would be most useful next?
