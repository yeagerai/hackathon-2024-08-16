"""
On-chain identity verification via social media.
We will check LinkedIn profile since it is a professional network.

We could also check other social media platforms like Twitter, Facebook, etc, but it's better to use APIs for those.
Example usage:
    linkedin_id = "john-doe"
    first_name = "John"
    last_name = "Doe"
    target_country = "United States"
    target_organization = "Google"
"""
import json
from backend.node.genvm.icontract import IContract
from backend.node.genvm.equivalence_principle import EquivalencePrinciple

class IdentityVerifier(IContract):
    def __init__(self, linkedin_id: str, first_name: str, last_name: str, target_country: str, target_organization: str):
        """
        Initializes a new instance of the IdentityVerifier contract.

        Args:
            linkedin_id (str): The LinkedIn ID of the person.
            first_name (str): The first name of the person.
            last_name (str): The last name of the person.
            target_country (str): The expected country of the person.
            target_organization (str): The expected organization of the person.
        
        Attributes:
            linkedin_url (str): The URL to the LinkedIn profile of the person.
            first_name (str): The first name of the person.
            last_name (str): The last name of the person.
            target_country (str): The expected country of the person.
            target_organization (str): The expected organization of the person.
            verified (bool): Indicates whether the person's identity has been verified. Default is False.
        """
        self.linkedin_url = "https://www.linkedin.com/in/" + linkedin_id
        self.first_name = first_name
        self.last_name = last_name
        self.target_country = target_country
        self.target_organization = target_organization
        self.verified = False

    async def verify_identity(self) -> bool:
        """
        Verifies the identity of the person by checking their LinkedIn profile.
        
        Returns:
            bool: True if the person's name, country, and organization match the expected values, False otherwise.
        """
        final_result = {}
        async with EquivalencePrinciple(
            result=final_result,
            principle="The name, country, and organization should match the target values",
            comparative=True,
        ) as eq:
            web_data = await eq.get_webpage(self.linkedin_url)
            print(web_data)

            task = f"""In the following LinkedIn profile page, find the current name, country, and organization of the person:
            Profile URL: {self.linkedin_url}

            Web page content:
            {web_data}
            End of web page data.

            Respond with the following JSON format:
            {{
                "first_name": str, // The first name of the person
                "last_name": str, // The last name of the person
                "country": str, // The current country of the person
                "organization": str // The current organization of the person
            }}
            It is mandatory that you respond only using the JSON format above,
            nothing else. Don't include any other words or characters,
            your output must be only JSON without any formatting prefix or suffix.
            This result should be perfectly parseable by a JSON parser without errors.
            """
            result = await eq.call_llm(task)
            print(result)
            eq.set(result)

        result_json = json.loads(final_result["output"])

        if (
            result_json["first_name"].lower() == self.first_name.lower() and
            result_json["last_name"].lower() == self.last_name.lower() and
            result_json["country"] == self.target_country and
            result_json["organization"] == self.target_organization
        ):
            self.verified = True
            return True

        return False
