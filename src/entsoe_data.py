"""Download and cache ENTSO-E Transparency Platform data.

Every query is saved to data/raw/ as CSV. The next call reads the file
instead of calling the API again, so each dataset is downloaded only once.
"""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
TZ = "Europe/Berlin"


def get_client():
    """Create an API client with the token from the project's .env file."""
    load_dotenv(PROJECT_ROOT / ".env")
    return EntsoePandasClient(api_key=os.environ["ENTSOE_API_KEY"])


def year_bounds(year):
    start = pd.Timestamp(f"{year}-01-01", tz=TZ)
    end = pd.Timestamp(f"{year + 1}-01-01", tz=TZ)
    return start, end


def _read_cached(path):
    df = pd.read_csv(path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(TZ)
    return df


def _cached(name, fetch):
    """Return cached data if present, otherwise fetch it and save it."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{name}.csv"
    if path.exists():
        return _read_cached(path)
    data = fetch()
    if isinstance(data, pd.Series):
        data = data.to_frame(name="value")
    data.to_csv(path)
    return data


def _clip(df, start, end):
    """Keep only [start, end): entsoe-py can return extra hours at both edges."""
    return df[(df.index >= start) & (df.index < end)]


def day_ahead_prices(client, zone, year):
    """Hourly day-ahead prices in EUR/MWh (Series)."""
    start, end = year_bounds(year)
    df = _cached(
        f"prices_{zone}_{year}",
        lambda: client.query_day_ahead_prices(zone, start=start, end=end),
    )
    s = _clip(df, start, end).iloc[:, 0].rename(zone)
    return s.resample("h").mean()


def load(client, zone, year):
    """Hourly actual load in MW (Series)."""
    start, end = year_bounds(year)
    df = _cached(
        f"load_{zone}_{year}",
        lambda: client.query_load(zone, start=start, end=end),
    )
    s = _clip(df, start, end).iloc[:, 0].rename(zone)
    return s.resample("h").mean()


def generation(client, zone, year):
    """Hourly actual generation by technology in MW (DataFrame).

    Downloaded month by month: each month is cached on its own, progress is
    printed, and a failed month can simply be retried.
    """
    # Reuse a full-year file if an earlier version of this code saved one.
    full_year = RAW_DIR / f"generation_{zone}_{year}.csv"
    if full_year.exists():
        start, end = year_bounds(year)
        return _clip(_read_cached(full_year), start, end).resample("h").mean()

    months = []
    for m in range(1, 13):
        m_start = pd.Timestamp(f"{year}-{m:02d}-01", tz=TZ)
        m_end = m_start + pd.offsets.MonthBegin(1)

        def fetch(s=m_start, e=m_end):
            df = client.query_generation(zone, start=s, end=e, psr_type=None)
            # Some zones return two column levels: (technology, Aggregated/Consumption).
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs("Actual Aggregated", axis=1, level=1)
            return df

        print(f"Generation {zone} {year}-{m:02d} ...", end=" ", flush=True)
        df = _cached(f"generation_{zone}_{year}_{m:02d}", fetch)
        months.append(_clip(df, m_start, m_end).resample("h").mean())
        print("done")
    return pd.concat(months).sort_index()
