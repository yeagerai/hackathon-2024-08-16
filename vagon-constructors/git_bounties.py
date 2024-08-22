import json
import math
from backend.node.genvm.icontract import IContract
from backend.node.genvm.equivalence_principle import (
    EquivalencePrinciple,
    get_webpage_with_principle,
)


class BountyData:
    issue: int
    points: int
    claimed: bool

    def __init__(self, issue, points):
        self.issue = issue
        self.points = points
        self.claimed = False


class GitBounties(IContract):
    def __init__(self, github_repository: str):
        self.owner = contract_runner.from_address
        self.repository = "https://github.com/" + github_repository
        self.developers = {}  # Mapping from: GitHub username -> Address
        self.points = {}  # Mapping from: GitHub username -> points earned
        self.bounties = {}  # Mapping from: Issue number -> BountyData
        pass

    def get_developers(self) -> dict:
        return self.developers

    def get_points(self) -> dict:
        return self.points

    def get_bounties(self) -> dict:
        bounties = {}
        for k, v in self.bounties.items():
            bounties[k] = {"issue": v.issue, "points": v.points, "claimed": v.claimed}
        return bounties

    def add_bounty(self, issue: int, points: int):
        if self.owner != contract_runner.from_address:
            raise Exception("only owner")

        bounty = self.bounties.setdefault(issue, BountyData(issue, points))
        if bounty.claimed:
            raise Exception("can't add bounty to claimed issue")

    async def register(self, github_username: str) -> None:
        dev_github_profile = f"https://github.com/{github_username}"
        developer_address = contract_runner.from_address

        web_data = await get_webpage_with_principle(
            dev_github_profile, "The result should be exactly the same"
        )
        if developer_address in web_data["output"]:
            self.developers[github_username] = developer_address
        else:
            raise Exception(
                "Couldn't verify the developer, GitHub profile page must have the given address on its bio"
            )

    async def claim(self, pull: int) -> None:
        final_result = {}
        async with EquivalencePrinciple(
            result=final_result,
            principle="The result should be exactly the same",
            comparative=True,
        ) as eq:
            web_data = await eq.get_webpage(self.repository + "/pull/" + str(pull))
            task = f"""
            The following web page content corresponds to a GitHub pull request.

            Web page content:
            {web_data}
            End of web page data.

            In that Pull Request, a developer should be fixing an issue from the repository 
            issues list: located at: https://github.com/cristiam86/genlayer-hackaton/issues

            To fin the issue, you should look for a text like "Fixes: #<issue_number>" in the 
            Pull Request first comment.
            It is very important to also include information about how many times a given PR has
            ben rejected (changes requested), son include the number of those as well.

            Respond with the following JSON format:
            {{
                "merged":  boolean, // if pull request was merged
                "username": string, // GitHub username of the developer who opened a pull request
                "issue":  int, // number of the closed issue
                "changes_requested": int // number of changes requested for the given pull request  
            }}

            It is mandatory that you respond only using the JSON format above, nothing else.
            Don't include any other words or characters, your output must be only JSON without any
            formatting prefix or suffix. This result should be perfectly parseable by a
            JSON parser without errors.
            """
            result = await eq.call_llm(task)
            print("\nresult: ", result)
            eq.set(result)

        res = json.loads(final_result["output"])
        if not res["merged"]:
            raise Exception("pull is not mergerd")

        bounty_issue = res["issue"]
        bounty_username = res["username"]
        pull_request_changes_requested = res["changes_requested"]
        bounty = self.bounties.get(bounty_issue, None)

        if bounty and not bounty.claimed:
            bounty.claimed = True
            if not bounty_username in self.points:
                self.points[bounty_username] = 0
            total_points = math.floor(
                bounty.points / (pull_request_changes_requested + 1)
            )
            self.points[bounty_username] += 1 if total_points <= 1 else total_points
