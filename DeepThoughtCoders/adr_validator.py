import json
import re
from backend.node.genvm.icontract import IContract
from backend.node.genvm.equivalence_principle import call_llm_with_principle


class ADRValidator(IContract):
    def __init__(self):
        self.owner = contract_runner.from_address
        self.arch_categories = {}
        self.balances = {}
        self.max_reward = 10

    def change_owner(self, new_owner: str):
        if contract_runner.from_address == self.owner:
            self.owner = new_owner

    def set_max_reward(self, new_max_reward: int):
        if contract_runner.from_address == self.owner:
            self.max_reward = new_max_reward

    def get_owner(self) -> str:
        return self.owner

    def get_categories(self) -> str:
        return {
            category: details["description"]
            for category, details in self.arch_categories.items()
        }

    def get_adrs_of_a_category(self, category_name: str) -> dict:
        if category_name in self.arch_categories:
            return self.arch_categories[category_name]["ADRs"]

    def get_balances(self) -> dict[str, int]:
        return self.balances

    def get_balance_of(self, address: str) -> int:
        return self.balances.get(address, 0)

    def add_category(self, category_name: str, category_description: str):
        if (
            contract_runner.from_address == self.owner
            and category_name not in self.arch_categories
        ):
            self.arch_categories[f"{category_name}"] = {
                "description": category_description,
                "ADRs": [],
            }

    async def validate_adr(self, adr: str, category_name: str) -> None:
        print("validate")
        # if not self._check_template(adr): return
        output = await self._evaluate_adr(adr, category_name)

        ## Improvement: would split checks more by concern
        if not output["accepted"]:
            return

        if contract_runner.from_address not in self.balances:
            self.balances[contract_runner.from_address] = 0

        self.balances[contract_runner.from_address] += output["reward"]
        self.arch_categories[category_name]["ADRs"].append(adr)

    def _check_template(self, adr: str) -> bool:
        adr = adr.replace("\r\n", "\n").replace("\r", "\n")
        pattern = r"^\# [^\n]+?\n+(- Status: (proposed|accepted|validated).+)\n+(- Deciders: [^\n]+)\n+(- Date: \d\d\d\d-\d\d-\d\d)\n+(\#\# Context and Problem Statement)\n+(\#\#\#\# Problem\n+(.|\n)*)+(\#\#\#\# Context\n+(.|\n)*)+(\#\# Decision Drivers+(.|\n)*)+(\#\# Considered Options+(.|\n)*)+(\#\# Decision Outcome+(.|\n)*)+(\#\#\# Consequences+(.|\n)*)+(\#\# Pros and Cons of the Options+(.|\n)*)+(\#\#\#(.|\n)*)+(\#\#\#\# Pros+(.|\n)*)+(\#\#\#\# Cons+(.|\n)*)+(\#\#\#(.|\n)*)+(\#\#\#\# Pros+(.|\n)*)+(\#\#\#\# Cons+(.|\n)*)"
        compiled_pattern = re.compile(pattern, re.MULTILINE | re.DOTALL)
        result = bool(compiled_pattern.match(adr))
        print("Result of checking template structure: ", result)
        return result

    async def _evaluate_adr(self, adr: str, category: str) -> object:
        print("Evaluating ADR...")
        valid_decisions = False
        prompt = f"""
        Here are some architecture decisions made in the past, and a new decision candidate.
        You must check past decisions for contradiction with the new candidate that would block this candidate from being added to ADRs.

        - Past decisions:
        {self.arch_categories[category]['ADRs']}

        - New decision candidate:
        {adr}

        You must decide if the new decision can be accepted or if it should be rejected.

        In case of rejection:
        - You MUST provide a REASON for the rejection.

        In case of acceptance:
        - The REASON should be an EMPTY STRING.
        - You MUST decide of a REWARD (INTEGER) between 1 and {self.max_reward}. Evaluate the reward based on the potential impact, importance, and writing quality of the candidate.

        Respond ONLY with the following format:
        {{
        "accepted": bool,
        "reasoning": str,
        "reward": int,
        }}
        It is mandatory that you respond only using the JSON format above,
        nothing else. Don't include any other words or characters,
        your output must be only JSON without any formatting prefix or suffix.
        This result should be perfectly parseable by a JSON parser without errors.
        """
        result = await call_llm_with_principle(
            prompt,
            eq_principle="The result['accepted'] has to be exactly the same",
        )
        result_clean = result.replace("True", "true").replace("False", "false")
        output = json.loads(result_clean)

        print(output)

        return output
