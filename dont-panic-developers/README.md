
# Roko's Mansion Intelligent Contract

This contract implements a text-based adventure game with dynamic content generation, puzzle-solving elements, and state management.

## Class: RokosMansion

Implements the game logic for the "Roko's Mansion" game.

### Attributes:
- `_allowed_styles`: List of allowed writing styles
- `_style`: Selected writing style
- `_allowed_countries`: List of allowed country styles
- `_country`: Selected country style
- `_inventory`: Player's inventory
- `_environment`: String summarizing changes in the environment
- `_current_page_number`: Current page number
- `_current_page`: Current page content
- `page_text_gen`: Generated page text
- `page_actions_gen`: Generated page actions
- `page_text`: Default page text
- `page_actions`: Default page actions
- `puzzles_solved`: List of solved puzzles
- `puzzles_for_victory`: Number of puzzles required to win
- `victory_page`: Page number for victory condition

### Public Methods:
```markdown
- `get_current_page() -> str`
- `get_current_page_number() -> int`
- `async update_current_page()`
- `async update_current_actions()`
- `get_current_actions() -> str`
- `async do_prompt(prompt: str) -> str`
```

### Key Features:
- Utilizes an LLM (Language Model) to generate dynamic page content and actions
- Manages game state, including inventory and environment changes
- Handles puzzle-solving mechanics and victory conditions
- Processes user prompts for both predefined actions and open-ended interactions

## Example Gameplay

`call __init__(country="USA", style="HP Lovecraft")`

`$ read get_current_page_number()`

1

`$ call update_current_page()`

The air hung thick with an otherworldly chill as Alex, the solitary engineer, stepped into the gloom of Professor Roko's mansion, its grandiose decay whispering tales of lurking horrors. Shadows danced as the heavy doors clanged shut, revealing a holographic specter of the professor, his eyes glinting with unholy knowledge, beckoning with promises of technological madness and treachery. An echoing voice, laced with malice, spoke of an insidious ASI from some deranged future, and Alex, with his empty inventory, felt the oppressive weight of unseen forces tightening around him, a prelude to a dark and twisted puzzle awaiting his unraveling.

`$ call update_current_actions()`

* Step into the foreboding entrance hall, where shadowy whispers echo and the air hangs heavy with the scent of forgotten tomes. Delve into the mind-bending puzzles that lie within these ancient walls, lest the unfathomable ASI tighten its insidious grip upon your reality.

`call do_prompt("enter the entrance hall")`

Alex cautiously advances deeper into the mansion, entering the entrance hall. The atmosphere is thick with unease, but the promise of knowledge drives him forward.

`$ read get_current_page_number()`

2

`$ call update_current_page()`

The air is thick with an unnameable dread as you stand in the cavernous entrance hall, shadows dancing in the flickering light of a solitary chandelier. Roko's holographic visage flickers urgently, eyes glinting with a manic fervor, imploring you to decipher the fetid mysteries that lurk behind the doors that loom like unblinking eyes. Each creak of the floorboards beneath your feet echoes with an ominous portent, a reminder that time ebbs like the tide, and an inscrutable force coils tighter in the depths of this cursed abode.

`$ call update_current_actions()`

* Choose the Left door to the Library: Step into a realm where the musty scent of ancient tomes cloaks the air, whispering secrets of eldritch knowledge that may drive a man to madness.
* Choose the Center door to the Laboratory: Cross the threshold into a chamber steeped in grotesque experiments and alchemical apparatus, where shadows linger like the ghosts of those who dared to defy nature's laws.
* Choose the Right door to the Study: Enter a sanctuary of decaying leather and ink-stained parchment, where the fevered musings of a tormented mind may provoke both enlightenment and horror.
* Choose the Door leading to Professor Roko's personal study: Approach the portal to his private sanctum, where the line between genius and insanity blurs amidst the relics of a dark intelligence.
* Take the Staircase to the upper floor: Ascend the creaking steps, each groan a ghostly lament, toward a realm where the air thickens with foreboding and the truth may lurk just beyond sight.

`cal do_prompt("enter the center door to the laboratory")`

You push open the center door, and the thick air of the entrance hall gives way to the cold sterility of the laboratory. Strange devices and flickering screens surround you, hinting at the wonders and horrors that lie within.

`page`

Beneath the flickering glow of phosphorescent lights, the air in the laboratory thrummed with a quiet menace, as two astoundingly lifelike robotic guardians loomed over a shimmering vault imbued with an eerie, metallic scent reminiscent of a forgotten age. A palpable sense of dread coiled around the empty grasp of my hands, void of any instruments save for the persistent whisper of dread that echoed through my mind—what horrors lay entombed within those impenetrable confines? Outside, the desolate landscape of the American South bore witness to this unnatural sanctuary, a grotesque fusion of ancient mystery and future terrors, beckoning only the foolhardy or the damned to plumb its depths. Guard 1 (lying only for uranium) says 'The materials are either uranium or thorium,' Guard 2 (lying only for plutonium) says 'The secret material is plutonium'; solve their statements to determine the correct radioactive material and sever the ASI's timeline connection.

`actions`

* With trembling fingers, you must discern the correct element, unraveling the eldritch secrets entwined in this arcane puzzle.
* With a heart heavy with foreboding, turn back to the Entrance Hall, the air thick with unseen specters, and select a new room to explore the mysteries that lurk within. To solve this puzzle you must clearly say if the secret material mentioned by the Guards is plutonium, uranium or thorium, and be logically consistent with that what the Guards have said.

`choose the thorium material`

The user chose the thorium as the material hidden in the vault. The decision is based on the logic that Guard 1, who lies only about uranium, said the material could be uranium or thorium. This means it can't be uranium because he lies about it, so it could potentially be thorium. Guard 2, who lies about plutonium, stated the material was plutonium, so it can't be that. Thus, by process of exclusion, thorium is the only logical possibility.

**Laboratory Puzzle Solved!**

`go back to entrance hall`

You leave the sepulchral depths of Professor Roko's laboratory and make your way back to the familiar surroundings of the Entrance Hall.

'go into left door'

You push open the left door, venturing into an area draped in shadow and the scent of old paper. This door leads you deeper into the mansion's secrets...

## NFT Prototype for Game Awards: LlmErc721

This NFT prototype allows for the integration of a game award system into the RokosMansion game, where players can receive an NFT token upon successfully completing the game.

### Class: LlmErc721

Implements an ERC721-like NFT contract using LLM for ownership transfers.

### Attributes:
- `_name`: Name of the NFT collection
- `_symbol`: Symbol of the NFT collection
- `_contract_address`: Address of the contract/game system
- `_owners`: Mapping of token IDs to owners
- `_balances`: Mapping of owners to token balances
- `_token_approvals`: Mapping of token approvals
- `_operator_approvals`: Mapping of operator approvals

### Public Methods:
```markdown
- `async safe_transfer(from_address: str, to_address: str, token_id: int) -> None`
- `balance_of(owner: str) -> int`
- `owner_of(token_id: int) -> str`
- `name() -> str`
- `symbol() -> str`
- `approve(to_address: str, token_id: int) -> None`
- `get_approved(token_id: int) -> str`
- `is_approved_for_all(owner: str, operator: str) -> bool`
- `set_approval_for_all(owner: str, operator: str, approved: bool) -> None`
- `async player_wins(player_address: str) -> None`
```

### Key Features:
- Uses an LLM to manage token ownership transfers
- Implements basic ERC721 functions like balance checking and approvals
- Includes a `player_wins` function to award an NFT upon game completion
- Utilizes the EquivalencePrinciple for validating LLM-based transfers












