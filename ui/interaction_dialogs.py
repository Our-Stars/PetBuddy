"""喂食、学习、睡觉和玩耍选择对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt

from core.game_rules import GameRules
from core.game_state import GameState
from core.shop_system import ShopSystem
from core.task_system import STUDY_OPTIONS, SLEEP_OPTIONS
from .dialog_styles import DIALOG_STYLE


class OptionDialog(QDialog):
    def __init__(self, state: GameState, title: str, parent=None):
        super().__init__(parent)
        self.state = state
        self.selected_option = None
        self.setWindowTitle(title)
        self.setMinimumWidth(360)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(DIALOG_STYLE)

    def _create_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        return layout

    def _add_summary(self, layout: QVBoxLayout, text: str):
        label = QLabel(text)
        label.setObjectName("summaryLabel")
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(label)

    def _add_empty_message(self, layout: QVBoxLayout, text: str):
        label = QLabel(text)
        label.setObjectName("emptyLabel")
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(label)

    def _add_card(
        self,
        layout: QVBoxLayout,
        title: str,
        detail: str,
        button_text: str,
        enabled: bool,
        value,
    ):
        card = QFrame()
        card.setObjectName("optionCard")
        card.setEnabled(enabled)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        row = QHBoxLayout(card)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(16)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        lbl_title = QLabel(title)
        lbl_title.setObjectName("cardTitle")
        lbl_detail = QLabel(detail)
        lbl_detail.setObjectName("cardDetail")
        lbl_detail.setWordWrap(True)
        info_layout.addWidget(lbl_title)
        info_layout.addWidget(lbl_detail)
        row.addLayout(info_layout, 1)
        row.addStretch()

        button = QPushButton(button_text)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setEnabled(enabled)
        if enabled:
            button.clicked.connect(lambda checked=False, v=value: self._select(v))
        row.addWidget(button)

        layout.addWidget(card)

    def _add_cancel(self, layout: QVBoxLayout):
        btn_close = QPushButton("取消")
        btn_close.setObjectName("secondaryButton")
        btn_close.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_close.clicked.connect(self.reject)
        layout.addStretch()
        layout.addWidget(btn_close)

    def _select(self, value):
        self.selected_option = value
        self.accept()


class FeedDialog(OptionDialog):
    def __init__(self, state: GameState, parent=None):
        super().__init__(state, "选择食物", parent)
        self._init_ui()

    def _init_ui(self):
        layout = self._create_layout()
        self._add_summary(layout, f"当前饱食：{self.state.satiety:.1f} | 当前心情：{self.state.mood:.1f}")

        can_feed, reason = GameRules.can_feed(self.state)
        if reason.startswith("没有食物"):
            reason = ""
        food_items = [
            item for item in ShopSystem.get_items_by_type("food")
            if ShopSystem.get_inventory_count(self.state, item["id"]) > 0
        ]
        if not food_items:
            self._add_empty_message(layout, "没有食物了")
            self._add_cancel(layout)
            return

        for item in food_items:
            enabled = can_feed
            button_text = "喂食" if enabled else "无法喂食"
            count = ShopSystem.get_inventory_count(self.state, item["id"])
            detail = f"剩余：{count} | {item['desc']}"
            if reason:
                detail = f"{detail} | {reason}"
            self._add_card(layout, item["name"], detail, button_text, enabled, item["id"])

        self._add_cancel(layout)


class StudyDialog(OptionDialog):
    def __init__(self, state: GameState, parent=None):
        super().__init__(state, "选择学习", parent)
        self._init_ui()

    def _init_ui(self):
        layout = self._create_layout()
        self._add_summary(layout, f"当前学识：{self.state.knowledge:g} | 当前饱食：{self.state.satiety:.1f}")

        can_study, reason = GameRules.can_study(self.state)
        for option in STUDY_OPTIONS:
            mins = option["duration"] // 60
            enabled = can_study
            button_text = "开始学习" if enabled else "无法学习"
            detail = f"时长：{mins}分钟 | 完成后：学识 +{option['knowledge_gain']:g}"
            if reason:
                detail = f"{detail} | {reason}"
            self._add_card(layout, option["name"], detail, button_text, enabled, option["name"])

        self._add_cancel(layout)


class SleepDialog(OptionDialog):
    def __init__(self, state: GameState, parent=None):
        super().__init__(state, "选择睡觉", parent)
        self._init_ui()

    def _init_ui(self):
        layout = self._create_layout()
        self._add_summary(layout, f"当前心情：{self.state.mood:.1f} | 当前饱食：{self.state.satiety:.1f}")

        can_sleep, reason = GameRules.can_sleep(self.state)
        for option in SLEEP_OPTIONS:
            mins = option["duration"] // 60
            enabled = can_sleep
            button_text = "开始睡觉" if enabled else "无法睡觉"
            detail = f"时长：{mins}分钟 | 心情 +{option['mood_recovery']}"
            if reason:
                detail = f"{detail} | {reason}"
            self._add_card(layout, option["name"], detail, button_text, enabled, option["name"])

        self._add_cancel(layout)


class PlayDialog(OptionDialog):
    def __init__(self, state: GameState, parent=None):
        super().__init__(state, "选择玩耍", parent)
        self._init_ui()

    def _init_ui(self):
        layout = self._create_layout()
        self._add_summary(layout, f"当前心情：{self.state.mood:.1f}")

        can_play, reason = GameRules.can_use_toy(self.state)
        if reason.startswith("没有玩具"):
            reason = ""
        toy_items = [
            item for item in ShopSystem.get_items_by_type("toy")
            if ShopSystem.get_inventory_count(self.state, item["id"]) > 0
        ]
        if not toy_items:
            self._add_empty_message(layout, "没有玩具了")
            self._add_cancel(layout)
            return

        for item in toy_items:
            enabled = can_play
            button_text = "玩耍" if enabled else "无法玩耍"
            count = ShopSystem.get_inventory_count(self.state, item["id"])
            detail = f"剩余：{count} | {item['desc']}"
            if reason:
                detail = f"{detail} | {reason}"
            self._add_card(layout, item["name"], detail, button_text, enabled, item["id"])

        self._add_cancel(layout)
