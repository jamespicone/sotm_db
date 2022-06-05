import sqlite3

# Construct the database structure:
# We track:
# - mods: Collections of game content; the base game is a 'mod' as well.
# - decks: An individual hero/villain/environment deck
# - cards: A single SOTM card.
#
# Every deck belongs to a mod, every card belongs to a deck.

db = sqlite3.connect("sotm_cards.db")
cur = db.cursor()

cur.execute("DROP TABLE IF EXISTS mods;")
cur.execute("DROP TABLE IF EXISTS decks;")
cur.execute("DROP TABLE IF EXISTS cards;")

# Table mods
# - PK
# - Name
# - Authors
# - Link
cur.execute("""
CREATE TABLE mods (
	key INTEGER PRIMARY KEY NOT NULL,
	name VARCHAR(255) UNIQUE NOT NULL COLLATE NOCASE,
	authors VARCHAR(255) NOT NULL,
	link VARCHAR(255)
);
""")

# Table decks
# - PK
# - mod id
# - name
# - deck_type
cur.execute("""
CREATE TABLE decks (
	key INTEGER PRIMARY KEY NOT NULL,
	mod_key INTEGER NOT NULL,
	name VARCHAR(255) NOT NULL COLLATE NOCASE,
	deck_type VARCHAR(255) NOT NULL,

	FOREIGN KEY(mod_key) REFERENCES mods(key)
);
""")

# Table cards
# - PK
# - deck id
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
# - Card flavour text & flavour reference (may be quotes?)
cur.execute("""
CREATE TABLE cards (
	key INTEGER PRIMARY KEY NOT NULL,
	deck_key INTEGER NOT NULL,
	name VARCHAR(255) NOT NULL COLLATE NOCASE,
	text VARCHAR(255),

	FOREIGN KEY(deck_key) REFERENCES decks(key)
);
""")

db.commit()
db.close()