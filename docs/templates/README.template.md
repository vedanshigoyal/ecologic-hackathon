<!-- GENERATED FILE: edit docs/templates/README.template.md, then run `python analyze.py` (or `python render_docs.py`). Every number below comes from results/impact.json. -->

# SmartIrrigate

**Soil-moisture-driven irrigation scheduling for water savings: a simulation study on AquaCrop-OSPy.**

Submission by **Team Codexa** (Vedanshi Goyal, Apoorva Singh, Soumyadip Manna, Pranay Maheshwari) for EcoLogic 1.0 Sustainability Hackathon, theme Smart Agriculture.

> **All results in this repository are SIMULATED** with the FAO AquaCrop crop-water model
> (Python port AquaCrop-OSPy). They are not field measurements. The weather is the
> AquaCrop-OSPy bundled sample climate for **Tunis, Tunisia**, not an Indian location.

## Problem

Many farmers irrigate on a fixed calendar: a set depth of water every few days, whatever the
weather or the state of the soil. When rain has already wetted the root zone, that water drains
below the roots or evaporates. The waste is twofold: the water itself, and the electricity used
to pump it.

## Solution

A **soil-moisture-threshold scheduler**: irrigate only when the root zone has dried below a set
fraction of its available water, and then refill it. We compare it against a fixed-interval,
farmer-style baseline across {{n_seasons}} simulated wheat seasons and translate the difference into
litres, kWh, rupees and kg CO₂ per hectare per season.

The same rule can run in the field on a low-cost soil-moisture sensor and a pump relay; see
[docs/DEPLOYMENT_PATH.md](docs/DEPLOYMENT_PATH.md). That hardware is **not built or tested** in this
submission.

## How it works

1. `run_experiment.py` runs 8 strategies through AquaCrop-OSPy over the same {{n_seasons}} wheat seasons
   ({{first_season}} to {{last_season}}), same soil ({{soil}}) and same weather, and saves per-season
   yield and irrigation to `results/results.csv`.
   - `rainfed`: no irrigation (reference)
   - `{{baseline_id}}` (baseline): {{base_depth}} mm every {{base_interval}} days from planting, as a predefined schedule
   - `smt_40` … `smt_90`: irrigate when root-zone water falls below 40 … 90 % of total available water
2. `analyze.py` applies a selection rule that was **fixed before any results were seen**, computes
   savings and writes `results/impact.json`, `results/selection.json` and the charts.
3. `build_deck.py` builds the presentation from the same `impact.json`.

**Selection rule:** {{rule_text}}

**Rule met: {{rule_met}}.** Selected scheduler: `{{scheduler_id}}`.

## Results (simulated, per hectare per season, mean of {{n_seasons}} seasons)

| Metric | Baseline `{{baseline_id}}` | Scheduler `{{scheduler_id}}` |
|---|---|---|
| Irrigation (mm) | {{base_mm}} | {{sched_mm}} (range {{sched_mm_min}} to {{sched_mm_max}}, SD {{sched_mm_std}}) |
| Dry yield (t/ha) | {{base_yield}} (range {{base_yield_range}}) | {{sched_yield}} (range {{sched_yield_range}}) |
| Irrigation water productivity (kg grain per m³ irrigation) | {{base_wp}} | {{sched_wp}} |

| Saving vs baseline | Mean | Range across seasons |
|---|---|---|
| Water | **{{saved_l}} L/ha** ({{saved_mm}} mm, {{saved_pct}} of baseline) | {{saved_l_min}} to {{saved_l_max}} L/ha (SD {{saved_l_std}}) |
| Pump energy | **{{saved_kwh}} kWh/ha** | {{saved_kwh_range}} kWh/ha |
| Electricity cost | **{{saved_inr}}/ha** | {{saved_inr_range}}/ha |
| CO₂ | **{{saved_co2}} kg/ha** | {{saved_co2_range}} kg/ha |
| Yield change | {{yield_diff_t}} t/ha ({{yield_diff_pct}}) | |

Paired season-by-season comparison: the scheduler used less water in **{{paired_less_water}}** seasons and
kept yield within 2 % of the baseline in **{{paired_within_2pct}}** seasons.

Energy, cost and CO₂ use assumed values: pump head {{head_m}} m, pump efficiency {{pump_eff}}
(= {{kwh_per_m3}} kWh/m³), tariff {{tariff}}/kWh, grid factor {{grid_ef}} kg CO₂/kWh. Sensitivity to pump head:

{{sensitivity_table}}

### Read this before quoting the headline number

- **In this sample climate the crop is barely water-limited.** Rainfed wheat already reaches
  {{rainfed_yield}} t/ha, {{rainfed_pct}} of the baseline yield. So most of the saving comes from the
  baseline applying far more water than the crop needs, not from clever scheduling. In a drier climate,
  or against a leaner baseline, the saving would be smaller.
- The selected scheduler irrigated nothing in {{zero_irr_seasons}} of {{n_seasons}} seasons, so its very high
  water productivity mainly reflects rainfall doing the work.
- The full strategy table shows the gradient; even the most generous threshold (`smt_90`) uses far less
  water than the baseline:

{{strategy_table}}

### Charts

![Irrigation vs yield by strategy (simulated)](results/irrigation_vs_yield.png)

![Water saved per season (simulated)](results/water_saved_per_season.png)

![Impact summary (simulated)](results/impact_summary.png)

## How to run

Tested on Python 3.12.4 (Windows). Python 3.10 and 3.11 were not tested.

```bash
pip install -r requirements.txt
python run_experiment.py   # ~3 minutes; writes results/results.csv
python analyze.py && python build_deck.py   # impact.json, charts, README, video script, deck
```

Tests: `pytest`.

## Data source

Weather: `tunis_climate.txt`, the sample daily climate file bundled with AquaCrop-OSPy
(Tunis, Tunisia, 1979 to 2002). **Simulated; not Jaipur and not any Indian site.** Crop and soil
parameters: AquaCrop-OSPy built-in `Wheat` and `SandyLoam`.

## Assumptions

Every assumption lives in `config.py` with the tag `# ASSUMPTION - verify before submission`.
Details and verification status: [docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md).

| Assumption | Value | Status |
|---|---|---|
| Baseline depth per irrigation | {{base_depth}} mm | to verify |
| Baseline interval | {{base_interval}} days | to verify |
| Pump total head | {{head_m}} m (sensitivity 15 / 30 / 60 m) | to verify |
| Overall pump-set efficiency | {{pump_eff}} | to verify |
| Electricity tariff | {{tariff}}/kWh (placeholder) | to verify |
| Grid emission factor | {{grid_ef}} kg CO₂/kWh (placeholder) | to verify |
| Application efficiency | 100 % for all strategies (model default) | modelling choice |
| Max irrigation per day | 25 mm for all strategies (model default) | modelling choice |

## Limitations

- **Simulated results only.** No field data; the model has not been calibrated to any farm.
- **Sample climate, not local.** Tunis weather from 1979 to 2002, not an Indian site.
- **Single crop and soil.** Wheat on sandy loam only.
- **Modest innovation.** Threshold-based soil-moisture scheduling is a well-known technique; the
  contribution here is a transparent, reproducible quantification of its savings, not a new algorithm.
- **No economic model beyond the stated assumptions.** No capital cost, payback, subsidy, labour or
  water-price modelling; tariffs and emission factors are placeholders until verified.
- The baseline is one stylised farmer schedule; real practice varies widely and drives the size of the saving.

## Credits

- [AquaCrop-OSPy](https://github.com/aquacropos/aquacrop) (Apache License 2.0), the Python
  implementation of the FAO AquaCrop model used for all simulations. This project uses its public API;
  no tutorial code is copied.
- FAO AquaCrop crop-water productivity model (Food and Agriculture Organization of the United Nations).

## License

Source code in this repository: MIT, see [LICENSE](LICENSE). AquaCrop-OSPy is a separate dependency
under Apache 2.0.

## More documentation

- [docs/METHODOLOGY.md](docs/METHODOLOGY.md): model setup, verified API behaviour, formulas
- [docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md)
- [docs/DEPLOYMENT_PATH.md](docs/DEPLOYMENT_PATH.md)
- [docs/VIDEO_SCRIPT.md](docs/VIDEO_SCRIPT.md)
- [docs/SUBMISSION_CHECKLIST.md](docs/SUBMISSION_CHECKLIST.md)
