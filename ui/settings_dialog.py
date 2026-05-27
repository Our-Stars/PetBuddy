"""设置对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QCheckBox, QComboBox, QPushButton,
    QHBoxLayout, QMessageBox, QGroupBox,
)
from PySide6.QtCore import Qt
from core.game_state import GameState, PetSize
from storage.save_manager import SaveManager


class SettingsDialog(QDialog):
    def __init__(self, state: GameState, save_manager: SaveManager, parent=None):
        super().__init__(parent)
        self.state = state
        self.save_manager = save_manager
        self.setWindowTitle("设置")
        self.setMinimumWidth(300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 显示设置
        display_group = QGroupBox("显示设置")
        display_form = QFormLayout()

        self.chk_top = QCheckBox("始终置顶")
        self.chk_top.setChecked(self.state.always_on_top)
        self.chk_top.toggled.connect(lambda v: self._set_and_save("always_on_top", v))
        display_form.addRow("置顶：", self.chk_top)

        self.chk_status_text = QCheckBox("显示状态文字")
        self.chk_status_text.setChecked(self.state.show_status_text)
        self.chk_status_text.toggled.connect(lambda v: self._set_and_save("show_status_text", v))
        display_form.addRow("状态文字：", self.chk_status_text)

        self.chk_bubble = QCheckBox("启用气泡提示")
        self.chk_bubble.setChecked(self.state.bubble_tips_enabled)
        self.chk_bubble.toggled.connect(lambda v: self._set_and_save("bubble_tips_enabled", v))
        display_form.addRow("气泡提示：", self.chk_bubble)

        self.cmb_size = QComboBox()
        self.cmb_size.addItems(["小", "中", "大"])
        size_map = {PetSize.SMALL: 0, PetSize.MEDIUM: 1, PetSize.LARGE: 2}
        self.cmb_size.setCurrentIndex(size_map.get(self.state.pet_size, 1))
        self.cmb_size.currentIndexChanged.connect(self._on_size_changed)
        display_form.addRow("宠物大小：", self.cmb_size)

        display_group.setLayout(display_form)
        layout.addWidget(display_group)

        # 交互设置
        interact_group = QGroupBox("交互设置")
        interact_form = QFormLayout()

        self.chk_click_mood = QCheckBox("点击增加心情")
        self.chk_click_mood.setChecked(self.state.click_mood_enabled)
        self.chk_click_mood.toggled.connect(lambda v: self._set_and_save("click_mood_enabled", v))
        interact_form.addRow(self.chk_click_mood)

        self.chk_click_animation = QCheckBox("显示点击动画")
        self.chk_click_animation.setChecked(self.state.click_animation_enabled)
        self.chk_click_animation.toggled.connect(lambda v: self._set_and_save("click_animation_enabled", v))
        interact_form.addRow(self.chk_click_animation)

        self.chk_quiet = QCheckBox("安静模式（减少提示和动画）")
        self.chk_quiet.setChecked(self.state.quiet_mode)
        self.chk_quiet.toggled.connect(lambda v: self._set_and_save("quiet_mode", v))
        interact_form.addRow(self.chk_quiet)

        interact_group.setLayout(interact_form)
        layout.addWidget(interact_group)

        # 存档设置
        save_group = QGroupBox("存档设置")
        save_layout = QHBoxLayout()

        btn_reset = QPushButton("重置存档")
        btn_reset.setStyleSheet("QPushButton { color: red; }")
        btn_reset.clicked.connect(self._reset_save)
        save_layout.addWidget(btn_reset)

        save_group.setLayout(save_layout)
        layout.addWidget(save_group)

        # 关闭按钮
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _on_size_changed(self, index: int):
        size_map = {0: PetSize.SMALL, 1: PetSize.MEDIUM, 2: PetSize.LARGE}
        self.state.pet_size = size_map.get(index, PetSize.MEDIUM)
        self._save_and_apply()

    def _set_and_save(self, name: str, value):
        setattr(self.state, name, value)
        self._save_and_apply()

    def _save_and_apply(self):
        parent = self.parent()
        if parent is not None and hasattr(parent, "apply_settings"):
            parent.apply_settings()
            parent.update()
        self.save_manager.save(self.state)

    def _reset_save(self):
        reply = QMessageBox.question(
            self, "确认重置",
            "确定要重置存档吗？\n此操作将清除当前设备上的所有宠物数据，且无法恢复。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.save_manager.reset()
            # 重置状态为默认
            new_state = GameState()
            self.state.__dict__.update(new_state.__dict__)
            self.chk_top.setChecked(True)
            self.chk_status_text.setChecked(False)
            self.chk_bubble.setChecked(True)
            self.cmb_size.setCurrentIndex(1)
            self.chk_click_mood.setChecked(True)
            self.chk_click_animation.setChecked(True)
            self.chk_quiet.setChecked(False)
            self._save_and_apply()
