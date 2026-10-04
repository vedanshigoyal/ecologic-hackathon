# Deployment path: from simulation to field

> **Status: concept only. None of the hardware below has been built or tested in this submission.**
> The simulation shows what the threshold rule could save; this document describes how the same rule
> would run on a farm and how a pilot would check the simulated savings against reality.

## 1. The rule being deployed

The simulated scheduler is the AquaCrop "soil-moisture target" rule:

```
every day (or every few hours):
    depletion_fraction = (field_capacity_water - current_root_zone_water) / total_available_water
    if depletion_fraction > 1 - SMT/100:
        irrigate until the root zone is back near field capacity   (capped at the system's max depth)
```

With the selected threshold (`SMT` from `results/selection.json`), the controller waits until the
root zone has dried to that fraction of its available water, then refills it.

## 2. Architecture

```
 [Capacitive soil-moisture probes]  -->  [Microcontroller / edge gateway]  -->  [Relay / contactor]  -->  [Pump or solenoid valve]
   2 depths in root zone                  reads sensors, applies rule,          switches pump / valve
   (e.g. 15 cm and 40 cm)                 logs data, fail-safe timers
                                                  |
                                                  v
                                     [Dashboard: local app or cloud]
                                     moisture trend, irrigation log, water/kWh estimate, manual override
```

- **Sensors:** capacitive soil-moisture probes (no exposed electrodes, so less corrosion than resistive
  probes), at two depths within the root zone, at least two locations per plot.
- **Controller:** a low-power microcontroller (ESP32-class) or a small edge gateway. Runs the threshold
  rule locally so irrigation still works without connectivity.
- **Actuation:** relay or contactor on the pump starter, or a solenoid valve on a drip/sprinkler line.
  Hard maximum run-time and a manual override for safety.
- **Connectivity (optional):** Wi-Fi, GSM or LoRa uplink to a dashboard. Optional weather-forecast input
  to skip irrigation before forecast rain (a future extension, not simulated here).
- **Metering:** a flow meter (or pump run-time × rated flow) and an energy meter to measure water and
  kWh directly during the pilot, replacing the assumptions in `config.py`.

## 3. Calibration to local soil

Capacitive probes report a raw value, not volumetric water content. Before use:

1. Take soil samples at several moisture levels from the actual plot; measure volumetric water content
   gravimetrically (weigh, oven-dry, weigh).
2. Fit a calibration curve from raw reading to water content for that soil.
3. Determine field capacity and wilting point for the plot (lab test or field method) to compute total
   available water, which the threshold rule needs.
4. Re-check calibration each season.

## 4. Rough bill of materials (per plot, ESTIMATES TO VERIFY)

All prices are rough order-of-magnitude estimates for the Indian retail market, **not quotes, and not
verified**. Get real quotes before using them in any cost claim.

| Item | Qty | Rough unit cost (₹, estimate) |
|---|---|---|
| Capacitive soil-moisture probe (outdoor-rated) | 4 | 300 to 2,000 |
| ESP32-class microcontroller board | 1 | 400 to 1,000 |
| Relay / contactor interface for pump starter | 1 | 500 to 3,000 |
| Enclosure (IP65), wiring, connectors | 1 | 800 to 2,000 |
| Power: adapter or small solar panel + battery | 1 | 1,000 to 5,000 |
| Flow meter (for the pilot) | 1 | 2,000 to 8,000 |
| Optional GSM/LoRa module | 1 | 500 to 2,500 |

No payback calculation is made in this submission (see README limitations).

## 5. Pilot plan

- **Design:** one field split into two comparable plots (same crop, soil, sowing date, variety, fertiliser).
  - Control plot: the farmer's normal schedule.
  - Treatment plot: irrigation triggered by the threshold controller.
- **Measure:** water applied (flow meter), pump energy (energy meter), soil moisture, rainfall, final yield
  (harvest a measured area from each plot).
- **Duration:** at least one full season; ideally replicate across several farms, since one season and one
  farm cannot separate the scheduler's effect from field variability.
- **Compare with simulation:** run this repository with local weather and the measured soil properties,
  and compare simulated vs measured water and yield. Report the gap honestly.
- **Success criterion (proposed):** treatment uses measurably less water and energy with yield within the
  same 2 % tolerance used in the simulation.

## 6. Scaling

- The rule is a few lines of logic and runs on cheap hardware; the main per-farm work is calibration.
- One controller can serve several valves/zones on the same pump.
- Fits alongside existing pump-solarisation or drip programmes: less water pumped means a smaller
  solar array or more area served per pump.
