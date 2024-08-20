import json
from backend.node.genvm.icontract import IContract
from backend.node.genvm.equivalence_principle import EquivalencePrinciple

class LlmErc721(IContract):
    def __init__(self, name: str, symbol: str, contract_address: str):
        # Initialize ERC721 contract with name and symbol
        self._name = name
        self._symbol = symbol
        self._contract_address = contract_address  # The address of the contract/game system
        
        # Maps token IDs to owners
        self._owners = {}
        # Maps owners to token balances
        self._balances = {}
        # Maps token approvals
        self._token_approvals = {}
        # Maps operator approvals
        self._operator_approvals = {}
        
        # Initialize the token for the game (e.g., Token ID 1)
        token_id = 1
        self._owners[token_id] = self._contract_address  # The game/system owns the token initially
        self._balances[self._contract_address] = 1  # System owns one NFT

    async def safe_transfer(self, from_address: str, to_address: str, token_id: int) -> None:
        prompt = f"""
        You keep track of the ownership of non-fungible tokens (NFTs) between users.
        The current ownership of all NFTs in JSON format is:
        {json.dumps(self._owners)}
        The balances for each user are:
        {json.dumps(self._balances)}
        The transaction to compute is: {{
            sender: "{from_address}",
            recipient: "{to_address}",
            token_id: {token_id}
        }}
        For every transaction, validate that the sender owns the token and that the recipient is valid.
        If any transaction is invalid, it shouldn't be processed.
        Update the ownership and balances based on valid transactions only.
        Given the current ownership and balances in JSON format and the transaction provided,
        please provide the result of your calculation with the following format:
        {{
            "transaction_success": bool,          // Whether the transaction was successful
            "transaction_error": str,             // Empty if transaction is successful
            "updated_owners": object<int, str>,   // Updated owners after the transaction
            "updated_balances": object<str, int>  // Updated balances after the transaction
        }}
        It is mandatory that you respond only using the JSON format above,
        nothing else. Don't include any other words or characters,
        your output must be only JSON without any formatting prefix or suffix.
        This result should be perfectly parseable by a JSON parser without errors.
        """
        print(prompt)
        final_result = {}
        async with EquivalencePrinciple(
            result=final_result,
            principle="""The new balance of the sender should have decreased
            by 1 and the new balance of the receiver should have increased by 1.
            The owner of the token should be updated accordingly.""",
            comparative=True,
        ) as eq:
            result = await eq.call_llm(prompt)
            result_clean = result.replace("True", "true").replace("False", "false")
            eq.set(result_clean)
        
        print("final_result: ", final_result)
        print("final_result[output]: ", final_result["output"])
        result_json = json.loads(final_result["output"])
        
        # Update balances and ownerships based on the response
        if result_json["transaction_success"]:
            self._owners = result_json["updated_owners"]
            self._balances = result_json["updated_balances"]

    def balance_of(self, owner: str) -> int:
        if owner == "":
            raise Exception("Invalid owner address")
        return self._balances.get(owner, 0)

    def owner_of(self, token_id: int) -> str:
        owner = self._owners.get(token_id)
        if owner is None:
            raise Exception("Token ID does not exist")
        return owner

    def name(self) -> str:
        return self._name

    def symbol(self) -> str:
        return self._symbol

    def approve(self, to_address: str, token_id: int) -> None:
        owner = self.owner_of(token_id)
        if to_address == owner:
            raise Exception("Approval to current owner not allowed")
        self._token_approvals[token_id] = to_address

    def get_approved(self, token_id: int) -> str:
        return self._token_approvals.get(token_id, "")

    def is_approved_for_all(self, owner: str, operator: str) -> bool:
        return self._operator_approvals.get(owner, {}).get(operator, False)

    def set_approval_for_all(self, owner: str, operator: str, approved: bool) -> None:
        if owner not in self._operator_approvals:
            self._operator_approvals[owner] = {}
        self._operator_approvals[owner][operator] = approved

    async def player_wins(self, player_address: str) -> None:
        # Player wins the game, transfer the NFT to the player
        token_id = 1  # The token that represents winning the game
        from_address = self._contract_address  # The system's address (the current owner of the token)
        print(f"Transferring NFT token ID {token_id} from {from_address} to {player_address}...")
        # Initiate the transfer
        await self.safe_transfer(from_address, player_address, token_id)
        print(f"NFT token ID {token_id} successfully transferred to {player_address}!")
