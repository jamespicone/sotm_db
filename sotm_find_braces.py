import sqlite3
import unicodedata
import re
from operator import attrgetter

pattern = re.compile("\{[^\r\n}]*\}|\[[^\r\n\]]*\]")

db = sqlite3.connect("sotm_cards.db")
db.row_factory = sqlite3.Row
cur = db.cursor()

cards = cur.execute("SELECT * from cards").fetchall()
abilities = cur.execute("SELECT * from abilities").fetchall()

braces = {}

def add_braces(name, input_string):
	global braces
	if input_string is None:
		return

	for match in re.findall(pattern, input_string):
		braces[match] = braces.get(match, list()) + [ name ]

for card in cards:
	add_braces(card["name"], card["name"])
	add_braces(card["name"], card["other_name"])
	add_braces(card["name"], card["text"])
	add_braces(card["name"], card["gameplay"])
	add_braces(card["name"], card["setup"])
	add_braces(card["name"], card["advanced"])
	add_braces(card["name"], card["challenge"])
	add_braces(card["name"], card["keywords"])

for ability in abilities:
	add_braces("ABILITY: " + ability["ability_name"], ability["ability_name"])
	add_braces("ABILITY: " + ability["ability_name"], ability["text"])

sorted_braces = sorted(braces.keys())
for text in sorted_braces:
	cardnames = ", ".join(braces[text])
	print(f"{text}: {cardnames}")
	