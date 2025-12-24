from .helpers.registry import get_handler
import requests
from . import load_config

API_BASE = load_config()['base_url']

def create(structure, *, org_name, api_key, domain, representation):
    handler = get_handler(domain, representation)
    result = handler(structure)

    payload = {
        "org_name" : org_name,
        "hash_value": result["hash_value"],
        "domain": result["domain"],
        "representation_type": result["representation_type"],
        "canonical_package": result["canonical_package"],
        "canonical_package_version": result["canonical_package_version"]
    }

    print(f"{API_BASE}/api/create")

    resp = requests.post(
        f"{API_BASE}/action/api/create",
        json=payload,
        headers={"X-API-Key": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    return {
        "salt": result["salt"],
        "raw_structure": structure, 
        "can_structure": result["canonical"],
        "receipt": data["receipt"]
    }