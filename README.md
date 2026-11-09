# CWE 2030 in PyPSA: storage, interconnectors and bidding zones

An open, reproducible study of the German power market and its neighbours for 2030, built with [PyPSA](https://pypsa.org) and open data.

> **Status:** work in progress (started November 2026). Results will be added block by block.

## Why this project

Germany's power system is changing fast: more wind and solar, more batteries, more cross-border trade, and an open debate about bidding zones. This project asks a few practical questions that TSOs, regulators and investors face, and answers them with a small, transparent model that anyone can rerun.

## Questions

| # | Question | Main outputs |
| --- | --- | --- |
| 1 | Does the model reproduce 2024? | Modelled vs actual day-ahead prices, generation mix |
| 2 | What do prices and flows look like in 2030? | Prices by zone, cross-border flows, congestion hours, curtailment |
| 3 | How much battery storage is worth building? | Optimal storage by zone, storage revenues, effect on price spreads |
| 4 | Is one extra interconnector worth it? | Welfare change, congestion rent and CO2 vs annualised cost |
| 5 | What if Germany splits into two bidding zones? | Prices in DE-North vs DE-South, internal congestion |
| 6 | Is the 2030 system adequate in bad weather? | Unserved energy and scarcity hours across several weather years |

Blocks 1–4 are the core. Blocks 5–6 follow if time allows.

## Scope

- **Zones:** DE (one zone, or DE-North / DE-South in block 5), FR, NL, BE, PL, CZ, AT, DK
- **Time:** hourly, 8,760 hours; 2024 for validation, 2030 for scenarios
- **Network:** zonal transport model with net transfer capacities (NTC)
- **Model type:** linear dispatch and capacity expansion (no unit commitment)

## Data

| Data | Source |
| --- | --- |
| Load, generation, day-ahead prices (2024) | [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) via `entsoe-py` |
| 2030 installed capacities | ENTSO-E TYNDP 2024 scenario data |
| Wind and solar profiles | renewables.ninja or `atlite` (ERA5) |
| Technology costs | PyPSA `technology-data` |
| Fuel and CO2 prices | Own assumptions in `config.yaml` |

Only open data is used. API keys are kept in a local `.env` file and are never committed.

## Tools

PyPSA · linopy · HiGHS (open-source solver) · pandas · matplotlib · pytest

## Repository structure (planned)

```
cwe-2030-pypsa/
├── README.md
├── environment.yml      # pinned package versions
├── config.yaml          # zones, years, prices, scenarios
├── src/
│   ├── data_fetch.py    # ENTSO-E data, profiles, capacities
│   ├── build_network.py # PyPSA network from config
│   ├── scenarios.py     # study blocks 1–6
│   └── plots.py
├── tests/               # data checks and sanity tests
└── results/             # CSV outputs and figures
```

## How to run (planned)

```
conda env create -f environment.yml
conda activate cwe-2030-pypsa
python src/data_fetch.py
python src/scenarios.py --block 1
```

## Known limitations

- NTC-based exchanges instead of flow-based market coupling
- No unit commitment or ramping constraints
- Simplified hydro and storage reservoirs
- 2030 inputs are scenario assumptions, not forecasts

## Author

Andrey Perevertaev, power system economist and market modeller · [LinkedIn](https://www.linkedin.com/in/aperever/)

## License

MIT
