# Assumptions

Every value below is set in `config.py`. Values tagged `# ASSUMPTION - verify before submission`
there are **not yet verified against a source**. No source has been cited for them in this repository;
the team must check each one, record the source here, and change the status.

Changing a value in `config.py` and re-running `python analyze.py` updates `results/impact.json`,
the charts, the README, the video script and (after `python build_deck.py`) the deck.

## Assumptions to verify

| # | Assumption | Value | Why this value | Where to verify | Source | Status |
|---|---|---|---|---|---|---|
| 1 | Baseline irrigation depth per event | 25 mm | A common round figure for a surface/flood irrigation event; also AquaCrop's default max daily depth | Local agronomy extension guidance, farmer survey | _none yet_ | **To verify** |
| 2 | Baseline irrigation interval | 7 days | Weekly calendar irrigation as a stylised farmer practice | Same as above | _none yet_ | **To verify** |
| 3 | Pump total dynamic head H | 30 m | Mid-range value for a borewell pump; sensitivity run at 15 and 60 m | Local groundwater depth data, pump specifications | _none yet_ | **To verify** |
| 4 | Overall pump-set efficiency η | 0.45 | Agricultural pump sets are often well below nameplate efficiency; 0.45 gives ≈ 0.18 kWh/m³ at 30 m | Pump-set efficiency audits / manufacturer data | _none yet_ | **To verify** |
| 5 | Electricity tariff | ₹6.0 /kWh | Placeholder. Agricultural tariffs in India vary by state and are often subsidised; the true marginal cost to the utility may differ from what the farmer pays | State electricity regulatory commission tariff order for the target state | _none yet_ | **To verify (placeholder)** |
| 6 | Grid emission factor | 0.71 kg CO₂/kWh | Placeholder | Central Electricity Authority (India) "CO2 Baseline Database for the Indian Power Sector", latest edition | _none yet_ | **To verify (placeholder)** |
| 7 | Sensitivity heads | 15, 30, 60 m | Spans shallow to deep pumping so results do not hinge on one head | As #3 | _none yet_ | **To verify** |

## Modelling choices (not external facts)

| Choice | Value | Reason |
|---|---|---|
| Crop | AquaCrop-OSPy built-in `Wheat` | Rabi staple; built-in parameters avoid inventing crop data |
| Soil | AquaCrop-OSPy built-in `SandyLoam` | Free-draining soil where over-irrigation is lost to drainage |
| Planting date | 1 October | Fits the sample climate's seasons; harvest falls before 31 May |
| Initial water content | Field capacity | Model convention; same for all strategies |
| Weather | `tunis_climate.txt` (bundled sample) | Only climate data shipped with the library; **not Indian** |
| Simulation window | 1979/10/01 to 2002/05/31 (23 seasons) | All complete seasons in the weather file |
| Application efficiency | 100 % for all strategies | Model default; method 3 (baseline) ignores AppEff, so 100 % keeps the comparison fair |
| Max irrigation per day | 25 mm for all strategies | Model default; same cap for every strategy |
| Selection rule threshold | 98 % of baseline mean yield | Fixed before results were seen (`config.YIELD_RETENTION_MIN`) |

## Exact constants (not assumptions)

| Constant | Value |
|---|---|
| 1 mm of water over 1 ha | 10 m³ = 10 000 L |
| Water density ρ | 1000 kg/m³ |
| Gravity g | 9.81 m/s² |
| 1 kWh | 3.6 × 10⁶ J |
