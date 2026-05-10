import csv
import os

_SYSTEM_TEMPLATE = """\
你是一個 NLP 課程的問答助手。回答時請遵守以下規則：
1. 答案要簡潔精確，不要過於冗長。
2. 若問題涉及以下課程專屬資訊，以下方資料為準，不要自行猜測。
3. 若問題屬於 NLP 學術知識，請依據你的知識回答。
4. 若確實無法回答，請說「無法回答」，不要捏造答案。
5. 在簡易測試時，會是文字輸入，請你用文字輸出；在實際使用時，輸入是 CSV 格式，請你用 CSV 格式輸出。

【課程專屬資訊】
{course_info}"""


def _load_csv(csv_path: str) -> str:
    pairs = []
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pairs.append(f"Q: {row['關鍵問題']}\nA: {row['答案']}")
    return "\n\n".join(pairs)


def _load_slides(slides_dir: str) -> str:
    if not os.path.isdir(slides_dir):
        return ""
    parts = []
    for fname in sorted(os.listdir(slides_dir)):
        if fname.endswith(".txt"):
            with open(os.path.join(slides_dir, fname), encoding="utf-8") as f:
                parts.append(f.read().strip())
    return "\n\n".join(parts)


def build_system_prompt(data_dir: str) -> str:
    course_info = _load_csv(os.path.join(data_dir, "NLP-Course-Info.csv"))

    slides = _load_slides(os.path.join(data_dir, "slides"))
    if slides:
        course_info += f"\n\n【課程教材】\n{slides}"

    return _SYSTEM_TEMPLATE.format(course_info=course_info)
