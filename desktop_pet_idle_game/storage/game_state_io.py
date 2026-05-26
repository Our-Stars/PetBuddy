"""GameState 与 JSON dict 之间的序列化/反序列化"""

from core.game_state import GameState, PetStatus, PetSize


def game_state_to_dict(state: GameState) -> dict:
    """将 GameState 序列化为 dict"""
    return {
        "version": 1,
        "coins": state.coins,
        "mood": state.mood,
        "satiety": state.satiety,
        "knowledge": state.knowledge,
        "status": state.status.value,
        "food_count": state.food_count,
        "premium_food_count": state.premium_food_count,
        "bed_level": state.bed_level,
        "current_task": state.current_task,
        "task_remaining_seconds": state.task_remaining_seconds,
        "position_x": state.position_x,
        "position_y": state.position_y,
        "pet_size": state.pet_size.value,
        "always_on_top": state.always_on_top,
        "show_status_text": state.show_status_text,
        "bubble_tips_enabled": state.bubble_tips_enabled,
        "click_mood_enabled": state.click_mood_enabled,
        "click_animation_enabled": state.click_animation_enabled,
        "quiet_mode": state.quiet_mode,
        "last_saved_time": state.last_saved_time,
    }


def dict_to_game_state(data: dict) -> GameState:
    """从 dict 反序列化为 GameState"""
    status_str = data.get("status", "idle")
    try:
        status = PetStatus(status_str)
    except ValueError:
        status = PetStatus.IDLE

    size_str = data.get("pet_size", "medium")
    try:
        pet_size = PetSize(size_str)
    except ValueError:
        pet_size = PetSize.MEDIUM

    state = GameState(
        coins=data.get("coins", 0),
        mood=data.get("mood", 80),
        satiety=data.get("satiety", 80),
        knowledge=data.get("knowledge", 0),
        status=status,
        food_count=data.get("food_count", 0),
        premium_food_count=data.get("premium_food_count", 0),
        bed_level=data.get("bed_level", 0),
        current_task=data.get("current_task"),
        task_remaining_seconds=data.get("task_remaining_seconds", 0),
        position_x=data.get("position_x", 1200),
        position_y=data.get("position_y", 700),
        pet_size=pet_size,
        always_on_top=data.get("always_on_top", True),
        show_status_text=data.get("show_status_text", False),
        bubble_tips_enabled=data.get("bubble_tips_enabled", True),
        click_mood_enabled=data.get("click_mood_enabled", True),
        click_animation_enabled=data.get("click_animation_enabled", True),
        quiet_mode=data.get("quiet_mode", False),
        last_saved_time=data.get("last_saved_time", ""),
    )
    state.clamp_values()
    return state
