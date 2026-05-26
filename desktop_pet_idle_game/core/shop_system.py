"""商店系统：购买、道具使用"""

from .game_state import GameState

# 商品定义
SHOP_ITEMS = [
    {"name": "普通食物", "price": 20, "effect": "satiety", "value": 20, "mood_bonus": 0, "type": "food"},
    {"name": "高级食物", "price": 80, "effect": "satiety", "value": 50, "mood_bonus": 5, "type": "premium_food"},
    {"name": "玩具", "price": 50, "effect": "mood", "value": 15, "mood_bonus": 0, "type": "toy"},
    {"name": "小床升级", "price": 200, "effect": "bed", "value": 1, "mood_bonus": 0, "type": "upgrade"},
]


class ShopSystem:
    @staticmethod
    def get_items() -> list[dict]:
        return SHOP_ITEMS

    @staticmethod
    def buy(state: GameState, item_name: str) -> tuple[bool, str]:
        """购买商品，返回 (成功, 消息)"""
        item = None
        for i in SHOP_ITEMS:
            if i["name"] == item_name:
                item = i
                break
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
            state.mood = min(100, state.mood + item["value"])
            state.clamp_values()
            return True, f"使用了 {item['name']}！心情 +{item['value']}"
        elif item["type"] == "upgrade":
            state.bed_level += item["value"]
            return True, f"小床升级成功！当前等级：{state.bed_level}"
        return False, "未知错误"

    @staticmethod
    def use_food(state: GameState, is_premium: bool = False) -> tuple[bool, str]:
        """喂食宠物，返回 (成功, 消息)"""
        if is_premium:
            if state.premium_food_count <= 0:
                return False, "没有高级食物"
            state.premium_food_count -= 1
            state.satiety = min(100, state.satiety + 50)
            state.mood = min(100, state.mood + 5)
            state.clamp_values()
            return True, "喂食高级食物！饱食度 +50，心情 +5"
        else:
            if state.food_count <= 0:
                return False, "没有普通食物"
            state.food_count -= 1
            state.satiety = min(100, state.satiety + 20)
            state.clamp_values()
            return True, "喂食普通食物！饱食度 +20"
