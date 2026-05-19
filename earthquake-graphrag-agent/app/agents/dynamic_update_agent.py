from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

from app.schemas import StrategyResult


class DynamicUpdateAgent:
    """动态更新 Agent：保存生成结果和人工反馈。"""

    def __init__(self, memory_file: Path, feedback_file: Path):
        self.memory_file = memory_file
        self.feedback_file = feedback_file

    def save_result(self, result: StrategyResult) -> None:
        records = self._load_json_list(self.memory_file)
        records.append(asdict(result))
        self._write_json_list(self.memory_file, records)

    def add_feedback(self, event_id: str, feedback_text: str, corrected_measures: Optional[List[str]] = None) -> Dict:
        records = self._load_json_list(self.feedback_file)
        item = {
            "event_id": event_id,
            "feedback_text": feedback_text,
            "corrected_measures": corrected_measures or [],
        }
        records.append(item)
        self._write_json_list(self.feedback_file, records)
        return item

    @staticmethod
    def _load_json_list(path: Path) -> List[Dict]:
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []

    @staticmethod
    def _write_json_list(path: Path, records: List[Dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(records, ensure_ascii=False, indent=2)
        text = text.encode("utf-8", errors="surrogateescape").decode("utf-8", errors="replace")
        path.write_text(text, encoding="utf-8")
