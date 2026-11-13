"""PII utilities used before data leaves the restricted zone.

Pseudonymisation keeps records joinable (same input -> same token) without exposing the
original value. The salt must come from a secret store (Key Vault / Unity Catalog secret),
never from code.
"""

from __future__ import annotations

import hashlib
import hmac


def pseudonymise(value: str | None, salt: str) -> str | None:
    """Return a stable, non-reversible token for a PII value (HMAC-SHA256)."""
    if value is None:
        return None
    if not salt:
        raise ValueError("A non-empty salt is required; load it from a secret store.")
    normalised = value.strip().lower()
    return hmac.new(salt.encode(), normalised.encode(), hashlib.sha256).hexdigest()


def mask_email(email: str | None) -> str | None:
    """Mask an email for display: 'jane.doe@site.org' -> 'j*******@site.org'."""
    if email is None or "@" not in email:
        return email
    local, domain = email.split("@", 1)
    if not local:
        return email
    return f"{local[0]}{'*' * (len(local) - 1)}@{domain}"
