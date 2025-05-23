﻿import sqlite3
import sys
import os
import glob
import json5
from flashtext import KeywordProcessor

icon_replacer = KeywordProcessor(case_sensitive=True)
icon_replacer.add_keyword("{BR}", "\n")
icon_replacer.add_keyword("{br}", "\n")
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
icon_replacer.add_keyword("[i]", "*")
icon_replacer.add_keyword("[/i]", "*")
icon_replacer.add_keyword("[u]", "__")
icon_replacer.add_keyword("[/u]", "__")
icon_replacer.add_keyword("[sc]", "**")
icon_replacer.add_keyword("[/sc]", "**")
icon_replacer.add_keyword("[suc]", "**")
icon_replacer.add_keyword("[/suc]", "**")
icon_replacer.add_keyword("[bi]", "***")
icon_replacer.add_keyword("[/bi]", "***")
icon_replacer.add_keyword("{d6_1}", "⚀")
icon_replacer.add_keyword("{d6_2}", "⚁")
icon_replacer.add_keyword("{d6_3}", "⚂")
icon_replacer.add_keyword("{d6_4}", "⚃")
icon_replacer.add_keyword("{d6_5}", "⚄")
icon_replacer.add_keyword("{d6_6}", "⚅")
icon_replacer.add_keyword("{Bear}", "🧸")
icon_replacer.add_keyword("{Blade}", "🗡")
icon_replacer.add_keyword("{Blood}", "🩸")
icon_replacer.add_keyword("{Blood}", "🩸")
icon_replacer.add_keyword("{Clue}", "👁")
icon_replacer.add_keyword("{Crown}", "👑")
icon_replacer.add_keyword("{Danger}", "🔱")
icon_replacer.add_keyword("{Dog}", "🐶")
icon_replacer.add_keyword("{ErlenFlaskEffect}", "🧪")
icon_replacer.add_keyword("{Fist}", "👊")
icon_replacer.add_keyword("{Past}", "🔷")
icon_replacer.add_keyword("{Future}", "🔶")
icon_replacer.add_keyword("{Madness}", "🧠")
icon_replacer.add_keyword("{Mask}", "👺")
icon_replacer.add_keyword("{Rad}", "☢")
icon_replacer.add_keyword("{ShiftLLL}", "<<<")
icon_replacer.add_keyword("{ShiftLL}", "<<")
icon_replacer.add_keyword("{ShiftL}", "<")
icon_replacer.add_keyword("{ShiftRRR}", ">>>")
icon_replacer.add_keyword("{ShiftRR}", ">>")
icon_replacer.add_keyword("{ShiftR}", ">")
icon_replacer.add_keyword("{Skull}", "💀")
icon_replacer.add_keyword("{Spider}", "🕷")
icon_replacer.add_keyword("{Tattle}", "Tt")
icon_replacer.add_keyword("{TriskDemonSymbol}", "👿")
icon_replacer.add_keyword("{club}", "♣")
icon_replacer.add_keyword("{diamond}", "♦️")
icon_replacer.add_keyword("{heart}", "♥")
icon_replacer.add_keyword("{spade}", "♠")
icon_replacer.add_keyword("{dragon}", "🐉")
icon_replacer.add_keyword("{buccellini}", "🪙")
icon_replacer.add_keyword("{bulletpoint}", "§")
icon_replacer.add_keyword("{tlatoani}", "🌵")
icon_replacer.add_keyword("{healthy}", "🙂")
icon_replacer.add_keyword("{hurt}", "😠")
icon_replacer.add_keyword("{H}", "Ⓗ")
icon_replacer.add_keyword("{IconH}", "Ⓗ")
icon_replacer.add_keyword("{Bass}", "🎻") # there's no bass emoji; violin is what i'm going to go with
icon_replacer.add_keyword("{Vocal}", "🎤")
icon_replacer.add_keyword("{Guitar}", "🎸")
icon_replacer.add_keyword("{Drum}", "🥁")
icon_replacer.add_keyword("{BetriceMagic}", "🌙")
icon_replacer.add_keyword("{iceSmall}", "❄")
icon_replacer.add_keyword("{ice}", "❄")

icon_replacer.set_non_word_boundaries("")

import re

bold_replacer = re.compile("\[b=[^\r\n\]]*\]|\[/b\]")
text_size_replacer = re.compile("\[y=[^\r\n\]]*\]|\[/y\]")
h_equation_replacer = re.compile("\{([0-9 +\-*]*H[0-9 +\-*]*)\}")

tt_id_replacer = re.compile(".*\.(.*)DeckList\.json")

turntaker_id_and_name = {}
card_id_and_name = {}

def replace_braced_stuff(text):
	global turntaker_id_and_name
	global card_id_and_name

	while True:
		prev = text
		text = icon_replacer.replace_keywords(text)
		if prev == text:
			break

	text = bold_replacer.sub("**", text)
	text = text_size_replacer.sub("", text)

	def h_equation_replace(match):
		return match.group(1).replace("H", "Ⓗ")

	text = h_equation_replacer.sub(h_equation_replace, text)

	if len(turntaker_id_and_name) > 0:
		text = text.replace("{" + list(turntaker_id_and_name.keys())[0] + "}", "*" + list(turntaker_id_and_name.values())[0] + "*")

	if len(turntaker_id_and_name) > 0:		
		text = text.replace("{" + list(card_id_and_name.keys())[0] + "}", "*" + list(card_id_and_name.values())[0] + "*")

	return text

# Find the manifest
def get_manifest(dir_to_use):
	possible_manifests = list(glob.iglob(os.path.join(dir_to_use, "**", "Manifest.json"), recursive=True))
	if (len(possible_manifests) != 1):
		if (len(possible_manifests) == 0):
			print("No manifests found.")
			return None
		else:
			print(f"Several possible manifests found: {', '.join(possible_manifests)}. Do only one mod at a time.")
			return None

	return possible_manifests[0]

def get_decklists(dir_to_use):
	return list(glob.iglob(os.path.join(dir_to_use, "**", "*DeckList*.json"), recursive=True))

def load_manifest(dir_to_use):
	manifest_filename = get_manifest(dir_to_use)
	if manifest_filename == None:
		return None

	try:
		with open(manifest_filename, "r", encoding="utf-8") as manifest_file:
			manifest = json5.load(manifest_file)
		
			if not ("title" in manifest):
				print(f"No 'title' in mod manifest {manifest_filename}")

			if not ("author" in manifest):
				print(f"No 'author' in mod manifest {manifest_filename}")

			print(f"Manifest loaded as {manifest}")

			return manifest
	except BaseException as err:
		print(f"Failed to interpret {manifest_filename} as a mod manifest: {err}")

def get_mod_key(manifest):
	print(f"Manifest: {manifest}")
	cur.execute("INSERT OR IGNORE INTO mods (name, authors, version) VALUES(?, ?, ?);", ( manifest["title"], manifest["author"], manifest.get("version", "") ))
	cur.execute("UPDATE mods SET authors = ? WHERE name = ?;", ( manifest["title"], manifest["author"] ))
	cur.execute("UPDATE mods SET version = ? WHERE name = ?;", ( manifest["title"], manifest.get("version", "") ))
	key = cur.execute("SELECT key FROM mods WHERE name = ?;",  ( manifest["title"], )).fetchone()

	cur.execute("DELETE FROM abilities WHERE card_key in (SELECT key FROM cards WHERE deck_key IN (SELECT key FROM decks WHERE mod_key = ?));", ( key[0], ))
	cur.execute("DELETE FROM cards WHERE deck_key IN (SELECT key FROM decks WHERE mod_key = ?);", ( key[0], ))
	cur.execute("DELETE FROM decks WHERE mod_key = ?;", ( key[0], ))
	
	return key[0]

def read_text_list(node, key):
	element = node.get(key)
	if isinstance(element, list):
		return replace_braced_stuff("\n".join(element))

	if isinstance(element, str):
		return replace_braced_stuff(element)

	return element

def read_keywords(node, key):
	element = node.get(key, [])
	if isinstance(element, list):
		return replace_braced_stuff(", ".join(element))

	if isinstance(element, str):
		return replace_braced_stuff(element)

	return ""

def import_card_with_fields(card, deck_key, is_back):
	global turntaker_id_and_name
	global card_id_and_name

	front_keys = {
		"text": "body",
		"setup": "setup",
		"gameplay": "gameplay",
		"advanced": "advanced",
		"challenge": "challengeText",
		"hitpoints": "hitpoints",
		"powers": "powers",
		"abilities": "activatableAbilities",
		"incaps": None,
		"keywords": "keywords",
		"footerTitle": "footerTitle",
		"footerBody": "footerBody",
		"magicNumbers": "magicNumbers"
	}

	back_keys = {
		"text": "flippedBody",
		"setup": None,
		"gameplay": "flippedGameplay",
		"advanced": "flippedAdvanced",
		"challenge": "flippedChallengeText",
		"hitpoints": "flippedHitPoints",
		"powers": "flippedPowers",
		"abilities": None,
		"incaps": "incapacitatedAbilities",
		"keywords": "flippedKeywords",
		"footerTitle": None,
		"footerBody": None,
		"magicNumbers": None
	}

	keys_to_use = front_keys
	if is_back:
		keys_to_use = back_keys

	title = card["title"]
	title = card.get("alternateTitle", title)
	title = card.get("promoTitle", title)
	front_title = title
	if is_back:
		title = card.get("flippedTitle", title)

	identifier = card["identifier"]
	card_id_and_name = { identifier: title }

	text = read_text_list(card, keys_to_use["text"])
	gameplay = read_text_list(card, keys_to_use["gameplay"])
	advanced = read_text_list(card, keys_to_use["advanced"])
	challenge = read_text_list(card, keys_to_use["challenge"])
	keywords = read_keywords(card, keys_to_use["keywords"])
	hitpoints = card.get(keys_to_use["hitpoints"])
	count = card.get("count", 1)
	incaps = None
	if keys_to_use["incaps"] != None:
		incaps = card.get(keys_to_use["incaps"])

	footerTitle = None
	if keys_to_use["footerTitle"] != None:
		footerTitle = card.get(keys_to_use["footerTitle"])

	footerBody = None
	if keys_to_use["footerBody"] != None:
		footerBody = read_text_list(card, keys_to_use["footerBody"])

	magicNumbers = None
	if keys_to_use["magicNumbers"] != None:
		element = card.get(keys_to_use["magicNumbers"])
		if element != None:
			magicNumbers = ", ".join(str(x) for x in element)

	setup = None
	if keys_to_use["setup"] != None:
		setup = read_text_list(card, keys_to_use["setup"])

	if is_back and text == None and gameplay == None and advanced == None and challenge == None and hitpoints == None and not isinstance(incaps, list) and keywords == "" and front_title == title:
		return ( None, None )

	front_hitpoints = card.get(front_keys["hitpoints"])
	if card.get("flippedShowHitpoints", True):
		hitpoints = front_hitpoints

	if is_back and keywords == "":
		keywords = keywords = read_keywords(card, front_keys["keywords"])

	card_key = cur.execute("INSERT INTO cards (name, hitpoints, text, setup, gameplay, advanced, challenge, keywords, count, deck_key, footer_title, footer_body, magic_numbers) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING key;",
		(title, hitpoints, text, setup, gameplay, advanced, challenge, keywords, count, deck_key, footerTitle, footerBody, magicNumbers)
	).fetchone()[0]

	def import_power(powertext):
		cur.execute("INSERT INTO abilities (card_key, ability_name, text) VALUES(?, ?, ?);",
			(card_key, "power", replace_braced_stuff(powertext))
		)

	powers = card.get(keys_to_use["powers"])
	if isinstance(powers, list):
		for power in powers:
			import_power(power)

	if isinstance(powers, str):
		import_power(powers)

	if isinstance(incaps, list):
		for incap in incaps:
			if not isinstance(incap, str):
				incap = incap.get("text")

			if incap == None: continue

			cur.execute("INSERT INTO abilities (card_key, ability_name, text) VALUES(?, ?, ?);",
				(card_key, "incap", replace_braced_stuff(incap))
			)

	if keys_to_use["abilities"] != None:
		abilities = card.get(keys_to_use["abilities"])
		if isinstance(abilities, list):
			for ability in abilities:
				name = replace_braced_stuff(ability.get("name"))
				ability_text = replace_braced_stuff(ability.get("text"))
				cur.execute("INSERT INTO abilities (card_key, ability_name, text) VALUES(?, ?, ?);",
					(card_key, name, ability_text)
				)

	return ( card_key, title )

def import_card(card, deck_key):
	front_key, front_title = import_card_with_fields(card, deck_key, False)
	back_key, back_title = import_card_with_fields(card, deck_key, True)

	if front_key != None and back_key != None:
		cur.execute("UPDATE cards SET back_side = ? WHERE key = ?;", (back_key, front_key))
		cur.execute("UPDATE cards SET other_name= ? WHERE key = ?;", (back_title, front_key))
		cur.execute("UPDATE cards SET front_side = ? WHERE key = ?;", (front_key, back_key))
		cur.execute("UPDATE cards SET other_name = ? WHERE key = ?;", (front_title, back_key))

def import_decklist(decklist_filename, mod_key):
	global turntaker_id_and_name
	global card_id_and_name

	try:
		with open(decklist_filename, "r", encoding="utf-8-sig", errors="ignore") as decklist_file:
			decklist = json5.load(decklist_file)

			deckname = decklist.get("name")
			decktype = decklist.get("kind")

			if deckname == None or decktype == None:
				# Could be PromoDeckLists.
				# If it is, we expect a series of keys that contain an array of cards. If we find that's the case, we assume we've got PromoDeckLists.
				# Don't want to go off filename for defensive programming reasons.
				deckname = "Promos"
				decktype = "Promos"

				turntaker_id_and_name = {}

				deck_key = cur.execute("INSERT INTO decks (name, deck_type, mod_key) VALUES(?, ?, ?) RETURNING key;", (deckname, decktype, mod_key )).fetchone()[0]
							
				for key, cards in decklist.items():
					for card in cards:
						import_card(card, deck_key)

			else:
				identifier = tt_id_replacer.search(decklist_filename).group(1)
				turntaker_id_and_name = { identifier : deckname }

				print (f"Decklist {decklist_filename} contains {decktype} deck \"{deckname}\" ID \"{identifier}\"")

				deck_key = cur.execute("INSERT INTO decks (name, deck_type, mod_key) VALUES(?, ?, ?) RETURNING key;", (deckname, decktype, mod_key )).fetchone()[0]

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
		print(f"!!! Failed to interpret {decklist_filename} as a decklist: {err}")

def import_mod(directory_to_use):
	print(f"Importing mod in {directory_to_use}")

	manifest = load_manifest(directory_to_use)
	if manifest == None:
		return

	mod_key = get_mod_key(manifest)
	print(f"Entry for {manifest['title']} has key {mod_key}")

	decklists = get_decklists(directory_to_use)
	print(f"Found {len(decklists)} decklist files to inspect")

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

# Walk over the directory passed, or cwd if no directory passed
directory_to_use = os.getcwd()
if (len(sys.argv) > 1): directory_to_use = sys.argv[1]

dir_to_use = os.path.abspath(directory_to_use)

print(f"Importing all mods in {directory_to_use}")
mod_folders = list(glob.iglob(os.path.join(dir_to_use, "*"), recursive=False))

db = sqlite3.connect("sotm_cards.db")
cur = db.cursor()

for mod_folder in mod_folders:
	import_mod(mod_folder)

db.close()