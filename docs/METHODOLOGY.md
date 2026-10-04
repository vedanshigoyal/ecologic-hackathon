# Methodology

All results in this project are **simulated** with the FAO AquaCrop crop-water model
(Python port AquaCrop-OSPy). Nothing here is field-measured.

## 1. Verified API behaviour (Stage 1)

Checked by reading the installed source of `aquacrop==3.1.0` on Python 3.12.4
(`aquacrop/core.py`, `aquacrop/entities/irrigationManagement.py`,
`aquacrop/solution/irrigation.py`, `aquacrop/initialize/read_irrigation_management.py`,
`aquacrop/entities/output.py`).

| Item | Verified behaviour |
|---|---|
| `AquaCropModel(...)` | `sim_start_time`, `sim_end_time` as `'YYYY/MM/DD'` strings; `weather_df`, `soil`, `crop`, `initial_water_content`, optional `irrigation_management`, `field_management`, `groundwater`, `co2_concentration`, `off_season=False` |
| `Crop(c_name, planting_date)` | planting date as `'MM/DD'` |
| `InitialWaterContent(value=['FC'])` | defaults `wc_type='Prop'`, `method='Layer'` |
| `IrrigationManagement(irrigation_method, **kwargs)` | accepted kwargs: `WetSurf`, `AppEff` (default 100 %), `MaxIrr` (default **25 mm/day**), `MaxIrrSeason` (default 10 000 mm), `SMT`, `IrrInterval`, `Schedule`, `NetIrrSMT`, `depth`. Unknown kwargs are silently ignored. |
| Method 0 | rainfed, no irrigation |
| Method 1 (`SMT`) | each day, if root-zone depletion fraction `Dr/TAW > 1 − SMT[stage]/100`, irrigate `min(MaxIrr, depletion × (200 − AppEff)/100)`; otherwise 0 |
| **Method 2 (`IrrInterval`)** | irrigates every `IrrInterval` days starting on day 1 after planting, but the depth is `min(MaxIrr, current root-zone depletion × (200 − AppEff)/100)`. **It refills the soil deficit; it does not apply a fixed depth.** |
| Method 3 (`Schedule`) | a DataFrame with `Date`, `Depth` columns, reindexed onto the simulation days (missing days = 0). Depth on each day is `min(MaxIrr, scheduled depth)`. Applied only on days inside the growing season. |
| Season cap | any method: cumulative irrigation in a season is capped at `MaxIrrSeason` |
| `get_simulation_results()` columns | `Season`, `crop Type`, `Harvest Date (YYYY/MM/DD)`, `Harvest Date (Step)`, `Dry yield (tonne/ha)`, `Fresh yield (tonne/ha)`, `Yield potential (tonne/ha)`, `Seasonal irrigation (mm)` |

**Consequence for the baseline:** because method 2 is itself a deficit-refill
scheduler (it already knows the soil moisture), it is not a realistic
"farmer applies X mm every N days" baseline. The `fixed_7d` baseline is therefore
built as a **method 3 predefined schedule: 25 mm on planting day and every 7 days
after, until the end of the growing season** (scheduled dates after crop maturity are
ignored by the model because method 3 only applies inside the growing season).

## 2. Model setup

| Parameter | Value |
|---|---|
| Crop | `Wheat` (AquaCrop-OSPy built-in parameters) |
| Planting date | 1 October each year |
| Soil | `SandyLoam` (built-in) |
| Initial water content | field capacity (`FC`) at the start of the simulation |
| Weather | AquaCrop-OSPy bundled sample file `tunis_climate.txt` (Tunis, Tunisia; 1979-01-01 to 2002-05-31) |
| Simulation window | 1979/10/01 to 2002/05/31 (all complete wheat seasons in the file) |
| Application efficiency | 100 % for every strategy (model default; keeps method 1 and method 3 comparable, since method 3 ignores `AppEff`) |
| Max depth per irrigation day | 25 mm for every strategy (model default) |

See `config.py` for the authoritative values.

## 3. Strategies

| ID | Description |
|---|---|
| `rainfed` | method 0, reference only |
| `fixed_7d` | **baseline**, method 3 schedule, 25 mm every 7 days from planting |
| `smt_40` … `smt_90` | method 1, `SMT=[t, t, t, t]` for t = 40, 50, 60, 70, 80, 90 (% of total available water to keep in the root zone) |

All strategies use the same weather, soil, crop and seasons.

## 4. Selection rule (fixed before looking at results)

> Choose the SMT strategy with the **lowest mean seasonal irrigation (mm)** among those
> whose **mean dry yield is at least 98 % of the `fixed_7d` mean yield**. If none qualify,
> state this plainly and report the best yield-preserving trade-off without claiming it
> meets the rule.

## 5. Metric formulas

Per hectare per season; reported as mean across seasons plus min, max and standard deviation.

- Water saved (L/ha) = (baseline mm − scheduler mm) × 10 000 (1 mm on 1 ha = 10 m³ = 10 000 L)
- Yield difference = scheduler − baseline (t/ha and % of baseline)
- Water productivity of irrigation (kg/m³) = yield (t/ha) × 1000 / (irrigation mm × 10)
- Pump energy per m³ (kWh/m³) = ρ g H / (η × 3.6×10⁶), with ρ = 1000 kg/m³, g = 9.81 m/s²,
  H = pumping head (assumption), η = overall pump efficiency (assumption)
- Energy saved (kWh/ha) = water saved (m³/ha) × energy per m³
- Cost saved (₹/ha) = energy saved × tariff (assumption)
- CO₂ saved (kg/ha) = energy saved × grid emission factor (assumption)
- Paired per-season comparison: number of seasons in which the scheduler used less water
  than the baseline, and number in which its yield was within 2 % of the baseline yield.
