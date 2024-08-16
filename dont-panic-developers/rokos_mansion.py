import json
from backend.node.genvm.icontract import IContract
from backend.node.genvm.equivalence_principle import call_llm_with_principle


class RokosMansion(IContract):
    async def __init__(self, style: str = "Stephen King", country: str = "USA"):
        self._allowed_styles = ["Stephen King", "HP Lovecraft", "Clive Barker"]
        assert style in self._allowed_styles
        self._style = style
        self._allowed_countries = ['Andorra', 'Argentina', 'Brazil', 'España', 'Letonia', 'Portugal', 'Russia', 'Thailand', 'USA', 'Venezuela']
        assert country in self._allowed_countries
        self._country = country

        self._inventory = [] # list of strings
        self._current_page_number = 1
        self._current_page = ""
        self.page_text_gen = {}
        
        self.page_text = {
            1: "Arrival at the Mansion: You are an engineer named Alex, invited to visit the mansion of Professor Roko, a notorious mad scientist known for dabbling in AI technology. Upon arrival, the mansion seems eerie, its large doors creaking open on their own. As you step inside, you feel a strange presence. A hologram of Professor Roko appears and reveals that he has made contact with a malicious artificial superintelligence (ASI) from the future. The ASI is sending cryptic messages and puzzles through devices scattered across the mansion.",
            2: "The Entrance Hall: You stand in the grand entrance hall of the mansion with several doors leading to different rooms. Roko’s hologram reappears, urging you to hurry, as the ASI grows stronger by the minute. Your task is to solve three logical puzzles hidden within the mansion to weaken the ASI’s influence. However, you can explore the rooms to gather information and insights.",
            3: "The Library: The library is vast with towering bookshelves and strange devices scattered across the room. In the center is an ancient-looking machine emitting a low hum. Three mysterious boxes sit before the machine, each labeled with cryptic symbols. The labels on the boxes are all incorrect, and you must deduce the correct labels to deactivate the ASI’s control in the room.",
            4: "The Study: The study is a small room filled with strange devices and a desk with blueprints and journals. A glowing cube rests on the desk, and the room’s puzzle involves analyzing a statement about Organics and Synthetics to deactivate the ASI’s device.",
            5: "The Laboratory: The laboratory is packed with futuristic machines. This room holds the final puzzle involving two robotic guards. By solving it, you can retrieve the radioactive materials to sever the ASI’s connection to the present timeline.",
            6: "Professor Roko’s Dormitory: The dormitory is cluttered with books, blueprints, and gadgets. Professor Roko’s hologram stands in the center, offering cryptic insights about the ASI, the puzzles, and how to defeat the ASI.",
            7: "The Dining Hall: The dining hall is lavish but abandoned, with a long table covered in untouched dishes. There are no puzzles here, but there are clues about AI developments and future dangers.",
            8: "The Upstairs Hallway: The hallway is dark with paintings of futuristic cities on the walls. Faint mechanical sounds can be heard from one of the rooms. Several doors line the hall, but only one is unlocked.",
            9: "The Observatory: The observatory offers a breathtaking view of the night sky. There are no puzzles here, but you find a journal detailing Professor Roko’s early experiments with the ASI and troubling future visions.",
            10: "Return to the Entrance Hall: From any room in the mansion, the player can choose to return to the entrance hall and select a different room to explore. Gathering clues in these rooms may help solve the puzzles in the mansion.",
            11: "Victory!: After solving all the puzzles, you return to Professor Roko's study where the ASI's connection is permanently severed. The devices go dark, and you leave the mansion victorious, having saved the future."
        }
        self.page_actions = {
            1: "Action: Explore the mansion and solve the puzzles to prevent the ASI from taking control of your world.",
            2: "Action: Choose a door: Left (Library), Center (Laboratory), Right (Study), Door leading to Professor Roko's personal study, Staircase to the upper floor.",
            3: "Action: Choose the correct box and step through the portal and return to the entrance hall. Now you must decide which room to explore next: Center (Laboratory), Right (Study), Professor Roko's Personal Study.",
            4: "Action: Analyze the statement and determine if it is true or false. Correct it if necessary to deactivate the ASI’s device. Return to the entrance hall: Left (Library), Center (Laboratory), Professor Roko's Personal Study.",
            5: "Action: Choose the correct element to unlock the cave and retrieve the radioactive material. Return to the Entrance Hall and choose a new room to explore.",
            6: "Action: Speak to Professor Roko. You may ask him about the Origin of the ASI, the Nature of the Puzzles, or how to defeat the ASI.",
            7: "Action: Explore the room and read the newspaper. Return to the Entrance Hall or proceed to another room.",
            8: "Action: Explore the hallway. Enter the unlocked room or return downstairs.",
            9: "Action: Read Professor Roko’s journal. Return to the Entrance Hall or explore another part of the mansion.",
            10: "Action: Return to the Entrance Hall and select a different room to explore. Gather clues or explore the mansion.",
            11: "Action: Exit the mansion, completing your journey as the savior of the future. You’ve won the game!"
        }
        await self.update_current_page()

    def update_current_page(self) -> str:
        if not self._current_page_number in self.page_text_gen:  
            self.page_text_gen[self._current_page_number] = self._current_page
        self._current_page = self.page_text_gen[self._current_page_number]

        return self._current_page

    def get_current_page(self) -> str:
        if not self._current_page_number in self.page_text_gen: 
            return "Empty description."
        return self.page_text_gen[self._current_page_number]

    def get_current_page_number(self) -> int:
        return self._current_page_number

    async def update_current_page(self):
        prompt = f"""
Generate a detailed scenario description for the current page in the "Mansion of Professor Roko" game. Use the following context:

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
