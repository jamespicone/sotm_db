import sqlite3
import sys
import os
import glob
import json
from flashtext import KeywordProcessor

icon_replacer = KeywordProcessor(case_sensitive=True)
icon_replacer.add_keyword("{BR}", "\n")
icon_replacer.add_keyword("{crocodile}", "🐊")
icon_replacer.add_keyword("{rhinoceros}", "🦏")
icon_replacer.add_keyword("{gazelle}", "🦌")
icon_replacer.add_keyword("{magic}", "✨")
icon_replacer.add_keyword("{filter}", "👽")
icon_replacer.add_keyword("{sun}", "☀")
icon_replacer.add_keyword("{elements}", "✋")
icon_replacer.add_keyword("{ankh}", "☥")
icon_replacer.add_keyword("{avian}", "🐦")
icon_replacer.add_keyword("{arcana}", "⛤")
icon_replacer.add_keyword("{SimurghDanger}", "#️⃣")
icon_replacer.add_keyword("{SimurghDanger1}", "1️⃣")
icon_replacer.add_keyword("{SimurghDanger2}", "2️⃣")
icon_replacer.add_keyword("{SimurghDanger3}", "3️⃣")
icon_replacer.add_keyword("{SimurghDanger4}", "4️⃣")
icon_replacer.add_keyword("{SimurghDanger5}", "5️⃣")
icon_replacer.add_keyword("{SimurghDanger6}", "6️⃣")
icon_replacer.add_keyword("{SimurghDanger7}", "7️⃣")
icon_replacer.add_keyword("{SimurghDanger8}", "8️⃣")
icon_replacer.add_keyword("{SimurghDanger9}", "9️⃣")
icon_replacer.add_keyword("[b]", "**")
icon_replacer.add_keyword("[/b]", "**")
icon_replacer.add_keyword("[u]", "__")
icon_replacer.add_keyword("[/u]", "__")
icon_replacer.set_non_word_boundaries("")

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

def replace_braced_stuff(text):
	return icon_replacer.replace_keywords(text)

def read_text_list(node, key):
	element = node.get(key)
	if isinstance(element, list):
		return replace_braced_stuff("\n".join(element))

	if isinstance(element, str):
		return replace_braced_stuff(element)

	return element

def import_card_with_fields(card, deck_key, is_back):	
	front_keys = {
		"text": "body",
		"gameplay": "gameplay",
		"advanced": "advanced",
		"challenge": "challengeText",
		"hitpoints": "hitpoints",
		"powers": "powers",
		"abilities": "activatableAbilities",
		"incaps": None,
		"keywords": "keywords"
	}

	back_keys = {
		"text": "flippedBody",
		"gameplay": "flippedGameplay",
		"advanced": "flippedAdvanced",
		"challenge": "flippedChallengeText",
		"hitpoints": "flippedHitPoints",
		"powers": "flippedPowers",
		"abilities": None,
		"incaps": "incapacitatedAbilities",
		"keywords": "flippedKeywords"
	}

	keys_to_use = front_keys
	if is_back:
		keys_to_use = back_keys

	title = card["title"]
	title = card.get("alternateTitle", title)
	title = card.get("promoTitle", title)
	text = read_text_list(card, keys_to_use["text"])
	gameplay = read_text_list(card, keys_to_use["gameplay"])
	advanced = read_text_list(card, keys_to_use["advanced"])
	challenge = read_text_list(card, keys_to_use["challenge"])
	keywords = replace_braced_stuff(", ".join(card.get(keys_to_use["keywords"], [])))
	hitpoints = card.get(keys_to_use["hitpoints"])
	count = card.get("count", 1)
	incaps = None
	if keys_to_use["incaps"] != None:
		incaps = card.get(keys_to_use["incaps"])

	if is_back and text == None and gameplay == None and advanced == None and challenge == None and hitpoints == None and not isinstance(incaps, list) and keywords == "":
		return None

	front_hitpoints = card.get(front_keys["hitpoints"])
	if card.get("flippedShowHitpoints", True):
		hitpoints = front_hitpoints

	if is_back and keywords == "":
		keywords = replace_braced_stuff(", ".join(card.get(front_keys["keywords"], [])))

	print(f"{title}: {text}")
	card_key = cur.execute("INSERT INTO cards (name, hitpoints, text, gameplay, advanced, challenge, keywords, count, deck_key) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING key;",
		(title, hitpoints, text, gameplay, advanced, challenge, keywords, count, deck_key)
	).fetchone()[0]

	powers = card.get(keys_to_use["powers"])
	if isinstance(powers, list):
		for power in powers:
			cur.execute("INSERT INTO abilities (card_key, ability_name, text) VALUES(?, ?, ?);",
				(card_key, "power", replace_braced_stuff(power))
			)

	if isinstance(incaps, list):
		for incap in incaps:
			cur.execute("INSERT INTO abilities (card_key, ability_name, text) VALUES(?, ?, ?);",
				(card_key, "incap", replace_braced_stuff(incap))
			)

	if keys_to_use["abilities"] != None:
		abilities = card.get(keys_to_use["abilities"])
		if isinstance(abilities, list):
			for ability in abilities:
				name = ability.get("name")
				ability_text = replace_braced_stuff(ability.get("text"))
				cur.execute("INSERT INTO abilities (card_key, ability_name, text) VALUES(?, ?, ?);",
					(card_key, name, ability_text)
				)

	return card_key

def import_card(card, deck_key):
	front_key = import_card_with_fields(card, deck_key, False)
	back_key = import_card_with_fields(card, deck_key, True)

	if front_key != None and back_key != None:
		cur.execute("UPDATE cards SET back_side = ? WHERE key = ?;", (back_key, front_key))
		cur.execute("UPDATE cards SET front_side = ? WHERE key = ?;", (front_key, back_key))

def import_decklist(decklist_filename, mod_key):
	try:
		with open(decklist_filename, "r", encoding="utf-8-sig") as decklist_file:
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

			subdecks = decklist.get("subdecks", [])
			for subdeck in subdecks:
				subdeck_cards = subdeck.get("cards", [])
				for card in subdeck_cards:
					import_card(card, deck_key)

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