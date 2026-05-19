from __future__ import annotations

from app.orchestrator import EarthquakeGraphRAGOrchestrator


def run_cli() -> None:
    orchestrator = EarthquakeGraphRAGOrchestrator()
    print("地震应急策略生成 GraphRAG Agent")
    print("输入灾情文本后回车。输入 exit 退出。")
    print("-" * 60)
    while True:
        text = input("请输入灾情：").strip()
        if text.lower() in {"exit", "quit", "q"}:
            print("已退出。")
            return
        if not text:
            print("输入为空，请重新输入。")
            continue
        result = orchestrator.generate_strategy(text)
        print("\n" + "=" * 60)
        print(f"事件 ID：{result.event_id}")
        print(result.strategy)
        print("=" * 60 + "\n")
