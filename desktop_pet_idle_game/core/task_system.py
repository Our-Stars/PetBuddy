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
        state.status = PetStatus.STUDYING
        state.current_task = "学习"
        state.task_remaining_seconds = STUDY_DURATION
        return True

    @staticmethod
    def start_work(state: GameState, job_name: str) -> bool:
        """开始工作，返回是否成功"""
        job = TaskSystem.get_job_by_name(job_name)
        if job is None:
            return False
        state.status = PetStatus.WORKING
        state.current_task = job_name
        state.task_remaining_seconds = job["duration"]
        return True

    @staticmethod
    def tick(state: GameState):
        """主循环每 tick 调用，处理任务倒计时"""
        if state.status not in (PetStatus.STUDYING, PetStatus.WORKING):
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

        if state.status == PetStatus.STUDYING:
            gain = STUDY_KNOWLEDGE_GAIN
            # 心情低于 20 时学识收益减半
            if state.mood < 20:
                gain = max(1, gain // 2)
            state.knowledge += gain
            result["type"] = "study"
            result["message"] = f"学习完成！学识 +{gain}"
        elif state.status == PetStatus.WORKING:
            job = TaskSystem.get_job_by_name(state.current_task)
            if job:
                base_reward = job["reward"]
                mood_mult = 1.0
                if state.mood >= 80:
                    mood_mult = 1.5
                elif state.mood >= 50:
                    mood_mult = 1.0
                elif state.mood >= 20:
                    mood_mult = 0.7
                else:
                    mood_mult = 0.3

                satiety_mult = 1.0
                if 30 <= state.satiety <= 59:
                    satiety_mult = 0.5

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
