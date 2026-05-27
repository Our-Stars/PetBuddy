"""桌面宠物放置养成游戏 - 入口"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from storage.save_manager import SaveManager
from ui.pet_window import PetWindow


def get_save_dir() -> str:
    """获取存档目录（可执行文件同级或当前目录）"""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(base, "saves")
    return save_dir


def main():
    # macOS 下允许非捆绑应用使用高 DPI
    if sys.platform == "darwin":
        os.environ.setdefault("QT_MAC_WANTS_LAYER", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("桌面宠物")
    app.setQuitOnLastWindowClosed(False)  # 关闭所有窗口不退出，宠物窗口常驻

    # 加载存档
    save_dir = get_save_dir()
    save_manager = SaveManager(save_dir)
    state = save_manager.load()

    if state is None:
        from core.game_state import GameState
        state = GameState()
        print("[Main] 使用默认初始状态")

    # 创建宠物窗口
    pet_window = PetWindow(state, save_manager)
    pet_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
