"""工作选择对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QScrollArea, QWidget,
)
from PySide6.QtCore import Qt
from core.game_state import GameState
from core.task_system import TaskSystem

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


class WorkDialog(QDialog):
    def __init__(self, state: GameState, parent=None):
        super().__init__(parent)
        self.state = state
        self.selected_job = None
        self.setWindowTitle("选择工作")
        self.setMinimumWidth(350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(DIALOG_STYLE)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_knowledge = QLabel()
        self.lbl_knowledge.setStyleSheet("font-size: 16px; font-weight: bold; margin: 8px;")
        layout.addWidget(self.lbl_knowledge)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        container_layout = QVBoxLayout(container)

        from core.task_system import JOBS
        for job in JOBS:
            container_layout.addWidget(self._create_job_card(job))

        scroll.setWidget(container)
        layout.addWidget(scroll)

        btn_close = QPushButton("取消")
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)

        self._refresh()

    def _create_job_card(self, job: dict) -> QFrame:
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(CARD_STYLE)

        row = QHBoxLayout(card)

        mins = job["duration"] // 60
        info = QLabel(f"{job['name']}\n学识要求：{job['knowledge']} | 时长：{mins}分钟 | 收益：{job['reward']}G")
        info.setStyleSheet("font-size: 13px; color: #222222;")
        row.addWidget(info)

        row.addStretch()

        unlocked = self.state.knowledge >= job["knowledge"]
        btn = QPushButton("开始工作" if unlocked else "未解锁")
        btn.setEnabled(unlocked)
        if unlocked:
            btn.clicked.connect(lambda checked=False, j=job: self._select(j))
        row.addWidget(btn)

        return card

    def _select(self, job: dict):
        self.selected_job = job["name"]
        self.accept()

    def _refresh(self):
        self.lbl_knowledge.setText(f"当前学识：{self.state.knowledge}")
