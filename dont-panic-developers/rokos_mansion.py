
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
        _inventory (list): Player's inventory.
        _environment (str): String summarizing the changes in the environment.
        _current_page_number (int): Current page number.
        _current_page (str): Current page content.
        page_text_gen (dict): Generated page text.
        page_actions_gen (dict): Generated page actions.
        page_text (dict): Default page text.
        page_actions (dict): Default page actions.
    """

    def __init__(self, style: str = "Stephen King", country: str = "USA"):
        """
        Initialize the RokosMansion contract.

        Args:
            style (str): Writing style. Defaults to "Stephen King".
            country (str): Country style. Defaults to "USA".

        Raises:
            AssertionError: If the provided style, country is not allowed.
        """
        self._allowed_styles = ["Stephen King", "HP Lovecraft", "Clive Barker", "Yukio Mishima"]
        assert style in self._allowed_styles
        self._style = style
        self._allowed_countries = ['Andorra', 'Argentina', 'Brazil', 'España', 'Latvia', 'Portugal', 'Russia', 'Thailand', 'USA', 'Venezuela','Japan']
        assert country in self._allowed_countries
        self._country = country
 
        self._inventory = []  # list of strings
        self._environment = ""
        self._current_page_number = 1
        self._current_page = ""
        self.page_text_gen = {}
        self.page_actions_gen = {}

        self.page_puzzles = {}
        self.page_puzzles[3] = "Each box is labeled, but all labels are incorrect. One box contains only **Poison**, one contains only **Antidote**, and the last contains **Both Poison and Antidote**. The puzzle asks you to pick one item from any box, knowing that the labels are wrong. For example, if you pick from the box labeled 'Both Poison and Antidote,' whatever you pull will reveal how to correctly label all three boxes. Solving this puzzle deactivates the ASI’s device in the library and allows you to proceed.",
        self.page_puzzles[4] = "The room’s puzzle involves analyzing the behavior of Organics and Synthetics, two types of beings affected by the ASI: Organics believe everything while awake is true, and everything while asleep is false, while Synthetics believe the opposite. The puzzle asks you to determine the truth of the statement: 'Any person that is awake believes they are organic.' Solve it to deactivate the ASI’s device in the room."
        self.page_puzzles[5] = "Guard 1 (lying for uranium) says 'The materials are either uranium or thorium,' Guard 2 (lying for plutonium) says 'The secret material is plutonium'; solve their statements to determine the correct radioactive material and sever the ASI's timeline connection."

        self.page_puzzles_action[3] = " To solve this puzzle you must choose ONLY one box and be logically consistent with the conditions.",
        self.page_puzzles_action[4] = " To solve this puzzle you must clearly say is the statement <Any person that is awake believes they are organic.> is true or false, and be logically consistent with the puzzle conditions."
        self.page_puzzles_acion[5] = "To solve this puzzle you must clearly say if the secret material mentioned by the Guards is plutonium, uranium or thorium, and be logically consistent with that what the Guards have said."

        self.page_text = {
            1: "Arrival at the Mansion: You are an engineer named Alex, invited to visit the mansion of Professor Roko, a notorious mad scientist known for dabbling in AI technology. Upon arrival, the mansion seems eerie, its large doors creaking open on their own. As you step inside, you feel a strange presence. A hologram of Professor Roko appears and reveals that he has made contact with a malicious artificial superintelligence (ASI) from the future. The ASI is sending cryptic messages and puzzles through devices scattered across the mansion.",
            2: "The Entrance Hall: You stand in the grand entrance hall of the mansion with several doors leading to different rooms. Roko's hologram reappears, urging you to hurry, as the ASI grows stronger by the minute. Your task is to solve three logical puzzles hidden within the mansion to weaken the ASI's influence. However, you can explore the rooms to gather information and insights.",
            3: "The Library: The library is a vast room filled with towering bookshelves and strange devices. In the center, an ancient machine hums softly, connected to three mysterious boxes.",
            4: "The Study: The study is a small room filled with strange devices, a desk cluttered with blueprints and journals, and a glowing cube resting on the desk.",
            5: "The Laboratory: A futuristic room where two robotic guards protect a vault containing either uranium, plutonium, or thorium .", 
            6: "Professor Roko's Dormitory: The dormitory is cluttered with books, blueprints, and gadgets. Professor Roko's hologram stands in the center, offering cryptic insights about the ASI, the puzzles, and how to defeat the ASI.",
            7: "The Dining Hall: The dining hall is lavish but abandoned, with a long table covered in untouched dishes. There are no puzzles here, but there are clues about AI developments and future dangers.",
            8: "The Upstairs Hallway: The hallway is dark with paintings of futuristic cities on the walls. Faint mechanical sounds can be heard from one of the rooms. Several doors line the hall, but only one is unlocked.",
            9: "The Observatory: The observatory offers a breathtaking view of the night sky. There are no puzzles here, but you find a journal detailing Professor Roko's early experiments with the ASI and troubling future visions.",
            10: "Return to the Entrance Hall: From any room in the mansion, the player can choose to return to the entrance hall and select a different room to explore. Gathering clues in these rooms may help solve the puzzles in the mansion.",
            11: "Victory!: After solving all the puzzles, you return to Professor Roko's study where the ASI's connection is permanently severed. The devices go dark, and you leave the mansion victorious, having saved the future."
        }
        self.page_actions = {
            1: "Action: Explore the mansion, enter the mansion entrance hall and solve the puzzles to prevent the ASI from taking control of your world.",
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
Generate a very brief but vivid scenario description (in 3 short sentences) for the current page in the "Mansion of Professor Roko" game. Use the following context:

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
        if self._current_page_number in self.page_puzzles:
           self.page_text_gen[self._current_page_number] += '\n\n' + self.page_puzzles[self._current_page_number] 

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
        room_mapping = {k: v.split(':')[0].strip() for k, v in self.page_text.items()}
        room_mapping_str = '\n'.join(f"{v} (Page {k})" for k, v in room_mapping.items())

        # Check if the prompt matches any current actions
        action_match_prompt = f"""
        Given the current actions for this page:
        {self.get_current_actions()}

        The user's inventory:
        {', '.join(self._inventory) if self._inventory else 'Empty'}

        The environment summary:
        {self._environment if self._environment else 'No changes in the environment.'}
        
        The current room:
        {room_mapping[self._current_page_number]} (Page {self._current_page_number})
        
        And the user's prompt:
        "{prompt}"

        Determine if the user's prompt roughly matches any of the current actions, or matches 
        the action of trying to solve a present puzzle if there is a puzzle present. 
        Respond with only "true" if it matches, or "false" if it doesn't match.
        """
        action_match_result = await call_llm_with_principle(
            action_match_prompt,
            eq_principle="The response must be either 'true' or 'false' based on whether the prompt matches an action (including an attemp to solve a puzzle if present)."
        )
        
        if action_match_result.strip().lower() == "true":
            # The prompt matches an action, so we need to move to another page/room or solve a puzzle
            print('DEBUG: # The prompt matches an action, so we need to move to another page/room or solve a puzzle')
            action_result_prompt = f"""
            Given the current page description:
            {self.get_current_page()}

            The user's inventory:
            {', '.join(self._inventory) if self._inventory else 'Empty'}

            The environment summary:
            {self._environment if self._environment else 'No changes in the environment.'}
            
            And the user's action:
            "{prompt}"

            All rooms in the game:
            {room_mapping_str}
        
            Determine the result of this action. If it leads to a new room, specify which room (page number) to move to.
            If it involves solving a puzzle, describe the attempt to solve it (true, false, null).
            
            Respond using ONLY the following JSON format:
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
                #await self.update_current_page()
                #await self.update_current_actions()
            
            return action_output["result"]
        else:
            # The prompt doesn't match an action, so we need to handle it as a question or environmental interaction
            print("DEBUG: # The prompt doesn't match an action, so we need to handle it as a question or environmental interaction")
            env_interaction_prompt = f"""
            Given the current page description:
            {self.get_current_page()}

            The user's inventory:
            {', '.join(self._inventory) if self._inventory else 'Empty'}

            The environment summary:
            {self._environment if self._environment else 'No changes in the environment.'}
            
            And the user's prompt:
            "{prompt}"

            Determine how this prompt affects the environment or inventory. If it's a question, provide an appropriate answer.
            
            Respond using ONLY the following JSON format:
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
