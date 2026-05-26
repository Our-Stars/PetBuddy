import os
import sys
import tempfile
import unittest


PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "desktop_pet_idle_game")
)
sys.path.insert(0, PROJECT_DIR)

from core.game_rules import GameRules
from core.game_state import GameState, PetStatus
from core.shop_system import ShopSystem
from core.task_system import TaskSystem
from storage.game_state_io import dict_to_game_state
from storage.save_manager import SaveManager


class GameRulesTest(unittest.TestCase):
    def test_hungry_state_has_priority_over_happy(self):
        state = GameState(satiety=10, status=PetStatus.HAPPY)
        state.happy_timer = 3

        GameRules.update_status(state)

        self.assertEqual(state.status, PetStatus.HUNGRY)

    def test_task_state_has_priority_over_hungry_and_happy(self):
        state = GameState(satiety=10, status=PetStatus.WORKING)
        state.happy_timer = 3

        GameRules.update_status(state)

        self.assertEqual(state.status, PetStatus.WORKING)

    def test_click_mood_multiplier_ranges(self):
        self.assertEqual(GameRules.get_mood_multiplier(80), 1.5)
        self.assertEqual(GameRules.get_mood_multiplier(50), 1.0)
        self.assertEqual(GameRules.get_mood_multiplier(20), 0.7)
        self.assertEqual(GameRules.get_mood_multiplier(0), 0.3)

    def test_natural_coin_income_accumulates_fractional_mood_multiplier(self):
        high = GameState(mood=80)
        low = GameState(mood=0)

        self.assertEqual(GameRules.add_natural_coin_income(high), 1)
        self.assertEqual(GameRules.add_natural_coin_income(high), 2)
        self.assertEqual(high.coins, 3)

        self.assertEqual(GameRules.add_natural_coin_income(low), 0)
        self.assertEqual(GameRules.add_natural_coin_income(low), 0)
        self.assertEqual(GameRules.add_natural_coin_income(low), 0)
        self.assertEqual(GameRules.add_natural_coin_income(low), 1)
        self.assertEqual(low.coins, 1)


class TaskSystemTest(unittest.TestCase):
    def test_locked_work_cannot_start(self):
        state = GameState(knowledge=0)

        started = TaskSystem.start_work(state, "神秘顾问")

        self.assertFalse(started)
        self.assertIsNone(state.current_task)
        self.assertEqual(state.status, PetStatus.IDLE)

    def test_study_cannot_start_when_satiety_is_too_low(self):
        state = GameState(satiety=20)

        started = TaskSystem.start_study(state)

        self.assertFalse(started)
        self.assertIsNone(state.current_task)

    def test_low_satiety_slows_study_progress(self):
        state = GameState(satiety=50, status=PetStatus.STUDYING, current_task="学习")
        state.task_remaining_seconds = 10

        state.elapsed_seconds = 1
        TaskSystem.tick(state)
        self.assertEqual(state.task_remaining_seconds, 10)

        state.elapsed_seconds = 2
        TaskSystem.tick(state)
        self.assertEqual(state.task_remaining_seconds, 9)

    def test_work_reward_uses_mood_and_satiety_multipliers(self):
        state = GameState(mood=85, satiety=40, knowledge=0)
        self.assertTrue(TaskSystem.start_work(state, "捡瓶子"))
        state.task_remaining_seconds = 0

        result = TaskSystem.check_completion(state)

        self.assertEqual(result["type"], "work")
        self.assertEqual(state.coins, 15)
        self.assertEqual(state.status, PetStatus.IDLE)

    def test_cancel_study_does_not_grant_knowledge(self):
        state = GameState(knowledge=2)
        self.assertTrue(TaskSystem.start_study(state))

        ok, msg = TaskSystem.cancel_current_task(state)

        self.assertTrue(ok)
        self.assertIn("已停止任务", msg)
        self.assertEqual(state.knowledge, 2)
        self.assertIsNone(state.current_task)
        self.assertEqual(state.task_remaining_seconds, 0)
        self.assertEqual(state.status, PetStatus.IDLE)

    def test_cancel_work_does_not_grant_coins(self):
        state = GameState(coins=5, knowledge=0)
        self.assertTrue(TaskSystem.start_work(state, "捡瓶子"))

        ok, msg = TaskSystem.cancel_current_task(state)

        self.assertTrue(ok)
        self.assertIn("已停止任务", msg)
        self.assertEqual(state.coins, 5)
        self.assertIsNone(state.current_task)
        self.assertEqual(state.task_remaining_seconds, 0)
        self.assertEqual(state.status, PetStatus.IDLE)

    def test_cancel_without_task_fails_without_state_change(self):
        state = GameState(coins=5, knowledge=2, status=PetStatus.IDLE)

        ok, msg = TaskSystem.cancel_current_task(state)

        self.assertFalse(ok)
        self.assertEqual(msg, "当前没有正在进行的任务")
        self.assertEqual(state.coins, 5)
        self.assertEqual(state.knowledge, 2)
        self.assertEqual(state.status, PetStatus.IDLE)


class ShopSystemTest(unittest.TestCase):
    def test_food_is_bought_then_used_from_inventory(self):
        state = GameState(coins=20, satiety=40)

        ok, _ = ShopSystem.buy(state, "普通食物")
        self.assertTrue(ok)
        self.assertEqual(state.coins, 0)
        self.assertEqual(state.food_count, 1)

        ok, _ = ShopSystem.use_food(state)
        self.assertTrue(ok)
        self.assertEqual(state.food_count, 0)
        self.assertEqual(state.satiety, 60)


class SaveManagerTest(unittest.TestCase):
    def test_loading_state_clamps_mood_and_satiety_range(self):
        loaded = dict_to_game_state({"mood": 150, "satiety": -10})

        self.assertEqual(loaded.mood, 100)
        self.assertEqual(loaded.satiety, 0)

    def test_save_load_round_trip_preserves_task_remaining_time(self):
        state = GameState(
            coins=12,
            mood=70,
            satiety=65,
            knowledge=3,
            status=PetStatus.WORKING,
            current_task="捡瓶子",
            task_remaining_seconds=42,
            show_status_text=True,
            bubble_tips_enabled=False,
            click_mood_enabled=False,
            click_animation_enabled=False,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = SaveManager(tmp_dir)
            self.assertTrue(manager.save(state))

            loaded = manager.load()

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.coins, 12)
        self.assertEqual(loaded.status, PetStatus.WORKING)
        self.assertEqual(loaded.current_task, "捡瓶子")
        self.assertEqual(loaded.task_remaining_seconds, 42)
        self.assertTrue(loaded.show_status_text)
        self.assertFalse(loaded.bubble_tips_enabled)
        self.assertFalse(loaded.click_mood_enabled)
        self.assertFalse(loaded.click_animation_enabled)


if __name__ == "__main__":
    unittest.main()
