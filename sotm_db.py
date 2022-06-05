import sqlite3

db = sqlite3.connect("sotm_cards.db")
db.row_factory = sqlite3.Row
cur = db.cursor()

class Card:
	def __init__(self, db_row):
		self.title = db_row["name"]
		self.text = db_row["text"]
		self.hitpoints = None
		self.keywords = []

	def __str__(self):
		ret = self.title

		if self.hitpoints is not None:
			ret += " | " + str(self.hitpoints) + " HP"

		ret += " | " + ", ".join(self.keywords) + " | " + self.text

		return ret

	def __repr__(self):
		return str(self)

def search_cards(search_string, deck_hint = None):
	"""
	Returns an iterable of Cards with title matching 'search_string'.
	
	If 'deck_hint' is supplied, only cards from decks matching it are returned.
	If 'mod_hint' is supplied, only cards from mods matching it are returned.

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
	return [ Card(row) for row in results ]

def get_card(card_title):
	"""
	Returns a Card with title equal to 'card_title', or None if no such card exists.
	"""
	results = cur.execute("SELECT * FROM cards WHERE name = ?;", (card_title, )).fetchall();
	if len(results) == 0:
		return None

	return Card(results[0])