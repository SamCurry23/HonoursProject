

import time
from datetime import datetime
from config import DOMAIN_DISPLAY_NAMES
from evaluation.scorer import score_response


# ── Prompt construction ────────────────────────────────────────────────────────

def _build_prompt(question: dict) -> str:
    
    domain = question.get("domain", "general")
    q_type = question.get("type", "keyword")

    if q_type == "exact":
        instruction = (
            "Answer the following question with a direct, concise response. "
            "Give only the answer — no explanation unless specifically asked."
        )
    elif q_type == "rubric":
        instruction = (
            "Answer the following question thoughtfully and in detail. "
            "Provide a structured, reasoned response."
        )
    else:
        instruction = (
            "Answer the following question clearly and accurately. "
            "Be direct and concise."
        )

    return f"{instruction}\n\nQuestion: {question['question']}"



def run_evaluation(
    model_manager,
    questions: list[dict],
    verbose: bool = True,
) -> dict:
    
    enabled_models = model_manager.get_enabled_models()
    total = len(questions)
    start_time = datetime.now()

    raw_results = []

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Starting evaluation: {total} questions × {len(enabled_models)} models")
        print(f"  Models: {', '.join(enabled_models)}")
        print(f"{'='*60}\n")

    for idx, question in enumerate(questions, 1):
        q_id     = question.get("id", f"q_{idx}")
        domain   = question.get("domain", "unknown")
        q_text   = question.get("question", "")

        if verbose:
            difficulty = question.get("difficulty", "")
            print(f"  [{idx}/{total}] {q_id} [{domain}/{difficulty}]")

        q_result = {
            "question_id": q_id,
            "question":    q_text,
            "domain":      domain,
            "difficulty":  question.get("difficulty"),
            "type":        question.get("type"),
            "models":      {},
        }

        for model_key in enabled_models:
            prompt   = _build_prompt(question)
            api_resp = model_manager.query(model_key, prompt)

            if api_resp["success"]:
                response_text = api_resp["response"]
                score_result  = score_response(response_text, question)
                if verbose:
                    pct = score_result["percentage"]
                    print(f"    {model_key:8s} → {pct:5.1f}%  {score_result['detail']}")
            else:
                response_text = ""
                score_result  = {
                    "score": 0.0, "max_score": 1.0, "percentage": 0.0,
                    "detail": f"API error: {api_resp['error']}",
                    "question_id": q_id, "domain": domain,
                    "difficulty": question.get("difficulty"), "type": question.get("type"),
                }
                if verbose:
                    print(f"    {model_key:8s} → ERROR: {api_resp['error']}")

            q_result["models"][model_key] = {
                "response":     response_text,
                "score_result": score_result,
                "api_success":  api_resp["success"],
            }

        raw_results.append(q_result)

    aggregated = _aggregate(raw_results, enabled_models)

    elapsed = (datetime.now() - start_time).total_seconds()

    results = {
        "metadata": {
            "timestamp":       start_time.isoformat(),
            "elapsed_seconds": round(elapsed, 1),
            "total_questions": total,
            "models_evaluated": enabled_models,
        },
        "raw_results":  raw_results,
        "aggregated":   aggregated,
    }

    if verbose:
        _print_summary(aggregated, enabled_models)

    return results



def _aggregate(raw_results: list[dict], model_keys: list[str]) -> dict:
    
    agg = {mk: {"overall": _empty_stats(), "by_domain": {}, "by_difficulty": {}}
           for mk in model_keys}

    for q_result in raw_results:
        domain     = q_result["domain"]
        difficulty = q_result.get("difficulty", "unknown")

        for mk in model_keys:
            model_data   = q_result["models"].get(mk, {})
            score_result = model_data.get("score_result", {})
            pct          = score_result.get("percentage", 0.0)

            
            _accumulate(agg[mk]["overall"], pct)

            
            if domain not in agg[mk]["by_domain"]:
                agg[mk]["by_domain"][domain] = _empty_stats()
            _accumulate(agg[mk]["by_domain"][domain], pct)

            if difficulty not in agg[mk]["by_difficulty"]:
                agg[mk]["by_difficulty"][difficulty] = _empty_stats()
            _accumulate(agg[mk]["by_difficulty"][difficulty], pct)

    for mk in model_keys:
        _finalise(agg[mk]["overall"])
        for d in agg[mk]["by_domain"].values():
            _finalise(d)
        for d in agg[mk]["by_difficulty"].values():
            _finalise(d)

    return agg


def _empty_stats() -> dict:
    return {"total": 0, "sum": 0.0, "mean": 0.0, "correct": 0}


def _accumulate(stats: dict, pct: float):
    stats["total"] += 1
    stats["sum"]   += pct
    if pct >= 60.0:
        stats["correct"] += 1


def _finalise(stats: dict):
    if stats["total"] > 0:
        stats["mean"] = round(stats["sum"] / stats["total"], 1)
    del stats["sum"]



def _print_summary(aggregated: dict, model_keys: list[str]):
    print(f"\n{'='*60}")
    print("  RESULTS SUMMARY")
    print(f"{'='*60}")

    domains = list(DOMAIN_DISPLAY_NAMES.keys())
    col_w   = 14

    header = f"  {'Domain':<20}" + "".join(f"{mk:>{col_w}}" for mk in model_keys)
    print(header)
    print("  " + "-" * (20 + col_w * len(model_keys)))

    for domain in domains:
        row = f"  {DOMAIN_DISPLAY_NAMES[domain]:<20}"
        for mk in model_keys:
            domain_stats = aggregated[mk]["by_domain"].get(domain)
            val = f"{domain_stats['mean']:.1f}%" if domain_stats else "  N/A"
            row += f"{val:>{col_w}}"
        print(row)

    print("  " + "-" * (20 + col_w * len(model_keys)))
    row = f"  {'OVERALL':<20}"
    for mk in model_keys:
        val = f"{aggregated[mk]['overall']['mean']:.1f}%"
        row += f"{val:>{col_w}}"
    print(row)
    print(f"{'='*60}\n")
