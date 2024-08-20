import json
from backend.node.genvm.icontract import IContract
from backend.node.genvm.equivalence_principle import call_llm_with_principle


class ConstitutionalDAO(IContract):
    """
    A Constitutional DAO that uses AI to interpret and execute motions.
    This DAO maintains a state and can update it based on user-submitted motions.
    """

    def __init__(self):
        """
        Initialize the ConstitutionalDAO with a basic constitution.
        """
        self.state = json.dumps({
            "constitution": [
                "1. Anyone can become a member of the DAO",
                "2. The constitution of the DAO can be updated by a unanimous vote"
            ]
        })

    async def execute_motion(self, motion: str) -> None:
        """
        Execute a motion proposed by a user.

        This method interprets the motion using an AI model and updates the DAO state accordingly.

        Args:
            motion (str): The motion proposed by a user.

        Returns:
            None
        """
        # Prepare the prompt for the language model
        prompt = f"""
You are a constitutional DAO

Your state is as follows:
{self.state}

User with the address "{contract_runner.from_address}"
has made the following motion:
{motion}

Decide how to proceed
Respond with the following JSON format:
{{
"reasoning": str,          // Your reasoning
"updated_state": any,      // The new state of the DAO - can be any format
}}

It is mandatory that you respond only using the JSON format above,
nothing else. Don't include any other words or characters,
your output must be only JSON without any formatting prefix or suffix.
This result should be perfectly parseable by a JSON parser without errors.
        """

        # Call the language model with the equivalence principle
        result = await call_llm_with_principle(
            prompt,
            eq_principle="The updated state has to be essentially equivalent",
        )

        # Clean up the result and parse it as JSON
        result_clean = result.replace("True", "true").replace("False", "false")
        output = json.loads(result_clean)

        # Update the DAO state
        self.state = json.dumps(output["updated_state"])

    def get_state(self) -> str:
        """
        Get the current state of the DAO.

        Returns:
            str: The current state of the DAO as a JSON string.
        """
        return self.state