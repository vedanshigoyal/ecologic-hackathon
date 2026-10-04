<!-- GENERATED FILE: edit docs/templates/VIDEO_SCRIPT.template.md, then run `python analyze.py`. Numbers come from results/impact.json. -->

# SmartIrrigate: demo video script (about 2 min 40 s)

Plain-language narration for the demo video. Speak slowly; the timestamps are targets, not hard cuts.

**Must be said on camera:** "These results are simulated with the FAO AquaCrop crop model. They are
not measurements from a real farm."

| Time | Shot (what is on screen) | Narration |
|---|---|---|
| 0:00 to 0:20 | Deck slide 1, then slide 2 | **Problem.** "A lot of farms water their crops on a calendar: the same amount every few days, rain or shine. When the soil is already wet, that water just drains away, and the electricity used to pump it is wasted too. We wanted to know how much of that could be saved." |
| 0:20 to 0:40 | Deck slide 4 (method) | **Baseline.** "Our baseline is a simple farmer-style schedule: 25 millimetres of water every 7 days. Over a wheat season that adds up to 725 millimetres. Our alternative only waters when a soil-moisture reading says the root zone is getting dry." |
| 0:40 to 1:20 | Terminal: run `python run_experiment.py` (speed up the wait), then `python analyze.py`; show the printed summary | **Running it.** "We tested this in a crop simulator called AquaCrop, built by the UN's Food and Agriculture Organization. We ran 23 wheat seasons of real historical weather from a sample dataset for Tunis, comparing the calendar schedule with six different moisture thresholds. Before looking at any results, we fixed our rule for picking the winner: use the least water while keeping at least 98 percent of the baseline yield. The rule picked the threshold called smt_40." |
| 1:20 to 2:00 | `results/irrigation_vs_yield.png`, then `results/impact_summary.png` | **Result.** "Here is the result. The calendar schedule used 725 millimetres per season; the moisture-based rule used about 26.1. Yield stayed the same: 9.37 versus 9.36 tonnes per hectare. That is about 6.99 million litres of water saved per hectare, every season. With our assumed pump and tariff, that is around 1,270 kilowatt-hours, ₹7,618 of electricity and 901 kilograms of CO2 per hectare per season. One honest caveat: in this climate, wheat grown on rain alone already got 98.5% of the baseline yield, so most of the saving comes from the calendar schedule over-watering." |
| 2:00 to 2:30 | Deck slide 3 (architecture), then slide 7 | **Deployment and limits.** "In the field, the same rule would run on a cheap soil-moisture sensor, a small controller and a relay on the pump. We have not built or tested that hardware yet; the next step is a pilot with one field split into a normal plot and a sensor-controlled plot. These results are simulated with the FAO AquaCrop crop model. They are not measurements from a real farm. They use a sample climate, not Indian weather, and one crop and one soil." |
| 2:30 to 2:40 | Deck slide 1 with team name | **Close.** "SmartIrrigate: water only when the soil asks for it. Everything is open source and reproducible with three commands. Thank you." |

## Recording notes

- Record the terminal at a large font size. `run_experiment.py` takes about 3 minutes; cut or speed up the wait.
- Do not read numbers from memory; they are filled in above from `results/impact.json`. If you change any
  assumption, re-run `python analyze.py` and this script updates.
- Keep the "simulated" sentence in the final cut.
