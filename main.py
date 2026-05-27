"""桌面宠物放置养成游戏 - 入口"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from storage.save_manager import SaveManager
from ui.pet_window import PetWindow


def get_base_dir() -> str:
    """获取资源基准目录（开发目录或打包后的可执行文件目录）"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_asset_path(*parts: str) -> str:
    """获取资源文件路径"""
    return os.path.join(get_base_dir(), "assets", *parts)


def get_save_dir() -> str:
    """获取存档目录（可执行文件同级或当前目录）"""
    save_dir = os.path.join(get_base_dir(), "saves")
    return save_dir


def load_app_icon() -> QIcon:
    """加载应用图标；缺失时返回空图标，不影响启动。"""
    return QIcon(get_asset_path("app_icon.png"))


def main():
    # macOS 下允许非捆绑应用使用高 DPI
    if sys.platform == "darwin":
        os.environ.setdefault("QT_MAC_WANTS_LAYER", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("桌面宠物")
    app.setQuitOnLastWindowClosed(False)  # 关闭所有窗口不退出，宠物窗口常驻
    app_icon = load_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

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
    if not app_icon.isNull():
        pet_window.setWindowIcon(app_icon)
    pet_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
