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

        # 2. Check that there is only one explicit decision being made in the ADR
        only_one_decision = await self._only_one_explicit_decision(adr)
        if not only_one_decision["valid"]:
            print("ADR has either implicit decisions or more than one explicit decision:", only_one_decision["reason"])
            return

        # 3. Check hierarchical validity (i.e., correct structure and section order)
        hierarchical_result = await self._hierarchical(adr)
        if not hierarchical_result["valid"]:
            print("ADR failed hierarchical validity check:", hierarchical_result["reason"])
            return

        # 4. Validate that the problem and context are clearly explained and relevant
        clear_problem_result = await self._clear_problem(adr)
        if not clear_problem_result["valid"]:
            print("ADR lacks a clear problem statement or relevant context:", clear_problem_result["reason"])
            return

        # 5. Validate that the decision drivers are clearly explained and relevant
        clear_decision_drivers = await self._clear_decision_drivers(adr)
        if not clear_decision_drivers["valid"]:
            print("ADR lacks clear decision drivers:", clear_decision_drivers["reason"])
            return

        # 6. Ensure logical consistency (solution follows from problem and decision drivers)
        logical_result = await self._logical_solution(adr)
        if not logical_result["valid"]:
            print("ADR failed logical consistency check:", logical_result["reason"])
            return
        
        # 7. Check for valid alternative solutions (ensure the best solution is proposed)
        alternative_solutions_result = await self._no_better_alternative_solutions(adr)
        if not alternative_solutions_result["valid"]:
            print("ADR potentially has better alternative solutions:", alternative_solutions_result["reason"])
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

    async def _only_one_explicit_decision(self, adr:str) -> bool:
        prompt = f"""
        Evaluate the following Architecture Decision Record (ADR) to determine if it meets the following criteria:

        1. There is exactly ONE explicit decision stated in the ADR.
        2. There are NO other explicit decisions.
        3. There are NO implicit or hidden decisions present.

        The ADR:

        "{adr}"

        To determine if these criteria are met, consider the following:
        - Identify the explicit decision(s) stated in the ADR.
        - Check if there is more than one explicit decision.
        - Determine if there are any implicit or hidden decisions that are suggested or assumed but not clearly documented.

        Based on these considerations, provide an evaluation.

        The REASON can't be an EMPTY STRING.

        Respond ONLY with the following format:
        
        {{
        "reason": str,
        "valid": int,
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

    async def _hierarchical(self, adr:str, category:str) -> bool:
        prompt = f"""
        Here are the past decisions on for the {category}:
        {self.arch_categories[category]['ADRs']}

        Here is the graph of dependencies:
        {self.arch_categories[category]['deps-DAG']}

        The new decision candidate:
        {adr}

        We define an ADR candidate as hierarchicaly valid if and only if depends on the previous decisions defined by the user (+ the corresponding chain of deps) 
        and does not depend on the rest of decisions, and does not depend on decisions that have not been discussed yet.

        You must decide if the new decision candidate is hierarchicaly valid. Else has to be rejected.

        The REASON can't be an EMPTY STRING.

        Respond ONLY with the following format:
        {{
        "reason": str,
        "valid": bool,
        }}
        It is mandatory that you respond only using the JSON format above,
        nothing else. Don't include any other words or characters,
        your output must be only JSON without any formatting prefix or suffix.
        This result should be perfectly parseable by a JSON parser without errors.
        """
        result = await call_llm_with_principle(
            prompt,
            eq_principle="The result['valid'] has to be exactly the same",
        )
        result_clean = result.replace("True", "true").replace("False", "false") # to make sure is valid python
        output = json.loads(result_clean)
        return output

    async def _clear_problem(self, adr:str) -> bool:
        prompt = f"""
        Evaluate the following problem statement in an Architecture Decision Record (ADR):

        "{adr}"

        To determine if the problem is well-posed and real, consider the following:
        1. Is the problem clearly and unambiguously defined?
        2. Is the problem relevant to the context or domain of the ADR?
        3. Is there evidence or examples provided to support the existence and significance of the problem?
        4. Is the problem statement specific and focused, not vague or overly broad?

        Based on these criteria, provide an evaluation.

        The REASON can't be an EMPTY STRING.

        Respond ONLY with the following format:
        {{
        "reason": str,
        "valid": bool,
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

    async def _clear_decision_drivers(self, adr:str) -> bool:
        prompt = f"""
        Evaluate the following decision drivers in an Architecture Decision Record (ADR):

        "{adr}"

        To determine if the decision drivers are correct, consider the following:
        1. Are the decision drivers relevant to the problem and context of the ADR?
        2. Are the decision drivers justified with clear reasoning for their importance?
        3. Do the decision drivers contradict each other or the problem statement?
        4. Are all relevant decision drivers considered, and are they prioritized correctly?

        Based on these criteria, provide an evaluation.

        The REASON can't be an EMPTY STRING.

        Respond ONLY with the following format:
        {{
        "reason": str,
        "valid": bool,
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

    async def _logical_solution(self, adr:str) -> bool:
        prompt = f"""
        Evaluate the following solution in an Architecture Decision Record (ADR):

        "{adr}"

        To determine if the solution follows logically from the problem and decision drivers, consider the following:
        1. Does the solution directly address the problem as defined in the ADR?
        2. Is there a logical progression from the decision drivers to the conclusion?
        3. Is the reasoning from the problem and decision drivers to the solution free from logical fallacies?
        4. Is the solution effective in resolving the problem given the decision drivers?

        Based on these criteria, provide an evaluation.

        The REASON can't be an EMPTY STRING.

        Respond ONLY with the following format:
        {{
        "reason": str,
        "valid": bool,
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

    async def _no_better_alternative_solutions(self, adr:str) -> bool:
        prompt = f"""
        Evaluate the following Architecture Decision Record (ADR) to determine if there are any better alternative solutions than the proposed solution.

        The ADR:

        "{adr}"

        To determine if the proposed solution is the best, consider the following:
        1. **Effectiveness**: Does the proposed solution solve the problem more effectively than other possible solutions? Are there other solutions that address the problem in a more complete or superior way?
        2. **Efficiency**: Is the proposed solution more resource-efficient (e.g., time, cost, manpower) than other potential solutions? Are there alternatives that achieve the same outcome with fewer resources?
        3. **Simplicity**: Is the proposed solution simpler to implement or understand compared to other potential solutions? Are there alternatives that are easier to implement or require less complexity?
        4. **Risk Management**: Does the proposed solution have fewer risks or potential downsides than other alternatives? Are there other solutions with lower risk profiles?

        Based on these criteria, evaluate whether there are any better alternative solutions than the proposed solution in the ADR.

        The REASON can't be an EMPTY STRING.

        Respond ONLY with the following format:
        {{
        "reason": str,
        "valid": bool,
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

    # The three checks below have to be done manually by team members for now but in the future can potentially be automated

    # async def _no_full_system_risk(self, adr:str) -> bool: ... # mega prompt with all ADRs of all categories (or find a more efficient way)

    # async def _feasible(self, adr:str) -> bool: ... # complex as we need external data to ensure that (github roadmaps, etc)

    # async def _strategically_aligned(self, adr:str) -> bool: ... # probably we need a genlayer DAO to answer

    async def _evaluate_adr_reward(self, adr: str, category: str) -> dict:
        prompt = f"""
        Here is a new valid ADR submitted by a user.

        {adr}

        You MUST decide of a REWARD (INTEGER) between 1 and {self.max_reward}. 
        Evaluate the reward based on the potential impact, importance, and writing quality of the candidate.

        Respond ONLY with the following format:
        
        {{
        "reason": str,
        "reward": int,
        }}
        
        It is mandatory that you respond only using the JSON format above,
        nothing else. Don't include any other words or characters,
        your output must be only JSON without any formatting prefix or suffix.
        This result should be perfectly parseable by a JSON parser without errors.
        """
        result = await call_llm_with_principle(
            prompt,
            eq_principle="The result['reward'] has to be +-1",
        )
        result_clean = result.replace("True", "true").replace("False", "false") # to make sure is valid python
        output = json.loads(result_clean)
        return output
