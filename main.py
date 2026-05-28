"""桌面宠物放置养成游戏 - 入口"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from storage.save_manager import SaveManager
from ui.pet_window import PetWindow


def get_base_dir() -> str:
    """获取资源基准目录。

    开发时：main.py 所在目录
    打包后：PyInstaller 的 _MEIPASS 临时解压目录
    """
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_asset_path(*parts: str) -> str:
    """获取资源文件路径"""
    return os.path.join(get_base_dir(), "assets", *parts)


def get_save_dir() -> str:
    """获取存档目录。

    开发时：项目根目录下的 saves/
    打包后：系统标准用户数据目录下的 DesktopPet/saves/
    """
    if getattr(sys, "frozen", False):
        if sys.platform == "darwin":
            base = os.path.expanduser("~/Library/Application Support/DesktopPet")
        elif sys.platform == "win32":
            base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "DesktopPet")
        else:
            base = os.path.join(os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")), "DesktopPet")
        return os.path.join(base, "saves")
    return os.path.join(get_base_dir(), "saves")


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
    pet_window = PetWindow(state, save_manager, asset_base=get_base_dir())
    if not app_icon.isNull():
        pet_window.setWindowIcon(app_icon)
    pet_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
