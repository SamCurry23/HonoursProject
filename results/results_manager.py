

import json
import os
from datetime import datetime
from config import RESULTS_DIR


def save_results(results: dict, filename: str | None = None) -> str:
    
    os.makedirs(RESULTS_DIR, exist_ok=True)
    if not filename:
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_{ts}.json"

    path = os.path.join(RESULTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"  Results saved to: {path}")
    return path


def load_results(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_results() -> list[str]:
    if not os.path.exists(RESULTS_DIR):
        return []
    files = [
        os.path.join(RESULTS_DIR, f)
        for f in sorted(os.listdir(RESULTS_DIR))
        if f.endswith(".json")
    ]
    return files


def export_summary_csv(results: dict, path: str | None = None) -> str:
    
    import csv
    from config import DOMAINS, DOMAIN_DISPLAY_NAMES

    if not path:
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(RESULTS_DIR, f"summary_{ts}.csv")

    aggregated   = results.get("aggregated", {})
    model_keys   = list(aggregated.keys())

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["domain"] + model_keys)

        for domain in DOMAINS:
            row = [DOMAIN_DISPLAY_NAMES.get(domain, domain)]
            for mk in model_keys:
                domain_stats = aggregated[mk]["by_domain"].get(domain)
                row.append(domain_stats["mean"] if domain_stats else "")
            writer.writerow(row)

        row = ["OVERALL"]
        for mk in model_keys:
            row.append(aggregated[mk]["overall"]["mean"])
        writer.writerow(row)

    print(f"  CSV summary saved to: {path}")
    return path
