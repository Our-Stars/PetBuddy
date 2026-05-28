"""商店系统：购买、道具使用"""

from .game_state import GameState

FOOD_ITEMS = [
    {
        "id": "bread",
        "name": "面包",
        "price": 15,
        "type": "food",
        "satiety": 18,
        "mood": 0,
        "desc": "饱食 +18",
    },
    {
        "id": "milk",
        "name": "牛奶",
        "price": 25,
        "type": "food",
        "satiety": 25,
        "mood": 2,
        "desc": "饱食 +25，心情 +2",
    },
    {
        "id": "cola",
        "name": "可乐",
        "price": 30,
        "type": "food",
        "satiety": 8,
        "mood": 12,
        "desc": "饱食 +8，心情 +12",
    },
    {
        "id": "lollipop",
        "name": "棒棒糖",
        "price": 35,
        "type": "food",
        "satiety": 5,
        "mood": 18,
        "desc": "饱食 +5，心情 +18",
    },
    {
        "id": "cat_meal",
        "name": "猫饭",
        "price": 70,
        "type": "food",
        "satiety": 65,
        "mood": 6,
        "buff_type": "satiety_decay",
        "buff_duration": 1200,
        "buff_rate": 0.20,
        "desc": "饱食 +65，心情 +6；20分钟内饱食下降速度 -20%",
    },
    {
        "id": "deluxe_can",
        "name": "豪华猫罐头",
        "price": 130,
        "type": "food",
        "satiety": 95,
        "mood": 12,
        "buff_type": "satiety_decay",
        "buff_duration": 2400,
        "buff_rate": 0.35,
        "desc": "饱食 +95，心情 +12；40分钟内饱食下降速度 -35%",
    },
]

TOY_ITEMS = [
    {
        "id": "paper_ball",
        "name": "纸团",
        "price": 10,
        "type": "toy",
        "mood": 8,
        "desc": "心情 +8",
    },
    {
        "id": "teaser_wand",
        "name": "逗猫棒",
        "price": 25,
        "type": "toy",
        "mood": 22,
        "desc": "心情 +22",
    },
    {
        "id": "scratching_board",
        "name": "猫抓板",
        "price": 55,
        "type": "toy",
        "mood": 40,
        "buff_type": "mood_decay",
        "buff_duration": 900,
        "buff_rate": 0.15,
        "desc": "心情 +40；15分钟内心情下降速度 -15%",
    },
    {
        "id": "yarn_ball",
        "name": "毛线球",
        "price": 75,
        "type": "toy",
        "mood": 52,
        "buff_type": "mood_decay",
        "buff_duration": 1200,
        "buff_rate": 0.20,
        "desc": "心情 +52；20分钟内心情下降速度 -20%",
    },
    {
        "id": "cat_tree",
        "name": "猫爬架",
        "price": 150,
        "type": "toy",
        "mood": 85,
        "buff_type": "mood_decay",
        "buff_duration": 2400,
        "buff_rate": 0.35,
        "desc": "心情 +85；40分钟内心情下降速度 -35%",
    },
]

SHOP_ITEMS = FOOD_ITEMS + TOY_ITEMS

LEGACY_ITEM_MAP = {
    "普通食物": "bread",
    "高级食物": "cat_meal",
    "玩具": "teaser_wand",
}


class ShopSystem:
    @staticmethod
    def get_items() -> list[dict]:
        return SHOP_ITEMS

    @staticmethod
    def get_items_by_type(item_type: str) -> list[dict]:
        return [item for item in SHOP_ITEMS if item["type"] == item_type]

    @staticmethod
    def get_item(item_id_or_name: str) -> dict | None:
        item_id_or_name = LEGACY_ITEM_MAP.get(item_id_or_name, item_id_or_name)
        for item in SHOP_ITEMS:
            if item["id"] == item_id_or_name or item["name"] == item_id_or_name:
                return item
        return None

    @staticmethod
    def get_item_by_name(item_name: str) -> dict | None:
        return ShopSystem.get_item(item_name)

    @staticmethod
    def get_inventory_count(state: GameState, item_id_or_name: str) -> int:
        item = ShopSystem.get_item(item_id_or_name)
        if item is None:
            return 0
        return int(state.inventory.get(item["id"], 0))

    @staticmethod
    def has_item_type(state: GameState, item_type: str) -> bool:
        for item in ShopSystem.get_items_by_type(item_type):
            if ShopSystem.get_inventory_count(state, item["id"]) > 0:
                return True
        return False

    @staticmethod
    def inventory_summary(state: GameState) -> str:
        parts = []
        for item in SHOP_ITEMS:
            count = ShopSystem.get_inventory_count(state, item["id"])
            if count > 0:
                parts.append(f"{item['name']} x{count}")
        return "、".join(parts) if parts else "无"

    @staticmethod
    def buy(state: GameState, item_id_or_name: str) -> tuple[bool, str]:
        """购买商品，返回 (成功, 消息)"""
        item = ShopSystem.get_item(item_id_or_name)
        if item is None:
            return False, "商品不存在"

        if state.coins < item["price"]:
            return False, f"金币不足，需要 {item['price']} 金币"

        state.coins -= item["price"]
        state.inventory[item["id"]] = ShopSystem.get_inventory_count(state, item["id"]) + 1
        return True, f"购买了 {item['name']}！当前库存：{state.inventory[item['id']]} 个"

    @staticmethod
    def use_food(state: GameState, item_id_or_name: str) -> tuple[bool, str]:
        """喂食宠物，返回 (成功, 消息)"""
        from .game_rules import GameRules
        can_feed, reason = GameRules.can_feed(state)
        if not can_feed:
            return False, reason

        item = ShopSystem.get_item(item_id_or_name)
        if item is None or item["type"] != "food":
            return False, "食物不存在"
        if ShopSystem.get_inventory_count(state, item["id"]) <= 0:
            return False, f"没有{item['name']}"

        state.inventory[item["id"]] -= 1
        state.satiety = min(100, state.satiety + item.get("satiety", 0))
        state.mood = min(100, state.mood + item.get("mood", 0))
        ShopSystem._apply_buff(state, item)
        state.clamp_values()

        parts = []
        if item.get("satiety", 0):
            parts.append(f"饱食度 +{item['satiety']}")
        if item.get("mood", 0):
            parts.append(f"心情 +{item['mood']}")
        buff_text = ShopSystem._buff_message(item)
        if buff_text:
            parts.append(buff_text)
        return True, f"喂食{item['name']}！{'，'.join(parts)}"

    @staticmethod
    def use_toy(state: GameState, item_id_or_name: str) -> tuple[bool, str]:
        """使用玩具，返回 (成功, 消息)"""
        from .game_rules import GameRules
        can_use, reason = GameRules.can_use_toy(state)
        if not can_use:
            return False, reason

        item = ShopSystem.get_item(item_id_or_name)
        if item is None or item["type"] != "toy":
            return False, "玩具不存在"
        if ShopSystem.get_inventory_count(state, item["id"]) <= 0:
            return False, f"没有{item['name']}"

        state.inventory[item["id"]] -= 1
        state.mood = min(100, state.mood + item.get("mood", 0))
        ShopSystem._apply_buff(state, item)
        state.clamp_values()

        parts = []
        if item.get("mood", 0):
            parts.append(f"心情 +{item['mood']}")
        buff_text = ShopSystem._buff_message(item)
        if buff_text:
            parts.append(buff_text)
        return True, f"玩耍：{item['name']}！{'，'.join(parts)}"

    @staticmethod
    def _apply_buff(state: GameState, item: dict):
        buff_type = item.get("buff_type")
        duration = int(item.get("buff_duration", 0))
        rate = float(item.get("buff_rate", 0))
        if duration <= 0 or rate <= 0:
            return
        if buff_type == "satiety_decay":
            state.satiety_decay_buff_remaining_seconds = duration
            state.satiety_decay_buff_rate = rate
        elif buff_type == "mood_decay":
            state.mood_decay_buff_remaining_seconds = duration
            state.mood_decay_buff_rate = rate

    @staticmethod
    def _buff_message(item: dict) -> str:
        buff_type = item.get("buff_type")
        duration = int(item.get("buff_duration", 0))
        rate = float(item.get("buff_rate", 0))
        if not buff_type or duration <= 0 or rate <= 0:
            return ""
        mins = duration // 60
        percent = int(rate * 100)
        if buff_type == "satiety_decay":
            return f"{mins}分钟内饱食下降速度 -{percent}%"
        if buff_type == "mood_decay":
            return f"{mins}分钟内心情下降速度 -{percent}%"
        return ""
