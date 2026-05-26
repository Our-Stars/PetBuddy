import os
import sys
import tempfile
import unittest


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "desktop_pet_idle_game")
)
sys.path.insert(0, PROJECT_DIR)

from PySide6.QtCore import QPoint
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from core.game_state import GameState, PetStatus
from storage.save_manager import SaveManager
from ui.pet_window import PetWindow
from ui.settings_dialog import SettingsDialog
from ui.shop_dialog import ShopDialog
from ui.status_panel import StatusPanel
from ui.work_dialog import WorkDialog


class CountingSaveManager:
    def __init__(self):
        self.save_count = 0

    def save(self, state):
        self.save_count += 1
        return True


class PetWindowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _make_window(self, state: GameState, save_manager=None):
        self.tmp_dir = tempfile.TemporaryDirectory()
        window = PetWindow(state, save_manager or SaveManager(self.tmp_dir.name))
        window.state.bubble_tips_enabled = False
        return window

    def tearDown(self):
        window = getattr(self, "window", None)
        if window is not None:
            window.timer.stop()
            window.hide()
        tmp_dir = getattr(self, "tmp_dir", None)
        if tmp_dir is not None:
            tmp_dir.cleanup()

    def test_game_tick_applies_natural_coin_mood_multiplier(self):
        self.window = self._make_window(GameState(mood=80))

        for _ in range(20):
            self.window._game_tick()

        self.assertEqual(self.window.state.coins, 3)

    def test_game_tick_saves_when_coins_mood_or_satiety_change(self):
        manager = CountingSaveManager()
        state = GameState(mood=80, satiety=80)
        self.window = self._make_window(state, manager)

        for _ in range(10):
            self.window._game_tick()
        self.assertEqual(state.coins, 1)
        self.assertEqual(manager.save_count, 1)

        for _ in range(50):
            self.window._game_tick()
        self.assertEqual(state.mood, 79)
        self.assertEqual(state.satiety, 79)
        self.assertGreaterEqual(manager.save_count, 2)

    def test_click_mood_setting_can_disable_mood_gain(self):
        state = GameState(mood=50, click_mood_enabled=False)
        self.window = self._make_window(state)

        self.window._on_click()

        self.assertEqual(state.mood, 50)

    def test_click_does_not_interrupt_working_status(self):
        state = GameState(status=PetStatus.WORKING, current_task="捡瓶子", task_remaining_seconds=10)
        self.window = self._make_window(state)

        self.window._on_click()

        self.assertEqual(state.status, PetStatus.WORKING)
        self.assertEqual(state.current_task, "捡瓶子")

    def test_expression_render_paths_do_not_raise(self):
        self.window = self._make_window(GameState())
        image = QImage(150, 150, QImage.Format_ARGB32)
        painter = QPainter(image)

        try:
            self.window._draw_expression(painter, PetStatus.HAPPY, 80, 80)
            self.window._draw_expression(painter, PetStatus.WORKING, 80, 80)
        finally:
            painter.end()

    def test_saved_position_is_clamped_to_screen_on_load(self):
        state = GameState(position_x=100000, position_y=100000)
        self.window = self._make_window(state)
        screen_rect = QApplication.primaryScreen().availableGeometry()

        self.assertLessEqual(state.position_x, screen_rect.right() - self.window.width() + 1)
        self.assertLessEqual(state.position_y, screen_rect.bottom() - self.window.height() + 1)

    def test_clamp_to_screen_keeps_position_visible(self):
        self.window = self._make_window(GameState())
        clamped = self.window._clamp_to_screen(QPoint(-100000, -100000))
        screen_rect = QApplication.primaryScreen().availableGeometry()

        self.assertGreaterEqual(clamped.x(), screen_rect.left())
        self.assertGreaterEqual(clamped.y(), screen_rect.top())

    def test_shop_purchase_saves_immediately(self):
        manager = CountingSaveManager()
        state = GameState(coins=20)
        dialog = ShopDialog(state, manager)

        dialog._buy({"name": "普通食物"})

        self.assertEqual(state.coins, 0)
        self.assertEqual(state.food_count, 1)
        self.assertEqual(manager.save_count, 1)
        dialog.close()

    def test_shop_dialog_contains_readable_item_text_and_buttons(self):
        dialog = ShopDialog(GameState(coins=100))

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        buttons = [button.text() for button in dialog.findChildren(QPushButton)]

        self.assertTrue(any("普通食物" in text for text in labels))
        self.assertTrue(any("价格：20 金币" in text for text in labels))
        self.assertTrue(any("购买（20G）" in text for text in buttons))
        dialog.close()

    def test_work_dialog_contains_readable_job_text_and_buttons(self):
        dialog = WorkDialog(GameState(knowledge=1))

        labels = [label.text() for label in dialog.findChildren(QLabel)]
        buttons = [button.text() for button in dialog.findChildren(QPushButton)]

        self.assertTrue(any("捡瓶子" in text for text in labels))
        self.assertTrue(any("收益：20G" in text for text in labels))
        self.assertTrue(any("开始工作" in text for text in buttons))
        dialog.close()

    def test_settings_change_saves_immediately(self):
        manager = CountingSaveManager()
        state = GameState(always_on_top=True)
        dialog = SettingsDialog(state, manager)

        dialog.chk_top.setChecked(False)

        self.assertFalse(state.always_on_top)
        self.assertEqual(manager.save_count, 1)
        dialog.close()

    def test_reset_save_writes_default_state_after_reset(self):
        manager = CountingSaveManager()
        state = GameState(coins=99, mood=10, satiety=10)
        dialog = SettingsDialog(state, manager)

        dialog.save_manager.reset = lambda: True
        dialog.state.__dict__.update(GameState().__dict__)
        dialog._save_and_apply()

        self.assertEqual(state.coins, 0)
        self.assertEqual(state.mood, 80)
        self.assertEqual(state.satiety, 80)
        self.assertEqual(manager.save_count, 1)
        dialog.close()

    def test_status_panel_cancel_task_saves_and_refreshes(self):
        manager = CountingSaveManager()
        state = GameState(status=PetStatus.STUDYING, current_task="学习", task_remaining_seconds=30)
        dialog = StatusPanel(state, manager)

        self.assertTrue(dialog.btn_cancel_task.isEnabled())
        dialog._cancel_current_task()

        self.assertIsNone(state.current_task)
        self.assertEqual(state.task_remaining_seconds, 0)
        self.assertEqual(state.status, PetStatus.IDLE)
        self.assertFalse(dialog.btn_cancel_task.isEnabled())
        self.assertEqual(manager.save_count, 1)
        dialog.close()


if __name__ == "__main__":
    unittest.main()
