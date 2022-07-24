import sqlite3

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

		self.text += "\t\t| " + box_text.replace("{BR}", "\n").replace("\n", "\n\t\t| ")
		self.text += "\n\n"

class Ability:
	def __init__(self, db_row):
		self.name = db_row["ability_name"]
		self.text = db_row["text"]

class Card:
	def __init__(self, db_row, ability_rows):
		self.title = db_row["name"]
		self.text = db_row["text"]
		self.gameplay = db_row["gameplay"]
		self.advanced = db_row["advanced"]
		self.challenge = db_row["challenge"]
		self.hitpoints = None
		self.keywords = db_row["keywords"]
		self.abilities = [ Ability(ability) for ability in ability_rows ]

	def __str__(self):
		ret = self.title

		if self.hitpoints is not None:
			ret += " | " + str(self.hitpoints) + " HP"

		ret += " | " + ", ".join(self.keywords) + " | " + self.text

		return ret

	def __repr__(self):
		formatter = TextFormatter()
		self.format(formatter)
		return str(formatter)

	def format(self, formatter):
		formatter.title(self.title)
		
		if self.hitpoints != None:
			formatter.smallbox("HP", hitpoints)

		if len(self.keywords) > 0:
			formatter.smallbox("Keywords", self.keywords)

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

		return "";

def search_cards(search_string, deck_hint = None):
	"""
	Returns an iterable of Cards with title matching 'search_string'.
	
	If 'deck_hint' is supplied, only cards from decks matching it are returned.

	Returns an empty iterable if no matching cards are found.
	"""

	search_string = "%" + search_string + "%"

	possible_decks = []

	params = [ search_string ]
	sql = "SELECT * FROM cards WHERE name LIKE ?"

	if deck_hint is not None:
		deck_hint = "%" + deck_hint + "%"
		params.append(deck_hint)
		sql += " AND deck_key IN (SELECT key FROM decks WHERE name LIKE ?)"

	results = cur.execute(sql, params).fetchall();

	def process_card(row):
		card_key = row["key"]
		abilities = cur.execute("SELECT * FROM abilities WHERE card_key == ?;", ( card_key, )).fetchall()
		return Card(row, abilities)
	
	return [ process_card(row) for row in results ]

def get_card(card_title):
	"""
	Returns a Card with title equal to 'card_title', or None if no such card exists.
	"""
	results = cur.execute("SELECT * FROM cards WHERE name = ?;", (card_title, )).fetchall();
	if len(results) == 0:
		return None

	return Card(results[0])