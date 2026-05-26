# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

桌面宠物放置养成游戏 — 本地单机版。宠物常驻桌面，用户通过点击、喂食、学习、工作等方式互动。程序关闭后游戏状态暂停，离线期间不产生收益也不惩罚。

## 技术栈

| 模块 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| GUI | PySide6（无边框透明窗口、右键菜单、对话框） |
| 本地存档 | JSON 文件（原子写入：先写临时文件再替换） |
| 定时器 | QTimer（主循环 1 秒/次） |
| 打包 | PyInstaller（macOS → .app，Windows → .exe） |

**不需要**账号系统、网络、数据库、Electron、游戏引擎。

## 项目结构

```
desktop_pet_idle_game/
├── main.py                  # 入口：初始化应用、读档、创建窗口、退出保存
├── requirements.txt
├── assets/                  # 图片/GIF/图标资源
│   ├── pet_idle.gif
│   ├── pet_happy.gif
│   ├── pet_hungry.gif
│   ├── pet_studying.gif
│   └── pet_working.gif
├── core/                    # 游戏逻辑层
│   ├── game_state.py        # 核心数据类（金币、心情、饱食度、学识等）
│   ├── game_rules.py        # 收益计算、倍率、条件判断
│   ├── task_system.py       # 学习/工作任务：开始、倒计时、完成结算
│   └── shop_system.py       # 购买、道具使用
├── storage/
│   └── save_manager.py      # JSON 存档读写、默认初始化、异常保护+备份
└── ui/                      # 界面层
    ├── pet_window.py        # 宠物主窗口：透明无边框、置顶、拖动、点击、右键菜单
    ├── status_panel.py      # 状态面板
    ├── shop_dialog.py       # 商店界面
    ├── settings_dialog.py   # 设置界面
    └── work_dialog.py       # 工作选择界面
```

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python main.py

# 打包 (macOS)
pyinstaller --onefile --windowed --add-data "assets:assets" main.py

# 打包 (Windows)
pyinstaller --onefile --windowed --add-data "assets;assets" main.py
```

## 核心架构

### 数据流

```
用户操作 → PySide6 UI → 游戏逻辑层 → GameState 对象 → JSON 存档
```

### 主循环 (QTimer, 1秒/次)

| 规则 | 频率 |
|------|------|
| 自然金币 | 每 10 秒 +1（× 心情倍率） |
| 心情下降 | 每 60 秒 -1 |
| 饱食度下降 | 每 60 秒 -1 |
| 自动保存 | 每 30-60 秒 |

### 核心数值

| 属性 | 范围 | 初始值 |
|------|------|--------|
| 金币 (coins) | 无上限 | 0 |
| 心情 (mood) | 0-100 | 80 |
| 饱食度 (satiety) | 0-100 | 80 |
| 学识 (knowledge) | 无上限 | 0 |

### 心情倍率（影响金币/工作收益）

| 心情范围 | 倍率 |
|----------|------|
| 80-100 | 1.5x |
| 50-79 | 1.0x |
| 20-49 | 0.7x |
| 0-19 | 0.3x |

### 饱食度门槛

| 范围 | 效果 |
|------|------|
| 60-100 | 正常 |
| 30-59 | 工作/学习收益降低 |
| 0-29 | 拒绝学习和工作 |

### 状态优先级

```
working/studying > hungry > happy > idle
```

学习和工作互斥，同时只能进行一个。

### 工作列表（学识要求递增）

| 工作 | 学识要求 | 时长 | 收益 |
|------|----------|------|------|
| 捡瓶子 | 0 | 60s | 20 |
| 发传单 | 10 | 180s | 100 |
| 咖啡店帮工 | 30 | 300s | 220 |
| 程序员宠物 | 60 | 600s | 520 |
| 神秘顾问 | 120 | 1200s | 1200 |

### 离线规则

程序关闭时所有状态暂停。关闭时正在进行的任务会保存剩余时间，下次启动从剩余时间继续。无离线结算。

### 存档安全

- 写入临时文件 → 重命名替换正式文件
- 保留最近一次备份
- 存档损坏时尝试恢复备份
- 重置存档前需用户确认
