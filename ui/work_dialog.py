"""工作选择对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QScrollArea, QWidget,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from core.game_rules import GameRules
from core.game_state import GameState
from .dialog_styles import DIALOG_STYLE


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
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        self.lbl_knowledge = QLabel()
        self.lbl_knowledge.setObjectName("summaryLabel")
        self.lbl_knowledge.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.lbl_knowledge)

        self.lbl_reason = QLabel()
        self.lbl_reason.setObjectName("reasonLabel")
        layout.addWidget(self.lbl_reason)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(12)

        from core.task_system import JOBS
        for job in JOBS:
            container_layout.addWidget(self._create_job_card(job))

        scroll.setWidget(container)
        layout.addWidget(scroll)

        btn_close = QPushButton("取消")
        btn_close.setObjectName("secondaryButton")
        btn_close.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)

        self._refresh()

    def _create_job_card(self, job: dict) -> QFrame:
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        row = QHBoxLayout(card)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(16)

        mins = job["duration"] // 60
        can_work, _ = GameRules.can_work(self.state)
        unlocked = self.state.knowledge >= job["knowledge"]
        enabled = can_work and unlocked
        card.setObjectName("optionCard")
        card.setEnabled(enabled)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        title = QLabel(job["name"])
        title.setObjectName("cardTitle")
        detail = QLabel(f"学识要求：{job['knowledge']} | 时长：{mins}分钟 | 收益：{job['reward']}G")
        detail.setObjectName("cardDetail")
        detail.setWordWrap(True)
        info_layout.addWidget(title)
        info_layout.addWidget(detail)
        row.addLayout(info_layout, 1)

        row.addStretch()

        btn = QPushButton("开始工作" if enabled else ("无法工作" if unlocked else "未解锁"))
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn.setEnabled(enabled)
        if enabled:
            btn.clicked.connect(lambda checked=False, j=job: self._select(j))
        row.addWidget(btn)

        return card

    def _select(self, job: dict):
        self.selected_job = job["name"]
        self.accept()

    def _refresh(self):
        self.lbl_knowledge.setText(f"当前学识：{self.state.knowledge}")
        can_work, reason = GameRules.can_work(self.state)
        self.lbl_reason.setText("" if can_work else reason)
