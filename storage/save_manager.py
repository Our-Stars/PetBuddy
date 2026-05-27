"""本地 JSON 存档读写、异常保护"""

import json
import os
import shutil
import tempfile
from datetime import datetime
from .game_state_io import game_state_to_dict, dict_to_game_state, GameState


class SaveManager:
    """存档管理器：原子写入 + 备份保护"""

    def __init__(self, save_dir: str):
        self.save_dir = save_dir
        self.save_path = os.path.join(save_dir, "save.json")
        self.backup_path = os.path.join(save_dir, "save_backup.json")

    def save(self, state: GameState) -> bool:
        """保存存档（原子写入），返回是否成功"""
        try:
            state.last_saved_time = datetime.now().isoformat()
            data = game_state_to_dict(state)
            json_str = json.dumps(data, ensure_ascii=False, indent=2)

            os.makedirs(self.save_dir, exist_ok=True)

            # 先写入临时文件
            fd, tmp_path = tempfile.mkstemp(dir=self.save_dir, suffix=".json")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(json_str)

            # 备份旧存档
            if os.path.exists(self.save_path):
                shutil.copy2(self.save_path, self.backup_path)

            # 原子替换
            os.replace(tmp_path, self.save_path)
            return True
        except Exception as e:
            print(f"[SaveManager] 保存失败: {e}")
            return False

    def load(self) -> GameState | None:
        """读取存档，损坏时尝试恢复备份，都失败返回 None"""
        data = self._read_json(self.save_path)
        if data is None:
            print("[SaveManager] 正式存档损坏，尝试恢复备份...")
            data = self._read_json(self.backup_path)
        if data is None:
            print("[SaveManager] 备份也损坏，使用默认存档")
            return None
        try:
            return dict_to_game_state(data)
        except Exception as e:
            print(f"[SaveManager] 解析存档失败: {e}")
            return None

    def _read_json(self, path: str) -> dict | None:
        """安全读取 JSON 文件"""
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[SaveManager] 读取 {path} 失败: {e}")
            return None

    def reset(self) -> bool:
        """重置存档（删除存档文件）"""
        try:
            for p in (self.save_path, self.backup_path):
                if os.path.exists(p):
                    os.remove(p)
            return True
        except OSError as e:
            print(f"[SaveManager] 重置存档失败: {e}")
            return False
