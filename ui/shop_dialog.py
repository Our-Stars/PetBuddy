"""商店对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QScrollArea, QWidget,
    QTabWidget, QSizePolicy,
)
from PySide6.QtCore import Qt
from core.game_state import GameState
from core.shop_system import ShopSystem
from .dialog_styles import DIALOG_STYLE


class ShopDialog(QDialog):
    def __init__(self, state: GameState, save_manager=None, parent=None):
        super().__init__(parent)
        self.state = state
        self.save_manager = save_manager
        self.setWindowTitle("商店")
        self.setMinimumWidth(320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(DIALOG_STYLE)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        self.lbl_coins = QLabel()
        self.lbl_coins.setObjectName("summaryLabel")
        self.lbl_coins.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.lbl_coins)

        tabs = QTabWidget()
        tabs.addTab(self._create_tab("food"), "食物")
        tabs.addTab(self._create_tab("toy"), "玩具")
        layout.addWidget(tabs)

        btn_close = QPushButton("关闭")
        btn_close.setObjectName("secondaryButton")
        btn_close.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self._refresh()

    def _create_tab(self, item_type: str) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 12, 10, 10)
        container_layout.setSpacing(12)

        for item in ShopSystem.get_items_by_type(item_type):
            container_layout.addWidget(self._create_item_card(item))
        container_layout.addStretch()

        scroll.setWidget(container)
        return scroll

    def _create_item_card(self, item: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("optionCard")
        card.setMinimumHeight(118)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        row = QHBoxLayout(card)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(16)

        desc = item.get("desc", "")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        title = QLabel(item["name"])
        title.setObjectName("cardTitle")
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        detail = QLabel(f"价格：{item['price']} 金币\n{desc}")
        detail.setObjectName("cardDetail")
        detail.setWordWrap(True)
        detail.setMinimumHeight(52)
        detail.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        info_layout.addWidget(title)
        info_layout.addWidget(detail)
        row.addLayout(info_layout, 1)

        row.addStretch()

        btn = QPushButton(f"购买（{item['price']}G）")
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn.clicked.connect(lambda checked=False, i=item: self._buy(i))
        row.addWidget(btn)

        return card

    def _buy(self, item: dict):
        ok, msg = ShopSystem.buy(self.state, item["id"])
        if ok:
            if self.save_manager is not None:
                self.save_manager.save(self.state)
            self._refresh()
        # 简单提示通过标题栏显示
        self.setWindowTitle(f"商店 - {msg}")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.setWindowTitle("商店"))

    def _refresh(self):
        self.lbl_coins.setText(f"金币：{self.state.coins} G")
