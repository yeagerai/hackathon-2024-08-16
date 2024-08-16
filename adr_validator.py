import re
import json
from backend.node.genvm.icontract import IContract
from backend.node.genvm.equivalence_principle import call_llm_with_principle

class ADRValidator(IContract):
    def __init__(self):
        self.owner = contract_runner.from_address
        self.arch_categories = {} # {"genvm": {"description":"", "ADRs":["","",""]}, "consensus":...}
        
    def change_owner(self, new_owner:str):
        if contract_runner.from_address == self.owner:
            self.owner = new_owner

    def get_owner(self) -> str:
        return self.owner

    def get_categories(self) -> str:
        return {category: details["description"] for category, details in self.arch_categories.items()}

    def get_adrs_of_a_category(self, category_name: str) -> dict:
            if category_name in self.arch_categories:
                return self.arch_categories[category_name]["ADRs"]

    ## Improvement: LLM fuzzy matching categories to warn about potential duplicates potentially using vectorDB
    def add_category(self, category_name: str, category_description: str):
        if contract_runner.from_address == self.owner and category_name not in self.arch_categories:
            self.arch_categories[f"{category_name}"] = {"description": category_description, "ADRs": []}

    async def validate_adr(self, adr: str, category_name: str) -> None:
        print("validate")
        if not self._check_template(adr): return
        if not self._check_decisions(adr): return
        self.arch_categories[category_name]["ADRs"].append(adr)

    def _check_template(self, adr: str) -> bool:
        print("check_template")
        pattern = r"""
        ^\#\s[^\n]+?\n
        (?:-\sStatus:\s[^\n]+?\n)+
        (?:-\sDeciders:\s[^\n]+?\n)+
        (?:-\sDate:\s[^\n]+?\n)+
        
        \#\#\sContext\sand\sProblem\sStatement\s*
        (?:.*?\n)+

        \#\#\sDecision\sDrivers\s*
        (?:-\s[^\n]+?\n)+

        \#\#\sConsidered\sOptions\s*
        (?:-\s[^\n]+?\n)+

        \#\#\sDecision\sOutcome\s*
        (?:Chosen\soption:\s[^\n]+?\n)+
        
        \#\#\#\sConsequences\s*
        (?:-\s\*\*[^\*]+?\*\*:\s[^\n]+?\n)+

        \#\#\sPros\sand\sCons\sof\sthe\sOptions\s*
        (?:\#\#\#\s[^\n]+?\n
        (?:\n|\s)+
        \#\#\#\#\sPros:\s*
        (?:-\s\*\*[^\*]+?\*\*:\s[^\n]+?\n)+
        \#\#\#\#\sCons:\s*
        (?:-\s\*\*[^\*]+?\*\*:\s[^\n]+?\n)+)+
        """

        result = bool(re.match(re.compile(pattern, re.VERBOSE | re.DOTALL), adr))
        print("template result:", result)
        return result

    async def _check_decisions(self, adr: str) -> bool:
        print("check_decisions")
        valid_decisions = False
        prompt = f"""
        Here are some dispute resolutions made in the past, and a new decision candidate.
        You must check past decisions for contradiction with the new candidate, or for dependencies that would block this candidate.

        - Past decisions:
        {self.arch_categories}

        - New decision candidate:
        {adr}

        You must decide if the new decision can be accepted or if it should be rejected.
        In case of rejection, you must also provide a reason for the rejection.
        In case of acceptance, the reason should be an empty string.

        Respond ONLY with the following format:
        {{
        "reasoning": str,
        "accepted": bool
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
        if output["accepted"] is True:
            return True
        else:
            return False