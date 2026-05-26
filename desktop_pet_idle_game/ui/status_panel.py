"""状态面板对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QGroupBox, QFormLayout, QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
from core.game_state import GameState, PetStatus
from core.game_rules import GameRules
from core.shop_system import ShopSystem
from core.task_system import TaskSystem

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
        self.lbl_food = QLabel()
        self.lbl_premium = QLabel()
        self.lbl_toy = QLabel()
        self.lbl_bed = QLabel()

        form.addRow("金币：", self.lbl_coins)
        form.addRow("心情：", self.lbl_mood)
        form.addRow("饱食度：", self.lbl_satiety)
        form.addRow("学识：", self.lbl_knowledge)
        form.addRow("状态：", self.lbl_status)
        form.addRow("当前任务：", self.lbl_task)
        form.addRow("普通食物：", self.lbl_food)
        form.addRow("高级食物：", self.lbl_premium)
        form.addRow("玩具：", self.lbl_toy)
        form.addRow("小床等级：", self.lbl_bed)
        group.setLayout(form)
        layout.addWidget(group)

        feed_row = QHBoxLayout()
        self.btn_feed_normal = QPushButton("喂普通食物")
        self.btn_feed_normal.clicked.connect(lambda: self._feed(False))
        feed_row.addWidget(self.btn_feed_normal)

        self.btn_feed_premium = QPushButton("喂高级食物")
        self.btn_feed_premium.clicked.connect(lambda: self._feed(True))
        feed_row.addWidget(self.btn_feed_premium)
        layout.addLayout(feed_row)

        self.btn_cancel_task = QPushButton("停止当前任务")
        self.btn_cancel_task.clicked.connect(self._cancel_current_task)
        layout.addWidget(self.btn_cancel_task)

        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _refresh(self):
        s = self.state
        self.lbl_coins.setText(str(s.coins))
        self.lbl_mood.setText(f"{s.mood} / 100")
        self.lbl_satiety.setText(f"{s.satiety} / 100")
        self.lbl_knowledge.setText(str(s.knowledge))
        self.lbl_status.setText(STATUS_LABELS.get(s.status, "未知"))

        if s.current_task:
            mins = s.task_remaining_seconds // 60
            secs = s.task_remaining_seconds % 60
            self.lbl_task.setText(f"{s.current_task}（剩余 {mins}分{secs:02d}秒）")
        else:
            self.lbl_task.setText("无")

        self.lbl_food.setText(str(s.food_count))
        self.lbl_premium.setText(str(s.premium_food_count))
        self.lbl_toy.setText(str(s.toy_count))
        self.lbl_bed.setText(str(s.bed_level))
        self.btn_feed_normal.setEnabled(s.food_count > 0)
        self.btn_feed_premium.setEnabled(s.premium_food_count > 0)
        self.btn_cancel_task.setEnabled(s.status in (PetStatus.STUDYING, PetStatus.WORKING, PetStatus.SLEEPING))

    def _feed(self, is_premium: bool):
        ok, msg = ShopSystem.use_food(self.state, is_premium=is_premium)
        if ok:
            if self.state.click_animation_enabled and not self.state.quiet_mode:
                self.state.happy_timer = 3
            GameRules.update_status(self.state)
            if self.save_manager is not None:
                self.save_manager.save(self.state)
            parent = self.parent()
            if parent is not None:
                parent.update()
            self._refresh()
        self.setWindowTitle(f"宠物状态 - {msg}")

    def _cancel_current_task(self):
        ok, msg = TaskSystem.cancel_current_task(self.state)
        if ok:
            if self.save_manager is not None:
                self.save_manager.save(self.state)
            parent = self.parent()
            if parent is not None:
                parent.update()
            self._refresh()
        self.setWindowTitle(f"宠物状态 - {msg}")
