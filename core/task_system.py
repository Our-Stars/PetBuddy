"""学习、工作和睡觉任务系统"""

from .game_state import GameState, PetStatus

# 学习配置
STUDY_OPTIONS = [
    {"name": "学习 5分钟", "duration": 300, "knowledge_gain": 1},
    {"name": "学习 15分钟", "duration": 900, "knowledge_gain": 3.5},
    {"name": "学习 40分钟", "duration": 2400, "knowledge_gain": 10},
]
DEFAULT_STUDY_NAME = STUDY_OPTIONS[0]["name"]
LEGACY_STUDY_NAME = "学习"
STUDY_DURATION = STUDY_OPTIONS[0]["duration"]
STUDY_KNOWLEDGE_GAIN = STUDY_OPTIONS[0]["knowledge_gain"]

# 睡觉配置
SLEEP_OPTIONS = [
    {"name": "小睡 5分钟", "duration": 300, "mood_recovery": 5},
    {"name": "午睡 15分钟", "duration": 900, "mood_recovery": 18},
    {"name": "长睡 40分钟", "duration": 2400, "mood_recovery": 50},
]
DEFAULT_SLEEP_NAME = SLEEP_OPTIONS[0]["name"]
LEGACY_SLEEP_NAME = "睡觉"

# 工作列表（每个工种包含多个时长档位，长档位时薪略高；学识 > 500 后启动工作收益加成）
JOBS = [
    {
        "name": "捡瓶子",
        "knowledge": 0,
        "options": [
            {"label": "捡瓶子 5分钟", "duration": 300, "reward": 20},
            {"label": "捡瓶子 15分钟", "duration": 900, "reward": 65},
        ],
    },
    {
        "name": "发传单",
        "knowledge": 20,
        "options": [
            {"label": "发传单 5分钟", "duration": 300, "reward": 40},
            {"label": "发传单 15分钟", "duration": 900, "reward": 128},
            {"label": "发传单 30分钟", "duration": 1800, "reward": 270},
        ],
    },
    {
        "name": "外卖骑手",
        "knowledge": 100,
        "options": [
            {"label": "外卖骑手 10分钟", "duration": 600, "reward": 95},
            {"label": "外卖骑手 30分钟", "duration": 1800, "reward": 300},
        ],
    },
    {
        "name": "咖啡师",
        "knowledge": 200,
        "options": [
            {"label": "咖啡师 10分钟", "duration": 600, "reward": 105},
            {"label": "咖啡师 30分钟", "duration": 1800, "reward": 330},
            {"label": "咖啡师 60分钟", "duration": 3600, "reward": 690},
        ],
    },
    {
        "name": "宠物主播",
        "knowledge": 300,
        "options": [
            {"label": "宠物主播 15分钟", "duration": 900, "reward": 180},
            {"label": "宠物主播 30分钟", "duration": 1800, "reward": 375},
            {"label": "宠物主播 60分钟", "duration": 3600, "reward": 780},
        ],
    },
    {
        "name": "程序员宠物",
        "knowledge": 400,
        "options": [
            {"label": "程序员宠物 15分钟", "duration": 900, "reward": 203},
            {"label": "程序员宠物 30分钟", "duration": 1800, "reward": 420},
            {"label": "程序员宠物 60分钟", "duration": 3600, "reward": 900},
        ],
    },
    {
        "name": "神秘顾问",
        "knowledge": 500,
        "options": [
            {"label": "神秘顾问 20分钟", "duration": 1200, "reward": 310},
            {"label": "神秘顾问 40分钟", "duration": 2400, "reward": 640},
            {"label": "神秘顾问 60分钟", "duration": 3600, "reward": 1000},
        ],
    },
]

MAX_JOB_KNOWLEDGE = 500

# 旧存档兼容：旧版 task name → 新版默认档位
LEGACY_JOB_NAME_MAP = {
    "捡瓶子": "捡瓶子 5分钟",
    "发传单": "发传单 5分钟",
    "咖啡店帮工": "咖啡师 10分钟",
    "咖啡店帮工 10分钟": "咖啡师 10分钟",
    "咖啡店帮工 30分钟": "咖啡师 30分钟",
    "程序员宠物": "程序员宠物 15分钟",
    "神秘顾问": "神秘顾问 20分钟",
}


class TaskSystem:
    @staticmethod
    def get_available_jobs(knowledge: int) -> list[dict]:
        """返回学识要求 <= 当前学识的工作列表（按学识要求升序）"""
        return [j for j in JOBS if j["knowledge"] <= knowledge]

    @staticmethod
    def get_job_option_by_name(name: str) -> dict | None:
        """根据选项标签或旧版工种名查找工作选项；兼容旧存档。"""
        name = LEGACY_JOB_NAME_MAP.get(name, name)
        for job in JOBS:
            for opt in job["options"]:
                if opt["label"] == name:
                    return opt
        return None

    @staticmethod
    def get_job_by_name(name: str) -> dict | None:
        """根据工种名查找工种配置（保留兼容，用于获取 knowledge 等字段）。"""
        for job in JOBS:
            if job["name"] == name:
                return job
        return None

    @staticmethod
    def get_study_option_by_name(name: str | None) -> dict | None:
        if name == LEGACY_STUDY_NAME:
            return STUDY_OPTIONS[0]
        for option in STUDY_OPTIONS:
            if option["name"] == name:
                return option
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
    def start_study(state: GameState, option_name: str = DEFAULT_STUDY_NAME) -> bool:
        """开始学习，返回是否成功"""
        from .game_rules import GameRules
        can_start, _ = GameRules.can_study(state)
        if not can_start:
            return False
        option = TaskSystem.get_study_option_by_name(option_name)
        if option is None:
            return False
        state.status = PetStatus.STUDYING
        state.current_task = option["name"]
        state.task_remaining_seconds = option["duration"]
        return True

    @staticmethod
    def start_work(state: GameState, option_label: str) -> bool:
        """开始工作，返回是否成功。option_label 为档位标签如「捡瓶子 5分钟」。"""
        from .game_rules import GameRules
        can_start, _ = GameRules.can_work(state)
        if not can_start:
            return False
        option = TaskSystem.get_job_option_by_name(option_label)
        if option is None:
            return False
        # 查找所属工种，检查学识要求
        for job in JOBS:
            if any(opt["label"] == option["label"] for opt in job["options"]):
                if state.knowledge < job["knowledge"]:
                    return False
                break
        state.status = PetStatus.WORKING
        state.current_task = option["label"]
        state.task_remaining_seconds = option["duration"]
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
    def get_work_reward_multiplier(knowledge: float) -> float:
        """学识超过 MAX_JOB_KNOWLEDGE 后启动工作收益加成：每点 +0.2%，上限 +100%。"""
        if knowledge <= MAX_JOB_KNOWLEDGE:
            return 1.0
        bonus = (knowledge - MAX_JOB_KNOWLEDGE) * 0.002
        return 1.0 + min(bonus, 1.0)

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
            option = TaskSystem.get_study_option_by_name(state.current_task)
            gain = option["knowledge_gain"] if option else STUDY_KNOWLEDGE_GAIN
            state.knowledge += gain
            result["type"] = "study"
            result["message"] = f"学习完成！学识 +{gain:g}"
        elif state.status == PetStatus.WORKING:
            option = TaskSystem.get_job_option_by_name(state.current_task)
            if option:
                reward = option["reward"]
                multiplier = TaskSystem.get_work_reward_multiplier(state.knowledge)
                if multiplier > 1.0:
                    reward = int(reward * multiplier)
                state.coins += reward
                result["type"] = "work"
                if multiplier > 1.0:
                    bonus_pct = int((multiplier - 1.0) * 100)
                    result["message"] = f"工作完成：{state.current_task}！获得 {reward} 金币（学识加成 +{bonus_pct}%）"
                else:
                    result["message"] = f"工作完成：{state.current_task}！获得 {reward} 金币"

        # 恢复状态
        state.current_task = None
        state.task_remaining_seconds = 0
        state.status = PetStatus.IDLE
        from .game_rules import GameRules
        GameRules.update_status(state)

        return result
