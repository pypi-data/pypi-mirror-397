from .helpers.registry import get_handler
import requests
import hashlib
from . import load_config

API_BASE = load_config()['base_url']

def sign(salt, structure, *, org_name, api_key, domain, representation, action):
    handler = get_handler(domain, representation)
    result = handler(structure)

    canonical = result["canonical"]
    combined_input = f"{salt}:{canonical}"
    hash_value = hashlib.sha256(combined_input.encode('utf-8')).hexdigest()

    payload = {
        "org_name": org_name,
        "hash_value": hash_value,
        "domain": result["domain"],
        "representation_type": result["representation_type"],
        "canonical_package": result["canonical_package"],
        "canonical_package_version": result["canonical_package_version"],
        "action": action
    }

    resp = requests.post(
        f"{API_BASE}/action/api/sign",
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
        "action": action,
        "receipt": data["receipt"]
    }