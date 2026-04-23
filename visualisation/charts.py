

import os
import math
import matplotlib
matplotlib.use("Agg")   
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from config import DOMAINS, DOMAIN_DISPLAY_NAMES, RESULTS_DIR, MODELS


MODEL_COLOURS = {
    "gpt":    "#10a37f",   
    "gemini": "#4285F4",   
    "claude": "#c96442",   
}

DEFAULT_COLOURS = ["#5c6bc0", "#26a69a", "#ef5350", "#ab47bc", "#ffa726"]


def _get_colour(model_key: str, idx: int = 0) -> str:
    return MODEL_COLOURS.get(model_key, DEFAULT_COLOURS[idx % len(DEFAULT_COLOURS)])


def _model_display(model_key: str) -> str:
    cfg = MODELS.get(model_key)
    return cfg["name"] if cfg else model_key.upper()



def plot_domain_scores(aggregated: dict, output_dir: str = RESULTS_DIR) -> str:
    model_keys  = list(aggregated.keys())
    domain_keys = [d for d in DOMAINS if any(
        d in aggregated[mk]["by_domain"] for mk in model_keys
    )]
    domain_labels = [DOMAIN_DISPLAY_NAMES[d] for d in domain_keys]

    n_domains = len(domain_keys)
    n_models  = len(model_keys)
    x         = np.arange(n_domains)
    bar_w     = 0.7 / n_models

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#f8f9fa")

    for i, mk in enumerate(model_keys):
        scores = []
        for d in domain_keys:
            stats = aggregated[mk]["by_domain"].get(d)
            scores.append(stats["mean"] if stats else 0.0)

        offset = (i - (n_models - 1) / 2) * bar_w
        bars   = ax.bar(
            x + offset, scores, bar_w,
            label=_model_display(mk),
            color=_get_colour(mk, i),
            alpha=0.88,
            edgecolor="white",
            linewidth=0.5,
        )
        for bar, score in zip(bars, scores):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{score:.0f}%",
                ha="center", va="bottom",
                fontsize=8, color="#333333",
            )

    ax.set_xlabel("Domain", fontsize=12, labelpad=8)
    ax.set_ylabel("Mean Score (%)", fontsize=12, labelpad=8)
    ax.set_title("AI Model Evaluation – Score by Domain", fontsize=14, fontweight="bold", pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels(domain_labels, fontsize=10)
    ax.set_ylim(0, 110)
    ax.axhline(y=100, color="#cccccc", linestyle="--", linewidth=0.8)
    ax.legend(fontsize=10, framealpha=0.8)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    path = os.path.join(output_dir, "chart_domain_scores.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Chart saved: {path}")
    return path



def plot_radar(aggregated: dict, output_dir: str = RESULTS_DIR) -> str:
    """Radar chart showing each model's profile across all domains."""
    model_keys  = list(aggregated.keys())
    domain_keys = [d for d in DOMAINS if any(
        d in aggregated[mk]["by_domain"] for mk in model_keys
    )]
    labels = [DOMAIN_DISPLAY_NAMES[d] for d in domain_keys]
    N      = len(labels)

    angles = [n / N * 2 * math.pi for n in range(N)]
    angles += angles[:1]   

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#f8f9fa")

    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], fontsize=7, color="#888888")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.grid(color="#cccccc", linewidth=0.5, linestyle="--", alpha=0.7)

    for i, mk in enumerate(model_keys):
        scores = []
        for d in domain_keys:
            stats = aggregated[mk]["by_domain"].get(d)
            scores.append(stats["mean"] if stats else 0.0)
        scores += scores[:1]

        colour = _get_colour(mk, i)
        ax.plot(angles, scores, linewidth=2, linestyle="solid", color=colour,
                label=_model_display(mk))
        ax.fill(angles, scores, alpha=0.12, color=colour)

    ax.set_title("Model Performance Profile", fontsize=14, fontweight="bold",
                 pad=20, y=1.08)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)

    plt.tight_layout()
    path = os.path.join(output_dir, "chart_radar.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Chart saved: {path}")
    return path



def plot_overall_scores(aggregated: dict, output_dir: str = RESULTS_DIR) -> str:
    model_keys = list(aggregated.keys())
    names  = [_model_display(mk) for mk in model_keys]
    scores = [aggregated[mk]["overall"]["mean"] for mk in model_keys]
    colours = [_get_colour(mk, i) for i, mk in enumerate(model_keys)]

    fig, ax = plt.subplots(figsize=(8, max(3, len(model_keys) * 1.2)))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#f8f9fa")

    bars = ax.barh(names, scores, color=colours, alpha=0.88,
                   edgecolor="white", linewidth=0.5, height=0.5)

    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.1f}%",
            va="center", fontsize=11, fontweight="bold",
        )

    ax.set_xlim(0, 115)
    ax.set_xlabel("Overall Mean Score (%)", fontsize=12)
    ax.set_title("Overall Model Scores", fontsize=14, fontweight="bold", pad=12)
    ax.axvline(x=100, color="#cccccc", linestyle="--", linewidth=0.8)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    path = os.path.join(output_dir, "chart_overall.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Chart saved: {path}")
    return path



def plot_difficulty_breakdown(aggregated: dict, output_dir: str = RESULTS_DIR) -> str:
    model_keys   = list(aggregated.keys())
    difficulties = ["easy", "medium", "hard"]

    x     = np.arange(len(difficulties))
    bar_w = 0.7 / len(model_keys)

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#f8f9fa")

    for i, mk in enumerate(model_keys):
        scores = []
        for diff in difficulties:
            stats = aggregated[mk]["by_difficulty"].get(diff)
            scores.append(stats["mean"] if stats else 0.0)

        offset = (i - (len(model_keys) - 1) / 2) * bar_w
        bars   = ax.bar(
            x + offset, scores, bar_w,
            label=_model_display(mk),
            color=_get_colour(mk, i),
            alpha=0.88,
            edgecolor="white",
        )
        for bar, score in zip(bars, scores):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{score:.0f}%",
                ha="center", va="bottom", fontsize=8,
            )

    ax.set_xticks(x)
    ax.set_xticklabels([d.capitalize() for d in difficulties], fontsize=11)
    ax.set_xlabel("Difficulty", fontsize=12)
    ax.set_ylabel("Mean Score (%)", fontsize=12)
    ax.set_title("Scores by Difficulty Level", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylim(0, 115)
    ax.legend(fontsize=10, framealpha=0.8)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    path = os.path.join(output_dir, "chart_difficulty.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Chart saved: {path}")
    return path



def generate_all_charts(results: dict, output_dir: str = RESULTS_DIR) -> list[str]:
    aggregated = results.get("aggregated", {})
    if not aggregated:
        print("  [Warning] No aggregated data found — skipping charts.")
        return []

    os.makedirs(output_dir, exist_ok=True)
    print("\n  Generating charts...")

    paths = [
        plot_overall_scores(aggregated, output_dir),
        plot_domain_scores(aggregated, output_dir),
        plot_radar(aggregated, output_dir),
        plot_difficulty_breakdown(aggregated, output_dir),
    ]
    return paths
