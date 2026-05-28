"""游戏规则：收益计算、倍率、条件判断"""

import time
from .game_state import GameState, PetStatus

CLICK_COOLDOWN_SECONDS = 10


class GameRules:
    """纯静态方法，不持有状态"""

    @staticmethod
    def get_mood_multiplier(mood: int) -> float:
        if mood >= 80:
            return 1.5
        elif mood >= 50:
            return 1.0
        elif mood >= 20:
            return 0.7
        else:
            return 0.3

    @staticmethod
    def get_satiety_multiplier(satiety: int) -> float:
        """当前任务收益不按结束时饱食度惩罚。"""
        return 1.0

    @staticmethod
    def add_natural_coin_income(state: GameState, base_income: float = 1.0) -> int:
        """按心情倍率累积自然金币收益，返回本次实际入账金币。"""
        state.natural_coin_progress += base_income * GameRules.get_mood_multiplier(state.mood)
        gained = int(state.natural_coin_progress)
        if gained > 0:
            state.coins += gained
            state.natural_coin_progress -= gained
        return gained

    @staticmethod
    def can_click(state: GameState) -> tuple[bool, str]:
        """检查点击（任务中禁止互动）"""
        if state.status == PetStatus.SLEEPING:
            return False, "正在睡觉，请勿打扰"
        if state.status == PetStatus.STUDYING:
            return False, "正在学习，请勿打扰"
        if state.status == PetStatus.WORKING:
            return False, "正在工作，请勿打扰"
        now = time.time()
        if now - state.last_click_time < CLICK_COOLDOWN_SECONDS:
            remaining = int(CLICK_COOLDOWN_SECONDS - (now - state.last_click_time))
            return False, f"点击冷却中，{remaining}秒后可再次点击"
        return True, ""

    @staticmethod
    def can_study(state: GameState) -> tuple[bool, str]:
        if state.satiety < 30:
            return False, "饱食度不足（<30），无法学习"
        if state.status == PetStatus.SLEEPING:
            return False, "正在睡觉，无法学习"
        if state.status == PetStatus.WORKING:
            return False, "正在工作中，无法学习"
        if state.status == PetStatus.STUDYING:
            return False, "已经在学习中"
        return True, ""

    @staticmethod
    def can_work(state: GameState) -> tuple[bool, str]:
        if state.satiety < 30:
            return False, "饱食度不足（<30），无法工作"
        if state.status == PetStatus.SLEEPING:
            return False, "正在睡觉，无法工作"
        if state.status == PetStatus.STUDYING:
            return False, "正在学习中，无法工作"
        if state.status == PetStatus.WORKING:
            return False, "已经在工作中"
        return True, ""

    @staticmethod
    def can_feed(state: GameState) -> tuple[bool, str]:
        if state.status == PetStatus.SLEEPING:
            return False, "正在睡觉，无法喂食"
        if state.status == PetStatus.STUDYING:
            return False, "正在学习中，无法喂食"
        if state.status == PetStatus.WORKING:
            return False, "正在工作中，无法喂食"
        if state.food_count <= 0 and state.premium_food_count <= 0:
            return False, "没有食物，请先去商店购买"
        return True, ""

    @staticmethod
    def can_use_toy(state: GameState) -> tuple[bool, str]:
        if state.status == PetStatus.SLEEPING:
            return False, "正在睡觉，无法使用玩具"
        if state.status == PetStatus.STUDYING:
            return False, "正在学习中，无法使用玩具"
        if state.status == PetStatus.WORKING:
            return False, "正在工作中，无法使用玩具"
        if state.toy_count <= 0:
            return False, "没有玩具，请先去商店购买"
        return True, ""

    @staticmethod
    def can_sleep(state: GameState) -> tuple[bool, str]:
        if state.status == PetStatus.STUDYING:
            return False, "正在学习中，无法睡觉"
        if state.status == PetStatus.WORKING:
            return False, "正在工作中，无法睡觉"
        if state.status == PetStatus.SLEEPING:
            return False, "已经在睡觉"
        return True, ""

    @staticmethod
    def update_status(state: GameState):
        """根据当前状态优先级自动更新宠物显示状态（非任务状态下调用）"""
        if state.status in (PetStatus.STUDYING, PetStatus.WORKING, PetStatus.SLEEPING):
            return
        if state.satiety < 30:
            state.status = PetStatus.HUNGRY
        elif state.happy_timer > 0:
            state.status = PetStatus.HAPPY
        else:
            state.status = PetStatus.IDLE
