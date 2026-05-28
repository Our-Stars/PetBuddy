"""工作选择对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QScrollArea, QWidget,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from core.game_rules import GameRules
from core.game_state import GameState
from core.task_system import JOBS
from .dialog_styles import DIALOG_STYLE


class WorkDialog(QDialog):
    def __init__(self, state: GameState, parent=None):
        super().__init__(parent)
        self.state = state
        self.selected_job = None
        self.setWindowTitle("选择工作")
        self.setMinimumWidth(380)
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
        self._container_layout = QVBoxLayout(container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._container_layout.setSpacing(12)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        btn_close = QPushButton("取消")
        btn_close.setObjectName("secondaryButton")
        btn_close.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)

        self._build_cards()

    def _build_cards(self):
        can_work, reason = GameRules.can_work(self.state)
        self.lbl_knowledge.setText(f"当前学识：{self.state.knowledge}")
        self.lbl_reason.setText("" if can_work else reason)

        for job in JOBS:
            for option in job["options"]:
                self._container_layout.addWidget(
                    self._create_option_card(job, option, can_work))

    def _create_option_card(self, job: dict, option: dict, can_work: bool) -> QFrame:
        card = QFrame()
        card.setObjectName("optionCard")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        unlocked = self.state.knowledge >= job["knowledge"]
        enabled = can_work and unlocked
        card.setEnabled(enabled)

        row = QHBoxLayout(card)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(16)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        title = QLabel(option["label"])
        title.setObjectName("cardTitle")
        mins = option["duration"] // 60
        detail = QLabel(f"学识要求：{job['knowledge']} | 时长：{mins}分钟 | 收益：{option['reward']}G")
        detail.setObjectName("cardDetail")
        detail.setWordWrap(True)
        info_layout.addWidget(title)
        info_layout.addWidget(detail)
        row.addLayout(info_layout, 1)
        row.addStretch()

        if not unlocked:
            btn_text = "学识不足"
        elif not can_work:
            btn_text = "无法工作"
        else:
            btn_text = "开始工作"
        btn = QPushButton(btn_text)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn.setEnabled(enabled)
        if enabled:
            btn.clicked.connect(lambda checked=False, o=option: self._select(o))
        row.addWidget(btn)

        return card

    def _select(self, option: dict):
        self.selected_job = option["label"]
        self.accept()
