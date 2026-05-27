# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

桌面宠物放置养成游戏 — 本地单机版。宠物（QPainter 绘制的橘猫）常驻桌面，用户通过点击、喂食、学习、工作等方式互动。程序关闭后游戏状态暂停，离线期间不产生收益也不惩罚。

## 技术栈

| 模块 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| GUI | PySide6（无边框透明窗口、右键菜单、对话框） |
| 宠物渲染 | QPixmap 加载 PNG 静态图片（`assets/Original static image/`，6 种状态各一张） |
| 本地存档 | JSON 文件（原子写入：先写临时文件再替换） |
| 定时器 | QTimer（主循环 1 秒/次） |
| 打包 | PyInstaller（macOS → .app，Windows → .exe） |
| 环境 | conda 环境 `desktop_pet` |

**不需要**账号系统、网络、数据库、Electron、游戏引擎。

## 项目结构

```
desktop_pet_idle_game/
├── main.py                  # 入口：初始化应用、读档、创建窗口、退出保存
├── requirements.txt         # PySide6>=6.5.0, pyinstaller>=6.0
├── assets/                  # 6 张 PNG 静态图片（每种状态一张）+ 预留素材目录
├── core/                    # 游戏逻辑层（纯 Python，不依赖 PySide6）
│   ├── game_state.py        # GameState 数据类 + PetStatus/PetSize 枚举
│   ├── game_rules.py        # 收益计算、倍率、条件判断、自然金币累积
│   ├── task_system.py       # 学习/工作任务：开始、倒计时、完成结算、取消
│   └── shop_system.py       # 购买、道具使用
├── storage/
│   ├── save_manager.py      # JSON 存档读写、原子写入、备份恢复、默认初始化
│   └── game_state_io.py     # GameState ↔ dict 序列化/反序列化
└── ui/                      # 界面层（依赖 PySide6 + core）
    ├── pet_window.py        # 宠物主窗口：透明无边框、QPainter 橘猫、拖动、点击、右键菜单、主循环
    ├── status_panel.py      # 状态面板（含喂食和停止任务按钮）
    ├── shop_dialog.py       # 商店界面（深色主题）
    ├── settings_dialog.py   # 设置界面
    └── work_dialog.py       # 工作选择界面（深色主题）
```

## 常用命令

```bash
# 激活环境
conda activate desktop_pet

# 安装依赖
pip install -r requirements.txt

# 运行（必须在 desktop_pet_idle_game/ 目录下执行）
cd desktop_pet_idle_game
python main.py

# 打包 (macOS)
pyinstaller --onefile --windowed --add-data "assets:assets" main.py

# 打包 (Windows)
pyinstaller --onefile --windowed --add-data "assets;assets" main.py
```

**导入注意**：项目使用绝对导入（`from core.game_state import ...`），必须以 `desktop_pet_idle_game/` 为工作目录运行。

## 核心架构

### 数据流

```
用户操作 → PySide6 UI → 游戏逻辑层(core) → GameState 对象 → JSON 存档
```

### GameState 关键字段

| 字段 | 类型 | 持久化 | 说明 |
|------|------|--------|------|
| coins | int | 是 | 金币 |
| mood | int | 是 | 心情 0-100 |
| satiety | int | 是 | 饱食度 0-100 |
| knowledge | float | 是 | 学识（支持小数，低状态时收益减半会产生 0.5） |
| status | PetStatus | 是 | 当前状态 |
| food_count / premium_food_count | int | 是 | 普通/高级食物库存 |
| toy_count | int | 是 | 玩具库存 |
| bed_level | int | 是 | 小床等级 |
| current_task / task_remaining_seconds | str/int | 是 | 当前任务名及剩余秒数 |
| position_x / position_y | int | 是 | 窗口位置 |
| pet_size | PetSize | 是 | 宠物大小（small/medium/large） |
| always_on_top | bool | 是 | 置顶开关 |
| show_status_text | bool | 是 | 宠物旁显示状态文字 |
| bubble_tips_enabled | bool | 是 | 气泡提示开关 |
| click_mood_enabled | bool | 是 | 点击是否增加心情（+3） |
| click_animation_enabled | bool | 是 | 点击是否显示开心动画（happy_timer=3） |
| quiet_mode | bool | 是 | 安静模式（抑制提示和动画） |
| last_saved_time | str | 是 | 上次存档时间 ISO 格式 |
| natural_coin_progress | float | 否 | 自然金币累积进度（小数，防止截断损失） |
| elapsed_seconds | int | 否 | 程序运行秒数 |
| last_click_time | float | 否 | 上次点击时间戳（用于 10 秒冷却） |
| happy_timer | int | 否 | 开心状态剩余秒数 |

### 主循环逻辑（_game_tick, 1秒/次）

1. 每 30 秒：`GameRules.add_natural_coin_income()` 按心情倍率累积金币（小数精度，不丢失零头）
2. 每 60 秒：心情 -1、饱食度 -1
3. happy_timer 倒计时
4. `TaskSystem.tick()` 推进任务倒计时（无条件每秒 -1）
5. `TaskSystem.check_completion()` 检查任务是否完成并结算（学习收益在 mood<20 或 satiety<60 时减半）
6. `GameRules.update_status()` 刷新宠物显示状态
7. 有变更或每 45 秒自动保存（`should_save` 或 `elapsed_seconds % 45 == 0`）
8. 置顶模式下每 2 秒 `raise_()` 保持窗口在前

### 心情倍率（影响金币/工作收益）

| 心情范围 | 倍率 |
|----------|------|
| 80-100 | 1.5x |
| 50-79 | 1.0x |
| 20-49 | 0.7x |
| 0-19 | 0.3x |

### 点击互动

- 点击宠物：心情 +3（可在设置中关闭），触发 3 秒开心状态
- 点击冷却：10 秒（`CLICK_COOLDOWN_SECONDS`），冷却期间显示剩余秒数
- 任务中（学习/工作/睡觉）禁止点击互动

### 睡觉

- 时长 30 秒（`SLEEP_DURATION`）
- 完成后心情 +20（`SLEEP_MOOD_RECOVERY`）
- 睡觉期间不能喂食、使用玩具、点击互动
- 学习和工作中不能睡觉

### 商店商品

| 商品 | 价格 | 效果 |
|------|------|------|
| 普通食物 | 20G | 饱食度 +20 |
| 高级食物 | 80G | 饱食度 +50，心情 +5 |
| 玩具 | 50G | 心情 +15（背包道具，可随时使用） |
| 小床升级 | 200G | 小床等级 +1 |

食物和玩具购买后存入背包，通过右键菜单或状态面板使用。

### 饱食度门槛

| 范围 | 效果 |
|------|------|
| 60-100 | 正常 |
| 30-59 | 工作收益减半；学习学识收益减半 |
| 0-29 | 拒绝学习和工作 |

### 状态优先级

```
working / studying > hungry > happy > idle
```

> 注意：hungry 优先级高于 happy，防止饱食度低时仍显示开心状态。

学习和工作互斥，同时只能进行一个。右键菜单可在任务中停止。

### 工作列表

| 工作 | 学识要求 | 时长 | 基础收益 |
|------|----------|------|----------|
| 捡瓶子 | 0 | 60s | 20 |
| 发传单 | 10 | 180s | 100 |
| 咖啡店帮工 | 30 | 300s | 220 |
| 程序员宠物 | 60 | 600s | 520 |
| 神秘顾问 | 120 | 1200s | 1200 |

实际收益 = 基础收益 × 心情倍率 × 饱食度倍率

### 设置对话框项

- **显示设置**：始终置顶、显示状态文字、启用气泡提示、宠物大小（小/中/大）
- **交互设置**：点击增加心情、显示点击动画、安静模式
- **存档设置**：重置存档（需确认）

### 离线规则

程序关闭时所有状态暂停。关闭时正在进行的任务会保存剩余时间，下次启动从剩余时间继续。无离线结算。

### 存档安全

- 写入临时文件 → 重命名替换正式文件
- 保留最近一次备份（save_backup.json）
- 存档损坏时尝试恢复备份
- 重置存档前需用户确认
- 存档目录：`desktop_pet_idle_game/saves/`

### 窗口定位

- `_clamp_to_screen()` 确保宠物不会被拖出屏幕
- 关闭时保存位置，下次启动恢复
- 若保存的位置超出当前屏幕范围，会自动 clamp 到可见区域
