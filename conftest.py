import sqlite3

import pytest

import create_db
from normalize import normalize_for_search


def _insert_card(cur, deck_key, name, *, keywords="", count=1, hitpoints=None,
                 text=None, gameplay=None, other_name=None, front_side=None):
	"""Insert a single card row, auto-filling the folded search columns. Returns its key."""
	return cur.execute(
		"""INSERT INTO cards (deck_key, name, other_name, search_name, search_other_name,
		                      keywords, count, hitpoints, text, gameplay, front_side)
		   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING key;""",
		(deck_key, name, other_name, normalize_for_search(name), normalize_for_search(other_name),
		 keywords, count, hitpoints, text, gameplay, front_side)
	).fetchone()[0]


def _insert_flip_card(cur, deck_key, front_name, back_name, **kwargs):
	"""Insert a two-sided card (front + back rows) wired together. Returns (front_key, back_key)."""
	front_key = _insert_card(cur, deck_key, front_name, other_name=back_name, **kwargs)
	back_key = _insert_card(cur, deck_key, back_name, other_name=front_name, front_side=front_key, **kwargs)
	cur.execute("UPDATE cards SET back_side = ? WHERE key = ?;", (back_key, front_key))
	return front_key, back_key


def _populate(cur):
	# Mods
	cur.executemany(
		"INSERT INTO mods (key, name, search_name, authors) VALUES (?, ?, ?, ?);",
		[
			(1, "Sentinels of the Multiverse", normalize_for_search("Sentinels of the Multiverse"), "GTG"),
			(2, "Cauldron", normalize_for_search("Cauldron"), "Cauldron Team"),
		],
	)

	# Decks
	cur.executemany(
		"INSERT INTO decks (key, mod_key, name, search_name, deck_type) VALUES (?, ?, ?, ?, ?);",
		[
			(1, 1, "La Capitán", normalize_for_search("La Capitán"), "Hero"),
			(2, 2, "Anathema", normalize_for_search("Anathema"), "Villain"),
			(3, 1, "Megalopolis", normalize_for_search("Megalopolis"), "Environment"),
			(4, 1, "Flip Test", normalize_for_search("Flip Test"), "Hero"),
		],
	)

	# Cards in the La Capitán deck (note the accented deck/card name)
	_insert_card(cur, 1, "La Capitán", keywords="Hero", hitpoints=28)
	_insert_card(cur, 1, "Plunder", keywords="One-Shot")
	_insert_card(cur, 1, "Captain's Orders", keywords="Ongoing")

	# Cards in the Anathema (Cauldron) deck, one with an ability
	biofeedback = _insert_card(cur, 2, "Biofeedback", keywords="Ongoing")
	cur.execute(
		"INSERT INTO abilities (card_key, ability_name, text) VALUES (?, ?, ?);",
		(biofeedback, "power", "Draw a card now."),
	)

	# Environment card
	_insert_card(cur, 3, "Plummeting Monorail", keywords="")

	# A two-sided card to exercise other_name / search_other_name matching and merging
	_insert_flip_card(cur, 4, "Frontside", "Backside")


@pytest.fixture
def sotm(monkeypatch):
	"""Provide the sotm_db module pointed at a fresh in-memory fixture database."""
	import sotm_db

	conn = sqlite3.connect(":memory:")
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	create_db.create_schema(cur)
	_populate(cur)
	conn.commit()

	monkeypatch.setattr(sotm_db, "db", conn)
	monkeypatch.setattr(sotm_db, "cur", cur)

	yield sotm_db

	conn.close()
