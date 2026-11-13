import pytest

from clinical_supply.pii import mask_email, pseudonymise


def test_pseudonymise_is_stable_and_normalised():
    assert pseudonymise("Jane@Site.org ", "s3cret") == pseudonymise("jane@site.org", "s3cret")


def test_pseudonymise_depends_on_salt():
    assert pseudonymise("jane@site.org", "a") != pseudonymise("jane@site.org", "b")


def test_pseudonymise_hides_original_value():
    token = pseudonymise("jane@site.org", "s3cret")
    assert "jane" not in token
    assert len(token) == 64


def test_pseudonymise_passes_through_none():
    assert pseudonymise(None, "s3cret") is None


def test_pseudonymise_requires_salt():
    with pytest.raises(ValueError):
        pseudonymise("jane@site.org", "")


@pytest.mark.parametrize(
    ("email", "expected"),
    [
        ("jane.doe@site.org", "j*******@site.org"),
        ("a@x.com", "a@x.com"),
        ("not-an-email", "not-an-email"),
        (None, None),
    ],
)
def test_mask_email(email, expected):
    assert mask_email(email) == expected
