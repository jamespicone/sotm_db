import sqlite3
import unicodedata
from operator import attrgetter

db = sqlite3.connect("sotm_cards.db")
db.row_factory = sqlite3.Row
cur = db.cursor()

def _merge_card_sides(card_rows, process_func):
	front_sides = [ process_func(row) for row in card_rows if row["front_side"] == None ]
	back_sides = [ process_func(row) for row in card_rows if row["front_side"] != None ]

	for card in back_sides:
		for front in front_sides:
			if card.is_other_side(front):
				card.set_other_side(front)
				front.set_other_side(card)
				break

	return sorted(front_sides, key = attrgetter("sort_key"))

class TextFormatter:
	def __init__(self):
		self.text = ""

	def __str__(self):
		return self.text

	def title(self, title_text):
		self.text += title_text + ":\n"

	def smallbox(self, box_title, box_text):
		self.text += "\t" + box_title + ": " + box_text + "\n"

	def box(self, box_title, box_text):
		self.text += "\t" + box_title + ":\n"

		self.text += "\t\t| " + box_text.replace("\n", "\n\t\t| ")
		self.text += "\n\n"

	def footer(self, footer_text):
		self.text += "(" + footer_text + ")"

class Ability:
	def __init__(self, db_row):
		self.name = db_row["ability_name"]
		self.text = db_row["text"]

class Card:
	def __init__(self, db_row, ability_rows):
		self.title = db_row["name"]
		self.other_title = db_row["other_name"]
		self.text = db_row["text"]
		self.setup = db_row["setup"]
		self.gameplay = db_row["gameplay"]
		self.advanced = db_row["advanced"]
		self.challenge = db_row["challenge"]
		self.hitpoints = db_row["hitpoints"]
		self.count = db_row["count"]
		self.keywords = db_row["keywords"]
		self.abilities = [ Ability(ability) for ability in ability_rows ]
		self.mod = db_row["mod_name"]
		self.deck = db_row["deck_name"]
		self.deck_type = db_row["deck_type"]
		self.sort_key = db_row["key"]
		self.footer_title = db_row["footer_title"]
		self.footer_body = db_row["footer_body"]

		self.card_key = db_row["key"]
		self.other_side = None

		self.is_front = True
		if db_row["front_side"] != None:
			self.is_front = False
			self.sort_key = db_row["front_side"]
			self.other_side_key = db_row["front_side"]
		else:
			self.other_side_key = db_row["back_side"]

		self.is_back = not self.is_front

	def __str__(self):
		return self.title

	def __repr__(self):
		formatter = TextFormatter()
		self.format(formatter)
		return str(formatter)

	def short_name(self):
		ret = f"{self.mod}|{self.deck}|{self.title}"

		if self.is_front_side() and self.other_side != None:
			ret += f" // " + self.other_side.short_name()

		return ret

	def short_card_name(self):
		ret = f"{self.title}"

		if self.is_front_side() and self.other_side != None:
			ret += f" // " + self.other_side.short_card_name()

		return ret

	def is_other_side(self, other):
		return self.card_key == other.other_side_key

	def set_other_side(self, other):
		self.other_side = other

	def is_exact_match(self, command):
		folded_command = unicodedata.normalize('NFC', command.casefold())
		if unicodedata.normalize('NFC', self.title.casefold()) == folded_command:
			return True

		if self.other_side != None and unicodedata.normalize('NFC', self.other_side.title.casefold()) == folded_command:
			return True

		return False

	def is_front_side(self):
		return self.is_front

	def format(self, formatter):
		if self.is_front:
			if self.title == self.other_title or not self.other_title:
				formatter.title(self.title)
			else:
				formatter.title(f"{self.title} (front side of {self.other_title})")
		else:
			if self.title == self.other_title:
				formatter.title(self.title + " (back side)")
			else:
				formatter.title(f"{self.title} (back side of {self.other_title})")
		
		if self.hitpoints:
			formatter.smallbox("HP", str(self.hitpoints))

		formatter.smallbox("Quantity", str(self.count))

		if len(self.keywords) > 0:
			formatter.smallbox("Keywords", self.keywords)

		if self.setup:
			formatter.box("Setup", self.setup)

		if self.text:
			formatter.box("Text", self.text)

		if self.gameplay:
			formatter.box("Gameplay", self.gameplay)

		if self.advanced:
			formatter.box("Advanced", self.advanced)

		if self.challenge:
			formatter.box("Challenge", self.challenge)

		if len(self.abilities) > 0:
			for ability in self.abilities:
				formatter.box(ability.name, ability.text)

		if self.footer_body:
			footer_box_title = "Footer"
			if self.footer_title != None:
				footer_box_title += ": " + self.footer_title

			formatter.box(footer_box_title, self.footer_body)

		formatter.footer(f"Deck: {self.deck}, Mod: {self.mod}, Deck type: {self.deck_type}")

class Deck:
	def __init__(self, db_row, cards):
		self.name = db_row["name"]
		self.deck_type = db_row["deck_type"]
		self.mod = db_row["mod_name"]
		self.card_count = db_row["card_count"]

		def process_card(row):
			return Card(row, [])

		self.cards = _merge_card_sides(cards, process_card)

	def __str__(self):
		return self.name

	def __repr__(self):
		formatter = TextFormatter()
		self.format(formatter)
		return str(formatter)

	def short_name(self):
		return f"{self.mod}|{self.name}"

	def is_exact_match(self, command):
		folded_command = unicodedata.normalize('NFC', command.casefold())
		return unicodedata.normalize('NFC', self.name.casefold()) == folded_command

	def format(self, formatter):
		formatter.title(self.name)

		formatter.smallbox("Deck type", self.deck_type)
		formatter.smallbox("Mod", self.mod)
		formatter.smallbox("Card count", str(self.card_count))

		if len(self.cards) > 0:
			card_list = "\n".join([ card.short_card_name() for card in self.cards])
			formatter.box("Cards", card_list)

class Mod:
	def __init__(self, db_row, decks):
		self.name = db_row["name"]
		self.authors = db_row["authors"]
		self.deck_count = db_row["deck_count"]
		self.version = db_row["version"]
		self.decks = [ Deck(x, []) for x in decks ]

	def __str__(self):
		return self.name

	def __repr__(self):
		formatter = TextFormatter()
		self.format(formatter)
		return str(formatter)

	def short_name(self):
		return self.name

	def is_exact_match(self, command):
		folded_command = unicodedata.normalize('NFC', command.casefold())
		return unicodedata.normalize('NFC', self.name.casefold()) == folded_command

	def format(self, formatter):
		formatter.title(self.name)

		formatter.smallbox("Authors", self.authors)
		formatter.smallbox("Version", self.version)
		formatter.smallbox("Deck count", str(self.deck_count))

		if len(self.decks) > 0:
			types = set([ deck.deck_type for deck in self.decks ])

			for decktype in types:
				deck_list = "\n".join([ deck.name for deck in self.decks if deck.deck_type == decktype])
				formatter.box(decktype + " decks", deck_list)

def generate_search_string(search_string):
	search_string = search_string.replace('%', '\%')
	search_string = search_string.replace('_', '\_')
	search_string = "%" + search_string + "%"
	return search_string


def _card_query():
	return "SELECT cards.*, decks.deck_type, decks.name AS deck_name, mods.name AS mod_name FROM cards INNER JOIN decks ON decks.key == cards.deck_key INNER JOIN mods ON mods.key == decks.mod_key "

def _deck_query():
	return "SELECT decks.*, mods.name as mod_name, (SELECT count(*) FROM cards WHERE deck_key == decks.key AND front_side is NULL) as card_count FROM decks INNER JOIN mods on decks.mod_key == mods.key "

def search_cards(search_string, deck_hint = None):
	"""
	Returns an iterable of Cards with title matching 'search_string'.
	
	If 'deck_hint' is supplied, only cards from decks matching it are returned.

	Returns an empty iterable if no matching cards are found.
	"""

	search_string = generate_search_string(search_string)
	possible_decks = []

	params = [ search_string, search_string ]
	sql = _card_query() + "WHERE (cards.name LIKE ? OR cards.other_name LIKE ?)"

	if deck_hint:
		deck_hint = "%" + deck_hint + "%"
		params.append(deck_hint)
		sql += " AND cards.deck_key IN (SELECT key FROM decks WHERE name LIKE ?)"

	results = cur.execute(sql, params).fetchall();

	def process_card(row):
		card_key = row["key"]
		abilities = cur.execute("SELECT * FROM abilities WHERE card_key == ?;", ( card_key, )).fetchall()
		return Card(row, abilities)

	return _merge_card_sides(results, process_card)

def search_decks(search_string):
	"""
	Returns an iterable of Decks with name matching 'search_string'

	Returns an empty iterable if no matching decks are found.
	"""

	search_string = generate_search_string(search_string)

	decks = cur.execute(_deck_query() + "WHERE decks.name LIKE ?", ( search_string, )).fetchall()

	def process_deck(row):
		cards = cur.execute(_card_query() + "WHERE cards.deck_key == ?", (row["key"], )).fetchall()
		return Deck(row, cards)

	return sorted([process_deck(row) for row in decks], key = attrgetter("name"))

def search_mods(search_string):
	"""
	Returns an iterable of Mods with name matching 'search_string'

	Returns an empty iterable if no matching mods are found.
	"""

	search_string = generate_search_string(search_string)

	mods = cur.execute("SELECT mods.*, (SELECT count(*) FROM decks WHERE mod_key == mods.key) as deck_count FROM mods WHERE mods.name LIKE ?", ( search_string, )).fetchall()

	def process_mod(row):
		decks = cur.execute(_deck_query() + "WHERE decks.mod_key == ?", (row["key"], )).fetchall()
		return Mod(row, decks)

	return sorted([process_mod(row) for row in mods], key = attrgetter("name"))

def get_card(card_title):
	"""
	Returns a Card with title equal to 'card_title', or None if no such card exists.
	"""
	results = cur.execute("SELECT * FROM cards WHERE name = ?;", (card_title, )).fetchall();
	if len(results) == 0:
		return None

	return Card(results[0])