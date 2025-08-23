# Open Board. Free TTRPG Audio Mixer and Sounboard

![Python](https://img.shields.io/badge/Python-3.13%2B-blue) 
![PySide6](https://img.shields.io/badge/PySide6-6.x-green)
![Flake8](https://img.shields.io/badge/linting-flake8-yellow.svg)
![Black](https://img.shields.io/badge/code%20formatter-black-000000.svg)
![isort](https://img.shields.io/badge/import%20sorting-isort-1674b1.svg)
![MyPy](https://img.shields.io/badge/type%20checking-mypy-blue.svg)

Open Board is an open-source PySide6 audio mixer and soundboard tailored for tabletop role-playing games (TTRPGs) such as Dungeons & Dragons, Pathfinder, Warhammer, and more. It lets Game Masters trigger ambient, music, and sound effects from a simple board interface to enhance every session.

![Open Board](./screenshot.png?raw=true)

## Getting Started

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the app:
   ```bash
   python main.py
   ```

The first run creates `ambient`, `music`, and `effects` folders with instructions on where to place your audio files.
