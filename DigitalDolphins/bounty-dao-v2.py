import json
from backend.node.genvm.icontract import IContract
from backend.node.genvm.equivalence_principle import call_llm_with_principle

# Custom exception classes for GenLayerDAO
class DAOException(Exception):
    """Base exception class for GenLayerDAO"""
    pass

class InsufficientTokensException(DAOException):
    """Exception raised when a user doesn't have enough tokens"""
    pass

class InvalidBountyException(DAOException):
    """Exception raised for invalid bounty operations"""
    pass

class VotingException(DAOException):
    """Exception raised for voting-related issues"""
    pass

class InvalidInputException(DAOException):
    """Exception raised for invalid input parameters"""
    pass

class Bounty:
    """
    Represents a bounty in the GenLayerDAO system.
    
    Attributes:
        id (int): Unique identifier for the bounty
        description (str): Detailed description of the bounty
        reward_description (str): Description of the reward for completing the bounty
        proposer (str): Address of the user who proposed the bounty
        votes_for (int): Number of votes in favor of the bounty
        votes_against (int): Number of votes against the bounty
        status (str): Current status of the bounty ("proposed", "active", or "completed")
        submissions (list): List of submissions for the bounty
        vote_snapshot (dict): Snapshot of token balances at proposal time
        has_voted (dict): Tracks which users have voted on the bounty
    """
    def __init__(self, id: int, description: str, reward_description: str, proposer: str):
        self.id = id
        self.description = description
        self.reward_description = reward_description
        self.proposer = proposer
        self.votes_for = 0
        self.votes_against = 0
        self.status = "proposed"  # Can be "proposed", "active", or "completed"
        self.submissions: list[dict[str, str | bool]] = []
        self.vote_snapshot: dict[str, int] = {}  # Snapshot of token balances at proposal time
        self.has_voted: dict[str, bool] = {}  # Track who has voted

class GenLayerDAO(IContract):
    """
    Implements the GenLayerDAO contract with bounty management and voting system.
    
    Attributes:
        total_supply (int): Total token supply of the DAO
        token_supply (int): Current available token supply
        balances (dict): Mapping of addresses to token balances
        bounties (dict): Mapping of bounty IDs to Bounty objects
        next_bounty_id (int): ID to be assigned to the next proposed bounty
        constitution (list): List of rules governing the DAO
    """
    def __init__(self):
        self.total_supply = 1000
        self.token_supply = self.total_supply
        self.balances: dict[str, int] = {}
        self.bounties: dict[int, Bounty] = {}
        self.next_bounty_id = 1

        # Define the constitution of the DAO
        self.constitution = [
            "This Constitution describes the decision-making framework for GenLayerDAO governance.",
            "The following process governs the rules and procedures by which GenLayerDAO may propose, vote on, and implement Bounty Programs.",
            "GenLayerDAO's purpose is to grow the GenLayer Blockchain by rewarding Bounty Program contributors with tokens.",
            "An address must hold at least one token to be a member of the DAO.",  
            "Only members of the GenLayerDAO can propose new Bounty Programs.",
            "Bounty programs must follow be in line with one of the following goals:",
            "- Increase Brand Awareness for the GenLayer Blockchain or one of the applications built on top of GenLayer.",
            "- Lead to Code Contributions to the GenLayer Repository on GitHub.",
            "- Lead to applications built on top of GenLayer.",
            "- Empower initiatives that help to build or enhance the community around GenLayer, such as meetups, hackathons, or online forums.",
            "If a Bounty program proposal does not help any of the listed goals, reject the proposal.",
            "Bounty programs must be unique. If a new bounty program proposal is the same as an existing proposed or active bounty, reject the proposal."
            "If a bounty program proposal meets the criteria, it is added to proposed bounties for a vote.",
            "A bounty program proposal has to be approved by a majority vote.",
            "The voting power of a member is proportional to the number of tokens a member holds.",
            "At least one-third of all votable tokens must participate in the voting process; otherwise, the proposal will be rejected",
            "A majority of those participating votable tokens must agree for the proposal to be accepted",        
            "Once a bounty program is approved, it is moved to the active bounty list",
            "Anyone can try to claim the reward of an active bounty, according to the rules of the bounty.",
            "A user does not have to be a member of the DAO or hold any DAO tokens to claim the bounty",
        ]

    async def propose_bounty(self, bounty_proposal: str) -> str:
        """
        Proposes a new bounty to the DAO.
        
        Args:
            bounty_proposal (str): Description of the proposed bounty
        
        Returns:
            str: Message indicating the result of the proposal
        
        Raises:
            InsufficientTokensException: If the proposer doesn't have any tokens
            DAOException: If the proposal is rejected
        """
        proposer = contract_runner.from_address
        if self.get_balance_of(proposer) == 0:
            raise InsufficientTokensException("Only DAO members can propose bounties.")

        # Prepare prompt for LLM evaluation
        prompt = f"""
You are GenLayerDAO.

GenLayerDAO has a constitution:
{json.dumps(self.constitution)}

A user with address "{proposer}" has proposed a new bounty:
Description: {bounty_proposal}

Evaluate if this bounty proposal adheres to the constitution.
Respond with the following JSON format:
{{
"reasoning": str,
"proposal_accepted": bool
}}

It is mandatory that you respond only using the JSON format above,
nothing else. Don't include any other words or characters,
your output must be only JSON without any formatting prefix or suffix.
This result should be perfectly parseable by a JSON parser without errors.
"""

        result = await call_llm_with_principle(prompt, eq_principle="proposal_accepted has to match exactly.")
        output = self._get_decode_json_resilient(result)

        if output["proposal_accepted"]:
            # Refine the bounty proposal
            refined_description, refined_reward = await self.refine_bounty_details(bounty_proposal)        

            bounty = Bounty(self.next_bounty_id, refined_description, refined_reward, proposer)
            bounty.vote_snapshot = self.balances.copy()
            self.bounties[self.next_bounty_id] = bounty

            # Automatically cast a vote for the proposer
            self._cast_vote(bounty, proposer, True)
            
            self.next_bounty_id += 1
            return f"Bounty proposed successfully and automatically voted for. Bounty ID: {bounty.id}"
        else:
            raise DAOException(f"Bounty proposal rejected. Reason: {output['reasoning']}")

    def vote_on_bounty(self, bounty_id: int, vote: bool) -> str:
        """
        Casts a vote on a proposed bounty.
        
        Args:
            bounty_id (int): ID of the bounty to vote on
            vote (bool): True for a positive vote, False for a negative vote
        
        Returns:
            str: Message indicating the result of the vote
        
        Raises:
            InvalidBountyException: If the bounty ID is invalid
            VotingException: If voting conditions are not met
        """
        voter = contract_runner.from_address
        if bounty_id not in self.bounties:
            raise InvalidBountyException("Invalid bounty ID.")

        bounty = self.bounties[bounty_id]
        if bounty.status != "proposed":
            raise VotingException("This bounty is not in the voting phase.")

        if voter not in bounty.vote_snapshot:
            raise VotingException("You didn't hold any tokens when this bounty was proposed, so you can't vote on it.")

        if bounty.has_voted.get(voter, False):
            raise VotingException("You have already voted on this bounty.")

        self._cast_vote(bounty, voter, vote)

        return self._check_voting_result(bounty)

    def _cast_vote(self, bounty: Bounty, voter: str, vote: bool):
        """
        Internal method to cast a vote on a bounty.
        
        Args:
            bounty (Bounty): The bounty being voted on
            voter (str): Address of the voter
            vote (bool): True for a positive vote, False for a negative vote
        """
        voter_balance = bounty.vote_snapshot[voter]

        if vote:
            bounty.votes_for += voter_balance
        else:
            bounty.votes_against += voter_balance

        bounty.has_voted[voter] = True

    def _check_voting_result(self, bounty: Bounty) -> str:
        """
        Checks the voting result for a bounty and updates its status if necessary.
        
        Args:
            bounty (Bounty): The bounty to check
        
        Returns:
            str: Message indicating the result of the check
        """
        total_votes = bounty.votes_for + bounty.votes_against
        if total_votes >= self.total_supply // 3:
            if bounty.votes_for > bounty.votes_against:
                bounty.status = "active"
                return f"Bounty {bounty.id} has been approved and is now active."
            else:
                del self.bounties[bounty.id]
                return f"Bounty {bounty.id} has been rejected and removed."

        return f"Vote recorded for bounty {bounty.id}."

    async def refine_bounty_details(self, bounty_proposal: str) -> tuple[str, str]:
        """
        Refines the bounty proposal using an LLM.
        
        Args:
            bounty_proposal (str): Original bounty proposal
        
        Returns:
            tuple: Refined description and reward description
        """
        prompt = f"""
You are an LLM helping to refine and standardize bounty proposals for GenLayerDAO. 
The original bounty proposal is: "{bounty_proposal}"

Please improve and structure this proposal by:
1. Separating the description and reward information.
2. Ensuring the description is clear, concise, and specifies concrete deliverables or success criteria.
3. Aligning it with GenLayerDAO's goals (increasing brand awareness, code contributions, application development, or community building).
4. Adding any relevant technical details or requirements.
5. Clarifying and standardizing the reward description, ensuring it's fair and motivating.

Provide the refined bounty details in the following JSON format:
{{
"refined_description": str,
"refined_reward": str
}}

The refined description should be a single, well-formatted paragraph.
The refined reward should be clear and specific, potentially including conditions or tiers if appropriate.

It is mandatory that you respond only using the JSON format above,
nothing else. Don't include any other words or characters,
your output must be only JSON without any formatting prefix or suffix.
This result should be perfectly parseable by a JSON parser without errors.
"""

        result = await call_llm_with_principle(prompt, eq_principle="The refined details should capture the essence of the original proposal.", comparative=False)
        print(result)
        output = self._get_decode_json_resilient(result)
        return output["refined_description"], output["refined_reward"]

    async def compute_reward(self, bounty_id: int, submission: str) -> int:
        """
        Computes the reward for a bounty submission using an LLM.
        
        Args:
            bounty_id (int): ID of the bounty
            submission (str): Submitted work for the bounty
        
        Returns:
            int: Computed reward amount
        
        Raises:
            InvalidBountyException: If the bounty ID is invalid
        """
        if bounty_id not in self.bounties:
            raise InvalidBountyException("Invalid bounty ID")

        bounty = self.bounties[bounty_id]
        prompt = f"""
You are the GenLayerDAO reward calculator. Your task is to determine the appropriate reward for a bounty submission based on the bounty description, reward description, and the actual submission.

Bounty Description: {bounty.description}
Reward Description: {bounty.reward_description}
Submission: {submission}

Please evaluate the submission against the bounty requirements and determine the appropriate reward. Consider factors such as completeness, quality, and impact of the submission.

Respond with the following JSON format:
{{
"reasoning": str,
"reward_amount": int
}}

The reward_amount should be a whole number of tokens, not exceeding the total supply of {self.total_supply}.

It is mandatory that you respond only using the JSON format above,
nothing else. Don't include any other words or characters,
your output must be only JSON without any formatting prefix or suffix.
This result should be perfectly parseable by a JSON parser without errors.
"""

        result = await call_llm_with_principle(prompt, eq_principle="The proposed reward should match exactly.")
        output = self._get_decode_json_resilient(result)
        return min(output["reward_amount"], self.total_supply)  # Ensure reward doesn't exceed total supply

    async def claim_bounty(self, bounty_id: int, submission: str) -> str:
        """
        Processes a claim for a bounty reward.
        
        Args:
            bounty_id (int): ID of the bounty being claimed
            submission (str): Submitted work for the bounty
        
        Returns:
            str: Message indicating the result of the claim
        
        Raises:
            InvalidBountyException: If the bounty ID is invalid or the bounty is not active
            InsufficientTokensException: If there are not enough tokens to pay the reward
            DAOException: If the submission is rejected
        """
        submitter = contract_runner.from_address
        if bounty_id not in self.bounties:
            raise InvalidBountyException("Invalid bounty ID.")

        bounty = self.bounties[bounty_id]
        if bounty.status != "active":
            raise InvalidBountyException("This bounty is not active.")
        
        if bounty.status == "completed":
            raise InvalidBountyException("This bounty has already been completed.")

        prompt = f"""
You are GenLayerDAO.

A submission has been made for bounty {bounty_id}:
Description: {bounty.description}
Reward: {bounty.reward_description}
Submission: {submission}

Evaluate if this submission satisfactorily completes the bounty.
Respond with the following JSON format:
{{
"reasoning": str,
"submission_accepted": bool
}}

It is mandatory that you respond only using the JSON format above,
nothing else. Don't include any other words or characters,
your output must be only JSON without any formatting prefix or suffix.
This result should be perfectly parseable by a JSON parser without errors.
"""

        result = await call_llm_with_principle(prompt, eq_principle="submission_accepted has to match exactly.")
        output = self._get_decode_json_resilient(result)

        if output["submission_accepted"]:
            reward_amount = await self.compute_reward(bounty_id, submission)
            if self.token_supply < reward_amount:
                raise InsufficientTokensException(f"Submission accepted, but insufficient tokens to pay reward. Current supply: {self.token_supply}")
            
            self._send_tokens(reward_amount, submitter)
            bounty.status = "completed"
            bounty.submissions.append({"submitter": submitter, "submission": submission, "accepted": True, "reward": reward_amount})
            return f"Bounty {bounty_id} completed. Reward of {reward_amount} tokens sent to {submitter}."
        else:
            bounty.submissions.append({"submitter": submitter, "submission": submission, "accepted": False})
            raise DAOException(f"Submission for bounty {bounty_id} rejected. Reason: {output['reasoning']}")


    def buy_tokens(self, amount: int):
        """
        Purchase tokens for the caller.

        Args:
            amount (int): The number of tokens to buy.

        Raises:
            InvalidInputException: If the amount is not a positive integer.
        """
        if amount <= 0:
            raise InvalidInputException("Amount must be a positive integer.")
        self._send_tokens(amount, contract_runner.from_address)

    def _send_tokens(self, amount: int, holder: str):
        """
        Internal method to send tokens to a holder.

        Args:
            amount (int): The number of tokens to send.
            holder (str): The address of the token recipient.

        Raises:
            InvalidInputException: If the amount is not a positive integer.
            InsufficientTokensException: If there are not enough tokens in the supply.
        """
        if amount <= 0:
            raise InvalidInputException("Amount must be a positive integer.")
        if self.token_supply < amount:
            raise InsufficientTokensException("Insufficient token supply")
        self.balances[holder] = self.balances.get(holder, 0) + amount
        self.token_supply -= amount

    def get_balances(self) -> dict[str, int]:
        """
        Get the token balances of all holders.

        Returns:
            dict[str, int]: A dictionary mapping addresses to token balances.
        """
        return self.balances

    def get_balance_of(self, address: str) -> int:
        """
        Get the token balance of a specific address.

        Args:
            address (str): The address to check the balance for.

        Returns:
            int: The token balance of the address.
        """
        return self.balances.get(address, 0)

    def get_bounties(self) -> dict[int, dict]:
        """
        Get all bounties in the system.

        Returns:
            dict[int, dict]: A dictionary mapping bounty IDs to bounty details.
        """
        return {id: bounty.__dict__ for id, bounty in self.bounties.items()}

    def get_bounty(self, bounty_id: int) -> dict:
        """
        Get details of a specific bounty.

        Args:
            bounty_id (int): The ID of the bounty to retrieve.

        Returns:
            dict: The details of the specified bounty.

        Raises:
            InvalidBountyException: If the bounty ID is invalid.
        """
        if bounty_id in self.bounties:
            return self.bounties[bounty_id].__dict__
        raise InvalidBountyException("Invalid bounty ID")

    def _get_decode_json_resilient(self, s: str) -> dict:
        """
        Decode a JSON string in a resilient manner.

        Args:
            s (str): The JSON string to decode.

        Returns:
            dict: The decoded JSON object.
        """
        # Clean the string and replace boolean literals
        clean = self._get_extract_json_from_string(s).replace("True", "true").replace("False", "false")
        return json.loads(clean)

    def _get_extract_json_from_string(self, s: str) -> str:
        """
        Extract a JSON object from a string.

        Args:
            s (str): The string potentially containing a JSON object.

        Returns:
            str: The extracted JSON string, or an empty string if no valid JSON is found.
        """
        start_index = s.find('{')
        end_index = s.rfind('}')
        if start_index != -1 and end_index != -1 and start_index < end_index:
            return s[start_index:end_index + 1]
        else:
            return ""