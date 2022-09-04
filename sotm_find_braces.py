import sqlite3
import unicodedata
import re
from operator import attrgetter

pattern = re.compile("\{[^\r\n}]*\}")

db = sqlite3.connect("sotm_cards.db")
db.row_factory = sqlite3.Row
cur = db.cursor()

cards = cur.execute("SELECT * from cards").fetchall()
abilities = cur.execute("SELECT * from abilities").fetchall()

braces = set()

def add_braces(input_string):
	global braces
	if input_string is None:
		return

	braces = braces.union(re.findall(pattern, input_string))

for card in cards:
	add_braces(card["name"])
	add_braces(card["other_name"])
	add_braces(card["text"])
	add_braces(card["gameplay"])
	add_braces(card["setup"])
	add_braces(card["advanced"])
	add_braces(card["challenge"])
	add_braces(card["keywords"])

for ability in abilities:
	add_braces(ability["ability_name"])
	add_braces(ability["text"])

sorted_braces = sorted(braces)
for text in sorted_braces:
	print(text)