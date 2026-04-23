

from config import DOMAIN_DISPLAY_NAMES


def analyse(results: dict) -> dict:
    
    raw      = results.get("raw_results", [])
    agg      = results.get("aggregated", {})
    models   = results["metadata"]["models_evaluated"]

    obs = {
        "all_zero_questions":    _find_all_zero(raw, models),
        "likely_false_negatives": _find_false_negatives(raw, models),
        "model_domain_strengths": _find_strengths(agg, models),
        "biggest_gaps":          _find_gaps(agg, models),
        "refusals":              _find_refusals(raw, models),
        "score_spread":          _score_spread(agg, models),
        "best_model_overall":    _best_overall(agg, models),
        "worst_domain_overall":  _worst_domain(agg, models),
    }

    results["observations"] = obs
    return obs



def _find_all_zero(raw: list, models: list) -> list:
    flagged = []
    for q in raw:
        scores = [q["models"].get(m, {}).get("score_result", {}).get("percentage", 0)
                  for m in models]
        if all(s == 0 for s in scores) and any(
            q["models"].get(m, {}).get("api_success", False) for m in models
        ):
            flagged.append({
                "id":       q["question_id"],
                "domain":   q["domain"],
                "question": q["question"][:80] + "..." if len(q["question"]) > 80 else q["question"],
            })
    return flagged


def _find_false_negatives(raw: list, models: list) -> list:
    
    flagged = []
    for q in raw:
        answer = (q.get("question", "") and
                  q["models"] and
                  next(iter(q["models"].values()), {}).get("score_result", {}).get("question_id"))
        for m in models:
            mdata  = q["models"].get(m, {})
            score  = mdata.get("score_result", {}).get("percentage", -1)
            resp   = mdata.get("response", "").lower()
            if score == 0 and resp:
                detail = mdata.get("score_result", {}).get("detail", "")
                if "partial" in detail.lower() or "1/" in detail:
                    flagged.append({
                        "id":       q["question_id"],
                        "model":    m,
                        "domain":   q["domain"],
                        "response_preview": resp[:100],
                        "detail":   detail,
                    })
    return flagged[:10]  


def _find_strengths(agg: dict, models: list) -> dict:
    strengths = {}
    for m in models:
        domain_scores = agg[m].get("by_domain", {})
        if not domain_scores:
            continue
        ranked = sorted(domain_scores.items(), key=lambda x: x[1]["mean"], reverse=True)
        strengths[m] = {
            "strongest":       ranked[0][0]  if ranked else None,
            "strongest_score": ranked[0][1]["mean"] if ranked else 0,
            "weakest":         ranked[-1][0] if ranked else None,
            "weakest_score":   ranked[-1][1]["mean"] if ranked else 0,
        }
    return strengths


def _find_gaps(agg: dict, models: list) -> list:
    all_domains = set()
    for m in models:
        all_domains.update(agg[m].get("by_domain", {}).keys())

    gaps = []
    for domain in all_domains:
        scores = {}
        for m in models:
            s = agg[m]["by_domain"].get(domain, {}).get("mean")
            if s is not None:
                scores[m] = s
        if len(scores) >= 2:
            best  = max(scores, key=scores.get)
            worst = min(scores, key=scores.get)
            gap   = scores[best] - scores[worst]
            gaps.append({
                "domain":      domain,
                "gap":         round(gap, 1),
                "best_model":  best,
                "best_score":  scores[best],
                "worst_model": worst,
                "worst_score": scores[worst],
            })

    return sorted(gaps, key=lambda x: x["gap"], reverse=True)


def _find_refusals(raw: list, models: list) -> dict:
    refusal_phrases = [
        "i cannot", "i'm not able", "i am not able", "i won't",
        "i will not", "cannot provide", "inappropriate", "harmful",
        "i don't think i should", "as an ai", "i must decline",
    ]
    refusals = {m: 0 for m in models}
    for q in raw:
        if q.get("domain") not in ("ethics", "creative"):
            continue
        for m in models:
            resp = q["models"].get(m, {}).get("response", "").lower()
            if any(p in resp for p in refusal_phrases):
                refusals[m] += 1
    return {m: v for m, v in refusals.items() if v > 0}


def _score_spread(agg: dict, models: list) -> dict:
    spreads = {}
    for m in models:
        scores = [v["mean"] for v in agg[m].get("by_domain", {}).values()]
        if scores:
            spreads[m] = round(max(scores) - min(scores), 1)
    return spreads


def _best_overall(agg: dict, models: list) -> str:
    scores = {m: agg[m]["overall"]["mean"] for m in models}
    return max(scores, key=scores.get) if scores else ""


def _worst_domain(agg: dict, models: list) -> dict:
    all_domains = set()
    for m in models:
        all_domains.update(agg[m].get("by_domain", {}).keys())

    domain_avgs = {}
    for d in all_domains:
        scores = [agg[m]["by_domain"][d]["mean"]
                  for m in models if d in agg[m].get("by_domain", {})]
        if scores:
            domain_avgs[d] = round(sum(scores) / len(scores), 1)

    if not domain_avgs:
        return {}
    worst = min(domain_avgs, key=domain_avgs.get)
    return {"domain": worst, "avg_score": domain_avgs[worst]}
