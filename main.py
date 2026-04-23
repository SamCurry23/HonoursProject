
 
import sys
import os
 
 
def _print_banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║          AI MODEL EVALUATION TOOL  v1.0                 ║
║   Systematically compare AI models across domains       ║
╚══════════════════════════════════════════════════════════╝
""")
 
 
def _check_env():
    from config import MODELS
    enabled = [k for k, v in MODELS.items() if v["enabled"]]
    if not enabled:
        print("  ⚠  No API keys found in .env\n")
        print("  Copy .env.example → .env and add at least one key.")
        print("  Available models: OpenAI (OPENAI_API_KEY), "
              "Gemini (GEMINI_API_KEY), Anthropic (ANTHROPIC_API_KEY)\n")
        sys.exit(1)
    return enabled
 
 
def _choose_domains() -> list[str]:
    from config import DOMAINS, DOMAIN_DISPLAY_NAMES
    print("\n  Available domains:")
    for i, d in enumerate(DOMAINS, 1):
        print(f"    {i}. {DOMAIN_DISPLAY_NAMES[d]}")
    print("    6. All domains")
    choice = input("\n  Select domains (e.g. 1,3 or 6 for all): ").strip()
    if "6" in choice or choice == "":
        return DOMAINS
    selected = []
    for c in choice.split(","):
        c = c.strip()
        if c.isdigit() and 1 <= int(c) <= len(DOMAINS):
            selected.append(DOMAINS[int(c) - 1])
    return selected if selected else DOMAINS
 
 
def _choose_run_mode() -> dict:
    print("\n  Run mode:")
    print("    1. Quick test   – 5 questions per domain")
    print("    2. Standard     – 15 questions per domain")
    print("    3. Full         – all questions (~200 total)")
    print("    4. Custom       – you choose how many per domain")
    choice = input("\n  Choice [1-4, default 2]: ").strip() or "2"
 
    if choice == "1":
        return {"max_per_domain": 5}
    elif choice == "2":
        return {"max_per_domain": 15}
    elif choice == "3":
        return {"max_per_domain": None}
    else:
        n = input("  Questions per domain: ").strip()
        n = int(n) if n.isdigit() else 10
        return {"max_per_domain": n}
 
 
def _show_dataset_summary():
    from evaluation.question_loader import get_summary
    from config import DOMAIN_DISPLAY_NAMES
    print("\n  Dataset summary:")
    summary = get_summary()
    for domain, info in summary.items():
        name = DOMAIN_DISPLAY_NAMES.get(domain, domain)
        easy   = info["by_difficulty"]["easy"]
        medium = info["by_difficulty"]["medium"]
        hard   = info["by_difficulty"]["hard"]
        print(f"    {name:<22} {info['total']:>3} questions  "
              f"(easy:{easy}  medium:{medium}  hard:{hard})")
    print()
 
 
def run_full_evaluation(domains, run_config):
    from api.model_manager import ModelManager
    from evaluation.question_loader import get_questions
    from evaluation.evaluator import run_evaluation
    from evaluation.observer import analyse
    from evaluation.report_notes import generate as generate_notes
    from results.results_manager import save_results, export_summary_csv
    from visualisation.charts import generate_all_charts
 
    print("\n  Loading model clients...")
    manager = ModelManager()
 
    print("\n  Loading questions...")
    questions = get_questions(
        domains=domains,
        max_per_domain=run_config.get("max_per_domain"),
        shuffle=True,
    )
    print(f"  {len(questions)} questions loaded across {len(domains)} domain(s).\n")
 
    results = run_evaluation(manager, questions, verbose=True)
 
    print("\n  Analysing results...")
    obs = analyse(results)
 
    print("\n  Saving results...")
    json_path  = save_results(results)
    csv_path   = export_summary_csv(results)
 
    chart_paths = generate_all_charts(results)
 
    notes_path = generate_notes(results)
 
    print("\n  ✓ Evaluation complete.")
    print(f"  JSON results  : {json_path}")
    print(f"  CSV summary   : {csv_path}")
    print(f"  Report notes  : {notes_path}")
    chart_names = ", ".join(os.path.basename(p) for p in chart_paths)
    print(f"  Charts        : {chart_names}")
 
    best = obs.get("best_model_overall", "?").upper()
    print(f"\n  Key finding   : Best model = {best}")
 
    wd = obs.get("worst_domain_overall", {})
    if wd:
        from config import DOMAIN_DISPLAY_NAMES
        label = DOMAIN_DISPLAY_NAMES.get(wd["domain"], wd["domain"])
        avg   = wd["avg_score"]
        print(f"  Hardest domain: {label} (avg {avg:.1f}%)")
 
    return results, json_path
 
 
def view_past_results():
    from results.results_manager import list_results, load_results
    from visualisation.charts import generate_all_charts
 
    files = list_results()
    if not files:
        print("\n  No saved results found.")
        return
 
    print("\n  Saved results:")
    for i, f in enumerate(files, 1):
        print(f"    {i}. {os.path.basename(f)}")
 
    choice = input("\n  Load which result? (number): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(files)):
        print("  Invalid choice.")
        return
 
    path    = files[int(choice) - 1]
    results = load_results(path)
 
    print("\n  Re-generating charts from saved results...")
    generate_all_charts(results)
    print("  Done.")
 
 
def export_for_website():
    from results.results_manager import list_results, load_results, export_summary_csv
 
    files = list_results()
    if not files:
        print("\n  No saved results found.")
        return
 
    path    = files[-1]
    results = load_results(path)
    csv     = export_summary_csv(results)
    print(f"\n  Exported to: {csv}")
    print("  Place this CSV in the website/data/ folder and open website/index.html.")
 
 
def main():
    _print_banner()
    enabled = _check_env()
    print(f"  Enabled models: {', '.join(enabled)}\n")
 
    while True:
        print("  Main Menu")
        print("  ─────────")
        print("  1. Run evaluation")
        print("  2. View dataset summary")
        print("  3. View / re-chart past results")
        print("  4. Export CSV for website")
        print("  5. Exit")
 
        choice = input("\n  > ").strip()
 
        if choice == "1":
            domains    = _choose_domains()
            run_config = _choose_run_mode()
            run_full_evaluation(domains, run_config)
 
        elif choice == "2":
            _show_dataset_summary()
 
        elif choice == "3":
            view_past_results()
 
        elif choice == "4":
            export_for_website()
 
        elif choice == "5":
            print("\n  Goodbye.\n")
            break
 
        else:
            print("  Invalid choice, try again.\n")
 
 
if __name__ == "__main__":
    main()