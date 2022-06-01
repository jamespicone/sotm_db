import sqlite3

# Cards need:
# - Card name
# - Hitpoints (poss. None)
# - Keywords list (poss. empty)
# - Card text (poss. None)
# - Card "Gameplay" text (poss. None)
# - Card "Setup" text (poss. None)
# - Card "Advanced" text (poss. None)
# - Card "Challenge" text (poss. None)
# - Card powers (poss. empty)
# - Card abilities (poss. empty)
# - Card back (another Card instance for the front side; self for the flipped side)
# - Card front (another Card instance for the flipped side; self for the front side)
# - Card count (number of copies of this card in the deck)
# - Card deck name
# - Card mod name
# - Card flavour text & flavour reference (may be quotes?)
#
# Extract from JSON files
# Remember 'body' text is used for power names on character cards.