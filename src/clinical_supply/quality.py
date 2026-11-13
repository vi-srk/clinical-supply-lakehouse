"""Lightweight record-level quality rules.

Phase 1 keeps these as plain Python so they are easy to unit test. In Phase 3 the same
rules become Lakeflow pipeline expectations, and bad rows go to a quarantine table instead
of failing the run.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import date

Rule = Callable[[dict], bool]

# Investigational drug kits are usually stored at 2-8 C (cold chain).
COLD_CHAIN_MIN_C = 2.0
COLD_CHAIN_MAX_C = 8.0

SHIPMENT_RULES: dict[str, Rule] = {
    "shipment_id_present": lambda r: bool(r.get("shipment_id")),
    "quantity_positive": lambda r: isinstance(r.get("kit_quantity"), int) and r["kit_quantity"] > 0,
    "dates_in_order": lambda r: (
        r.get("delivered_date") is None
        or (
            isinstance(r.get("shipped_date"), date)
            and r["delivered_date"] >= r["shipped_date"]
        )
    ),
    "temperature_recorded": lambda r: r.get("max_temp_c") is not None,
}


@dataclass
class QualityResult:
    valid: list[dict] = field(default_factory=list)
    quarantined: list[dict] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        total = len(self.valid) + len(self.quarantined)
        return 1.0 if total == 0 else len(self.valid) / total


def apply_rules(records: Iterable[dict], rules: dict[str, Rule]) -> QualityResult:
    """Split records into valid and quarantined, tagging each failure with the rules broken."""
    result = QualityResult()
    for record in records:
        failed = [name for name, rule in rules.items() if not rule(record)]
        if failed:
            result.quarantined.append({**record, "_failed_rules": failed})
        else:
            result.valid.append(record)
    return result


def is_temperature_excursion(record: dict) -> bool:
    """True when a shipment left the 2-8 C cold-chain range (a business flag, not a defect)."""
    low, high = record.get("min_temp_c"), record.get("max_temp_c")
    if low is None or high is None:
        return False
    return low < COLD_CHAIN_MIN_C or high > COLD_CHAIN_MAX_C
