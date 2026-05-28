"""GameState 与 JSON dict 之间的序列化/反序列化"""

from core.game_state import GameState, PetStatus, PetSize


def _inventory_from_data(data: dict) -> dict[str, int]:
    inventory = {}
    raw_inventory = data.get("inventory")
    if isinstance(raw_inventory, dict):
        for item_id, count in raw_inventory.items():
            try:
                count_int = int(count)
            except (TypeError, ValueError):
                continue
            if count_int > 0:
                inventory[str(item_id)] = count_int

    legacy_map = {
        "food_count": "bread",
        "premium_food_count": "cat_meal",
        "toy_count": "teaser_wand",
    }
    for old_key, item_id in legacy_map.items():
        try:
            count = int(data.get(old_key, 0))
        except (TypeError, ValueError):
            count = 0
        if count > 0:
            inventory[item_id] = inventory.get(item_id, 0) + count

    return inventory


def _to_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def game_state_to_dict(state: GameState) -> dict:
    """将 GameState 序列化为 dict"""
    return {
        "version": 2,
        "coins": state.coins,
        "mood": state.mood,
        "satiety": state.satiety,
        "knowledge": state.knowledge,
        "status": state.status.value,
        "inventory": state.inventory,
        "satiety_decay_buff_remaining_seconds": state.satiety_decay_buff_remaining_seconds,
        "satiety_decay_buff_rate": state.satiety_decay_buff_rate,
        "mood_decay_buff_remaining_seconds": state.mood_decay_buff_remaining_seconds,
        "mood_decay_buff_rate": state.mood_decay_buff_rate,
        "current_task": state.current_task,
        "task_remaining_seconds": state.task_remaining_seconds,
        "position_x": state.position_x,
        "position_y": state.position_y,
        "pet_size": state.pet_size.value,
        "always_on_top": state.always_on_top,
        "show_status_text": state.show_status_text,
        "bubble_tips_enabled": True,
        "click_mood_enabled": True,
        "click_animation_enabled": True,
        "quiet_mode": False,
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
        mood=data.get("mood", 100),
        satiety=data.get("satiety", 100),
        knowledge=float(data.get("knowledge", 0)),
        status=status,
        inventory=_inventory_from_data(data),
        satiety_decay_buff_remaining_seconds=_to_int(data.get("satiety_decay_buff_remaining_seconds", 0)),
        satiety_decay_buff_rate=_to_float(data.get("satiety_decay_buff_rate", 0.0)),
        mood_decay_buff_remaining_seconds=_to_int(data.get("mood_decay_buff_remaining_seconds", 0)),
        mood_decay_buff_rate=_to_float(data.get("mood_decay_buff_rate", 0.0)),
        current_task=data.get("current_task"),
        task_remaining_seconds=data.get("task_remaining_seconds", 0),
        position_x=data.get("position_x", 1200),
        position_y=data.get("position_y", 700),
        pet_size=pet_size,
        always_on_top=data.get("always_on_top", True),
        show_status_text=data.get("show_status_text", False),
        bubble_tips_enabled=True,
        click_mood_enabled=True,
        click_animation_enabled=True,
        quiet_mode=False,
        last_saved_time=data.get("last_saved_time", ""),
    )
    state.clamp_values()
    return state
