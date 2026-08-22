import fastf1
from pathlib import Path

fastf1.Cache.enable_cache(Path("f1cache"))
session = fastf1.get_session(2026, "Chinese Grand Prix", "R")
session.load(telemetry=False, weather=False, messages=False)
print(session.results.head())