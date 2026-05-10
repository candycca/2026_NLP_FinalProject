import os
import sys

from dotenv import load_dotenv

load_dotenv()

_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_BASE, "src"))

from prompt_builder import build_system_prompt
from llm_client import ask


def main() -> None:
    print("載入課程資料...", end=" ", flush=True)
    system_prompt = build_system_prompt(os.path.join(_BASE, "data"))
    print("完成。")
    print("輸入問題開始問答，輸入 'exit' 離開。\n")

    while True:
        try:
            question = input("問題：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再見！")
            break

        if not question:
            continue
        if question.lower() == "exit":
            print("再見！")
            break

        answer = ask(question, system_prompt)
        print(f"答案：{answer}\n")


if __name__ == "__main__":
    main()
