"""SmartIrrigate configuration: every parameter and assumption lives here.

All outputs of this project are SIMULATED with AquaCrop-OSPy. Nothing is field-measured.
Lines tagged "ASSUMPTION - verify before submission" are not taken from a cited source
and must be checked by the team (see docs/ASSUMPTIONS.md).
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
DECK_PATH = ROOT / "deck" / "SmartIrrigate_Deck.pptx"

TEAM_NAME = "Codexa"
TEAM_MEMBERS = ["Vedanshi Goyal", "Apoorva Singh", "Soumyadip Manna", "Pranay Maheshwari"]

# --- Crop / soil / weather (model inputs) -----------------------------------------
CROP_NAME = "Wheat"
PLANTING_DATE = "10/01"  # MM/DD, 1 October
SOIL_TYPE = "SandyLoam"
INITIAL_WATER_CONTENT = "FC"  # field capacity at simulation start
WEATHER_FILE = "tunis_climate.txt"  # bundled AquaCrop-OSPy sample (Tunis), NOT local Indian data
WEATHER_LABEL = "Tunis, Tunisia (AquaCrop-OSPy bundled sample climate)"

# Bundled weather covers 1979-01-01 .. 2002-05-31, so every complete wheat season fits.
SIM_START = "1979/10/01"
SIM_END = "2002/05/31"

# Irrigation hardware limits applied identically to every strategy (model defaults).
MAX_IRR_MM_PER_DAY = 25.0
APPLICATION_EFFICIENCY_PCT = 100.0

# --- Strategies -------------------------------------------------------------------
BASELINE_ID = "fixed_7d"
BASELINE_INTERVAL_DAYS = 7  # ASSUMPTION - verify before submission (typical farmer interval)
BASELINE_DEPTH_MM = 25.0  # ASSUMPTION - verify before submission (typical farmer depth per event)

SMT_LEVELS = [40, 50, 60, 70, 80, 90]  # % of total available water kept in root zone

STRATEGIES = (
    [{"id": "rainfed", "method": 0}]
    + [{"id": BASELINE_ID, "method": 3}]
    + [{"id": f"smt_{t}", "method": 1, "smt": t} for t in SMT_LEVELS]
)

# --- Selection rule (fixed BEFORE looking at results; do not tune) -----------------
YIELD_RETENTION_MIN = 0.98  # scheduler mean yield must be >= 98% of baseline mean yield
SELECTION_RULE_TEXT = (
    "Choose the SMT strategy with the lowest mean seasonal irrigation (mm) among those "
    "whose mean dry yield is at least 98% of the fixed_7d mean yield. If none qualify, "
    "report that plainly and show the best yield-preserving trade-off without claiming "
    "it meets the rule."
)
PAIRED_YIELD_TOLERANCE = 0.02  # per-season "yield within 2%" check

# --- Unit conversions (exact) -----------------------------------------------------
LITRES_PER_MM_PER_HA = 10_000  # 1 mm over 1 ha = 10 m3 = 10,000 L
M3_PER_MM_PER_HA = 10

# --- Energy / cost / CO2 ------------------------------------------------------------
WATER_DENSITY_KG_M3 = 1000.0
GRAVITY_M_S2 = 9.81
PUMP_HEAD_M = 30.0  # ASSUMPTION - verify before submission (total dynamic head of a borewell pump)
PUMP_EFFICIENCY = 0.45  # ASSUMPTION - verify before submission (overall pump-set efficiency)
TARIFF_INR_PER_KWH = 6.0  # ASSUMPTION - verify before submission (placeholder electricity tariff)
GRID_EF_KG_CO2_PER_KWH = 0.71  # ASSUMPTION - verify before submission (placeholder grid emission factor)
SENSITIVITY_HEADS_M = [15.0, 30.0, 60.0]  # ASSUMPTION - verify before submission (range of plausible heads)


def pump_kwh_per_m3(head_m: float = PUMP_HEAD_M, efficiency: float = PUMP_EFFICIENCY) -> float:
    """Electrical energy to lift 1 m3 of water by head_m metres: rho*g*H / (eta * 3.6e6)."""
    return WATER_DENSITY_KG_M3 * GRAVITY_M_S2 * head_m / (efficiency * 3.6e6)


def mm_to_litres_per_ha(mm: float) -> float:
    return mm * LITRES_PER_MM_PER_HA
