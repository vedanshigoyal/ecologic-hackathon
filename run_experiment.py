"""Run every irrigation strategy through AquaCrop-OSPy and write per-season results.

Output: results/results.csv with columns strategy, season, dry_yield_t_ha, irrigation_mm.
All numbers are SIMULATED (AquaCrop-OSPy model), not field measurements.
"""

import pandas as pd
from aquacrop import AquaCropModel, Crop, InitialWaterContent, IrrigationManagement, Soil
from aquacrop.utils import get_filepath, prepare_weather

import config


def load_weather() -> pd.DataFrame:
    return prepare_weather(get_filepath(config.WEATHER_FILE))


def baseline_schedule(sim_start: str, sim_end: str) -> pd.DataFrame:
    """Farmer-style schedule: fixed depth on planting day and every N days after.

    Dates outside the growing season are ignored by AquaCrop (method 3 only applies
    in-season), so we simply list every interval date from each planting day to the
    end of the simulation window.
    """
    start, end = pd.Timestamp(sim_start), pd.Timestamp(sim_end)
    month, day = (int(x) for x in config.PLANTING_DATE.split("/"))
    dates = []
    for year in range(start.year, end.year + 1):
        planting = pd.Timestamp(year=year, month=month, day=day)
        if planting < start or planting > end:
            continue
        next_planting = pd.Timestamp(year=year + 1, month=month, day=day)
        season_dates = pd.date_range(planting, min(end, next_planting - pd.Timedelta(days=1)),
                                     freq=f"{config.BASELINE_INTERVAL_DAYS}D")
        dates.extend(season_dates)
    return pd.DataFrame({"Date": pd.DatetimeIndex(dates),
                         "Depth": [config.BASELINE_DEPTH_MM] * len(dates)})


def irrigation_for(strategy: dict, sim_start: str, sim_end: str) -> IrrigationManagement:
    common = {"MaxIrr": config.MAX_IRR_MM_PER_DAY, "AppEff": config.APPLICATION_EFFICIENCY_PCT}
    method = strategy["method"]
    if method == 0:
        return IrrigationManagement(irrigation_method=0)
    if method == 1:
        return IrrigationManagement(irrigation_method=1, SMT=[strategy["smt"]] * 4, **common)
    if method == 3:
        return IrrigationManagement(irrigation_method=3,
                                    Schedule=baseline_schedule(sim_start, sim_end), **common)
    raise ValueError(f"Unsupported irrigation method {method} for {strategy['id']}")


def run_strategy(strategy: dict, weather: pd.DataFrame,
                 sim_start: str = config.SIM_START, sim_end: str = config.SIM_END) -> pd.DataFrame:
    model = AquaCropModel(
        sim_start_time=sim_start,
        sim_end_time=sim_end,
        weather_df=weather,
        soil=Soil(config.SOIL_TYPE),
        crop=Crop(config.CROP_NAME, planting_date=config.PLANTING_DATE),
        initial_water_content=InitialWaterContent(value=[config.INITIAL_WATER_CONTENT]),
        irrigation_management=irrigation_for(strategy, sim_start, sim_end),
    )
    model.run_model(till_termination=True)
    res = model.get_simulation_results()
    harvest = pd.to_datetime(res["Harvest Date (YYYY/MM/DD)"])
    return pd.DataFrame({
        "strategy": strategy["id"],
        # label each season by its sowing and harvest years, e.g. 1979-80
        "season": [f"{y - 1}-{str(y)[-2:]}" for y in harvest.dt.year],
        "dry_yield_t_ha": res["Dry yield (tonne/ha)"].astype(float).round(4),
        "irrigation_mm": res["Seasonal irrigation (mm)"].astype(float).round(4),
    })


def main() -> None:
    weather = load_weather()
    config.RESULTS_DIR.mkdir(exist_ok=True)
    frames = []
    for strategy in config.STRATEGIES:
        print(f"Running {strategy['id']} ...", flush=True)
        frames.append(run_strategy(strategy, weather))
    results = pd.concat(frames, ignore_index=True)
    out = config.RESULTS_DIR / "results.csv"
    results.to_csv(out, index=False)

    summary = (results.groupby("strategy", sort=False)
               .agg(seasons=("season", "count"),
                    mean_yield_t_ha=("dry_yield_t_ha", "mean"),
                    mean_irrigation_mm=("irrigation_mm", "mean"))
               .round(2))
    print(f"\nSIMULATED results ({config.WEATHER_LABEL}, {config.CROP_NAME}, {config.SOIL_TYPE}, "
          f"{config.SIM_START} to {config.SIM_END})")
    print(summary.to_string())
    print(f"\nWrote {len(results)} per-season rows to {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
