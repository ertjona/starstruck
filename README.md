# Starstruck

Starstruck is a strategy logic game where you place stars on a grid according to a set of rules. You need to use logical thinking to continuously narrow down the possibilities until all the stars fit perfectly. I often play this game on Netflix's Puzzled app and really enjoy it. I'm currently trying to make my own version.

## Gameplay

Place stars on the grid according to these laws:
- Each row contains exactly one star.
- Each column contains exactly one star.
- Each colored region contains exactly one star.
- Stars may not touch, even diagonally.

## Contents

- `starstruck.html`: The main game interface. Open this in any modern browser to play.
- `starstruck_generator.py`: A Python script to generate new puzzle sets.
- `rules.md`: Detailed game rules and development blueprint.
- `puzzles.json`: An example puzzle set.

## How to Generate Puzzles

Use the Python generator to create new constellations:

```bash
python3 starstruck_generator.py --size 8 --count 5 --save puzzles.json
```

## How to Play

1. Open `starstruck.html` in your browser.
2. Click **Load Puzzles** and select your `puzzles.json` file.
3. Click a cell once for **X**, twice for **★**, and three times to clear.
4. Solve the puzzle!
