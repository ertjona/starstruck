"""
Starstruck Puzzle Generator
============================
Generates Starstruck puzzles of any size N with guaranteed:
  - Exactly one valid solution
  - All regions orthogonally connected
  - One star per row, column, and region
  - No two stars touch (including diagonally)

Usage:
    python starstruck_generator.py              # generate 1x 5x5, 1x 6x6, 1x 7x7, 1x 8x8 and 1x 9x9. 
    python starstruck_generator.py --size 5 --count 3 --save puzzles.json   # generate 3 5x5 puzzles and save them to puzzles.json
    python starstruck_generator.py --size 8 --count 3
    python starstruck_generator.py --size 10 --count 1
"""

import random
import argparse
import json
from collections import defaultdict, deque


# ─── CORE SOLVER ──────────────────────────────────────────────────────────────

def find_all_solutions(regions, N, limit=2):
    """
    Find up to `limit` solutions using MRV (minimum remaining values) ordering.
    Processes the region with fewest valid candidates first at each step,
    which prunes the search tree dramatically for larger grids.
    """
    rm = defaultdict(list)
    for r in range(N):
        for c in range(N):
            rm[regions[r][c]].append((r, c))

    region_ids = list(range(N))
    solutions  = []

    def candidates(rid, used_rows, used_cols, chosen):
        return [
            (r, c) for r, c in rm[rid]
            if r not in used_rows
            and c not in used_cols
            and all(abs(r-r2)>1 or abs(c-c2)>1 for r2,c2 in chosen)
        ]

    def bt(remaining, used_rows, used_cols, chosen):
        if len(solutions) >= limit:
            return
        if not remaining:
            solutions.append(list(chosen))
            return

        # MRV: pick region with fewest valid candidates
        best_rid  = min(remaining, key=lambda rid: len(candidates(rid, used_rows, used_cols, chosen)))
        best_cands = candidates(best_rid, used_rows, used_cols, chosen)

        if not best_cands:
            return  # dead end

        next_remaining = [rid for rid in remaining if rid != best_rid]

        for r, c in best_cands:
            bt(next_remaining, used_rows | {r}, used_cols | {c}, chosen + [(r, c)])

    bt(region_ids, set(), set(), [])
    return solutions


def has_unique_solution(regions, N):
    return len(find_all_solutions(regions, N, limit=2)) == 1


# ─── REGION UTILITIES ─────────────────────────────────────────────────────────

def is_connected(cells):
    """Check if a list of (r,c) cells is orthogonally connected."""
    if not cells:
        return True
    cell_set = set(cells)
    visited = {cells[0]}
    q = deque([cells[0]])
    while q:
        r, c = q.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nb = (r + dr, c + dc)
            if nb in cell_set and nb not in visited:
                visited.add(nb)
                q.append(nb)
    return visited == cell_set


def all_regions_connected(regions, N):
    rm = defaultdict(list)
    for r in range(N):
        for c in range(N):
            rm[regions[r][c]].append((r, c))
    return all(is_connected(cells) for cells in rm.values())


# ─── STAR PLACEMENT ───────────────────────────────────────────────────────────

def generate_valid_stars(N, rng):
    """
    Generate a valid star placement: one per row, one per column, none adjacent.
    Uses random column permutation with backtracking.
    """
    cols = list(range(N))

    def bt(row, used_cols, chosen):
        if row == N:
            return chosen
        shuffled = cols[:]
        rng.shuffle(shuffled)
        for c in shuffled:
            if c in used_cols:
                continue
            if any(abs(row - r2) <= 1 and abs(c - c2) <= 1 for r2, c2 in chosen):
                continue
            result = bt(row + 1, used_cols | {c}, chosen + [(row, c)])
            if result:
                return result
        return None

    return bt(0, set(), [])


# ─── REGION GROWTH ────────────────────────────────────────────────────────────

def grow_regions(N, stars, rng):
    """
    Assign cells to stars using a randomized multi-seed expansion (flood fill).
    This ensures all regions remain orthogonally connected and exactly one star
    is placed in each region.
    """
    regions = [[-1] * N for _ in range(N)]
    frontier = []  # List of (r, c, rid)

    # Place star seeds and initialize frontier
    for i, (r, c) in enumerate(stars):
        regions[r][c] = i
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < N and 0 <= nc < N:
                frontier.append((nr, nc, i))

    while frontier:
        # Pick a random cell from the frontier to expand
        idx = rng.randrange(len(frontier))
        # Swap with last for O(1) removal
        frontier[idx], frontier[-1] = frontier[-1], frontier[idx]
        r, c, rid = frontier.pop()

        if regions[r][c] != -1:
            continue

        regions[r][c] = rid

        # Add neighbors to frontier
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < N and 0 <= nc < N and regions[nr][nc] == -1:
                frontier.append((nr, nc, rid))

    return regions


# ─── MAIN GENERATOR ───────────────────────────────────────────────────────────

def generate_puzzle(N, seed=None, max_attempts=None, verbose=False):
    if max_attempts is None:
        max_attempts = 5000 if N <= 6 else 20000
    """
    Generate a single valid Starstruck puzzle of size N.

    Returns a dict with:
        regions  : N×N list of region IDs
        solution : N×N list (1=star, 0=empty)
        stars    : list of (row, col) star positions
        seed     : the random seed used
    """
    rng = random.Random(seed)
    actual_seed = seed if seed is not None else rng.randint(0, 999999)
    rng = random.Random(actual_seed)

    for attempt in range(max_attempts):
        # Step 1: valid star placement
        stars = generate_valid_stars(N, rng)
        if not stars:
            continue

        # Step 2: grow connected regions
        regions = grow_regions(N, stars, rng)
        if regions is None:
            continue

        if not all_regions_connected(regions, N):
            continue

        # Step 3: verify unique solution
        if not has_unique_solution(regions, N):
            continue

        # Build solution grid
        solution = [[0] * N for _ in range(N)]
        for r, c in stars:
            solution[r][c] = 1

        if verbose:
            print(f"  Found after {attempt + 1} attempts (seed={actual_seed})")

        return {
            "regions": regions,
            "solution": solution,
            "stars": stars,
            "seed": actual_seed,
            "size": N,
        }

    return None  # failed after max_attempts


# ─── OUTPUT FORMATTERS ────────────────────────────────────────────────────────

PUZZLE_NAMES = {
    5:  ["The Cub",     "The Fox",      "The Owl",     "The Hare",    "The Swan",
         "The Wren",    "The Deer",     "The Wolf",    "The Lynx",    "The Heron"],
    6:  ["Vega",        "Altair",       "Deneb",       "Regulus",     "Spica",
         "Antares",     "Pollux",       "Castor",      "Arcturus",    "Capella"],
    7:  ["Orion",       "Cassiopeia",   "Andromeda",   "Perseus",     "Lyra",
         "Aquila",      "Cygnus",       "Draco",       "Hercules",    "Boötes"],
    8:  ["Sagittarius", "Scorpius",     "Gemini",      "Taurus",      "Leo",
         "Virgo",       "Aquarius",     "Pisces",      "Capricorn",   "Libra"],
    9:  ["Nebula I",    "Nebula II",    "Nebula III",  "Nebula IV",   "Nebula V",
         "Nebula VI",   "Nebula VII",   "Nebula VIII", "Nebula IX",   "Nebula X"],
    10: ["Cluster I",   "Cluster II",   "Cluster III", "Cluster IV",  "Cluster V",
         "Cluster VI",  "Cluster VII",  "Cluster VIII","Cluster IX",  "Cluster X"],
    11: ["Void I",      "Void II",      "Void III",    "Void IV",     "Void V"],
    12: ["Cosmos I",    "Cosmos II",    "Cosmos III",  "Cosmos IV",   "Cosmos V"],
}

def get_name(size, index):
    names = PUZZLE_NAMES.get(size, [])
    if index < len(names):
        return names[index]
    return f"Puzzle {index + 1} ({size}×{size})"


def print_puzzle(p, name):
    """Pretty-print a puzzle to the terminal for visual inspection."""
    N = p["size"]
    COLORS = ["🟦","🟩","🟥","🟪","🟧","⬜","🟫","🔶"]
    print(f"\n  {name}  (seed={p['seed']}, {N}×{N})")
    print("  Regions:")
    for row in p["regions"]:
        print("   ", " ".join(COLORS[v % len(COLORS)] for v in row))
    print("  Solution:")
    for r, row in enumerate(p["solution"]):
        cells = []
        for c, v in enumerate(row):
            cells.append("★" if v == 1 else "·")
        print("   ", " ".join(cells))
    print(f"  Stars: {p['stars']}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Starstruck puzzle generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 1x 5x5, 1x 6x6, 1x 7x7, 1x 8x8 and 1x 9x9
  python starstruck_generator.py --save puzzles.json

  # Generate 5 8x8 puzzles and save
  python starstruck_generator.py --size 8 --count 5 --save puzzles.json

  # Append to an existing puzzles.json instead of overwriting
  python starstruck_generator.py --size 8 --count 3 --save puzzles.json --append

  # Preview puzzles in terminal without saving
  python starstruck_generator.py --size 5 --count 2
        """
    )
    parser.add_argument("--size",    type=int, default=None,
                        help="Grid size N — any value from 5 upward (default: 5, 6, 7, 8, 9)")
    parser.add_argument("--count",   type=int, default=1,
                        help="Number of puzzles per size (default: 1)")
    parser.add_argument("--seed",    type=int, default=None,
                        help="Starting random seed for reproducibility")
    parser.add_argument("--save",    type=str, default=None, metavar="FILE",
                        help="Save puzzles as a .json file loadable in the game (e.g. puzzles.json)")
    parser.add_argument("--append",  action="store_true",
                        help="Append to an existing --save file instead of overwriting")
    parser.add_argument("--verbose", action="store_true",
                        help="Show attempt counts during generation")
    args = parser.parse_args()

    sizes = [args.size] if args.size else [5, 6, 7, 8, 9]
    all_new_puzzles = []  # flat list for JSON output

    for size in sizes:
        print(f"\nGenerating {args.count} puzzle(s) of size {size}×{size}...")
        attempt_seed = args.seed if args.seed is not None else random.randint(0, 99999)

        for i in range(args.count):
            print(f"  Puzzle {i+1}/{args.count}...", end=" ", flush=True)
            p = generate_puzzle(size, seed=attempt_seed, verbose=args.verbose)
            if p:
                name = get_name(size, len(all_new_puzzles))
                print(f"✓  (seed={p['seed']})")
                print_puzzle(p, name)
                all_new_puzzles.append({
                    "name":     name,
                    "size":     size,
                    "seed":     p["seed"],
                    "regions":  p["regions"],
                    "solution": p["solution"],
                })
            else:
                print("✗  FAILED — try a different seed")
            
            attempt_seed += 1

    if not all_new_puzzles:
        print("\nNo puzzles generated.")
        return

    # ── Save to JSON file ──────────────────────────────────────
    if args.save:
        existing = []

        # Load existing puzzles if appending
        if args.append:
            try:
                with open(args.save, "r") as f:
                    existing = json.load(f)
                print(f"\nLoaded {len(existing)} existing puzzle(s) from {args.save}")
            except FileNotFoundError:
                print(f"\n{args.save} not found — creating new file.")
            except json.JSONDecodeError:
                print(f"\nWarning: could not parse {args.save} — overwriting.")

        combined = existing + all_new_puzzles
        with open(args.save, "w") as f:
            json.dump(combined, f, indent=2)

        print(f"\n✓ Saved {len(all_new_puzzles)} new puzzle(s) "
              f"({len(combined)} total) → {args.save}")
        print(f"  Load this file in the game using the 'Load Puzzles' button.")

    else:
        # No --save: just print a JSON preview to the terminal
        print("\n" + "="*60)
        print("JSON PREVIEW (use --save puzzles.json to write a file):")
        print("="*60)
        print(json.dumps(all_new_puzzles, indent=2))


if __name__ == "__main__":
    main()
