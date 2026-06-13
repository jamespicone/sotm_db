import unicodedata

def normalize_for_search(s):
	"""
	Normalise a string for accent- and case-insensitive searching.

	Folds case (so 'ß' -> 'ss') and strips combining accent marks (so 'á' -> 'a'),
	letting a query like 'la capitan' match a card named 'La Capitán'.

	Returns None if given None.
	"""
	if s is None:
		return None

	# NFKD splits 'á' into 'a' + a combining accent; drop the combining marks.
	decomposed = unicodedata.normalize('NFKD', s.casefold())
	return ''.join(c for c in decomposed if not unicodedata.combining(c))
