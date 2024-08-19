"""
Module: RokosMansion
Description: Implements the RokosMansion game contract.
"""

import json
from backend.node.genvm.icontract import IContract
from backend.node.genvm.equivalence_principle import call_llm_with_principle


class RokosMansion(IContract):
    """
    RokosMansion game contract class.

    This class represents the game logic for the Mansion of Professor Roko game.
    It handles the game state, page transitions, and interactions with the game environment.

    Attributes:
        _allowed_styles (list): List of allowed writing styles.
        _style (str): Selected writing style.
        _allowed_countries (list): List of allowed country styles.
        _country (str): Selected country style.
        _allowed_difficulties (list): List of allowed difficulty levels.
        _difficulty (str): Selected difficulty level.
        _inventory (list): Player's inventory.
        _environment (str): String summarizing the changes in the environment.
        _current_page_number (int): Current page number.
        _current_page (str): Current page content.
        page_text_gen (dict): Generated page text.
        page_actions_gen (dict): Generated page actions.
        page_text (dict): Default page text.
        page_actions (dict): Default page actions.
    """

    def __init__(self, style: str = "Stephen King", country: str = "USA", difficulty: str = "Beginner"):
        """
        Initialize the RokosMansion contract.

        Args:
            style (str): Writing style. Defaults to "Stephen King".
            country (str): Country style. Defaults to "USA".
            difficulty (str): Difficulty level. Defaults to "Beginner".

        Raises:
            AssertionError: If the provided style, country, or difficulty is not allowed.
        """
        self._allowed_styles = ["Stephen King", "HP Lovecraft", "Clive Barker"]
        assert style in self._allowed_styles
        self._style = style
        self._allowed_countries = ['Andorra', 'Argentina', 'Brazil', 'España', 'Latvia', 'Portugal', 'Russia', 'Thailand', 'USA', 'Venezuela']
        assert country in self._allowed_countries
        self._country = country
        self._allowed_difficulties = ['Beginner', 'Medium', 'Difficult']
        assert difficulty in self._allowed_difficulties
        self._difficulty = difficulty

        self._inventory = []  # list of strings
        self._environment = ""
        self._current_page_number = 1
        self._current_page = ""
        self.page_text_gen = {}
        self.page_actions_gen = {}

        self.page_text = {
            1: "Action: Explore the mansion, enter the mansion entrance hall and solve the puzzles to prevent the ASI from taking control of your world.",
            2: "The Entrance Hall: You stand in the grand entrance hall of the mansion with several doors leading to different rooms. Roko's hologram reappears, urging you to hurry, as the ASI grows stronger by the minute. Your task is to solve three logical puzzles hidden within the mansion to weaken the ASI's influence. However, you can explore the rooms to gather information and insights.",
            3: "The Library: The library is vast with towering bookshelves and strange devices scattered across the room. In the center is an ancient-looking machine emitting a low hum. Three mysterious boxes sit before the machine, each labeled with cryptic symbols. The labels on the boxes are all incorrect, and you must deduce the correct labels to deactivate the ASI's control in the room.",
            4: "The Study: The study is a small room filled with strange devices and a desk with blueprints and journals. A glowing cube rests on the desk, and the room's puzzle involves analyzing a statement about Organics and Synthetics to deactivate the ASI's device.",
            5: "The Laboratory: The laboratory is packed with futuristic machines. This room holds the final puzzle involving two robotic guards. By solving it, you can retrieve the radioactive materials to sever the ASI's connection to the present timeline.",
            6: "Professor Roko's Dormitory: The dormitory is cluttered with books, blueprints, and gadgets. Professor Roko's hologram stands in the center, offering cryptic insights about the ASI, the puzzles, and how to defeat the ASI.",
            7: "The Dining Hall: The dining hall is lavish but abandoned, with a long table covered in untouched dishes. There are no puzzles here, but there are clues about AI developments and future dangers.",
            8: "The Upstairs Hallway: The hallway is dark with paintings of futuristic cities on the walls. Faint mechanical sounds can be heard from one of the rooms. Several doors line the hall, but only one is unlocked.",
            9: "The Observatory: The observatory offers a breathtaking view of the night sky. There are no puzzles here, but you find a journal detailing Professor Roko's early experiments with the ASI and troubling future visions.",
            10: "Return to the Entrance Hall: From any room in the mansion, the player can choose to return to the entrance hall and select a different room to explore. Gathering clues in these rooms may help solve the puzzles in the mansion.",
            11: "Victory!: After solving all the puzzles, you return to Professor Roko's study where the ASI's connection is permanently severed. The devices go dark, and you leave the mansion victorious, having saved the future."
        }
        self.page_actions = {
            1: "Action: Explore the mansion and solve the puzzles to prevent the ASI from taking control of your world.",
            2: "Action: Choose a door: Left (Library), Center (Laboratory), Right (Study), Door leading to Professor Roko's personal study, Staircase to the upper floor.",
            3: "Action: Choose the correct box and step through the portal and return to the entrance hall. Now you must decide which room to explore next: Center (Laboratory), Right (Study), Professor Roko's Personal Study.",
            4: "Action: Analyze the statement and determine if it is true or false. Correct it if necessary to deactivate the ASI's device. Return to the entrance hall: Left (Library), Center (Laboratory), Professor Roko's Personal Study.",
            5: "Action: Choose the correct element to unlock the cave and retrieve the radioactive material. Return to the Entrance Hall and choose a new room to explore.",
            6: "Action: Speak to Professor Roko. You may ask him about the Origin of the ASI, the Nature of the Puzzles, or how to defeat the ASI.",
            7: "Action: Explore the room and read the newspaper. Return to the Entrance Hall or proceed to another room.",
            8: "Action: Explore the hallway. Enter the unlocked room or return downstairs.",
            9: "Action: Read Professor Roko's journal. Return to the Entrance Hall or explore another part of the mansion.",
            10: "Action: Return to the Entrance Hall and select a different room to explore. Gather clues or explore the mansion.",
            11: "Action: Exit the mansion, completing your journey as the savior of the future. You've won the game!"
        }

    def update_current_page(self) -> str:
        """
        Update the current page content.

        Returns:
            str: Updated current page content.
        """
        if self._current_page_number not in self.page_text_gen:
            self.page_text_gen[self._current_page_number] = self._current_page
        self._current_page = self.page_text_gen[self._current_page_number]

        return self._current_page

    def get_current_page(self) -> str:
        """
        Get the current page content.

        Returns:
            str: Current page content.
        """
        if self._current_page_number not in self.page_text_gen:
            return "Void. Call `update_current_page`"
        return self.page_text_gen[self._current_page_number]

    def get_current_page_number(self) -> int:
        """
        Get the current page number.

        Returns:
            int: Current page number.
        """
        return self._current_page_number

    async def update_current_page(self):
        """
        Update the current page content using an LLM.

        This method generates a detailed scenario description for the current page
        based on the writer's style, country style, inventory, and original page scenario.
        """
        prompt = f"""
Generate a very brief but vivid scenario description for the current page in the "Mansion of Professor Roko" game. Use the following context:

1. Writer Style: {self._style}
2. Country Style: {self._country}
3. Inventory: {', '.join(self._inventory) if self._inventory else 'Empty'}
4. Page Scenario: {self.page_text[self._current_page_number]}

Create a very brief but vivid and immersive description that incorporates elements of the specified writer's style, cultural elements from the given country, mentions any items in the characters inventory, and based on the original page scenario. The description should be be brief but consistent with the original context while adding color and atmosphere.

Respond using ONLY the following format:
{{
"description": str
}}
"""
        result = await call_llm_with_principle(
            prompt,
            eq_principle="The generated description must be consistent with the original page scenario, writer's style, country's culture, and inventory items."
        )
        output = json.loads(result)
        self.page_text_gen[self._current_page_number] = output["description"]

    async def update_current_actions(self):
        """
        Update the current page actions using an LLM.

        This method generates brief and concise descriptions for the actions available
        on the current page based on the writer's style, country style, and inventory.
        """
        prompt = f"""
Generate brief and concise descriptions for the actions available on the current page of the "Mansion of Professor Roko" game. Use the following context:

1. Writer Style: {self._style}
2. Country Style: {self._country} 
3. Inventory: {', '.join(self._inventory) if self._inventory else 'Empty'}
4. Current Actions: {self.page_actions[self._current_page_number]}

Create very brief but vivid action descriptions that incorporate elements of the specified writer's style and cultural elements from the given country. The descriptions should be concise but consistent with the original actions while adding a touch of atmosphere.

Format the output as a single string with Markdown bullet points, like this:
* Action 1 description
* Action 2 description
* Action 3 description

Respond using ONLY the following format:
{{
"actions": str
}}
"""
        result = await call_llm_with_principle(
            prompt,
            eq_principle="The generated action descriptions must be consistent with the original actions, writer's style, and country's culture."
        )
        output = json.loads(result)
        self.page_actions_gen[self._current_page_number] = output["actions"]

    def get_current_actions(self) -> str:
        """
        Get the current page actions.

        Returns:
            str: Current page actions.
        """
        if self._current_page_number not in self.page_actions_gen:
            return "Void. Call `update_current_actions`"
        return self.page_actions_gen[self._current_page_number]

    async def do_prompt(self, prompt: str) -> str:
        """
        Process a user prompt and generate a response.

        This method checks if the prompt matches any current actions and responds accordingly.
        If the prompt doesn't match an action, it is treated as a question or environmental interaction.

        Args:
            prompt (str): User prompt.

        Returns:
            str: Generated response.
        """
        # Check if the prompt matches any current actions
        action_match_prompt = f"""
        Given the current actions for this page:
        {self.get_current_actions()}

        The user's inventory:
        {', '.join(self._inventory) if self._inventory else 'Empty'}

        The environment summary:
        {self._environment if self._environment else 'No changes in the environment.'}
        
        The difficulty level:
        {self._difficulty}
        
        And the user's prompt:
        "{prompt}"

        Determine if the user's prompt roughly matches any of the current actions.
        Respond with only "true" if it matches, or "false" if it doesn't match.
        """
        action_match_result = await call_llm_with_principle(
            action_match_prompt,
            eq_principle="The response must be either 'true' or 'false' based on whether the prompt matches an action."
        )
        
        if action_match_result.strip().lower() == "true":
            # The prompt matches an action, so we need to move to another page/room or solve a puzzle
            action_result_prompt = f"""
            Given the current page description:
            {self.get_current_page()}

            The user's inventory:
            {', '.join(self._inventory) if self._inventory else 'Empty'}

            The environment summary:
            {self._environment if self._environment else 'No changes in the environment.'}
            
            The difficulty level:
            {self._difficulty}
            
            And the user's action:
            "{prompt}"

            Determine the result of this action. If it leads to a new room, specify which room (page number) to move to.
            If it involves solving a puzzle, describe the attempt to solve it.
            
            Adjust the complexity and challenge of the puzzle based on the difficulty level.

            Respond in the following JSON format:
            {{
                "result": str,
                "new_page_number": int or null,
                "puzzle_solved": bool or null
            }}
            """
            action_result = await call_llm_with_principle(
                action_result_prompt,
                eq_principle="The response must be consistent with the game's logic, current state, inventory, environment, and difficulty level."
            )
            action_output = json.loads(action_result)
            
            if action_output["new_page_number"]:
                self._current_page_number = action_output["new_page_number"]
                await self.update_current_page()
                await self.update_current_actions()
            
            return action_output["result"]
        else:
            # The prompt doesn't match an action, so we need to handle it as a question or environmental interaction
            env_interaction_prompt = f"""
            Given the current page description:
            {self.get_current_page()}

            The user's inventory:
            {', '.join(self._inventory) if self._inventory else 'Empty'}

            The environment summary:
            {self._environment if self._environment else 'No changes in the environment.'}
            
            The difficulty level:
            {self._difficulty}
            
            And the user's prompt:
            "{prompt}"

            Determine how this prompt affects the environment or inventory. If it's a question, provide an appropriate answer.
            
            Respond in the following JSON format:
            {{
                "result": str,
                "inventory_change": [str] or null,
                "environment_change": str or null
            }}
            """
            env_result = await call_llm_with_principle(
                env_interaction_prompt,
                eq_principle="The response must be consistent with the game's current state, inventory, environment, and logical within the game world."
            )
            env_output = json.loads(env_result)
            
            if env_output["inventory_change"]:
                self._inventory.extend(env_output["inventory_change"])
            
            if env_output["environment_change"]:
                self._environment += f" {env_output['environment_change']}"
            
            return env_output["result"]
