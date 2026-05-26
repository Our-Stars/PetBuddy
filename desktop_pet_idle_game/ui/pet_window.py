"""宠物主窗口：无边框透明窗口、拖动、点击、右键菜单、主循环"""

import os
from PySide6.QtWidgets import (
    QMainWindow, QMenu, QApplication, QToolTip,
)
from PySide6.QtCore import Qt, QTimer, QPoint, QPointF, QRectF
from PySide6.QtGui import (
    QPainter, QBrush, QColor, QPen, QFont, QPainterPath,
    QMouseEvent, QPolygonF, QPixmap,
)

from core.game_state import GameState, PetStatus
from core.game_rules import GameRules
from core.task_system import TaskSystem, STUDY_DURATION, SLEEP_DURATION
from core.shop_system import ShopSystem
from storage.save_manager import SaveManager

STATIC_FILES = {
    PetStatus.IDLE: "pet_idle.png",
    PetStatus.HAPPY: "pet_happy.png",
    PetStatus.HUNGRY: "pet_hungry.png",
    PetStatus.STUDYING: "pet_studying.png",
    PetStatus.WORKING: "pet_working.png",
    PetStatus.SLEEPING: "pet_sleeping.png",
}

STATIC_DIR = "Original static image"


def _asset_path(*parts: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", *parts)


class PetWindow(QMainWindow):
    """桌面宠物主窗口"""

    def __init__(self, state: GameState, save_manager: SaveManager):
        super().__init__()
        self.state = state
        self.save_manager = save_manager
        self.dragging = False
        self.drag_offset = QPoint()
        self.press_global_pos = QPoint()
        self._frames: dict[PetStatus, list[QPixmap]] = {}
        self._current_pixmap: QPixmap | None = None

        self._init_window()
        self._load_frames()
        self._init_timer()
        self._load_position()
        self.apply_settings()

    # ========== 窗口初始化 ==========

    def _init_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.Window
            | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.NoFocus)
        w, h = self.state.pet_size_pixels
        self.setFixedSize(w, h)
        self.setWindowTitle("桌面宠物")

    def _load_frames(self):
        for status, fname in STATIC_FILES.items():
            pix = QPixmap(_asset_path(STATIC_DIR, fname))
            if not pix.isNull():
                self._frames[status] = [pix]
        self._update_frame()

    def _update_frame(self):
        frames = self._frames.get(self.state.status)
        if frames:
            self._current_pixmap = frames[0]
        self.update()

    def _init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._game_tick)
        self.timer.start(1000)

    def _load_position(self):
        pos = self._clamp_to_screen(QPoint(self.state.position_x, self.state.position_y))
        self.move(pos)
        self.state.position_x = pos.x()
        self.state.position_y = pos.y()

    def apply_settings(self):
        """应用置顶设置"""
        self.hide()
        flags = Qt.FramelessWindowHint | Qt.Window
        if self.state.always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        w, h = self.state.pet_size_pixels
        self.setFixedSize(w, h)
        self.show()

    # ========== 主循环 ==========

    def _game_tick(self):
        state = self.state
        state.elapsed_seconds += 1
        should_save = False

        # 每 10 秒自然金币
        if state.elapsed_seconds % 10 == 0:
            gained = GameRules.add_natural_coin_income(state)
            should_save = should_save or gained > 0

        # 每 60 秒心情和饱食度下降
        if state.elapsed_seconds % 60 == 0:
            old_mood = state.mood
            old_satiety = state.satiety
            state.mood = max(0, state.mood - 1)
            state.satiety = max(0, state.satiety - 1)
            should_save = should_save or state.mood != old_mood or state.satiety != old_satiety

        # Happy 计时器
        if state.happy_timer > 0:
            state.happy_timer -= 1

        # 任务倒计时
        TaskSystem.tick(state)

        # 检查任务完成
        result = TaskSystem.check_completion(state)
        if result:
            should_save = True
            self._show_tip(result["message"])

        # 更新宠物显示状态（非任务中）
        old_status = state.status
        GameRules.update_status(state)
        if state.status != old_status:
            self._update_frame()

        # 自动保存（每 45 秒）
        if should_save or state.elapsed_seconds % 45 == 0:
            self.save_manager.save(state)

        self.update()

    # ========== 绘制 ==========

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        base, full_h = self.state.pet_size_pixels
        scale = base / 150.0
        offset_y = int((full_h - base) / scale)

        # --- GIF 帧（QMovie 自动处理透明色） ---
        if self._current_pixmap and not self._current_pixmap.isNull():
            scaled = self._current_pixmap.scaled(
                base, base + offset_y + 10,
                Qt.KeepAspectRatio, Qt.SmoothTransformation,
            )
            px = (self.width() - scaled.width()) // 2
            py = (self.height() - scaled.height()) // 2 - offset_y // 2
            painter.drawPixmap(px, py, scaled)

        # --- 状态文字（顶部） ---
        if self.state.show_status_text:
            painter.save()
            painter.scale(scale, scale)
            self._draw_status_text(painter)
            painter.restore()

        # --- 任务进度条（底部） ---
        if self.state.current_task:
            self._draw_task_progress(painter, scale, offset_y)

        painter.end()

    def _draw_status_text(self, p: QPainter):
        """绘制简要状态文字。"""
        labels = {
            PetStatus.IDLE: "空闲",
            PetStatus.HAPPY: "开心",
            PetStatus.HUNGRY: "饥饿",
            PetStatus.STUDYING: "学习",
            PetStatus.WORKING: "工作",
            PetStatus.SLEEPING: "睡觉",
        }
        text = f"{labels.get(self.state.status, '未知')}  金币:{self.state.coins}"
        p.setPen(QPen(QColor("#333333"), 1))
        p.setFont(QFont("Arial", 16))
        p.drawText(QRectF(5, 4, 140, 26), Qt.AlignCenter, text)

    def _draw_task_progress(self, p: QPainter, scale: float, offset_y: int):
        """在宠物下方绘制任务进度条和时间文字"""
        s = self.state
        total = 0
        if s.status == PetStatus.STUDYING:
            total = STUDY_DURATION
        elif s.status == PetStatus.SLEEPING:
            total = SLEEP_DURATION
        elif s.status == PetStatus.WORKING:
            job = TaskSystem.get_job_by_name(s.current_task)
            if job:
                total = job["duration"]
        if total <= 0:
            return

        elapsed = total - s.task_remaining_seconds
        progress = max(0.0, min(1.0, elapsed / total))

        # 进度条放在宠物下方（设计坐标 y=135，上移一半 offset）
        bar_x, bar_w, bar_h = 0, 150, 7
        bar_y = 135 - offset_y // 2
        radius = 3

        p.save()
        p.scale(scale, scale)

        # 背景条
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(200, 200, 200, 160)))
        p.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), radius, radius)

        # 进度条
        if progress < 0.5:
            bar_color = QColor("#4CAF50")
        elif progress < 0.85:
            bar_color = QColor("#FF9800")
        else:
            bar_color = QColor("#F44336")
        p.setBrush(QBrush(bar_color))
        p.drawRoundedRect(QRectF(bar_x, bar_y, bar_w * progress, bar_h), radius, radius)

        # 时间文字
        remaining = s.task_remaining_seconds
        mins = remaining // 60
        secs = remaining % 60
        task_name = s.current_task or ""
        time_text = f"{task_name} {mins}:{secs:02d} / {total // 60}:{total % 60:02d}"

        p.setPen(QPen(QColor("#555555"), 1))
        p.setFont(QFont("Arial", 16))
        p.drawText(QRectF(bar_x, bar_y + bar_h + 2, bar_w, 20), Qt.AlignCenter, time_text)

        p.restore()

    # ---- 表情组件 ----

    # ========== 鼠标事件 ==========

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.press_global_pos = event.globalPosition().toPoint()
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            new_pos = self._clamp_to_screen(event.globalPosition().toPoint() - self.drag_offset)
            self.move(new_pos)
            # 保存位置
            self.state.position_x = new_pos.x()
            self.state.position_y = new_pos.y()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)

            # 判断是否是点击（没有明显拖动）
            drag_distance = (event.globalPosition().toPoint() - self.press_global_pos).manhattanLength()
            if drag_distance < 5:
                self._on_click()

    def _clamp_to_screen(self, pos: QPoint) -> QPoint:
        """限制窗口至少保留在当前屏幕可见区域内。"""
        screen = QApplication.screenAt(pos) or QApplication.primaryScreen()
        if screen is None:
            return pos

        rect = screen.availableGeometry()
        width = self.width()
        height = self.height()
        x = max(rect.left(), min(pos.x(), rect.right() - width + 1))
        y = max(rect.top(), min(pos.y(), rect.bottom() - height + 1))
        return QPoint(x, y)

    def _on_click(self):
        """左键点击宠物互动"""
        can, msg = GameRules.can_click(self.state)
        if not can:
            return

        import time
        self.state.last_click_time = time.time()
        if self.state.click_mood_enabled:
            self.state.mood = min(100, self.state.mood + 3)
        if (
            self.state.click_animation_enabled
            and not self.state.quiet_mode
            and self.state.status not in (PetStatus.STUDYING, PetStatus.WORKING, PetStatus.SLEEPING)
        ):
            self.state.happy_timer = 3  # 开心 3 秒
            self.state.status = PetStatus.HAPPY
        GameRules.update_status(self.state)
        self._update_frame()
        self.save_manager.save(self.state)
        self._show_tip("心情 +3" if self.state.click_mood_enabled else "已互动")
        self.update()

    def _show_tip(self, message: str):
        if self.state.quiet_mode or not self.state.bubble_tips_enabled:
            return
        QToolTip.showText(self.mapToGlobal(QPoint(self.width() // 2, 0)), message, self)

    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { font-size: 14px; padding: 4px; }")

        # 喂食子菜单
        feed_menu = menu.addMenu("喂食")
        feed_menu.setEnabled(GameRules.can_feed(self.state)[0])

        normal_action = feed_menu.addAction(f"普通食物（{self.state.food_count}个）")
        normal_action.setEnabled(self.state.food_count > 0)
        normal_action.triggered.connect(self._feed_normal)

        premium_action = feed_menu.addAction(f"高级食物（{self.state.premium_food_count}个）")
        premium_action.setEnabled(self.state.premium_food_count > 0)
        premium_action.triggered.connect(self._feed_premium)

        # 学习
        study_action = menu.addAction("学习")
        can_study, study_msg = GameRules.can_study(self.state)
        study_action.setEnabled(can_study)
        if not can_study:
            study_action.setToolTip(study_msg)
        study_action.triggered.connect(self._start_study)

        # 工作
        work_action = menu.addAction("工作")
        can_work, work_msg = GameRules.can_work(self.state)
        work_action.setEnabled(can_work)
        if not can_work:
            work_action.setToolTip(work_msg)
        work_action.triggered.connect(self._open_work_dialog)

        # 睡觉
        sleep_action = menu.addAction("睡觉")
        can_sleep, sleep_msg = GameRules.can_sleep(self.state)
        sleep_action.setEnabled(can_sleep)
        if not can_sleep:
            sleep_action.setToolTip(sleep_msg)
        sleep_action.triggered.connect(self._start_sleep)

        # 使用玩具
        toy_action = menu.addAction(f"使用玩具（{self.state.toy_count}个）")
        can_toy, toy_msg = GameRules.can_use_toy(self.state)
        toy_action.setEnabled(can_toy)
        if not can_toy:
            toy_action.setToolTip(toy_msg)
        toy_action.triggered.connect(self._use_toy)

        if self.state.status in (PetStatus.STUDYING, PetStatus.WORKING, PetStatus.SLEEPING):
            cancel_task_action = menu.addAction("停止当前任务")
            cancel_task_action.triggered.connect(self._cancel_current_task)

        menu.addSeparator()

        # 商店
        shop_action = menu.addAction("打开商店")
        shop_action.triggered.connect(self._open_shop)

        # 状态面板
        status_action = menu.addAction("查看状态")
        status_action.triggered.connect(self._open_status)

        # 设置
        settings_action = menu.addAction("设置")
        settings_action.triggered.connect(self._open_settings)

        menu.addSeparator()

        # 退出
        quit_action = menu.addAction("退出程序")
        quit_action.triggered.connect(self._quit_app)

        menu.exec(event.globalPos())

    # ========== 动作处理 ==========

    def _feed_normal(self):
        ok, msg = ShopSystem.use_food(self.state, is_premium=False)
        if ok:
            if self.state.click_animation_enabled and not self.state.quiet_mode:
                self.state.happy_timer = 3
            GameRules.update_status(self.state)
            self._update_frame()
            self.save_manager.save(self.state)
        self._show_tip(msg)
        self.update()

    def _feed_premium(self):
        ok, msg = ShopSystem.use_food(self.state, is_premium=True)
        if ok:
            if self.state.click_animation_enabled and not self.state.quiet_mode:
                self.state.happy_timer = 3
            GameRules.update_status(self.state)
            self._update_frame()
            self.save_manager.save(self.state)
        self._show_tip(msg)
        self.update()

    def _start_study(self):
        can, msg = GameRules.can_study(self.state)
        if not can:
            self._show_tip(msg)
            return
        TaskSystem.start_study(self.state)
        self._update_frame()
        self.save_manager.save(self.state)
        self._show_tip("开始学习")
        self.update()

    def _start_sleep(self):
        can, msg = GameRules.can_sleep(self.state)
        if not can:
            self._show_tip(msg)
            return
        TaskSystem.start_sleep(self.state)
        self._update_frame()
        self.save_manager.save(self.state)
        self._show_tip("开始睡觉")
        self.update()

    def _use_toy(self):
        ok, msg = ShopSystem.use_toy(self.state)
        if ok:
            if self.state.click_animation_enabled and not self.state.quiet_mode:
                self.state.happy_timer = 3
            GameRules.update_status(self.state)
            self._update_frame()
            self.save_manager.save(self.state)
        self._show_tip(msg)
        self.update()

    def _open_work_dialog(self):
        from .work_dialog import WorkDialog
        dlg = WorkDialog(self.state, self)
        if dlg.exec() and dlg.selected_job:
            can, msg = GameRules.can_work(self.state)
            if not can:
                self._show_tip(msg)
                return
            job = TaskSystem.get_job_by_name(dlg.selected_job)
            if job and self.state.knowledge >= job["knowledge"]:
                TaskSystem.start_work(self.state, dlg.selected_job)
                self._update_frame()
                self.save_manager.save(self.state)
                self._show_tip(f"开始工作：{dlg.selected_job}")
                self.update()

    def _cancel_current_task(self):
        ok, msg = TaskSystem.cancel_current_task(self.state)
        if ok:
            self._update_frame()
            self.save_manager.save(self.state)
        self._show_tip(msg)
        self.update()

    def _open_shop(self):
        from .shop_dialog import ShopDialog
        dlg = ShopDialog(self.state, self.save_manager, self)
        if dlg.exec():
            self.save_manager.save(self.state)
            self.update()

    def _open_status(self):
        from .status_panel import StatusPanel
        dlg = StatusPanel(self.state, self.save_manager, self)
        dlg.exec()
        self.update()

    def _open_settings(self):
        from .settings_dialog import SettingsDialog
        dlg = SettingsDialog(self.state, self.save_manager, self)
        if dlg.exec():
            self.apply_settings()
            self.save_manager.save(self.state)
            self.update()

    def _quit_app(self):
        self.save_manager.save(self.state)
        QApplication.quit()

    # ========== 生命周期 ==========

    def closeEvent(self, event):
        self.save_manager.save(self.state)
        super().closeEvent(event)
        QApplication.quit()
