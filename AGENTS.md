# AGENTS.md

This file provides guidance to Codex when working with code in this repository.

除非用户特别要求，否则使用中文沟通。修改前先阅读相关源码，文档内容要区分“当前已实现”和“需求规划”。

## 项目概述

这是一个本地单机桌面宠物放置养成游戏。应用使用 PySide6 创建透明、无边框、可拖动、可置顶的桌面宠物窗口；用户可通过左键点击、右键菜单、喂食、学习、工作、商店、状态面板和设置进行互动。

程序关闭后没有离线结算。正在进行的学习或工作任务会把剩余秒数写入存档，下次启动后从剩余时间继续。

## 技术栈

| 模块 | 当前实现 |
|------|----------|
| 语言 | Python 3.11+ |
| GUI | PySide6 |
| 宠物显示 | `QPainter` 直接绘制橘猫形象和不同表情 |
| 本地存档 | JSON，临时文件写入后 `os.replace` 原子替换 |
| 定时器 | `QTimer`，主循环每 1 秒执行 |
| 打包 | 需求中规划使用 PyInstaller；仓库当前未包含打包脚本 |

不要引入账号系统、网络服务、数据库、Electron、Tauri 或游戏引擎，除非用户明确改变项目方向。

## 目录结构

```text
desktop_pet_idle_game/
├── main.py
├── requirements.txt
├── assets/
├── core/
│   ├── game_state.py
│   ├── game_rules.py
│   ├── task_system.py
│   └── shop_system.py
├── storage/
│   ├── save_manager.py
│   └── game_state_io.py
├── ui/
│   ├── pet_window.py
│   ├── status_panel.py
│   ├── shop_dialog.py
│   ├── settings_dialog.py
│   └── work_dialog.py
└── saves/
    ├── save.json
    └── save_backup.json
```

根目录还包含：

- `需求文档.txt`：产品需求与规划，不一定完全等同当前实现。
- `CLAUDE.md`：Claude Code 说明，可能与本文件内容相似。
- `AGENTS.md`：本文件，给 Codex 使用。

## 常用命令

默认使用 `desktop_pet` conda 环境运行：

```bash
conda run -n desktop_pet python -m pip install -r desktop_pet_idle_game/requirements.txt
conda run -n desktop_pet python desktop_pet_idle_game/main.py
```

可选打包命令：

```bash
# macOS
cd desktop_pet_idle_game
PYINSTALLER_CONFIG_DIR=/tmp/desktop_pet_pyinstaller_config \
  conda run -n desktop_pet python -m PyInstaller --windowed --add-data "assets:assets" main.py

# Windows
conda run -n desktop_pet python -m PyInstaller --onefile --windowed --add-data "assets;assets" main.py
```

当前仓库使用 `unittest` 测试核心逻辑和 Qt offscreen 主窗口行为：

```bash
conda run -n desktop_pet python -m unittest discover -s tests
```

改动核心逻辑或 UI 行为后，同时运行 `conda run -n desktop_pet python -m compileall desktop_pet_idle_game tests` 和上述测试命令。

## 架构与数据流

```text
用户操作
  -> PySide6 UI
  -> core 游戏逻辑
  -> GameState
  -> storage JSON 存档
```

职责边界：

- `main.py`：创建 `QApplication`、加载存档、创建 `PetWindow`。
- `core/game_state.py`：定义 `GameState`、`PetStatus`、`PetSize` 和基础取值约束。
- `core/game_rules.py`：点击冷却、心情倍率、饱食度倍率、学习/工作/喂食条件、状态优先级。
- `core/task_system.py`：学习与工作任务配置、开始任务、倒计时、完成结算。
- `core/shop_system.py`：商品定义、购买、普通/高级食物使用。
- `storage/game_state_io.py`：`GameState` 与 JSON dict 的序列化和反序列化。
- `storage/save_manager.py`：读写 `save.json`、维护 `save_backup.json`、重置存档。
- `ui/pet_window.py`：主窗口、绘制、拖动、点击互动、右键菜单、主循环、自动保存。
- `ui/status_panel.py`：展示金币、心情、饱食度、学识、状态、任务和库存。
- `ui/shop_dialog.py`：商店列表和购买操作。
- `ui/work_dialog.py`：工作列表、解锁判断、工作选择。
- `ui/settings_dialog.py`：置顶、大小、安静模式和重置存档。

## 当前游戏规则

主循环在 `PetWindow._game_tick()` 中由 `QTimer` 每秒驱动。

| 规则 | 当前实现 |
|------|----------|
| 自然金币 | 每 10 秒按心情倍率累积自然收益，金币为整数入账 |
| 心情下降 | 每 60 秒 -1 |
| 饱食度下降 | 每 60 秒 -1 |
| 自动保存 | 每 45 秒保存一次 |
| 左键点击 | 10 秒冷却，心情 +3，开心 3 秒并立即保存 |
| 学习 | 60 秒，完成后学识 +1 |
| 工作 | 根据工作配置给金币，受心情和饱食度倍率影响 |

核心状态默认值：

| 属性 | 默认值 |
|------|--------|
| `coins` | 0 |
| `mood` | 80 |
| `satiety` | 80 |
| `knowledge` | 0 |
| `food_count` | 0 |
| `premium_food_count` | 0 |
| `bed_level` | 0 |
| `position_x` / `position_y` | 1200 / 700 |
| `pet_size` | `medium` |
| `always_on_top` | `True` |
| `show_status_text` | `False` |
| `bubble_tips_enabled` | `True` |
| `click_mood_enabled` | `True` |
| `click_animation_enabled` | `True` |
| `quiet_mode` | `False` |

心情倍率：

| 心情范围 | 倍率 |
|----------|------|
| 80-100 | 1.5 |
| 50-79 | 1.0 |
| 20-49 | 0.7 |
| 0-19 | 0.3 |

饱食度规则：

| 饱食度范围 | 效果 |
|------------|------|
| 60-100 | 学习/工作正常 |
| 30-59 | 工作收益 0.5 倍；学习进度减速 |
| 0-29 | 拒绝学习和工作 |

状态优先级在 `GameRules.update_status()` 中体现：

```text
studying/working 保持不变
satiety < 30 -> hungry
happy_timer > 0 -> happy
否则 -> idle
```

学习和工作互斥，同时只能进行一个。

## 工作与商店配置

工作配置位于 `core/task_system.py` 的 `JOBS`：

| 工作 | 学识要求 | 时长 | 基础收益 |
|------|----------|------|----------|
| 捡瓶子 | 0 | 60s | 20 |
| 发传单 | 10 | 180s | 100 |
| 咖啡店帮工 | 30 | 300s | 220 |
| 程序员宠物 | 60 | 600s | 520 |
| 神秘顾问 | 120 | 1200s | 1200 |

商品配置位于 `core/shop_system.py` 的 `SHOP_ITEMS`：

| 商品 | 价格 | 当前效果 |
|------|------|----------|
| 普通食物 | 20 | 购买后库存 +1；使用后饱食度 +20 |
| 高级食物 | 80 | 购买后库存 +1；使用后饱食度 +50、心情 +5 |
| 玩具 | 50 | 购买时立即心情 +15 |
| 小床升级 | 200 | 购买时 `bed_level` +1 |

## 存档规则

开发运行时，存档目录是 `desktop_pet_idle_game/saves/`。打包后，存档目录位于可执行文件同级的 `saves/`。

`SaveManager.save()` 会：

1. 更新 `last_saved_time`。
2. 将 `GameState` 序列化为 JSON。
3. 在存档目录写入临时 `.json` 文件。
4. 如果正式存档存在，复制为 `save_backup.json`。
5. 用 `os.replace()` 替换 `save.json`。

`SaveManager.load()` 会先读 `save.json`，失败后尝试 `save_backup.json`，都失败则返回 `None`，由 `main.py` 创建默认 `GameState`。

重置存档在 `SettingsDialog._reset_save()` 中有确认弹窗，不要绕过用户确认删除存档，除非用户明确要求。

## 开发注意事项

- 保持本地单机和低打扰定位。新功能优先放在现有 `core`、`storage`、`ui` 分层中。
- 修改游戏数值时同步更新 `core` 配置、UI 展示和本文档。
- 修改 `GameState` 持久化字段时，同时更新 `storage/game_state_io.py` 的序列化和反序列化。
- 不要把运行时字段 `elapsed_seconds`、`last_click_time`、`happy_timer`、`natural_coin_progress` 写入存档，除非明确改变存档设计。
- `quiet_mode` 会抑制气泡提示和点击/喂食动画；新增提示或动画时也要遵守该开关。
- `assets/` 当前不参与宠物绘制；主宠物形象由 `ui/pet_window.py` 的绘制函数生成。
- UI 修改要注意透明窗口、无边框、置顶和拖动行为。
- 项目目前没有网络依赖，新增依赖前先确认确有必要，并更新 `requirements.txt`。
