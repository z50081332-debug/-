from __future__ import annotations

import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Earthquake GraphRAG Agent")
    parser.add_argument("--cli", action="store_true", help="启动命令行模式")
    parser.add_argument("--api", action="store_true", help="启动 FastAPI 服务")
    parser.add_argument("--host", default="127.0.0.1", help="API 服务地址")
    parser.add_argument("--port", default=8000, type=int, help="API 服务端口")
    args = parser.parse_args()

    if args.cli:
        from app.cli import run_cli
        run_cli()
        return

    if args.api:
        uvicorn.run("app.api:app", host=args.host, port=args.port, reload=False)
        return

    print("请选择启动方式：")
    print("  python main.py --cli")
    print("  python main.py --api --host 127.0.0.1 --port 8000")


if __name__ == "__main__":
    main()
