"""商店对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QScrollArea, QWidget,
)
from PySide6.QtCore import Qt
from core.game_state import GameState
from core.shop_system import ShopSystem

CARD_STYLE = """
QFrame {
    background: #f8f8f8;
    border: 1px solid #d9d9d9;
    border-radius: 8px;
    padding: 8px;
    margin: 4px;
}
QLabel {
    color: #222222;
    background: transparent;
}
"""

DIALOG_STYLE = """
QDialog, QScrollArea, QWidget {
    background: #303030;
    color: #ffffff;
}
QLabel {
    color: #ffffff;
}
QPushButton {
    min-height: 28px;
    padding: 4px 12px;
}
QPushButton:disabled {
    color: #777777;
    background: #eeeeee;
    border: 1px solid #cccccc;
}
"""


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

        self.lbl_coins = QLabel()
        self.lbl_coins.setStyleSheet("font-size: 16px; font-weight: bold; margin: 8px;")
        layout.addWidget(self.lbl_coins)

        # 商品列表
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        container_layout = QVBoxLayout(container)

        for item in ShopSystem.get_items():
            container_layout.addWidget(self._create_item_card(item))

        scroll.setWidget(container)
        layout.addWidget(scroll)

        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self._refresh()

    def _create_item_card(self, item: dict) -> QFrame:
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(CARD_STYLE)

        row = QHBoxLayout(card)

        desc = item.get("desc", "")
        info = QLabel(f"{item['name']}\n价格：{item['price']} 金币\n{desc}")
        info.setStyleSheet("font-size: 14px; color: #222222;")
        row.addWidget(info)

        row.addStretch()

        btn = QPushButton(f"购买（{item['price']}G）")
        btn.clicked.connect(lambda checked=False, i=item: self._buy(i))
        row.addWidget(btn)

        return card

    def _buy(self, item: dict):
        ok, msg = ShopSystem.buy(self.state, item["name"])
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
