"""商店系统：购买、道具使用"""

from .game_state import GameState

# 商品定义
SHOP_ITEMS = [
    {"name": "普通食物", "price": 20, "effect": "satiety", "value": 20, "mood_bonus": 0, "type": "food",
     "desc": "饱食度 +20"},
    {"name": "高级食物", "price": 50, "effect": "satiety", "value": 50, "mood_bonus": 5, "type": "premium_food",
     "desc": "饱食度 +50，心情 +5"},
    {"name": "玩具", "price": 20, "effect": "mood", "value": 20, "mood_bonus": 0, "type": "toy",
     "desc": "心情 +20（购买后存入背包，非任务中可使用）"},
    {"name": "小床升级", "price": 200, "effect": "bed", "value": 1, "mood_bonus": 0, "type": "upgrade",
     "desc": "小床等级 +1"},
]


class ShopSystem:
    @staticmethod
    def get_items() -> list[dict]:
        return SHOP_ITEMS

    @staticmethod
    def get_item_by_name(item_name: str) -> dict | None:
        for item in SHOP_ITEMS:
            if item["name"] == item_name:
                return item
        return None

    @staticmethod
    def buy(state: GameState, item_name: str) -> tuple[bool, str]:
        """购买商品，返回 (成功, 消息)"""
        item = ShopSystem.get_item_by_name(item_name)
        if item is None:
            return False, "商品不存在"

        if state.coins < item["price"]:
            return False, f"金币不足，需要 {item['price']} 金币"

        state.coins -= item["price"]

        if item["type"] == "food":
            state.food_count += 1
            return True, f"购买了 {item['name']}！当前库存：{state.food_count} 个"
        elif item["type"] == "premium_food":
            state.premium_food_count += 1
            return True, f"购买了 {item['name']}！当前库存：{state.premium_food_count} 个"
        elif item["type"] == "toy":
            state.toy_count += 1
            return True, f"购买了 {item['name']}！当前库存：{state.toy_count} 个"
        elif item["type"] == "upgrade":
            state.bed_level += item["value"]
            return True, f"小床升级成功！当前等级：{state.bed_level}"
        return False, "未知错误"

    @staticmethod
    def use_food(state: GameState, is_premium: bool = False) -> tuple[bool, str]:
        """喂食宠物，返回 (成功, 消息)"""
        from .game_rules import GameRules
        can_feed, reason = GameRules.can_feed(state)
        if not can_feed:
            return False, reason

        if is_premium:
            if state.premium_food_count <= 0:
                return False, "没有高级食物"
            item = ShopSystem.get_item_by_name("高级食物")
            satiety_gain = item["value"]
            mood_gain = item["mood_bonus"]
            state.premium_food_count -= 1
            state.satiety = min(100, state.satiety + satiety_gain)
            state.mood = min(100, state.mood + mood_gain)
            state.clamp_values()
            return True, f"喂食高级食物！饱食度 +{satiety_gain}，心情 +{mood_gain}"
        else:
            if state.food_count <= 0:
                return False, "没有普通食物"
            item = ShopSystem.get_item_by_name("普通食物")
            satiety_gain = item["value"]
            state.food_count -= 1
            state.satiety = min(100, state.satiety + satiety_gain)
            state.clamp_values()
            return True, f"喂食普通食物！饱食度 +{satiety_gain}"

    @staticmethod
    def use_toy(state: GameState) -> tuple[bool, str]:
        """使用玩具，返回 (成功, 消息)"""
        from .game_rules import GameRules
        can_use, reason = GameRules.can_use_toy(state)
        if not can_use:
            return False, reason

        if state.toy_count <= 0:
            return False, "没有玩具"
        item = ShopSystem.get_item_by_name("玩具")
        mood_gain = item["value"]
        state.toy_count -= 1
        state.mood = min(100, state.mood + mood_gain)
        state.clamp_values()
        return True, f"使用了玩具！心情 +{mood_gain}"
