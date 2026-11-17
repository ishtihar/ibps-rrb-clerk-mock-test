#!/usr/bin/env python3
"""Refresh exactly 100 self-checked original arithmetic practice questions weekly."""
import datetime as dt
import hashlib
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
START = "// WEEKLY_QUESTIONS_START"
END = "// WEEKLY_QUESTIONS_END"
today = dt.datetime.now(dt.timezone.utc).date()
week = today.isocalendar()
seed = f"{week.year}-W{week.week:02d}"
rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16], 16))
questions = []
seen = set()

def add(subject, topic, prompt, answer, explanation, distractors):
    if prompt in seen:
        return
    seen.add(prompt)
    choices = list(dict.fromkeys([str(answer)] + [str(x) for x in distractors]))
    if len(choices) < 4:
        raise ValueError(f"Duplicate choices: {prompt}")
    choices = choices[:4]
    rng.shuffle(choices)
    idx = choices.index(str(answer))
    assert choices[idx] == str(answer) and len(set(choices)) == 4
    questions.append([subject, topic, prompt, choices, idx, explanation])

for i in range(25):
    a = 18 + i * 7 + rng.randint(1, 5)
    b = 3 + i % 9
    c = 4 + rng.randint(1, 12)
    ans = a * b + c
    add("Quantitative Aptitude", "Simplification", f"{a} × {b} + {c} = ?", ans,
        f"पहले गुणा करें: {a} × {b} = {a*b}, फिर {c} जोड़ें: {ans}.",
        [ans + 2, ans - 3, ans + 5])
for i in range(25):
    base = 400 + 40 * i + rng.randint(1, 9) * 20
    rate = [5, 10, 15, 20, 25][i % 5]
    ans = base * rate // 100
    add("Quantitative Aptitude", "Percentage", f"{base} का {rate}% कितना है?", ans,
        f"{base} × {rate} / 100 = {ans}.",
        [ans + 10, ans - 10, ans + 20])
for i in range(25):
    first = 3 + i * 2 + rng.randint(0, 2)
    step = 2 + (i % 7)
    seq = [first + j * step for j in range(4)]
    ans = first + 4 * step
    add("Reasoning", "Series", f"अगला पद चुनें: {', '.join(map(str, seq))}, ?", ans,
        f"हर बार {step} जोड़ते हैं, इसलिए अगला पद {ans} है.",
        [ans - step, ans + step, ans + 2 * step])
for i in range(25):
    first = 12 + i * 3 + rng.randint(0, 3)
    second = first - 2 - (i % 4)
    third = second - 1 - (i % 3)
    ans = "A > C"
    add("Reasoning", "Inequality",
        f"यदि A = {first}, B = {second}, C = {third}, तो सही संबंध चुनें.",
        ans, f"A = {first} और C = {third}; इसलिए A > C.",
        ["A < C", "A = C", "B < C"])
assert len(questions) == 100, len(questions)
content = INDEX.read_text(encoding="utf-8")
replacement = START + "\nconst WEEKLY_QUESTIONS=" + json.dumps(questions, ensure_ascii=False, separators=(",", ":")) + ";\n" + END
pattern = re.escape(START) + r".*?" + re.escape(END)
if not re.search(pattern, content, re.S):
    raise RuntimeError("Missing weekly question markers in index.html")
content = re.sub(pattern, lambda _: replacement, content, count=1, flags=re.S)
INDEX.write_text(content, encoding="utf-8")
summary = {"week": seed, "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
           "question_count": len(questions), "topics": {"Simplification":25,"Percentage":25,"Series":25,"Inequality":25}}
(ROOT / "weekly-update.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False))
