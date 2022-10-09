import sqlite3
import unicodedata
from operator import attrgetter

db = sqlite3.connect("sotm_cards.db")
db.row_factory = sqlite3.Row
cur = db.cursor()

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
			if self.title == self.other_title or self.other_title is None:
				formatter.title(self.title)
			else:
				formatter.title(f"{self.title} (front side of {self.other_title})")
		else:
			if self.title == self.other_title:
				formatter.title(self.title + " (back side)")
			else:
				formatter.title(f"{self.title} (back side of {self.other_title})")
		
		if self.hitpoints != None:
			formatter.smallbox("HP", str(self.hitpoints))

		formatter.smallbox("Quantity", str(self.count))

		if len(self.keywords) > 0:
			formatter.smallbox("Keywords", self.keywords)

		if self.setup != None:
			formatter.box("Setup", self.setup)

		if self.text != None:
			formatter.box("Text", self.text)

		if self.gameplay != None:
			formatter.box("Gameplay", self.gameplay)

		if self.advanced != None:
			formatter.box("Advanced", self.advanced)

		if self.challenge != None:
			formatter.box("Challenge", self.challenge)

		if len(self.abilities) > 0:
			for ability in self.abilities:
				formatter.box(ability.name, ability.text)

		formatter.footer(f"Deck: {self.deck}, Mod: {self.mod}, Deck type: {self.deck_type}")

def search_cards(search_string, deck_hint = None):
	"""
	Returns an iterable of Cards with title matching 'search_string'.
	
	If 'deck_hint' is supplied, only cards from decks matching it are returned.

	Returns an empty iterable if no matching cards are found.
	"""

	search_string = "%" + search_string + "%"

	possible_decks = []

	params = [ search_string, search_string ]
	sql = "SELECT cards.*, decks.deck_type, decks.name AS deck_name, mods.name AS mod_name FROM cards INNER JOIN decks ON decks.key == cards.deck_key INNER JOIN mods ON mods.key == decks.mod_key WHERE (cards.name LIKE ? OR cards.other_name LIKE ?)"

	if deck_hint is not None:
		deck_hint = "%" + deck_hint + "%"
		params.append(deck_hint)
		sql += " AND cards.deck_key IN (SELECT key FROM decks WHERE name LIKE ?)"

	results = cur.execute(sql, params).fetchall();

	def process_card(row):
		card_key = row["key"]
		abilities = cur.execute("SELECT * FROM abilities WHERE card_key == ?;", ( card_key, )).fetchall()
		return Card(row, abilities)

	front_sides = [ process_card(row) for row in results if row["front_side"] == None ]
	back_sides = [ process_card(row) for row in results if row["front_side"] != None ]

	for card in back_sides:
		for front in front_sides:
			if card.is_other_side(front):
				card.set_other_side(front)
				front.set_other_side(card)
				break

	return sorted(front_sides, key = attrgetter("sort_key"))

def get_card(card_title):
	"""
	Returns a Card with title equal to 'card_title', or None if no such card exists.
	"""
	results = cur.execute("SELECT * FROM cards WHERE name = ?;", (card_title, )).fetchall();
	if len(results) == 0:
		return None

	return Card(results[0])