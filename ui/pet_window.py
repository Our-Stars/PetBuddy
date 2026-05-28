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
from core.task_system import TaskSystem
from core.shop_system import ShopSystem
from storage.save_manager import SaveManager
from .dialog_styles import CONTEXT_MENU_STYLE

STATIC_FILES = {
    PetStatus.IDLE: "pet_idle.png",
    PetStatus.HAPPY: "pet_happy.png",
    PetStatus.HUNGRY: "pet_hungry.png",
    PetStatus.STUDYING: "pet_studying.png",
    PetStatus.WORKING: "pet_working.png",
    PetStatus.SLEEPING: "pet_sleeping.png",
}

STATIC_DIR = "Original static image"


class PetWindow(QMainWindow):
    """桌面宠物主窗口"""

    def __init__(self, state: GameState, save_manager: SaveManager, asset_base: str | None = None):
        super().__init__()
        self.state = state
        self.save_manager = save_manager
        self.dragging = False
        self.drag_offset = QPoint()
        self.press_global_pos = QPoint()
        self._frames: dict[PetStatus, list[QPixmap]] = {}
        self._current_pixmap: QPixmap | None = None

        if asset_base is None:
            asset_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        self._asset_base = asset_base

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
            path = os.path.join(self._asset_base, "assets", STATIC_DIR, fname)
            pix = QPixmap(path)
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

        # 每 60 秒自然金币，基础值为 1，受心情倍率影响
        if state.elapsed_seconds % 60 == 0:
            gained = GameRules.add_natural_coin_income(state)
            should_save = should_save or gained > 0

        # 每 60 秒心情和饱食度下降；学习/工作消耗为空闲的 1.2 倍，睡觉只消耗少量饱食度。
        if state.elapsed_seconds % 60 == 0:
            old_mood = state.mood
            old_satiety = state.satiety
            mood_cost = 0.5
            satiety_cost = 0.5
            if state.status in (PetStatus.STUDYING, PetStatus.WORKING):
                mood_cost = 0.6
                satiety_cost = 0.6
            elif state.status == PetStatus.SLEEPING:
                mood_cost = 0
                satiety_cost = 0.2
            if state.mood_decay_buff_remaining_seconds > 0:
                mood_cost *= 1 - state.mood_decay_buff_rate
            if state.satiety_decay_buff_remaining_seconds > 0:
                satiety_cost *= 1 - state.satiety_decay_buff_rate
            state.mood = max(0, state.mood - mood_cost)
            state.satiety = max(0, state.satiety - satiety_cost)
            should_save = should_save or state.mood != old_mood or state.satiety != old_satiety

        if state.satiety_decay_buff_remaining_seconds > 0:
            state.satiety_decay_buff_remaining_seconds -= 1
            if state.satiety_decay_buff_remaining_seconds == 0:
                state.satiety_decay_buff_rate = 0
                should_save = True
        if state.mood_decay_buff_remaining_seconds > 0:
            state.mood_decay_buff_remaining_seconds -= 1
            if state.mood_decay_buff_remaining_seconds == 0:
                state.mood_decay_buff_rate = 0
                should_save = True

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
            self._update_frame()

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

        # --- 宠物图片（下移，给顶部状态文字留空间） ---
        status_area_h = 60 if self.state.show_status_text else 0
        if self._current_pixmap and not self._current_pixmap.isNull():
            scaled = self._current_pixmap.scaled(
                base, base, Qt.KeepAspectRatio, Qt.SmoothTransformation,
            )
            px = (self.width() - scaled.width()) // 2
            py = status_area_h
            painter.drawPixmap(px, py, scaled)

        # --- 状态文字（猫下方，带半透明背景） ---
        if self.state.show_status_text:
            painter.save()
            painter.scale(scale, scale)
            self._draw_status_text(painter, offset_y)
            painter.restore()

        # --- 任务进度条（底部） ---
        if self.state.current_task:
            self._draw_task_progress(painter, scale, base)

        painter.end()

    def _draw_status_text(self, p: QPainter, offset_y: int):
        """绘制状态文字，四行各占一行 + 半透明背景，位于窗口顶部"""
        labels = {
            PetStatus.IDLE: "空闲",
            PetStatus.HAPPY: "开心",
            PetStatus.HUNGRY: "饥饿",
            PetStatus.STUDYING: "学习",
            PetStatus.WORKING: "工作",
            PetStatus.SLEEPING: "睡觉",
        }
        s = self.state
        lines = [
            labels.get(s.status, "未知"),
            f"心情: {s.mood:.1f}",
            f"饱食: {s.satiety:.1f}",
            f"金币: {s.coins:.1f}",
        ]
        font_h = 13
        total_h = len(lines) * font_h + 6
        top_y = 0

        # 半透明背景
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(0, 0, 0, 100)))
        p.drawRoundedRect(QRectF(15, top_y, 120, total_h), 6, 6)
        # 白色文字
        p.setPen(QPen(Qt.white, 1))
        p.setFont(QFont("Arial", 11))
        y = top_y + 2
        for line in lines:
            p.drawText(QRectF(15, y, 120, font_h), Qt.AlignCenter, line)
            y += font_h

    def _draw_task_progress(self, p: QPainter, scale: float, base: int):
        """在宠物下方绘制任务进度条和时间文字"""
        s = self.state
        total = 0
        if s.status == PetStatus.STUDYING:
            study_option = TaskSystem.get_study_option_by_name(s.current_task)
            if study_option:
                total = study_option["duration"]
        elif s.status == PetStatus.SLEEPING:
            sleep_option = TaskSystem.get_sleep_option_by_name(s.current_task)
            if sleep_option:
                total = sleep_option["duration"]
        elif s.status == PetStatus.WORKING:
            option = TaskSystem.get_job_option_by_name(s.current_task)
            if option:
                total = option["duration"]
        if total <= 0:
            return

        elapsed = total - s.task_remaining_seconds
        progress = max(0.0, min(1.0, elapsed / total))

        # 进度条固定用窗口像素绘制，避免随宠物缩放后太细或被裁切。
        margin = 12
        bar_x = margin
        bar_w = self.width() - margin * 2
        bar_h = 11
        text_h = 28
        gap = 4
        bottom_margin = 8
        bar_y = self.height() - bottom_margin - text_h - gap - bar_h
        radius = 6

        # 背景条
        p.setPen(QPen(QColor(80, 80, 80, 170), 1))
        p.setBrush(QBrush(QColor(235, 235, 235, 210)))
        p.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), radius, radius)

        # 进度条
        if progress < 0.5:
            bar_color = QColor("#4CAF50")
        elif progress < 0.85:
            bar_color = QColor("#FF9800")
        else:
            bar_color = QColor("#F44336")
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(bar_color))
        p.drawRoundedRect(QRectF(bar_x, bar_y, bar_w * progress, bar_h), radius, radius)

        # 时间文字
        remaining = s.task_remaining_seconds
        mins = remaining // 60
        secs = remaining % 60
        time_text = f"{mins}:{secs:02d} / {total // 60}:{total % 60:02d}"

        p.setPen(QPen(QColor("#555555"), 1))
        p.setFont(QFont("Arial", max(18, int(11 * scale))))
        p.drawText(QRectF(bar_x, bar_y + bar_h + gap, bar_w, text_h), Qt.AlignCenter, time_text)

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
        self.state.mood = min(100, self.state.mood + 3)
        if (
            self.state.status not in (PetStatus.STUDYING, PetStatus.WORKING, PetStatus.SLEEPING)
        ):
            self.state.happy_timer = 3  # 开心 3 秒
            self.state.status = PetStatus.HAPPY
        GameRules.update_status(self.state)
        self._update_frame()
        self.save_manager.save(self.state)
        self._show_tip("心情 +3")
        self.update()

    def _show_tip(self, message: str):
        QToolTip.showText(self.mapToGlobal(QPoint(self.width() // 2, 0)), message, self)

    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(CONTEXT_MENU_STYLE)

        # 喂食
        feed_action = menu.addAction("喂食")
        feed_action.triggered.connect(self._open_feed_dialog)

        # 玩耍
        play_action = menu.addAction("玩耍")
        play_action.triggered.connect(self._open_play_dialog)

        # 学习
        study_action = menu.addAction("学习")
        study_action.triggered.connect(self._open_study_dialog)

        # 工作
        work_action = menu.addAction("工作")
        work_action.triggered.connect(self._open_work_dialog)

        # 睡觉
        sleep_action = menu.addAction("睡觉")
        sleep_action.triggered.connect(self._open_sleep_dialog)

        if self.state.status in (PetStatus.STUDYING, PetStatus.WORKING, PetStatus.SLEEPING):
            cancel_task_action = menu.addAction("停止当前任务")
            cancel_task_action.triggered.connect(self._cancel_current_task)

        menu.addSeparator()

        # 商店
        shop_action = menu.addAction("商店")
        shop_action.triggered.connect(self._open_shop)

        # 状态面板
        status_action = menu.addAction("状态")
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

    def _feed(self, item_id: str):
        ok, msg = ShopSystem.use_food(self.state, item_id)
        if ok:
            self.state.happy_timer = 3
            GameRules.update_status(self.state)
            self._update_frame()
            self.save_manager.save(self.state)
        self._show_tip(msg)
        self.update()

    def _start_study(self, option_name: str):
        can, msg = GameRules.can_study(self.state)
        if not can:
            self._show_tip(msg)
            return
        option = TaskSystem.get_study_option_by_name(option_name)
        if option is None or not TaskSystem.start_study(self.state, option_name):
            self._show_tip("学习选项不存在")
            return
        self._update_frame()
        self.save_manager.save(self.state)
        self._show_tip(f"开始学习：{option_name}")
        self.update()

    def _start_sleep(self, option_name: str):
        can, msg = GameRules.can_sleep(self.state)
        if not can:
            self._show_tip(msg)
            return
        option = TaskSystem.get_sleep_option_by_name(option_name)
        if option is None or not TaskSystem.start_sleep(self.state, option_name):
            self._show_tip("睡觉选项不存在")
            return
        self._update_frame()
        self.save_manager.save(self.state)
        self._show_tip(f"开始睡觉：{option_name}")
        self.update()

    def _use_toy(self, item_id: str):
        ok, msg = ShopSystem.use_toy(self.state, item_id)
        if ok:
            self.state.happy_timer = 3
            GameRules.update_status(self.state)
            self._update_frame()
            self.save_manager.save(self.state)
        self._show_tip(msg)
        self.update()

    def _open_feed_dialog(self):
        from .interaction_dialogs import FeedDialog
        dlg = FeedDialog(self.state, self)
        if dlg.exec() and dlg.selected_option is not None:
            self._feed(dlg.selected_option)

    def _open_study_dialog(self):
        from .interaction_dialogs import StudyDialog
        dlg = StudyDialog(self.state, self)
        if dlg.exec() and dlg.selected_option:
            self._start_study(dlg.selected_option)

    def _open_sleep_dialog(self):
        from .interaction_dialogs import SleepDialog
        dlg = SleepDialog(self.state, self)
        if dlg.exec() and dlg.selected_option:
            self._start_sleep(dlg.selected_option)

    def _open_play_dialog(self):
        from .interaction_dialogs import PlayDialog
        dlg = PlayDialog(self.state, self)
        if dlg.exec() and dlg.selected_option:
            self._use_toy(dlg.selected_option)

    def _open_work_dialog(self):
        from .work_dialog import WorkDialog
        dlg = WorkDialog(self.state, self)
        if dlg.exec() and dlg.selected_job:
            can, msg = GameRules.can_work(self.state)
            if not can:
                self._show_tip(msg)
                return
            if TaskSystem.start_work(self.state, dlg.selected_job):
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
