"""Generate synthetic clinical-supply data as JSON Lines files.

Entities: trial sites, patients (PII), shipments of drug kits, adverse-event reports.
A small share of shipments is deliberately dirty so the quality rules have work to do.

Usage:
    python -m data_generator.generate --patients 1000 --out data/raw --seed 42
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

COUNTRIES = ["CA", "US", "DE", "CH", "GB", "JP", "BR", "IN"]
TRIALS = ["TRIAL-ONC-101", "TRIAL-NEU-204", "TRIAL-IMM-310"]
SEVERITIES = ["mild", "moderate", "severe"]


def make_sites(fake: Faker, n: int) -> list[dict]:
    return [
        {
            "site_id": f"SITE-{i:04d}",
            "site_name": f"{fake.city()} Clinical Research Centre",
            "country": random.choice(COUNTRIES),
            "trial_id": random.choice(TRIALS),
            "activated_on": fake.date_between("-3y", "-1y").isoformat(),
        }
        for i in range(1, n + 1)
    ]


def make_patients(fake: Faker, n: int, sites: list[dict]) -> list[dict]:
    patients = []
    for i in range(1, n + 1):
        site = random.choice(sites)
        patients.append(
            {
                "patient_id": f"PT-{i:06d}",
                "site_id": site["site_id"],
                "trial_id": site["trial_id"],
                # PII / PHI columns - tagged and masked in Phase 5
                "full_name": fake.name(),
                "email": fake.email(),
                "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=85).isoformat(),
                "sex": random.choice(["F", "M"]),
                "enrolled_on": fake.date_between("-1y", "today").isoformat(),
            }
        )
    return patients


def make_shipments(fake: Faker, n: int, sites: list[dict], dirty_rate: float) -> list[dict]:
    shipments = []
    for i in range(1, n + 1):
        shipped = fake.date_between("-1y", "today")
        delivered = shipped + timedelta(days=random.randint(1, 10))
        record = {
            "shipment_id": f"SHP-{i:07d}",
            "site_id": random.choice(sites)["site_id"],
            "kit_quantity": random.randint(5, 200),
            "shipped_date": shipped.isoformat(),
            "delivered_date": delivered.isoformat() if delivered <= date.today() else None,
            "min_temp_c": round(random.uniform(1.0, 4.0), 1),
            "max_temp_c": round(random.uniform(5.0, 9.5), 1),
        }
        if random.random() < dirty_rate:
            defect = random.choice(["no_id", "bad_qty", "bad_dates", "no_temp"])
            if defect == "no_id":
                record["shipment_id"] = None
            elif defect == "bad_qty":
                record["kit_quantity"] = -random.randint(1, 20)
            elif defect == "bad_dates":
                record["delivered_date"] = (shipped - timedelta(days=3)).isoformat()
            else:
                record["max_temp_c"] = None
        shipments.append(record)
    return shipments


def make_adverse_events(fake: Faker, patients: list[dict], rate: float) -> list[dict]:
    events = []
    for p in patients:
        if random.random() < rate:
            events.append(
                {
                    "event_id": f"AE-{len(events) + 1:06d}",
                    "patient_id": p["patient_id"],
                    "trial_id": p["trial_id"],
                    "reported_on": fake.date_between("-1y", "today").isoformat(),
                    "severity": random.choices(SEVERITIES, weights=[70, 25, 5])[0],
                    "serious": random.random() < 0.08,
                }
            )
    return events


def write_jsonl(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--patients", type=int, default=1000)
    parser.add_argument("--sites", type=int, default=50)
    parser.add_argument("--shipments", type=int, default=5000)
    parser.add_argument("--dirty-rate", type=float, default=0.03)
    parser.add_argument("--ae-rate", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path("data/raw"))
    args = parser.parse_args()

    random.seed(args.seed)
    fake = Faker()
    Faker.seed(args.seed)

    sites = make_sites(fake, args.sites)
    patients = make_patients(fake, args.patients, sites)
    shipments = make_shipments(fake, args.shipments, sites, args.dirty_rate)
    events = make_adverse_events(fake, patients, args.ae_rate)

    for name, rows in [
        ("sites", sites),
        ("patients", patients),
        ("shipments", shipments),
        ("adverse_events", events),
    ]:
        write_jsonl(rows, args.out / name / f"{name}.jsonl")
        print(f"wrote {len(rows):>6} rows -> {args.out / name}")


if __name__ == "__main__":
    main()
