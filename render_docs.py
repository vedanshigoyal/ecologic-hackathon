"""Render README.md and docs/VIDEO_SCRIPT.md from templates filled with results/impact.json.

Numbers are never typed into those documents by hand: templates in docs/templates/ hold
{{placeholders}} and this module substitutes values formatted from impact.json, so the
README, video script and deck (which uses fmt_values too) always agree.
"""

import json
import re

import config

TEMPLATES = {
    config.ROOT / "docs" / "templates" / "README.template.md": config.ROOT / "README.md",
    config.ROOT / "docs" / "templates" / "VIDEO_SCRIPT.template.md": config.ROOT / "docs" / "VIDEO_SCRIPT.md",
}


def load_impact() -> dict:
    return json.loads((config.RESULTS_DIR / "impact.json").read_text(encoding="utf-8"))


def fmt_values(impact: dict) -> dict:
    """Flat dict of display strings derived from impact.json."""
    s, b, sc = impact["savings_per_ha_per_season"], impact["baseline"], impact["scheduler"]
    a, p, setup = impact["assumptions"], impact["paired"], impact["setup"]
    yd = impact["yield_difference"]
    v = {
        "n_seasons": str(setup["n_seasons"]),
        "first_season": setup["first_season"],
        "last_season": setup["last_season"],
        "weather": setup["weather"],
        "crop": setup["crop"],
        "soil": setup["soil"],
        "baseline_id": b["id"],
        "scheduler_id": sc["id"],
        "rule_met": "Yes" if impact["selection"]["rule_met"] else "No",
        "selection_note": impact["selection"]["note"],
        "rule_text": impact["selection"]["rule"],
        "base_mm": f"{b['irrigation_mm']['mean']:.0f}",
        "sched_mm": f"{sc['irrigation_mm']['mean']:.1f}",
        "sched_mm_min": f"{sc['irrigation_mm']['min']:.0f}",
        "sched_mm_max": f"{sc['irrigation_mm']['max']:.0f}",
        "sched_mm_std": f"{sc['irrigation_mm']['std']:.1f}",
        "base_mm_std": f"{b['irrigation_mm']['std']:.1f}",
        "base_yield": f"{b['yield_t_ha']['mean']:.2f}",
        "sched_yield": f"{sc['yield_t_ha']['mean']:.2f}",
        "base_yield_range": f"{b['yield_t_ha']['min']:.2f} to {b['yield_t_ha']['max']:.2f}",
        "sched_yield_range": f"{sc['yield_t_ha']['min']:.2f} to {sc['yield_t_ha']['max']:.2f}",
        "yield_diff_t": f"{yd['t_ha']['mean']:+.3f}",
        "yield_diff_pct": f"{yd['pct_of_baseline']:+.2f}%",
        "base_wp": f"{b['water_productivity_kg_m3']:.2f}",
        "sched_wp": f"{sc['water_productivity_kg_m3']:.1f}",
        "zero_irr_seasons": str(sc["seasons_with_zero_irrigation"]),
        "rainfed_yield": f"{impact['rainfed_reference']['yield_t_ha']:.2f}",
        "rainfed_pct": f"{impact['rainfed_reference']['yield_pct_of_baseline']:.1f}%",
        "saved_mm": f"{s['water_mm']['mean']:.0f}",
        "saved_pct": f"{s['water_pct_of_baseline']:.0f}%",
        "saved_l": f"{s['water_litres']['mean']:,.0f}",
        "saved_ml": f"{s['water_litres']['mean'] / 1e6:.2f} million",
        "saved_l_min": f"{s['water_litres']['min']:,.0f}",
        "saved_l_max": f"{s['water_litres']['max']:,.0f}",
        "saved_l_std": f"{s['water_litres']['std']:,.0f}",
        "saved_m3": f"{s['water_m3']['mean']:,.0f}",
        "saved_kwh": f"{s['energy_kwh']['mean']:,.0f}",
        "saved_kwh_range": f"{s['energy_kwh']['min']:,.0f} to {s['energy_kwh']['max']:,.0f}",
        "saved_inr": f"₹{s['cost_inr']['mean']:,.0f}",
        "saved_inr_range": f"₹{s['cost_inr']['min']:,.0f} to ₹{s['cost_inr']['max']:,.0f}",
        "saved_co2": f"{s['co2_kg']['mean']:,.0f}",
        "saved_co2_range": f"{s['co2_kg']['min']:,.0f} to {s['co2_kg']['max']:,.0f}",
        "paired_less_water": f"{p['seasons_scheduler_used_less_water']} of {p['n_seasons']}",
        "paired_within_2pct": f"{p['seasons_yield_within_2pct']} of {p['n_seasons']}",
        "head_m": f"{a['pump_head_m']:.0f}",
        "pump_eff": f"{a['pump_efficiency']:.2f}",
        "kwh_per_m3": f"{a['kwh_per_m3']:.3f}",
        "tariff": f"₹{a['tariff_inr_per_kwh']:.2f}",
        "grid_ef": f"{a['grid_ef_kg_co2_per_kwh']:.2f}",
        "base_interval": str(a["baseline_interval_days"]),
        "base_depth": f"{a['baseline_depth_mm']:.0f}",
    }
    v["sensitivity_table"] = sensitivity_markdown(impact)
    v["strategy_table"] = strategy_markdown(impact)
    return v


def sensitivity_rows(impact: dict) -> list:
    return [(f"{r['head_m']:.0f} m", f"{r['kwh_per_m3']:.3f}", f"{r['kwh_saved']:,.0f}",
             f"₹{r['inr_saved']:,.0f}", f"{r['kg_co2_saved']:,.0f}")
            for r in impact["sensitivity_head"]]


def sensitivity_markdown(impact: dict) -> str:
    lines = ["| Pump head | kWh per m³ | kWh saved/ha/season | ₹ saved/ha/season | kg CO₂ saved/ha/season |",
             "|---|---|---|---|---|"]
    lines += ["| " + " | ".join(r) + " |" for r in sensitivity_rows(impact)]
    return "\n".join(lines)


def strategy_markdown(impact: dict) -> str:
    sel, base = impact["scheduler"]["id"], impact["baseline"]["id"]
    lines = ["| Strategy | Mean irrigation (mm/season) | Mean dry yield (t/ha) |", "|---|---|---|"]
    for r in impact["strategies"]:
        tag = " (selected)" if r["id"] == sel else " (baseline)" if r["id"] == base else ""
        lines.append(f"| `{r['id']}`{tag} | {r['mean_irrigation_mm']:.1f} | {r['mean_yield_t_ha']:.2f} |")
    return "\n".join(lines)


def render(template: str, values: dict) -> str:
    def sub(match):
        key = match.group(1)
        if key not in values:
            raise KeyError(f"Unknown placeholder {{{{{key}}}}}")
        return values[key]
    return re.sub(r"\{\{(\w+)\}\}", sub, template)


def render_all(impact: dict | None = None) -> None:
    values = fmt_values(impact or load_impact())
    for src, dst in TEMPLATES.items():
        if not src.exists():
            continue
        dst.write_text(render(src.read_text(encoding="utf-8"), values), encoding="utf-8")
        print(f"Rendered {dst.relative_to(config.ROOT)} from impact.json")


if __name__ == "__main__":
    render_all()
