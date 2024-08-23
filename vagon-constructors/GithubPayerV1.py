from backend.node.genvm.icontract import IContract
from backend.node.genvm.equivalence_principle import EquivalencePrinciple

import json

class BountyData:
    issue: int
    value: int
    claimed: bool
    def __init__(self, issue):
        self.issue = issue
        self.value = 0
        self.claimed = False

class GithubPayer(IContract):
    def __init__(self, repo: str):
        self.repo_raw = repo
        self.repo = "https://github.com/" + repo
        self.users = {}
        self.owner = contract_runner.from_address
        self.bounties = {}
        pass
    
    def get_bounties(self) -> str:
        r = {}
        for k, v in self.bounties.items():
            r[k] = {"issue": v.issue, "value": v.value, "claimed": v.claimed}
        return json.dumps(r)
    
    def add_bounty(self, issue: int):
        bounty = self.bounties.setdefault(issue, BountyData(issue))
        if bounty.claimed:
            raise Exception("can't add bounty to claimed issue")
        bounty.value += 1 # message.value

    async def register(self, username: str) -> None:
        address = contract_runner.from_address

        final_result = {}
        async with EquivalencePrinciple(
            result=final_result,
            principle="The result should be exactly the same",
            comparative=True,
        ) as eq:
            web_data = await eq.get_webpage("https://github.com/" + username)
            if address in web_data:
                eq.set(True)
            else:
                eq.set(False)
        print(final_result)
        if not final_result["output"]:
            raise Exception("couldn't verify, user must have an address listed")
        self.users[username] = address

    async def claim(self, pull: int) -> None:
        final_result = {}
        async with EquivalencePrinciple(
            result=final_result,
            principle="The result should be exactly the same",
            comparative=True,
        ) as eq:
            web_data = await eq.get_webpage(self.repo + "/pull/" + str(pull))
            api_data = await eq.get_webpage("https://api.github.com/repos/" + self.repo_raw  + "/pulls/" + str(pull))
            print(api_data)
            api_data = json.loads(api_data)
            prompt = f"""
            In the following web page, find information about GitHub pull request

            Web page content:
            {web_data}
            End of web page data.

            Respond with the following JSON format:
            {{
                "merged":  boolean, // if pull request was merged
                "user": string, // username of a person who opened a pull request
                "issue":  int[], // numbers of closed issues
            }}

            It is mandatory that you respond only using the JSON format above, nothing else. Don't include any other words or characters, your output must be only JSON without any formatting prefix or suffix. This result should be perfectly parseable by a JSON parser without errors.
            """
            res = await eq.call_llm(prompt)
            res = json.loads(res)
            res["user"] = api_data["user"]["login"]
            res["merged"] = api_data["merged_at"] is not None
            eq.set(res)
        res = final_result["output"]
        print(res)
        if not res["merged"]:
            raise Exception("pull is not mergerd")
        address = self.users[res["user"]]
        for b in res["issue"]:
            bounty = self.bounties.get(b, None)
            if bounty is None:
                continue
            if bounty.claimed:
                continue
            #transfer(address, bounty.value)
            print(f"claiming {b}")
            bounty.claimed = True
