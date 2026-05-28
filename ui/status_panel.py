"""状态面板对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QGroupBox, QFormLayout, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from core.game_state import GameState, PetStatus
from core.shop_system import ShopSystem
from .dialog_styles import DIALOG_STYLE

STATUS_LABELS = {
    PetStatus.IDLE: "空闲",
    PetStatus.HAPPY: "开心",
    PetStatus.HUNGRY: "饥饿",
    PetStatus.STUDYING: "学习中",
    PetStatus.WORKING: "工作中",
    PetStatus.SLEEPING: "睡觉中",
}


class StatusPanel(QDialog):
    def __init__(self, state: GameState, save_manager=None, parent=None):
        super().__init__(parent)
        self.state = state
        self.save_manager = save_manager
        self.setWindowTitle("宠物状态")
        self.setMinimumWidth(360)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(DIALOG_STYLE)
        self._init_ui()
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(1000)
        self.refresh_timer.timeout.connect(self._refresh)
        self.refresh_timer.start()
        self._refresh()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        group = QGroupBox("核心状态")
        form = QFormLayout()
        form.setContentsMargins(6, 8, 6, 6)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(10)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.lbl_coins = QLabel()
        self.lbl_mood = QLabel()
        self.lbl_satiety = QLabel()
        self.lbl_knowledge = QLabel()
        self.lbl_status = QLabel()
        self.lbl_task = QLabel()
        self.lbl_inventory = QLabel()
        self.lbl_satiety_buff = QLabel()
        self.lbl_mood_buff = QLabel()
        self.lbl_inventory.setWordWrap(True)
        self.lbl_task.setWordWrap(True)
        self.lbl_satiety_buff.setWordWrap(True)
        self.lbl_mood_buff.setWordWrap(True)
        for label in (
            self.lbl_coins, self.lbl_mood, self.lbl_satiety, self.lbl_knowledge,
            self.lbl_status, self.lbl_task, self.lbl_inventory,
            self.lbl_satiety_buff, self.lbl_mood_buff,
        ):
            label.setObjectName("fieldValue")
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        form.addRow("金币：", self.lbl_coins)
        form.addRow("心情：", self.lbl_mood)
        form.addRow("饱食度：", self.lbl_satiety)
        form.addRow("学识：", self.lbl_knowledge)
        form.addRow("状态：", self.lbl_status)
        form.addRow("当前任务：", self.lbl_task)
        form.addRow("库存：", self.lbl_inventory)
        form.addRow("饱食Buff：", self.lbl_satiety_buff)
        form.addRow("心情Buff：", self.lbl_mood_buff)
        group.setLayout(form)
        layout.addWidget(group)

    def _refresh(self):
        s = self.state
        self.lbl_coins.setText(f"{s.coins:.1f}")
        self.lbl_mood.setText(f"{s.mood:.1f} / 100.0")
        self.lbl_satiety.setText(f"{s.satiety:.1f} / 100.0")
        self.lbl_knowledge.setText(f"{s.knowledge:.1f}")
        self.lbl_status.setText(STATUS_LABELS.get(s.status, "未知"))

        if s.current_task:
            mins = s.task_remaining_seconds // 60
            secs = s.task_remaining_seconds % 60
            self.lbl_task.setText(f"{s.current_task}（剩余 {mins}分{secs:02d}秒）")
        else:
            self.lbl_task.setText("无")

        self.lbl_inventory.setText(ShopSystem.inventory_summary(s))
        self.lbl_satiety_buff.setText(self._format_buff(s.satiety_decay_buff_remaining_seconds, s.satiety_decay_buff_rate))
        self.lbl_mood_buff.setText(self._format_buff(s.mood_decay_buff_remaining_seconds, s.mood_decay_buff_rate))

    def _format_buff(self, remaining_seconds: int, rate: float) -> str:
        if remaining_seconds <= 0 or rate <= 0:
            return "无"
        mins = remaining_seconds // 60
        secs = remaining_seconds % 60
        return f"剩余 {mins}分{secs:02d}秒，下降速度 -{int(rate * 100)}%"
