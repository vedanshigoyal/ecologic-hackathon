"""Apply the pre-registered selection rule, compute impact metrics, draw charts.

Reads results/results.csv (from run_experiment.py) and writes:
  results/selection.json, results/impact.json, results/*.png
All numbers are SIMULATED (AquaCrop-OSPy model), not field measurements.
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import config

# Chart styling (validated categorical pair: baseline orange, selected blue; others neutral)
C_BASE, C_SEL, C_OTHER = "#eb6834", "#2a78d6", "#9a9890"
INK, INK_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
DPI = 200


def stats(series: pd.Series) -> dict:
    return {"mean": float(series.mean()), "min": float(series.min()),
            "max": float(series.max()), "std": float(series.std(ddof=1))}


def select_strategy(summary: pd.DataFrame) -> dict:
    base_yield = summary.loc[config.BASELINE_ID, "mean_yield_t_ha"]
    threshold = config.YIELD_RETENTION_MIN * base_yield
    smt = summary[summary.index.str.startswith("smt_")]
    candidates = [
        {"strategy": sid,
         "mean_irrigation_mm": float(row.mean_irrigation_mm),
         "mean_yield_t_ha": float(row.mean_yield_t_ha),
         "yield_pct_of_baseline": float(100 * row.mean_yield_t_ha / base_yield),
         "qualifies": bool(row.mean_yield_t_ha >= threshold)}
        for sid, row in smt.iterrows()
    ]
    qualifying = [c for c in candidates if c["qualifies"]]
    if qualifying:
        chosen = min(qualifying, key=lambda c: c["mean_irrigation_mm"])["strategy"]
        note = "Selection rule met."
    else:
        # Fallback: highest yield, ties broken by lower water. Explicitly NOT a rule pass.
        chosen = min(candidates, key=lambda c: (-c["mean_yield_t_ha"], c["mean_irrigation_mm"]))["strategy"]
        note = ("No SMT strategy met the selection rule. Reporting the best yield-preserving "
                "trade-off; this does NOT meet the rule.")
    return {"rule": config.SELECTION_RULE_TEXT, "rule_met": bool(qualifying),
            "selected": chosen, "note": note, "baseline": config.BASELINE_ID,
            "baseline_mean_yield_t_ha": float(base_yield),
            "yield_threshold_t_ha": float(threshold), "candidates": candidates}


def energy_block(water_saved_m3: float, head_m: float) -> dict:
    kwh_per_m3 = config.pump_kwh_per_m3(head_m)
    kwh = water_saved_m3 * kwh_per_m3
    return {"head_m": head_m, "kwh_per_m3": kwh_per_m3, "kwh_saved": kwh,
            "inr_saved": kwh * config.TARIFF_INR_PER_KWH,
            "kg_co2_saved": kwh * config.GRID_EF_KG_CO2_PER_KWH}


def compute_impact(results: pd.DataFrame, summary: pd.DataFrame, selection: dict) -> dict:
    sel, base = selection["selected"], config.BASELINE_ID
    wide = results.pivot(index="season", columns="strategy")
    b_mm, s_mm = wide["irrigation_mm"][base], wide["irrigation_mm"][sel]
    b_y, s_y = wide["dry_yield_t_ha"][base], wide["dry_yield_t_ha"][sel]

    saved_mm = b_mm - s_mm
    saved_l = saved_mm * config.LITRES_PER_MM_PER_HA
    saved_m3 = saved_mm * config.M3_PER_MM_PER_HA
    kwh_m3 = config.pump_kwh_per_m3()
    saved_kwh = saved_m3 * kwh_m3

    def wp(strategy):  # kg of grain per m3 of irrigation water, on season means
        mm = summary.loc[strategy, "mean_irrigation_mm"]
        y = summary.loc[strategy, "mean_yield_t_ha"]
        return float(y * 1000 / (mm * config.M3_PER_MM_PER_HA)) if mm > 0 else None

    n = len(saved_mm)
    rainfed_y = float(summary.loc["rainfed", "mean_yield_t_ha"])
    return {
        "label": "SIMULATED with AquaCrop-OSPy; not field-measured",
        "setup": {"crop": config.CROP_NAME, "soil": config.SOIL_TYPE,
                  "weather": config.WEATHER_LABEL, "sim_start": config.SIM_START,
                  "sim_end": config.SIM_END, "n_seasons": n,
                  "first_season": str(saved_mm.index.min()), "last_season": str(saved_mm.index.max())},
        "selection": {k: selection[k] for k in ("selected", "rule_met", "note", "rule")},
        "baseline": {"id": base, "irrigation_mm": stats(b_mm), "yield_t_ha": stats(b_y),
                     "water_productivity_kg_m3": wp(base)},
        "scheduler": {"id": sel, "irrigation_mm": stats(s_mm), "yield_t_ha": stats(s_y),
                      "water_productivity_kg_m3": wp(sel),
                      "seasons_with_zero_irrigation": int((s_mm == 0).sum())},
        "rainfed_reference": {"yield_t_ha": rainfed_y,
                              "yield_pct_of_baseline": 100 * rainfed_y / float(b_y.mean())},
        "savings_per_ha_per_season": {
            "water_mm": stats(saved_mm),
            "water_litres": stats(saved_l),
            "water_m3": stats(saved_m3),
            "water_pct_of_baseline": float(100 * saved_mm.mean() / b_mm.mean()),
            "energy_kwh": stats(saved_kwh),
            "cost_inr": stats(saved_kwh * config.TARIFF_INR_PER_KWH),
            "co2_kg": stats(saved_kwh * config.GRID_EF_KG_CO2_PER_KWH),
        },
        "yield_difference": {"t_ha": stats(s_y - b_y),
                             "pct_of_baseline": float(100 * (s_y.mean() - b_y.mean()) / b_y.mean())},
        "paired": {"n_seasons": n,
                   "seasons_scheduler_used_less_water": int((s_mm < b_mm).sum()),
                   "seasons_yield_within_2pct": int(((s_y - b_y).abs() <= config.PAIRED_YIELD_TOLERANCE * b_y).sum())},
        "assumptions": {"pump_head_m": config.PUMP_HEAD_M, "pump_efficiency": config.PUMP_EFFICIENCY,
                        "kwh_per_m3": kwh_m3, "tariff_inr_per_kwh": config.TARIFF_INR_PER_KWH,
                        "grid_ef_kg_co2_per_kwh": config.GRID_EF_KG_CO2_PER_KWH,
                        "baseline_interval_days": config.BASELINE_INTERVAL_DAYS,
                        "baseline_depth_mm": config.BASELINE_DEPTH_MM},
        "sensitivity_head": [energy_block(float(saved_m3.mean()), h) for h in config.SENSITIVITY_HEADS_M],
        "per_season": [{"season": s, "baseline_mm": float(b_mm[s]), "scheduler_mm": float(s_mm[s]),
                        "water_saved_litres": float(saved_l[s]), "baseline_yield_t_ha": float(b_y[s]),
                        "scheduler_yield_t_ha": float(s_y[s])} for s in saved_mm.index],
        "strategies": [{"id": sid, "mean_irrigation_mm": float(r.mean_irrigation_mm),
                        "mean_yield_t_ha": float(r.mean_yield_t_ha)} for sid, r in summary.iterrows()],
    }


def _style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def chart_irrigation_vs_yield(summary, selection, path):
    sel, base = selection["selected"], config.BASELINE_ID
    fig, ax = plt.subplots(figsize=(8, 4.8))
    _style(ax)
    for sid, r in summary.iterrows():
        color = C_SEL if sid == sel else C_BASE if sid == base else C_OTHER
        size = 90 if sid in (sel, base) else 50
        ax.scatter(r.mean_irrigation_mm, r.mean_yield_t_ha, s=size, color=color,
                   edgecolor="white", linewidth=1.5, zorder=3)
        if sid == sel:  # selected label sits below the cluster of SMT points
            ax.annotate(f"{sid} (selected)", (r.mean_irrigation_mm, r.mean_yield_t_ha), xytext=(4, -16),
                        textcoords="offset points", fontsize=9, color=INK, fontweight="bold")
        elif sid == base:
            ax.annotate(f"{sid} (baseline)", (r.mean_irrigation_mm, r.mean_yield_t_ha), xytext=(0, -16),
                        textcoords="offset points", fontsize=9, color=INK, fontweight="bold", ha="right")
        else:
            ax.annotate(sid, (r.mean_irrigation_mm, r.mean_yield_t_ha), xytext=(2, 7),
                        textcoords="offset points", fontsize=8, color=INK_2, rotation=45)
    thr = selection["yield_threshold_t_ha"]
    ax.axhline(thr, color=INK_2, linestyle="--", linewidth=1)
    ax.text(summary.mean_irrigation_mm.max(), thr, "98% of baseline yield", ha="right",
            va="bottom", fontsize=8.5, color=INK_2)
    lo = min(summary.mean_yield_t_ha.min(), thr)
    hi = summary.mean_yield_t_ha.max()
    ax.set_ylim(lo - 0.08, hi + 0.12)
    ax.set_xlabel("Mean seasonal irrigation (mm)", color=INK)
    ax.set_ylabel("Mean dry yield (t/ha)", color=INK)
    ax.set_title("Irrigation vs yield by strategy (simulated, wheat, Tunis sample climate)",
                 color=INK, fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def chart_water_saved(impact, path):
    rows = impact["per_season"]
    seasons = [r["season"] for r in rows]
    vals = [r["water_saved_litres"] / 1e6 for r in rows]
    mean = impact["savings_per_ha_per_season"]["water_litres"]["mean"] / 1e6
    fig, ax = plt.subplots(figsize=(9, 4.4))
    _style(ax)
    ax.bar(seasons, vals, color=C_SEL, width=0.75, edgecolor="white", linewidth=1)
    ax.axhline(mean, color=INK_2, linestyle="--", linewidth=1)
    ax.text(-0.5, max(vals) * 1.06, f"dashed line: mean {mean:.2f} million L/ha", ha="left",
            va="bottom", fontsize=8.5, color=INK_2)
    ax.set_ylim(0, max(vals) * 1.15)
    ax.set_xlabel("Wheat season", color=INK)
    ax.set_ylabel("Water saved (million litres per ha)", color=INK)
    ax.set_title(f"Water saved per season: {impact['scheduler']['id']} vs {impact['baseline']['id']} (simulated)",
                 color=INK, fontsize=11, loc="left")
    plt.setp(ax.get_xticklabels(), rotation=60, ha="right", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def chart_impact_summary(impact, path):
    s = impact["savings_per_ha_per_season"]
    tiles = [
        (f"{s['water_litres']['mean'] / 1e6:.2f} M", "litres of water"),
        (f"{s['energy_kwh']['mean']:,.0f}", "kWh of pump energy"),
        (f"₹{s['cost_inr']['mean']:,.0f}", "electricity cost"),
        (f"{s['co2_kg']['mean']:,.0f}", "kg CO₂"),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(10, 2.3))
    for ax, (value, label) in zip(axes, tiles):
        ax.set_axis_off()
        ax.add_patch(plt.Rectangle((0.03, 0.05), 0.94, 0.8, transform=ax.transAxes,
                                   facecolor="#f3f2ef", edgecolor="none"))
        ax.text(0.5, 0.55, value, ha="center", va="center", fontsize=22, color=INK,
                fontweight="bold", transform=ax.transAxes)
        ax.text(0.5, 0.25, label, ha="center", va="center", fontsize=10, color=INK_2,
                transform=ax.transAxes)
    fig.suptitle("Saved per hectare per season, mean of "
                 f"{impact['setup']['n_seasons']} seasons (simulated; energy, cost, CO₂ use stated assumptions)",
                 fontsize=10.5, color=INK, x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def main() -> None:
    results = pd.read_csv(config.RESULTS_DIR / "results.csv", dtype={"season": str})
    summary = (results.groupby("strategy", sort=False)
               .agg(mean_yield_t_ha=("dry_yield_t_ha", "mean"),
                    mean_irrigation_mm=("irrigation_mm", "mean")))

    selection = select_strategy(summary)
    (config.RESULTS_DIR / "selection.json").write_text(json.dumps(selection, indent=2), encoding="utf-8")

    impact = compute_impact(results, summary, selection)
    (config.RESULTS_DIR / "impact.json").write_text(json.dumps(impact, indent=2), encoding="utf-8")

    chart_irrigation_vs_yield(summary, selection, config.RESULTS_DIR / "irrigation_vs_yield.png")
    chart_water_saved(impact, config.RESULTS_DIR / "water_saved_per_season.png")
    chart_impact_summary(impact, config.RESULTS_DIR / "impact_summary.png")

    s, b, sc = impact["savings_per_ha_per_season"], impact["baseline"], impact["scheduler"]
    print("SIMULATED results - AquaCrop-OSPy, not field-measured")
    print(f"Selection rule met: {selection['rule_met']}  ->  selected {selection['selected']}")
    print(f"  {selection['note']}")
    print(f"Baseline  {b['id']:>9}: {b['irrigation_mm']['mean']:7.1f} mm, {b['yield_t_ha']['mean']:.2f} t/ha")
    print(f"Scheduler {sc['id']:>9}: {sc['irrigation_mm']['mean']:7.1f} mm, {sc['yield_t_ha']['mean']:.2f} t/ha")
    print(f"Saved per ha per season: {s['water_litres']['mean']:,.0f} L, {s['energy_kwh']['mean']:,.1f} kWh, "
          f"Rs {s['cost_inr']['mean']:,.0f}, {s['co2_kg']['mean']:,.1f} kg CO2")
    print(f"Rainfed reference yield: {impact['rainfed_reference']['yield_pct_of_baseline']:.1f}% of baseline")

    from render_docs import render_all
    render_all(impact)


if __name__ == "__main__":
    main()
