

import json
import os
import random
from config import DATA_DIR, DOMAINS


def load_domain(domain: str) -> list[dict]:
    path = os.path.join(DATA_DIR, f"{domain}.json")
    if not os.path.exists(path):
        print(f"  [Warning] No question file found for domain '{domain}' at {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        questions = json.load(f)
    return questions


def load_all_questions() -> list[dict]:
    all_questions = []
    for domain in DOMAINS:
        questions = load_domain(domain)
        all_questions.extend(questions)
    return all_questions


def get_questions(
    domains: list[str] | None = None,
    difficulty: str | None = None,
    max_per_domain: int | None = None,
    shuffle: bool = True,
) -> list[dict]:
    
    selected_domains = domains if domains else DOMAINS
    result = []

    for domain in selected_domains:
        qs = load_domain(domain)

        if difficulty:
            qs = [q for q in qs if q.get("difficulty") == difficulty]

        if shuffle:
            random.shuffle(qs)

        if max_per_domain:
            qs = qs[:max_per_domain]

        result.extend(qs)

    return result


def get_summary() -> dict:
    summary = {}
    for domain in DOMAINS:
        qs = load_domain(domain)
        by_difficulty = {"easy": 0, "medium": 0, "hard": 0}
        for q in qs:
            d = q.get("difficulty", "unknown")
            if d in by_difficulty:
                by_difficulty[d] += 1
        summary[domain] = {"total": len(qs), "by_difficulty": by_difficulty}
    return summary
