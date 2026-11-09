# CWE 2030 in PyPSA: storage, interconnectors and bidding zones

An open, reproducible study of the German power market and its neighbours for 2030, built with [PyPSA](https://pypsa.org) and open data.

> **Status:** work in progress (started November 2026). Results are added block by block.

## Progress

- [x] Conda environment and ENTSO-E API access
- [x] Data loader with local caching (`src/entsoe_data.py`)
- [x] Market overview of DE-LU and neighbours, 2024 (`notebooks/02_entsoe_2024.ipynb`)
- [x] Market overview 2025, calibration year (`notebooks/02_entsoe_2025.ipynb`)
- [ ] Block 1: model validation against actual prices
- [ ] Blocks 2–6: 2030 scenarios

## Why this project

Germany's power system is changing fast: more wind and solar, more batteries, more cross-border trade, and an open debate about bidding zones. This project asks a few practical questions that TSOs, regulators and investors face, and answers them with a small, transparent model that anyone can rerun.

## Questions

| # | Question | Main outputs |
| --- | --- | --- |
| 1 | Does the model reproduce the calibration year? | Modelled vs actual day-ahead prices, generation mix |
| 2 | What do prices and flows look like in 2030? | Prices by zone, cross-border flows, congestion hours, curtailment |
| 3 | How much battery storage is worth building? | Optimal storage by zone, storage revenues, effect on price spreads |
| 4 | Is one extra interconnector worth it? | Welfare change, congestion rent and CO2 vs annualised cost |
| 5 | What if Germany splits into two bidding zones? | Prices in DE-North vs DE-South, internal congestion |
| 6 | Is the 2030 system adequate in bad weather? | Unserved energy and scarcity hours across several weather years |

Blocks 1–4 are the core. Blocks 5–6 follow if time allows.

## First findings: DE-LU day-ahead market 2024 and 2025

| Indicator | 2024 | 2025 |
| --- | --- | --- |
| Average price (EUR/MWh) | 78.5 | 89.3 |
| Median price (EUR/MWh) | 79.6 | 92.4 |
| Minimum price (EUR/MWh) | −135.4 | −250.3 |
| Maximum price (EUR/MWh) | 936.3 | 583.4 |
| Hours with negative prices | 457 | 576 |
| Hours above 150 EUR/MWh | 361 | 635 |

Hourly values; from October 2025 they are averages of four 15-minute prices, which smooths the most extreme quarter-hours.

**2025 compared with 2024:** prices were higher on average and more volatile at both ends. There were about a quarter more hours with negative prices and almost twice as many hours above 150 EUR/MWh. The midday solar dip became deeper (May–June midday averages close to zero), while morning and evening peaks were stronger, especially in winter and in September evenings. The single highest price was lower than the December 2024 peak.

**Neighbouring zones, average day-ahead price (EUR/MWh):**

| Zone | 2024 | 2025 | Change |
| --- | --- | --- | --- |
| FR | 58.0 | 61.1 | +3.1 |
| DK1 | 70.6 | 81.1 | +10.5 |
| BE | 70.3 | 82.6 | +12.3 |
| NL | 77.3 | 86.8 | +9.5 |
| DE-LU | 78.5 | 89.3 | +10.8 |
| CZ | 85.1 | 96.8 | +11.7 |
| AT | 81.5 | 98.9 | +17.4 |
| PL | 96.3 | 104.3 | +8.0 |

The price order between zones stayed almost the same: France is the cheapest zone, Poland the most expensive, and DE-LU sits in the middle. Most zones became 8–17 EUR/MWh more expensive, but France only 3 EUR/MWh, so the average FR–DE spread grew from 20.5 to 28.2 EUR/MWh. A larger and persistent spread makes the FR–DE border a natural candidate for the interconnector analysis in block 4.

**2024 in more detail:**

- **Solar shapes the daily price curve.** From April to September, midday prices are the lowest of the day, and even the monthly maximum prices stay low between 10:00 and 16:00.
- **The evening peak grows from spring to autumn.** After sunset (18:00–21:00) prices rise, with monthly maxima above 300 EUR/MWh in September and October.
- **The highest prices come in November and December.** Periods with little wind and sun ("Dunkelflaute") pushed prices above 300 EUR/MWh for most of the day in December and up to 936 EUR/MWh.
- **Neighbours:** France is much cheaper in spring and summer (around 30 EUR/MWh in April–May), Poland is the most expensive zone most of the year, and DE-LU, NL, AT and CZ move closely together.

For the model this means: block 1 should reproduce the price level, the daily shape and the price order between zones. Scarcity peaks of several hundred EUR/MWh are not expected to be captured by a simple cost-based model (see limitations).

## Scope

- **Zones:** DE-LU (one zone, or DE-North / DE-South in block 5), FR, NL, BE, PL, CZ, AT, DK1
- **Time:** hourly, 8,760 hours; 2025 as calibration year, 2030 for scenarios
- **Network:** zonal transport model with net transfer capacities (NTC)
- **Model type:** linear dispatch and capacity expansion (no unit commitment)

## Data

| Data | Source |
| --- | --- |
| Load, generation, day-ahead prices | [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) via `entsoe-py` |
| 2030 installed capacities | ENTSO-E TYNDP 2024 scenario data |
| Wind and solar profiles | renewables.ninja or `atlite` (ERA5) |
| Technology costs | PyPSA `technology-data` |
| Fuel and CO2 prices | Own assumptions in `config.yaml` |

Notes on data handling:

- Downloads are cached as CSV in `data/raw/` and are not stored in the repository; they can be downloaded again at any time.
- 15-minute load and generation data are averaged to hourly values. Since 1 October 2025 day-ahead prices have a 15-minute resolution; they are averaged to hourly values for the hourly model.
- Data are trimmed to the exact calendar year, because the API can return extra hours at the edges of a period.
- One missing DE-LU price in 2024 (2024-12-31 00:00) was filled by linear interpolation. Gaps longer than three hours are not filled.

## Tools

PyPSA · linopy · HiGHS (open-source solver) · pandas · matplotlib · pytest · Jupyter

## Repository structure

```
cwe-2030-pypsa/
├── README.md
├── environment.yml          # conda environment
├── src/
│   ├── entsoe_data.py       # ENTSO-E download with local caching
│   └── check_entsoe.py      # API connection check
├── notebooks/
│   ├── 02_entsoe_2024.ipynb # market overview DE-LU and neighbours, 2024
│   └── 02_entsoe_2025.ipynb # market overview DE-LU and neighbours, 2025
└── data/raw/                # cached downloads (not in Git)
```

Planned: `config.yaml`, `src/build_network.py`, `src/scenarios.py`, `tests/`, `results/`.

## How to run

1. Create the environment:
   ```
   conda env create -f environment.yml
   conda activate cwe-2030-pypsa
   ```
2. Get a free ENTSO-E API token and put it in a `.env` file in the project root (never commit this file):
   ```
   ENTSOE_API_KEY=your_token
   ```
3. Open the notebooks in `notebooks/` and run all cells. The first run downloads the data; later runs read the cache.

## Known limitations

- NTC-based exchanges instead of flow-based market coupling
- No unit commitment, ramping constraints or scarcity pricing; extreme price peaks will be underestimated
- Simplified hydro and storage reservoirs
- Hourly resolution, while the day-ahead market moved to 15-minute products in October 2025
- 2030 inputs are scenario assumptions, not forecasts

## Author

Andrey Perevertaev, power system economist and market modeller · [LinkedIn](https://www.linkedin.com/in/aperever/)

## License

MIT
