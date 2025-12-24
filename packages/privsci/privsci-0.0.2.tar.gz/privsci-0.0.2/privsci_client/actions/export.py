import requests
from . import load_config

API_BASE = load_config()['base_url']

def export(*, org_name, api_key, leaf_index, old_sth):
    old_size = old_sth["tree_size"]

    payload = {
        "org_name" : org_name,
        "leaf_index": leaf_index,
        "old_size": old_size
    }

    resp = requests.post(
        f"{API_BASE}/action/api/export",
        json=payload,
        headers={"X-API-Key": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    return data