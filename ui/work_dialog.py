"""工作选择对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QScrollArea,
    QWidget, QComboBox, QSizePolicy,
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
        self.setMinimumWidth(400)
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
        self._container_layout.setSpacing(10)

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
            self._container_layout.addWidget(
                self._create_job_card(job, can_work))

    def _create_job_card(self, job: dict, can_work: bool) -> QFrame:
        card = QFrame()
        card.setObjectName("optionCard")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        unlocked = self.state.knowledge >= job["knowledge"]
        enabled = can_work and unlocked
        card.setEnabled(enabled)

        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(14, 12, 14, 12)
        vbox.setSpacing(8)

        # 第一行：工种名 + 学识要求
        header = QHBoxLayout()
        title = QLabel(job["name"])
        title.setObjectName("cardTitle")
        header.addWidget(title)
        header.addStretch()
        req = QLabel(f"学识 {job['knowledge']}")
        req.setObjectName("cardDetail")
        header.addWidget(req)
        vbox.addLayout(header)

        # 第二行：时长下拉框 + 收益 + 按钮
        controls = QHBoxLayout()
        controls.setSpacing(10)

        lbl_duration = QLabel("时长：")
        lbl_duration.setObjectName("cardDetail")
        controls.addWidget(lbl_duration)

        combo = QComboBox()
        combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        combo.setMinimumWidth(120)
        for opt in job["options"]:
            mins = opt["duration"] // 60
            combo.addItem(f"{mins}分钟", opt)
        combo.setEnabled(enabled)
        controls.addWidget(combo)

        lbl_reward = QLabel()
        lbl_reward.setObjectName("cardDetail")
        lbl_reward.setMinimumWidth(80)
        controls.addWidget(lbl_reward)

        controls.addStretch()

        if not unlocked:
            btn_text = "学识不足"
        elif not can_work:
            btn_text = "无法工作"
        else:
            btn_text = "开始工作"
        btn = QPushButton(btn_text)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn.setEnabled(enabled)
        controls.addWidget(btn)

        vbox.addLayout(controls)

        # 联动：下拉框切换时更新收益显示
        def _update_reward():
            opt = combo.currentData()
            if opt:
                lbl_reward.setText(f"收益：{opt['reward']}G")
            else:
                lbl_reward.setText("收益：--")

        combo.currentIndexChanged.connect(lambda: _update_reward())
        _update_reward()

        # 按钮点击：取当前下拉框选中的档位
        btn.clicked.connect(
            lambda checked=False, c=combo: self._select(c.currentData()))

        return card

    def _select(self, option: dict):
        self.selected_job = option["label"]
        self.accept()
