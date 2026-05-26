"""宠物主窗口：无边框透明窗口、拖动、点击、右键菜单、主循环"""

from PySide6.QtWidgets import (
    QMainWindow, QMenu, QApplication, QToolTip,
)
from PySide6.QtCore import Qt, QTimer, QPoint, QPointF, QRectF
from PySide6.QtGui import (
    QPainter, QBrush, QColor, QPen, QFont, QPainterPath,
    QMouseEvent, QPolygonF,
)

from core.game_state import GameState, PetStatus
from core.game_rules import GameRules
from core.task_system import TaskSystem
from core.shop_system import ShopSystem
from storage.save_manager import SaveManager


class PetWindow(QMainWindow):
    """桌面宠物主窗口"""

    def __init__(self, state: GameState, save_manager: SaveManager):
        super().__init__()
        self.state = state
        self.save_manager = save_manager
        self.dragging = False
        self.drag_offset = QPoint()
        self.press_global_pos = QPoint()

        self._init_window()
        self._init_timer()
        self._load_position()
        self.apply_settings()

    # ========== 窗口初始化 ==========

    def _init_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.Tool
            | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.state.pet_size_pixels, self.state.pet_size_pixels)
        self.setWindowTitle("桌面宠物")

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
        """应用置顶和安静模式设置"""
        self.hide()
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.state.always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setFixedSize(self.state.pet_size_pixels, self.state.pet_size_pixels)
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
        GameRules.update_status(state)

        # 自动保存（每 45 秒）
        if should_save or state.elapsed_seconds % 45 == 0:
            self.save_manager.save(state)

        self.update()

    # ========== 绘制 ==========

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        size = self.state.pet_size_pixels
        scale = size / 150.0  # 基于 150px 设计尺寸缩放

        painter.scale(scale, scale)

        status = self.state.status
        mood = self.state.mood
        satiety = self.state.satiety

        # 身体
        self._draw_body(painter)
        # 耳朵
        self._draw_ears(painter)
        # 脸
        self._draw_face(painter, status)
        # 表情
        self._draw_expression(painter, status, mood, satiety)
        if self.state.show_status_text:
            self._draw_status_text(painter)

        painter.end()

    def _draw_body(self, p: QPainter):
        """绘制身体（椭圆）"""
        body_color = QColor("#FF9F43")  # 橘猫色
        p.setBrush(QBrush(body_color))
        p.setPen(QPen(QColor("#E08030"), 2))
        p.drawEllipse(QPointF(75, 100), 42, 30)

    def _draw_ears(self, p: QPainter):
        """绘制耳朵"""
        ear_color = QColor("#FF9F43")
        inner_ear = QColor("#FFB8B8")
        p.setBrush(QBrush(ear_color))
        p.setPen(QPen(QColor("#E08030"), 2))

        # 左耳
        left_ear = QPolygonF([QPointF(42, 38), QPointF(58, 15), QPointF(70, 35)])
        p.drawPolygon(left_ear)

        # 右耳
        right_ear = QPolygonF([QPointF(108, 38), QPointF(92, 15), QPointF(80, 35)])
        p.drawPolygon(right_ear)

        # 耳朵内部
        p.setBrush(QBrush(inner_ear))
        p.setPen(Qt.NoPen)
        p.drawPolygon(QPolygonF([QPointF(47, 36), QPointF(57, 20), QPointF(64, 34)]))
        p.drawPolygon(QPolygonF([QPointF(103, 36), QPointF(93, 20), QPointF(86, 34)]))

    def _draw_face(self, p: QPainter, status: PetStatus):
        """绘制脸部底色"""
        face_color = QColor("#FFB366")
        p.setBrush(QBrush(face_color))
        p.setPen(QPen(QColor("#E08030"), 2))
        p.drawEllipse(QPointF(75, 60), 32, 28)

    def _draw_expression(self, p: QPainter, status: PetStatus, mood: int, satiety: int):
        """根据不同状态绘制表情"""
        p.setPen(QPen(Qt.black, 2))

        if status == PetStatus.HAPPY:
            # 开心：^_^ 眼睛
            self._draw_happy_eyes(p)
            self._draw_smile(p, big=True)
            # 腮红
            p.setBrush(QBrush(QColor(255, 150, 150, 80)))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(58, 62), 6, 4)
            p.drawEllipse(QPointF(92, 62), 6, 4)

        elif status == PetStatus.HUNGRY:
            # 饥饿：下垂眼 + 难过嘴
            self._draw_sad_eyes(p)
            self._draw_sad_mouth(p)
            # 泪水
            p.setPen(QPen(QColor("#66CCFF"), 2))
            p.setBrush(QBrush(QColor("#99DDFF")))
            p.drawEllipse(QPointF(52, 58), 3, 4)

        elif status == PetStatus.STUDYING:
            # 学习：眼镜 + 专注
            self._draw_glasses(p)
            self._draw_normal_eyes(p)
            self._draw_small_mouth(p)

        elif status == PetStatus.WORKING:
            # 工作：坚毅眼神
            self._draw_determined_eyes(p)
            self._draw_small_mouth(p)
            # 汗滴
            p.setPen(QPen(QColor("#66CCFF"), 1.5))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(98, 45), 4, 6)

        else:  # IDLE
            self._draw_normal_eyes(p)
            self._draw_small_mouth(p)

        # 鼻子
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#FF8888")))
        p.drawEllipse(QPointF(75, 65), 4, 3)

        # 胡须
        p.setPen(QPen(QColor("#CCCCCC"), 1))
        # 左侧胡须
        p.drawLine(QPointF(48, 63), QPointF(28, 58))
        p.drawLine(QPointF(48, 66), QPointF(26, 66))
        p.drawLine(QPointF(48, 69), QPointF(28, 74))
        # 右侧胡须
        p.drawLine(QPointF(102, 63), QPointF(122, 58))
        p.drawLine(QPointF(102, 66), QPointF(124, 66))
        p.drawLine(QPointF(102, 69), QPointF(122, 74))

    def _draw_status_text(self, p: QPainter):
        """绘制简要状态文字。"""
        labels = {
            PetStatus.IDLE: "待机",
            PetStatus.HAPPY: "开心",
            PetStatus.HUNGRY: "饥饿",
            PetStatus.STUDYING: "学习",
            PetStatus.WORKING: "工作",
        }
        text = f"{labels.get(self.state.status, '未知')}  金币:{self.state.coins}"
        p.setPen(QPen(QColor("#333333"), 1))
        p.setFont(QFont("Arial", 8))
        p.drawText(QRectF(5, 2, 140, 18), Qt.AlignCenter, text)

    # ---- 表情组件 ----

    def _draw_normal_eyes(self, p: QPainter):
        p.setBrush(QBrush(Qt.white))
        p.setPen(QPen(Qt.black, 1.5))
        p.drawEllipse(QPointF(64, 56), 5, 6)
        p.drawEllipse(QPointF(86, 56), 5, 6)
        # 瞳孔
        p.setBrush(QBrush(Qt.black))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(65, 55), 2.5, 3)

    def _draw_happy_eyes(self, p: QPainter):
        p.setPen(QPen(Qt.black, 2))
        p.setBrush(Qt.NoBrush)
        # ^ ^ 形状用弧线
        path = QPainterPath()
        path.moveTo(56, 55)
        path.cubicTo(60, 48, 64, 48, 68, 55)
        p.drawPath(path)
        path2 = QPainterPath()
        path2.moveTo(82, 55)
        path2.cubicTo(86, 48, 90, 48, 94, 55)
        p.drawPath(path2)

    def _draw_sad_eyes(self, p: QPainter):
        p.setBrush(QBrush(Qt.white))
        p.setPen(QPen(Qt.black, 1.5))
        p.drawEllipse(QPointF(64, 58), 5, 5)
        p.drawEllipse(QPointF(86, 58), 5, 5)
        # 半闭眼
        p.setBrush(QBrush(QColor("#FFB366")))
        p.setPen(Qt.NoPen)
        p.drawRect(QRectF(58, 56, 12, 3))
        p.drawRect(QRectF(80, 56, 12, 3))
        # 瞳孔
        p.setBrush(QBrush(Qt.black))
        p.drawEllipse(QPointF(65, 59), 2, 2)

    def _draw_determined_eyes(self, p: QPainter):
        p.setBrush(QBrush(Qt.white))
        p.setPen(QPen(Qt.black, 2))
        p.drawEllipse(QPointF(64, 56), 5, 5)
        p.drawEllipse(QPointF(86, 56), 5, 5)
        # 小瞳孔（坚毅）
        p.setBrush(QBrush(Qt.black))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(64, 56), 2, 2)
        p.drawEllipse(QPointF(86, 56), 2, 2)
        # 眉毛
        p.setPen(QPen(Qt.black, 2))
        p.drawLine(QPointF(58, 49), QPointF(70, 50))
        p.drawLine(QPointF(92, 50), QPointF(80, 49))

    def _draw_glasses(self, p: QPainter):
        p.setPen(QPen(QColor("#333333"), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(64, 56), 8, 8)
        p.drawEllipse(QPointF(86, 56), 8, 8)
        p.drawLine(QPointF(72, 56), QPointF(78, 56))

    def _draw_smile(self, p: QPainter, big: bool = False):
        p.setPen(QPen(Qt.black, 2))
        p.setBrush(Qt.NoBrush)
        if big:
            path = QPainterPath()
            path.moveTo(68, 70)
            path.cubicTo(72, 78, 78, 78, 82, 70)
            p.drawPath(path)
        else:
            path = QPainterPath()
            path.moveTo(70, 72)
            path.cubicTo(73, 76, 77, 76, 80, 72)
            p.drawPath(path)

    def _draw_small_mouth(self, p: QPainter):
        p.setPen(QPen(Qt.black, 1.5))
        p.setBrush(Qt.NoBrush)
        path = QPainterPath()
        path.moveTo(72, 71)
        path.cubicTo(74, 73, 76, 73, 78, 71)
        p.drawPath(path)

    def _draw_sad_mouth(self, p: QPainter):
        p.setPen(QPen(Qt.black, 2))
        p.setBrush(Qt.NoBrush)
        path = QPainterPath()
        path.moveTo(70, 75)
        path.cubicTo(73, 72, 77, 72, 80, 75)
        p.drawPath(path)

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
            and self.state.status not in (PetStatus.STUDYING, PetStatus.WORKING)
        ):
            self.state.happy_timer = 3  # 开心 3 秒
            self.state.status = PetStatus.HAPPY
        GameRules.update_status(self.state)
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

        if self.state.status in (PetStatus.STUDYING, PetStatus.WORKING):
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
            self.save_manager.save(self.state)
        self._show_tip(msg)
        self.update()

    def _feed_premium(self):
        ok, msg = ShopSystem.use_food(self.state, is_premium=True)
        if ok:
            if self.state.click_animation_enabled and not self.state.quiet_mode:
                self.state.happy_timer = 3
            GameRules.update_status(self.state)
            self.save_manager.save(self.state)
        self._show_tip(msg)
        self.update()

    def _start_study(self):
        can, msg = GameRules.can_study(self.state)
        if not can:
            self._show_tip(msg)
            return
        TaskSystem.start_study(self.state)
        self.save_manager.save(self.state)
        self._show_tip("开始学习")
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
                self.save_manager.save(self.state)
                self._show_tip(f"开始工作：{dlg.selected_job}")
                self.update()

    def _cancel_current_task(self):
        ok, msg = TaskSystem.cancel_current_task(self.state)
        if ok:
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
