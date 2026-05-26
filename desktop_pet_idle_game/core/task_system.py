"""学习和工作任务系统"""

from .game_state import GameState, PetStatus

# 学习配置
STUDY_DURATION = 60  # 秒
STUDY_KNOWLEDGE_GAIN = 1

# 工作列表
JOBS = [
    {"name": "捡瓶子", "knowledge": 0, "duration": 60, "reward": 20},
    {"name": "发传单", "knowledge": 10, "duration": 180, "reward": 100},
    {"name": "咖啡店帮工", "knowledge": 30, "duration": 300, "reward": 220},
    {"name": "程序员宠物", "knowledge": 60, "duration": 600, "reward": 520},
    {"name": "神秘顾问", "knowledge": 120, "duration": 1200, "reward": 1200},
]


class TaskSystem:
    @staticmethod
    def get_available_jobs(knowledge: int) -> list[dict]:
        """返回学识要求 <= 当前学识的工作列表（按学识要求升序）"""
        return [j for j in JOBS if j["knowledge"] <= knowledge]

    @staticmethod
    def get_job_by_name(name: str) -> dict | None:
        for j in JOBS:
            if j["name"] == name:
                return j
        return None

    @staticmethod
    def start_study(state: GameState) -> bool:
        """开始学习，返回是否成功"""
        from .game_rules import GameRules
        can_start, _ = GameRules.can_study(state)
        if not can_start:
            return False
        state.status = PetStatus.STUDYING
        state.current_task = "学习"
        state.task_remaining_seconds = STUDY_DURATION
        return True

    @staticmethod
    def start_work(state: GameState, job_name: str) -> bool:
        """开始工作，返回是否成功"""
        from .game_rules import GameRules
        can_start, _ = GameRules.can_work(state)
        if not can_start:
            return False
        job = TaskSystem.get_job_by_name(job_name)
        if job is None:
            return False
        if state.knowledge < job["knowledge"]:
            return False
        state.status = PetStatus.WORKING
        state.current_task = job_name
        state.task_remaining_seconds = job["duration"]
        return True

    @staticmethod
    def cancel_current_task(state: GameState) -> tuple[bool, str]:
        """取消当前学习或工作任务，不结算奖励。"""
        if state.status not in (PetStatus.STUDYING, PetStatus.WORKING) or state.current_task is None:
            return False, "当前没有正在进行的任务"

        task_name = state.current_task
        state.current_task = None
        state.task_remaining_seconds = 0
        state.status = PetStatus.IDLE

        from .game_rules import GameRules
        GameRules.update_status(state)
        return True, f"已停止任务：{task_name}"

    @staticmethod
    def tick(state: GameState):
        """主循环每 tick 调用，处理任务倒计时"""
        if state.status not in (PetStatus.STUDYING, PetStatus.WORKING):
            return

        if state.task_remaining_seconds <= 0:
            return

        if state.status == PetStatus.STUDYING and TaskSystem._study_speed_divisor(state) > 1:
            if state.elapsed_seconds % TaskSystem._study_speed_divisor(state) != 0:
                return

        state.task_remaining_seconds -= 1

    @staticmethod
    def _study_speed_divisor(state: GameState) -> int:
        """心情或饱食度较低时降低学习推进速度。"""
        if state.mood < 20 or state.satiety < 60:
            return 2
        return 1

    @staticmethod
    def check_completion(state: GameState) -> dict | None:
        """检查任务是否完成，完成则结算并返回结果；未完成返回 None"""
        if state.task_remaining_seconds > 0:
            return None
        if state.current_task is None:
            return None

        result = {"task": state.current_task, "type": "", "message": ""}

        if state.status == PetStatus.STUDYING:
            gain = STUDY_KNOWLEDGE_GAIN
            state.knowledge += gain
            result["type"] = "study"
            result["message"] = f"学习完成！学识 +{gain}"
        elif state.status == PetStatus.WORKING:
            job = TaskSystem.get_job_by_name(state.current_task)
            if job:
                base_reward = job["reward"]
                from .game_rules import GameRules
                mood_mult = GameRules.get_mood_multiplier(state.mood)
                satiety_mult = GameRules.get_satiety_multiplier(state.satiety)

                reward = int(base_reward * mood_mult * satiety_mult)
                state.coins += reward
                result["type"] = "work"
                result["message"] = f"工作完成：{state.current_task}！获得 {reward} 金币"
                if mood_mult != 1.0 or satiety_mult != 1.0:
                    result["message"] += f"（心情倍率 {mood_mult}x，饱食度倍率 {satiety_mult}x）"

        # 恢复状态
        state.current_task = None
        state.task_remaining_seconds = 0
        state.status = PetStatus.IDLE
        from .game_rules import GameRules
        GameRules.update_status(state)

        return result
