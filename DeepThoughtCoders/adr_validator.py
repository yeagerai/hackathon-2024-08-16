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
        print("Validating ADR...")

        # 1. Check the template structure of the ADR
        if not self._check_template(adr):
            print("ADR is not following the template, and thus is invalid...")
            return

        # 2. Check hierarchical validity (i.e., correct structure and section order)
        hierarchical_result = await self._hierarchical(adr)
        if not hierarchical_result["valid"]:
            print("ADR failed hierarchical validity check:", hierarchical_result["reason"])
            return

        # 3. Ensure logical consistency (no contradictions within the ADR or with past ADRs)
        logical_result = await self._logical(adr)
        if not logical_result["valid"]:
            print("ADR failed logical consistency check:", logical_result["reason"])
            return

        # 4. Check for implicit decisions (ensure all decisions are explicit)
        implicit_result = await self._implicit(adr)
        if not implicit_result["valid"]:
            print("ADR has implicit decisions:", implicit_result["reason"])
            return

        # 5. Validate that the problem and context are clearly explained and relevant
        clear_problem_result = await self._clear_problem(adr)
        if not clear_problem_result["valid"]:
            print("ADR lacks a clear problem statement or relevant context:", clear_problem_result["reason"])
            return

        # 6. Check for valid alternative solutions (ensure the best solution is proposed)
        alternative_solutions_result = await self._valid_alternative_solutions(adr)
        if not alternative_solutions_result["valid"]:
            print("ADR does not consider or justify alternative solutions:", alternative_solutions_result["reason"])
            return

        # 7. Assess trade-offs and risks to the full system (ensure no negative impact on the overall system)
        full_system_risk_result = await self._full_system_risk(adr)
        if not full_system_risk_result["valid"]:
            print("ADR poses risks to the full system:", full_system_risk_result["reason"])
            return

        # 8. Check feasibility (ensure the solution is practical with available resources and technology)
        feasibility_result = await self._feasible(adr)
        if not feasibility_result["valid"]:
            print("ADR is not feasible:", feasibility_result["reason"])
            return

        # If all checks pass, proceed to update balances and add ADR
        if contract_runner.from_address not in self.balances:
            self.balances[contract_runner.from_address] = 0

        # Example of adding reward logic here based on evaluation
        output = await self._evaluate_adr_reward(adr, category_name)  # Hypothetical reward evaluation function
        self.balances[contract_runner.from_address] += output["reward"]
        self.arch_categories[category_name]["ADRs"].append(adr)

        print("ADR successfully validated and added.")

    def _check_template(self, adr: str) -> bool:
        adr = adr.replace("\r\n", "\n").replace("\r", "\n")
        pattern = r"^\# [^\n]+?\n+(- Status: (proposed|accepted|validated).+)\n+(- Deciders: [^\n]+)\n+(- Date: \d\d\d\d-\d\d-\d\d)\n+(\#\# Context and Problem Statement)\n+(\#\#\#\# Problem\n+(.|\n)*)+(\#\#\#\# Context\n+(.|\n)*)+(\#\# Decision Drivers+(.|\n)*)+(\#\# Considered Options+(.|\n)*)+(\#\# Decision Outcome+(.|\n)*)+(\#\#\# Consequences+(.|\n)*)+(\#\# Pros and Cons of the Options+(.|\n)*)+(\#\#\#(.|\n)*)+(\#\#\#\# Pros+(.|\n)*)+(\#\#\#\# Cons+(.|\n)*)+(\#\#\#(.|\n)*)+(\#\#\#\# Pros+(.|\n)*)+(\#\#\#\# Cons+(.|\n)*)"
        compiled_pattern = re.compile(pattern, re.MULTILINE | re.DOTALL)
        result = bool(compiled_pattern.match(adr))
        print("Result of checking template structure: ", result)
        return result

    async def _hierarchical(self, adr:str, category:str) -> bool:
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
            eq_principle="The result['reward'] has to be exactly the same",
        )
        result_clean = result.replace("True", "true").replace("False", "false") # to make sure is valid python
        output = json.loads(result_clean)
        return output

    async def _logical(self, adr:str) -> bool:
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
            eq_principle="The result['reward'] has to be exactly the same",
        )
        result_clean = result.replace("True", "true").replace("False", "false") # to make sure is valid python
        output = json.loads(result_clean)
        return output

    async def _implicit(self, adr:str) -> bool:
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
            eq_principle="The result['reward'] has to be exactly the same",
        )
        result_clean = result.replace("True", "true").replace("False", "false") # to make sure is valid python
        output = json.loads(result_clean)
        return output

    async def _clear_problem(self, adr:str) -> bool:
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
            eq_principle="The result['reward'] has to be exactly the same",
        )
        result_clean = result.replace("True", "true").replace("False", "false") # to make sure is valid python
        output = json.loads(result_clean)
        return output

    async def _valid_alternative_solutions(self, adr:str) -> bool:
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
            eq_principle="The result['reward'] has to be exactly the same",
        )
        result_clean = result.replace("True", "true").replace("False", "false") # to make sure is valid python
        output = json.loads(result_clean)
        return output

    async def _full_system_risk(self, adr:str) -> bool: # mega prompt (maybe we need memory here)
        ...

    async def _feasible(self, adr:str) -> bool: # complex
        ...

    async def _evaluate_adr_reward(self, adr: str, category: str) -> object:
        prompt = f"""
        Here is a new valid ADR submitted by a user.

        {adr}

        You MUST decide of a REWARD (INTEGER) between 1 and {self.max_reward}. 
        Evaluate the reward based on the potential impact, importance, and writing quality of the candidate.

        Respond ONLY with the following format:
        
        {{
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
            eq_principle="The result['reward'] has to be exactly the same",
        )
        result_clean = result.replace("True", "true").replace("False", "false") # to make sure is valid python
        output = json.loads(result_clean)
        return output
