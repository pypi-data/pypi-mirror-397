from .helpers.registry import get_handler
from .helpers.verifier import Verifier
import hashlib

def verify_inclusion(salt, structure, action=None, *, domain, representation, proof, root):
    handler = get_handler(domain, representation)
    result = handler(structure)

    combined_input = f"{salt}:{result["canonical"]}"
    hash_value = hashlib.sha256(combined_input.encode('utf-8')).hexdigest()

    if action:
        combined_data = f"{hash_value}:{action}"
        action_commitment = hashlib.sha256(combined_data.encode('utf-8')).hexdigest()
    else: 
        action_commitment = hash_value

    verifier = Verifier()
    is_included = verifier.verify_inclusion(action_commitment, proof, root)

    return is_included

def verify_consistency(old_sth, new_sth, proof):
    verifier = Verifier()
    is_consistent = verifier.verify_consistency(old_sth, new_sth, proof)
    
    return is_consistent