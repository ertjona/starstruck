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

## How to Play on iPhone/Mobile

Since Starstruck is a purely static HTML game with no backend, you can easily play it on your phone:

**Option A: GitHub Pages (Recommended)**
If you host this repository on GitHub, enable **GitHub Pages** in your repository settings. 

- **Seamless Loading**: If you name your generation file `puzzles.json` and keep it in the same folder as `starstruck.html`, the game will **automatically load** your puzzles when you open the site on your iPhone!
- **Zero Transfer**: You don't need to manually transfer files to your phone. Just commit/push to GitHub and refresh the page on Safari.

**Option B: Local File via iCloud**
1. Generate your puzzles on your Mac: `python3 starstruck_generator.py --save puzzles.json`.
2. Move `starstruck.html` and `puzzles.json` to your **iCloud Drive** (or send them via **AirDrop**).
3. Open the **Files app** on your iPhone, find the folder, and tap `starstruck.html`.
4. Tap "Load Puzzles" and select your `puzzles.json` from the same folder.

**Option C: Local Network Server**
1. Run a local web server on your computer: `python3 -m http.server 8000`
2. Find your computer's local IP address (e.g., `192.168.1.5`).
3. Open your iPhone's browser and go to `http://<your-ip>:8000/starstruck.html`.

## How to Play

1. Open `starstruck.html` in your browser.
2. Click **Load Puzzles** and select your `puzzles.json` file.
3. Click a cell once for **X**, twice for **★**, and three times to clear.
4. Solve the puzzle!
