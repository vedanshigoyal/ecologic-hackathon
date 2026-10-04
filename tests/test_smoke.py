"""Smoke test: one strategy, one season, plus the unit conversion. Results are simulated."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
from run_experiment import load_weather, run_strategy  # noqa: E402


def test_litres_conversion():
    assert config.mm_to_litres_per_ha(1) == 10_000


def test_pump_energy_formula():
    # 1000 * 9.81 * 30 / (0.45 * 3.6e6) = 0.18167 kWh/m3
    assert abs(config.pump_kwh_per_m3(30, 0.45) - 0.181667) < 1e-5


def test_one_season_runs():
    strategy = {"id": "smt_70", "method": 1, "smt": 70}
    out = run_strategy(strategy, load_weather(), "1979/10/01", "1980/05/31")
    assert len(out) == 1
    assert out["dry_yield_t_ha"].iloc[0] > 0
    assert out["irrigation_mm"].iloc[0] >= 0


def test_baseline_schedule_is_fixed_depth_interval():
    strategy = {"id": config.BASELINE_ID, "method": 3}
    out = run_strategy(strategy, load_weather(), "1979/10/01", "1980/05/31")
    mm = out["irrigation_mm"].iloc[0]
    assert mm > 0
    assert mm % config.BASELINE_DEPTH_MM == 0  # whole number of fixed-depth events
