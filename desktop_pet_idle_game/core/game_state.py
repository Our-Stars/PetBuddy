"""核心游戏状态数据类"""

from dataclasses import dataclass, field
from enum import Enum


class PetStatus(Enum):
    IDLE = "idle"
    HAPPY = "happy"
    HUNGRY = "hungry"
    STUDYING = "studying"
    WORKING = "working"


class PetSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass
class GameState:
    coins: int = 0
    mood: int = 80
    satiety: int = 80
    knowledge: int = 0
    status: PetStatus = PetStatus.IDLE
    food_count: int = 0
    premium_food_count: int = 0
    bed_level: int = 0
    current_task: str | None = None
    task_remaining_seconds: int = 0
    position_x: int = 1200
    position_y: int = 700
    pet_size: PetSize = PetSize.MEDIUM
    always_on_top: bool = True
    show_status_text: bool = False
    bubble_tips_enabled: bool = True
    click_mood_enabled: bool = True
    click_animation_enabled: bool = True
    quiet_mode: bool = False
    last_saved_time: str = ""

    # 非持久化字段（运行时状态）
    elapsed_seconds: int = field(default=0, repr=False)
    last_click_time: float = field(default=0.0, repr=False)
    happy_timer: int = field(default=0, repr=False)
    natural_coin_progress: float = field(default=0.0, repr=False)

    @property
    def pet_size_pixels(self) -> int:
        """返回宠物窗口的像素大小"""
        return {PetSize.SMALL: 100, PetSize.MEDIUM: 150, PetSize.LARGE: 200}[self.pet_size]

    def clamp_values(self):
        """将心情和饱食度限制在 0-100 范围内"""
        self.mood = max(0, min(100, self.mood))
        self.satiety = max(0, min(100, self.satiety))
