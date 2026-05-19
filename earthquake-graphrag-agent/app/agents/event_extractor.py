from __future__ import annotations

import re
from typing import Dict, List, Optional


class EventExtractorAgent:
    """灾情要素抽取 Agent：从输入文本中抽取震级、地点线索、灾害关键词。"""

    RISK_KEYWORDS = [
        "房屋倒塌", "建筑倒塌", "建筑物受损", "人员被困", "人员伤亡", "伤员", "道路塌方", "交通中断",
        "通信中断", "电力中断", "余震", "滑坡", "崩塌", "落石", "堰塞湖", "洪水", "泥石流",
        "危化品", "泄漏", "火灾", "爆炸", "有毒", "下风向", "学校", "学生", "医院", "医疗",
        "低温", "寒冷", "失温", "安置", "避难", "物资", "饮水", "食品", "帐篷", "老人", "儿童"
    ]

    SCENARIO_KEYWORDS = {
        "山区": ["山区", "山地", "村镇", "塌方", "落石", "滑坡"],
        "城市": ["城市", "城区", "高层", "小区", "交通拥堵", "医院"],
        "河谷堰塞湖": ["河谷", "河道", "堰塞湖", "洪水", "水位"],
        "工业园区": ["工业园", "危化", "储罐", "管线", "泄漏", "爆炸"],
        "高寒安置": ["低温", "寒冷", "棉被", "取暖", "失温"],
        "校园": ["学校", "校园", "学生", "教学楼", "家长"],
    }

    def run(self, disaster_text: str) -> Dict:
        magnitude = self._extract_magnitude(disaster_text)
        location = self._extract_location(disaster_text)
        risk_keywords = [kw for kw in self.RISK_KEYWORDS if kw in disaster_text]
        scenarios = self._detect_scenarios(disaster_text)
        return {
            "magnitude": magnitude,
            "location_hint": location,
            "risk_keywords": risk_keywords,
            "scenarios": scenarios,
            "raw_text": disaster_text,
        }

    @staticmethod
    def _extract_magnitude(text: str) -> Optional[float]:
        patterns = [
            r"(\d+(?:\.\d+)?)\s*级地震",
            r"震级\s*(\d+(?:\.\d+)?)",
            r"M\s*(\d+(?:\.\d+)?)",
            r"Mw\s*(\d+(?:\.\d+)?)",
        ]
        for p in patterns:
            m = re.search(p, text, flags=re.IGNORECASE)
            if m:
                try:
                    return float(m.group(1))
                except ValueError:
                    return None
        return None

    @staticmethod
    def _extract_location(text: str) -> str:
        # 简易地点线索抽取。真实系统应替换为地名识别模型或行政区划词典。
        m = re.search(r"([\u4e00-\u9fa5]{2,20}?)(发生|突发|出现|遭遇)(\d+(?:\.\d+)?级)?地震", text)
        if m:
            return m.group(1)
        m = re.search(r"(某[\u4e00-\u9fa5]{1,8})", text)
        if m:
            return m.group(1)
        return "未知区域"

    def _detect_scenarios(self, text: str) -> List[str]:
        result = []
        for scene, kws in self.SCENARIO_KEYWORDS.items():
            if any(kw in text for kw in kws):
                result.append(scene)
        return result or ["综合地震灾情"]
