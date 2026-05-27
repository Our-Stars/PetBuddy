"""学习、工作和睡觉任务系统"""

from .game_state import GameState, PetStatus

# 学习配置
STUDY_DURATION = 300  # 秒
STUDY_KNOWLEDGE_GAIN = 1

# 睡觉配置
SLEEP_OPTIONS = [
    {"name": "小睡 5分钟", "duration": 300, "mood_recovery": 5},
    {"name": "午睡 15分钟", "duration": 900, "mood_recovery": 18},
    {"name": "长睡 40分钟", "duration": 2400, "mood_recovery": 50},
]
DEFAULT_SLEEP_NAME = SLEEP_OPTIONS[0]["name"]
LEGACY_SLEEP_NAME = "睡觉"

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
    def get_sleep_option_by_name(name: str | None) -> dict | None:
        if name == LEGACY_SLEEP_NAME:
            return SLEEP_OPTIONS[0]
        for option in SLEEP_OPTIONS:
            if option["name"] == name:
                return option
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
    def start_sleep(state: GameState, option_name: str = DEFAULT_SLEEP_NAME) -> bool:
        """开始睡觉，返回是否成功"""
        from .game_rules import GameRules
        can_start, _ = GameRules.can_sleep(state)
        if not can_start:
            return False
        option = TaskSystem.get_sleep_option_by_name(option_name)
        if option is None:
            return False
        state.status = PetStatus.SLEEPING
        state.current_task = option["name"]
        state.task_remaining_seconds = option["duration"]
        return True

    @staticmethod
    def cancel_current_task(state: GameState) -> tuple[bool, str]:
        """取消当前任务（学习/工作/睡觉），不结算奖励。"""
        if state.status not in (PetStatus.STUDYING, PetStatus.WORKING, PetStatus.SLEEPING) or state.current_task is None:
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
        if state.status not in (PetStatus.STUDYING, PetStatus.WORKING, PetStatus.SLEEPING):
            return

        if state.task_remaining_seconds <= 0:
            return

        state.task_remaining_seconds -= 1

    @staticmethod
    def check_completion(state: GameState) -> dict | None:
        """检查任务是否完成，完成则结算并返回结果；未完成返回 None"""
        if state.task_remaining_seconds > 0:
            return None
        if state.current_task is None:
            return None

        result = {"task": state.current_task, "type": "", "message": ""}

        if state.status == PetStatus.SLEEPING:
            option = TaskSystem.get_sleep_option_by_name(state.current_task)
            recovery = option["mood_recovery"] if option else 0
            state.mood = min(100, state.mood + recovery)
            result["type"] = "sleep"
            result["message"] = f"睡醒了！心情 +{recovery}"
        elif state.status == PetStatus.STUDYING:
            gain = STUDY_KNOWLEDGE_GAIN
            state.knowledge += gain
            result["type"] = "study"
            result["message"] = f"学习完成！学识 +{gain:.0f}"
        elif state.status == PetStatus.WORKING:
            job = TaskSystem.get_job_by_name(state.current_task)
            if job:
                reward = job["reward"]
                state.coins += reward
                result["type"] = "work"
                result["message"] = f"工作完成：{state.current_task}！获得 {reward} 金币"

        # 恢复状态
        state.current_task = None
        state.task_remaining_seconds = 0
        state.status = PetStatus.IDLE
        from .game_rules import GameRules
        GameRules.update_status(state)

        return result
