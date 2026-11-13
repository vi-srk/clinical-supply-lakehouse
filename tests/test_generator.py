import random

from faker import Faker

from data_generator.generate import make_patients, make_shipments, make_sites


def setup_module():
    random.seed(1)
    Faker.seed(1)


def test_generated_entities_link_together():
    fake = Faker()
    sites = make_sites(fake, 5)
    patients = make_patients(fake, 20, sites)
    site_ids = {s["site_id"] for s in sites}
    assert len(patients) == 20
    assert all(p["site_id"] in site_ids for p in patients)


def test_dirty_rate_zero_gives_clean_shipments():
    fake = Faker()
    sites = make_sites(fake, 3)
    shipments = make_shipments(fake, 200, sites, dirty_rate=0.0)
    assert all(s["shipment_id"] and s["kit_quantity"] > 0 for s in shipments)
