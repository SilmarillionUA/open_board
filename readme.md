# Open Board

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![PySide6](https://img.shields.io/badge/PySide6-6.x-green)

Open Board is an open-source PySide6 audio mixer and soundboard tailored for tabletop role-playing games (TTRPGs) such as Dungeons & Dragons, Pathfinder, Warhammer, and more. It lets Game Masters trigger ambient, music, and sound effects from a simple board interface to enhance every session.

## Getting Started

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the app:
   ```bash
   python music_board_app.py
   ```

The first run creates `ambient`, `music`, and `effects` folders with instructions on where to place your audio files.
