import sqlite3

# Construct the database structure:
# We track:
# - mods: Collections of game content; the base game is a 'mod' as well.
# - decks: An individual hero/villain/environment deck
# - cards: A single SOTM card.
#
# Every deck belongs to a mod, every card belongs to a card.
#
# The search_name / search_other_name columns hold accent- and case-folded
# copies of the corresponding name columns (see normalize.normalize_for_search)
# so that searches are accent-insensitive.

SCHEMA = """
DROP TABLE IF EXISTS mods;
DROP TABLE IF EXISTS decks;
DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS abilities;

CREATE TABLE mods (
	key INTEGER PRIMARY KEY NOT NULL,
	name VARCHAR(255) UNIQUE NOT NULL COLLATE NOCASE,
	search_name VARCHAR(255),
	authors VARCHAR(255) NOT NULL,
	link VARCHAR(255),
	version VARCHAR(255)
);

CREATE TABLE decks (
	key INTEGER PRIMARY KEY NOT NULL,
	mod_key INTEGER NOT NULL,
	name VARCHAR(255) NOT NULL COLLATE NOCASE,
	search_name VARCHAR(255),
	deck_type VARCHAR(255) NOT NULL,

	FOREIGN KEY(mod_key) REFERENCES mods(key)
);

CREATE TABLE cards (
	key INTEGER PRIMARY KEY NOT NULL,
	deck_key INTEGER NOT NULL,
	name VARCHAR(255) NOT NULL COLLATE NOCASE,
	other_name VARCHAR(255) COLLATE NOCASE,
	search_name VARCHAR(255),
	search_other_name VARCHAR(255),
	hitpoints INTEGER,
	text VARCHAR(255),
	gameplay VARCHAR(255),
	setup VARCHAR(255),
	advanced VARCHAR(255),
	challenge VARCHAR(255),
	keywords VARCHAR(255),
	count INTEGER NOT NULL,
	back_side INTEGER,
	front_side INTEGER,
	flavour_text VARCHAR(255),
	flavour_reference VARCHAR(255),
	footer_title VARCHAR(255),
	footer_body VARCHAR(255),
	magic_numbers VARCHAR(255),

	FOREIGN KEY(deck_key) REFERENCES decks(key)
	FOREIGN KEY(back_side) REFERENCES cards(key)
	FOREIGN KEY(front_side) REFERENCES cards(key)
);

CREATE TABLE abilities (
	key INTEGER PRIMARY KEY NOT NULL,
	card_key INTEGER NOT NULL,
	ability_name VARCHAR(255) NOT NULL,
	text VARCHAR(255),

	FOREIGN KEY(card_key) REFERENCES cards(key)
);
"""

def create_schema(cur):
	"""Create the (empty) SOTM schema on the given cursor, dropping any existing tables first."""
	cur.executescript(SCHEMA)

if __name__ == "__main__":
	db = sqlite3.connect("sotm_cards.db")
	cur = db.cursor()
	create_schema(cur)
	db.commit()
	db.close()
