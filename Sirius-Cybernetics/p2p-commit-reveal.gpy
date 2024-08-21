"""
Private P2P contracts with commit/reveal.

"""
import json
import hashlib
from backend.node.genvm.icontract import IContract
# from backend.node.genvm.equivalence_principle import call_llm_with_principle

class CommitRevealContract(IContract):
    def __init__(self):
        self.committed_hash = None
        self.revealed_value = None
        self.reveal_secret = None

    async def commit(self, value: str, secret: str) -> None:
        """
        Commit to a value with a secret.
        """
        # Generate hash of the value and secret
        value_secret_combined = value + secret
        self.committed_hash = hashlib.sha256(value_secret_combined.encode()).hexdigest()

    async def reveal(self, value: str, secret: str) -> bool:
        """
        Reveal the value and secret, and validate the commitment.
        """
        if not self.committed_hash:
            raise ValueError("No value has been committed yet.")
        
        # Recreate the hash from the revealed value and secret
        value_secret_combined = value + secret
        hash_to_check = hashlib.sha256(value_secret_combined.encode()).hexdigest()

        # Check if the hash matches the committed hash
        if hash_to_check == self.committed_hash:
            self.revealed_value = value
            self.reveal_secret = secret
            return True
        else:
            return False

    def get_revealed_value(self) -> str:
        """
        Get the revealed value if available.
        """
        if self.revealed_value:
            return self.revealed_value
        else:
            raise ValueError("No value has been revealed yet.")

    def get_reveal_secret(self) -> str:
        """
        Get the reveal secret if available.
        """
        if self.reveal_secret:
            return self.reveal_secret
        else:
            raise ValueError("No secret has been revealed yet.")
