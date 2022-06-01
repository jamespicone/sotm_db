import sqlite3

class Card:
	def __init__(self, title, keywords, text, hitpoints = None):
		self.title = title
		self.keywords = keywords
		self.text = text
		self.hitpoints = hitpoints
		pass

	def __str__(self):
		ret = self.title

		if self.hitpoints is not None:
			ret += " | " + str(self.hitpoints) + " HP"

		ret += " | " + ", ".join(self.keywords) + " | " + self.text

		return ret

	def __repr__(self):
		return str(self)

def get_card(search_string, deck_hint = None, mod_hint = None):
	"""
	Returns an iterable of Cards with title matching 'search_string'.
	
	If 'deck_hint' is supplied, only cards from decks matching it are returned.
	If 'mod_hint' is supplied, only cards from mods matching it are returned.

	Returns an empty iterable if no matching cards are found.
	"""
	return [
		Card("Test Card", ["ongoing", "fred"], "Do something interesting", 5),
		Card("Other Card", [], "Do 1 damage")
	]