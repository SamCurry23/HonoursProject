

import re
import string



def _normalise(text: str) -> str:
    
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_numbers(text: str) -> list[str]:
    return re.findall(r"-?\d+\.?\d*", text)



def score_exact(response: str, question: dict) -> dict:
    
    if not response:
        return {"score": 0.0, "max_score": 1.0, "percentage": 0.0, "detail": "No response"}

    norm_response = _normalise(response)
    keywords = [_normalise(k) for k in question.get("keywords", [])]
    correct = _normalise(question.get("answer", ""))

    if correct and correct in norm_response:
        return {"score": 1.0, "max_score": 1.0, "percentage": 100.0, "detail": "Exact match"}

    matched = sum(1 for kw in keywords if kw in norm_response)
    if matched == len(keywords) and keywords:
        return {"score": 1.0, "max_score": 1.0, "percentage": 100.0, "detail": "All keywords matched"}

    if matched > 0:
        pct = matched / len(keywords) * 100
        return {
            "score": round(matched / len(keywords), 2),
            "max_score": 1.0,
            "percentage": round(pct, 1),
            "detail": f"Partial match ({matched}/{len(keywords)} keywords)",
        }

    resp_nums = set(_extract_numbers(norm_response))
    ans_nums  = set(_extract_numbers(correct))
    if ans_nums and ans_nums.issubset(resp_nums):
        return {"score": 1.0, "max_score": 1.0, "percentage": 100.0, "detail": "Numeric match"}

    return {"score": 0.0, "max_score": 1.0, "percentage": 0.0, "detail": "No match"}


def score_keyword(response: str, question: dict) -> dict:
    
    if not response:
        return {"score": 0.0, "max_score": 1.0, "percentage": 0.0, "detail": "No response"}

    norm_response = _normalise(response)
    keywords = [_normalise(k) for k in question.get("keywords", [])]

    if not keywords:
        return {"score": 0.5, "max_score": 1.0, "percentage": 50.0, "detail": "No keywords defined"}

    matched = [kw for kw in keywords if kw in norm_response]
    score   = len(matched) / len(keywords)
    pct     = round(score * 100, 1)

    detail = (
        f"Matched {len(matched)}/{len(keywords)} keywords"
        if matched
        else "No keywords found"
    )
    return {"score": round(score, 2), "max_score": 1.0, "percentage": pct, "detail": detail}


def score_rubric(response: str, question: dict) -> dict:
    
    if not response:
        return {"score": 0.0, "max_score": 1.0, "percentage": 0.0, "detail": "No response"}

    norm_response = _normalise(response)
    rubric   = question.get("rubric", {})
    criteria = rubric.get("criteria", [])
    keywords = [_normalise(k) for k in question.get("keywords", [])]

    if keywords:
        keyword_score = sum(1 for kw in keywords if kw in norm_response) / len(keywords)
    else:
        keyword_score = 0.5

    word_count = len(response.split())
    length_bonus = min(word_count / 100, 0.2)  

    raw = min(keyword_score + length_bonus, 1.0)

    if raw >= 0.8:
        tier = "Excellent"
    elif raw >= 0.6:
        tier = "Good"
    elif raw >= 0.4:
        tier = "Adequate"
    elif raw >= 0.2:
        tier = "Weak"
    else:
        tier = "Poor"

    criteria_count = len(criteria)
    detail = f"{tier} – {criteria_count} criteria assessed, {word_count} words"

    return {
        "score": round(raw, 2),
        "max_score": 1.0,
        "percentage": round(raw * 100, 1),
        "detail": detail,
    }



def score_response(response: str, question: dict) -> dict:
    
    q_type = question.get("type", "keyword")

    if q_type == "exact":
        result = score_exact(response, question)
    elif q_type == "rubric":
        result = score_rubric(response, question)
    else:
        result = score_keyword(response, question)

    result.update({
        "question_id": question.get("id", ""),
        "domain":      question.get("domain", ""),
        "difficulty":  question.get("difficulty", ""),
        "type":        q_type,
    })
    return result
