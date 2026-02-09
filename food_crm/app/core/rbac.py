from fastapi import HTTPException

ROLE_PERMS: dict[str, set[str]] = {
    "owner": {"*"},
    "admin": {
        "companies:*", "contacts:*", "items:*", "pricelists:*",
        "quotes:*", "po:*", "emails:*", "deals:*", "activities:*",
    },
    "sales": {
        "companies:read", "contacts:*", "deals:*", "activities:*",
        "quotes:*", "emails:*",
    },
    "ops": {
        "companies:read", "contacts:read", "items:*", "pricelists:*",
        "po:*", "emails:send",
    },
    "viewer": {
        "companies:read", "contacts:read", "items:read",
        "pricelists:read", "quotes:read", "po:read",
    },
}


def require_perm(role: str, perm: str):
    perms = ROLE_PERMS.get(role, set())
    if "*" in perms:
        return
    if perm in perms:
        return
    prefix = perm.split(":")[0] + ":*"
    if prefix in perms:
        return
    raise HTTPException(status_code=403, detail="Forbidden")
