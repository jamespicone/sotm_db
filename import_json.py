import sqlite3
import sys
import os
import glob
import json

# Walk over the directory passed, or cwd if no directory passed
directory_to_use = os.getcwd()
if (len(sys.argv) > 1): directory_to_use = sys.argv[1]

directory_to_use = os.path.abspath(directory_to_use)

print(f"Importing mod content from {directory_to_use}")

# Load DB
db = sqlite3.connect("sotm_cards.db")
cur = db.cursor()

# Find the manifest
def get_manifest(dir_to_use):
	possible_manifests = list(glob.iglob(os.path.join(dir_to_use, "**", "Manifest.json"), recursive=True))
	if (len(possible_manifests) != 1):
		if (len(possible_manifests) == 0):
			print("No manifests found.")
			sys.exit(1)
		else:
			print(f"Several possible manifests found: {', '.join(possible_manifests)}. Do only one mod at a time.")
			sys.exit(1)

	return possible_manifests[0]

def get_decklists(dir_to_use):
	return list(glob.iglob(os.path.join(dir_to_use, "**", "*DeckList*.json"), recursive=True))

def load_manifest(dir_to_use):
	manifest_filename = get_manifest(dir_to_use)
	try:
		with open(manifest_filename, "r", encoding="utf-8") as manifest_file:
			manifest = json.load(manifest_file)
		
			if not ("title" in manifest):
				print(f"No 'title' in mod manifest {manifest_filename}")

			if not ("author" in manifest):
				print(f"No 'author' in mod manifest {manifest_filename}")

			return manifest
	except BaseException as err:
		print(f"Failed to interpret {manifest_filename} as a mod manifest: {err}")

def get_mod_key(manifest):
	cur.execute("INSERT OR IGNORE INTO mods (name, authors) VALUES(?, ?);", ( manifest["title"], manifest["author"] ))
	cur.execute("UPDATE mods SET authors = ? WHERE name = ?;", ( manifest["title"], manifest["author"] ))
	key = cur.execute("SELECT key FROM mods WHERE name = ?;",  ( manifest["title"], )).fetchone()

	cur.execute("DELETE FROM abilities WHERE card_key in (SELECT key FROM cards WHERE deck_key IN (SELECT key FROM decks WHERE mod_key = ?));", ( key[0], ))
	cur.execute("DELETE FROM cards WHERE deck_key IN (SELECT key FROM decks WHERE mod_key = ?);", ( key[0], ))
	cur.execute("DELETE FROM decks WHERE mod_key = ?;", ( key[0], ))
	
	return key[0]

manifest = load_manifest(directory_to_use)
mod_key = get_mod_key(manifest)
print(f"Entry for {manifest['title']} has key {mod_key}")

decklists = get_decklists(directory_to_use)
print(f"Found {len(decklists)} decklist files to inspect")

def read_text_list(node, key):
	element = node.get(key)
	if isinstance(element, list):
		return "\n".join(element).replace("{BR}", "\n")

	return element

def import_card_with_fields(card, deck_key, text_key, gameplay_key, advanced_key, challenge_key, hitpoints_key, powers_key, abilities_key, incap_key):
	title = card["title"]
	text = read_text_list(card, text_key)
	gameplay = read_text_list(card, gameplay_key)
	advanced = read_text_list(card, advanced_key)
	challenge = read_text_list(card, challenge_key)
	keywords = ", ".join(card.get("keywords", []))
	hitpoints = card.get(hitpoints_key)
	count = card.get("count", 1)
	incaps = None
	if incap_key != None:
		incaps = card.get(incap_key)

	if text == None and gameplay == None and advanced == None and challenge == None and hitpoints == None and not isinstance(incaps, list):
		return None

	print(f"{title}: {text}")
	card_key = cur.execute("INSERT INTO cards (name, hitpoints, text, gameplay, advanced, challenge, keywords, count, deck_key) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING key;",
		(title, hitpoints, text, gameplay, advanced, challenge, keywords, count, deck_key)
	).fetchone()[0]

	powers = card.get(powers_key)
	if isinstance(powers, list):
		for power in powers:
			cur.execute("INSERT INTO abilities (card_key, ability_name, text) VALUES(?, ?, ?);",
				(card_key, "power", power.replace("{BR}", "\n"))
			)

	if isinstance(incaps, list):
		for incap in incaps:
			cur.execute("INSERT INTO abilities (card_key, ability_name, text) VALUES(?, ?, ?);",
				(card_key, "incap", incap.replace("{BR}", "\n"))
			)

	if abilities_key != None:
		abilities = card.get(abilities_key)
		if isinstance(abilities, list):
			for ability in abilities:
				name = ability.get("name")
				ability_text = ability.get("text").replace("{BR}", "\n")
				cur.execute("INSERT INTO abilities (card_key, ability_name, text) VALUES(?, ?, ?);",
					(card_key, name, ability_text)
				)

	return card_key

def import_card(card, deck_key):
	front_key = import_card_with_fields(
		card, deck_key,
		"body",
		"gameplay",
		"advanced",
		"challengeText",
		"hitpoints",
		"powers",
		"activatableAbilities",
		None
	)

	back_key = import_card_with_fields(
		card, deck_key,
		"flippedBody",
		"flippedGameplay",
		"flippedAdvanced",
		"flippedChallengeText",
		"flippedHitPoints",
		"flippedPowers",
		None,
		"incapacitatedAbilities"
	)

	if front_key != None and back_key != None:
		cur.execute("UPDATE cards SET back_side = ? WHERE key = ?;", (back_key, front_key))
		cur.execute("UPDATE cards SET front_side = ? WHERE key = ?;", (front_key, back_key))

def import_decklist(decklist_filename, mod_key):
	try:
		with open(decklist_filename, "r", encoding="utf-8") as decklist_file:
			decklist = json.load(decklist_file)

			deckname = decklist["name"]
			decktype = decklist["kind"]

			print (f"Decklist {decklist_filename} contains {decktype} deck \"{deckname}\"")

			deck_key =  cur.execute("INSERT INTO decks (name, deck_type, mod_key) VALUES(?, ?, ?) RETURNING key;", (deckname, decktype, mod_key )).fetchone()[0]

			cards = decklist["cards"]
			for card in cards:
				import_card(card, deck_key)

			promos = decklist.get("promoCards", [])
			for promo in promos:
				import_card(promo, deck_key)

	except BaseException as err:
		print(f"Failed to interpret {decklist_filename} as a decklist: {err}")


for decklist in decklists:
	import_decklist(decklist, mod_key)

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

db.commit()
db.close()