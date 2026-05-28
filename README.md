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
- Context menu for feeding, studying, working, sleeping, playing, shop, status, and settings
- Feeding, studying, working, sleeping, and playing all open a choice dialog before execution
- Warm pet-themed palette (orange/brown tones) for choice dialogs, shop, status, settings, and the context menu
- Live status panel refresh for task remaining time and active buff timers
- Feeding, playing, and click interactions are unavailable while studying, working, or sleeping
- Study tasks: 5 / 15 / 40 minutes for 1 / 3.5 / 10 knowledge
- Work tasks unlocked by knowledge level
- Sleep tasks: 5 / 15 / 40 minutes with mood recovery
- Shop pages for food and toys, with multiple items and fixed-duration buffs
- Local autosave and task remaining-time persistence
- Configurable pet size, always-on-top mode, and status text
- Bubble tips, click mood gain, and click happy animation are always enabled; quiet mode is always off and is not user-configurable

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
| Mood decay | Idle -0.5/min, studying/working -0.6/min, sleeping no decay |
| Satiety decay | Idle -0.5/min, studying/working -0.6/min, sleeping -0.2/min |
| Click interaction | 10-second cooldown, mood +3 |
| Study | 5 / 15 / 40 minutes, knowledge +1 / +3.5 / +10 |
| Sleep | 5 / 15 / 40 minutes, mood +5 / +18 / +50 |
| Buffs | Higher-tier food can slow satiety decay, and higher-tier toys can slow mood decay; buff duration is fixed by item |

### Initial State

On first launch without an existing save, the pet starts with 0 coins, 0 knowledge, 100 mood, and 100 satiety. Existing saves keep their stored values.

### Mood Multiplier

| Mood | Multiplier |
| --- | ---: |
| 80-100 | 1.5x |
| 50-79 | 1.0x |
| 20-49 | 0.7x |
| 0-19 | 0.3x |

## Jobs

Each job offers multiple duration options. Longer durations have slightly higher hourly rates. You can browse all job options and rewards even before unlocking them.

| Job | Required Knowledge | Duration | Coins | Rate (G/min) |
| --- | ---: | ---: | ---: | ---: |
| Bottle Collector | 0 | 5 / 15 min | 20 / 65 | 4.00 / 4.33 |
| Flyer Distributor | 20 | 5 / 15 / 30 min | 40 / 128 / 270 | 8.00 / 8.53 / 9.00 |
| Delivery Rider | 100 | 10 / 30 min | 95 / 300 | 9.50 / 10.00 |
| Barista | 200 | 10 / 30 / 60 min | 105 / 330 / 690 | 10.50 / 11.00 / 11.50 |
| Pet Streamer | 300 | 15 / 30 / 60 min | 180 / 375 / 780 | 12.00 / 12.50 / 13.00 |
| Pet Programmer | 400 | 15 / 30 / 60 min | 203 / 420 / 900 | 13.53 / 14.00 / 15.00 |
| Mystery Consultant | 500 | 20 / 40 / 60 min | 310 / 640 / 1000 | 15.50 / 16.00 / 16.67 |

Once knowledge exceeds 500 (the highest job requirement), each extra point grants +0.2% work coin bonus, capped at +100% (knowledge 1000). Old saves with "Cafe Helper" are automatically mapped to "Barista".

## Shop

The shop is split into Food and Toys pages.

| Food | Price | Effect |
| --- | ---: | --- |
| Bread | 15 | Satiety +18 |
| Milk | 25 | Satiety +25, mood +2 |
| Cola | 30 | Satiety +8, mood +12 |
| Lollipop | 35 | Satiety +5, mood +18 |
| Cat Meal | 70 | Satiety +65, mood +6; satiety decay -20% for 20 minutes |
| Deluxe Cat Can | 130 | Satiety +95, mood +12; satiety decay -35% for 40 minutes |

| Toy | Price | Effect |
| --- | ---: | --- |
| Paper Ball | 10 | Mood +8 |
| Teaser Wand | 25 | Mood +22 |
| Scratching Board | 55 | Mood +40; mood decay -15% for 15 minutes |
| Yarn Ball | 75 | Mood +52; mood decay -20% for 20 minutes |
| Cat Tree | 150 | Mood +85; mood decay -35% for 40 minutes |

## Save Data

During development runs, save files are stored in the `saves/` directory under the project root. The app keeps `save.json` and `save_backup.json`, and writes saves through a temporary file followed by atomic replacement.

## UI Notes

PetBuddy uses static pet images from `assets/Original static image/` for each pet state. The main window draws overlays such as status text and task progress with `QPainter`.

Most modal UI uses the shared warm pet-themed palette in `ui/dialog_styles.py`, including choice dialogs, the shop, status, settings, and the right-click context menu. The status panel keeps refreshing while it is open, so remaining task time and buff timers stay current.

## Packaging

PyInstaller is listed as a dependency for future packaging. A simple macOS build command can start from:

```bash
conda run -n petbuddy python -m PyInstaller --windowed --add-data "assets:assets" main.py
```

For Windows, PyInstaller uses a semicolon in `--add-data`:

```bash
conda run -n petbuddy python -m PyInstaller --onefile --windowed --add-data "assets;assets" main.py
```
