# PetBuddy

English | [中文](README.zh-CN.md)

<img src="assets/app_icon.png" alt="PetBuddy app icon" width="120">

## Overview

PetBuddy is a small local desktop pet idle game. The pet stays on your desktop in a transparent, frameless window. You can interact with it through the context menu and status panel: feed it, study, work, sleep, buy items, and adjust display settings.

The app is fully local. It does not use accounts, online services, or a database. Save data is stored as local JSON files.

## Features

- Transparent, frameless, draggable, always-on-top pet window
- Static pet images for idle, happy, hungry, studying, working, and sleeping states
- Click interaction with mood gain
- Context menu for feeding, studying, working, sleeping, shop, status, and settings
- Study task: 5 minutes for 1 knowledge
- Work tasks unlocked by knowledge level
- Sleep tasks: 5 / 15 / 40 minutes with mood recovery
- Shop items: normal food, premium food, toy, and bed upgrade
- Local autosave and task remaining-time persistence
- Configurable pet size, always-on-top mode, bubble tips, click animation, and quiet mode

## Requirements

- Python 3.11+
- PySide6
- Pillow
- PyInstaller, for packaging

Create a conda environment and install dependencies:

```bash
conda create -n petbuddy python=3.11
conda run -n petbuddy python -m pip install -r requirements.txt
```

## Run

From the project root, run the app with the conda environment:

```bash
conda activate petbuddy
python main.py
```

## Current Rules

| Item | Rule |
| --- | --- |
| Passive coins | Base +1 per minute, affected by mood multiplier |
| Mood decay | Idle -1/min, studying/working -1.2/min, sleeping no decay |
| Satiety decay | Idle -1/min, studying/working -1.2/min, sleeping -0.5/min |
| Click interaction | 10-second cooldown, mood +3 |
| Study | 5 minutes, knowledge +1 |
| Sleep | 5 / 15 / 40 minutes, mood +5 / +18 / +50 |

### Mood Multiplier

| Mood | Multiplier |
| --- | ---: |
| 80-100 | 1.5x |
| 50-79 | 1.0x |
| 20-49 | 0.7x |
| 0-19 | 0.3x |

## Jobs

| Job | Required Knowledge | Duration | Coins |
| --- | ---: | ---: | ---: |
| Bottle Collector | 0 | 1 min | 20 |
| Flyer Distributor | 10 | 3 min | 100 |
| Cafe Helper | 30 | 5 min | 220 |
| Pet Programmer | 60 | 10 min | 520 |
| Mystery Consultant | 120 | 20 min | 1200 |

## Shop

| Item | Price | Effect |
| --- | ---: | --- |
| Normal Food | 20 | Satiety +20 |
| Premium Food | 50 | Satiety +50, mood +5 |
| Toy | 20 | Mood +20 |
| Bed Upgrade | 200 | Bed level +1 |

## Save Data

During development runs, save files are stored in the `saves/` directory under the project root. The app keeps `save.json` and `save_backup.json`, and writes saves through a temporary file followed by atomic replacement.

## Packaging

PyInstaller is listed as a dependency for future packaging. A simple macOS build command can start from:

```bash
conda run -n petbuddy python -m PyInstaller --windowed --add-data "assets:assets" main.py
```

For Windows, PyInstaller uses a semicolon in `--add-data`:

```bash
conda run -n petbuddy python -m PyInstaller --onefile --windowed --add-data "assets;assets" main.py
```
