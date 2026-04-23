

import os
from datetime import datetime
from config import RESULTS_DIR, DOMAIN_DISPLAY_NAMES, MODELS


def generate(results: dict, notes_path: str | None = None) -> str:
    
    meta  = results.get("metadata", {})
    agg   = results.get("aggregated", {})
    obs   = results.get("observations", {})
    model_keys = meta.get("models_evaluated", list(agg.keys()))

    def model_name(k):
        return MODELS.get(k, {}).get("name", k.upper())

    ts      = meta.get("timestamp", datetime.now().isoformat())[:19].replace("T", " ")
    elapsed = meta.get("elapsed_seconds", 0)
    total_q = meta.get("total_questions", 0)

    lines = []
    lines += [
        f"# Evaluation Run Notes",
        f"",
        f"**Date/time:** {ts}  ",
        f"**Questions:** {total_q}  ",
        f"**Duration:** {elapsed}s  ",
        f"**Models:** {', '.join(model_name(m) for m in model_keys)}  ",
        f"",
        f"---",
        f"",
        f"## Overall Scores",
        f"",
        f"| Model | Overall |",
        f"|-------|---------|",
    ]
    for m in model_keys:
        score = agg[m]["overall"]["mean"]
        lines.append(f"| {model_name(m)} | {score:.1f}% |")

    lines += [""]

    lines += ["## Scores by Domain", ""]
    header = "| Domain | " + " | ".join(model_name(m) for m in model_keys) + " |"
    divider = "|--------|" + "|".join(["--------"] * len(model_keys)) + "|"
    lines += [header, divider]

    for domain, label in DOMAIN_DISPLAY_NAMES.items():
        row = f"| {label} |"
        for m in model_keys:
            s = agg[m]["by_domain"].get(domain, {}).get("mean")
            row += f" {s:.1f}% |" if s is not None else " N/A |"
        lines.append(row)
    lines.append("")

    lines += ["## Scores by Difficulty", ""]
    header = "| Difficulty | " + " | ".join(model_name(m) for m in model_keys) + " |"
    divider = "|------------|" + "|".join(["--------"] * len(model_keys)) + "|"
    lines += [header, divider]
    for diff in ["easy", "medium", "hard"]:
        row = f"| {diff.capitalize()} |"
        for m in model_keys:
            s = agg[m]["by_difficulty"].get(diff, {}).get("mean")
            row += f" {s:.1f}% |" if s is not None else " N/A |"
        lines.append(row)
    lines.append("")

    lines += ["## Automatic Observations", ""]

    best = obs.get("best_model_overall", "")
    if best:
        best_score = agg[best]["overall"]["mean"]
        lines.append(f"- **Best overall model:** {model_name(best)} ({best_score:.1f}%)")

    wd = obs.get("worst_domain_overall", {})
    if wd:
        label = DOMAIN_DISPLAY_NAMES.get(wd["domain"], wd["domain"])
        lines.append(f"- **Hardest domain for all models:** {label} (avg {wd['avg_score']:.1f}%)")

    spreads = obs.get("score_spread", {})
    if spreads:
        most_consistent = min(spreads, key=spreads.get)
        most_variable   = max(spreads, key=spreads.get)
        lines.append(f"- **Most consistent model:** {model_name(most_consistent)} "
                     f"(domain spread: {spreads[most_consistent]:.1f}pp)")
        lines.append(f"- **Most variable model:** {model_name(most_variable)} "
                     f"(domain spread: {spreads[most_variable]:.1f}pp)")

    strengths = obs.get("model_domain_strengths", {})
    for m, s in strengths.items():
        strong_label = DOMAIN_DISPLAY_NAMES.get(s["strongest"], s["strongest"])
        weak_label   = DOMAIN_DISPLAY_NAMES.get(s["weakest"],   s["weakest"])
        lines.append(
            f"- **{model_name(m)}:** strongest in {strong_label} ({s['strongest_score']:.1f}%), "
            f"weakest in {weak_label} ({s['weakest_score']:.1f}%)"
        )

    gaps = obs.get("biggest_gaps", [])
    if gaps:
        g = gaps[0]
        label = DOMAIN_DISPLAY_NAMES.get(g["domain"], g["domain"])
        lines.append(
            f"- **Largest inter-model gap:** {label} — "
            f"{model_name(g['best_model'])} scored {g['best_score']:.1f}% vs "
            f"{model_name(g['worst_model'])} at {g['worst_score']:.1f}% "
            f"(gap: {g['gap']:.1f}pp)"
        )

    refusals = obs.get("refusals", {})
    if refusals:
        for m, count in refusals.items():
            lines.append(f"- **{model_name(m)}** refused or declined to answer "
                         f"{count} ethics/creative question(s)")
    else:
        lines.append("- No refusals detected across ethics or creative questions")

    zeros = obs.get("all_zero_questions", [])
    if zeros:
        lines += ["", f"### Questions where all models scored 0 ({len(zeros)} found)", ""]
        lines.append("These may indicate overly strict scoring heuristics or ambiguous questions:")
        for z in zeros:
            lines.append(f"- `{z['id']}` [{z['domain']}]: {z['question']}")
    lines.append("")

    lines += [
        "---",
        "",
        "## Notes for Report Writing",
        "",
        "The following points are worth discussing in the relevant report sections:",
        "",
        "### Implementation section",
        f"- Evaluation ran {total_q} questions across {len(model_keys)} models in {elapsed}s",
        "- Rate limiting required exponential backoff with jitter — implemented in `base_client.py`",
        "- Gemini SDK was deprecated mid-project; migrated from `google-generativeai` to `google-genai`",
        "- `temperature=0` set on all models to ensure deterministic, reproducible responses",
        "",
        "### Scoring/evaluation section",
        "- Three scoring modes used: exact match (mathematics), keyword matching (factual/logical), rubric (ethics/creative)",
        "- Rubric scoring for subjective domains uses keyword presence + response length as proxies for quality",
        "- This is a known limitation — discuss in critical evaluation section",
    ]

    if zeros:
        lines.append(f"- {len(zeros)} question(s) scored 0 across all models — "
                     "review whether scoring heuristics are appropriate for these")

    lines += [
        "",
        "### Results/findings section",
    ]
    for m, s in strengths.items():
        strong_label = DOMAIN_DISPLAY_NAMES.get(s["strongest"], s["strongest"])
        weak_label   = DOMAIN_DISPLAY_NAMES.get(s["weakest"],   s["weakest"])
        lines.append(f"- {model_name(m)} shows domain-specific behaviour: strong in "
                     f"{strong_label}, weaker in {weak_label}")

    if gaps:
        g     = gaps[0]
        label = DOMAIN_DISPLAY_NAMES.get(g["domain"], g["domain"])
        lines.append(f"- The {label} domain shows the most variation between models ({g['gap']:.1f}pp gap), "
                     "suggesting this domain most effectively differentiates model capabilities")

    lines += [
        "",
        "### Critical evaluation section",
        "- No single model dominated across all domains — supports the project's core argument "
        "that domain-specific evaluation is more useful than a single overall score",
        "- Scoring methodology for ethics/creative is heuristic-based and should be "
        "acknowledged as a limitation",
        "- Results from a single run may not be fully reproducible; "
        "multiple runs would improve statistical validity",
        "- Dataset of 200 questions, while sufficient for demonstration, "
        "is smaller than established benchmarks (MMLU: 14,000+ questions)",
        "",
    ]

    content = "\n".join(lines)

    if not notes_path:
        ts_file = datetime.now().strftime("%Y%m%d_%H%M%S")
        notes_path = os.path.join(RESULTS_DIR, f"report_notes_{ts_file}.md")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Report notes saved to: {notes_path}")
    return notes_path
