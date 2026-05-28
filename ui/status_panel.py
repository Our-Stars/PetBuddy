"""状态面板对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QGroupBox, QFormLayout,
)
from PySide6.QtCore import Qt
from core.game_state import GameState, PetStatus
from core.shop_system import ShopSystem

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
        self.setMinimumWidth(280)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._init_ui()
        self._refresh()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        group = QGroupBox("核心状态")
        form = QFormLayout()
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
